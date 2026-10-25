#!/usr/bin/env python3
"""The table's secrecy check: nothing the GM keeps secret is in a document for the store.

The store is the player's screen, so the check projects the campaign afresh (game/state,
game/morten, game/realm, game/rules) and reads every document already written for it
(DIR/page/out/<collection>/<doc_id>.json, plus any --docs folder, e.g. an export), then
looks in every key and string for:

- gm-secrets.md beyond the explored mark: an unexplored room's number with its monster,
  a monster or a room feature found only in unexplored rooms, a floor's totals, and in
  game/realm.floors a room shown that isn't explored or an unknown room with a monster;
- realms.json's GM-only data: a hidden asset (one map.json doesn't show) by its id, as
  "the <owner>' <Kind>", or as its kind next to its hex; the engine's private keys (rng,
  next_id, dissident, a goal's since/against) and its rng value;
- `realms.py --gm` output ("(GM: all)", hidden-event lines).

Usage:
  python3 dnd-crunch/tools/check_table.py DIR [--docs FOLDER ...]

Exits 1 and prints each offending document and key; 0 when clean.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import realms as R  # noqa: E402
import table as T  # noqa: E402

PRIVATE_KEYS = {"rng", "next_id", "dissident", "since", "against"}
GM_MARKERS = ["(GM: all)", "hidden events too", "GM secrets ·"]


def word(s):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(s) + r"(?![a-z0-9])")


def public_text(d):
    """Text the player may know anyway: the public rules and the engine's fight lists."""
    bits = [(T.GAME / f).read_text() for f in ("CLAUDE.md", "realms.md") if (T.GAME / f).exists()]
    if (d / "rules.md").exists():
        bits.append((d / "rules.md").read_text())
    names = {m for A in R.ASSETS.values() for m in A["fight"] or []}
    names |= {m for v in R.BEASTS.values() for m in v} | set(R.SEAT_FIGHT)
    return "\n".join(bits + sorted(names))


def monster_name(enc):
    m = re.match(r"^\d+×\s*(.+)$", enc)
    return m.group(1) if m else enc


def secrets(d):
    """[(what, compiled pattern)] and the hidden asset ids."""
    pats = []
    floors = T.parse_secrets(d / "gm-secrets.md")
    seen_mon = {monster_name(r["encounter"]) for f in floors.values() for r in f["rooms"] if r["explored"]}
    seen_feat = {r["feature"] for f in floors.values() for r in f["rooms"] if r["explored"]}
    pub = public_text(d)
    hidden_mon, hidden_feat = set(), set()
    for h, f in floors.items():
        for r in f["rooms"]:
            if r["explored"]:
                continue
            mon = monster_name(r["encounter"])
            pats.append((f"unexplored room {r['n']} ({h}) with its monster",
                         re.compile(re.escape(r["n"]) + r"\b.{0,60}" + re.escape(mon.split()[-1])
                                    + "|" + re.escape(mon) + r".{0,60}(?<![\d.])" + re.escape(r["n"]) + r"\b",
                                    re.I | re.S)))
            if mon not in seen_mon and not word(mon).search(pub):
                hidden_mon.add(mon)
            if r["feature"] not in seen_feat:
                hidden_feat.add(r["feature"])
    for mon in sorted(hidden_mon):
        pats.append((f"a monster only in unexplored rooms: {mon}",
                     re.compile(r"(?<![A-Za-z])" + re.escape(mon) + r"(?:s|es)?(?![a-z])")))
    for feat in sorted(hidden_feat):
        pats.append((f"a room feature only in unexplored rooms: {feat}", re.compile(re.escape(feat))))
    pats.append(("a floor's totals from gm-secrets.md", re.compile(r"floor total:", re.I)))
    hidden_ids = set()
    st = json.loads((d / "realms.json").read_text()) if (d / "realms.json").exists() else None
    mp = json.loads((d / "map.json").read_text()) if (d / "map.json").exists() else None
    if st and mp:
        shown = {a["id"] for h in mp["hexes"] for a in h["assets"]}
        shown_kind = {(a["owner"], a["name"], h["id"]) for h in mp["hexes"] for a in h["assets"]}
        shown_ok = {(a["owner"], a["name"]) for h in mp["hexes"] for a in h["assets"]}
        for a in st["assets"].values():
            if a["id"] in shown:
                continue
            hidden_ids.add(a["id"])
            name = R.ASSETS[a["kind"]]["name"]
            pats.append((f"hidden asset {a['id']} ({a['owner']}' {name} in {a['hex']})",
                         re.compile(r"(?<![A-Za-z0-9])" + re.escape(a["id"]) + r"(?![0-9])")))
            if (a["owner"], name) not in shown_ok:
                pats.append((f"hidden asset {a['id']} by name",
                             re.compile(re.escape(R.poss(a["owner"])) + r"\s+" + re.escape(name), re.I)))
            if (a["owner"], name, a["hex"]) not in shown_kind:
                pats.append((f"hidden asset {a['id']} by kind and hex",
                             re.compile(re.escape(name) + r"\b.{0,30}\b" + re.escape(a["hex"]) + r"\b", re.I | re.S)))
        pats.append(("realms.json's rng", re.compile(r"\b" + str(st.get("rng")) + r"\b")))
    for m in GM_MARKERS:
        pats.append((f"--gm or gm-secrets output ({m})", re.compile(re.escape(m))))
    return pats, floors


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}" if path else k, k, None
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, None, obj


