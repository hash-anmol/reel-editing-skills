# Production contract — fair cut

This reference defines the fragile parts of a tight jump-cut edit (a "fair cut"). Read it before writing a manifest, cutting segments, or assembling a render.
It carries the rough-cut production contract forward and adds the tight rules.

## Tight-cut rules

- Clip edges sit at speech: first/last speech inside the selected range, plus a
  0.05 s pad. Detection runs on the source audio with
  `silencedetect=noise=-35dB:d=0.12`; speech spans shorter than ~0.10 s are
  treated as noise and ignored.
- Internal pauses >= 0.30 s are removed, keeping 0.05 s of pad on each side of
  the cut. Shorter gaps stay: they are speech rhythm, not dead air.
- Joint target: at most ~0.15 s of room tone between phrases. Assert it with
  `scripts/check_dead_air.py`; the cut is not done while a longer silence
  exists anywhere in the render.
- Handles are minimal by design (0.05 s): they protect word onsets and
  releases, not manual trimming. If the creator wants trimming handles, that
  is a rough cut.
- Never merge an aborted lead-in with the full take that follows it. Keep the
  complete take alone; a stub plus its take is how a repeated line ships.
- `sourceStart`/`sourceEnd` remain the utterance bounds from the pause-split
  transcript. The cutter derives the real edges from speech detection, so the
  manifest bounds do not need to be frame-exact.

## File roles

```text
<project>/
├── source/                         # copied originals or adopted source references
├── analysis/
│   ├── transcripts/                # ASR evidence + source wavs used for detection
│   ├── script-provided.md          # verbatim user-supplied script, when provided
│   ├── script-unique.md            # deduplicated proposed script
│   ├── script-variations.md        # alternatives with source ranges
│   ├── edit-decisions.md           # user confirmations and assumptions
│   ├── edit-manifest.json          # authoritative ordered timeline (+ cutStyle)
│   ├── cut-segments/               # tightened intermediate clips
│   ├── concat-ordered.txt          # generated only from the manifest
│   ├── final-qc.json               # post-edit transcript read-back of the render
│   └── verification.md             # render + dead-air + QC results
└── renders/
    └── <project>-rough-cut.mp4     # verified playable output
```

Do not overwrite source originals. A local preview copied from a remote render
is not the authoritative remote artifact; report both paths.

## Timeline contract

- `segments` order is semantic viewer order.
- Every segment has one video range and the matching audio range.
- `end > start` and both values are within the source duration.
- Encoded segment duration may differ by a frame; assemble using measured
  encoded durations, not only requested durations.
- The final timeline is contiguous: the next segment starts exactly where the
  prior segment ends.
- Removing internal pauses >= 0.30 s is deliberate for a fair cut; do not
  "fix" it back. A rough cut keeps those pauses; this cut does not.

## Color contract

Probe `color_space`, `color_transfer`, `color_primaries`, and pixel format.
HDR input commonly reports BT.2020 plus HLG (`arib-std-b67`). A BT.709 SDR
deliverable should have BT.709 tags and yuv420p. Use one tone-map path per
segment and inspect frames; metadata alone cannot prove a correct grade. On
hosts without a GPU, run libplacebo through the software Vulkan device
(lavapipe) via `-init_hw_device vulkan=vk -filter_hw_device vk` and keep the
filter SW-in/SW-out (the bare filter fails device init with `Found no suitable
device`; a hwupload/hwdownload wrapper can run yet silently zero the chroma
planes — monochrome-green output — so verify colors via channel means, not
luma stats).

## Render contract

The actual MP4 is the deliverable. A composition preview, lint result, or
successful command is not sufficient. A render is complete only when:

1. the expected first segment is visible at the beginning;
2. duration and stream metadata match the requested output;
3. video and audio decode to EOF without errors;
4. representative frames show correct orientation, exposure, and no gaps;
5. the dead-air assertion passes (`scripts/check_dead_air.py`, longest
   silence <= ~0.15 s);
6. the output hash/path is recorded.

## Decision states

Use explicit state labels in `edit-decisions.md`:

- `confirmed` — the user chose it;
- `inferred` — directly implied by the request and reversible;
- `candidate` — shown for user selection;
- `unresolved` — do not make an irreversible cut yet.

When a user supplies the script, record that the script is authoritative and
mark its wording and order `confirmed`. The variation map remains source
evidence; it must not turn an already supplied script into a second approval
gate.
