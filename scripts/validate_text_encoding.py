#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".json", ".py", ".ps1", ".yml", ".yaml"}
SUSPICIOUS = ["鍒涘缓", "鎶€鏈", "鐧借壊", "绯荤粺", "鏁版嵁", "缁撴瀯"]


def iter_files(paths: list[str]):
    for raw in paths:
        path = Path(raw)
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path
        elif path.is_dir():
            yield from (p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES)


def main() -> int:
    failures = []
    for path in iter_files(sys.argv[1:] or ["."]):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{path}: not valid UTF-8 ({exc})")
            continue
        hits = [frag for frag in SUSPICIOUS if frag in text]
        if hits:
            failures.append(f"{path}: suspicious mojibake {hits}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("UTF-8/text validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
