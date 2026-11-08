#!/usr/bin/env python3
"""Generate the Hotel's floors: random 13th Age guests, one floor per character level.

Floor N is built for one level N character (13th Age has ten levels, so the Hotel has ten
floors). Each floor has 12 rooms, since a 13th Age character levels after three full
heal-ups of about four battles each (srd/Running-the-Game/Leveling-Up.md). Each room holds
one random monster kind from srd/Bestiary/, in a number that fits a budget for a party of
one, counted with the monster equivalents of srd/Running-the-Game/Building-Battles.md:

- the budget is one standard monster (Normal), 0.7 (Easy) or 1.5 (Hard);
- at champion tier (floors 5-7) "same level" means one level above the character, at epic
  tier (floors 8-10) two above, as the chart says;
- a mook is worth the chart's mook column, raised to 1/3 at levels 1-2 and 1/4 at 3-4
  (Building-Battles.md: Mooks); mooks come as one mob of 3 to 8;
- large and double-strength count twice, huge and triple-strength three times, elite 1.5,
  weakling 0.5;
- non-mook guests come 1 to 4 to a room, all of one kind.

Kinds are fully random on purpose. Each room also gets one piece of furniture that matters
in a fight, and the luggage's coins (a quarter of the GP per full heal-up for the level,
Leveling-Up.md: Loot, give or take half).

Usage:
  python3 13th-age/tools/gen_hotel.py --seed 7 > out.md
  python3 13th-age/tools/gen_hotel.py --seed 7 --floors 3-5
  python3 13th-age/tools/gen_hotel.py --floors 4 --seed 55 --rooms 1   # one restock group
"""
import argparse
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BESTIARY = ROOT / "srd" / "Bestiary"

ROOMS = 12
GP_PER_HEAL_UP = [None, 100, 125, 175, 210, 250, 325, 425, 500, 650, 850]

# Building-Battles.md: the monster equivalents chart, by levels above "same level".
NORMAL = {-2: 0.5, -1: 0.7, 0: 1, 1: 1.5, 2: 2, 3: 3, 4: 4}
MOOK = {-2: 0.1, -1: 0.15, 0: 0.2, 1: 0.3, 2: 0.4, 3: 0.6, 4: 0.8}
LARGE = {-2: 1, -1: 1.5, 0: 2, 1: 3, 2: 4, 3: 6, 4: 8}
HUGE = {-2: 1.5, -1: 2, 0: 3, 1: 4, 2: 6, 3: 8}

DIFFICULTY = [("Easy", 0.7, 0.30), ("Normal", 1.0, 0.45), ("Hard", 1.5, 0.25)]
TOLERANCE = 0.2  # a room's total may miss its budget by this fraction

# Baseline-Stats-for-Normal-Monsters.md: a normal monster's HP by level. A stat block with
# far more HP than its level and size suggest is a story boss (an icon's dragon), not a guest.
BASE_HP = [20, 27, 36, 45, 54, 72, 90, 108, 144, 180, 216, 288, 360, 432, 576, 720]
HP_CAP = 2.5

FEATURES = [
    "wardrobes (something can hide behind one; reaching it from the door is a move)",
    "overturned furniture (moving through the room's middle is a dicey move)",
    "a flooded bathroom (ankle-deep water; a prone creature is half under)",
    "a mezzanine bed up a ladder (far away from the door; up the ladder is a move)",
    "a hole in the floor into the room below (a dicey move next to it can drop someone)",
    "a chandelier (a ranged attack on its chain drops it on whoever is under it)",
    "the lights out (darkness: bring a light, or fight blind)",
    "a narrow hallway inside the door (only one creature can be engaged in it at a time)",
    "a bare, empty room",
    "a balcony over the street, three floors up or more",
    "a fireplace, lit (fire to grab, push into, or put out)",
    "steam from a bath (nobody can see far away; everyone is nearby or engaged)",
]


def tier(floor):
    return "adventurer" if floor <= 4 else "champion" if floor <= 7 else "epic"


def same_level(floor):
    """The monster level that counts as 'same level' for a level-`floor` character."""
    return floor + {"adventurer": 0, "champion": 1, "epic": 2}[tier(floor)]


def _field(block, key):
    m = re.search(rf'^{key}:\s*"?([^"\n]*)"?\s*$', block, re.M)
    return m.group(1).strip() if m else None


