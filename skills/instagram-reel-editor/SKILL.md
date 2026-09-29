---
name: instagram-reel-editor
description: "Build, revise, and verify a minimal, story-led Instagram Reel in HyperFrames from an approved brief and asset board."
---

# Instagram Reel Editor

Use this skill when `BRIEF.md` and the asset board are approved and the task is to implement or revise the actual Reel. It is the execution and verification layer; it should not invent a new visual treatment while editing.

## Inputs and gates

Inspect the active project, source A-roll, transcript timings, `BRIEF.md`, `SCRIPT_EDIT_MAP.md`, `STYLE_TOKENS.json`, `ASSET_MANIFEST.md`, and `asset-decisions.json`. If a material brief or asset decision is missing, stop at that gate and ask for it rather than silently guessing. Preserve user files and keep generated renders separate from sources.

Before a costly full render, make a targeted preview of the opening, one changed middle beat, and the ending. For audio changes, preview the intro-to-continuation transition and the last 8 seconds first.

## Canonical visual language

Route each beat to one of the detailed references below:

- [`a-roll-plus-caption.md`](references/a-roll-plus-caption.md)
- [`a-roll-plus-media-minimal-overlay.md`](references/a-roll-plus-media-minimal-overlay.md)
- [`full-screen-b-roll.md`](references/full-screen-b-roll.md)
- [`white-editorial-canvas-with-captions.md`](references/white-editorial-canvas-with-captions.md)
- [`motion-graphics.md`](references/motion-graphics.md)

The white editorial caption canvas and motion graphics are separate modes. Do not put maps, counters, diagrams, or logo animations in the caption-only reference.

Defaults learned from this workflow:

- Minimal means raw media: no border, shadow, label, or duplicate explanatory caption unless the approved brief explicitly requests it.
- Keep captions consistent in a lower-centre, face-safe region; reserve centred text for deliberate editorial cards.
- Use exact relevant footage over generic decoration, and keep recognition-critical images fully visible.
- Make consecutive B-roll clips contiguous with hard cuts. Prevent one-frame A-roll flashes, blank first frames, and accidental dissolve carry-over with posters/readiness handling.
- Keep the caption, colour, spacing, and motion vocabulary consistent. Change style only when the meaning requires it.

Read [`references/style-system.md`](references/style-system.md) for shared tokens, [`references/music-and-sound.md`](references/music-and-sound.md) for soundtrack decisions, and [`references/qa-and-delivery.md`](references/qa-and-delivery.md) before claiming completion. The examples are principles, not assets to reuse blindly:

- [`examples/builder-culture-reel.md`](examples/builder-culture-reel.md)
- [`examples/reintroduction-reference.md`](examples/reintroduction-reference.md)

## Audio and implementation

Use the approved soundtrack and the audio arc in the brief. Never repeat a short hook across an entire reel by default: if the intro is intentionally looped, limit it to the approved intro window, crossfade into the source continuation, and automate a deliberate middle fade and ending pickup. Read [`references/music-and-sound.md`](references/music-and-sound.md) for the decision rules. Keep dialogue dominant and mute external B-roll audio unless explicitly approved.

Use the existing HyperFrames skills for composition, captions, media readiness, animation, and audio rather than copying their manuals. Keep source timing explicit (`data-start`, `data-duration`, and `data-media-start` where applicable), use intentional z-index/overlap declarations, and preserve exact asset paths.

## Verification and delivery

Run the pinned project check. Then inspect representative frames and every changed boundary, including adjacent frames around hard cuts. Verify the final artifact with `ffprobe` (duration, dimensions, frame rate, codecs, colour metadata, audio) and a full `ffmpeg -v error` decode. Check audio loudness and the actual transition/ending, not merely a successful render. Report the render path, download path, and SHA-256 identity only after read-back.
