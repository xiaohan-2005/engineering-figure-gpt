#!/usr/bin/env python3
"""Verify objective raster-output constraints for generated research figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def parse_size(value: str | None) -> tuple[int, int] | None:
    if not value or value.lower() == "auto":
        return None
    text = value.lower().replace("×", "x")
    if "x" not in text:
        raise SystemExit("Expected size must look like WIDTHxHEIGHT, for example 1536x1024.")
    left, right = text.split("x", 1)
    try:
        width, height = int(left), int(right)
    except ValueError as exc:
        raise SystemExit("Expected size must contain integer dimensions.") from exc
    if width <= 0 or height <= 0:
        raise SystemExit("Expected dimensions must be positive.")
    return width, height


def inspect_image(path: Path) -> dict:
    if not path.is_file():
        return {"path": str(path), "ok": False, "errors": ["file-not-found"]}
    try:
        with Image.open(path) as image:
            image.load()
            return {
                "path": str(path),
                "ok": True,
                "width": int(image.width),
                "height": int(image.height),
                "format": str(image.format or "").upper(),
                "mode": str(image.mode),
                "bytes": path.stat().st_size,
            }
    except Exception as exc:  # Pillow raises several format-specific exceptions.
        return {"path": str(path), "ok": False, "errors": [f"unreadable-image: {exc}"]}


def verify(
    info: dict,
    expected_size: tuple[int, int] | None = None,
    min_width: int | None = None,
    min_height: int | None = None,
    min_megapixels: float | None = None,
    target_aspect: float | None = None,
    aspect_tolerance: float = 0.03,
    require_format: str | None = None,
) -> dict:
    errors = list(info.get("errors") or [])
    warnings: list[str] = []
    if info.get("ok"):
        width = int(info["width"])
        height = int(info["height"])
        if expected_size and (width, height) != expected_size:
            errors.append(f"size-mismatch: got {width}x{height}, expected {expected_size[0]}x{expected_size[1]}")
        if min_width is not None and width < min_width:
            errors.append(f"width-too-small: {width} < {min_width}")
        if min_height is not None and height < min_height:
            errors.append(f"height-too-small: {height} < {min_height}")
        if min_megapixels is not None:
            megapixels = (width * height) / 1_000_000
            if megapixels < min_megapixels:
                errors.append(f"megapixels-too-small: {megapixels:.3f} < {min_megapixels:.3f}")
        if target_aspect is not None:
            actual = width / height
            relative_error = abs(actual - target_aspect) / target_aspect
            if relative_error > aspect_tolerance:
                errors.append(
                    f"aspect-mismatch: got {actual:.4f}, target {target_aspect:.4f}, tolerance {aspect_tolerance:.3f}"
                )
        if require_format:
            actual_format = str(info.get("format") or "").lower()
            if actual_format != require_format.lower():
                errors.append(f"format-mismatch: got {actual_format or 'unknown'}, expected {require_format.lower()}")
        if info.get("bytes", 0) <= 0:
            errors.append("empty-file")
        if width < 1000 and height < 1000:
            warnings.append("both-dimensions-below-1000px: usually too small for a final paper raster")

    result = dict(info)
    result["errors"] = errors
    result["warnings"] = warnings
    result["ok"] = not errors
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify objective image-output constraints.")
    parser.add_argument("images", nargs="+")
    parser.add_argument("--expected-size", help="Exact WIDTHxHEIGHT expected from the provider.")
    parser.add_argument("--min-width", type=int)
    parser.add_argument("--min-height", type=int)
    parser.add_argument("--min-megapixels", type=float)
    parser.add_argument("--target-aspect", type=float, help="Width / height ratio, e.g. 1.5 for 3:2.")
    parser.add_argument("--aspect-tolerance", type=float, default=0.03)
    parser.add_argument("--require-format", choices=("png", "jpeg", "webp"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    expected = parse_size(args.expected_size)
    results = [
        verify(
            inspect_image(Path(path)),
            expected,
            args.min_width,
            args.min_height,
            args.min_megapixels,
            args.target_aspect,
            args.aspect_tolerance,
            args.require_format,
        )
        for path in args.images
    ]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "PASS" if result["ok"] else "FAIL"
            dims = ""
            if "width" in result:
                dims = f" {result['width']}x{result['height']} {result.get('format', '')}".rstrip()
            print(f"[{status}] {result['path']}{dims}")
            for warning in result.get("warnings", []):
                print(f"  warning: {warning}")
            for error in result.get("errors", []):
                print(f"  error: {error}")

    return 0 if all(result["ok"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
