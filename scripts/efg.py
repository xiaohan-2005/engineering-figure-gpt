#!/usr/bin/env python3
"""Unified CLI for Engineering Figure GPT.

The user-facing CLI keeps intermediate JSON and prompt files optional:

- `efg image --figure-template ...` builds the final prompt and generates in one command.
- `efg plot request.json` normalizes the request and renders in one command.
- `efg render spec.json` remains available when a normalized plot spec already exists.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(parts: list[str]) -> int:
    return subprocess.call([sys.executable, *parts], cwd=ROOT)


def add_image_runtime_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-image", action="append", default=[], help="Input image for editing; may be repeated.")
    parser.add_argument("--model")
    parser.add_argument("--base-url")
    parser.add_argument("--allow-third-party", action="store_true")
    parser.add_argument("--api-key-file")
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"))
    parser.add_argument("--size")
    parser.add_argument("--output-format", choices=("png", "jpeg", "webp"))
    parser.add_argument(
        "--background",
        dest="image_background",
        choices=("transparent", "opaque", "auto"),
        help="Image canvas background setting forwarded to the Images API; distinct from the scientific background text.",
    )
    parser.add_argument("--input-fidelity", choices=("low", "high"))
    parser.add_argument("--n", type=int)
    parser.add_argument("--out-dir")
    parser.add_argument("--prefix")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--highres", action="store_true", help="Use the configured final/high-resolution model route and fail closed if unavailable.")
    parser.add_argument("--final", action="store_true", help="Alias for final-quality/high-resolution routing.")
    parser.add_argument("--dry-run", action="store_true")


def image_runtime_args(args: argparse.Namespace) -> list[str]:
    parts: list[str] = []
    for value in getattr(args, "input_image", []) or []:
        parts += ["--input-image", str(value)]

    scalar = (
        ("model", "--model"),
        ("base_url", "--base-url"),
        ("api_key_file", "--api-key-file"),
        ("quality", "--quality"),
        ("size", "--size"),
        ("output_format", "--output-format"),
        ("image_background", "--background"),
        ("input_fidelity", "--input-fidelity"),
        ("n", "--n"),
        ("out_dir", "--out-dir"),
        ("prefix", "--prefix"),
        ("timeout", "--timeout"),
    )
    for attr, flag in scalar:
        value = getattr(args, attr, None)
        if value is not None:
            parts += [flag, str(value)]

    if getattr(args, "allow_third_party", False):
        parts.append("--allow-third-party")
    if getattr(args, "highres", False):
        parts.append("--highres")
    if getattr(args, "final", False):
        parts.append("--final")
    if getattr(args, "dry_run", False):
        parts.append("--dry-run")
    return parts


def cmd_prompt(args: argparse.Namespace) -> int:
    cmd = [str(SCRIPTS / "build_engineering_figure_prompt.py"), "--figure-template", args.figure_template]
    if args.lang:
        cmd += ["--lang", args.lang]
    if args.style_note:
        cmd += ["--style-note", args.style_note]
    if args.background_file:
        cmd += ["--background-file", args.background_file]
    if args.out:
        cmd += ["--out", args.out]
    if args.background:
        cmd += [args.background]
    return run(cmd)


def cmd_image(args: argparse.Namespace) -> int:
    generator = str(SCRIPTS / "generate_image.py")
    runtime = image_runtime_args(args)

    if not args.figure_template:
        if args.background_file:
            return run([generator, "--prompt-file", args.background_file, *runtime])
        if not args.background:
            print("Provide prompt/background text, --background-file, or --figure-template.", file=sys.stderr)
            return 2
        return run([generator, args.background, *runtime])

    if not args.background and not args.background_file:
        print("Template image mode requires background text or --background-file.", file=sys.stderr)
        return 2

    def execute_with_prompt_path(prompt_path: Path) -> int:
        build = [
            str(SCRIPTS / "build_engineering_figure_prompt.py"),
            "--figure-template",
            args.figure_template,
            "--out",
            str(prompt_path),
        ]
        if args.lang:
            build += ["--lang", args.lang]
        if args.style_note:
            build += ["--style-note", args.style_note]
        if args.background_file:
            build += ["--background-file", args.background_file]
        if args.background:
            build += [args.background]
        code = run(build)
        if code:
            return code
        return run([generator, "--prompt-file", str(prompt_path), *runtime])

    if args.save_prompt:
        prompt_path = Path(args.save_prompt)
        if not prompt_path.is_absolute():
            prompt_path = ROOT / prompt_path
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        return execute_with_prompt_path(prompt_path)

    with tempfile.TemporaryDirectory(prefix="efg-prompt-") as tmp:
        return execute_with_prompt_path(Path(tmp) / "final-prompt.txt")


def cmd_build_plot(args: argparse.Namespace) -> int:
    return run([str(SCRIPTS / "build_plot_spec.py"), args.request_file, "--out", args.out])


def cmd_render(args: argparse.Namespace) -> int:
    return run([
        str(SCRIPTS / "plot_publication_figure.py"),
        args.spec_file,
        "--out-path",
        args.out_path,
        "--formats",
        *args.formats,
    ])


def cmd_plot(args: argparse.Namespace) -> int:
    spec_out = Path(args.spec_out)
    if not spec_out.is_absolute():
        spec_out = ROOT / spec_out
    spec_out.parent.mkdir(parents=True, exist_ok=True)
    code = run([str(SCRIPTS / "build_plot_spec.py"), args.request_file, "--out", str(spec_out)])
    if code:
        return code
    return run([
        str(SCRIPTS / "plot_publication_figure.py"),
        str(spec_out),
        "--out-path",
        args.out_path,
        "--formats",
        *args.formats,
    ])


def cmd_provider_check(args: argparse.Namespace) -> int:
    command = [str(SCRIPTS / "generate_image.py"), "--check-provider"]
    if args.base_url:
        command += ["--base-url", args.base_url]
    if args.model:
        command += ["--model", args.model]
    if args.api_key_file:
        command += ["--api-key-file", args.api_key_file]
    if args.allow_third_party:
        command += ["--allow-third-party"]
    if args.timeout is not None:
        command += ["--timeout", str(args.timeout)]
    return run(command)


def cmd_check(_: argparse.Namespace) -> int:
    required = [
        "SKILL.md",
        "assets/prompt-templates/engineering-figure-templates.json",
        "assets/prompt-templates/mathematical-modeling-templates.json",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Engineering Figure GPT CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    prompt = sub.add_parser("prompt", help="Build a conceptual-figure prompt without network calls.")
    prompt.add_argument("background", nargs="?")
    prompt.add_argument("--background-file")
    prompt.add_argument("--figure-template", required=True)
    prompt.add_argument("--lang", choices=("en", "zh"))
    prompt.add_argument("--style-note")
    prompt.add_argument("--out")
    prompt.set_defaults(func=cmd_prompt)

    image = sub.add_parser("image", help="Build an optional figure-template prompt and generate/edit in one command.")
    image.add_argument("background", nargs="?", help="Raw final prompt, or scientific background when --figure-template is used.")
    image.add_argument("--background-file", help="UTF-8 prompt/background file.")
    image.add_argument("--figure-template")
    image.add_argument("--lang", choices=("en", "zh"))
    image.add_argument("--style-note")
    image.add_argument("--save-prompt", help="Preserve the resolved final prompt for reproducibility.")
    add_image_runtime_options(image)
    image.set_defaults(func=cmd_image)

    build = sub.add_parser("build-plot", help="Normalize a concise plot request JSON only.")
    build.add_argument("request_file")
    build.add_argument("--out", required=True)
    build.set_defaults(func=cmd_build_plot)

    plot = sub.add_parser("plot", help="Normalize a concise plot request and render it in one command.")
    plot.add_argument("request_file")
    plot.add_argument("--spec-out", default="output/plot-spec.json")
    plot.add_argument("--out-path", default="output/publication-figure")
    plot.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"])
    plot.set_defaults(func=cmd_plot)

    render = sub.add_parser("render", help="Render an already normalized exact plot spec.")
    render.add_argument("spec_file")
    render.add_argument("--out-path", default="output/publication-figure")
    render.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"])
    render.set_defaults(func=cmd_render)

    provider = sub.add_parser("provider-check", help="Probe an official or explicitly trusted OpenAI-compatible relay without generating an image.")
    provider.add_argument("--base-url")
    provider.add_argument("--model")
    provider.add_argument("--api-key-file")
    provider.add_argument("--allow-third-party", action="store_true")
    provider.add_argument("--timeout", type=int)
    provider.set_defaults(func=cmd_provider_check)

    check = sub.add_parser("check", help="Run offline smoke checks without spending image API credits.")
    check.set_defaults(func=cmd_check)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
