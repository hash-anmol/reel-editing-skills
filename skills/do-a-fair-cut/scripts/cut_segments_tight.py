#!/usr/bin/env python3
"""Speech-aware segment cutter for fair cuts: no dead air, pauses removed.

Reads an ordered edit manifest (same schema as do-a-rough-cut) and writes one
tightened clip per segment.

Cutting rules
- Clip edges sit at the first/last speech inside [sourceStart, sourceEnd] plus
a small outer pad (default 0.05 s).
- Internal pauses >= --internal-pause-min (default 0.30 s) are removed, keeping
--cut-pad (default 0.05 s) on each side.
- Speech detection: silencedetect noise=-35dB d=0.12 on the source's mono wav
(analysis/transcripts/<stem>.wav; extracted automatically when missing).
- One tone-map pass per segment by default (house HLG/BT.2020 -> BT.709 chain);
pass --no-tonemap for sources that are already SDR.

Resumable: existing outputs are skipped; *.part.mp4 leftovers are discarded.
Run heavy jobs under nice; shared hosts restart sessions mid-render.
"""
from __future__ import annotations

import argparse
import json
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


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--project", type=Path, default=None,
                    help="project dir (default: manifest dir's parent)")
    ap.add_argument("--segment-dir", type=Path, default=None,
                    help="output dir (default: <project>/analysis/cut-segments)")
    ap.add_argument("--wav-dir", type=Path, default=None,
                    help="source wavs (default: <project>/analysis/transcripts)")
    ap.add_argument("--outer-pad", type=float, default=0.05,
                    help="pad at clip edges (default 0.05 s)")
    ap.add_argument("--cut-pad", type=float, default=0.05,
                    help="pad each side of a removed pause (default 0.05 s)")
    ap.add_argument("--internal-pause-min", type=float, default=0.30,
                    help="remove internal pauses at least this long (default 0.30 s)")
    ap.add_argument("--detect-d", type=float, default=0.12,
                    help="silencedetect duration floor (default 0.12 s)")
    ap.add_argument("--noise", default="-35dB", help="silencedetect noise floor")
    ap.add_argument("--no-tonemap", action="store_true",
                    help="skip the HDR->SDR tone-map (use for SDR sources)")
    ap.add_argument("--only", default=None,
                    help="comma-separated segment ids to cut (default: all)")
    return ap.parse_args()


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def probe_duration(path: Path) -> float:
    return float(subprocess.check_output(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], text=True).strip())


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    segments = manifest["segments"]
    project = args.project or args.manifest.resolve().parent.parent
    seg_dir = args.segment_dir or project / "analysis" / "cut-segments"
    wav_dir = args.wav_dir or project / "analysis" / "transcripts"
    canvas = manifest.get("canvas", {})
    w = int(canvas.get("width", 1080))
    h = int(canvas.get("height", 1920))
    fps = int(canvas.get("fps", 30))
    seg_dir.mkdir(parents=True, exist_ok=True)
    wav_dir.mkdir(parents=True, exist_ok=True)
    only = set(args.only.split(",")) if args.only else None

    silence_cache: dict[str, list[tuple[float, float]]] = {}

    def source_wav(stem: str, src: Path) -> Path:
        wav = wav_dir / f"{stem}.wav"
        if not wav.is_file():
            print(f"  extracting wav: {wav.name}", flush=True)
            subprocess.run(
                [FFMPEG, "-y", "-v", "error", "-i", str(src),
                 "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)],
                check=True)
        return wav

    def silences_for(stem: str, src: Path) -> list[tuple[float, float]]:
        if stem in silence_cache:
            return silence_cache[stem]
        wav = source_wav(stem, src)
        r = run([FFMPEG, "-v", "info", "-i", str(wav), "-af",
                 f"silencedetect=noise={args.noise}:d={args.detect_d}",
                 "-f", "null", "-"])
        starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", r.stderr)]
        ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", r.stderr)]
        dur = probe_duration(wav)
        sils = [(s, ends[i] if i < len(ends) else dur) for i, s in enumerate(starts)]
        silence_cache[stem] = sils
        return sils

    def speech_spans(stem: str, src: Path, a: float, b: float) -> list[tuple[float, float]]:
        spans, cur = [], a
        for s, e in silences_for(stem, src):
            if e <= a or s >= b:
                continue
            s2, e2 = max(s, a), min(e, b)
            if s2 > cur:
                spans.append((cur, s2))
            cur = max(cur, e2)
        if cur < b:
            spans.append((cur, b))
        return [(x, y) for x, y in spans if y - x >= 0.10]

    def build_keeps(spans: list[tuple[float, float]]):
        keeps, removed = [], []
        cur_s, cur_e = spans[0]
        for x, y in spans[1:]:
            if x - cur_e >= args.internal_pause_min:
                removed.append((cur_e, x))
                keeps.append((cur_s, cur_e))
                cur_s, cur_e = x, y
            else:
                cur_e = y
        keeps.append((cur_s, cur_e))
        return keeps, removed

    errors = 0
    for seg in segments:
        sid = seg["id"]
        if only and sid not in only:
            continue
        src = project / seg["source"]
        stem = Path(seg["source"]).stem
        start = float(seg.get("sourceStart", seg.get("start")))
        end = float(seg.get("sourceEnd", seg.get("end")))
        out = seg_dir / f"{sid}.mp4"
        if out.is_file() and out.stat().st_size > 0:
            print(f"[{sid}] SKIP (exists)", flush=True)
            continue
        (seg_dir / f"{sid}.part.mp4").unlink(missing_ok=True)

        spans = speech_spans(stem, src, start, end)
        if not spans:
            print(f"[{sid}] ERROR: no speech found in {start:.2f}-{end:.2f}; "
                  f"widen the range or lower the noise threshold", flush=True)
            errors += 1
            continue
        keeps, removed = build_keeps(spans)
        first_start, last_end = keeps[0][0], keeps[-1][1]
        seg_a = max(0.0, first_start - args.outer_pad)
        seg_b = last_end + args.outer_pad
        trimmed = []
        for i, (ks, ke) in enumerate(keeps):
            s = (first_start - args.outer_pad) if i == 0 else (ks - args.cut_pad)
            e = (last_end + args.outer_pad) if i == len(keeps) - 1 else (ke + args.cut_pad)
            trimmed.append((max(0.0, s), e))

        removed_report = ", ".join(f"{a:.2f}-{b:.2f} ({b-a:.2f}s)" for a, b in removed) or "none"
        print(f"[{sid}] {seg['source']} {seg_a:.2f}-{seg_b:.2f}  cuts={len(trimmed)}  "
              f"removed-pauses: {removed_report}", flush=True)

        n = len(trimmed)
        parts = [f"[0:v]split={n}" + "".join(f"[vi{i}]" for i in range(n)),
                 f"[0:a]asplit={n}" + "".join(f"[ai{i}]" for i in range(n))]
        for i, (ks, ke) in enumerate(trimmed):
            parts.append(f"[vi{i}]trim=start={ks-seg_a:.3f}:end={ke-seg_a:.3f},setpts=PTS-STARTPTS[v{i}]")
            parts.append(f"[ai{i}]atrim=start={ks-seg_a:.3f}:end={ke-seg_a:.3f},asetpts=PTS-STARTPTS[a{i}]")
        if n > 1:
            pairs = "".join(f"[v{i}][a{i}]" for i in range(n))
            parts.append(f"{pairs}concat=n={n}:v=1:a=1[cv][ca]")
        else:
            parts.append("[v0]null[cv]")
            parts.append("[a0]anull[ca]")
        if args.no_tonemap:
            parts.append(f"[cv]scale={w}:{h}:force_original_aspect_ratio=increase,"
                         f"crop={w}:{h},setsar=1[vout]")
        else:
            parts.append(
                "[cv]libplacebo=tonemapping=bt.2446a:colorspace=bt709:color_primaries=bt709:"
                "color_trc=bt709:range=tv,eq=saturation=1.10,"
                f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1[vout]")
        graph = ";".join(parts)

        cmd = [FFMPEG, "-y", "-v", "error", "-nostdin"]
        if not args.no_tonemap:
            cmd += ["-init_hw_device", "vulkan=vk", "-filter_hw_device", "vk"]
        cmd += ["-ss", f"{seg_a:.3f}", "-to", f"{seg_b:.3f}", "-i", str(src),
                "-filter_complex", graph,
                "-map", "[vout]", "-map", "[ca]", "-r", str(fps),
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-movflags", "+faststart", str(seg_dir / f"{sid}.part.mp4")]
        subprocess.run(cmd, check=True)
        (seg_dir / f"{sid}.part.mp4").rename(out)
        print(f"    -> {out.name}  {probe_duration(out):.3f}s", flush=True)

    print(f"FAIR SEGMENTS DONE (errors={errors})", flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
