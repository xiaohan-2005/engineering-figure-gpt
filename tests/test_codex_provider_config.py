from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONFIG_MODULE_PATH = ROOT / "scripts" / "codex_provider_config.py"
IMAGE_MODULE_PATH = ROOT / "scripts" / "generate_image.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_codex_files(tmp_path: Path, *, bearer: str | None = None, auth_key: str | None = None):
    codex = tmp_path / ".codex"
    codex.mkdir()
    bearer_line = f'\nexperimental_bearer_token = "{bearer}"' if bearer else ""
    config = codex / "config.toml"
    config.write_text(
        'model_provider = "ccswitch"\n'
        'model = "gpt-5.6-codex"\n\n'
        '[model_providers.ccswitch]\n'
        'name = "CC Switch"\n'
        'base_url = "https://relay.example/v1"\n'
        'wire_api = "responses"\n'
        f'requires_openai_auth = true{bearer_line}\n',
        encoding="utf-8",
    )
    auth = codex / "auth.json"
    auth.write_text(json.dumps({"OPENAI_API_KEY": auth_key}) if auth_key else "{}", encoding="utf-8")
    return config, auth


def connection_args(config: Path, auth: Path, **overrides):
    values = dict(
        base_url=None,
        no_codex_config=False,
        codex_config=str(config),
        codex_auth=str(auth),
        allow_third_party=False,
        model="gpt-image-2",
        n=1,
        timeout=30,
    )
    values.update(overrides)
    return argparse.Namespace(**values)


def test_reads_cc_switch_base_url_and_auth_json_key(tmp_path):
    module = load(CONFIG_MODULE_PATH, "codex_provider_config_auth")
    config, auth = write_codex_files(tmp_path, auth_key="cc-auth-key")
    info = module.load_codex_live_provider(config, auth)
    assert info["provider_name"] == "ccswitch"
    assert info["base_url"] == "https://relay.example/v1"
    assert info["wire_api"] == "responses"
    assert info["api_key"] == "cc-auth-key"
    assert info["key_source"] == "auth.json:OPENAI_API_KEY"


def test_provider_bearer_token_takes_priority_over_auth_json(tmp_path):
    module = load(CONFIG_MODULE_PATH, "codex_provider_config_bearer")
    config, auth = write_codex_files(tmp_path, bearer="provider-token", auth_key="auth-token")
    info = module.load_codex_live_provider(config, auth)
    assert info["api_key"] == "provider-token"
    assert info["key_source"] == "config.toml:experimental_bearer_token"


def test_image_cli_reuses_active_codex_provider_without_second_opt_in(tmp_path, monkeypatch):
    module = load(IMAGE_MODULE_PATH, "image_codex_provider")
    config, auth = write_codex_files(tmp_path, auth_key="cc-auth-key")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_ALLOW_THIRD_PARTY", raising=False)
    args = connection_args(config, auth)
    resolved = module.resolve_connection(args)
    assert resolved["source"] == "codex-config"
    assert resolved["codex_provider"] == "ccswitch"
    assert args.base_url == "https://relay.example/v1"
    assert module.read_key(args) == "cc-auth-key"
    assert module.validate_target(args) is True


def test_codex_text_model_is_not_reused_as_image_model(tmp_path, monkeypatch):
    module = load(IMAGE_MODULE_PATH, "image_model_separation")
    config, auth = write_codex_files(tmp_path, auth_key="cc-auth-key")
    monkeypatch.delenv("OPENAI_IMAGE_MODEL", raising=False)
    args = connection_args(config, auth, model=None, highres=False, final=False)
    module.resolve_connection(args)
    model, final_requested = module.resolve_model(args, "routine research figure")
    assert model == "gpt-image-2"
    assert final_requested is False


def test_explicit_custom_url_does_not_gain_codex_implicit_trust(tmp_path, monkeypatch):
    module = load(IMAGE_MODULE_PATH, "image_explicit_provider")
    config, auth = write_codex_files(tmp_path, auth_key="cc-auth-key")
    monkeypatch.delenv("OPENAI_ALLOW_THIRD_PARTY", raising=False)
    args = connection_args(config, auth, base_url="https://other-relay.example/v1")
    resolved = module.resolve_connection(args)
    assert resolved["source"] == "cli"
    assert getattr(args, "_codex_api_key") is None
    with pytest.raises(SystemExit, match="allow-third-party"):
        module.validate_target(args)


def test_sanitized_summary_never_contains_secret(tmp_path):
    module = load(CONFIG_MODULE_PATH, "codex_provider_config_summary")
    config, auth = write_codex_files(tmp_path, bearer="super-secret-token")
    info = module.load_codex_live_provider(config, auth)
    summary = module.sanitized_summary(info)
    text = json.dumps(summary)
    assert "super-secret-token" not in text
    assert summary["has_api_key"] is True
