---
name: FairCut
description: Tight-jump-cut workflow — no dead air, speech-boundary cuts, dead-air assertion, and a post-edit transcript QC pass.
---

# Fair cut workflow

Use this workflow when the creator wants a tight jump-cut edit: every clip begins immediately after the previous spoken phrase ends, and all dead air and pauses are removed. It follows the same transcript-first pipeline as the rough-cut workflow; this document covers everything from the ordered manifest onward, plus the tight cutting rules, the dead-air assertion, and the post-edit QC pass.

If the project has no evidence or manifest yet, run `do-a-rough-cut` first (evidence, unique script, variation map, decision checkpoint, ordered manifest), then return here. If a rough cut already exists and only needs tightening, start at step 1.

## 1. Manifest shape for a fair cut

Same schema as the rough cut, plus a `cutStyle` block:

```json
{
  "cutStyle": {
    "type": "tight-jump-cut",
    "outerPadSeconds": 0.05,
    "internalPauseMinSeconds": 0.30
  }
}
```

`sourceStart`/`sourceEnd` stay the utterance bounds from the pause-split transcript (the ASR evidence). The cutter derives the real edges from speech detection, so manifest bounds do not need to be frame-exact.

Rules when selecting ranges:

- Never merge an aborted lead-in with the full take that follows it. If the speaker restarts a phrase, keep the complete take alone; merging a stub plus its full take is exactly how a line gets repeated in the delivery.
- Prefer the cleaner performance when takes differ; final consonants are allowed to be soft (that is how people speak), but do not cut into the word.

## 2. Cut the segments

Run the cutter from the skill directory (in this repo: `.agents/skills/do-a-fair-cut/scripts/cut_segments_tight.py`):

```bash
python3 .agents/skills/do-a-fair-cut/scripts/cut_segments_tight.py \
  --manifest videos/<project>/analysis/edit-manifest.json
```

Per segment it: detects silences on the source's mono wav (`silencedetect -35dB/0.12s`, extracted to `analysis/transcripts/<stem>.wav` when missing), sets clip edges at first/last speech plus 0.05 s pads, removes internal pauses >= 0.30 s (0.05 s pads each side), applies one tone-map pass, and encodes H.264/AAC.

- Run it under `nice` and keep it resumable: finished segments are skipped, so a killed run can simply be restarted. Shared hosts restart sessions mid-render.
- Read the printed per-segment report (`cuts=N`, `removed-pauses: ...`). If a removed pause carries meaning (for example a beat before a punchline), raise `--internal-pause-min` for that project rather than editing by hand.
- To force a re-cut, delete the segment file (or its `*.part.mp4` leftover) and rerun; `--only id1,id2` cuts a subset.

## 3. Assemble

Use `scripts/build_ordered_concat.py` (manifest order only, never a glob), then stream-copy concat:

```bash
ffmpeg -y -v error -f concat -safe 0 -i analysis/concat-ordered.txt \
  -c copy -movflags +faststart renders/<project>-rough-cut.mp4
```

## 4. Verify the render (including dead air)

Standard verification first: probe metadata, full video and audio decode, boundary order check (final frame vs segment frame), frame sanity, contact sheet, hash. Then the fair-cut assertion:

```bash
python3 .agents/skills/do-a-fair-cut/scripts/check_dead_air.py \
  --final renders/<project>-rough-cut.mp4 --max-silence 0.15
```

It fails when any silence in the render exceeds the threshold. A fair cut should show a longest silence of roughly 0.10-0.15 s (the joint pads). If it fails, find the offending joint and re-cut that segment. Also spot-check colors via RGB channel means of sampled frames (not luma only): all three channels must carry data.

## 5. Post-edit QC (transcribe the finished cut)

After the render is verified, transcribe the finished cut's audio and read the whole thing back before handoff:

- Use the same code-mix ASR as the evidence pass (e.g. Sarvam `saaras:v3`, mode `codemix`). A tight cut has no long pauses, so split the audio into fixed chunks of ~15 s instead of relying on pause detection; keep the pass resumable.
- Read the chunks in order and check: nothing repeated, nothing out of place, order matches the intended script, and it makes sense end to end.
- When ASR drops or mangles a word in the finished cut, test the source range with extra tail room before blaming the cut. Unreleased final consonants and context-free chunks are normal ASR artifacts, not edit defects.
- Save the QC transcript (for example `analysis/final-qc.json`) and record the outcome in `analysis/verification.md`.

## 6. Handoff

Report: the render path, exact duration, SHA-256, the dead-air result (longest silence), the QC outcome, and the preview link. State that it is a rough-cut-stage piece (no captions, music, or graphics) unless the project has moved past that stage.
