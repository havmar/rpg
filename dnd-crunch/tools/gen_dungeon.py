#!/usr/bin/env python3
"""Generate a demo dungeon: one floor per character level, random SRD monsters.

Floor N is built for a level N character on their own. Its encounters add up to at least
the XP needed to go from level N to N+1 (floor 20 uses the 19 → 20 amount). Each encounter
is one random monster type from reference/srd/Monsters/, in a number (1–4) that fits a
Low, Moderate or High budget from the 2024 encounter table (one character). Themes are
fully random on purpose: the point is to see what each monster can do.

realms.py imports encounter(), floor() and floor_md() from here, so keep their RNG call order.

Usage:
  python3 dnd-crunch/tools/gen_dungeon.py --seed 7 > out.md
  python3 dnd-crunch/tools/gen_dungeon.py --seed 7 --floors 3-5
"""
import argparse
import random
import re
from pathlib import Path

SRD = Path(__file__).resolve().parents[2] / "reference" / "srd" / "Monsters"

# Level Advancement.md: XP needed to reach each level.
THRESHOLD = [0, 0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
             100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]

# Combat Encounters.md: XP budget per character, (Low, Moderate, High), by level.
BUDGET = [None, (50, 75, 100), (100, 150, 200), (150, 225, 400), (250, 375, 500),
          (500, 750, 1100), (600, 1000, 1400), (750, 1300, 1700), (1000, 1700, 2100),
          (1300, 2000, 2600), (1600, 2300, 3100), (1900, 2900, 4100), (2200, 3700, 4700),
          (2600, 4200, 5400), (2900, 4900, 6200), (3300, 5400, 7800), (3800, 6100, 9800),
          (4500, 7200, 11700), (5000, 8700, 14200), (5500, 10700, 17200),
          (6400, 13200, 22000)]

DIFFICULTY = [("Low", 0.3), ("Moderate", 0.45), ("High", 0.25)]
MAX_COUNT = 4

SIZES = [(6, 6), (6, 8), (8, 8), (8, 10), (10, 10), (10, 12), (12, 12), (6, 12), (4, 12)]
FEATURES = [
    "pillars (full cover)", "rubble (difficult terrain, half cover)",
    "knee-deep water (difficult terrain)", "a 3 m ledge along one wall (elevation)",
    "magical darkness in half the room", "a chasm crossed by a 1.5 m-wide bridge",
    "statues (half cover)", "a narrow 1.5 m entrance (chokepoint)", "an open, empty floor",
    "a high ceiling (9 m) with hanging chains", "burning braziers (bright light, fire)",
    "thick fog (heavily obscured beyond 3 m)",
]

CR_LINE = re.compile(r"\*\*CR\*\* (\S+) \((?:XP )?([\d,]+)")
SPEED_LINE = re.compile(r"\*\*Speed\*\* (\d+) ft\.(.*)")
FLOODED = "flooded: water 3 m deep, a 1.5 m ledge around the edge"


def load_monsters():
    monsters = []
    for f in sorted(SRD.glob("*.md")):
        text = f.read_text()
        m = CR_LINE.search(text)
        if not m:
            continue
        xp = int(m.group(2).rstrip(",").replace(",", ""))
        # Swimmers that barely walk get a flooded room instead of a random feature.
        sp = SPEED_LINE.search(text)
        aquatic = bool(sp) and int(sp.group(1)) <= 10 and "Swim" in sp.group(2)
        if xp > 0:
            monsters.append((f.stem, m.group(1), xp, aquatic))
    return monsters


_MONSTERS = []


def encounter(level, rng, monsters=None):
    """One random encounter for a level-N character: rolls difficulty, then monster."""
    if monsters is None:
        if not _MONSTERS:
            _MONSTERS.extend(load_monsters())
        monsters = _MONSTERS
    diff = rng.choices([d for d, _ in DIFFICULTY], [w for _, w in DIFFICULTY])[0]
    budget = BUDGET[level][[d for d, _ in DIFFICULTY].index(diff)]
    pool = [m for m in monsters if m[2] <= budget and m[2] * MAX_COUNT >= budget]
    name, cr, xp, aquatic = rng.choice(pool)
    count = min(MAX_COUNT, budget // xp)
    return {"diff": diff, "name": name, "cr": cr, "xp": xp, "count": count,
            "total": xp * count, "aquatic": aquatic}


def floor(level, monsters, rng):
    need = THRESHOLD[min(level + 1, 20)] - THRESHOLD[level] if level < 20 else 50000
    encounters, total = [], 0
    while total < need:
        e = encounter(level, rng, monsters)
        w, h = rng.choice(SIZES)
        e["room"] = f"{w}×{h} sq ({w * 1.5:g}×{h * 1.5:g} m)"
        e["feature"] = FLOODED if e.pop("aquatic") else rng.choice(FEATURES)
        e["gp"] = e["total"] // 10
        encounters.append(e)
        total += e["total"]
    return need, total, encounters


def floor_md(level, need, total, encs, title=None):
    """A floor as Markdown: heading, totals line, room table, trailing blank line."""
    goal = f"XP needed for level {level + 1}" if level < 20 else "Final floor, XP target"
    out = [f"## {title or f'Floor {level} (for level {level})'}\n",
           f"{goal}: {need:,} · floor total: {total:,} · {len(encs)} encounters\n",
           "| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |",
           "|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(encs, 1):
        out.append(f"| {level}.{i} | {e['count']}× {e['name']} | {e['cr']} | {e['total']:,} "
                   f"| {e['diff']} | {e['room']} | {e['feature']} | {e['gp']:,} GP |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--floors", default="1-20", help="e.g. 1-20 or 3-5")
    a = ap.parse_args()
    lo, _, hi = a.floors.partition("-")
    lo, hi = int(lo), int(hi or lo)

    rng = random.Random(a.seed)
    monsters = load_monsters()
    for level in range(1, 21):
        need, total, encs = floor(level, monsters, rng)  # always roll every floor
        if not lo <= level <= hi:
            continue
        print(floor_md(level, need, total, encs))


if __name__ == "__main__":
    main()
