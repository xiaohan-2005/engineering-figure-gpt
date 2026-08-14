#!/usr/bin/env python3
"""Portable GPT-image generation/editing fallback for Engineering Figure GPT.

Inside Codex, prefer the built-in image-generation path. This CLI exists for reproducibility,
local testing, and environments where the built-in image tool is unavailable.

Official OpenAI is trusted by default. OpenAI-compatible relay/base URLs are supported only
with explicit opt-in via --allow-third-party or OPENAI_ALLOW_THIRD_PARTY=1 so credentials are
never silently sent to an unexpected host.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-image-2"
OFFICIAL_HOST = "api.openai.com"
FINAL_HINTS = (
    "2k",
    "highres",
    "high-res",
    "high resolution",
    "final export",
    "final-export",
    "final quality",
    "最终导出",
    "最终质量",
    "高分辨率",
)


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def read_key(args: argparse.Namespace) -> str:
    if getattr(args, "api_key", None):
        return args.api_key.strip()
    if os.getenv("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"].strip()
    key_file = getattr(args, "api_key_file", None) or os.getenv("OPENAI_API_KEY_FILE")
    if key_file:
        path = Path(key_file).expanduser()
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    default = Path.home() / ".codex" / "secrets" / "openai_api_key.txt"
    if default.is_file():
        value = default.read_text(encoding="utf-8").strip()
        if value:
            return value
    raise SystemExit("Missing API key. Set OPENAI_API_KEY or OPENAI_API_KEY_FILE.")


def read_prompt(args: argparse.Namespace) -> str:
    if getattr(args, "prompt_file", None):
        text = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        if text:
            return text
        raise SystemExit("Prompt file is empty.")
    if getattr(args, "prompt", None) and args.prompt.strip():
        return args.prompt.strip()
    raise SystemExit("Provide a prompt or --prompt-file.")


def normalized_base_url(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SystemExit("--base-url must be a valid http(s) URL, for example https://api.example.com/v1")
    if parsed.username or parsed.password:
        raise SystemExit("Do not embed credentials in --base-url; use API-key configuration instead.")
    return value


def is_official_base_url(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.scheme == "https" and (parsed.hostname or "").lower() == OFFICIAL_HOST


def final_quality_requested(args: argparse.Namespace, prompt: str = "") -> bool:
    if bool(getattr(args, "highres", False)) or bool(getattr(args, "final", False)):
        return True
    lowered = (prompt or "").lower()
    return any(hint in lowered for hint in FINAL_HINTS)


def resolve_model(args: argparse.Namespace, prompt: str = "") -> tuple[str, bool]:
    final_requested = final_quality_requested(args, prompt)
    explicit_model = getattr(args, "model", None)
    if explicit_model:
        return str(explicit_model), final_requested
    if final_requested:
        highres_model = os.getenv("OPENAI_IMAGE_HIGHRES_MODEL", "").strip()
        if not highres_model:
            raise SystemExit(
                "Final/high-resolution output was requested, but OPENAI_IMAGE_HIGHRES_MODEL is not configured. "
                "Set it to the final-quality model exposed by your official endpoint or trusted relay, or pass --model explicitly. "
                "The skill will not silently downgrade a final-quality request."
            )
        return highres_model, True
    return os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL, False


def validate_target(args: argparse.Namespace) -> bool:
    args.base_url = normalized_base_url(args.base_url)
    third_party = not is_official_base_url(args.base_url)
    allow_third_party = bool(getattr(args, "allow_third_party", False)) or env_flag("OPENAI_ALLOW_THIRD_PARTY")
    if third_party and not allow_third_party:
        raise SystemExit(
            "Custom/relay base URL detected. Re-run with --allow-third-party or set "
            "OPENAI_ALLOW_THIRD_PARTY=1 after you trust that endpoint."
        )
    model = str(getattr(args, "model", ""))
    if not model.startswith("gpt-image-"):
        raise SystemExit("Only GPT Image model names are allowed by this GPT-only skill.")
    if int(getattr(args, "n", 1)) < 1:
        raise SystemExit("--n must be at least 1.")
    if int(getattr(args, "timeout", 240)) <= 0:
        raise SystemExit("--timeout must be positive.")
    return third_party


def api_error(operation: str, response) -> str:
    message = ""
    try:
        payload = response.json()
        error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error, dict):
            message = str(error.get("message") or "").strip()
    except (ValueError, TypeError, AttributeError):
        pass
    if not message:
        message = str(getattr(response, "text", "") or "").strip()
    if len(message) > 1000:
        message = message[:1000] + "..."
    suffix = f": {message}" if message else ""
    return f"Image {operation} request failed ({response.status_code}){suffix}"


def response_json(operation: str, response) -> dict:
    if not response.ok:
        raise SystemExit(api_error(operation, response))
    try:
        payload = response.json()
    except ValueError as exc:
        raise SystemExit(f"Image {operation} request returned a non-JSON response.") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Image {operation} request returned an unexpected response type.")
    return payload


def save_result(payload: dict, out_dir: Path, prefix: str, output_format: str) -> list[Path]:
    data = payload.get("data") or []
    if not data:
        raise SystemExit("Image API returned no data.")
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise SystemExit("Image API returned an invalid data item.")
        target = out_dir / f"{prefix}-{index}.{output_format}"
        if item.get("b64_json"):
            try:
                content = base64.b64decode(item["b64_json"], validate=True)
            except Exception as exc:
                raise SystemExit("Image API returned invalid base64 image data.") from exc
            if not content:
                raise SystemExit("Image API returned an empty image payload.")
            target.write_bytes(content)
        elif item.get("url"):
            try:
                response = requests.get(item["url"], timeout=120)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise SystemExit(f"Failed to download image output: {exc}") from exc
            if not response.content:
                raise SystemExit("Downloaded image output is empty.")
            target.write_bytes(response.content)
        else:
            raise SystemExit("Unsupported image response item: missing b64_json/url.")
        if target.stat().st_size <= 0:
            raise SystemExit(f"Generated output file is empty: {target}")
        saved.append(target)
        print(target)
    return saved


def generation_request(args: argparse.Namespace, prompt: str, headers: dict) -> dict:
    body = {
        "model": args.model,
        "prompt": prompt,
        "size": args.size,
        "quality": args.quality,
        "output_format": args.output_format,
        "n": args.n,
    }
    if args.background:
        body["background"] = args.background
    try:
        response = requests.post(
            f"{args.base_url.rstrip('/')}/images/generations",
            headers={**headers, "Content-Type": "application/json"},
            json=body,
            timeout=args.timeout,
        )
    except requests.Timeout as exc:
        raise SystemExit(f"Image generation timed out after {args.timeout}s.") from exc
    except requests.RequestException as exc:
        raise SystemExit(f"Image generation network error: {exc}") from exc
    return response_json("generation", response)


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
        data = {
            "model": args.model,
            "prompt": prompt,
            "size": args.size,
            "quality": args.quality,
            "output_format": args.output_format,
            "n": str(args.n),
        }
        if args.background:
            data["background"] = args.background
        if args.input_fidelity:
            data["input_fidelity"] = args.input_fidelity
        try:
            response = requests.post(
                f"{args.base_url.rstrip('/')}/images/edits",
                headers=headers,
                data=data,
                files=files,
                timeout=args.timeout,
            )
        except requests.Timeout as exc:
            raise SystemExit(f"Image edit timed out after {args.timeout}s.") from exc
        except requests.RequestException as exc:
            raise SystemExit(f"Image edit network error: {exc}") from exc
        return response_json("edit", response)
    finally:
        for handle in handles:
            handle.close()


def endpoint_probe(url: str, headers: dict, timeout: int) -> dict:
    try:
        response = requests.options(url, headers=headers, timeout=timeout)
    except requests.Timeout:
        return {"status": "timeout", "http_status": None}
    except requests.RequestException as exc:
        return {"status": "network-error", "http_status": None, "detail": str(exc)[:300]}
    code = int(response.status_code)
    if code == 404:
        status = "missing"
    elif code in {401, 403}:
        status = "auth-required"
    elif code == 405:
        status = "route-present-options-unsupported"
    elif 200 <= code < 500:
        status = "reachable"
    else:
        status = "server-error"
    return {"status": status, "http_status": code}


def provider_check(args: argparse.Namespace, third_party: bool) -> int:
    key = read_key(args)
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    base = args.base_url.rstrip("/")
    result = {
        "profile": "openai-compatible-relay" if third_party else "official-openai",
        "base_url": base,
        "model": args.model,
        "models_endpoint": {"status": "not-checked", "http_status": None, "model_advertised": None},
        "generation_endpoint": endpoint_probe(f"{base}/images/generations", headers, args.timeout),
        "edit_endpoint": endpoint_probe(f"{base}/images/edits", headers, args.timeout),
    }
    try:
        response = requests.get(f"{base}/models", headers=headers, timeout=args.timeout)
        model_info = {"http_status": int(response.status_code)}
        if response.ok:
            try:
                payload = response.json()
                items = payload.get("data", []) if isinstance(payload, dict) else []
                ids = {str(item.get("id")) for item in items if isinstance(item, dict) and item.get("id")}
                model_info.update({"status": "reachable", "model_advertised": args.model in ids if ids else None})
            except ValueError:
                model_info.update({"status": "reachable-non-json", "model_advertised": None})
        elif response.status_code == 404:
            model_info.update({"status": "missing", "model_advertised": None})
        else:
            model_info.update({"status": "http-error", "model_advertised": None})
        result["models_endpoint"] = model_info
    except requests.Timeout:
        result["models_endpoint"] = {"status": "timeout", "http_status": None, "model_advertised": None}
    except requests.RequestException as exc:
        result["models_endpoint"] = {"status": "network-error", "http_status": None, "model_advertised": None, "detail": str(exc)[:300]}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    generation_status = result["generation_endpoint"]["status"]
    if generation_status in {"missing", "network-error", "timeout", "server-error"}:
        print("Provider check did not confirm a usable /images/generations route.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or edit research figures with a GPT Image-compatible API.")
    parser.add_argument("prompt", nargs="?")
    parser.add_argument("--prompt-file")
    parser.add_argument("--input-image", action="append", default=[], help="Input image for editing; may be repeated.")
    parser.add_argument("--model", default=None, help="Explicit GPT Image model override.")
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL), help="Official OpenAI or explicitly approved OpenAI-compatible relay base URL, usually ending in /v1.")
    parser.add_argument("--allow-third-party", action="store_true", default=env_flag("OPENAI_ALLOW_THIRD_PARTY"), help="Allow a non-OpenAI relay/base URL. Only enable for an endpoint you trust.")
    parser.add_argument("--api-key")
    parser.add_argument("--api-key-file")
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default=os.getenv("OPENAI_IMAGE_QUALITY", "high"))
    parser.add_argument("--size", default=os.getenv("OPENAI_IMAGE_SIZE", "1536x1024"))
    parser.add_argument("--output-format", choices=("png", "jpeg", "webp"), default=os.getenv("OPENAI_IMAGE_OUTPUT_FORMAT", "png"))
    parser.add_argument("--background", choices=("transparent", "opaque", "auto"))
    parser.add_argument("--input-fidelity", choices=("low", "high"), default=None, help="Explicit input fidelity for image edits when supported by the selected endpoint/model.")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--out-dir", default="output/image")
    parser.add_argument("--prefix", default="engineering-figure-gpt")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--highres", action="store_true", help="Use OPENAI_IMAGE_HIGHRES_MODEL and fail closed when it is not configured.")
    parser.add_argument("--final", action="store_true", help="Alias for final-quality/high-resolution routing.")
    parser.add_argument("--check-provider", action="store_true", help="Probe relay/API compatibility without generating an image. Requires API authentication but does not call image generation.")
    parser.add_argument("--dry-run", action="store_true", help="Validate arguments without calling the API.")
    args = parser.parse_args()

    prompt = "" if args.check_provider else read_prompt(args)
    args.model, final_requested = resolve_model(args, prompt)
    third_party = validate_target(args)
    if third_party:
        print(f"[WARN] Using explicitly approved third-party relay: {args.base_url}", file=sys.stderr)

    if args.check_provider:
        return provider_check(args, third_party)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "edit" if args.input_image else "generate",
                    "model": args.model,
                    "base_url": args.base_url,
                    "third_party": third_party,
                    "final_quality_requested": final_requested,
                    "size": args.size,
                    "quality": args.quality,
                    "output_format": args.output_format,
                    "n": args.n,
                    "prompt_chars": len(prompt),
                },
                ensure_ascii=False,
            )
        )
        return 0

    key = read_key(args)
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    result = edit_request(args, prompt, headers) if args.input_image else generation_request(args, prompt, headers)
    save_result(result, Path(args.out_dir), args.prefix, args.output_format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
