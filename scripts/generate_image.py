#!/usr/bin/env python3
"""Portable GPT-only image generation/editing fallback for Engineering Figure GPT.

Inside Codex, prefer the built-in image-generation path. This CLI exists for reproducibility,
local testing, and environments where the built-in image tool is unavailable.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path

import requests

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-image-2"


def read_key(args: argparse.Namespace) -> str:
    if args.api_key:
        return args.api_key.strip()
    if os.getenv("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"].strip()
    key_file = args.api_key_file or os.getenv("OPENAI_API_KEY_FILE")
    if key_file:
        path = Path(key_file).expanduser()
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    default = Path.home() / ".codex" / "secrets" / "openai_api_key.txt"
    if default.is_file():
        return default.read_text(encoding="utf-8").strip()
    raise SystemExit("Missing OpenAI API key. Set OPENAI_API_KEY or OPENAI_API_KEY_FILE.")


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt.strip()
    raise SystemExit("Provide a prompt or --prompt-file.")


def validate_target(args: argparse.Namespace) -> None:
    if args.base_url.rstrip("/") != DEFAULT_BASE_URL:
        raise SystemExit("Custom base URLs are intentionally rejected; this skill uses the official OpenAI endpoint only.")
    if not args.model.startswith("gpt-image-"):
        raise SystemExit("Only GPT Image models are allowed by this GPT-only skill.")


def save_result(payload: dict, out_dir: Path, prefix: str, output_format: str) -> list[Path]:
    data = payload.get("data") or []
    if not data:
        raise SystemExit(f"Image API returned no data: {payload}")
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for index, item in enumerate(data, start=1):
        target = out_dir / f"{prefix}-{index}.{output_format}"
        if item.get("b64_json"):
            target.write_bytes(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            response = requests.get(item["url"], timeout=120)
            response.raise_for_status()
            target.write_bytes(response.content)
        else:
            raise SystemExit(f"Unsupported image response item: {item}")
        saved.append(target)
        print(target)
    return saved


def generation_request(args: argparse.Namespace, prompt: str, headers: dict) -> dict:
    body = {"model": args.model, "prompt": prompt, "size": args.size, "quality": args.quality, "output_format": args.output_format, "n": args.n}
    if args.background:
        body["background"] = args.background
    response = requests.post(f"{args.base_url.rstrip('/')}/images/generations", headers={**headers, "Content-Type": "application/json"}, json=body, timeout=args.timeout)
    if not response.ok:
        raise SystemExit(f"OpenAI image generation failed ({response.status_code}): {response.text}")
    return response.json()


def edit_request(args: argparse.Namespace, prompt: str, headers: dict) -> dict:
    files = []
    handles = []
    try:
        for path_text in args.input_image:
            path = Path(path_text)
            if not path.is_file():
                raise SystemExit(f"Input image not found: {path}")
            handle = path.open("rb")
            handles.append(handle)
            mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            files.append(("image[]", (path.name, handle, mime)))
        data = {"model": args.model, "prompt": prompt, "size": args.size, "quality": args.quality, "output_format": args.output_format, "n": str(args.n)}
        if args.background:
            data["background"] = args.background
        if args.input_fidelity:
            data["input_fidelity"] = args.input_fidelity
        response = requests.post(f"{args.base_url.rstrip('/')}/images/edits", headers=headers, data=data, files=files, timeout=args.timeout)
        if not response.ok:
            raise SystemExit(f"OpenAI image edit failed ({response.status_code}): {response.text}")
        return response.json()
    finally:
        for handle in handles:
            handle.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or edit research figures with GPT Image 2.")
    parser.add_argument("prompt", nargs="?")
    parser.add_argument("--prompt-file")
    parser.add_argument("--input-image", action="append", default=[], help="Input image for editing; may be repeated.")
    parser.add_argument("--model", default=os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key")
    parser.add_argument("--api-key-file")
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default=os.getenv("OPENAI_IMAGE_QUALITY", "high"))
    parser.add_argument("--size", default=os.getenv("OPENAI_IMAGE_SIZE", "1536x1024"))
    parser.add_argument("--output-format", choices=("png", "jpeg", "webp"), default=os.getenv("OPENAI_IMAGE_OUTPUT_FORMAT", "png"))
    parser.add_argument("--background", choices=("transparent", "opaque", "auto"))
    parser.add_argument("--input-fidelity", choices=("low", "high"), default=None, help="Send only when the selected GPT Image endpoint supports/needs an explicit fidelity setting.")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--out-dir", default="output/image")
    parser.add_argument("--prefix", default="engineering-figure-gpt")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--dry-run", action="store_true", help="Validate arguments without calling the API.")
    args = parser.parse_args()

    prompt = read_prompt(args)
    validate_target(args)
    if args.dry_run:
        print(json.dumps({"mode": "edit" if args.input_image else "generate", "model": args.model, "size": args.size, "quality": args.quality, "output_format": args.output_format, "prompt_chars": len(prompt)}, ensure_ascii=False))
        return 0

    key = read_key(args)
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    result = edit_request(args, prompt, headers) if args.input_image else generation_request(args, prompt, headers)
    save_result(result, Path(args.out_dir), args.prefix, args.output_format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
