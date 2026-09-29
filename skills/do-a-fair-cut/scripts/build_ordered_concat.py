#!/usr/bin/env python3
"""Write an FFmpeg concat list from manifest order, never filename order."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def ffconcat_quote(path: Path) -> str:
    # FFmpeg concat files use single-quoted paths. Escape embedded quotes.
    return str(path.resolve()).replace("'", "'\\''")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--segment-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text())
        segments = data["segments"]
        if not isinstance(segments, list) or not segments:
            raise ValueError("manifest.segments must be a non-empty array")
        ids = [s["id"] for s in segments]
        if len(ids) != len(set(ids)):
            raise ValueError("manifest contains duplicate segment IDs")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2

    paths = []
    for segment in segments:
        segment_id = segment["id"]
        candidate = args.segment_dir / f"{segment_id}.mp4"
        if not candidate.is_file():
            print(f"missing segment for manifest order: {candidate}", file=sys.stderr)
            return 3
        paths.append(candidate)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(f"file '{ffconcat_quote(path)}'\n" for path in paths))
    print("Ordered concat:")
    for index, path in enumerate(paths, 1):
        print(f"{index:02d}. {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
