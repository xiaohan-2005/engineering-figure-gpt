from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_image.py"


def load_module():
    spec = importlib.util.spec_from_file_location("efg_generate_image_errors", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ErrorResponse:
    ok = False
    status_code = 429
    text = "rate limit reached"

    def json(self):
        return {"error": {"message": "rate limit reached"}}


def test_generation_surfaces_http_error_without_fallback(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module.requests, "post", lambda *args, **kwargs: ErrorResponse())
    args = argparse.Namespace(
        model="gpt-image-2",
        base_url="https://api.openai.com/v1",
        size="1536x1024",
        quality="high",
        output_format="png",
        n=1,
        background=None,
        timeout=30,
    )
    with pytest.raises(SystemExit, match="429"):
        module.generation_request(args, "test", {"Authorization": "Bearer x"})


def test_empty_image_response_is_rejected(tmp_path):
    module = load_module()
    with pytest.raises(SystemExit, match="no data"):
        module.save_result({"data": []}, tmp_path, "figure", "png")
