from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reference_index_points_to_existing_files():
    index = (ROOT / "references" / "README.md").read_text(encoding="utf-8")
    expected = [
        "figure-brief-spec.md",
        "image-mode.md",
        "plot-mode.md",
        "mixed-mode.md",
        "natural-language-plot-workflow.md",
        "publication-plot-api.md",
        "publication-chart-patterns.md",
        "publication-figure-design.md",
        "mathematical-modeling.md",
        "chinese-labels.md",
        "gpt-image-2-guidance.md",
        "openai-image-workflow.md",
        "codex-cc-switch.md",
        "image-execution-reliability.md",
        "highres-policy.md",
        "editable-figure-handoff.md",
        "reproducibility-chain.md",
        "quality-gates.md",
    ]
    for name in expected:
        assert name in index
        assert (ROOT / "references" / name).is_file()
