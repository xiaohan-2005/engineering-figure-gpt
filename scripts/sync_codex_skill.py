#!/usr/bin/env python3
"""Sync a pruned runtime copy of Engineering Figure GPT into Codex."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = Path.home() / ".codex" / "skills" / "engineering-figure-gpt"
ALLOW = ["SKILL.md", "LICENSE", "agents", "assets", "references", "schemas", "scripts", "templates", "secrets"]
RUNTIME_SCRIPT_ALLOW = {
    "build_engineering_figure_prompt.py",
    "build_plot_spec.py",
    "check_setup.ps1",
    "efg.py",
    "generate_image.py",
    "plot_publication_figure.py",
    "wizard.ps1",
}


def safe_target(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.name != "engineering-figure-gpt":
        raise SystemExit(f"Refusing to sync to unexpected directory: {resolved}")
    if resolved == ROOT.resolve():
        raise SystemExit("Refusing to overwrite the source repository.")
    return resolved


def copy_item(source: Path, target: Path) -> None:
    if not source.exists():
        return
    if source.is_dir() and source.name == "scripts":
        target.mkdir(parents=True, exist_ok=True)
        for child in source.iterdir():
            if child.name in RUNTIME_SCRIPT_ALLOW:
                copy_item(child, target / child.name)
        return
    if source.is_dir():
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
        shutil.copytree(source, target, ignore=ignore)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def sync(target: Path) -> None:
    target = safe_target(target)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for name in ALLOW:
        copy_item(ROOT / name, target / name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the pruned Engineering Figure GPT runtime package.")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    target = safe_target(args.target)
    sync(target)
    print(f"Synced runtime skill to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
