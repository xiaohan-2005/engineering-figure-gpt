#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def main():
    parser = argparse.ArgumentParser(description="Engineering Figure GPT CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    prompt = sub.add_parser("prompt")
    prompt.add_argument("background")
    prompt.add_argument("--figure-template", required=True)
    prompt.add_argument("--lang", choices=("en", "zh"), default="zh")

    plot = sub.add_parser("plot")
    plot.add_argument("spec_file")
    plot.add_argument("--out-path", default="output/publication-figure")

    sub.add_parser("check")
    args = parser.parse_args()

    if args.command == "prompt":
        cmd = [sys.executable, str(SCRIPTS / "build_engineering_figure_prompt.py"), "--figure-template", args.figure_template, "--lang", args.lang, args.background]
    elif args.command == "plot":
        cmd = [sys.executable, str(SCRIPTS / "plot_publication_figure.py"), args.spec_file, "--out-path", args.out_path]
    else:
        cmd = [sys.executable, str(SCRIPTS / "build_engineering_figure_prompt.py"), "--figure-template", "system-architecture", "offline smoke test"]

    raise SystemExit(subprocess.call(cmd, cwd=ROOT))


if __name__ == "__main__":
    main()
