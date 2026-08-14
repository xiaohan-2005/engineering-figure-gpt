from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "docs" / "examples"
MANIFEST_SCHEMA = EXAMPLES / "example-manifest.schema.json"
PLOT_REQUEST_SCHEMA = ROOT / "schemas" / "plot-request.schema.json"
PLOT_SPEC_SCHEMA = ROOT / "schemas" / "plot-spec.schema.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_example_manifest_schema_accepts_reproducible_image_example():
    schema = load(MANIFEST_SCHEMA)
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


def test_every_committed_manifest_is_valid_and_resolves_artifacts():
    validator = Draft202012Validator(load(MANIFEST_SCHEMA))
    manifests = sorted(EXAMPLES.glob("*/manifest.json"))
    assert manifests, "At least one completed reproducible example should exist."
    for path in manifests:
        manifest = load(path)
        errors = list(validator.iter_errors(manifest))
        assert errors == [], f"{path}: {errors}"
        assert path.parent.name == manifest["slug"]
        for rel in manifest["input_artifacts"]:
            assert (path.parent / rel).is_file(), f"Missing input artifact {path.parent / rel}"
        output = path.parent / manifest["output_artifact"]
        assert output.is_file(), f"Missing output artifact {output}"
        assert output.stat().st_size > 0, f"Empty output artifact {output}"
        assert (path.parent / "verification.md").is_file()


def test_completed_plot_examples_follow_request_and_spec_schemas():
    request_validator = Draft202012Validator(load(PLOT_REQUEST_SCHEMA))
    spec_validator = Draft202012Validator(load(PLOT_SPEC_SCHEMA))
    manifests = sorted(EXAMPLES.glob("*/manifest.json"))
    plot_examples = [p for p in manifests if load(p).get("mode") == "plot"]
    assert plot_examples
    for manifest_path in plot_examples:
        folder = manifest_path.parent
        request = folder / "request.json"
        spec = folder / "plot-spec.json"
        assert request.is_file()
        assert spec.is_file()
        request_errors = list(request_validator.iter_errors(load(request)))
        spec_errors = list(spec_validator.iter_errors(load(spec)))
        assert request_errors == [], f"{request}: {request_errors}"
        assert spec_errors == [], f"{spec}: {spec_errors}"
