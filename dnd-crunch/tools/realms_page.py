#!/usr/bin/env python3
"""Build the Realms map page for a campaign.

    python3 dnd-crunch/tools/realms_page.py <campaign dir> [--out FILE]

Reads <campaign dir>/map.json (written by realms.py after every domain turn) and writes
<campaign dir>/page.html (or FILE): dnd-crunch/ui/realms-map.html with the JSON inlined
in its one placeholder. The page is then published (or republished to the same URL) as a
claude.ai artifact; see dnd-crunch/ui/README.md. Stdlib only.
"""
import argparse
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "ui" / "realms-map.html"
PLACEHOLDER = "__MAP_JSON__"


def inline_json(data) -> str:
    """JSON safe inside a <script> element: no '<', '>' or '&' outside escapes.

    Those characters can only occur inside JSON strings, where \\u escapes mean the same,
    so '</script>' or '<!--' in a name or a report line can't end the element early.
    """
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return (text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def build(campaign: Path, out: Path | None = None, template: Path = TEMPLATE) -> Path:
    src = campaign / "map.json"
    if not src.is_file():
        sys.exit(f"no map.json in {campaign} (realms.py writes it after `new` and every turn)")
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{src} is not valid JSON: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("hexes"), list):
        sys.exit(f"{src} has no 'hexes' list; is it the map.json the page reads?")
    page = template.read_text(encoding="utf-8")
    if page.count(PLACEHOLDER) != 1:
        sys.exit(f"{template} must hold the placeholder {PLACEHOLDER} exactly once")
    out = out or campaign / "page.html"
    out.write_text(page.replace(PLACEHOLDER, inline_json(data)), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the Realms map page from a campaign's map.json.")
    ap.add_argument("campaign", type=Path, help="the campaign folder, e.g. dnd-crunch/campaigns/realms2")
    ap.add_argument("--out", type=Path, help="where to write the page (default: <campaign>/page.html)")
    args = ap.parse_args()
    out = build(args.campaign, args.out)
    print(f"wrote {out} (month {json.loads((args.campaign / 'map.json').read_text(encoding='utf-8')).get('month', '?')})")


if __name__ == "__main__":
    main()
