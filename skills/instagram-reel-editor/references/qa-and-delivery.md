# QA and delivery

Do not call a render final because the command exited zero. Verify the artifact and the edit decisions.

## Before the full render

- Run the project's pinned HyperFrames check; resolve errors and warnings that affect the edit.
- Create targeted previews for the opening, every changed beat, and the final 8 seconds.
- Extract frames immediately before and after every hard cut, especially where one video replaces another.
- Confirm first-frame readiness, no blank frame, no A-roll flash, no accidental overlay, and no text collision.
- Listen to the music handoff, middle fade, and ending at the intended playback level.

## Final artifact

Read back with `ffprobe`: duration, width, height, frame rate, video/audio codecs, sample rate, channels, and colour metadata. Run a complete `ffmpeg -v error -f null -` decode and require an empty error log. Check representative frames as an actual contact sheet, not only CSS or snapshots.

## Delivery record

Record:

- render path and review/master name;
- project check result;
- source and asset manifest versions;
- any intentional caveats or unverified claims;
- final file hash and, when copied, a hash comparison between master and download.

Report gaps plainly. A technically valid file with an unresolved rights, factual, or editorial problem is not a finished delivery.
