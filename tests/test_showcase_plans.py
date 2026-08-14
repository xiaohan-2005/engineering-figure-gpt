from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "docs" / "showcase-plans"
EXPECTED = {
    "zh-mathematical-modeling-framework",
    "rag-system-architecture",
    "genetic-algorithm-workflow",
    "multisource-fusion-graphical-abstract",
}


def test_real_conceptual_showcase_queue_has_evidence_inputs_only():
    index = (PLANS / "README.md").read_text(encoding="utf-8")
    verification_template = PLANS / "verification-template.md"
    assert verification_template.is_file()
    assert "PASS" in verification_template.read_text(encoding="utf-8")

    for slug in EXPECTED:
        folder = PLANS / slug
        brief = folder / "brief.md"
        prompt = folder / "prompt.txt"
        assert brief.is_file(), slug
        assert prompt.is_file(), slug
        assert brief.stat().st_size > 500, slug
        assert prompt.stat().st_size > 800, slug
        assert slug in index

        # Plans are intentionally not completed examples until a real output exists.
        assert not (folder / "manifest.json").exists(), slug
        assert not (folder / "output.png").exists(), slug
        assert not (folder / "output.jpg").exists(), slug
        assert not (folder / "output.webp").exists(), slug


def test_plan_prompts_contain_non_fabrication_language():
    combined = "\n".join((PLANS / slug / "prompt.txt").read_text(encoding="utf-8").lower() for slug in EXPECTED)
    assert "不得虚构" in combined
    assert "do not invent" in combined
    assert "white background" in combined or "白色背景" in combined
