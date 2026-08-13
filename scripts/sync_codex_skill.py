#!/usr/bin/env python3
"""Sync only runtime-required files into the Codex skill directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOW = ["SKILL.md", "LICENSE", "agents", "assets", "references", "schemas", "scripts", "templates"]
DEFAULT_TARGET = Path.home() / ".codex" / "skills" / "engineering-figure-gpt"


def copy_item(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target)
    elif source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def sync(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for name in ALLOW:
        source = ROOT / name
        if source.exists():
            copy_item(source, target / name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    sync(args.target.expanduser())
    print(f"Synced runtime skill to {args.target.expanduser()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
