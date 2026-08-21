#!/usr/bin/env python3
"""Portable GPT-image generation/editing fallback for Engineering Figure GPT.

Connection priority:
1. explicit CLI overrides;
2. active Codex provider from ~/.codex/config.toml + ~/.codex/auth.json;
3. legacy OPENAI_* environment variables/files;
4. official OpenAI defaults.

The script is GPT-only and keeps model-specific policy explicit instead of assuming
that every OpenAI-compatible relay implements every Images parameter identically.
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

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from codex_provider_config import load_codex_live_provider
from image_model_policy import (
    is_gpt_image_2,
    source_preserving_gpt_image_2_size,
    validate_gpt_image_2_size,
)

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1536x1024"
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


def resolve_connection(args: argparse.Namespace) -> dict:
    """Resolve endpoint/key source while preferring the active Codex provider."""
    explicit_base = str(getattr(args, "base_url", None) or "").strip()
    codex_info = None
    source = "official-default"
    provider_name = None
    codex_key = None
    codex_trusted = False

    if explicit_base:
        base_url = explicit_base
        source = "cli"
    else:
        no_codex = bool(getattr(args, "no_codex_config", False))
        if not no_codex:
            codex_info = load_codex_live_provider(
                getattr(args, "codex_config", None),
                getattr(args, "codex_auth", None),
            )
        if codex_info and codex_info.get("configured"):
            base_url = codex_info.get("base_url") or DEFAULT_BASE_URL
            source = "codex-config"
            provider_name = codex_info.get("provider_name")
            codex_key = codex_info.get("api_key")
            codex_trusted = True
        elif os.getenv("OPENAI_BASE_URL"):
            base_url = os.environ["OPENAI_BASE_URL"]
            source = "environment"
        else:
            base_url = DEFAULT_BASE_URL

    args.base_url = normalized_base_url(base_url)
    args._connection_source = source
    args._codex_provider = provider_name
    args._codex_api_key = codex_key
    args._codex_trusted = codex_trusted
    args._codex_info = codex_info
    return {
        "source": source,
        "base_url": args.base_url,
        "codex_provider": provider_name,
        "codex_trusted": codex_trusted,
        "has_codex_key": bool(codex_key),
    }


def read_key(args: argparse.Namespace) -> str:
    if getattr(args, "api_key", None):
        return args.api_key.strip()

    explicit_key_file = getattr(args, "api_key_file", None)
    if explicit_key_file:
        path = Path(explicit_key_file).expanduser()
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
        raise SystemExit(f"API key file not found or empty: {path}")

    codex_key = str(getattr(args, "_codex_api_key", None) or "").strip()
    if codex_key:
        return codex_key

    if os.getenv("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"].strip()

    env_key_file = os.getenv("OPENAI_API_KEY_FILE")
    if env_key_file:
        path = Path(env_key_file).expanduser()
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value

    default = Path.home() / ".codex" / "secrets" / "openai_api_key.txt"
    if default.is_file():
        value = default.read_text(encoding="utf-8").strip()
        if value:
            return value

    info = getattr(args, "_codex_info", None) or {}
    if info.get("configured"):
        raise SystemExit(
            "The active Codex provider was detected, but no reusable API key was found in "
            "config.toml/auth.json. Re-enable the provider in CC Switch or configure the "
            "provider's env_key. Do not paste secrets into prompts."
        )
    raise SystemExit("Missing API key. Configure Codex/CC Switch or set OPENAI_API_KEY/OPENAI_API_KEY_FILE.")


def read_prompt(args: argparse.Namespace) -> str:
    if getattr(args, "prompt_file", None):
        text = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        if text:
            return text
        raise SystemExit("Prompt file is empty.")
    if getattr(args, "prompt", None) and args.prompt.strip():
        return args.prompt.strip()
    raise SystemExit("Provide a prompt or --prompt-file.")


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
                "Set it to the final-quality image model exposed by the active provider, or pass --model explicitly. "
                "The skill will not silently downgrade a final-quality request."
            )
        return highres_model, True
    return os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL, False


def resolve_output_size(args: argparse.Namespace) -> None:
    """Resolve a concrete output size after model selection.

    GPT Image 2 edits preserve the primary input canvas when it is legal. If the source
    dimensions are not legal but the aspect ratio can be preserved, use the nearest legal
    canvas and report that adjustment. Other models retain the historical default unless
    the caller/provider supplied a size explicitly.
    """
    if args.size:
        return
    if args.input_image and is_gpt_image_2(args.model):
        try:
            size, exact = source_preserving_gpt_image_2_size(args.input_image[0])
        except Exception as exc:
            raise SystemExit(f"Could not resolve GPT Image 2 edit canvas from the source image: {exc}") from exc
        args.size = size
        if exact:
            print(f"[INFO] Preserving source canvas for GPT Image 2 edit: {size}", file=sys.stderr)
        else:
            print(
                f"[WARN] Source canvas is not a legal GPT Image 2 output size; using nearest legal canvas {size}.",
                file=sys.stderr,
            )
        return
    args.size = DEFAULT_SIZE


def validate_target(args: argparse.Namespace) -> bool:
    args.base_url = normalized_base_url(args.base_url)
    third_party = not is_official_base_url(args.base_url)
    allow_third_party = (
        bool(getattr(args, "allow_third_party", False))
        or env_flag("OPENAI_ALLOW_THIRD_PARTY")
        or bool(getattr(args, "_codex_trusted", False))
    )
    if third_party and not allow_third_party:
        raise SystemExit(
            "Custom/relay base URL detected. Re-run with --allow-third-party or set "
            "OPENAI_ALLOW_THIRD_PARTY=1 after you trust that endpoint. Active Codex/CC Switch "
            "providers are trusted automatically because the user already selected them there."
        )

    model = str(getattr(args, "model", ""))
    if not model.startswith("gpt-image-"):
        raise SystemExit("Only GPT Image model names are allowed by this GPT-only skill.")
    if int(getattr(args, "n", 1)) < 1:
        raise SystemExit("--n must be at least 1.")
    if int(getattr(args, "timeout", 240)) <= 0:
        raise SystemExit("--timeout must be positive.")

    if is_gpt_image_2(model):
        if getattr(args, "input_fidelity", None):
            raise SystemExit(
                "GPT Image 2 does not accept --input-fidelity. Omit it: GPT Image 2 always processes image inputs at high fidelity."
            )
        if getattr(args, "background", None) == "transparent":
            raise SystemExit("GPT Image 2 does not currently support transparent backgrounds.")
        try:
            validate_gpt_image_2_size(str(args.size))
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
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
        "connection_source": getattr(args, "_connection_source", None),
        "codex_provider": getattr(args, "_codex_provider", None),
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
        result["models_endpoint"] = {
            "status": "network-error",
            "http_status": None,
            "model_advertised": None,
            "detail": str(exc)[:300],
        }

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
    parser.add_argument("--base-url", default=None, help="Explicit endpoint override. Without this flag, the active Codex/CC Switch provider is preferred.")
    parser.add_argument("--codex-config", help="Optional config.toml override for testing/advanced use.")
    parser.add_argument("--codex-auth", help="Optional auth.json override for testing/advanced use.")
    parser.add_argument("--no-codex-config", action="store_true", help="Ignore ~/.codex live provider files and use explicit/env/default connection settings.")
    parser.add_argument("--allow-third-party", action="store_true", default=env_flag("OPENAI_ALLOW_THIRD_PARTY"), help="Trust a custom URL supplied outside the active Codex config.")
    parser.add_argument("--api-key")
    parser.add_argument("--api-key-file")
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default=os.getenv("OPENAI_IMAGE_QUALITY", "high"))
    parser.add_argument("--size", default=os.getenv("OPENAI_IMAGE_SIZE"))
    parser.add_argument("--output-format", choices=("png", "jpeg", "webp"), default=os.getenv("OPENAI_IMAGE_OUTPUT_FORMAT", "png"))
    parser.add_argument("--background", choices=("transparent", "opaque", "auto"))
    parser.add_argument(
        "--input-fidelity",
        choices=("low", "high"),
        default=None,
        help="Only for image models/endpoints that support it. GPT Image 2 rejects this option because image inputs are always high fidelity.",
    )
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--out-dir", default="output/image")
    parser.add_argument("--prefix", default="engineering-figure-gpt")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--highres", action="store_true", help="Use OPENAI_IMAGE_HIGHRES_MODEL and fail closed when it is not configured.")
    parser.add_argument("--final", action="store_true", help="Alias for final-quality/high-resolution routing.")
    parser.add_argument("--check-provider", action="store_true", help="Probe the resolved provider without generating an image.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve and validate configuration without calling the API.")
    args = parser.parse_args()

    prompt = "" if args.check_provider else read_prompt(args)
    resolve_connection(args)
    args.model, final_requested = resolve_model(args, prompt)
    resolve_output_size(args)
    third_party = validate_target(args)

    if third_party and getattr(args, "_connection_source", None) == "codex-config":
        print(
            f"[INFO] Reusing active Codex provider '{getattr(args, '_codex_provider', None)}': {args.base_url}",
            file=sys.stderr,
        )
    elif third_party:
        print(f"[WARN] Using explicitly approved third-party relay: {args.base_url}", file=sys.stderr)

    if args.check_provider:
        return provider_check(args, third_party)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "edit" if args.input_image else "generate",
                    "model": args.model,
                    "connection_source": getattr(args, "_connection_source", None),
                    "codex_provider": getattr(args, "_codex_provider", None),
                    "base_url": args.base_url,
                    "third_party": third_party,
                    "final_quality_requested": final_requested,
                    "size": args.size,
                    "quality": args.quality,
                    "output_format": args.output_format,
                    "input_fidelity": args.input_fidelity,
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
