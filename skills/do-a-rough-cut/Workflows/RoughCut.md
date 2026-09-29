---
name: RoughCut
description: Transcript-first workflow for mapping repeated takes, confirming editorial choices, assembling a gapless rough cut, and rendering a verified draft.
---

# Rough cut workflow

Use this workflow for existing footage where the speaker recorded repeated versions of lines and the first deliverable is a clean, editable assembly rather than a finished social edit.

## Step 0 — sufficiency check

Before editing, inspect the request and recent conversation.

- If the source videos, intended output, and decision state are clear, proceed.
- If one missing fact would make the assembly structurally wrong, ask no more than three focused questions and stop before cutting. Offer `proceed` for a best-effort draft.
- If an ambiguity is workable, state one short flag such as: `⚠️ I’m choosing the complete take over the shorter take because it avoids a clipped sentence; redirect if you want the shorter version.`

Do not silently convert a transcript guess into a final script choice. If the user has supplied a script, this is not a script-approval task: treat the supplied wording and order as confirmed and continue to source matching.

## 1. Establish the work area and inspect media

Create a dedicated project directory such as `videos/<project-name>/`. Keep user originals untouched. Record:

- absolute source paths and SHA-256 hashes;
- duration, dimensions, frame rate, audio presence, and color metadata;
- whether each file is portrait, landscape, HDR/HLG, or SDR;
- the requested canvas, render location, and whether captions, music, graphics, or transitions are out of scope.

For an explicitly requested remote render, first verify the named SSH alias with a harmless command and check free space. Copy source files to the remote project, hash them there, and do all heavy extraction, cutting, and rendering remotely. Copy only a preview back for display unless the user asks for more. Never invent a hostname or silently use a different host.

## 2. Create the transcript evidence

Extract mono 16 kHz audio per source and transcribe locally or on the authorized render host with word timestamps. Prefer a multilingual Whisper model for mixed-language speech; use an English model only when appropriate or as a second pass. Use focused re-transcription for:

- product/project names;
- words at clip boundaries;
- lines where two takes differ;
- words the first pass marks as unintelligible.

Store raw evidence under `analysis/transcripts/` and keep the original ASR output. Correct obvious spelling and punctuation in a derived transcript, but never change a word's timestamps when correcting text. ASR is evidence, not authority: inspect the audio around disputed words before choosing a take.

For code-mixed speech (Hinglish and similar): a single English-only Whisper pass mishears Hindi clauses as plausible English and must not be used to build the script. Use a code-mix transcriber (e.g. Sarvam `saaras:v3`, mode `codemix`; keep the API key in your environment) and split the audio at measured pauses (`silencedetect=noise=-35dB:d=0.45`) so each utterance is transcribed alone and maps to an exact source range. Keep the pass resumable: write one JSON per utterance and skip existing ones.

## 3. Build the unique script and variation map

Write both artifacts before assembling the reel:

- `analysis/script-unique.md` — the deduplicated narrative in proposed viewer order;
- `analysis/script-variations.md` — every materially different take, with source file, start/end, transcript, confidence, and a short note about what changes.

If the user supplied a script in the prompt or as a file:

- preserve it verbatim in `analysis/script-provided.md`;
- use it as the authoritative wording and order for `analysis/script-unique.md`;
- mark those wording/order decisions **confirmed by user**;
- use the transcript and variation map to locate the matching takes and expose alternatives, not to reopen the script decision;
- flag a specific source mismatch, missing line, or genuinely ambiguous match, but do not silently rewrite the supplied script.

Group repeated attempts by meaning, not only exact ASR text. Keep variants separate when they change wording, language, claim strength, project name, CTA, or where the speaker stops. Mark each decision as:

- **confirmed by user**;
- **inferred from the request**;
- **candidate**;
- **unresolved**.

The map must make it easy to answer “which version did I say?” without reopening every source video. Include a proposed sequence and a table like:

| Order | Segment | Candidate | Source range | Wording / ending | Status |
|---|---|---|---|---|---|
| 1 | Hook | A | `IMG_0001.MOV 00:00–00:18` | complete sentence | inferred |
| 2 | Main claim | B | `IMG_0002.MOV 01:12–01:25` | ends after “here?” | candidate |

## 4. Decision checkpoint — do not cut past unresolved choices

When no script was supplied, present the proposed script and variation map in the conversation, then ask for the smallest set of decisions that materially changes the edit. Typical decisions are:

- exact take for each competing line;
- whether a line ends at a particular word or includes the speaker's continuation;
- narrative order and whether a claim follows immediately after a question;
- which named projects or examples to keep;
- CTA wording;
- relaxed handle length versus hard word-level cuts;
- canvas/aspect ratio and whether to preserve, neutralize, or convert HDR color;
- whether captions, music, graphics, or transitions are included.

