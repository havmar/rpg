#!/usr/bin/env python3
"""Generate one breach: a pocket of intruding reality, as a dungeon for one dungeoneer and
their automaton (a party of two) at a given level.

A breach has a PRINCIPAL kind: the SRD monster whose reality intruded. It fills at least half
the breach's XP and decides what the breach does to the land above (the surface hint). The
other rooms hold STOWAWAYS: random SRD kinds that came through with it; the GM fits them to
the theme (the pirates' captive, the ship's rats, the thing they were fleeing). The deepest
room holds the RIFT, the tear itself, with the principal's largest group guarding it.

Rooms add up to at least the SRD's XP from level N to N+1 (a full SRD level: the game's
halved thresholds mean a dungeoneer needs to kill about half of it). Encounters use the 2024
budgets for TWO characters. Every encounter carries a DISPOSITION from its alignment, which
says whether it can be deported (sent home through the rift) and how.

Usage:
  python3 breach/tools/gen_breach.py --seed 4812 --level 3
  python3 breach/tools/gen_breach.py --seed 4812 --level 3 --reported 2   # scouts said level 2

month.py imports breach() and principal_for(); keep the RNG call order if you change them.
"""
import argparse
import random
import re
from pathlib import Path

SRD = Path(__file__).resolve().parents[2] / "reference" / "srd" / "Monsters"

# Level Advancement.md: SRD XP needed to reach each level (the game halves these for the
# dungeoneer; the breach is still built to the full amount).
THRESHOLD = [0, 0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
             100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]

# Combat Encounters.md: XP budget per character (Low, Moderate, High) by level.
BUDGET = [None, (50, 75, 100), (100, 150, 200), (150, 225, 400), (250, 375, 500),
          (500, 750, 1100), (600, 1000, 1400), (750, 1300, 1700), (1000, 1700, 2100),
          (1300, 2000, 2600), (1600, 2300, 3100), (1900, 2900, 4100), (2200, 3700, 4700),
          (2600, 4200, 5400), (2900, 4900, 6200), (3300, 5400, 7800), (3800, 6100, 9800),
          (4500, 7200, 11700), (5000, 8700, 14200), (5500, 10700, 17200),
          (6400, 13200, 22000)]
PARTY = 2
MAX_COUNT = 5
# Mostly cheap rooms, so a breach has rooms to search rather than two big fights.
DIFFICULTY = [("Low", 0.5), ("Moderate", 0.35), ("High", 0.15)]

SIZES = [(6, 6), (6, 8), (8, 8), (8, 10), (10, 10), (10, 12), (12, 12), (6, 12), (4, 12)]
FEATURES = [
    "pillars or masts (full cover)", "rubble or wreckage (difficult terrain, half cover)",
    "knee-deep water (difficult terrain)", "a 3 m ledge along one wall (elevation)",
    "magical darkness in half the room", "a chasm crossed by a 1.5 m-wide bridge",
    "statues or stacked cargo (half cover)", "a narrow 1.5 m entrance (chokepoint)",
    "an open, empty floor", "a high ceiling (9 m) with hanging ropes or chains",
    "open fires (bright light, fire)", "thick fog (heavily obscured beyond 3 m)",
]
FLOODED = "flooded: water 3 m deep, a 1.5 m ledge around the edge"
RIFT = "the rift: a 3 m tear in the air at the far end, humming; whatever passes it goes home"

SURFACE = {
    "Beast": "the land becomes their country: forest, marsh or grassland where there was pasture",
    "Humanoid": "their place comes with them: a ship on new water, a camp, a street of their town",
    "Undead": "a barrow or a graveyard rises; the ground is cold and the light grey",
    "Elemental": "the element itself: a pool of fire, a standing wave, a wind that never drops",
    "Fey": "a wood that wasn't there, flowers out of season, moonlight at noon",
    "Fiend": "scorched earth, sulphur on the wind, a chapel or a pit",
    "Celestial": "a light on the hill, a hush, every bird in the county gathered",
    "Dragon": "a lair: a cave mouth in a hill that had none, and the glint of a hoard",
    "Giant": "the land scaled up: furrows a cart could lie in, a hall of boulders",
    "Construct": "a workshop or a vault, all right angles, humming",
    "Monstrosity": "a lair: bones, a warren, webs between the trees",
    "Aberration": "wrong angles, a cold attention, a hole with stars in it",
    "Ooze": "a bog where the road was, every surface slick",
    "Plant": "a thicket overnight, roots through the walls",
    "Swarm": "the air or the ground alive with them",
}

CR_LINE = re.compile(r"\*\*CR\*\* (\S+) \((?:XP )?([\d,]+)")
SPEED_LINE = re.compile(r"\*\*Speed\*\* (\d+) ft\.(.*)")
TYPE_LINE = re.compile(r"^_(.+?)_\s*$", re.M)
SIZES_WORDS = ("Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan", "or")


def parse_type(line):
    """'Medium or Small Humanoid, Neutral' -> ('Humanoid', 'Neutral')."""
    head, _, align = line.rpartition(",")
    words = [w for w in head.split() if w not in SIZES_WORDS]
    typ = " ".join(words)
    base = typ.split()[0] if typ else "Monstrosity"
    if typ.startswith("Swarm"):
        base = "Swarm"
    return base, align.strip()


