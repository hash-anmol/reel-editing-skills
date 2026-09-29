# Asset manifest schema

`ASSET_MANIFEST.md` is human-reviewable. Keep one row per file or intentional file set.

| Field | Required meaning |
|---|---|
| File | Relative path to the preserved original or normalized edit copy |
| Beat | Script beat(s) where it may appear |
| Role | Image, B-roll, logo, music, SFX, poster, or fallback |
| Source URL | Direct page or download URL, not a search-results page |
| Owner / creator | Company, creator, library, or user-supplied |
| Retrieved | ISO date and retrieval method |
| Licence / usage | Licence evidence, attribution, or unresolved caveat |
| Technical | Dimensions, duration, codec, frame rate, audio channels |
| Selection | Exact source in/out and any crop or mute decision |
| Hash | SHA-256 of the preserved file |
| Decision | Recommended, alternate, approved, rejected, or blocked |

Do not write “royalty-free” without evidence. A successful download is not a licence grant.
