from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_quality_gates_documented():
    path = ROOT / "references" / "quality-gates.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Runtime pruning" in text
    assert "Plot renderer E2E" in text
    assert "GPT image fallback" in text
