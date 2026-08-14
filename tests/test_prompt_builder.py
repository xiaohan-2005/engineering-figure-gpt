import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_pack(name: str) -> dict:
    path = ROOT / "assets" / "prompt-templates" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_engineering_templates_have_chinese_and_english():
    templates = load_pack("engineering-figure-templates.json")
    assert "system-architecture" in templates
    assert "mathematical-model-framework" in templates
    for item in templates.values():
        assert "en" in item
        assert "zh" in item


def test_modeling_domain_pack_has_expected_templates():
    templates = load_pack("mathematical-modeling-templates.json")
    for key in (
        "problem-analysis",
        "q1-q2-q3-dependency",
        "forecasting-workflow",
        "multi-objective-pareto",
        "sensitivity-analysis",
        "robustness-analysis",
        "full-modeling-pipeline",
    ):
        assert key in templates
        assert "en" in templates[key]
        assert "zh" in templates[key]


def test_prompt_builder_runs_offline_for_engineering_template():
    script = ROOT / "scripts" / "build_engineering_figure_prompt.py"
    result = subprocess.run(
        [sys.executable, str(script), "--figure-template", "algorithm-workflow", "--lang", "en", "input to model to output"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "input to model to output" in result.stdout


def test_prompt_builder_runs_offline_for_modeling_template():
    script = ROOT / "scripts" / "build_engineering_figure_prompt.py"
    result = subprocess.run(
        [sys.executable, str(script), "--figure-template", "sensitivity-analysis", "--lang", "zh", "对参数进行±10%扰动并比较目标函数变化"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "敏感性" in result.stdout
    assert "±10%" in result.stdout


def test_list_templates_does_not_require_background_or_template():
    script = ROOT / "scripts" / "build_engineering_figure_prompt.py"
    result = subprocess.run(
        [sys.executable, str(script), "--list-templates"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "system-architecture" in result.stdout
    assert "full-modeling-pipeline" in result.stdout
