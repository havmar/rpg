#!/usr/bin/env python3
"""Build the table's page: join src/ into dist/table.html.

    python3 dnd-crunch/web/build.py            # write dist/table.html, print its size
    python3 dnd-crunch/web/build.py --check    # exit 1 if dist/table.html is not the current build

src/page.html holds two slot lines, `/*@CSS*/` and `/*@JS*/`, each alone on its line. The
first becomes one <style> with src/css/*.css in file-name order, the second one <script>
with src/js/*.js in file-name order. The output has no doctype, <html>, <head> or <body>:
the artifact host adds that skeleton. Python 3 standard library only.
"""

import argparse
import re
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent
SRC = WEB / "src"
DIST = WEB / "dist" / "table.html"
CSS_SLOT = "/*@CSS*/"
JS_SLOT = "/*@JS*/"
FONTS_HOST = "https://fonts.googleapis.com/"


def fail(msg):
    print(f"build.py: {msg}", file=sys.stderr)
    sys.exit(2)


def joined(folder, suffix):
    files = sorted(p for p in (SRC / folder).glob(f"*{suffix}") if p.is_file())
    if not files:
        fail(f"no {suffix} files in src/{folder}/")
    parts = []
    for p in files:
        text = p.read_text(encoding="utf-8").rstrip() + "\n"
        parts.append(f"/* ---- {folder}/{p.name} ---- */\n{text}")
    return "".join(parts), [p.name for p in files]


def build():
    page = (SRC / "page.html").read_text(encoding="utf-8")
    for slot in (CSS_SLOT, JS_SLOT):
        if page.count(slot) != 1:
            fail(f"src/page.html must hold {slot} exactly once")
    css, css_files = joined("css", ".css")
    js, js_files = joined("js", ".js")
    if re.search(r"</style", css, re.I):
        fail("a CSS file contains '</style'")
    if re.search(r"</script", js, re.I):
        fail("a JS file contains '</script' (write '<\\/script' in strings)")
    out = page.replace(CSS_SLOT, f"<style>\n{css}</style>").replace(JS_SLOT, f"<script>\n{js}</script>")
    check_contract(out)
    return out, css_files, js_files


def check_contract(out):
    head = out[:8192]
    m = re.search(r"<title>([^<]*)</title>", head)
    if not m:
        fail("no <title> in the first 8 KB")
    words = m.group(1).split()
    if not 2 <= len(words) <= 4:
        fail(f"the <title> should be two to four words, not {m.group(1)!r}")
    for tag in ("!doctype", "html", "head", "body"):
        if re.search(rf"<{tag}[\s>]", out, re.I):
            fail(f"the page must not contain <{tag}>: the artifact host adds the skeleton")
    if re.search(r"<script[^>]*\ssrc=", out, re.I):
        fail("no external scripts: everything is inline")
    for href in re.findall(r"<link[^>]*rel=\"stylesheet\"[^>]*href=\"([^\"]+)\"", out):
        if not href.startswith(FONTS_HOST):
            fail(f"stylesheets come only from Google Fonts, not {href}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if dist/table.html is stale")
    args = ap.parse_args()
    out, css_files, js_files = build()
    size = len(out.encode("utf-8"))
    if args.check:
        current = DIST.read_text(encoding="utf-8") if DIST.exists() else None
        if current != out:
            print("dist/table.html is stale: run python3 dnd-crunch/web/build.py")
            sys.exit(1)
        print(f"dist/table.html is current ({size:,} bytes)")
        return
    DIST.parent.mkdir(parents=True, exist_ok=True)
    DIST.write_text(out, encoding="utf-8")
    print(f"wrote dnd-crunch/web/dist/table.html: {size:,} bytes ({size / 1024:.1f} KB) from {len(css_files)} CSS and {len(js_files)} JS files")


if __name__ == "__main__":
    main()
