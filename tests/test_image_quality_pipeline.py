from __future__ import annotations

import argparse
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


def test_edit_runtime_args_do_not_split_positional_image_path():
    module = load_module(ROOT / "scripts/efg.py", "efg_unified_cli")
    args = argparse.Namespace(input_image="figure.png")
    runtime = module.image_runtime_args(args, include_input_images=False)
    assert "--input-image" not in runtime
    assert "figure.png" not in runtime


def test_image_runtime_args_forward_real_image_lists_only():
    module = load_module(ROOT / "scripts/efg.py", "efg_unified_cli_images")
    args = argparse.Namespace(input_image=["one.png", "two.png"])
    runtime = module.image_runtime_args(args, include_input_images=True)
    assert runtime == ["--input-image", "one.png", "--input-image", "two.png"]


def test_efg_edit_dry_run_preserves_legal_source_canvas(tmp_path):
    image = tmp_path / "source.png"
    Image.new("RGB", (1536, 1024), "white").save(image)
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
    assert '"size": "1536x1024"' in proc.stdout
    assert '"input_fidelity": null' in proc.stdout
    assert "Preserving source canvas" in proc.stderr


def test_efg_draft_profile_uses_low_quality(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/efg.py"),
            "image",
            "simple research workflow",
            "--quality-profile",
            "draft",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert '"quality": "low"' in proc.stdout
    assert '"size": "1024x1024"' in proc.stdout


def test_efg_final_profile_uses_larger_canvas_without_forcing_highres_route():
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/efg.py"),
            "image",
            "simple research workflow",
            "--quality-profile",
            "final",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert '"model": "gpt-image-2"' in proc.stdout
    assert '"final_quality_requested": false' in proc.stdout
    assert '"quality": "high"' in proc.stdout
    assert '"size": "2048x1152"' in proc.stdout


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
