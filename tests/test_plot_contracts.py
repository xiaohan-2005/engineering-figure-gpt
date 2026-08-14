from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REQUEST_SCHEMA = ROOT / "schemas" / "plot-request.schema.json"
SPEC_SCHEMA = ROOT / "schemas" / "plot-spec.schema.json"
BUILDER = ROOT / "scripts" / "build_plot_spec.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("efg_plot_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_schema(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_examples_validate_and_round_trip_to_renderer_contract():
    request_validator = Draft202012Validator(load_schema(REQUEST_SCHEMA))
    spec_validator = Draft202012Validator(load_schema(SPEC_SCHEMA))
    builder = load_builder()

    for path in [
        ROOT / "examples" / "benchmark-plot-request.json",
        ROOT / "examples" / "multi-panel-plot-request.json",
    ]:
        request = json.loads(path.read_text(encoding="utf-8"))
        request_errors = list(request_validator.iter_errors(request))
        assert request_errors == [], f"{path.name}: {[e.message for e in request_errors]}"

        normalized = builder.build_spec(request)
        spec_errors = list(spec_validator.iter_errors(normalized))
        assert spec_errors == [], f"{path.name}: {[e.message for e in spec_errors]}"

        assert all("kind" not in panel for panel in normalized["panels"])
        assert all("type" in panel for panel in normalized["panels"])
