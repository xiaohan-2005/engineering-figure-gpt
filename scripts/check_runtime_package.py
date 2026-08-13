#!/usr/bin/env python3
from __future__ import annotations
import argparse
import tempfile
from pathlib import Path
from sync_codex_skill import sync

TEXT_SUFFIXES = {".md", ".txt", ".json", ".py", ".ps1", ".yml", ".yaml"}


def count_tokens(root: Path) -> int:
    import tiktoken
    encoder = tiktoken.get_encoding("o200k_base")
    total = 0
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            total += len(encoder.encode(path.read_text(encoding="utf-8")))
    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-budget", type=int, default=43000)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="efg-runtime-") as tmp:
        target = Path(tmp) / "engineering-figure-gpt"
        sync(target)
        skills = list(target.rglob("SKILL.md"))
        if len(skills) != 1 or skills[0] != target / "SKILL.md":
            raise SystemExit("Runtime must contain exactly one root SKILL.md")
        total = count_tokens(target)
    print(f"Runtime token total: {total}")
    if total > args.token_budget:
        raise SystemExit(f"Runtime token budget exceeded: {total} > {args.token_budget}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
