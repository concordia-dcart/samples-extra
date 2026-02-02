#!/usr/bin/env python3
"""
Generate a Strudel-compatible samples JSON map.

- Requires Python 3. Run from the repo root: `python3 generate_strudel_samples_json.py --root . --base https://your.cdn.example/samples-extra --output strudel.json`.
- `--base` sets the URL prefix stored under `_base` in the JSON; leave it empty for local file use.
- The generated `strudel.json` maps each sample folder to its audio files for Strudel or any sampler that reads the same format.
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


def iter_audio_dirs(root: Path) -> Iterable[Path]:
    """Yield all non-hidden subdirectories under root, depth-first sorted."""
    dirs = [
        path
        for path in root.rglob("*")
        if path.is_dir()
        and not any(part.startswith(".") for part in path.relative_to(root).parts)
    ]
    for path in sorted(dirs, key=lambda p: p.relative_to(root).as_posix()):
        yield path


def build_map(root: Path, base: str) -> OrderedDict:
    data: OrderedDict[str, list[str]] = OrderedDict()
    data["_base"] = base

    for directory in iter_audio_dirs(root):
        files: list[str] = []
        for path in sorted(directory.iterdir()):
            if is_audio_file(path):
                rel_path = "/" + path.relative_to(root).as_posix()
                files.append(rel_path)
        if files:
            key = directory.name
            if key not in data:
                data[key] = []
            data[key].extend(files)
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
        # Compact JSON: single line with no extra spaces to match Strudel example.
        json.dump(data, f, ensure_ascii=True, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
