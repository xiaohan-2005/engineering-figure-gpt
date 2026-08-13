#!/usr/bin/env python3
"""Unified CLI for Engineering Figure GPT."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(parts: list[str]) -> int:
    return subprocess.call([sys.executable, *parts], cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="Engineering Figure GPT CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    prompt = sub.add_parser("prompt", help="Build a conceptual-figure prompt.")
    prompt.add_argument("background")
    prompt.add_argument("--figure-template", required=True)
    prompt.add_argument("--lang", choices=("en", "zh"))
    prompt.add_argument("--style-note")
    prompt.add_argument("--out")

    image = sub.add_parser("image", help="GPT Image 2 CLI fallback; Codex built-in image generation is preferred in-agent.")
    image.add_argument("args", nargs=argparse.REMAINDER)

    build = sub.add_parser("build-plot", help="Normalize a concise plot request JSON.")
    build.add_argument("request_file")
    build.add_argument("--out", required=True)

    plot = sub.add_parser("plot", help="Render a normalized exact plot spec.")
    plot.add_argument("spec_file")
    plot.add_argument("--out-path", default="output/publication-figure")
    plot.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"])

    sub.add_parser("check", help="Run offline smoke checks without spending image API credits.")
    args = parser.parse_args()

    if args.command == "prompt":
        cmd = [str(SCRIPTS / "build_engineering_figure_prompt.py"), "--figure-template", args.figure_template]
        if args.lang:
            cmd += ["--lang", args.lang]
        if args.style_note:
            cmd += ["--style-note", args.style_note]
        if args.out:
            cmd += ["--out", args.out]
        cmd += [args.background]
        return run(cmd)

    if args.command == "image":
        return run([str(SCRIPTS / "generate_image.py"), *args.args])

    if args.command == "build-plot":
        return run([str(SCRIPTS / "build_plot_spec.py"), args.request_file, "--out", args.out])

    if args.command == "plot":
        return run([str(SCRIPTS / "plot_publication_figure.py"), args.spec_file, "--out-path", args.out_path, "--formats", *args.formats])

    required = [
        "SKILL.md",
        "assets/prompt-templates/engineering-figure-templates.json",
        "scripts/build_engineering_figure_prompt.py",
        "scripts/build_plot_spec.py",
        "scripts/plot_publication_figure.py",
        "scripts/generate_image.py",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    if missing:
        print("Missing runtime files:", *missing, sep="\n  - ", file=sys.stderr)
        return 1
    code = run([str(SCRIPTS / "build_engineering_figure_prompt.py"), "--figure-template", "system-architecture", "offline smoke test"])
    if code:
        return code
    return run([str(SCRIPTS / "generate_image.py"), "offline smoke test", "--dry-run"])


if __name__ == "__main__":
    raise SystemExit(main())
