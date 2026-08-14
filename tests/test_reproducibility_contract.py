from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reproducibility_guidance_exists():
    reference = ROOT / "references" / "reproducibility-chain.md"
    gallery = ROOT / "docs" / "examples" / "README.md"
    assert reference.is_file()
    assert gallery.is_file()
    text = reference.read_text(encoding="utf-8")
    assert "Figure Brief" in text
    assert "Real GPT Output" in text
    assert "Plot Request" in text
