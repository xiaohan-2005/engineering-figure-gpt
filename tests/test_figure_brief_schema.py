from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "figure-brief.schema.json"


def validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def valid_brief():
    return {
        "figure_goal": "Explain the modeling workflow.",
        "paper_claim": "The method links forecasting, optimization, and validation.",
        "figure_type": "mathematical-model-framework",
        "mode": "image",
        "panels": [
            {
                "name": "Main workflow",
                "purpose": "Show the complete reasoning path.",
                "content": "Data preprocessing -> forecasting -> optimization -> validation",
                "evidence_or_data": "Method section",
            }
        ],
        "must_keep_labels": ["Forecasting", "Optimization"],
        "data": {},
        "style_constraints": ["white background"],
        "output_formats": ["png"],
        "verification_checklist": ["Check labels and arrow direction"],
    }


def test_valid_figure_brief_passes():
    errors = list(validator().iter_errors(valid_brief()))
    assert errors == []


def test_panel_requires_name_and_content():
    brief = valid_brief()
    brief["panels"] = [{"purpose": "missing required fields"}]
    errors = list(validator().iter_errors(brief))
    messages = "\n".join(error.message for error in errors)
    assert "name" in messages
    assert "content" in messages


def test_invalid_output_format_is_rejected():
    brief = valid_brief()
    brief["output_formats"] = ["docx"]
    assert list(validator().iter_errors(brief))
