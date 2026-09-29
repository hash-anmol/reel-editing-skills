---
name: do-a-rough-cut
description: "Create a transcript-led rough cut from repeated video takes: extract the spoken script, map unique variations to source time ranges, use a supplied script as authoritative when provided, confirm only unresolved editorial choices, assemble an ordered gapless draft, and render a verified preview. USE WHEN cleaning recorded footage, removing repeated takes, building a script variation map, choosing takes for a reel, assembling a rough cut, or rendering a first edit. NOT FOR final polish, captions, graphics, music, or color styling unless explicitly requested."
---

# Do a Rough Cut

Build an editable first cut from several recordings of the same spoken piece. The skill is deliberately transcript-first: it keeps the words and their source ranges visible before making irreversible editorial choices. When the user supplies the script, that wording and order become the editorial source of truth; the transcript and variation map are then used to locate and validate the matching takes rather than to ask for script approval again.

## Workflow routing

| Request | Workflow |
|---|---|
| Create, revise, or render a transcript-led rough cut | `Workflows/RoughCut.md` |

## Non-negotiable invariants

- Preserve source originals; work from copies or source references.
- Produce a unique-script document and a variation map before cutting.
- Match ASR to the speech: for code-mixed takes (e.g. Hinglish), use a code-mix transcriber (e.g. Sarvam `saaras:v3`, mode `codemix`; keep the API key in your environment) with utterance splits at measured pauses. A single English-only Whisper pass produces confident, badly wrong text on code-mixed audio.
- If the user supplies a script, treat its wording and order as confirmed; do not ask the user to confirm the script again. Confirm only decisions the supplied script cannot answer.
- Pause at the decision checkpoint when competing takes materially change the words, meaning, or ending. “Proceed” is a valid best-effort override.
- Treat the ordered edit manifest as the only source of timeline order. Never build an FFmpeg concat list from a filesystem glob.
- Keep selected audio and video ranges identical, cut immediately between segments, and leave handles around words when the user asks for a relaxed rough cut.
- Inspect source color metadata. Apply at most one deliberate HLG/BT.2020 → BT.709 SDR conversion, then verify the result visually.
- On GPU-less hosts, libplacebo needs an explicit software Vulkan device: `-init_hw_device vulkan=vk -filter_hw_device vk`; the bare filter fails device init with `Found no suitable device`. Keep it SW-in/SW-out: a hwupload/hwdownload wrapper can run yet silently zero the chroma planes (monochrome-green output), so verify colors via channel means, not luma stats.
- Verify the rendered MP4 itself, not only the HTML/composition preview: probe metadata, decode all video and audio, check first/last frames, and report the real output path and duration.

## Supporting material

- Main procedure: [Workflows/RoughCut.md](Workflows/RoughCut.md)
- Timeline and render contract: [references/ProductionContract.md](references/ProductionContract.md)
- Deterministic concat helper: `scripts/build_ordered_concat.py`
- Cut-manifest verifier: `scripts/validate_cut_manifest.py`

## Example

```text
User: “Use these three recordings to make a rough Instagram reel. Remove repeats, show me the script variations first, then cut and render it.”
→ Transcribes each source and writes the unique script plus variation map.
→ Asks only the unresolved take/order/ending decisions.
→ After confirmation, writes an ordered manifest, creates relaxed gapless cuts, renders, and verifies the MP4.

User: “Here is the final script: [script]. Use it to make the rough cut.”
→ Saves the supplied script verbatim, marks its wording/order as confirmed, and maps each line to the best matching source range.
→ Does not ask for script approval; it asks only about a genuine non-script ambiguity or proceeds automatically when none remains.
→ Writes the ordered manifest, creates relaxed gapless cuts, renders, and verifies the MP4.
```
