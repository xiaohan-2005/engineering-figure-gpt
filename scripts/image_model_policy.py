#!/usr/bin/env python3
"""Model-specific image policy shared by Engineering Figure GPT CLIs."""

from __future__ import annotations

import math
import re
from pathlib import Path

GPT2_MIN_PIXELS = 655_360
GPT2_MAX_PIXELS = 8_294_400
GPT2_MAX_EDGE = 3840
GPT2_MAX_ASPECT = 3.0


def is_gpt_image_2(model: str | None) -> bool:
    return bool(model and str(model).startswith("gpt-image-2"))


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


def validate_gpt_image_2_size(value: str) -> None:
    if value.lower() == "auto":
        return
    width, height = parse_size(value)
    if not valid_gpt_image_2_size(width, height):
        raise ValueError(
            "GPT Image 2 size must have edges <=3840px, both edges divisible by 16, "
            "aspect ratio <=3:1, and total pixels between 655360 and 8294400."
        )


def nearest_gpt_image_2_size(width: int, height: int) -> tuple[int, int]:
    """Return a close legal size while preserving the source aspect approximately."""
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive.")
    ratio = max(width, height) / min(width, height)
    if ratio > GPT2_MAX_ASPECT:
        raise ValueError(
            f"Source aspect ratio {ratio:.3f}:1 exceeds GPT Image 2's 3:1 output limit; "
            "pad/crop first or pass an explicit legal --size."
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
    source_ratio = width / height
    target_pixels = width * height * scale * scale
    candidates: list[tuple[float, int, int]] = []
    for dw in range(-128, 129, 16):
        for dh in range(-128, 129, 16):
            w = base_w + dw
            h = base_h + dh
            if not valid_gpt_image_2_size(w, h):
                continue
            ratio_error = abs((w / h) - source_ratio) / max(abs(source_ratio), 1e-9)
            scale_error = abs((w * h) - target_pixels) / max(target_pixels, 1)
            candidates.append((ratio_error * 10 + scale_error, w, h))
    if not candidates:
        raise ValueError("Could not derive a legal GPT Image 2 output size close to the source canvas.")
    _, best_w, best_h = min(candidates)
    return best_w, best_h


def read_raster_size(path: str | Path) -> tuple[int, int]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for raster size inspection. Install requirements.txt.") from exc
    with Image.open(path) as image:
        return int(image.width), int(image.height)


def source_preserving_gpt_image_2_size(path: str | Path) -> tuple[str, bool]:
    """Return (size, exact_preservation)."""
    width, height = read_raster_size(path)
    if valid_gpt_image_2_size(width, height):
        return f"{width}x{height}", True
    new_w, new_h = nearest_gpt_image_2_size(width, height)
    return f"{new_w}x{new_h}", False
