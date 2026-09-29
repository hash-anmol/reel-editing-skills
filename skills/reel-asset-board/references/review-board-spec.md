# Asset review board specification

The generated HTML should work offline from the project directory.

## Page contract

- Show the project title, brief version, and a short rights warning.
- Group cards by script beat and global time range.
- Show the spoken line and intended visual mode before the media preview.
- Use `<img>`, `<video controls muted playsinline>`, and `<audio controls>` previews with dimensions constrained to the page.
- Show source, owner, retrieval date, licence note, selected range, and file path.
- Provide `approve`, `reject`, and `fallback` controls plus a notes field.
- Persist controls in `localStorage` and offer an `Export decisions JSON` button.
- Do not load remote media at review time when local copies exist.

## Decision file

Export an object keyed by relative file path:

```json
{
  "assets/example.mp4": {
    "decision": "approved",
    "notes": "Use 00:03.0–00:09.6; mute source audio"
  }
}
```

The editor must refuse to treat an unreviewed recommendation as an approval.