def check_floors(name, doc, floors):
    bad = []
    for h, f in (doc.get("floors") or {}).items():
        real = {r["n"]: r for r in floors.get(h, {}).get("rooms", [])}
        for i, r in enumerate(f.get("rooms") or []):
            src = real.get(r.get("n"))
            where = f"floors.{h}.rooms[{i}]"
            if src is None:
                bad.append((name, where, f"room {r.get('n')} is not in gm-secrets.md"))
            elif r.get("state") == "unknown":
                if any(r.get(k) for k in ("monster", "cr", "xp", "size", "feature", "note")):
                    bad.append((name, where, f"unknown room {r['n']} shows its contents"))
            elif not src["explored"]:
                bad.append((name, where, f"room {r['n']} is shown but not explored"))
    return bad


def check_doc(name, doc, pats, floors):
    bad = []
    for path, key, text in walk(doc):
        if key is not None:
            if key in PRIVATE_KEYS:
                bad.append((name, path, f"realms.json's private key '{key}'"))
            continue
        for what, p in pats:
            if p.search(text):
                bad.append((name, path, what))
    if isinstance(doc, dict) and "floors" in doc:
        bad += check_floors(name, doc, floors)
    return bad


def docs_of(d, extra):
    """[(name, doc)]: the fresh projections, page/out, and each --docs folder."""
    out = []
    c = T.Camp(d, need_page=False)
    if c.morten is not None:
        out.append(("projected game/morten", T.proj_morten(c)))
        if c.state is not None:
            out.append(("projected game/state", T.proj_state(c)))
    if c.map is not None:
        out.append(("projected game/realm", T.proj_realm(c)))
    out.append(("projected game/rules", T.proj_rules(c)))
    for folder in [d / "page" / "out"] + [Path(x) for x in extra]:
        if not folder.exists():
            continue
        for p in sorted(folder.rglob("*.json")):
            if p.name.startswith("batch"):
                continue
            out.append((str(p), json.loads(p.read_text())))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 epilog="Exit 1 with the offending document and key.")
    ap.add_argument("dir", help="the campaign folder")
    ap.add_argument("--docs", action="append", default=[], help="another folder of store documents")
    a = ap.parse_args(argv)
    d = Path(a.dir).resolve()
    try:
        pats, floors = secrets(d)
        docs = docs_of(d, a.docs)
    except T.Bad as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    bad = []
    for name, doc in docs:
        bad += check_doc(name, doc, pats, floors)
    for name, path, what in bad:
        print(f"SECRET in {name} at {path}: {what}")
    if bad:
        print(f"{len(bad)} secret(s) in the store's documents", file=sys.stderr)
        return 1
    print(f"ok: {len(docs)} documents, {len(pats)} secret patterns, nothing secret")
    return 0


if __name__ == "__main__":
    sys.exit(main())
