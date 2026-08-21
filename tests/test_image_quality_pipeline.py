from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_figure_prompt_injects_publication_quality_contract():
    module = load_module(ROOT / "scripts/build_engineering_figure_prompt.py", "efg_prompt_builder")
    prompt = module.build_prompt(
        "system-architecture",
        "OCR -> embedding -> reranking -> answer synthesis",
        "en",
        None,
        "paper",
    )
    assert "Publication Image Quality Contract" in prompt
    assert "50%" in prompt
    assert "micro-text" in prompt
    assert "safe outer margin" in prompt


def test_correct_edit_prompt_is_preservation_first():
    module = load_module(ROOT / "scripts/build_image_edit_prompt.py", "efg_edit_prompt")
    prompt = module.build_edit_prompt(
        "Change Encoder to Cross-Attention Encoder only",
        "correct",
        "en",
        preserve=["all arrow endpoints"],
        allow_change=["Encoder label text"],
        quality_profile="paper",
    )
    assert "smallest possible correction" in prompt
    assert "every unaffected label" in prompt
    assert "all arrow endpoints" in prompt
    assert "Encoder label text" in prompt
    assert "do not treat this as a from-scratch generation task" in prompt


def test_efg_edit_dry_run_resolves_to_edit_mode(tmp_path):
    image = tmp_path / "source.png"
    image.write_bytes(b"placeholder")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/efg.py"),
            "edit",
            str(image),
            "Fix one label only",
            "--mode",
            "correct",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert '"mode": "edit"' in proc.stdout
    assert '"quality": "high"' in proc.stdout


def test_verify_image_output_accepts_expected_dimensions(tmp_path):
    image = tmp_path / "figure.png"
    Image.new("RGB", (1536, 1024), "white").save(image)
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/verify_image_output.py"),
            str(image),
            "--expected-size",
            "1536x1024",
            "--require-format",
            "png",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "[PASS]" in proc.stdout


def test_verify_image_output_rejects_size_mismatch(tmp_path):
    image = tmp_path / "figure.png"
    Image.new("RGB", (1024, 1024), "white").save(image)
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/verify_image_output.py"),
            str(image),
            "--expected-size",
            "1536x1024",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "size-mismatch" in proc.stdout
