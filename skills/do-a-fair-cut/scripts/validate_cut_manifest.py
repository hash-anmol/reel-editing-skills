#!/usr/bin/env python3
"""Validate manifest IDs/ranges and report measured encoded segment durations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe_duration(path: Path) -> float:
    value = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        text=True,
    ).strip()
    return float(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--segment-dir", required=True, type=Path)
    parser.add_argument("--expected-first")
    parser.add_argument("--expected-last")
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text())
        segments = data["segments"]
        if not isinstance(segments, list) or not segments:
            raise ValueError("manifest.segments must be a non-empty array")
        ids = [s["id"] for s in segments]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate segment IDs")
        for s in segments:
            # Accept both the compact contract (start/end) and the explicit
            # source-range form used by existing rough-cut manifests.
            start = s.get("start", s.get("sourceStart"))
            end = s.get("end", s.get("sourceEnd"))
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                raise ValueError(f"invalid range for {s.get('id')}")
            if end <= start:
                raise ValueError(f"non-positive range for {s.get('id')}")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2

    if args.expected_first and ids[0] != args.expected_first:
        print(f"wrong first segment: expected {args.expected_first}, got {ids[0]}", file=sys.stderr)
        return 4
    if args.expected_last and ids[-1] != args.expected_last:
        print(f"wrong last segment: expected {args.expected_last}, got {ids[-1]}", file=sys.stderr)
        return 5

    total = 0.0
    print("Manifest order:")
    for index, segment_id in enumerate(ids, 1):
        path = args.segment_dir / f"{segment_id}.mp4"
        if not path.is_file():
            print(f"missing segment: {path}", file=sys.stderr)
            return 3
        duration = probe_duration(path)
        total += duration
        print(f"{index:02d}. {segment_id}: {duration:.3f}s")
    print(f"Measured total: {total:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