def disposition(base, align):
    """How the denizens take to being sent home."""
    if base in ("Swarm", "Ooze", "Plant", "Construct"):
        return "Mindless: lure it through (a fitting check, DC 15, GM's call) or destroy it"
    if align == "Unaligned":
        return "Wild: herd it through (Animal Handling DC 15) or fight"
    if "Good" in align:
        return "Peaceful: goes home when shown the rift; may help"
    if "Evil" in align:
        return "Hostile: will not go; fights"
    return "Wary: Persuasion or Intimidation DC 15 to go; refused, it bargains or fights"


def load_monsters():
    monsters = []
    for f in sorted(SRD.glob("*.md")):
        text = f.read_text()
        m = CR_LINE.search(text)
        t = TYPE_LINE.search(text)
        if not m or not t:
            continue
        xp = int(m.group(2).rstrip(",").replace(",", ""))
        if xp <= 0:
            continue
        sp = SPEED_LINE.search(text)
        aquatic = bool(sp) and int(sp.group(1)) <= 10 and "Swim" in sp.group(2)
        base, align = parse_type(t.group(1))
        monsters.append({"name": f.stem, "cr": m.group(1), "xp": xp, "aquatic": aquatic,
                         "type": base, "align": align})
    return monsters


_MONSTERS = []


def monsters():
    if not _MONSTERS:
        _MONSTERS.extend(load_monsters())
    return _MONSTERS


def budgets(level):
    return tuple(b * PARTY for b in BUDGET[level])


def fits(m, level):
    """The kind can form at least one legal encounter at this level."""
    low, _, high = budgets(level)
    return m["xp"] <= high and m["xp"] * MAX_COUNT >= low


def group(m, level, diff, rng):
    budget = budgets(level)[[d for d, _ in DIFFICULTY].index(diff)]
    count = max(1, min(MAX_COUNT, budget // m["xp"]))
    return {"diff": diff, "name": m["name"], "cr": m["cr"], "xp": m["xp"], "count": count,
            "total": m["xp"] * count, "aquatic": m["aquatic"], "type": m["type"],
            "align": m["align"], "disposition": disposition(m["type"], m["align"])}


def pick_diff(rng):
    return rng.choices([d for d, _ in DIFFICULTY], [w for _, w in DIFFICULTY])[0]


def principal_for(level, seed):
    """The principal kind alone (what the scouts report). Same RNG start as breach()."""
    rng = random.Random(seed)
    pool = [m for m in monsters() if fits(m, level)]
    return rng.choice(pool)


def breach(level, seed, reported=None):
    rng = random.Random(seed)
    pool = [m for m in monsters() if fits(m, level)]
    principal = rng.choice(pool)
    need = THRESHOLD[min(level + 1, 20)] - THRESHOLD[level] if level < 20 else 50000

    rift = group(principal, level, "High", rng)
    rooms, total = [], rift["total"]
    ptotal = rift["total"]
    while ptotal < need / 2:
        g = group(principal, level, pick_diff(rng), rng)
        rooms.append(g)
        ptotal += g["total"]
        total += g["total"]
    while total < need:
        g = group(rng.choice(pool), level, pick_diff(rng), rng)
        g["stowaway"] = True
        rooms.append(g)
        total += g["total"]
    rng.shuffle(rooms)
    rooms.append(rift)
    for i, r in enumerate(rooms, 1):
        w, h = rng.choice(SIZES)
        r["room"] = f"{w}×{h} sq ({w * 1.5:g}×{h * 1.5:g} m)"
        r["feature"] = FLOODED if r.pop("aquatic") else rng.choice(FEATURES)
        if r is rift:
            r["feature"] = RIFT
        r["gp"] = r["total"] // 10
        r["n"] = i
    return {"level": level, "reported": reported or level, "seed": seed, "need": need,
            "total": total, "principal": principal, "rooms": rooms,
            "surface": SURFACE.get(principal["type"], SURFACE["Monstrosity"])}


def breach_md(b):
    p = b["principal"]
    out = [f"## Breach (seed {b['seed']}) · level {b['level']}"
           + (f", scouts reported level {b['reported']}" if b["reported"] != b["level"] else ""),
           "",
           f"**Principal kind:** {p['name']} (CR {p['cr']}, {p['type']}, {p['align']}). "
           f"**On the surface:** {b['surface']}.",
           f"XP in the breach: {b['total']:,} (a full SRD level is {b['need']:,}; the dungeoneer "
           f"needs half) · {len(b['rooms'])} rooms, the rift last.", "",
           "| Room | Denizens | CR | XP | Difficulty | Disposition | Room size | Feature | Coins |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in b["rooms"]:
        who = f"{r['count']}× {r['name']}" + (" (stowaway)" if r.get("stowaway") else "")
        out.append(f"| {r['n']} | {who} | {r['cr']} | {r['total']:,} | {r['diff']} "
                   f"| {r['disposition']} | {r['room']} | {r['feature']} | {r['gp']:,} GP |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--reported", type=int, help="the level the scouts reported, if wrong")
    a = ap.parse_args()
    print(breach_md(breach(a.level, a.seed, a.reported)))


if __name__ == "__main__":
    main()
