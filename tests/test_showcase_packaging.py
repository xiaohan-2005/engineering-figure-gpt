from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package_showcase_example.py"
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_package_image_example_requires_real_output_and_builds_manifest(tmp_path):
    brief = write(tmp_path / "brief-source.md", "# Brief\nreal brief\n")
    prompt = write(tmp_path / "resolved-prompt.txt", "publication figure prompt\n")
    verification = write(tmp_path / "verification-source.md", "# Verification\nlabels checked\n")
    output = tmp_path / "generated.png"
    output.write_bytes(ONE_PIXEL_PNG)
    destination = tmp_path / "examples"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--slug",
            "test-image-case",
            "--mode",
            "image",
            "--brief",
            str(brief),
            "--source",
            f"{prompt}=prompt.txt",
            "--output",
            str(output),
            "--verification",
            str(verification),
            "--model",
            "gpt-image-2",
            "--quality",
            "high",
            "--size",
            "1536x1024",
            "--check",
            "labels checked",
            "--destination",
            str(destination),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    target = destination / "test-image-case"
    assert (target / "brief.md").is_file()
    assert (target / "prompt.txt").is_file()
    assert (target / "output.png").stat().st_size > 0
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["output_artifact"] == "output.png"
    assert manifest["model"] == "gpt-image-2"
    assert manifest["verification"] == ["labels checked"]


def test_package_plot_example_requires_request_and_spec(tmp_path):
    brief = write(tmp_path / "brief.md", "brief")
    verification = write(tmp_path / "verification.md", "verified")
    request = write(tmp_path / "request-source.json", "{}")
    spec = write(tmp_path / "spec-source.json", "{}")
    output = write(tmp_path / "plot.svg", "<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>")
    destination = tmp_path / "examples"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--slug",
            "test-plot-case",
            "--mode",
            "plot",
            "--brief",
            str(brief),
            "--source",
            f"{request}=request.json",
            "--source",
            f"{spec}=plot-spec.json",
            "--output",
            str(output),
            "--verification",
            str(verification),
            "--destination",
            str(destination),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    target = destination / "test-plot-case"
    assert (target / "request.json").is_file()
    assert (target / "plot-spec.json").is_file()
    assert (target / "output.svg").is_file()


def test_package_image_example_rejects_missing_prompt(tmp_path):
    brief = write(tmp_path / "brief.md", "brief")
    verification = write(tmp_path / "verification.md", "verified")
    output = write(tmp_path / "out.svg", "<svg></svg>")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--slug",
            "missing-prompt",
            "--mode",
            "image",
            "--brief",
            str(brief),
            "--output",
            str(output),
            "--verification",
            str(verification),
            "--destination",
            str(tmp_path / "examples"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "prompt.txt" in result.stderr


def test_packaging_refuses_empty_output(tmp_path):
    brief = write(tmp_path / "brief.md", "brief")
    prompt = write(tmp_path / "prompt.txt", "prompt")
    verification = write(tmp_path / "verification.md", "verified")
    output = tmp_path / "empty.png"
    output.write_bytes(b"")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--slug",
            "empty-output",
            "--mode",
            "image",
            "--brief",
            str(brief),
            "--source",
            f"{prompt}=prompt.txt",
            "--output",
            str(output),
            "--verification",
            str(verification),
            "--destination",
            str(tmp_path / "examples"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Output is empty" in result.stderr


def test_packaging_refuses_fake_png_signature(tmp_path):
    brief = write(tmp_path / "brief.md", "brief")
    prompt = write(tmp_path / "prompt.txt", "prompt")
    verification = write(tmp_path / "verification.md", "verified")
    output = tmp_path / "fake.png"
    output.write_bytes(b"this is not actually a PNG")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--slug",
            "fake-png",
            "--mode",
            "image",
            "--brief",
            str(brief),
            "--source",
            f"{prompt}=prompt.txt",
            "--output",
            str(output),
            "--verification",
            str(verification),
            "--destination",
            str(tmp_path / "examples"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "signature does not match" in result.stderr
