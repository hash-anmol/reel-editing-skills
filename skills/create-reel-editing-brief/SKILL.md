---
name: create-reel-editing-brief
description: "Turn a Reel script, timing, references, and approved edit decisions into a canonical production brief and beat-by-beat edit map."
---

# Create Reel Editing Brief

Use this skill before collecting assets or editing. It converts the creator's prompt and, when present, `EDIT_DECISIONS.md` into the source of truth for the production pass. It may draft a brief directly when the prompt is already specific; it must not invent unresolved creative choices.

## Inputs and inspection

Inspect the active project, source video, transcript or word-level timings, previous reference edits, supplied assets, and any existing brief. Preserve exact script wording and time ranges. Distinguish spoken copy, authored on-screen copy, facts to verify, and licensing notes.

## Required brief

Write or update:

- `BRIEF.md` — objective, audience, technical contract, design direction, caption system, audio arc, visual modes, approvals, and revision history.
- `SCRIPT_EDIT_MAP.md` — one row or section per meaningful spoken beat.
- `STYLE_TOKENS.json` — reusable colour, typography, spacing, safe-area, media-card, and transition values.
- `DECISIONS_LOG.md` — what changed, who approved it, and which older rule it superseded.

Use the schema in [`references/brief-schema.md`](references/brief-schema.md). The edit map must state the visual mode, A-roll visibility, media target, crop rule, caption treatment, motion, audio treatment, transition, and asset/licensing status for every beat.

## Visual modes

Use the canonical mode names exactly so the editor can route them:

1. `A-roll + caption`
2. `A-roll + media minimal overlay`
3. `Full-screen B-roll`
4. `White editorial canvas with captions`
5. `Motion graphics`

Motion graphics are deliberately separate from the white editorial caption canvas. A map, logo sequence, counter, or diagram must never be hidden inside the caption-only mode.

## Approval and revisions

End with a short approval block. Do not collect assets or mutate the edit until material decisions are approved. On every revision, update the canonical rule and append the superseded rule to `DECISIONS_LOG.md`; never leave contradictory instructions such as an old shadow treatment beside a later raw-media instruction.

This skill plans the edit. Use [`reel-asset-board`](../reel-asset-board/SKILL.md) for collection/review and [`instagram-reel-editor`](../instagram-reel-editor/SKILL.md) for implementation.
