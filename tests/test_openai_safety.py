from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_image.py"


def load_module():
    spec = importlib.util.spec_from_file_location("efg_generate_image_safety", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def args_for(base_url: str, model: str = "gpt-image-2", allow_third_party: bool = False):
    return argparse.Namespace(
        base_url=base_url,
        model=model,
        allow_third_party=allow_third_party,
        n=1,
        timeout=30,
        size="1536x1024",
        input_fidelity=None,
        background=None,
        _codex_trusted=False,
    )


def test_official_base_url_is_allowed():
    module = load_module()
    assert module.validate_target(args_for("https://api.openai.com/v1")) is False


def test_custom_base_url_requires_explicit_opt_in(monkeypatch):
    module = load_module()
    monkeypatch.delenv("OPENAI_ALLOW_THIRD_PARTY", raising=False)
    with pytest.raises(SystemExit, match="allow-third-party"):
        module.validate_target(args_for("https://relay.example/v1"))


def test_custom_base_url_is_allowed_with_flag(monkeypatch):
    module = load_module()
    monkeypatch.delenv("OPENAI_ALLOW_THIRD_PARTY", raising=False)
    args = args_for("https://relay.example/v1/", allow_third_party=True)
    assert module.validate_target(args) is True
    assert args.base_url == "https://relay.example/v1"


def test_custom_base_url_is_allowed_with_environment_flag(monkeypatch):
    module = load_module()
    monkeypatch.setenv("OPENAI_ALLOW_THIRD_PARTY", "1")
    assert module.validate_target(args_for("https://relay.example/v1")) is True


def test_malformed_base_url_is_rejected():
    module = load_module()
    with pytest.raises(SystemExit, match="valid http"):
        module.validate_target(args_for("relay.example/v1", allow_third_party=True))


def test_embedded_credentials_in_base_url_are_rejected():
    module = load_module()
    with pytest.raises(SystemExit, match="embed credentials"):
        module.validate_target(args_for("https://user:pass@relay.example/v1", allow_third_party=True))


def test_non_gpt_image_model_is_rejected():
    module = load_module()
    with pytest.raises(SystemExit, match="Only GPT Image model"):
        module.validate_target(args_for("https://api.openai.com/v1", model="other-model"))


def test_gpt_image_2_transparent_background_is_rejected():
    module = load_module()
    args = args_for("https://api.openai.com/v1")
    args.background = "transparent"
    with pytest.raises(SystemExit, match="does not currently support transparent"):
        module.validate_target(args)


def test_default_model_resolution_is_gpt_image_2(monkeypatch):
    module = load_module()
    monkeypatch.delenv("OPENAI_IMAGE_MODEL", raising=False)
    args = argparse.Namespace(model=None, highres=False, final=False)
    model, final_requested = module.resolve_model(args, "routine paper figure")
    assert model == "gpt-image-2"
    assert final_requested is False


def test_highres_request_fails_closed_without_config(monkeypatch):
    module = load_module()
    monkeypatch.delenv("OPENAI_IMAGE_HIGHRES_MODEL", raising=False)
    args = argparse.Namespace(model=None, highres=True, final=False)
    with pytest.raises(SystemExit, match="OPENAI_IMAGE_HIGHRES_MODEL"):
        module.resolve_model(args, "final figure")


def test_highres_request_uses_configured_model(monkeypatch):
    module = load_module()
    monkeypatch.setenv("OPENAI_IMAGE_HIGHRES_MODEL", "gpt-image-2-final")
    args = argparse.Namespace(model=None, highres=True, final=False)
    model, final_requested = module.resolve_model(args, "final figure")
    assert model == "gpt-image-2-final"
    assert final_requested is True


def test_explicit_model_can_satisfy_final_request(monkeypatch):
    module = load_module()
    monkeypatch.delenv("OPENAI_IMAGE_HIGHRES_MODEL", raising=False)
    args = argparse.Namespace(model="gpt-image-2-custom", highres=False, final=True)
    model, final_requested = module.resolve_model(args, "final figure")
    assert model == "gpt-image-2-custom"
    assert final_requested is True


def test_dry_run_does_not_require_api_key():
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.pop("OPENAI_API_KEY_FILE", None)
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "test research figure", "--dry-run"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert '"model": "gpt-image-2"' in result.stdout
    assert '"mode": "generate"' in result.stdout
    assert '"third_party": false' in result.stdout
    assert '"final_quality_requested": false' in result.stdout
    assert '"size": "1536x1024"' in result.stdout


def test_relay_dry_run_works_with_environment_opt_in():
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.pop("OPENAI_API_KEY_FILE", None)
    env["OPENAI_BASE_URL"] = "https://relay.example/v1"
    env["OPENAI_ALLOW_THIRD_PARTY"] = "1"
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "test research figure", "--dry-run"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert '"base_url": "https://relay.example/v1"' in result.stdout
    assert '"third_party": true' in result.stdout
    assert "third-party relay" in result.stderr


def test_key_file_can_be_loaded(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    key_file = tmp_path / "key.txt"
    key_file.write_text("file-test-key\n", encoding="utf-8")
    args = argparse.Namespace(api_key=None, api_key_file=str(key_file))
    assert module.read_key(args) == "file-test-key"
