#!/usr/bin/env python3
"""Unified CLI for Engineering Figure GPT.

User-facing workflows:
- `efg image`: generate a conceptual figure with a publication-quality contract.
- `efg edit`: preservation-first correction/revision/restyling/redrawing.
- `efg verify-image`: verify objective raster metadata.
- `efg plot` / `efg render`: deterministic quantitative figures.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
QUALITY_PATH = ROOT / "assets" / "prompt-templates" / "image-quality-contracts.json"
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_IMAGE_MODEL = "gpt-image-2"

GPT2_MIN_PIXELS = 655_360
GPT2_MAX_PIXELS = 8_294_400
GPT2_MAX_EDGE = 3840
GPT2_MAX_ASPECT = 3.0

PROFILE_QUALITY = {"draft": "low", "paper": "high", "final": "high"}
PROFILE_SIZE = {"draft": "1024x1024", "paper": "1536x1024", "final": "2048x1152"}


def run(parts: list[str]) -> int:
    return subprocess.call([sys.executable, *parts], cwd=ROOT)


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))


def load_quality_contract(profile: str, lang: str) -> str:
    data = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    if profile not in data or lang not in data[profile]:
        raise SystemExit(f"Missing image quality contract: {profile}/{lang}")
    return str(data[profile][lang]).strip()


def resolve_quality_profile(args: argparse.Namespace) -> str:
    explicit = getattr(args, "quality_profile", None)
    if explicit:
        return explicit
    if getattr(args, "final", False) or getattr(args, "highres", False):
        return "final"
    return "paper"


def build_raw_image_prompt(text: str, lang: str | None, style_note: str | None, profile: str) -> str:
    resolved_lang = lang or ("zh" if contains_chinese(text) else "en")
    if resolved_lang == "zh":
        prompt = f"{text.strip()}\n\n论文图像质量约束：\n{load_quality_contract(profile, 'zh')}"
        if style_note:
            prompt += f"\n\n附加风格要求：\n{style_note.strip()}"
        return prompt
    prompt = f"{text.strip()}\n\nPublication Image Quality Contract:\n{load_quality_contract(profile, 'en')}"
    if style_note:
        prompt += f"\n\nAdditional style requirements:\n{style_note.strip()}"
    return prompt


def parse_size(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise ValueError(f"Invalid size: {value}")
    return int(match.group(1)), int(match.group(2))


def valid_gpt_image_2_size(width: int, height: int) -> bool:
    if width <= 0 or height <= 0:
        return False
    if width > GPT2_MAX_EDGE or height > GPT2_MAX_EDGE:
        return False
    if width % 16 or height % 16:
        return False
    ratio = max(width, height) / min(width, height)
    pixels = width * height
    return ratio <= GPT2_MAX_ASPECT and GPT2_MIN_PIXELS <= pixels <= GPT2_MAX_PIXELS


def nearest_gpt_image_2_size(width: int, height: int) -> tuple[int, int]:
    """Return a close legal GPT Image 2 output size while preserving aspect approximately."""
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive.")
    ratio = max(width, height) / min(width, height)
    if ratio > GPT2_MAX_ASPECT:
        raise ValueError(
            f"Source aspect ratio {ratio:.3f}:1 exceeds GPT Image 2's 3:1 output limit; pass --size explicitly after padding/cropping."
        )

    scale = 1.0
    max_edge = max(width, height)
    pixels = width * height
    if max_edge > GPT2_MAX_EDGE:
        scale = min(scale, GPT2_MAX_EDGE / max_edge)
    if pixels > GPT2_MAX_PIXELS:
        scale = min(scale, math.sqrt(GPT2_MAX_PIXELS / pixels))
    if pixels < GPT2_MIN_PIXELS:
        scale = max(scale, math.sqrt(GPT2_MIN_PIXELS / pixels))

    base_w = max(16, round(width * scale / 16) * 16)
    base_h = max(16, round(height * scale / 16) * 16)

    candidates: list[tuple[float, int, int]] = []
    source_ratio = width / height
    for dw in range(-128, 129, 16):
        for dh in range(-128, 129, 16):
            w = base_w + dw
            h = base_h + dh
            if not valid_gpt_image_2_size(w, h):
                continue
            ratio_error = abs((w / h) - source_ratio) / max(abs(source_ratio), 1e-9)
            scale_error = abs((w * h) - (width * height * scale * scale)) / max(width * height * scale * scale, 1)
            candidates.append((ratio_error * 10 + scale_error, w, h))
    if not candidates:
        raise ValueError("Could not derive a legal GPT Image 2 output size close to the source canvas.")
    _, best_w, best_h = min(candidates)
    return best_w, best_h


def read_raster_size(path: str) -> tuple[int, int]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow is required for edit canvas preservation. Install requirements.txt.") from exc
    with Image.open(path) as image:
        return int(image.width), int(image.height)


def intended_image_model(args: argparse.Namespace) -> str:
    if getattr(args, "model", None):
        return str(args.model)
    if getattr(args, "final", False) or getattr(args, "highres", False):
        return os.getenv("OPENAI_IMAGE_HIGHRES_MODEL", "").strip()
    return os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL).strip() or DEFAULT_IMAGE_MODEL


def apply_profile_defaults(args: argparse.Namespace, profile: str, *, editing: bool = False) -> None:
    if getattr(args, "quality", None) is None and not os.getenv("OPENAI_IMAGE_QUALITY"):
        args.quality = PROFILE_QUALITY[profile]
    if getattr(args, "output_format", None) is None and not os.getenv("OPENAI_IMAGE_OUTPUT_FORMAT"):
        args.output_format = "png"
    if not editing and getattr(args, "size", None) is None and not os.getenv("OPENAI_IMAGE_SIZE"):
        args.size = PROFILE_SIZE[profile]


def resolve_edit_canvas(args: argparse.Namespace) -> int:
    """Preserve the source raster canvas by default for GPT Image 2 edits."""
    if getattr(args, "size", None) or os.getenv("OPENAI_IMAGE_SIZE"):
        return 0

    model = intended_image_model(args)
    if not model:
        print(
            "Final/high-resolution model is not configured, so edit canvas preservation cannot resolve the target model yet.",
            file=sys.stderr,
        )
        return 0

    if not model.startswith("gpt-image-2"):
        if args.mode == "correct":
            print(
                "Preservation-first correct mode requires an explicit --size for non-GPT-Image-2 models; "
                "the skill will not silently change the canvas.",
                file=sys.stderr,
            )
            return 2
        args.size = "auto"
        print(
            f"[WARN] Model '{model}' is not GPT Image 2; edit output size is left to the provider (size=auto).",
            file=sys.stderr,
        )
        return 0

    try:
        width, height = read_raster_size(args.input_image)
    except Exception as exc:
        print(f"Could not inspect source image dimensions: {exc}", file=sys.stderr)
        return 2

    if valid_gpt_image_2_size(width, height):
        args.size = f"{width}x{height}"
        print(f"[INFO] Preserving source canvas for GPT Image 2 edit: {args.size}", file=sys.stderr)
        return 0

    try:
        new_w, new_h = nearest_gpt_image_2_size(width, height)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    args.size = f"{new_w}x{new_h}"
    print(
        f"[WARN] Source canvas {width}x{height} is not a legal GPT Image 2 output size; "
        f"using nearest legal canvas {args.size}. Pass --size explicitly to override.",
        file=sys.stderr,
    )
    return 0


def add_image_runtime_options(parser: argparse.ArgumentParser, include_input_images: bool = True) -> None:
    if include_input_images:
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
        help="Image canvas background setting forwarded to the Images API.",
    )
    parser.add_argument(
        "--input-fidelity",
        choices=("low", "high"),
        help="Only for image models/endpoints that support this parameter. GPT Image 2 rejects it because input fidelity is always high.",
    )
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


def resolve_prompt_output_path(save_prompt: str | None, temp_dir: str) -> Path:
    if save_prompt:
        path = Path(save_prompt)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return Path(temp_dir) / "final-prompt.txt"


def resolved_requested_size(args: argparse.Namespace) -> str | None:
    value = getattr(args, "size", None) or os.getenv("OPENAI_IMAGE_SIZE")
    return str(value) if value else None


def resolved_requested_format(args: argparse.Namespace) -> str:
    return str(getattr(args, "output_format", None) or os.getenv("OPENAI_IMAGE_OUTPUT_FORMAT", "png"))


def output_paths_from_stdout(stdout: str) -> list[str]:
    paths: list[str] = []
    for line in stdout.splitlines():
        text = line.strip()
        if not text or text.startswith("{") or text.startswith("["):
            continue
        candidate = Path(text)
        if candidate.suffix.lower() in RASTER_SUFFIXES:
            paths.append(text)
    return paths


def run_image_and_verify(args: argparse.Namespace, command: list[str]) -> int:
    proc = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        return proc.returncode
    if getattr(args, "dry_run", False):
        return 0
    outputs = output_paths_from_stdout(proc.stdout)
    if not outputs:
        print("Image command succeeded but no raster output path could be verified.", file=sys.stderr)
        return 1
    verify_command = [str(SCRIPTS / "verify_image_output.py"), *outputs]
    expected_size = resolved_requested_size(args)
    if expected_size and expected_size.lower() != "auto":
        verify_command += ["--expected-size", expected_size]
    expected_format = resolved_requested_format(args)
    if expected_format:
        verify_command += ["--require-format", expected_format]
    return run(verify_command)


def cmd_prompt(args: argparse.Namespace) -> int:
    cmd = [
        str(SCRIPTS / "build_engineering_figure_prompt.py"),
        "--figure-template", args.figure_template,
        "--quality-profile", args.quality_profile,
    ]
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
    profile = resolve_quality_profile(args)
    apply_profile_defaults(args, profile, editing=False)
    runtime = image_runtime_args(args)
    with tempfile.TemporaryDirectory(prefix="efg-prompt-") as tmp:
        prompt_path = resolve_prompt_output_path(args.save_prompt, tmp)
        if args.figure_template:
            if not args.background and not args.background_file:
                print("Template image mode requires background text or --background-file.", file=sys.stderr)
                return 2
            build = [
                str(SCRIPTS / "build_engineering_figure_prompt.py"),
                "--figure-template", args.figure_template,
                "--quality-profile", profile,
                "--out", str(prompt_path),
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
        else:
            raw = args.background
            if args.background_file:
                raw = Path(args.background_file).read_text(encoding="utf-8")
            if not raw:
                print("Provide prompt/background text, --background-file, or --figure-template.", file=sys.stderr)
                return 2
            prompt_path.write_text(build_raw_image_prompt(raw, args.lang, args.style_note, profile) + "\n", encoding="utf-8")
        return run_image_and_verify(args, [generator, "--prompt-file", str(prompt_path), *runtime])


def cmd_edit(args: argparse.Namespace) -> int:
    generator = str(SCRIPTS / "generate_image.py")
    profile = resolve_quality_profile(args)
    apply_profile_defaults(args, profile, editing=True)

    images = [args.input_image, *(args.reference_image or [])]
    for image in images:
        if not Path(image).is_file():
            print(f"Input/reference image not found: {image}", file=sys.stderr)
            return 2

    canvas_code = resolve_edit_canvas(args)
    if canvas_code:
        return canvas_code
    runtime = image_runtime_args(args)

    with tempfile.TemporaryDirectory(prefix="efg-edit-") as tmp:
        prompt_path = resolve_prompt_output_path(args.save_prompt, tmp)
        build = [
            str(SCRIPTS / "build_image_edit_prompt.py"),
            args.instruction,
            "--mode", args.mode,
            "--quality-profile", profile,
            "--out", str(prompt_path),
        ]
        if args.lang:
            build += ["--lang", args.lang]
        for value in args.preserve:
            build += ["--preserve", value]
        for value in args.allow_change:
            build += ["--allow-change", value]
        code = run(build)
        if code:
            return code
        image_args: list[str] = []
        for image in images:
            image_args += ["--input-image", image]
        return run_image_and_verify(args, [generator, "--prompt-file", str(prompt_path), *image_args, *runtime])


def cmd_verify_image(args: argparse.Namespace) -> int:
    command = [str(SCRIPTS / "verify_image_output.py"), *args.images]
    scalar = (
        ("expected_size", "--expected-size"),
        ("min_width", "--min-width"),
        ("min_height", "--min-height"),
        ("min_megapixels", "--min-megapixels"),
        ("target_aspect", "--target-aspect"),
        ("aspect_tolerance", "--aspect-tolerance"),
        ("require_format", "--require-format"),
    )
    for attr, flag in scalar:
        value = getattr(args, attr, None)
        if value is not None:
            command += [flag, str(value)]
    if args.json:
        command.append("--json")
    return run(command)


def cmd_build_plot(args: argparse.Namespace) -> int:
    return run([str(SCRIPTS / "build_plot_spec.py"), args.request_file, "--out", args.out])


def cmd_render(args: argparse.Namespace) -> int:
    return run([str(SCRIPTS / "plot_publication_figure.py"), args.spec_file, "--out-path", args.out_path, "--formats", *args.formats])


def cmd_plot(args: argparse.Namespace) -> int:
    spec_out = Path(args.spec_out)
    if not spec_out.is_absolute():
        spec_out = ROOT / spec_out
    spec_out.parent.mkdir(parents=True, exist_ok=True)
    code = run([str(SCRIPTS / "build_plot_spec.py"), args.request_file, "--out", str(spec_out)])
    if code:
        return code
    return run([str(SCRIPTS / "plot_publication_figure.py"), str(spec_out), "--out-path", args.out_path, "--formats", *args.formats])


def cmd_provider_check(args: argparse.Namespace) -> int:
    command = [str(SCRIPTS / "generate_image.py"), "--check-provider"]
    for attr, flag in (("base_url", "--base-url"), ("model", "--model"), ("api_key_file", "--api-key-file"), ("timeout", "--timeout")):
        value = getattr(args, attr, None)
        if value is not None:
            command += [flag, str(value)]
    if args.allow_third_party:
        command += ["--allow-third-party"]
    return run(command)


def cmd_check(_: argparse.Namespace) -> int:
    required = [
        "SKILL.md",
        "assets/prompt-templates/engineering-figure-templates.json",
        "assets/prompt-templates/mathematical-modeling-templates.json",
        "assets/prompt-templates/image-quality-contracts.json",
        "scripts/build_engineering_figure_prompt.py",
        "scripts/build_image_edit_prompt.py",
        "scripts/build_plot_spec.py",
        "scripts/plot_publication_figure.py",
        "scripts/generate_image.py",
        "scripts/verify_image_output.py",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    if missing:
        print("Missing runtime files:", *missing, sep="\n  - ", file=sys.stderr)
        return 1
    code = run([str(SCRIPTS / "build_engineering_figure_prompt.py"), "--figure-template", "system-architecture", "--quality-profile", "paper", "offline smoke test"])
    if code:
        return code
    code = run([str(SCRIPTS / "build_image_edit_prompt.py"), "fix one label only", "--mode", "correct"])
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
    prompt.add_argument("--quality-profile", choices=("draft", "paper", "final"), default="paper")
    prompt.add_argument("--out")
    prompt.set_defaults(func=cmd_prompt)

    image = sub.add_parser("image", help="Generate a conceptual figure with a publication image-quality contract.")
    image.add_argument("background", nargs="?", help="Raw prompt/background, or scientific background with --figure-template.")
    image.add_argument("--background-file", help="UTF-8 prompt/background file.")
    image.add_argument("--figure-template")
    image.add_argument("--lang", choices=("en", "zh"))
    image.add_argument("--style-note")
    image.add_argument("--quality-profile", choices=("draft", "paper", "final"), default=None)
    image.add_argument("--save-prompt")
    add_image_runtime_options(image)
    image.set_defaults(func=cmd_image)

    edit = sub.add_parser("edit", help="Edit an existing research figure with explicit preservation rules.")
    edit.add_argument("input_image", help="Primary raster figure to modify.")
    edit.add_argument("instruction", help="Exact requested change.")
    edit.add_argument("--mode", choices=("correct", "revise", "restyle", "redraw"), default="correct")
    edit.add_argument("--reference-image", action="append", default=[])
    edit.add_argument("--preserve", action="append", default=[])
    edit.add_argument("--allow-change", action="append", default=[])
    edit.add_argument("--lang", choices=("en", "zh"))
    edit.add_argument("--quality-profile", choices=("draft", "paper", "final"), default=None)
    edit.add_argument("--save-prompt")
    add_image_runtime_options(edit, include_input_images=False)
    edit.set_defaults(func=cmd_edit)

    verify_image = sub.add_parser("verify-image", help="Verify objective pixel/format/aspect constraints for raster outputs.")
    verify_image.add_argument("images", nargs="+")
    verify_image.add_argument("--expected-size")
    verify_image.add_argument("--min-width", type=int)
    verify_image.add_argument("--min-height", type=int)
    verify_image.add_argument("--min-megapixels", type=float)
    verify_image.add_argument("--target-aspect", type=float)
    verify_image.add_argument("--aspect-tolerance", type=float, default=0.03)
    verify_image.add_argument("--require-format", choices=("png", "jpeg", "webp"))
    verify_image.add_argument("--json", action="store_true")
    verify_image.set_defaults(func=cmd_verify_image)

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

    provider = sub.add_parser("provider-check", help="Probe an official or trusted OpenAI-compatible relay without generating an image.")
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
