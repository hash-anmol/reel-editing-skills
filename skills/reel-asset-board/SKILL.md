---
name: reel-asset-board
description: "Collect, normalize, provenance-check, and present Reel assets in a reviewable HTML board before editing."
---

# Reel Asset Board

Use this skill after the editing brief is approved and before the HyperFrames edit begins. It collects the exact visual and audio evidence requested by each beat; it does not silently choose generic substitutes and it does not edit the Reel.

## Collection order

1. User-supplied files and local project assets.
2. Official company, product, creator, or first-party footage.
3. Properly licensed stock libraries and royalty-free music libraries.
4. Generic fallback media only when labelled as a fallback and approved.

For every external item, verify the target identity and record the source URL, owner/creator, retrieval date, licence or usage caveat, attribution, dimensions, duration, codec, selected in/out range, and SHA-256. Download originals without overwriting user files, then create clearly named normalized copies for editing. Mute source audio on external B-roll unless the brief explicitly calls for it.

## Review board

Create `asset-review.html` with one card per beat. Each card shows the spoken line, intended mode, recommended asset, alternatives, inline image/video/audio preview, source and rights notes, and approve/reject/fallback controls with notes. Persist decisions to `asset-decisions.json`; the board is a gate, not decoration.

Use [`references/asset-manifest-schema.md`](references/asset-manifest-schema.md) for the manifest fields and [`references/review-board-spec.md`](references/review-board-spec.md) for the HTML contract. The optional helper [`scripts/build_asset_board.py`](scripts/build_asset_board.py) can build a review board from a JSON manifest.

## Music and rights

Preview the intended music arc, not just its first few seconds. A short opening hook may be repeated only for the explicitly approved intro; then use the source's natural continuation with a crossfade. Record licence evidence for royalty-free tracks and flag anything that is merely technically downloadable but not cleared for publication.

Stop and report blocked, watermarked, ambiguous, misleading, or low-quality sources. Do not replace them quietly.