When a script was supplied, do not ask for script confirmation. Give a concise match report—what was found, what take/range was selected, and any source mismatch—and proceed automatically if no material non-script choice remains. Ask only about decisions the script cannot answer, such as a material choice between two equally matching takes, remote render destination, canvas/aspect ratio, handles, color treatment, captions, music, graphics, or transitions. Record the supplied-script authority and any assumptions in `analysis/edit-decisions.md`.

Confirm decisions already supplied by the user instead of asking again. If the user says “do it,” use the stated choices and resolve only harmless details. Do not render a final-looking polished edit at a script-approval checkpoint; with a supplied script there is no script-approval checkpoint, so proceed to the rough-cut render once source matching is complete.

## 5. Write the edit manifest

After the checkpoint, create `analysis/edit-manifest.json` with one ordered `segments` array. Each segment should contain:

```json
{
  "id": "culture-question",
  "source": "source/IMG_0002.MOV",
  "start": 81.25,
  "end": 90.85,
  "text": "The selected wording and intended stopping point.",
  "preRoll": 0.25,
  "postRoll": 0.20,
  "decision": "confirmed"
}
```

For a user-supplied script, the `text` field must reproduce the selected supplied-script line, and `decision` should be `confirmed` for the script wording/order. A matching take choice may still be `inferred` or `candidate` when the source contains materially different performances.

The array is authoritative. It must already be in viewer order. Validate unique IDs, positive ranges, source bounds, and any explicit first/last segment expectation before cutting.

## 6. Cut and assemble the rough draft

Use the manifest to create normalized segment files with matching video/audio source ranges. For a social talking-head rough cut, default to immediate cuts with no transition, no gap, no added silence, and no captions/music/graphics unless confirmed. Use modest handles—usually 0.2–1.0 seconds—when the user asks for relaxed cuts; handles should make manual trimming possible without importing a duplicated sentence.

Use `scripts/build_ordered_concat.py` to write the FFmpeg concat file. It must read the manifest array in order and fail if a segment is missing or duplicated. Do not use `for f in *.mp4`, `sort`, directory order, or any other filename-derived ordering.

Normalize only as needed for reliable concatenation. For a default Instagram Reel output use 1080×1920, 30 fps, H.264, yuv420p, AAC, and 48 kHz audio. Preserve framing and do not add zooms or crops unless requested.

Write each normalized segment to its own file and skip existing files when rerunning, and run heavy jobs with `nice`. Shared hosts restart sessions mid-render; a rerun of the same script must resume from the completed segments.

Tight-jump-cut variant (when the user asks to remove dead air): cut every clip at its first/last speech (0.05 s pads; detect with `silencedetect=noise=-35dB:d=0.12` on the source) and remove internal pauses ≥ 0.30 s (0.05 s pads each side). After assembly, assert the result: silencedetect on the final render must show no silence above ~0.15 s. Then run a post-edit QC pass on the finished render: transcribe it with the code-mix transcriber and read the whole thing back for repeats, order, and sense before handoff — this is also the check that catches delivered-line defects like a repeated lead-in.

## 7. Handle color deliberately

Probe the source and cut files. If footage is HLG/BT.2020:

1. preserve the source profile in the intermediate cut when possible;
2. apply one explicit tone map for an SDR deliverable;
3. tag the result BT.709;
4. compare representative source/output frames for exposure, skin tone, white shirt/highlight clipping, and white balance.

Do not tone-map each stage and then tone-map the final again. If the user says the grade is wrong, fix the color pipeline before changing editorial ranges.

## 8. Validate and render

Build an optional HyperFrames HTML composition from the same ordered segment list and run `npx hyperframes check <project>` when HyperFrames is available. The check validates the preview structure; it does not replace validation of a separate FFmpeg export.

Render the actual MP4 from the manifest-ordered concat file. Then run:

- `scripts/validate_cut_manifest.py` against the cut directory;
- `ffprobe` for duration, dimensions, frame rate, codecs, pixel format, and color tags;
- a complete video decode and complete audio decode;
- first, boundary, midpoint, and final-frame extraction/contact sheet inspection;
- a start-order assertion that the first segment in the MP4 is the manifest's first segment.

If remote, compare the remote render hash with the copied local preview hash. Report failures plainly; do not call an HTML check a successful render.

## 9. Handoff

Return:

- the playable preview or absolute local preview path;
- the authoritative remote render path when applicable;
- the exact duration and output format;
- the script/variation-map paths;
- the decisions applied and any remaining uncertainty;
- what was verified and what was not.

State that this is a raw rough cut when it contains no captions, graphics, music, or final polish.
