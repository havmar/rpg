#!/usr/bin/env python3
"""Generate one breach: a pocket of intruding reality that has taken over a building or a
piece of the Under, as a dungeon for one officer and their automaton (a party of two).

A breach has a PRINCIPAL kind: the SRD monster whose reality intruded. It fills at least half
the breach's XP and decides what the breach has done to the place (the street hint). The
other rooms hold STOWAWAYS: random SRD kinds that came through with it; the GM fits them to
the theme. The deepest room is the ANCHOR, where the piece is lodged and where the automaton
can set up the gizmo that sends it home, with the principal's largest group in it.

Few rooms, each a real fight: Moderate or High by the 2024 budgets for TWO characters, the
anchor always High, at least three rooms. A group is as many of its kind as fill the budget,
up to ten, so weak kinds come in numbers. Kinds are picked so that over levels 1 to 20
SRD monsters are about equally likely, with crowds the exception (see pool_for). Rooms add up to at least the SRD's XP from level N
to N+1 (the game halves the thresholds, so killing about half of a breach is a level). Every
group carries a DISPOSITION: Evil kinds are Hostile; every other group rolls a d6 (1-2
Hostile, 3-5 Neutral, 6 Willing; a mindless kind is Neutral on a 6 too).

Usage:
  python3 breach2/tools/gen_breach.py --seed 4812 --level 3
  python3 breach2/tools/gen_breach.py --seed 4812 --level 5 --reported 2   # the Reader said grade 2

day.py imports breach() and principal_for(); keep the RNG call order if you change them.
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
MAX_COUNT = 10       # weak kinds come in numbers: ten rats, not five
FILL = 0.8           # a kind fits a level if MAX_COUNT of it reach this share of Moderate
FILL_L1 = 0.65       # looser at level 1, so ten CR 0 creatures (cats, commoners) can appear
BIG_GROUP = 4        # groups larger than this are made rarer, by (BIG_GROUP / n) squared
TOP_SLACK = 1.25     # at level 20 only, one creature may run this far over High
MIN_ROOMS = 3
# Few rooms, each dangerous: no Low fights. (Name, weight, index into the budget tuple.)
DIFFICULTY = [("Moderate", 0.5, 1), ("High", 0.5, 2)]

SIZES = [(6, 6), (6, 8), (8, 8), (8, 10), (10, 10), (10, 12), (12, 12), (6, 12), (4, 12)]
FEATURES = [
    "pillars, boilers or masts (full cover)", "rubble or wreckage (difficult terrain, half cover)",
    "knee-deep water (difficult terrain)", "a 3 m ledge along one wall (elevation)",
    "magical darkness in half the room", "a chasm crossed by a 1.5 m-wide bridge",
    "machinery, statues or stacked cargo (half cover)", "a narrow 1.5 m entrance (chokepoint)",
    "an open, empty floor", "a high ceiling (9 m) with gantries, ropes or chains",
    "open fires or a live furnace (bright light, fire)",
    "thick fog or steam (heavily obscured beyond 3 m)",
    "no roof: open sky that is not the city's sky",
]
FLOODED = "flooded: water 3 m deep, a 1.5 m ledge around the edge"
ANCHOR = ("the anchor: where the piece is lodged; the air is thick and the floor hums; "
          "the gizmo is set up here and nowhere else")
HOSTILE_ON = 2       # a group that isn't Evil is Hostile anyway on a d6 roll this low
HOSTILE = "Hostile: fights; will not be talked round"
NEUTRAL = "Neutral: no quarrel yet; will not go home unless convinced (GM's discretion)"
WILLING = "Willing: wants to go home; may help"

SURFACE = {
    "Beast": "their country indoors: a tenement whose stairwells are forest, a depot gone to marsh",
    "Humanoid": "their place inside ours: a ship in a flooded cellar, a camp on a factory floor, their street behind a shop door",
    "Undead": "a crypt where the cellars were; the windows frosted from inside, the gaslight grey",
    "Elemental": "the element itself: a boiler house that is all fire, a stairwell that is a standing wave",
    "Fey": "a wood under a roof, flowers through the floorboards, moonlight in the windows at noon",
    "Fiend": "scorched brick, sulphur in the street, a chapel or a pit where the basement was",
    "Celestial": "light under every door, a hush on the block, every pigeon in the precinct on the roof",
    "Dragon": "a lair: a warehouse hollowed into a cave, the glint of a hoard through the loading doors",
    "Giant": "the building scaled up: doors three storeys tall, a hall of girders like matchwood",
    "Construct": "a workshop or a vault, all right angles, humming, cleaner than anything in the city",
    "Monstrosity": "a lair: bones in the lift shaft, a warren through the party walls, webs across the street",
    "Aberration": "wrong angles, a cold attention, a window with stars in it",
    "Ooze": "a sump where the tunnel was, every surface slick, the drains backing up for a block",
    "Plant": "a thicket overnight, roots through the brickwork, the roof pushed off",
    "Swarm": "the walls or the pipes alive with them",
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


def disposition(base, align, rng):
    """How the group takes to the pair, and to being sent home."""
    if "Evil" in align:
        return HOSTILE
    roll = rng.randint(1, 6)
    if roll <= HOSTILE_ON:
        return HOSTILE
    if roll == 6 and base not in ("Swarm", "Ooze", "Plant", "Construct"):
        return WILLING
    return NEUTRAL


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


def grade_of(level):
    """Grade N is levels 2N-1 and 2N."""
    return (level + 1) // 2


def budgets(level):
    return tuple(b * PARTY for b in BUDGET[level])


def fits(m, level):
    """The kind can make a real fight at this level: one of it is not over High, and
    MAX_COUNT of it are not far under Moderate."""
    _, mod, high = budgets(level)
    if level == 20:
        high *= TOP_SLACK
    return m["xp"] <= high and m["xp"] * MAX_COUNT >= (FILL_L1 if level == 1 else FILL) * mod


def best_count(m, level, budget):
    """As many of the kind as come nearest the budget without passing High."""
    high = budgets(level)[2]
    ok = [n for n in range(1, MAX_COUNT + 1) if n * m["xp"] <= high] or [1]
    return min(ok, key=lambda n: (abs(n * m["xp"] - budget), -n))


_WEIGHT = {}


def pool_for(level):
    """The kinds that fit this level, and their weights. Each kind has the same total
    weight over levels 1 to 20, so a kind that fits one level is as likely over a career
    as one that fits twelve. Within its levels a kind's weight leans to those where it
    comes alone or in a small group (BIG_GROUP / n beyond that), so crowds are the
    exception. This is as uniform as it gets: a third of the SRD is CR 1/2 or less, and
    making those fully equal would fill every low level with ten-strong crowds."""
    if not _WEIGHT:
        for m in monsters():
            f = {}
            for l in range(1, 21):
                if fits(m, l):
                    n = best_count(m, l, budgets(l)[1])
                    f[l] = min(1.0, BIG_GROUP / n) ** 2
            for l, v in f.items():
                _WEIGHT[m["name"], l] = v / sum(f.values())
    pool = [m for m in monsters() if fits(m, level)]
    return pool, [_WEIGHT[m["name"], level] for m in pool]


def group(m, level, diff, rng):
    """The label is what the group actually is, not what was asked for."""
    _, mod, high = budgets(level)
    count = best_count(m, level, budgets(level)[{d: i for d, _, i in DIFFICULTY}[diff]])
    total = m["xp"] * count
    diff = "High" if total > (mod + high) / 2 else "Moderate" if total >= 0.8 * mod else "Low"
    return {"diff": diff, "name": m["name"], "cr": m["cr"], "xp": m["xp"], "count": count,
            "total": m["xp"] * count, "aquatic": m["aquatic"], "type": m["type"],
            "align": m["align"]}


def pick_diff(rng):
    return rng.choices([d for d, _, _ in DIFFICULTY], [w for _, w, _ in DIFFICULTY])[0]


def principal_for(level, seed):
    """The principal kind alone (what the Reader reports). Same RNG start as breach()."""
    rng = random.Random(seed)
    pool, weights = pool_for(level)
    return rng.choices(pool, weights)[0]


def breach(level, seed, reported=None):
    rng = random.Random(seed)
    pool, weights = pool_for(level)
    principal = rng.choices(pool, weights)[0]
    need = THRESHOLD[min(level + 1, 20)] - THRESHOLD[level] if level < 20 else 50000

    anchor = group(principal, level, "High", rng)
    rooms, total = [], anchor["total"]
    ptotal = anchor["total"]
    while ptotal < need / 2:
        g = group(principal, level, pick_diff(rng), rng)
        rooms.append(g)
        ptotal += g["total"]
        total += g["total"]
    while total < need or len(rooms) + 1 < MIN_ROOMS:
        g = group(rng.choices(pool, weights)[0], level, pick_diff(rng), rng)
        g["stowaway"] = True
        rooms.append(g)
        total += g["total"]
    rng.shuffle(rooms)
    rooms.append(anchor)
    for i, r in enumerate(rooms, 1):
        w, h = rng.choice(SIZES)
        r["room"] = f"{w}×{h} sq ({w * 1.5:g}×{h * 1.5:g} m)"
        r["feature"] = FLOODED if r.pop("aquatic") else rng.choice(FEATURES)
        if r is anchor:
            r["feature"] = ANCHOR
        r["gp"] = r["total"] // 10
        r["n"] = i
    for r in rooms:  # rolled last, so a seed's rooms are what they were before dispositions
        r["disposition"] = disposition(r["type"], r["align"], rng)
    return {"level": level, "reported": reported or grade_of(level), "seed": seed, "need": need,
            "total": total, "principal": principal, "rooms": rooms,
            "surface": SURFACE.get(principal["type"], SURFACE["Monstrosity"])}


def breach_md(b):
    p = b["principal"]
    out = [f"## Breach (seed {b['seed']}) · level {b['level']} (grade {grade_of(b['level'])})"
           + (f", the Reader said grade {b['reported']}"
              if b["reported"] != grade_of(b["level"]) else ""),
           "",
           f"**Principal kind:** {p['name']} (CR {p['cr']}, {p['type']}, {p['align']}). "
           f"**From the street:** {b['surface']}.",
           f"XP in the breach: {b['total']:,} (a full SRD level is {b['need']:,}; the dungeoneer "
           f"needs half) · {len(b['rooms'])} rooms, the anchor last.", "",
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
    ap.add_argument("--reported", type=int, help="the grade the Reader reported, if wrong")
    a = ap.parse_args()
    print(breach_md(breach(a.level, a.seed, a.reported)))


if __name__ == "__main__":
    main()
