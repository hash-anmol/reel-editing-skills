# Production contract

This reference defines the fragile parts of a transcript-led rough cut. Read it before writing a manifest, concat file, or render command.

## File roles

```text
<project>/
├── source/                         # copied originals or adopted source references
├── analysis/
│   ├── transcripts/                # raw and focused word-level ASR evidence
│   ├── script-provided.md          # verbatim user-supplied script, when provided
│   ├── script-unique.md            # deduplicated proposed script
│   ├── script-variations.md        # alternatives with source ranges
│   ├── edit-decisions.md           # user confirmations and assumptions
│   ├── edit-manifest.json          # authoritative ordered timeline
│   ├── cut-segments/               # normalized intermediate clips
│   └── concat-ordered.txt          # generated only from the manifest
└── renders/
    └── <project>-rough-cut.mp4     # verified playable output
```

Do not overwrite source originals. A local preview copied from a remote render is not the authoritative remote artifact; report both paths.

## Timeline contract

- `segments` order is semantic viewer order.
- Every segment has one video range and the matching audio range.
- `end > start` and both values are within the source duration.
- Encoded segment duration may differ by a frame; assemble using measured encoded durations, not only requested durations.
- The final timeline is contiguous: the next segment starts exactly where the prior segment ends.
- “Gapless” means no timeline gap. It does not mean delete every natural pause inside a chosen take.
- Handles are intentional and documented. Never hide an unwanted duplicated word inside a handle.

## Color contract

Probe `color_space`, `color_transfer`, `color_primaries`, and pixel format. HDR input commonly reports BT.2020 plus HLG (`arib-std-b67`). A BT.709 SDR deliverable should have BT.709 tags and yuv420p. Use one tone-map path and inspect frames; metadata alone cannot prove a correct grade. On hosts without a GPU, run libplacebo through the software Vulkan device (lavapipe) via `-init_hw_device vulkan=vk -filter_hw_device vk` and keep the filter SW-in/SW-out (the bare filter fails device init with `Found no suitable device`; a hwupload/hwdownload wrapper can run yet silently zero the chroma planes — monochrome-green output — so verify colors via channel means, not luma stats).

## Render contract

The actual MP4 is the deliverable. A composition preview, lint result, or successful command is not sufficient. A render is complete only when:

1. the expected first segment is visible at the beginning;
2. duration and stream metadata match the requested output;
3. video and audio decode to EOF without errors;
4. representative frames show correct orientation, exposure, and no gaps;
5. the output hash/path is recorded.

## Decision states

Use explicit state labels in `edit-decisions.md`:

- `confirmed` — the user chose it;
- `inferred` — directly implied by the request and reversible;
- `candidate` — shown for user selection;
- `unresolved` — do not make an irreversible cut yet.

When a user supplies the script, record that the script is authoritative and mark its wording and order `confirmed`. The variation map remains source evidence; it must not turn an already supplied script into a second approval gate.
