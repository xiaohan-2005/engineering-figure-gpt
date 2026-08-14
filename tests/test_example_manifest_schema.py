from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "examples" / "example-manifest.schema.json"


def test_example_manifest_schema_accepts_reproducible_image_example():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    manifest = {
        "slug": "rag-system-architecture",
        "mode": "image",
        "input_artifacts": ["brief.md", "prompt.txt"],
        "output_artifact": "output.png",
        "model": "gpt-image-2",
        "quality": "high",
        "size": "1536x1024",
        "verification": ["labels checked", "arrow directions checked"],
    }
    assert list(Draft202012Validator(schema).iter_errors(manifest)) == []
