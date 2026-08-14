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


def test_custom_base_url_is_rejected():
    module = load_module()
    args = argparse.Namespace(base_url="https://relay.example/v1", model="gpt-image-2")
    with pytest.raises(SystemExit, match="official OpenAI endpoint"):
        module.validate_target(args)


def test_non_gpt_image_model_is_rejected():
    module = load_module()
    args = argparse.Namespace(base_url="https://api.openai.com/v1", model="other-model")
    with pytest.raises(SystemExit, match="Only GPT Image models"):
        module.validate_target(args)


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


def test_key_file_can_be_loaded(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    key_file = tmp_path / "key.txt"
    key_file.write_text("file-test-key\n", encoding="utf-8")
    args = argparse.Namespace(api_key=None, api_key_file=str(key_file))
    assert module.read_key(args) == "file-test-key"
