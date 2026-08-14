#!/usr/bin/env python3
"""Package a completed research-figure run into a reproducible docs/examples case.

This script is repository tooling, not part of the pruned Codex runtime. It refuses to
create a completed manifest unless the referenced evidence and output files really exist,
are non-empty, and have a plausible file signature for their declared format.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = ROOT / "docs" / "examples"
MANIFEST_SCHEMA = DEFAULT_DESTINATION / "example-manifest.schema.json"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SUPPORTED_OUTPUT_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf"}


def existing_file(value: str, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"{label} not found: {path}")
    if path.stat().st_size <= 0:
        raise SystemExit(f"{label} is empty: {path}")
    return path


def validate_output_file(path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_OUTPUT_SUFFIXES:
        raise SystemExit(f"Unsupported showcase output format: {suffix or '<none>'}")
    head = path.read_bytes()[:64]
    valid = False
    if suffix == ".png":
        valid = head.startswith(b"\x89PNG\r\n\x1a\n")
    elif suffix in {".jpg", ".jpeg"}:
        valid = head.startswith(b"\xff\xd8\xff")
    elif suffix == ".webp":
        valid = len(head) >= 12 and head.startswith(b"RIFF") and head[8:12] == b"WEBP"
    elif suffix == ".pdf":
        valid = head.startswith(b"%PDF-")
    elif suffix == ".svg":
        text = path.read_text(encoding="utf-8-sig", errors="strict").lstrip()
        valid = text.startswith("<svg") or (text.startswith("<?xml") and "<svg" in text[:1000])
    if not valid:
        raise SystemExit(f"Output file signature does not match {suffix}: {path}")


def copy_required(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if not target.is_file() or target.stat().st_size <= 0:
        raise SystemExit(f"Failed to create non-empty artifact: {target}")


def source_pair(text: str) -> tuple[Path, str]:
    if "=" in text:
        raw_path, dest_name = text.split("=", 1)
    else:
        raw_path = text
        dest_name = Path(text).name
    source = existing_file(raw_path, "Source artifact")
    dest_name = dest_name.strip()
    if not dest_name or Path(dest_name).name != dest_name:
        raise SystemExit("Source destination names must be simple filenames, e.g. prompt.txt or request.json")
    return source, dest_name


def validate_mode_sources(mode: str, names: set[str]) -> None:
    if mode == "image" and "prompt.txt" not in names:
        raise SystemExit("Image showcase packaging requires a source mapped to prompt.txt")
    if mode == "plot":
        missing = {"request.json", "plot-spec.json"}.difference(names)
        if missing:
            raise SystemExit(f"Plot showcase packaging requires {sorted(missing)}")


def build_manifest(args: argparse.Namespace, source_names: list[str], output_name: str) -> dict:
    manifest: dict = {
        "slug": args.slug,
        "mode": args.mode,
        "input_artifacts": ["brief.md", *source_names],
        "output_artifact": output_name,
        "verification": args.check or ["verification.md is present and must be reviewed before publication use"],
    }
    for field in ("model", "quality", "size"):
        value = getattr(args, field, None)
        if value:
            manifest[field] = value
    return manifest


def validate_manifest(manifest: dict) -> None:
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda item: list(item.path))
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise SystemExit(f"Generated manifest does not satisfy schema: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a completed reproducible showcase example.")
    parser.add_argument("--slug", required=True, help="Lowercase kebab-case example slug.")
    parser.add_argument("--mode", choices=("image", "plot", "mixed"), required=True)
    parser.add_argument("--brief", required=True, help="Completed Figure Brief markdown file.")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Evidence source file. Use PATH=DESTNAME to normalize names, e.g. final-prompt.txt=prompt.txt. Repeat as needed.",
    )
    parser.add_argument("--output", required=True, help="Real PNG/JPEG/WebP/SVG/PDF output file to package.")
    parser.add_argument("--verification", required=True, help="Verification markdown file.")
    parser.add_argument("--check", action="append", default=[], help="Short verified statement for manifest.json; may be repeated.")
    parser.add_argument("--model")
    parser.add_argument("--quality")
    parser.add_argument("--size")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--force", action="store_true", help="Replace an existing example directory.")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        raise SystemExit("--slug must be lowercase kebab-case using a-z, 0-9, and single hyphens")

    brief = existing_file(args.brief, "Brief")
    verification = existing_file(args.verification, "Verification")
    output = existing_file(args.output, "Output")
    validate_output_file(output)
    pairs = [source_pair(item) for item in args.source]
    source_names = [name for _, name in pairs]
    if len(source_names) != len(set(source_names)):
        raise SystemExit("Source destination filenames must be unique")
    validate_mode_sources(args.mode, set(source_names))

    output_name = f"output{output.suffix.lower()}"
    manifest = build_manifest(args, source_names, output_name)
    validate_manifest(manifest)

    destination_root = args.destination.expanduser().resolve()
    target = destination_root / args.slug
    if target.exists():
        if not args.force:
            raise SystemExit(f"Example directory already exists: {target}. Use --force only when replacement is intentional.")
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    copy_required(brief, target / "brief.md")
    for source, name in pairs:
        copy_required(source, target / name)
    copy_required(output, target / output_name)
    copy_required(verification, target / "verification.md")
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(target)
    print(target / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
