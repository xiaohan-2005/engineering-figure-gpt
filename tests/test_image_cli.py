from __future__ import annotations

import argparse
import base64
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_image.py"


def load_module():
    spec = importlib.util.spec_from_file_location("efg_generate_image", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text="ok"):
        self._payload = payload or {"data": [{"b64_json": base64.b64encode(b"img").decode("ascii")}]}
        self.status_code = status_code
        self.text = text
        self.ok = 200 <= status_code < 300
        self.content = b"downloaded"

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(self.text)


def base_args(**overrides):
    values = dict(
        model="gpt-image-2",
        base_url="https://api.openai.com/v1",
        size="1536x1024",
        quality="high",
        output_format="png",
        n=1,
        background=None,
        timeout=30,
        input_image=[],
        input_fidelity=None,
    )
    values.update(overrides)
    return argparse.Namespace(**values)


def test_generation_request_builds_openai_payload(monkeypatch):
    module = load_module()
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse({"data": [{"b64_json": "aW1n"}]})

    monkeypatch.setattr(module.requests, "post", fake_post)
    result = module.generation_request(base_args(background="opaque", n=2), "paper figure", {"Authorization": "Bearer test"})

    assert captured["url"] == "https://api.openai.com/v1/images/generations"
    assert captured["json"] == {
        "model": "gpt-image-2",
        "prompt": "paper figure",
        "size": "1536x1024",
        "quality": "high",
        "output_format": "png",
        "n": 2,
        "background": "opaque",
    }
    assert result["data"]


def test_edit_request_uses_multipart_and_fidelity(monkeypatch, tmp_path):
    module = load_module()
    image = tmp_path / "input.png"
    image.write_bytes(b"png")
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["data"] = dict(kwargs["data"])
        captured["file_fields"] = [item[0] for item in kwargs["files"]]
        captured["file_names"] = [item[1][0] for item in kwargs["files"]]
        return FakeResponse({"data": [{"b64_json": "aW1n"}]})

    monkeypatch.setattr(module.requests, "post", fake_post)
    args = base_args(input_image=[str(image)], input_fidelity="high")
    result = module.edit_request(args, "preserve structure", {"Authorization": "Bearer test"})

    assert captured["url"] == "https://api.openai.com/v1/images/edits"
    assert captured["data"]["input_fidelity"] == "high"
    assert captured["file_fields"] == ["image[]"]
    assert captured["file_names"] == ["input.png"]
    assert result["data"]


def test_save_result_writes_base64_image(tmp_path):
    module = load_module()
    payload = {"data": [{"b64_json": base64.b64encode(b"binary-image").decode("ascii")}]}
    saved = module.save_result(payload, tmp_path, "figure", "png")
    assert saved == [tmp_path / "figure-1.png"]
    assert saved[0].read_bytes() == b"binary-image"


def test_read_key_prefers_environment(monkeypatch):
    module = load_module()
    monkeypatch.setenv("OPENAI_API_KEY", "env-test-key")
    args = argparse.Namespace(api_key=None, api_key_file=None)
    assert module.read_key(args) == "env-test-key"
