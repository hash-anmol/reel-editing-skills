# Reel editing brief schema

Keep this document concise enough to review. The brief is a decision record, not a diary of every search or render attempt.

## `BRIEF.md`

1. **Objective** — audience, promise, platform, aspect ratio, target duration, and success criterion.
2. **Locked inputs** — source paths, transcript version, spoken-copy rules, reference edits, and technical constraints.
3. **Design direction** — colour, type, caption safe area, emphasis colour, spacing, crop philosophy, and motion vocabulary.
4. **Caption system** — where captions appear, when they are omitted, word timing, emphasis limits, and authored-card rules.
5. **Audio arc** — source track, intro/continuation plan, volume envelope, dialogue ducking, SFX policy, and source-audio muting.
6. **Visual modes** — links to the editor's mode references and the criteria for choosing each mode.
7. **Approval block** — explicit status for script, style, assets, audio, fact handling, and final delivery.

## `SCRIPT_EDIT_MAP.md`

Use one section per meaningful beat:

```text
Beat / global time range:
Spoken line:
Intent:
Visual mode:
A-roll visibility:
Media target and required proof:
Crop / aspect / full-visibility rule:
Caption or authored text:
Motion:
Audio / SFX:
Transition:
Asset status / source / licence note:
Open question or approval:
```

## `STYLE_TOKENS.json`

Keep machine-readable values for background, ink, accent, fonts, font sizes, safe-area bounds, caption position, media geometry, default transition, and audio levels. Name tokens semantically; do not bury values in prose only.

## Revision log

Every revision entry includes:

```text
date:
feedback:
changed rule:
superseded rule:
affected beats:
approval status:
```
