#!/usr/bin/env python3
"""Build a small offline asset-review board from a JSON manifest.

Input may be a list of records or {"assets": [...]} where each record has at
least `file`; optional beat, spoken_line, mode, role, source_url, owner,
licence, selection, technical, and decision fields are rendered as metadata.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def media_tag(path: str, role: str) -> str:
    src = esc(path)
    suffix = Path(path).suffix.lower()
    if role.lower() in {"music", "sfx", "audio"} or suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac"}:
        return f'<audio controls preload="metadata" src="{src}"></audio>'
    if suffix in {".mp4", ".mov", ".webm", ".m4v", ".avi"}:
        return f'<video controls muted playsinline preload="metadata" src="{src}"></video>'
    return f'<img loading="lazy" src="{src}" alt="{esc(Path(path).stem)}">'


def build(records: list[dict], title: str) -> str:
    cards: list[str] = []
    for item in records:
        path = str(item.get("file", ""))
        if not path:
            continue
        key = esc(path)
        decision = esc(item.get("decision", "unreviewed"))
        meta = [
            ("Beat", item.get("beat")),
            ("Mode", item.get("mode")),
            ("Role", item.get("role")),
            ("Source", item.get("source_url")),
            ("Owner", item.get("owner")),
            ("Licence", item.get("licence")),
            ("Selection", item.get("selection")),
            ("Technical", item.get("technical")),
        ]
        details = "".join(
            f'<div><b>{esc(label)}</b><span>{esc(value)}</span></div>'
            for label, value in meta
            if value
        )
        option_html = "".join(
            f'<option value="{value}" {"selected" if decision == value else ""}>{value.title()}</option>'
            for value in ("unreviewed", "approved", "rejected", "fallback")
        )
        cards.append(
            f'''<article class="card" data-file="{key}">
  <div class="preview">{media_tag(path, str(item.get("role", "")))}</div>
  <h2>{esc(item.get("beat", "Unassigned beat"))}</h2>
  <p class="line">{esc(item.get("spoken_line", ""))}</p>
  <dl>{details}</dl>
  <div class="controls">
    <label>Decision <select data-decision>
      {option_html}
    </select></label>
    <label>Notes <textarea data-notes placeholder="Review notes">{esc(item.get("notes", ""))}</textarea></label>
  </div>
</article>'''
        )

    return f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — asset review</title>
<style>
  :root {{ color-scheme: light; font: 15px/1.4 system-ui, sans-serif; color: #171513; background: #f6f3ed; }}
  body {{ max-width: 1200px; margin: 0 auto; padding: 28px; }}
  header {{ display:flex; justify-content:space-between; gap:16px; align-items:end; margin-bottom:24px; }}
  h1 {{ margin:0; font-size:28px; }} h2 {{ font-size:18px; margin:14px 0 6px; }}
  .warning {{ color:#8a2f00; max-width:620px; }}
  button {{ border:1px solid #171513; border-radius:999px; background:#fff; padding:9px 14px; cursor:pointer; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:18px; }}
  .card {{ background:#fff; border:1px solid #d8d1c7; border-radius:14px; padding:14px; }}
  .preview {{ display:grid; place-items:center; min-height:180px; background:#171513; border-radius:9px; overflow:hidden; }}
  img,video {{ max-width:100%; max-height:320px; display:block; }} audio {{ width:100%; }}
  .line {{ color:#625c54; min-height:2.8em; }} dl {{ margin:10px 0; }} dl div {{ display:grid; grid-template-columns:82px 1fr; gap:8px; margin:4px 0; }}
  dl span {{ overflow-wrap:anywhere; }} .controls {{ display:grid; gap:9px; }}
  label {{ display:grid; gap:4px; font-weight:600; }} select,textarea {{ font:inherit; border:1px solid #bdb4aa; border-radius:7px; padding:7px; }} textarea {{ min-height:50px; resize:vertical; font-weight:400; }}
</style>
<body><header><div><h1>{esc(title)}</h1><p class="warning">Review rights before publication. Download success is not a licence grant.</p></div><button id="export">Export decisions JSON</button></header>
<main class="grid">{"".join(cards)}</main>
<script>
const key = 'reel-asset-board:{esc(title)}';
const saved = JSON.parse(localStorage.getItem(key) || '{{}}');
document.querySelectorAll('[data-file]').forEach(card => {{
  const file = card.dataset.file, state = saved[file] || {{}};
  const decision = card.querySelector('[data-decision]'), notes = card.querySelector('[data-notes]');
  if (state.decision) decision.value = state.decision; if (state.notes) notes.value = state.notes;
  const save = () => {{ saved[file] = {{decision: decision.value, notes: notes.value}}; localStorage.setItem(key, JSON.stringify(saved)); }};
  decision.addEventListener('change', save); notes.addEventListener('input', save);
}});
document.querySelector('#export').addEventListener('click', () => {{
  const blob = new Blob([JSON.stringify(saved, null, 2)], {{type:'application/json'}}), a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'asset-decisions.json'; a.click(); URL.revokeObjectURL(a.href);
}});
</script></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default="Instagram Reel Asset Board")
    args = parser.parse_args()
    raw = json.loads(args.manifest.read_text())
    records = raw.get("assets", raw) if isinstance(raw, dict) else raw
    if not isinstance(records, list):
        raise SystemExit("manifest must be a list or an object with an assets list")
    args.output.write_text(build(records, args.title))


if __name__ == "__main__":
    main()
