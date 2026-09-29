# Reel Editing Skills

Six agent skills for making Instagram Reels with an AI agent. Together they carry a loose recording to a finished, verified reel: plan the edit, cut the footage, finish the piece.

Built on real reels by Anmol Malik.

## What's inside

| Skill | What it does |
|---|---|
| [`grill-me-reel-edit`](skills/grill-me-reel-edit) | Interviews you about the hook, pacing, and the choices that actually change the edit, before anything gets cut. |
| [`create-reel-editing-brief`](skills/create-reel-editing-brief) | Turns the script and decisions into a production brief with a beat-by-beat edit map and the style rules. |
| [`reel-asset-board`](skills/reel-asset-board) | Collects the assets the reel needs into one reviewable board. An approval gate before editing. |
| [`do-a-rough-cut`](skills/do-a-rough-cut) | Transcript-led first cut: transcribes every take, maps the repeats, keeps your one true script, assembles an ordered cut. |
| [`do-a-fair-cut`](skills/do-a-fair-cut) | The tight pass: clips start right after the previous spoken phrase, pauses removed, dead air machine-checked. |
| [`instagram-reel-editor`](skills/instagram-reel-editor) | Builds the final reel in HyperFrames: captions, overlays, motion graphics, verified render. |

## Install

**Step 1. Install HyperFrames first.** HyperFrames renders an edit into video, and the final editing step runs on it. Ask your agent:

> "Install HyperFrames and set it up for video rendering."

**Step 2. Install these skills.** Ask your agent:

> "Clone github.com/hash-anmol/reel-editing-skills and install all six skills for me."

Or by hand: clone this repo, copy the six folders from `skills/` into your agent's skills directory, then start a new session so it sees them.

Common skills directories:

| Agent | Where |
|---|---|
| Hermes | `~/.hermes/skills/` (or your profile's `skills/` folder) |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| OpenCode | `~/.config/opencode/skills/` |

## Setup

- `ffmpeg` and `ffprobe` on PATH (both cutting skills run on them).
- Node.js and HyperFrames (only the final edit step).
- A transcriber. Local Whisper handles clean English; code-mixed speech (Hinglish) needs a code-mix model, for example Sarvam `saaras:v3` in `codemix` mode.

Full guide: **[guide/reel-editing-skills-guide.pdf](guide/reel-editing-skills-guide.pdf)**

## When to use what

| You want to | Use |
|---|---|
| Lock the edit decisions first | `grill-me-reel-edit` |
| A full brief and beat-by-beat map | `create-reel-editing-brief` |
| Collected, approved assets before editing | `reel-asset-board` |
| A first cut from repeated takes | `do-a-rough-cut` |
| A tight cut with no dead air | `do-a-fair-cut` |
| The finished reel: captions, overlays, verified render | `instagram-reel-editor` |

Normal flow: grill, brief, asset board, rough cut, fair cut, final edit.

## License

MIT. See [LICENSE](LICENSE).
