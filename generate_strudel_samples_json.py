#!/usr/bin/env python3
"""
Generate a Strudel-compatible samples JSON map from this repo.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Iterable


AUDIO_EXTS = {
    ".wav",
    ".aif",
    ".aiff",
    ".mp3",
    ".ogg",
    ".flac",
}


def is_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in AUDIO_EXTS


def iter_top_level_dirs(root: Path) -> Iterable[Path]:
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            yield entry


def build_map(root: Path, base: str) -> OrderedDict:
    data: OrderedDict[str, list[str]] = OrderedDict()
    data["_base"] = base

    for top_dir in iter_top_level_dirs(root):
        files: list[str] = []
        for path in sorted(top_dir.rglob("*")):
            if is_audio_file(path):
                rel_path = path.relative_to(root).as_posix()
                files.append(rel_path)
        if files:
            data[top_dir.name] = files
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Strudel samples JSON.")
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to scan (default: current directory).",
    )
    parser.add_argument(
        "--base",
        default="",
        help="Base URL for samples (stored under _base).",
    )
    parser.add_argument(
        "--output",
        default="strudel.json",
        help="Output JSON file (default: strudel.json).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    data = build_map(root, args.base)

    output_path = Path(args.output)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
