#!/usr/bin/env python3
"""Read the active Codex provider without exposing credentials.

CC Switch and similar provider managers write Codex's live configuration under
~/.codex. This helper intentionally reads only the active provider needed by the
portable image fallback:

- config.toml: model_provider, model_providers.<name>.base_url, env_key,
  experimental_bearer_token, wire_api
- auth.json: OPENAI_API_KEY fallback

The caller may use the returned key in memory, but diagnostics never print it.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - runtime targets Python 3.11+
    raise SystemExit("Python 3.11+ is required to read Codex config.toml.") from exc


def codex_home() -> Path:
    configured = os.getenv("CODEX_HOME", "").strip()
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def _read_toml(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"Could not read Codex config: {path}: {exc}") from exc
    return value if isinstance(value, dict) else {}


def _read_auth(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read Codex auth file: {path}: {exc}") from exc
    return value if isinstance(value, dict) else {}


def _provider_table(config: dict, provider_name: str) -> dict:
    providers = config.get("model_providers")
    if not isinstance(providers, dict):
        return {}
    direct = providers.get(provider_name)
    if isinstance(direct, dict):
        return direct
    lowered = provider_name.casefold()
    for name, value in providers.items():
        if str(name).casefold() == lowered and isinstance(value, dict):
            return value
    return {}


def load_codex_live_provider(
    config_path: str | Path | None = None,
    auth_path: str | Path | None = None,
) -> dict:
    home = codex_home()
    config_file = Path(config_path).expanduser() if config_path else home / "config.toml"
    auth_file = Path(auth_path).expanduser() if auth_path else home / "auth.json"

    config = _read_toml(config_file)
    auth = _read_auth(auth_file)

    provider_name = str(config.get("model_provider") or "openai")
    provider = _provider_table(config, provider_name)

    base_url = str(provider.get("base_url") or "").strip() or None
    if not base_url and provider_name.casefold() == "openai":
        base_url = str(config.get("openai_base_url") or "").strip() or None

    api_key = None
    key_source = None

    env_key_name = str(provider.get("env_key") or "").strip()
    if env_key_name and os.getenv(env_key_name):
        api_key = os.environ[env_key_name].strip()
        key_source = f"env:{env_key_name}"

    if not api_key:
        bearer = str(provider.get("experimental_bearer_token") or "").strip()
        if bearer:
            api_key = bearer
            key_source = "config.toml:experimental_bearer_token"

    if not api_key:
        auth_key = str(auth.get("OPENAI_API_KEY") or "").strip()
        if auth_key:
            api_key = auth_key
            key_source = "auth.json:OPENAI_API_KEY"

    return {
        "provider_name": provider_name,
        "provider_display_name": str(provider.get("name") or provider_name),
        "base_url": base_url,
        "wire_api": str(provider.get("wire_api") or "").strip() or None,
        "requires_openai_auth": bool(provider.get("requires_openai_auth", False)),
        "api_key": api_key,
        "key_source": key_source,
        "config_path": str(config_file),
        "auth_path": str(auth_file),
        "config_exists": config_file.is_file(),
        "auth_exists": auth_file.is_file(),
        "configured": bool(provider or base_url or api_key),
    }


def sanitized_summary(info: dict) -> dict:
    return {
        "provider_name": info.get("provider_name"),
        "provider_display_name": info.get("provider_display_name"),
        "base_url": info.get("base_url"),
        "wire_api": info.get("wire_api"),
        "requires_openai_auth": info.get("requires_openai_auth"),
        "has_api_key": bool(info.get("api_key")),
        "key_source": info.get("key_source"),
        "config_path": info.get("config_path"),
        "auth_path": info.get("auth_path"),
        "config_exists": info.get("config_exists"),
        "auth_exists": info.get("auth_exists"),
        "configured": info.get("configured"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the active Codex provider without printing secrets.")
    parser.add_argument("--config")
    parser.add_argument("--auth")
    args = parser.parse_args()
    info = load_codex_live_provider(args.config, args.auth)
    print(json.dumps(sanitized_summary(info), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
