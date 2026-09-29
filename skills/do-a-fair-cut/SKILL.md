---
name: do-a-fair-cut
description: "Use when the creator wants tight jump cuts, no dead air."
---

# Do a Fair Cut

Build a tight jump-cut edit from recorded takes. A fair cut is a rough cut with the dead air taken out: every clip begins immediately after the previous spoken phrase ends, internal pauses are removed, and the finished render is asserted for silence before handoff. The pipeline is transcript-first, like `do-a-rough-cut`; the difference is the cutting rule and the extra verification.

## When to Use

- The creator asks for tight jump cuts, a "fair cut", or says to remove all dead air and pauses so every clip begins immediately after the previous spoken phrase ends.
- An existing rough cut needs tightening: the takes are already chosen and only the pauses and handles need to go.
- Not for captions, graphics, music, or final polish unless explicitly requested.

Sibling skill: use [`do-a-rough-cut`](../do-a-rough-cut/SKILL.md) when the creator wants handles for manual trimming; use this skill when they want the pauses gone.

## Workflow routing

| Request | Workflow |
|---|---|
| Create a fair cut, or tighten an existing rough cut | `Workflows/FairCut.md` |

## Non-negotiable invariants

- Preserve source originals; work from copies or source references.
- Evidence first: unique script, variation map, and ordered manifest before cutting (same as `do-a-rough-cut`). Match ASR to the speech: code-mixed takes (e.g. Hinglish) need a code-mix transcriber (e.g. Sarvam `saaras:v3`, mode `codemix`).
- Speech is the clock: clip edges sit at the first/last speech inside the selected range plus 0.05 s pads; detection is `silencedetect=noise=-35dB:d=0.12` on the source audio. Never cut mid-word.
- No dead air: internal pauses >= 0.30 s are removed (0.05 s pads each side). After assembly, the longest silence anywhere in the render must be <= ~0.15 s — assert it with `scripts/check_dead_air.py`, do not eyeball it.
- Never merge an aborted lead-in with the take that follows it. A stub plus its full take is exactly how a repeated line ships; keep the complete take alone.
- The ordered edit manifest is the only source of timeline order. Never build a concat list from a filesystem glob.
- One deliberate tone-map per segment for HDR sources (house HLG/BT.2020 to BT.709 chain). On GPU-less hosts run libplacebo through the software Vulkan device (`-init_hw_device vulkan=vk -filter_hw_device vk`), keep it SW-in/SW-out, and verify colors via channel means, not luma stats.
- A render is not done until verified: probe, full decode, boundary order, dead-air assertion, hash. Then transcribe the finished cut and read it back for repeats, order, and sense.
- When ASR drops a word ending in the finished cut, test the source range with extra tail room before blaming the cut: unreleased final consonants are normal speech, not edit defects.

## Supporting material

- Main procedure: [Workflows/FairCut.md](Workflows/FairCut.md)
- Timeline, color, and render contract (tight variant): [references/ProductionContract.md](references/ProductionContract.md)
- Speech-aware segment cutter: `scripts/cut_segments_tight.py`
- Dead-air assertion for the final render: `scripts/check_dead_air.py`
- Deterministic concat helper: `scripts/build_ordered_concat.py` (mirrors `do-a-rough-cut`)
- Cut-manifest verifier: `scripts/validate_cut_manifest.py` (mirrors `do-a-rough-cut`)

## Example

```text
User: "Cut this reel tight. Remove all dead air and pauses so every clip begins immediately after the previous spoken phrase ends."
→ Builds transcript evidence and the variation map, confirms only unresolved take choices, writes the ordered manifest with a tight cutStyle.
→ Cuts each clip at its speech boundaries with internal pauses removed, assembles in manifest order, verifies the render including the dead-air assertion, then transcribes the finished cut and reads it back for repeats, order, and sense before handoff.
```
