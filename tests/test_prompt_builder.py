import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_templates_have_chinese_and_english():
    path = ROOT / "assets" / "prompt-templates" / "engineering-figure-templates.json"
    templates = json.loads(path.read_text(encoding="utf-8"))
    assert "system-architecture" in templates
    assert "mathematical-model-framework" in templates
    for item in templates.values():
        assert "en" in item
        assert "zh" in item


def test_prompt_builder_runs_offline():
    script = ROOT / "scripts" / "build_engineering_figure_prompt.py"
    result = subprocess.run(
        [sys.executable, str(script), "--figure-template", "algorithm-workflow", "--lang", "en", "input to model to output"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "input to model to output" in result.stdout
