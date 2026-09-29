#!/usr/bin/env python3
"""Assert a fair cut has no dead air: the longest silence must be small.

Runs silencedetect on the render's audio and fails when any detected silence
exceeds --max-silence (default 0.15 s). Joint pads in a fair cut keep the
longest silence around 0.10-0.15 s; anything longer is dead air that survived
the cut.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def find_tool(name: str) -> str:
    local = Path.home() / ".local" / "bin" / name
    if local.is_file():
        return str(local)
    found = shutil.which(name)
    if found:
        return found
    sys.exit(f"error: {name} not found on PATH or ~/.local/bin")


FFMPEG = find_tool("ffmpeg")
FFPROBE = find_tool("ffprobe")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final", required=True, type=Path,
                    help="finished render to check")
    ap.add_argument("--max-silence", type=float, default=0.15,
                    help="fail when a silence exceeds this (default 0.15 s)")
    ap.add_argument("--detect-d", type=float, default=0.10,
                    help="silencedetect duration floor; must be < --max-silence")
    ap.add_argument("--noise", default="-35dB")
    args = ap.parse_args()

    if args.detect_d >= args.max_silence:
        sys.exit("error: --detect-d must be smaller than --max-silence, "
                 "or short dead air cannot be detected")

    r = subprocess.run(
        [FFMPEG, "-v", "info", "-i", str(args.final), "-af",
         f"silencedetect=noise={args.noise}:d={args.detect_d}",
         "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", r.stderr)]
    dur = float(subprocess.check_output(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(args.final)], text=True).strip())
    sils = [(s, ends[i] if i < len(ends) else dur) for i, s in enumerate(starts)]
    longest = max((e - s for s, e in sils), default=0.0)

    print(f"file: {args.final}")
    print(f"silences >= {args.detect_d:.2f}s: {len(sils)}")
    for s, e in sorted(sils, key=lambda x: x[1] - x[0], reverse=True)[:5]:
        print(f"  {s:7.3f}-{e:7.3f}  {e-s:.3f}s")
    print(f"longest silence: {longest:.3f}s  (limit {args.max_silence:.3f}s)")
    if longest > args.max_silence:
        print("FAIL: dead air found; re-cut the offending joint")
        return 1
    print("PASS: no dead air")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