def load_monsters():
    monsters = []
    for f in sorted(BESTIARY.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.search(r"```statblock\n(.*?)```", text, re.S)
        if not m:
            continue
        b = m.group(1)
        try:
            level = int(_field(b, "level"))
            hp = int(re.sub(r"\D", "", _field(b, "hp") or "") or 0)
        except (TypeError, ValueError):
            continue
        role = (_field(b, "role") or "").lower()
        size = (_field(b, "size") or "normal").lower()
        mook = role == "mook" or (_field(b, "mook") or "").lower() == "yes"
        monsters.append({
            "name": _field(b, "name") or f.stem.replace("-", " "),
            "level": level, "role": role, "size": size, "mook": mook,
            "type": (_field(b, "type") or "").lower(),
            "ac": _field(b, "ac"), "pd": _field(b, "pd"), "md": _field(b, "md"),
            "hp": hp, "init": _field(b, "initiative"),
            "file": str(f.relative_to(ROOT.parent)),
        })
    return monsters


def worth(mon, floor):
    """What one of this monster counts as for one level-`floor` character, or None."""
    d = mon["level"] - same_level(floor)
    if mon["mook"]:
        if d not in MOOK:
            return None
        scale = 1 / 3 if floor <= 2 else 1 / 4 if floor <= 4 else 1 / 5
        return MOOK[d] * scale / 0.2
    if mon["size"] in ("large", "double-strength"):
        return LARGE.get(d)
    if mon["size"] in ("huge", "triple-strength"):
        return HUGE.get(d)
    base = NORMAL.get(d)
    if base is None:
        return None
    return base * {"elite": 1.5, "weakling": 0.5}.get(mon["size"], 1)


def is_guest(mon):
    if mon["mook"] or not 0 <= mon["level"] < len(BASE_HP):
        return True
    mult = {"large": 2, "double-strength": 2, "huge": 3, "triple-strength": 3,
            "elite": 1.5, "weakling": 0.5}.get(mon["size"], 1)
    return mon["hp"] <= HP_CAP * BASE_HP[mon["level"]] * mult


def room(rng, monsters, floor):
    names, weights = zip(*[(n, w) for n, _, w in DIFFICULTY])
    diff = rng.choices(names, weights)[0]
    budget = dict((n, b) for n, b, _ in DIFFICULTY)[diff]
    for _ in range(2000):
        mon = rng.choice(monsters)
        w = worth(mon, floor)
        if not w:
            continue
        lo, hi = (3, 8) if mon["mook"] else (1, 4)
        n = max(lo, min(hi, round(budget / w)))
        if abs(n * w - budget) <= TOLERANCE * budget:
            gp = GP_PER_HEAL_UP[floor] / 4 * rng.uniform(0.5, 1.5)
            return {"monster": mon, "count": n, "worth": n * w, "difficulty": diff,
                    "feature": rng.choice(FEATURES), "gp": int(round(gp / 5) * 5)}
    raise RuntimeError(f"no monster fits floor {floor}")


def floor_rooms(rng, monsters, floor, rooms=ROOMS):
    return [room(rng, monsters, floor) for _ in range(rooms)]


def size_word(mon):
    if mon["mook"]:
        return "mook"
    return {"double-strength": "large", "triple-strength": "huge"}.get(mon["size"], mon["size"])


def floor_md(floor, rooms):
    lines = [f"## Floor {floor} · level {floor} · {tier(floor)} tier "
             f"(same level = monster level {same_level(floor)})", "",
             "| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rooms, 1):
        m = r["monster"]
        hp = f"{m['hp']} (mob {m['hp'] * r['count']})" if m["mook"] else str(m["hp"])
        lines.append(
            f"| {floor}{i:02d} | {r['count']} × {m['name']} | {m['level']} "
            f"| {m['role']} · {size_word(m)} | {m['ac']}/{m['pd']}/{m['md']} | {hp} | +{m['init']} "
            f"| {r['worth']:.2f} | {r['difficulty']} | {r['feature']} | {r['gp']} |")
    lines.append("")
    lines.append("Files: " + " · ".join(sorted({f"`{r['monster']['file']}`" for r in rooms})))
    lines.append("")
    return "\n".join(lines)


def parse_floors(s):
    if "-" in s:
        a, b = s.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(s)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--floors", default="1-10")
    ap.add_argument("--rooms", type=int, default=ROOMS)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    monsters = [m for m in load_monsters() if is_guest(m)]
    print(f"# The Hotel · seed {a.seed}\n")
    print("Worth: what the room's guests count as for one character (1 = one standard "
          "monster, Building-Battles.md). Mooks fight as one mob sharing its HP. Fight: the "
          "room's difficulty, which is also its weight on the heal-up clock (Easy 0.7, "
          "Normal 1, Hard 1.5 battles; CLAUDE.md, House rules).\n")
    for fl in parse_floors(a.floors):
        print(floor_md(fl, floor_rooms(rng, monsters, fl, a.rooms)))


if __name__ == "__main__":
    main()
