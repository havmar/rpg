#!/usr/bin/env python3
"""Roll the opponents for a scene, so the GM never picks them. Every roll is printed.

Usage (from the repo root):
  python3 eclipse-phase/tools/threat.py PLACE           # PLACE: civilised, fringe, ruins, exoplanet, mesh
  python3 eclipse-phase/tools/threat.py PLACE --seed N  # repeatable
  python3 eclipse-phase/tools/threat.py list            # print the catalogue

Reads the table in eclipse-phase/threats.md. On 1d4:
  2-4  native: one entry, evenly, from those whose Places include PLACE
  1    out of place: a Kind evenly, then an entry of that Kind evenly, from the whole table;
       the story has to explain why it is here
Colour "rolled" (house entries): 1d6, 1-3 yellow, 4-5 orange, 6 red.
Number: a book range is rolled and halved, rounded up (the book assumes four PCs, we are
two), and red or ultraviolet is always 1; "rolled" is yellow 2d3, orange 1d2, red 1.
"""
import os
import random
import re
import sys

PLACES = ["civilised", "fringe", "ruins", "exoplanet", "mesh"]
TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "threats.md")


def load():
    rows = []
    for line in open(TABLE, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 8 and cells[0].isdigit():
            n, name, kind, colour, number, places, stats, what = cells
            rows.append({"n": int(n), "name": name, "kind": kind, "colour": colour,
                         "number": number, "places": [p.strip() for p in places.split(",")],
                         "stats": stats, "what": what})
    return rows


def d(sides, label):
    r = random.randint(1, sides)
    print(f"  1d{sides} {label}: {r}")
    return r


def main(argv):
    if "--seed" in argv:
        i = argv.index("--seed")
        random.seed(int(argv[i + 1]))
        argv = argv[:i] + argv[i + 2:]
    rows = load()
    if argv == ["list"]:
        for r in rows:
            print(f"{r['n']:>2} {r['name']:<27} {r['kind']:<9} {r['colour']:<11} {', '.join(r['places'])}")
        return
    if len(argv) != 1 or argv[0] not in PLACES:
        sys.exit(__doc__)
    place = argv[0]

    print(f"Opponents in a {place} place")
    if d(4, "native (2-4) or out of place (1)") == 1:
        kinds = sorted({r["kind"] for r in rows})
        kind = kinds[d(len(kinds), "kind, of " + ", ".join(kinds)) - 1]
        pool = [r for r in rows if r["kind"] == kind]
        origin = "OUT OF PLACE: explain why it is here"
    else:
        pool = [r for r in rows if place in r["places"]]
        origin = "native"
    t = pool[d(len(pool), f"entry, of {len(pool)}") - 1]

    colour = t["colour"]
    if colour == "rolled":
        c = d(6, "colour (1-3 yellow, 4-5 orange, 6 red)")
        colour = "yellow" if c <= 3 else "orange" if c <= 5 else "red"

    num = t["number"]
    if num == "rolled":
        if colour == "yellow":
            count = d(3, "number") + d(3, "number")
        elif colour == "orange":
            count = d(2, "number")
        else:
            count = 1
    else:
        m = re.match(r"^(\d+)(?:-(\d+))?$", num)
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
        raw = random.randint(lo, hi)
        count = max(1, -(-raw // 2))
        if colour in ("red", "ultraviolet"):
            count = 1
        print(f"  book number {num}: {raw}, halved for two PCs: {count}"
              + (" (red and ultraviolet: always 1)" if colour in ("red", "ultraviolet") else ""))

    stats = ("house: build from rulebook/18/05-npc-and-threat-rules.md (Threat Level)"
             if t["stats"] == "house" else "rulebook/" + t["stats"])
    print(f"=> {count} x {t['name']} ({t['kind']}, {colour}), {origin}")
    print(f"   {t['what']}")
    print(f"   stats: {stats}")


if __name__ == "__main__":
    main(sys.argv[1:])
