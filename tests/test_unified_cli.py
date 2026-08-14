from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EFG = ROOT / "scripts" / "efg.py"


def test_template_image_dry_run_builds_prompt_and_resolves_image_command(tmp_path):
    prompt_out = tmp_path / "final-prompt.txt"
    proc = subprocess.run(
        [
            sys.executable,
            str(EFG),
            "image",
            "A retrieval system with OCR, embeddings, reranking, and answer synthesis.",
            "--figure-template",
            "system-architecture",
            "--lang",
            "en",
            "--save-prompt",
            str(prompt_out),
            "--dry-run",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert prompt_out.is_file()
    assert "retrieval" in prompt_out.read_text(encoding="utf-8").lower()
    assert '"mode": "generate"' in proc.stdout
    assert '"model": "gpt-image-2"' in proc.stdout


def test_plot_command_builds_spec_and_renders_in_one_step(tmp_path):
    request = ROOT / "examples" / "benchmark-plot-request.json"
    spec = tmp_path / "normalized.json"
    out = tmp_path / "figure"
    proc = subprocess.run(
        [
            sys.executable,
            str(EFG),
            "plot",
            str(request),
            "--spec-out",
            str(spec),
            "--out-path",
            str(out),
            "--formats",
            "png",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert spec.is_file()
    assert (tmp_path / "figure.png").is_file()
    assert (tmp_path / "figure.png").stat().st_size > 0


def test_render_command_accepts_normalized_spec(tmp_path):
    request = ROOT / "examples" / "benchmark-plot-request.json"
    spec = tmp_path / "normalized.json"
    build = subprocess.run(
        [sys.executable, str(EFG), "build-plot", str(request), "--out", str(spec)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert build.returncode == 0, build.stderr

    out = tmp_path / "rendered"
    render = subprocess.run(
        [sys.executable, str(EFG), "render", str(spec), "--out-path", str(out), "--formats", "png"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert render.returncode == 0, render.stderr
    assert (tmp_path / "rendered.png").is_file()
