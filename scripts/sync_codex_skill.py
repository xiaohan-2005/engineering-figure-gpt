#!/usr/bin/env python3
"""Sync a pruned execution runtime of Engineering Figure GPT into Codex.

Repository/install helpers, CI validators, showcase files, schemas, examples, and
release-only references stay in the source checkout. The installed Skill keeps only
the files needed by the agent or invoked by the runtime CLI.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = Path.home() / ".codex" / "skills" / "engineering-figure-gpt"

ROOT_ALLOW = {"SKILL.md", "agents", "assets", "references", "scripts"}

RUNTIME_SCRIPT_ALLOW = {
    "build_engineering_figure_prompt.py",
    "build_image_edit_prompt.py",
    "build_plot_spec.py",
    "codex_provider_config.py",
    "efg.py",
    "generate_image.py",
    "plot_publication_figure.py",
    "verify_image_output.py",
}

# Keep references that materially affect execution decisions. Release/CI-only docs,
# duplicated overview docs, and source-install helpers remain in the repository.
RUNTIME_REFERENCE_ALLOW = {
    "chinese-labels.md",
    "codex-cc-switch.md",
    "edit-mode.md",
    "editable-figure-handoff.md",
    "figure-brief-spec.md",
    "highres-policy.md",
    "image-quality-contract.md",
    "mathematical-modeling.md",
    "publication-plot-api.md",
    "visual-qa.md",
}


def safe_target(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.name != "engineering-figure-gpt":
        raise SystemExit(f"Refusing to sync to unexpected directory: {resolved}")
    if resolved == ROOT.resolve():
        raise SystemExit("Refusing to overwrite the source repository.")
    return resolved


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_filtered_directory(source: Path, target: Path, allowed: set[str]) -> None:
    if not source.is_dir():
        return
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        if child.is_file() and child.name in allowed:
            copy_file(child, target / child.name)


def copy_item(source: Path, target: Path) -> None:
    if not source.exists():
        return
    if source.is_dir() and source.name == "scripts":
        copy_filtered_directory(source, target, RUNTIME_SCRIPT_ALLOW)
        return
    if source.is_dir() and source.name == "references":
        copy_filtered_directory(source, target, RUNTIME_REFERENCE_ALLOW)
        return
    if source.is_dir():
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
        shutil.copytree(source, target, ignore=ignore)
    else:
        copy_file(source, target)


def sync(target: Path) -> None:
    target = safe_target(target)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for name in sorted(ROOT_ALLOW):
        copy_item(ROOT / name, target / name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the pruned Engineering Figure GPT execution runtime.")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    target = safe_target(args.target)
    sync(target)
    print(f"Synced pruned runtime skill to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
