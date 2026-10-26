#!/usr/bin/env python3
"""Realms v3: the overworld engine for D&D Crunch (rules: dnd-crunch/realms-v3.md).

A 4×5 hex map of six static realms and Morten's tower. Each realm has one goal with a
clock and rolls one d6 a month for it; a full clock changes the map. Morten's missions
move the clocks directly, his standing with each realm says how it treats the tower, and
his Renown climbs a ladder of five tiers. realms.json is the state and this script owns
it; world.md and map.json (the map page's data) are written from it after every change.
Nothing is hidden from the tower but the dungeon floors. Realms v1 and v2 worlds are
refused: play them with realms_v1.py and realms.py.

Usage:
  python3 dnd-crunch/tools/realms3.py new --seed 7 --campaign DIR [--level 3] [--force]
  python3 dnd-crunch/tools/realms3.py show --campaign DIR [--at C3]
  python3 dnd-crunch/tools/realms3.py encounter --campaign DIR (--site s7 | --aid REALM
      | --contact REALM | --hex C3 [--seed N]) [--level N]
  python3 dnd-crunch/tools/realms3.py turn --campaign DIR [--at HEX] [--level N]
      [--strike s7 | --rob s8 | --aid REALM | --contact REALM | --delve]
      [--goal take:HEX|ally:REALM|topple:REALM|drop]
      [--buy garrison@HEX|walls@HEX|works@HEX|mend]... [--give REALM=GP]...
      [--back REALM | --hinder REALM] [--set REALM=GOAL] [--deposit GP] [--withdraw GP]
      [--plan "why"]... [--dry-run]
  python3 dnd-crunch/tools/realms3.py sim [--seeds 1-10] [--months 24] [--scripted]
      [--seed N --verbose]
"""
import argparse
import json
import random
import re
import sys
from collections import Counter, deque
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ noise in the repo
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_dungeon import BUDGET, SRD, encounter, floor, floor_md, load_monsters  # noqa: E402

VERSION = 3

# ---- Constants (realms-v3.md, the constants table). Change both together. ----
COLS, ROWS = "ABCD", 5
N_REALMS, REALM_SIZE, N_BAD = 6, 3, 4
N_RIVERS, RIVER_LEN, N_LAKES = 2, (3, 6), 2
INCOME = 10              # GP per hex level a month
TYRANT_INCOME = 1.5      # a Tyrant's hex income multiplier
WORKS_INCOME = 50        # a works site's income
START_DIV, START_GP = 10, 10   # Force S ÷ 10 (rounded, min 1, max 5); treasury S × 10
MAX_FORCE = 5
CLOCK = {"take": 4, "fortify": 3, "raise": 3, "raid": 2, "press": 3, "squeeze": 2,
         "break": 4, "break_tower": 4, "court": 2}
WALLED_TAKE = 6          # a take against a walled hex
TOWER_CLOCK = {"take": 2, "ally": 3, "topple": 3}   # take and topple add the realm's Force
WALLED_TOWER_TAKE = 2    # more on the tower's take against a walled hex
PRICE = {"fortify": 300, "raise": 200, "garrison": 400, "walls": 600, "works": 300,
         "mend": 200, "back": 100}       # raise: × the new Force
RAID_GP = 100            # a Raid takes this × the raider's Force; from the tower at most half
ROB_GP = 100             # a Rob takes this × the realm's Force
SQUEEZE_GP, SQUEEZE_MONTHS, SQUEEZE_DC = 100, 3, 4
CONTACT_DC, CONTACT_BAD, CONTACT_STANDING = 12, 3, 2
GIVE_MIN = 200           # a Give of this much in a month: +1 on the roll, standing +1, a mark
MARKS, MARKS_POWER = 2, 3   # what a Strike or an Aid moves (3 at Power)
HOLD = 3
TOWER_START_GP = 100
TIERS = [(0, "Hermit"), (2, "Lord of the hex"), (5, "Warden of the marches"),
         (9, "A power in the land"), (14, "Master of the twenty hexes")]
LORD, WARDEN, POWER, MASTER = 1, 2, 3, 4
GOAL_MONTHS = 12         # a goal not done in this many months is dropped (the plan said 6;
                         # a take at −1 or −2 needs 8–12 months, so 6 just restarted the same goal)
MENACE = 7               # a bad neighbour of the tower at standing 0 or less weighs break the
                         # tower on a d6 of this or more at any tier (7: never; the sim's knob)
RICH = 0                 # a realm with this much gold raises or fortifies before its tag's goal
                         # (0: never; the sim's knob)
CONQ_OPEN = True         # a Conqueror prefers border hexes with no garrison or walls (tuned: hexes
                         # change hands 1.9 a world instead of 0.9)
FIGHT_MAX = 4            # most monsters in a mission fight
STANDING_WORD = {-2: "enemy", -1: "wary", 0: "neutral", 1: "friendly", 2: "ally"}

# ---- Sites (section 6). Fight: SRD monsters, picked to the tier's budget. ----
SEAT_FIGHT = ["Noble", "Spy", "Tough", "Guard", "Knight", "Guard Captain"]
GARRISON_FIGHT = {1: ["Guard", "Scout", "Guard Captain"],
                  2: ["Knight", "Warrior Veteran", "Warhorse"],
                  3: ["Berserker", "Warrior Veteran", "Gladiator", "Ogre"]}
WORKS_FIGHT = {"Farms": ["Guard", "Mastiff", "Scout"],
               "Mine": ["Tough", "Guard", "Tough Boss"],
               "Caravans": ["Guard", "Scout", "Warrior Veteran", "Mastiff"]}
WALLS_FIGHT = ["Animated Armor", "Guard", "Gargoyle"]
WORKS_BIOME = {"hills": "Mine", "mountains": "Mine", "plains": "Caravans", "savanna": "Caravans"}
SITE_NAME = {"seat": "Seat", "garrison": "Garrison", "walls": "Walls"}
BEASTS = {"Humans": ["Mastiff", "Warhorse", "Scout"],
          "Elves": ["Giant Owl", "Giant Eagle", "Giant Elk"],
          "Orcs": ["Worg", "Dire Wolf", "Giant Boar"],
          "Gnomes": ["Giant Badger", "Giant Goat", "Brown Bear"],
          "Tieflings": ["Imp", "Hell Hound"],
          "Goblinkind": ["Giant Hyena", "Worg", "Gnoll Warrior"],
          "tower folk": ["Mastiff", "Giant Owl", "Brown Bear"]}

BIOMES = {1: ["tundra", "taiga", "mountains"],
          2: ["taiga", "hills", "mountains", "forest"],
          3: ["forest", "plains", "hills", "swamp"],
          4: ["plains", "forest", "swamp", "hills", "savanna"],
          5: ["desert", "savanna", "jungle", "mountains"]}
BAD = ["Conqueror", "Raider", "Slaver", "Tyrant"]
GOOD = ["Steward", "Liberator"]
VERB = {"Conqueror": "takes land", "Raider": "robs its neighbours",
        "Slaver": "takes people for soldiers", "Tyrant": "squeezes its own people",
        "Steward": "keeps the peace", "Liberator": "fights tyrants"}
PEOPLES = {  # titles, names (names are unique across the lists)
    "Humans": (["Lord", "Marshal", "Reeve"],
               ["Aldric", "Bertrand", "Cassia", "Doran", "Edda", "Fenwick", "Galen", "Hilde",
                "Isolde", "Jorund", "Katrin", "Leopold", "Mirela", "Osric"]),
    "Elves": (["Speaker", "Archon", "Warden"],
              ["Aelar", "Caelynn", "Erevan", "Faelar", "Ilyana", "Mirethil", "Naivara",
               "Quelenna", "Sariel", "Thamior", "Valanthe", "Ynnara", "Zelphar", "Eilistra"]),
    "Orcs": (["Warlord", "Chief", "Boss"],
             ["Grukk", "Shaya", "Mogra", "Thokk", "Urzul", "Brakka", "Durgash", "Kragga",
              "Nazha", "Ruuk", "Vorga", "Yashna", "Hruma", "Ozgar"]),
    "Gnomes": (["Mayor", "Provost", "Tinker-General"],
               ["Bimble", "Dabbin", "Fizwick", "Nissa", "Orryn", "Quillon", "Roondar", "Tana",
                "Wrenna", "Zook", "Ellywick", "Pockle", "Sindri", "Tobble"]),
    "Tieflings": (["Hierarch", "Magister", "Exarch"],
                  ["Akmenos", "Bryseis", "Damaia", "Ekemon", "Kallista", "Leucis", "Mordai",
                   "Nemeia", "Orianna", "Skamos", "Therai", "Vexa", "Iados", "Rieta"]),
    "Goblinkind": (["Big Boss", "Warchief", "Overlord"],
                   ["Snik", "Krell", "Yark", "Muzgash", "Skreek", "Drubb", "Nagra", "Vizzik",
                    "Hrothak", "Gnasha", "Turk", "Blix", "Zarga", "Kobb"]),
}
TOWER, TOWER_FOLK = "tower", "tower folk"


class Bad(Exception):
    """A bad input: one-line error, no state change."""


def check_fights():
    """Every fight monster must be an SRD file."""
    names = set(SEAT_FIGHT) | set(WALLS_FIGHT)
    for v in list(GARRISON_FIGHT.values()) + list(WORKS_FIGHT.values()) + list(BEASTS.values()):
        names |= set(v)
    missing = sorted(n for n in names if not (SRD / f"{n}.md").exists())
    if missing:
        raise SystemExit(f"error: no SRD monster file for {', '.join(missing)}")


# ---- Dice ----

DICE = re.compile(r"^(\d+)d(\d+)([+-]\d+)?$")


def roll(rng, spec):
    """(total, 'spec a+b+mod = total'), at least 0."""
    n, s, m = DICE.match(spec).groups()
    faces = [rng.randint(1, int(s)) for _ in range(int(n))]
    tot = max(0, sum(faces) + int(m or 0))
    return tot, f"{spec} {'+'.join(map(str, faces))}{m or ''} = {tot}"


# ---- Map (as v2) ----

def hkey(h):
    return COLS.index(h[0]), int(h[1:])


HEXES = [f"{c}{r}" for c in COLS for r in range(1, ROWS + 1)]


def nbrs(h):
    c, r = hkey(h)
    out = [(c, r - 1), (c, r + 1)]
    rows = (r - 1, r) if c % 2 == 0 else (r, r + 1)
    out += [(c + d, rr) for d in (-1, 1) for rr in rows]
    return sorted((f"{COLS[cc]}{rr}" for cc, rr in out
                   if 0 <= cc < len(COLS) and 1 <= rr <= ROWS), key=hkey)


def edge(a, b):
    return "|".join(sorted((a, b), key=hkey))


EDGES = sorted({edge(h, n) for h in HEXES for n in nbrs(h)})


def dist(a, b):
    """Hex steps from a to b."""
    seen, q = {a: 0}, deque([a])
    while q:
        h = q.popleft()
        if h == b:
            return seen[h]
        for n in nbrs(h):
            if n not in seen:
                seen[n] = seen[h] + 1
                q.append(n)
    return 99


def verts(e):
    a, b = e.split("|")
    common = sorted(set(nbrs(a)) & set(nbrs(b)), key=hkey)
    return [frozenset((a, b, c)) for c in common] + [("out", e, i) for i in range(2 - len(common))]


def other(e, v):
    return next(x for x in verts(e) if x != v)


def rim(v):
    return isinstance(v, tuple)


def vedges(v):
    a, b, c = sorted(v)
    return [edge(a, b), edge(a, c), edge(b, c)]


def river_walk(rng, used, lake):
    if lake:
        e = rng.choice([edge(lake, n) for n in nbrs(lake)])
        start = rng.choice(verts(e))
    else:
        e = rng.choice([x for x in EDGES if any(rim(v) for v in verts(x))])
        start = next(v for v in verts(e) if rim(v))
    if e in used:
        return None
    path, seen, v = [e], {start}, other(e, start)
    while not rim(v) and len(path) < RIVER_LEN[1]:
        seen.add(v)
        opts = [x for x in vedges(v) if x not in path and x not in used and other(x, v) not in seen]
        if not opts:
            return None
        e = rng.choice(opts)
        path.append(e)
        v = other(e, v)
    return path if rim(v) and len(path) >= RIVER_LEN[0] else None


def carve(rng, free, level):
    """6 contiguous 3-hex realms over free hexes, leftovers to the poorest adjacent realm."""
    for _ in range(10000):
        left, realms = set(free), []
        while len(realms) < N_REALMS and left:
            r = [rng.choice(sorted(left, key=hkey))]
            left.discard(r[0])
            while len(r) < REALM_SIZE:
                opts = sorted({n for h in r for n in nbrs(h)} & left, key=hkey)
                if not opts:
                    break
                r.append(rng.choice(opts))
                left.discard(r[-1])
            if len(r) < REALM_SIZE:
                break
            realms.append(r)
        if len(realms) < N_REALMS:
            continue
        ok = True
        for h in sorted(left, key=hkey):
            adj = [r for r in realms if set(nbrs(h)) & set(r)]
            if not adj:
                ok = False
                break
            low = min(sum(level[x] for x in r) for r in adj)
            rng.choice([r for r in adj if sum(level[x] for x in r) == low]).append(h)
        if ok:
            return realms
    raise SystemExit("error: could not carve realms")


# ---- State helpers ----

def people_of(name):
    return TOWER_FOLK if name == TOWER else name


def hexes_of(st, name):
    return [h for h in HEXES if st["hexes"][h]["holder"] == name]


def deepest(st, hs):
    return sorted(hs, key=lambda h: (-st["hexes"][h]["level"], hkey(h)))


def sites_of(st, owner=None, hex=None, kind=None):
    return [s for s in sorted(st["sites"].values(), key=lambda s: int(s["id"][1:]))
            if (owner is None or s["owner"] == owner) and (hex is None or s["hex"] == hex)
            and (kind is None or s["kind"] == kind)]


def site_at(st, h, kind, owner=None):
    for s in sites_of(st, owner, h, kind):
        return s
    return None


def walled(st, h):
    return site_at(st, h, "walls") is not None


def poss(name):
    return "the tower's" if name == TOWER else f"the {name}'"  if name.endswith("s") else f"the {name}'s"


def the(name):
    return "the tower" if name == TOWER else f"the {name}"


def cap(s):
    return s[:1].upper() + s[1:]


def label(f):
    L = f["leader"]
    return f"{L['label']}: {VERB[L['tag']]}"


def who(f):
    return f"{the(f['name'])} ({label(f)})"


def tier_of(force):
    return 1 if force <= 2 else 2 if force <= 4 else 3


def realm_tier(st, name):
    return 1 if name == TOWER else tier_of(st["realms"][name]["force"])


def site_tier(st, s):
    t = realm_tier(st, s["owner"])
    if s["kind"] == "seat":
        return min(3, t + 1)
    if s["kind"] == "works":
        return max(1, t - 1)
    return t


def site_fight(st, s):
    if s["kind"] == "seat":
        return SEAT_FIGHT
    if s["kind"] == "garrison":
        return GARRISON_FIGHT[site_tier(st, s)]
    if s["kind"] == "works":
        return WORKS_FIGHT[s["name"]]
    return WALLS_FIGHT


def sname(st, s):
    return f"{poss(s['owner'])} {s['name']} {s['id']}"


def is_ally(f):
    return f["standing"] >= 2


def standing_word(n):
    return STANDING_WORD[n]


def hex_income(st, h):
    x = st["hexes"][h]
    f = st["realms"].get(x["holder"])
    mult = TYRANT_INCOME if f and f["leader"]["tag"] == "Tyrant" else 1
    return int(x["level"] * INCOME * mult)


def income_of(st, name):
    hx = sum(hex_income(st, h) for h in hexes_of(st, name))
    return hx + WORKS_INCOME * len(sites_of(st, name, kind="works"))


def renown_of(st):
    allies = sum(1 for f in st["realms"].values() if is_ally(f))
    return max(0, len(hexes_of(st, TOWER)) - 1) + allies + 2 * st["tower"]["toppled"]


def tier_for(renown):
    return max(i for i, (need, _) in enumerate(TIERS) if renown >= need)


def tier_now(st):
    return tier_for(renown_of(st))


def tier_name(t):
    return TIERS[t][1]


def mark_step(st):
    return MARKS_POWER if tier_now(st) >= POWER else MARKS


def neighbours_of(st, name):
    """Realms (and the tower) holding a hex next to one of name's."""
    out = set()
    for h in hexes_of(st, name):
        for n in nbrs(h):
            hold = st["hexes"][n]["holder"]
            if hold != name:
                out.add(hold)
    return sorted(out, key=lambda n: (n == TOWER, n))


def aim_hex(st, name):
    """The hex a realm's goal is aimed at (its seat for goals with no hex)."""
    f = st["realms"][name]
    g = f["goal"]
    if not g:
        return f["seat"]
    if g["hex"]:
        return g["hex"]
    if g["target"] == TOWER:
        return st["warded"]
    if g["target"]:
        return st["realms"][g["target"]]["seat"]
    return f["seat"]


def goal_text(st, g, owner=None):
    if not g:
        return None
    k, t, h = g["kind"], g["target"], g["hex"]
    if k == "take":
        return f"take {h} from {the(t)}"
    if k == "fortify":
        return f"fortify {h}"
    if k == "raise":
        return "raise"
    if k in ("raid", "press", "break"):
        return f"{k} {the(t)}"
    if k == "squeeze":
        return "squeeze"
    if k == "break_tower":
        return "break the tower"
    if k == "court":
        return "court the tower"
    if k == "ally":
        return f"ally {the(t)}"
    if k == "topple":
        return f"topple {the(t)}"
    return k


def clock_text(g):
    s = f"{g['marks']} of {g['size']}"
    if g.get("waits"):
        s += f", done, waits for {g['waits']:,} GP"
    return s


def contact_dc(st, name):
    f = st["realms"][name]
    dc = CONTACT_DC + (CONTACT_BAD if f["leader"]["label"] == "bad" else 0) \
        - CONTACT_STANDING * f["standing"]
    if f["squeeze_until"] and st["month"] <= f["squeeze_until"]:
        dc += SQUEEZE_DC
    return dc


def sync(st):
    """The derived lists: each holder's hexes and sites, the tower's Renown and tier."""
    for n, f in st["realms"].items():
        f["hexes"] = hexes_of(st, n)
    T = st["tower"]
    T["hexes"] = hexes_of(st, TOWER)
    T["sites"] = [s["id"] for s in sites_of(st, TOWER)]
    T["renown"] = renown_of(st)
    T["tier"] = tier_for(T["renown"])
    for h, x in st["hexes"].items():
        x["sites"] = [s["id"] for s in sites_of(st, hex=h)]


# ---- World generation ----

def name_for(st, people, rng):
    used = set(st["names"])
    free = [n for n in PEOPLES[people][1] if n not in used]
    if free:
        n = rng.choice(free)
    else:
        base, k = rng.choice(PEOPLES[people][1]), 2
        while f"{base} {k}" in used:
            k += 1
        n = f"{base} {k}"
    st["names"].append(n)
    return n


def new_leader(st, people, rng, label_):
    tag = rng.choice(BAD if label_ == "bad" else GOOD)
    return {"name": name_for(st, people, rng), "title": rng.choice(PEOPLES[people][0]),
            "label": label_, "tag": tag}


def add_site(st, owner, kind, hex):
    i = st["next_id"]
    st["next_id"] += 1
    name = SITE_NAME.get(kind) or WORKS_BIOME.get(st["hexes"][hex]["biome"], "Farms")
    s = {"id": f"s{i}", "owner": owner, "kind": kind, "hex": hex, "name": name}
    st["sites"][s["id"]] = s
    return s


def generate(seed, level=3):
    rng = random.Random(seed)
    levels = list(range(1, len(HEXES) + 1))
    rng.shuffle(levels)
    lv = dict(zip(HEXES, levels))
    tower = next(h for h in HEXES if lv[h] == 1)
    realms = carve(rng, [h for h in HEXES if h != tower], lv)
    peoples = list(PEOPLES)
    rng.shuffle(peoples)
    st = {"version": VERSION, "seed": seed, "month": 1, "rng": 0, "warded": tower,
          "hexes": {}, "rivers": [], "sites": {}, "next_id": 1, "realms": {},
          "tower": {"treasury": TOWER_START_GP, "hold": HOLD, "goal": None, "toppled": 0,
                    "won": None},
          "morten": {"hex": tower, "level": level}, "names": ["Morten"],
          "events": [], "report": {}, "log": []}
    for h in HEXES:
        st["hexes"][h] = {"level": lv[h], "biome": rng.choice(BIOMES[hkey(h)[1]]),
                          "people": TOWER_FOLK, "holder": TOWER, "lake": False, "sites": []}
    for people, hexes in zip(peoples, realms):
        for h in hexes:
            st["hexes"][h].update(people=people, holder=people)
    lakes = rng.sample(HEXES, N_LAKES)
    for h in lakes:
        st["hexes"][h]["lake"] = True
    used, srcs = set(), list(lakes)
    for _ in range(N_RIVERS):
        for _ in range(10000):
            src = rng.choice(srcs + ["edge"])
            path = river_walk(rng, used, None if src == "edge" else src)
            if path:
                break
        else:
            raise SystemExit("error: could not lay a river")
        if src != "edge":
            srcs.remove(src)
        used |= set(path)
        st["rivers"].append({"from": src, "edges": path})
    good = set(rng.sample(peoples, N_REALMS - N_BAD))
    for people in peoples:
        mine = deepest(st, hexes_of(st, people))
        s = sum(lv[h] for h in mine)
        force = max(1, min(MAX_FORCE, int(s / START_DIV + 0.5)))
        f = {"name": people, "leader": new_leader(st, people, rng, "good" if people in good else "bad"),
             "force": force, "treasury": s * START_GP, "seat": mine[0], "hexes": mine,
             "standing": 1 if people in good else 0, "goal": None, "squeeze_until": 0,
             "dissident": None, "last": None}
        st["realms"][people] = f
        add_site(st, people, "seat", mine[0])
        add_site(st, people, "garrison", mine[1])
        add_site(st, people, "works", mine[2])
    sync(st)
    st["rng"] = rng.getrandbits(32)
    t = Turn(st)  # every realm starts with a goal
    for n in st["realms"]:
        t.pick_goal(n)
    st["rng"] = t.rng.getrandbits(32)
    st["log"] = ["The world begins."] + [x for x in t.log]
    return st


# ---- Mission fights ----

_MON = {}


def monsters():
    if not _MON:
        for name, cr, xp, _ in load_monsters():
            _MON[name] = (cr, xp)
    return _MON


def build_fight(names, budget):
    """At most FIGHT_MAX monsters of at most two kinds from names, the most XP ≤ budget.
    Deterministic. Returns ([(count, name)], total, over_budget)."""
    M = monsters()
    best = None
    for lead in [None] + names:
        for troop in names:
            for n in range(1, FIGHT_MAX + 1):
                k = n + (1 if lead else 0)
                if k > FIGHT_MAX:
                    continue
                tot = M[troop][1] * n + (M[lead][1] if lead else 0)
                if tot > budget:
                    continue
                score = (tot, -k, -names.index(troop))
                if best is None or score > best[0]:
                    parts = [(1, lead)] if lead and lead != troop else []
                    cnt = n + (1 if lead == troop else 0)
                    best = (score, parts + [(cnt, troop)], tot)
    if best:
        return best[1], best[2], False
    cheap = min(names, key=lambda n: M[n][1])
    return [(1, cheap)], M[cheap][1], True


def fight_for(st, target, level):
    """target: a site dict (Strike or Rob), or a realm name (the Aid obstacle).
    Returns (title, tier, difficulty, budget, parts, total, over)."""
    if isinstance(target, dict):
        names, tier = site_fight(st, target), site_tier(st, target)
        title = f"{sname(st, target)} in {target['hex']}"
    else:
        f = st["realms"][target]
        g = f["goal"]
        h = aim_hex(st, target)
        if g and g["target"] and g["target"] != TOWER:
            o = st["realms"][g["target"]]
            names, tier = GARRISON_FIGHT[tier_of(o["force"])], tier_of(o["force"])
            title = f"Aid {the(target)} in {h}: {poss(g['target'])} soldiers"
        else:
            names, tier = BEASTS[st["hexes"][h]["people"]], tier_of(f["force"])
            title = f"Aid {the(target)} in {h}: the beasts of {h}"
    diff = ["Low", "Moderate", "High"][tier - 1]
    budget = BUDGET[level][tier - 1]
    parts, total, over = build_fight(names, budget)
    return title, tier, diff, budget, parts, total, over


def fight_lines(st, target, level):
    title, tier, diff, budget, parts, total, over = fight_for(st, target, level)
    M = monsters()
    out = [f"**Fight · {title}**", "",
           f"- Tier {tier} → {diff} for level {level}: budget {budget:,} XP"]
    for n, m in parts:
        out.append(f"- {n}× {m} · CR {M[m][0]} · {M[m][1]:,} XP each")
    out.append(f"- {total:,} XP total{' (over budget: nothing smaller fits)' if over else ''}"
               f" · coins on them {total // 10:,} GP")
    return out


def fight_word(st, target, level):
    """'Moderate (Knights)' for the Open and Chance lines."""
    _, _, diff, _, parts, _, _ = fight_for(st, target, level)
    return f"{diff}, {', '.join(f'{n} {m}' for n, m in parts)}"


# ---- The world's turn ----

PASSIVE = dict(at=None, level=None, strike=None, rob=None, aid=None, contact=None, delve=False,
               goal=None, buy=[], give=[], back=None, hinder=None, set=[], deposit=0,
               withdraw=0, plan=[])


class Turn:
    def __init__(self, st):
        self.st = st
        self.rng = random.Random(st["rng"])
        self.month = st["month"]
        self.log = []
        self.income = []
        self.events = []
        self.plan = []
        self.happened = []      # dicts: the tower's goal line, then one per realm
        self.stats = Counter()
        self.gave = Counter()   # realm → GP given this month
        self.backed = {}        # realm → +1 / −1
        self.touched = {}       # realm → what Morten did to its goal this month
        self.tower_marks = []   # (n, why) on the tower's goal this month
        self.mission = None

    # -- small helpers --
    def d(self, n):
        return self.rng.randint(1, n)

    def R(self, name):
        return self.st["realms"][name]

    @property
    def T(self):
        return self.st["tower"]

    def holder(self, h):
        return self.st["hexes"][h]["holder"]

    def say(self, text):
        self.log.append(text)

    def event(self, actor, action, frm, to, target, result, text, involves=()):
        self.events.append({"month": self.month, "actor": actor, "action": action,
                            "from_hex": frm, "to_hex": to, "target": target, "result": result,
                            "text": text, "involves": sorted({actor, *involves} - {None})})
        self.say(text)

    def realm(self, s):
        for n in self.st["realms"]:
            if n.lower() == s.strip().lower():
                return n
        raise Bad(f"no realm '{s}' (realms: {', '.join(self.st['realms'])})")

    def hexarg(self, s):
        h = s.strip().upper()
        if h not in self.st["hexes"]:
            raise Bad(f"no hex '{s}' (A1–D5)")
        return h

    def site(self, sid):
        s = self.st["sites"].get(sid.strip().lower())
        if not s:
            raise Bad(f"no site '{sid}' (sites: {', '.join(self.st['sites'])})")
        return s

    def step(self):
        return mark_step(self.st)

    def stand(self, name, delta, cap=None, why=""):
        f = self.R(name)
        old = f["standing"]
        new = max(-2, min(2, old + delta))
        if cap is not None and delta > 0:
            new = min(new, max(old, cap))
        if new == old:
            return ""
        f["standing"] = new
        self.stats["standing"] += 1
        self.say(f"Standing: {the(name)} {old:+d} → {new:+d} ({standing_word(new)}){', ' + why if why else ''}.")
        return f"standing {new:+d}, {standing_word(new)}"

    def set_standing(self, name, value, why=""):
        f = self.R(name)
        old = f["standing"]
        f["standing"] = value
        if old != value:
            self.say(f"Standing: {the(name)} {old:+d} → {value:+d} ({standing_word(value)}){', ' + why if why else ''}.")

    def tower_mark(self, n, why):
        g = self.T["goal"]
        if not g or n == 0:
            return
        g["marks"] = max(0, min(g["size"], g["marks"] + n))
        self.tower_marks.append((n, why))
        self.say(f"The tower's goal {goal_text(self.st, g)}: {n:+d} ({why}) → {clock_text(g)}.")

    def new_goal(self, kind, target=None, hex=None, size=None):
        if size is None:
            size = CLOCK[kind]
            if kind == "take" and walled(self.st, hex):
                size = WALLED_TAKE
        return {"kind": kind, "target": target, "hex": hex, "size": size, "marks": 0,
                "since": self.month, "waits": 0}

    # -- the picker (section 7) --
    def pick_goal(self, name, why="new goal"):
        st, f = self.st, self.R(name)
        tag, bad = f["leader"]["tag"], f["leader"]["label"] == "bad"
        tier, ally = tier_now(st), is_ally(f)
        g, note = None, ""
        if not f["hexes"]:
            g = self.take_back(name, landless=True)
        if g is None and bad and not ally:
            if f["standing"] <= -1:
                g = self.new_goal("break_tower", TOWER)
            elif tier >= WARDEN and f["standing"] <= 0:
                r = self.d(6)
                note = f" (the tower is {tier_name(tier)}: d6 {r} for break the tower)"
                if r >= 4:
                    g = self.new_goal("break_tower", TOWER)
            elif MENACE <= 6 and f["standing"] <= 0 and TOWER in neighbours_of(st, name):
                r = self.d(6)
                note = f" (a neighbour of the tower: d6 {r} for break the tower)"
                if r >= MENACE:
                    g = self.new_goal("break_tower", TOWER)
        if g is None:
            g = self.take_back(name)
        if g is None and not bad and 0 <= f["standing"] <= 1 and tier >= LORD:
            r = self.d(6)
            note = f" (the tower is {tier_name(tier)}: d6 {r} for court the tower)"
            if r >= 4:
                g = self.new_goal("court", TOWER)
        if g is None and RICH and f["treasury"] >= RICH:
            if f["force"] < MAX_FORCE:
                g = self.new_goal("raise")
            else:
                for h in deepest(st, [h for h in f["hexes"] if not walled(st, h)]):
                    g = self.new_goal("fortify", None, h)
                    break
            if g:
                note = f" (rich: {f['treasury']:,} GP)"
        if g is None:
            g = self.tag_goal(name)
        if g is None:
            g = self.fallback(name)
        f["goal"] = g
        self.stats["goals_picked"] += 1
        self.stats[f"picked_{g['kind']}"] += 1
        self.say(f"{cap(the(name))} ({label(f)}): {why}, {goal_text(st, g)}"
                 f" (clock {g['size']}){note}.")
        return g

    def take_back(self, name, landless=False):
        st, f = self.st, self.R(name)
        lost = [h for h in HEXES if st["hexes"][h]["people"] == name and self.holder(h) != name]
        ok = []
        for h in deepest(st, lost):
            hold = self.holder(h)
            if hold == TOWER:
                if h == st["warded"] or is_ally(f):
                    continue
                ok.append(h)
            elif landless or f["force"] >= self.R(hold)["force"]:
                ok.append(h)
        if not ok:
            return None
        return self.new_goal("take", self.holder(ok[0]), ok[0])

    def tag_goal(self, name):
        st, f = self.st, self.R(name)
        tag = f["leader"]["tag"]
        if tag == "Conqueror":
            seats = {x["seat"] for x in st["realms"].values()} | {st["warded"]}
            border = {n for h in f["hexes"] for n in nbrs(h)} - set(f["hexes"]) - seats
            if is_ally(f):
                border -= set(hexes_of(st, TOWER))
            if CONQ_OPEN:
                opn = [h for h in border if not site_at(st, h, "garrison", self.holder(h))
                       and not walled(st, h)]
                border = opn or border
            for h in deepest(st, border):
                return self.new_goal("take", self.holder(h), h)
            return None
        if tag == "Raider":
            ns = neighbours_of(st, name)
            if is_ally(f):
                ns = [n for n in ns if n != TOWER]
            if not ns:
                return None
            rich = max(ns, key=lambda n: (self.T["treasury"] if n == TOWER else self.R(n)["treasury"],
                                          n != TOWER, -ns.index(n)))
            return self.new_goal("raid", rich)
        if tag == "Slaver":
            ns = [n for n in neighbours_of(st, name) if n != TOWER and self.R(n)["force"] >= 2]
            if not ns:
                return None
            weak = min(ns, key=lambda n: (self.R(n)["force"], self.R(n)["treasury"], n))
            return self.new_goal("press", weak)
        if tag == "Tyrant":
            last = f["last"]
            if last == "squeeze":
                if not walled(st, f["seat"]):
                    return self.new_goal("fortify", None, f["seat"])
                if f["force"] < MAX_FORCE:
                    return self.new_goal("raise")
            elif last == "fortify" and f["force"] < MAX_FORCE:
                return self.new_goal("raise")
            return self.new_goal("squeeze")
        if tag == "Liberator":
            ns = [n for n in neighbours_of(st, name) if n != TOWER
                  and self.R(n)["leader"]["label"] == "bad" and self.R(n)["force"] < f["force"]]
            if ns:
                weak = min(ns, key=lambda n: (self.R(n)["force"], n))
                return self.new_goal("break", weak)
        # Steward, and a Liberator with no tyrant in reach
        if not walled(st, f["seat"]):
            return self.new_goal("fortify", None, f["seat"])
        if f["last"] == "fortify" and f["force"] < MAX_FORCE:
            return self.new_goal("raise")
        for h in deepest(st, [h for h in f["hexes"] if not walled(st, h)]):
            return self.new_goal("fortify", None, h)
        if f["force"] < MAX_FORCE:
            return self.new_goal("raise")
        return None

    def fallback(self, name):
        st, f = self.st, self.R(name)
        if f["force"] < MAX_FORCE and f["treasury"] >= PRICE["raise"] * (f["force"] + 1):
            return self.new_goal("raise")
        if f["seat"] and not walled(st, f["seat"]):
            return self.new_goal("fortify", None, f["seat"])
        return self.new_goal("squeeze")

    def gone(self, name):
        """Why a realm's goal has lost its target, or None."""
        st, f = self.st, self.R(name)
        g = f["goal"]
        k = g["kind"]
        if k == "take":
            if self.holder(g["hex"]) != g["target"]:
                return f"{g['hex']} is no longer {poss(g['target'])}"
            if g["target"] == TOWER and is_ally(f):
                return "the tower is an ally"
        elif k == "fortify":
            if self.holder(g["hex"]) != name:
                return f"{g['hex']} is lost"
            if walled(st, g["hex"]):
                return f"{g['hex']} already has walls"
        elif k == "raise" and f["force"] >= MAX_FORCE:
            return "its Force is 5 already"
        elif k in ("press", "break") and self.R(g["target"])["force"] <= 1:
            return f"{the(g['target'])} are at Force 1 already"
        elif k in ("raid", "break_tower") and g["target"] == TOWER and is_ally(f):
            return "the tower is an ally"
        elif k == "court" and f["standing"] >= 1:
            return f"the tower already counts it {standing_word(f['standing'])}"
        return None

    # -- the roll (section 7) --
    def roll_goal(self, name):
        st, f = self.st, self.R(name)
        g = f["goal"]
        mods = []
        t = g["target"]
        if t and t != TOWER:
            o = self.R(t)
            if f["force"] > o["force"]:
                mods.append((1, f"Force {f['force']} over {o['force']}"))
            elif f["force"] < o["force"]:
                mods.append((-1, f"Force {f['force']} under {o['force']}"))
        aimed = g["hex"] if g["kind"] == "take" else st["warded"] if g["kind"] == "break_tower" else None
        if aimed:
            holder = self.holder(aimed)
            if site_at(st, aimed, "garrison", holder):
                mods.append((-1, f"garrison in {aimed}"))
            if site_at(st, aimed, "walls", holder):
                mods.append((-1, f"walls in {aimed}"))
        if self.gave[name] >= GIVE_MIN:
            mods.append((1, f"the tower gave {self.gave[name]:,} GP"))
        if name in self.backed:
            mods.append((self.backed[name], "the tower backs it" if self.backed[name] > 0 else "the tower hinders it"))
        die = self.d(6)
        total = die + sum(m for m, _ in mods)
        if die == 1:
            n, word = -1, "setback"
        elif total <= 2:
            n, word = 0, "nothing"
        elif total <= 5:
            n, word = 1, "one mark"
        else:
            n, word = 2, "two marks"
        old = g["marks"]
        g["marks"] = max(0, min(g["size"], old + n))
        mtxt = "".join(f" {m:+d} ({w})" for m, w in mods)
        self.say(f"{cap(the(name))}, {goal_text(st, g)}: d6 {die}{mtxt} = {total} → {word}:"
                 f" {g['marks']} of {g['size']}.")
        self.stats["rolls"] += 1
        return die, total, n, word

    # -- firing (section 7's catalogue) --
    def fire(self, name):
        """The goal's clock is full: pay and fire, or wait. Returns the effect in words."""
        st, f = self.st, self.R(name)
        g = f["goal"]
        k, t, h = g["kind"], g["target"], g["hex"]
        price = PRICE["raise"] * (f["force"] + 1) if k == "raise" else PRICE.get(k, 0)
        if price and f["treasury"] < price:
            if not g["waits"]:
                self.stats["waits"] += 1
            g["waits"] = price
            self.stats["wait_months"] += 1
            return f"done, waits for {price:,} GP (has {f['treasury']:,} GP)"
        if price:
            f["treasury"] -= price
            self.stats["paid"] += price
        aimed = aim_hex(st, name)
        if k == "take":
            self.take_hex(h, name)
            res = f"{h} is {poss(name)} now"
            self.stats["hexes_taken"] += 1
            if t == TOWER:
                self.stats["tower_lost"] += 1
        elif k == "fortify":
            add_site(st, name, "walls", h)
            res = f"{price} GP paid, walls stand at {h}"
        elif k == "raise":
            f["force"] += 1
            res = f"{price:,} GP paid, Force {f['force'] - 1} → {f['force']}"
            self.stats["raises"] += 1
        elif k == "raid":
            want = RAID_GP * f["force"]
            if t == TOWER:
                amt = min(want, self.T["treasury"] // 2)
                self.T["treasury"] -= amt
                self.stats["tower_raided"] += 1
            else:
                amt = min(want, self.R(t)["treasury"])
                self.R(t)["treasury"] -= amt
            f["treasury"] += amt
            res = f"{amt:,} GP taken from {the(t)}"
            self.stats["raid_gp"] += amt
            self.stats["raids"] += 1
        elif k == "press":
            o = self.R(t)
            f["force"] = min(MAX_FORCE, f["force"] + 1)
            o["force"] = max(1, o["force"] - 1)
            res = f"Force {f['force']}, {the(t)} down to Force {o['force']}"
        elif k == "squeeze":
            amt = SQUEEZE_GP * len(f["hexes"])
            f["treasury"] += amt
            f["squeeze_until"] = self.month + SQUEEZE_MONTHS
            res = f"{amt:,} GP squeezed out, Contact there is DC +{SQUEEZE_DC} for {SQUEEZE_MONTHS} months"
        elif k == "break":
            o = self.R(t)
            o["force"] = max(1, o["force"] - 1)
            res = f"{the(t)} down to Force {o['force']}"
        elif k == "break_tower":
            res = self.break_tower(name)
        elif k == "court":
            res = self.stand(name, 1, cap=1, why="courting the tower") or "standing unchanged"
        else:
            res = "nothing"
        self.stats["fired"] += 1
        self.stats[f"fired_{k}"] += 1
        self.event(name, "Goal", f["seat"], aimed, goal_text(st, g), res,
                   f"{cap(the(name))} ({label(f)}) did {goal_text(st, g)}: {res}.",
                   involves=[t] if t else [])
        f["last"] = k
        f["goal"] = None
        return res

    def break_tower(self, name):
        st, T = self.st, self.T
        half = T["treasury"] // 2
        T["treasury"] -= half
        self.stats["tower_broken"] += 1
        if T["hold"] > 0:
            T["hold"] -= 1
            res = f"the tower's Hold {T['hold'] + 1} → {T['hold']}, {half:,} GP taken"
            self.stats["hold_lost"] += 1
        else:
            mine = [h for h in hexes_of(st, TOWER) if h != st["warded"]]
            if mine:
                h = deepest(st, mine)[0]
                self.take_hex(h, name)
                res = f"Hold is 0, so {h} is {poss(name)} now, and {half:,} GP taken"
                self.stats["tower_lost"] += 1
            else:
                res = f"Hold is 0 and the tower holds no other hex: {half:,} GP taken"
        w = self.stand(name, -1, why="at war with the tower")
        return res + (f"; {w}" if w else "")

    def take_hex(self, h, taker):
        st = self.st
        loser = self.holder(h)
        for s in sites_of(st, loser, h):
            if s["kind"] == "seat":
                del st["sites"][s["id"]]
            else:
                s["owner"] = taker
        st["hexes"][h]["holder"] = taker
        sync(st)
        if taker != TOWER and self.R(taker)["seat"] is None:
            self.R(taker)["seat"] = h
            add_site(st, taker, "seat", h)
            self.say(f"{cap(the(taker))} hold land again: their seat is {h}.")
        if loser != TOWER:
            L = self.R(loser)
            if L["seat"] == h:
                left = deepest(st, L["hexes"])
                L["seat"] = left[0] if left else None
                if left:
                    add_site(st, loser, "seat", left[0])
                    self.say(f"{cap(the(loser))} move their seat to {left[0]}.")
                else:
                    self.say(f"{cap(the(loser))} hold no land now.")
            if taker == TOWER:
                self.stand(loser, -2, why=f"the tower took {h}")
        sync(st)

    # -- Morten's month (section 10) and the purse (section 9) --
    def land(self, o):
        st, T = self.st, self.T
        if o.level:
            if not 1 <= o.level <= 20:
                raise Bad("--level must be 1–20")
            st["morten"]["level"] = o.level
        if o.at:
            st["morten"]["hex"] = self.hexarg(o.at)
        here = st["morten"]["hex"]
        missions = [m for m in ("strike", "rob", "aid", "contact", "delve") if getattr(o, m)]
        if len(missions) > 1:
            raise Bad(f"one mission a month, not {' and '.join(missions)}")
        for line in o.plan:
            self.plan.append(line)
        if o.goal:
            self.set_goal(o.goal)
        if o.strike:
            self.do_strike(o.strike, here)
        if o.rob:
            self.do_rob(o.rob, here)
        if o.aid:
            self.do_aid(o.aid, here)
        if o.contact:
            self.do_contact(o.contact, here)
        if o.delve:
            lv = st["hexes"][here]["level"]
            self.mission = f"Morten: Delve floor {lv} under {here}."
            self.event(TOWER, "Delve", here, here, f"floor {lv}", "delved",
                       f"Morten: Delve floor {lv} under {here} (the dungeon game; no domain effect).")
        if o.deposit:
            if o.deposit < 0:
                raise Bad("--deposit must be positive")
            T["treasury"] += o.deposit
            self.say(f"Morten: deposit {o.deposit:,} GP → tower {T['treasury']:,} GP.")
        if o.withdraw:
            if not 0 < o.withdraw <= T["treasury"]:
                raise Bad(f"--withdraw {o.withdraw:,}: the tower holds {T['treasury']:,} GP")
            T["treasury"] -= o.withdraw
            self.say(f"Morten: withdraw {o.withdraw:,} GP → tower {T['treasury']:,} GP.")
        for spec in o.buy:
            self.buy(spec)
        for spec in o.set:
            self.set_ally_goal(spec)
        for spec in o.give:
            self.give(spec)
        for name, amt in sorted(self.gave.items()):
            if amt >= GIVE_MIN:
                g = T["goal"]
                if g and g["kind"] == "topple" and g["target"] == name:
                    self.tower_mark(1, f"{amt:,} GP to the dissident")
                else:
                    self.stand(name, 1, cap=1, why=f"the tower gave {amt:,} GP")
                    if g and g["kind"] == "ally" and g["target"] == name:
                        self.tower_mark(1, f"{amt:,} GP given")
        if o.back and o.hinder:
            raise Bad("one of --back and --hinder a month")
        for spec, sign in ((o.back, 1), (o.hinder, -1)):
            if spec:
                self.back(spec, sign)
        if self.mission:
            self.plan.insert(0, self.mission)
        else:
            self.plan.insert(0, "Morten: no mission.")

    def do_strike(self, sid, here):
        st = self.st
        s = self.site(sid)
        if s["owner"] == TOWER:
            raise Bad(f"{s['id']} is the tower's own {s['name']}")
        if s["hex"] != here:
            raise Bad(f"{sname(st, s)} is in {s['hex']}; Morten is in {here} (use --at)")
        name, f = s["owner"], self.R(s["owner"])
        n = self.step()
        bits = []
        g = f["goal"]
        if g:
            old = g["marks"]
            g["marks"] = max(0, old - n)
            bits.append(f"their {goal_text(st, g)} {old} → {g['marks']} of {g['size']}")
            lost = old - g["marks"]
            self.touched[name] = (f"the Strike cost them {lost} mark{'s' if lost != 1 else ''}" if lost
                                  else "the Strike found their clock empty")
        w = self.stand(name, -2 if s["kind"] == "seat" else -1, why=f"Morten struck their {s['name']}")
        if w:
            bits.append(w)
        tg = self.T["goal"]
        if tg:
            if tg["kind"] == "take" and tg["hex"] == here:
                self.tower_mark(n, f"the Strike in {here}")
            elif tg["kind"] == "topple" and tg["target"] == name:
                self.tower_mark(n if s["kind"] == "seat" else 1, f"the Strike on their {s['name']}")
        self.stats["strikes"] += 1
        self.mission = f"Morten: Strike {sname(st, s)} in {here} (tier {site_tier(st, s)})."
        self.event(TOWER, "Strike", here, here, sname(st, s), "won: " + "; ".join(bits),
                   f"Morten: Strike on {sname(st, s)} in {here}, won: {'; '.join(bits)}.",
                   involves=[name])

    def do_rob(self, sid, here):
        st = self.st
        s = self.site(sid)
        if s["kind"] != "works" or s["owner"] == TOWER:
            raise Bad(f"Rob needs a realm's works; {s['id']} is {sname(st, s)}")
        if s["hex"] != here:
            raise Bad(f"{sname(st, s)} is in {s['hex']}; Morten is in {here} (use --at)")
        name, f = s["owner"], self.R(s["owner"])
        amt = min(ROB_GP * f["force"], f["treasury"])
        f["treasury"] -= amt
        self.T["treasury"] += amt
        w = self.stand(name, -1, why=f"Morten robbed their {s['name']}")
        self.stats["robs"] += 1
        self.mission = f"Morten: Rob {sname(st, s)} in {here}."
        self.event(TOWER, "Rob", here, here, sname(st, s), f"won: {amt:,} GP",
                   f"Morten: Rob {sname(st, s)} in {here}, won: {amt:,} GP to the tower"
                   f" ({the(name)} {f['treasury'] + amt:,} → {f['treasury']:,} GP){'; ' + w if w else ''}.",
                   involves=[name])

    def do_aid(self, spec, here):
        st = self.st
        name = self.realm(spec)
        f = self.R(name)
        g = f["goal"]
        if not g:
            raise Bad(f"{the(name)} have no goal to aid")
        if g["target"] == TOWER:
            raise Bad(f"{poss(name)} goal is {goal_text(st, g)}: the tower can't aid that")
        aimed = aim_hex(st, name)
        if aimed != here:
            raise Bad(f"{poss(name)} {goal_text(st, g)} is aimed at {aimed}; Morten is in {here} (use --at)")
        n = self.step()
        old = g["marks"]
        g["marks"] = min(g["size"], old + n)
        self.touched[name] = f"the Aid gave them {g['marks'] - old} mark{'s' if g['marks'] - old != 1 else ''}"
        bits = [f"their {goal_text(st, g)} {old} → {g['marks']} of {g['size']}"]
        w = self.stand(name, 1, cap=1, why="Morten aided them")
        if w:
            bits.append(w)
        tg = self.T["goal"]
        if tg and tg["kind"] == "ally" and tg["target"] == name:
            self.tower_mark(n, "the Aid")
        self.stats["aids"] += 1
        self.mission = f"Morten: Aid {the(name)} in {here} with their {goal_text(st, g)}."
        self.event(TOWER, "Aid", here, aimed, the(name), "won: " + "; ".join(bits),
                   f"Morten: Aid {the(name)} in {here}, won: {'; '.join(bits)}.", involves=[name])

    def do_contact(self, spec, here):
        st = self.st
        name = self.realm(spec)
        f = self.R(name)
        if here not in f["hexes"]:
            raise Bad(f"Contact {the(name)} needs Morten in one of their hexes ({' '.join(f['hexes']) or 'none'}); he is in {here}")
        if f["standing"] <= -2:
            raise Bad(f"{the(name)} are enemies and refuse Contact")
        dc = contact_dc(st, name)
        bits = []
        w = self.stand(name, 1, cap=1, why="Morten's Contact")
        if w:
            bits.append(w)
        if f["standing"] >= 1 and not f["dissident"]:
            dn = name_for(st, name, self.rng)
            f["dissident"] = {"name": dn, "hex": here}
            bits.append(f"{dn} is named as the dissident")
        tg = self.T["goal"]
        if tg and tg["kind"] == "ally" and tg["target"] == name:
            self.tower_mark(1, "the Contact")
        self.stats["contacts"] += 1
        self.mission = f"Morten: Contact {the(name)} in {here} (Persuasion DC {dc})."
        self.event(TOWER, "Contact", here, here, the(name), "won: " + ("; ".join(bits) or "nothing new"),
                   f"Morten: Contact {the(name)} in {here} (DC {dc}), won: {'; '.join(bits) or 'nothing new'}.",
                   involves=[name])

    def set_goal(self, spec):
        st, T = self.st, self.T
        kind, _, arg = spec.strip().partition(":")
        kind = kind.lower()
        old = T["goal"]
        if kind == "drop":
            if not old:
                raise Bad("the tower has no goal to drop")
            self.say(f"Tower: drops {goal_text(st, old)} at {clock_text(old)}.")
            self.event(TOWER, "Goal", None, None, goal_text(st, old), "dropped",
                       f"Tower: the goal {goal_text(st, old)} is dropped at {clock_text(old)}.")
            T["goal"] = None
            self.plan.append(f"Tower: drop the goal {goal_text(st, old)}.")
            return
        if kind == "take":
            h = self.hexarg(arg)
            holder = self.holder(h)
            if holder == TOWER:
                raise Bad(f"{h} is the tower's already")
            f = self.R(holder)
            size = TOWER_CLOCK["take"] + f["force"] + (WALLED_TOWER_TAKE if walled(st, h) else 0)
            g = {"kind": "take", "target": holder, "hex": h, "size": size, "marks": 0,
                 "since": self.month, "waits": 0}
        elif kind == "ally":
            name = self.realm(arg)
            if is_ally(self.R(name)):
                raise Bad(f"{the(name)} are an ally already")
            g = {"kind": "ally", "target": name, "hex": None, "size": TOWER_CLOCK["ally"],
                 "marks": 0, "since": self.month, "waits": 0}
        elif kind == "topple":
            name = self.realm(arg)
            f = self.R(name)
            if not f["dissident"]:
                raise Bad(f"topple {the(name)} needs a dissident named there (Contact at standing +1)")
            g = {"kind": "topple", "target": name, "hex": f["seat"],
                 "size": TOWER_CLOCK["topple"] + f["force"], "marks": 0, "since": self.month,
                 "waits": 0}
        else:
            raise Bad(f"--goal {spec}: want take:HEX, ally:REALM, topple:REALM or drop")
        if old and (old["kind"], old["target"], old["hex"]) == (g["kind"], g["target"], g["hex"]):
            self.plan.append(f"Tower: the goal {goal_text(st, old)}, {clock_text(old)}.")
            return
        if old:
            self.say(f"Tower: drops {goal_text(st, old)} at {clock_text(old)} for a new goal.")
        T["goal"] = g
        self.plan.append(f"Tower: goal {goal_text(st, g)} (clock {g['size']})"
                         + (f", dropping {goal_text(st, old)} at {clock_text(old)}." if old else "."))
        self.event(TOWER, "Goal", None, g["hex"], goal_text(st, g), f"declared, clock {g['size']}",
                   f"Tower: the goal is {goal_text(st, g)}, a clock of {g['size']}.")

    def pay(self, what, price):
        T = self.T
        if T["treasury"] < price:
            raise Bad(f"{what} costs {price:,} GP; the tower has {T['treasury']:,} GP at that point")
        T["treasury"] -= price

    def buy(self, spec):
        st, T = self.st, self.T
        what, _, h = spec.strip().lower().partition("@")
        tier = tier_now(st)
        if what == "mend":
            if T["hold"] >= HOLD:
                raise Bad(f"Hold is {HOLD} of {HOLD} already")
            self.pay("Mend", PRICE["mend"])
            T["hold"] += 1
            self.stats["mends"] += 1
            self.plan.append(f"Tower: Mend ({PRICE['mend']} GP), Hold {T['hold']} of {HOLD}.")
            self.event(TOWER, "Mend", None, None, "Hold", f"{T['hold']} of {HOLD}",
                       f"Tower: Mend for {PRICE['mend']} GP → Hold {T['hold']} of {HOLD}.")
            return
        if what not in ("garrison", "walls", "works"):
            raise Bad(f"--buy {spec}: want garrison@HEX, walls@HEX, works@HEX or mend")
        if not h:
            raise Bad(f"--buy {spec}: {what} needs a hex ({what}@HEX)")
        h = self.hexarg(h)
        if self.holder(h) != TOWER:
            raise Bad(f"{h} is {poss(self.holder(h))}, not the tower's")
        if what in ("garrison", "walls") and tier < LORD:
            raise Bad(f"{what.capitalize()} needs the tower at Lord (tier 1); it is {tier_name(tier)}")
        if what == "walls" and not site_at(st, h, "garrison", TOWER):
            raise Bad(f"Walls at {h} need a garrison there first")
        if site_at(st, h, what, TOWER):
            raise Bad(f"the tower has {what} at {h} already")
        self.pay(what.capitalize(), PRICE[what])
        s = add_site(st, TOWER, what, h)
        sync(st)
        self.stats["buys"] += 1
        self.plan.append(f"Tower: {s['name']} at {h} ({PRICE[what]} GP).")
        self.event(TOWER, "Buy", None, h, f"{s['name']} {s['id']}", f"{PRICE[what]} GP",
                   f"Tower: {s['name']} {s['id']} built at {h} for {PRICE[what]} GP.")

    def give(self, spec):
        st, T = self.st, self.T
        r, _, amt = spec.partition("=")
        name = self.realm(r)
        try:
            amt = int(amt)
        except ValueError:
            raise Bad(f"--give {spec}: want REALM=GP")
        if amt <= 0:
            raise Bad(f"--give {spec}: the gift must be positive")
        self.pay(f"Give {the(name)}", amt)
        g = T["goal"]
        to_dissident = g and g["kind"] == "topple" and g["target"] == name
        if to_dissident:
            dn = self.R(name)["dissident"]["name"]
            self.plan.append(f"Tower: Give {amt:,} GP to {dn}, the dissident of {the(name)}.")
            self.event(TOWER, "Give", None, self.R(name)["seat"], dn, f"{amt:,} GP",
                       f"Tower: Give {amt:,} GP to {dn}, {poss(name)} dissident.", involves=[name])
        else:
            self.R(name)["treasury"] += amt
            self.plan.append(f"Tower: Give {amt:,} GP to {the(name)}.")
            self.event(TOWER, "Give", None, self.R(name)["seat"], the(name), f"{amt:,} GP",
                       f"Tower: Give {amt:,} GP to {the(name)} → {self.R(name)['treasury']:,} GP.",
                       involves=[name])
        self.gave[name] += amt
        self.stats["given"] += amt

    def back(self, spec, sign):
        st = self.st
        name = self.realm(spec)
        tier = tier_now(st)
        if tier < WARDEN:
            raise Bad(f"back and hinder need the tower at Warden (tier 2); it is {tier_name(tier)}")
        word = "Back" if sign > 0 else "Hinder"
        self.pay(word, PRICE["back"])
        self.backed[name] = sign
        self.plan.append(f"Tower: {word} {the(name)} ({PRICE['back']} GP).")
        self.event(TOWER, word, None, self.R(name)["seat"], the(name), f"{sign:+d} on their roll",
                   f"Tower: {word} {the(name)} for {PRICE['back']} GP: {sign:+d} on their roll.",
                   involves=[name])

    def set_ally_goal(self, spec):
        """The Master's power: --set REALM=GOAL, GOAL as take:HEX, fortify:HEX, raise,
        raid:REALM, press:REALM, squeeze or break:REALM."""
        st = self.st
        tier = tier_now(st)
        if tier < MASTER:
            raise Bad(f"--set needs the tower at Master (tier 4); it is {tier_name(tier)}")
        r, _, gs = spec.partition("=")
        name = self.realm(r)
        f = self.R(name)
        if not is_ally(f):
            raise Bad(f"--set: {the(name)} are not an ally")
        kind, _, arg = gs.strip().lower().partition(":")
        if kind == "take":
            h = self.hexarg(arg)
            if self.holder(h) in (name, TOWER) or h == st["warded"]:
                raise Bad(f"--set {spec}: {h} is {poss(self.holder(h))}")
            g = self.new_goal("take", self.holder(h), h)
        elif kind == "fortify":
            h = self.hexarg(arg)
            if self.holder(h) != name or walled(st, h):
                raise Bad(f"--set {spec}: {h} is not an unwalled hex of theirs")
            g = self.new_goal("fortify", None, h)
        elif kind in ("raid", "press", "break"):
            t = self.realm(arg)
            if t == name:
                raise Bad(f"--set {spec}: a realm can't {kind} itself")
            g = self.new_goal(kind, t)
        elif kind in ("raise", "squeeze"):
            g = self.new_goal(kind)
        else:
            raise Bad(f"--set {spec}: want take:HEX, fortify:HEX, raise, raid:REALM, press:REALM, squeeze or break:REALM")
        f["goal"] = g
        self.plan.append(f"Tower: sets {poss(name)} goal to {goal_text(st, g)} (clock {g['size']}).")
        self.event(TOWER, "Set", None, aim_hex(st, name), the(name), goal_text(st, g),
                   f"Tower: {poss(name)} goal is set to {goal_text(st, g)} (clock {g['size']}).",
                   involves=[name])

    # -- the world's turn (section 12) --
    def economy(self):
        st = self.st
        for name in list(st["realms"]) + [TOWER]:
            f = self.T if name == TOWER else self.R(name)
            hs = hexes_of(st, name)
            hx = sum(hex_income(st, h) for h in hs)
            wk = WORKS_INCOME * len(sites_of(st, name, kind="works"))
            f["treasury"] += hx + wk
            self.stats["income"] += hx + wk
            bits = [f"{hx:,} GP from {len(hs)} hex{'es' if len(hs) != 1 else ''}"]
            if wk:
                bits.append(f"{wk} GP from works")
            self.income.append(f"{cap(the(name))}: {' + '.join(bits)} → {f['treasury']:,} GP.")

    def order(self):
        names = list(self.st["realms"])
        rolls = {n: self.d(6) for n in names}
        names.sort(key=lambda n: (-self.R(n)["force"], -rolls[n], n))
        self.say("Order: " + " · ".join(f"{n} Force {self.R(n)['force']} (d6 {rolls[n]})" for n in names) + ".")
        return names

    def world(self):
        st = self.st
        for name in self.order():
            f = self.R(name)
            entry = {"who": name, "label": label(f), "goal": None, "roll": None, "marks": 0,
                     "size": 0, "fired": False, "text": "", "far": False, "waits": 0, "new": None}
            self.happened.append(entry)
            note = ""
            if f["goal"] is None:
                self.pick_goal(name)
            why = self.gone(name)
            if why:
                old = f["goal"]
                self.say(f"{cap(the(name))} drop {goal_text(st, old)}: {why}.")
                f["last"] = old["kind"]
                f["goal"] = None
                self.stats["goal_drop"] += 1
                self.stats["drop_gone"] += 1
                self.stats[f"gone_{old['kind']}"] += 1
                self.pick_goal(name, why=f"{goal_text(st, old)} was dropped ({why}); new goal")
                note = f"dropped *{goal_text(st, old)}* ({why}) and took up *{goal_text(st, f['goal'])}* ({f['goal']['size']}); "
            g = f["goal"]
            entry["goal"] = goal_text(st, g)
            entry["size"] = g["size"]
            if g["waits"]:
                if f["treasury"] >= g["waits"]:
                    res = self.fire(name)
                    entry.update(roll="paid", marks=g["size"], fired=True)
                    self.pick_goal(name)
                    entry["new"] = goal_text(st, f["goal"])
                    entry["text"] = (f"{cap(who(f))}, *{goal_text(st, g)}*: paid at last, {res}."
                                     f" New goal: *{entry['new']}* ({f['goal']['size']}).")
                else:
                    entry.update(roll="waits", marks=g["size"], waits=g["waits"])
                    self.stats["wait_months"] += 1
                    self.say(f"{cap(the(name))}, {goal_text(st, g)}: done, waits for"
                             f" {g['waits']:,} GP (has {f['treasury']:,} GP).")
                    entry["text"] = (f"{cap(who(f))}, *{goal_text(st, g)}*: done, waits for"
                                     f" {g['waits']:,} GP (has {f['treasury']:,} GP).")
                continue
            die, total, n, word = self.roll_goal(name)
            if die == 1:
                rolled = "rolled a natural 1, a setback"
            elif total != die:
                rolled = f"rolled a {total} ({die} {total - die:+d})"
            else:
                rolled = f"rolled a {total}"
            entry["roll"] = rolled
            touched = self.touched.get(name)
            lead = f"{cap(who(f))} {note}" if note else f"{cap(who(f))}, *{goal_text(st, g)}*: "
            if touched:
                lead += touched + ", and "
            if g["marks"] >= g["size"]:
                res = self.fire(name)
                entry["marks"] = g["size"]
                if f["goal"] is None:
                    entry["fired"] = True
                    self.pick_goal(name)
                    entry["new"] = goal_text(st, f["goal"])
                    entry["text"] = (f"{lead}{rolled}: **{g['size']} of {g['size']}, done**, {res}."
                                     f" New goal: *{entry['new']}* ({f['goal']['size']}).")
                else:
                    entry["waits"] = g["waits"]
                    entry["text"] = f"{lead}{rolled}: **{g['size']} of {g['size']}**, {res}."
            else:
                entry["marks"] = g["marks"]
                entry["text"] = f"{lead}{rolled}: **{g['marks']} of {g['size']}**."
            if not touched and n == 0 and not note:
                entry["far"] = True

    def tower_goal(self):
        st, T = self.st, self.T
        g = T["goal"]
        if not g:
            return
        if g["kind"] == "take" and self.holder(g["hex"]) != g["target"]:
            self.say(f"Tower: {goal_text(st, g)} is dropped: {g['hex']} is {poss(self.holder(g['hex']))} now.")
            self.event(TOWER, "Goal", None, g["hex"], goal_text(st, g), "dropped",
                       f"Tower: the goal {goal_text(st, g)} is dropped: {g['hex']} changed hands.")
            T["goal"] = None
            self.happened.insert(0, {"who": TOWER, "label": None, "goal": goal_text(st, g),
                                     "roll": None, "marks": g["marks"], "size": g["size"],
                                     "fired": False, "far": False, "waits": 0, "new": None,
                                     "text": f"**The tower:** *{goal_text(st, g)}* is dropped: {g['hex']} changed hands first."})
            return
        if g["kind"] in ("take", "topple"):
            allies = [n for n, f in st["realms"].items() if is_ally(f) and n != g["target"]]
            k = min(len(allies), 2 if tier_now(st) >= POWER else 1)
            for n in allies[:k]:
                self.tower_mark(1, f"{the(n)}, an ally")
        res = ""
        fired = g["marks"] >= g["size"]
        if fired:
            res = self.fire_tower()
        bits = ", ".join(f"{n:+d} {w}" for n, w in self.tower_marks)
        text = f"**The tower:** *{goal_text(st, g)}*, **{g['marks']} of {g['size']}**"
        text += f" ({bits})" if bits else " (no marks this month)"
        text += f": done, {res}." if fired else "."
        self.happened.insert(0, {"who": TOWER, "label": None, "goal": goal_text(st, g),
                                 "roll": bits or None, "marks": g["marks"], "size": g["size"],
                                 "fired": fired, "far": False, "waits": 0, "new": None, "text": text})

    def fire_tower(self):
        st, T = self.st, self.T
        g = T["goal"]
        k, name = g["kind"], g["target"]
        f = self.R(name)
        if k == "take":
            self.take_hex(g["hex"], TOWER)
            res = f"{g['hex']} is the tower's with its sites"
            self.stats["tower_took"] += 1
        elif k == "ally":
            self.set_standing(name, 2, why="the tower's ally goal")
            res = f"{the(name)} are the tower's ally"
            self.stats["allied"] += 1
        else:
            old = f["leader"]
            dn = f["dissident"]["name"]
            f["leader"] = {"name": dn, "title": self.rng.choice(PEOPLES[name][0]), "label": "good",
                           "tag": self.rng.choice(GOOD)}
            f["dissident"] = None
            f["last"] = None
            f["goal"] = None
            T["toppled"] += 1
            self.set_standing(name, 2, why="a ruler the tower put on the throne")
            self.pick_goal(name)
            res = (f"{old['title']} {old['name']} is toppled; {f['leader']['title']} {dn} rules"
                   f" {the(name)} ({label(f)}), the treasury kept, new goal {goal_text(st, f['goal'])}")
            self.stats["toppled"] += 1
        T["goal"] = None
        sync(st)
        self.event(TOWER, "Goal", None, g["hex"] or f["seat"], goal_text(st, g), res,
                   f"Tower: {goal_text(st, g)} is done: {res}.", involves=[name])
        return res

    def cleanup(self):
        st, T = self.st, self.T
        for name, f in st["realms"].items():
            g = f["goal"]
            if g and not g["waits"] and self.month - g["since"] + 1 >= GOAL_MONTHS:
                self.say(f"{cap(the(name))} drop {goal_text(st, g)} after {GOAL_MONTHS} months at {clock_text(g)}.")
                f["last"] = g["kind"]
                f["goal"] = None
                self.stats["goal_drop"] += 1
                self.stats["drop_time"] += 1
                self.stats[f"timed_{g['kind']}"] += 1
                self.pick_goal(name, why=f"{goal_text(st, g)} dropped after {GOAL_MONTHS} months; new goal")
        sync(st)
        old, new = T.get("tier", 0), tier_now(st)
        if new != old:
            word = "rises to" if new > old else "falls to"
            self.say(f"The tower {word} {tier_name(new)} (tier {new}, Renown {renown_of(st)}).")
            self.event(TOWER, "Tier", None, None, tier_name(new), f"tier {new}",
                       f"The tower {word} {tier_name(new)} (tier {new}, Renown {renown_of(st)}).")
            self.stats["tier_changes"] += 1
        if new >= MASTER and all(is_ally(f) for f in st["realms"].values()) and not T["won"]:
            T["won"] = self.month
            self.say("The tower is Master of the twenty hexes and every realm is an ally or toppled: the world is his.")
        st["month"] += 1
        st["rng"] = self.rng.getrandbits(32)
        sync(st)

    def run(self, o):
        st = self.st
        self.land(o)
        if not any(p.startswith("Tower:") for p in self.plan):
            g = self.T["goal"]
            self.plan.append(f"Tower: the goal {goal_text(st, g)}, {clock_text(g)}; no purse action."
                             if g else "Tower: no goal, no purse action.")
        self.economy()
        self.world()
        self.tower_goal()
        self.cleanup()
        st["events"] = [{k: e[k] for k in ("month", "actor", "action", "from_hex", "to_hex",
                                           "target", "result")} for e in self.events]
        st["log"] = list(self.log)
        return self.month


# ---- Views ----

def hex_label(st, h):
    x = st["hexes"][h]
    return f"{h} (L{x['level']}, {x['biome']}, {x['holder']})"


def site_line(st, s, where=True):
    loc = f" in {s['hex']}" if where else ""
    mod = {"garrison": "−1 to goal rolls at this hex", "walls": "−1 to goal rolls at this hex; a take needs 6",
           "works": f"income +{WORKS_INCOME} GP; a Rob takes from it", "seat": "the ruler's court"}[s["kind"]]
    return f"{s['id']} {poss(s['owner'])} {s['name']}{loc} · tier {site_tier(st, s)} · {mod}"


def realm_line(st, f):
    L = f["leader"]
    g = f["goal"]
    bits = [f"{f['name']} · {L['title']} {L['name']} ({label(f)})", f"Force {f['force']}",
            f"{f['treasury']:,} GP", f"seat {f['seat'] or 'none'}",
            f"hexes {' '.join(f['hexes']) or 'none'}"]
    bits.append(f"goal: {goal_text(st, g)} · {clock_text(g)}" if g else "no goal")
    bits.append(f"standing {f['standing']:+d} {standing_word(f['standing'])}")
    if f.get("dissident"):
        bits.append(f"dissident {f['dissident']['name']} ({f['dissident']['hex']})")
    return " · ".join(bits)


def near_morten(st, name):
    h = st["morten"]["hex"]
    return bool({h, *nbrs(h)} & set(hexes_of(st, name)))


def near_tower(st, name):
    mine = set(hexes_of(st, TOWER))
    return bool({n for h in mine for n in nbrs(h)} & set(hexes_of(st, name)))


def aimed_at_tower(st, g):
    return bool(g) and (g["target"] == TOWER or (g["kind"] == "take" and st["hexes"][g["hex"]]["holder"] == TOWER))


def tower_now(st):
    T = st["tower"]
    t = tier_now(st)
    out = [f"{tier_name(t)} (tier {t}, Renown {renown_of(st)}) · Hold {T['hold']} of {HOLD}"
           f" · {T['treasury']:,} GP · income {income_of(st, TOWER):,} GP a month"
           f" · Morten level {st['morten']['level']} in {st['morten']['hex']}"]
    out.append(f"Hexes: {' '.join(hexes_of(st, TOWER))} ({st['warded']} warded)")
    mine = sites_of(st, TOWER)
    out.append("Sites: " + ("; ".join(site_line(st, s) for s in mine) if mine else "none"))
    al = [n for n, f in st["realms"].items() if is_ally(f)]
    en = [n for n, f in st["realms"].items() if f["standing"] <= -2]
    out.append(f"Allies: {', '.join(al) or 'none'} · enemies: {', '.join(en) or 'none'}")
    g = T["goal"]
    out.append(f"Goal: {goal_text(st, g)}, {clock_text(g)}" if g else "Goal: none (declare one with --goal)")
    ds = [f"{f['dissident']['name']} ({n}, {f['dissident']['hex']})" for n, f in st["realms"].items() if f.get("dissident")]
    if ds:
        out.append("Dissidents named: " + ", ".join(ds))
    if T.get("won"):
        out.append(f"The world is his (since month {T['won']}).")
    return out


ODDS = {0: "never", 1: "one in six", 2: "one in three", 3: "one in two", 4: "two in three",
        5: "five in six", 6: "certain"}


def roll_odds(st, name):
    """(faces that add a mark, the lowest face that does) for a realm's goal next month."""
    f = st["realms"][name]
    g = f["goal"]
    mod = 0
    t = g["target"]
    if t and t != TOWER:
        o = st["realms"][t]
        mod += 1 if f["force"] > o["force"] else -1 if f["force"] < o["force"] else 0
    aimed = g["hex"] if g["kind"] == "take" else st["warded"] if g["kind"] == "break_tower" else None
    if aimed:
        holder = st["hexes"][aimed]["holder"]
        mod -= bool(site_at(st, aimed, "garrison", holder)) + bool(site_at(st, aimed, "walls", holder))
    faces = [d for d in range(2, 7) if d + mod >= 3]
    return len(faces), (faces[0] if faces else None)


def outlook(st):
    """Next month's lines as (kind, text, realms, hexes) for the report and the rumours."""
    T = st["tower"]
    here = st["morten"]["hex"]
    level = st["morten"]["level"]
    out = []
    for n, f in st["realms"].items():
        g = f["goal"]
        if not aimed_at_tower(st, g):
            continue
        left = g["size"] - g["marks"]
        k, low = roll_odds(st, n)
        if g["waits"]:
            odds = "it is full and waits for nothing"
        elif left <= 1:
            odds = f"a {low} or more does it ({ODDS[k]})" if low else "no roll can add a mark"
        elif left == 2:
            odds = f"a 6 does it at once; a {low} or more adds one ({ODDS[k]})" if low and low <= 6 else "no roll can add a mark"
        else:
            odds = f"a {low} or more adds one ({ODDS[k]})" if low else "no roll can add a mark"
        if g["kind"] == "raid":
            effect = f", and takes up to {min(RAID_GP * f['force'], T['treasury'] // 2):,} GP"
        elif g["kind"] == "break_tower":
            effect = f", and takes a Hold box and half the treasury" if T["hold"] else ", and takes a hex of the tower's"
        else:
            effect = f", and {g['hex']} is theirs"
        out.append(("Threat", f"{who(f)}: *{goal_text(st, g)}* needs {left} mark{'s' if left != 1 else ''};"
                    f" {odds}{effect}.", {n}, {g["hex"]} - {None}))
    tg = T["goal"]
    for n, f in st["realms"].items():
        g = f["goal"]
        if not g or g["waits"]:
            continue
        step = mark_step(st)
        if aimed_at_tower(st, g) and 0 < g["marks"] <= step:
            ss = sites_of(st, n)
            out.append(("Chance", f"a Strike on any of {poss(n)} sites ({', '.join(s['id'] + ' in ' + s['hex'] for s in ss)})"
                        f" empties their *{goal_text(st, g)}* ({clock_text(g)}).", {n}, {s["hex"] for s in ss}))
        elif not aimed_at_tower(st, g) and 0 < g["size"] - g["marks"] <= step and f["standing"] >= -1:
            h = aim_hex(st, n)
            out.append(("Chance", f"an Aid in {h} finishes {poss(n)} *{goal_text(st, g)}* ({clock_text(g)}):"
                        f" {fight_word(st, n, level)}.", {n}, {h}))
    if tg and tg["kind"] == "ally" and tg["size"] - tg["marks"] <= 1:
        f = st["realms"][tg["target"]]
        out.append(("Chance", f"one Contact {the(tg['target'])} (DC {contact_dc(st, tg['target'])}) makes them an ally"
                    f" (*{goal_text(st, tg)}*, {clock_text(tg)}).", {tg["target"]}, set(f["hexes"])))
    for n, f in st["realms"].items():
        for s in sites_of(st, n, kind="works"):
            amt = min(ROB_GP * f["force"], f["treasury"])
            if amt >= ROB_GP * f["force"] and dist(s["hex"], here) <= 2:
                out.append(("Chance", f"{poss(n)} {s['name']} {s['id']} in {s['hex']}: a Rob takes {amt:,} GP"
                            f" ({fight_word(st, s, level)}).", {n}, {s["hex"]}))
    for n, f in st["realms"].items():
        if f["standing"] == 1 and not is_ally(f) and not (tg and tg["target"] == n):
            out.append(("Chance", f"{who(f)} are friendly: an *ally* goal is 3 marks, Contact at DC {contact_dc(st, n)}.",
                        {n}, set(f["hexes"])))
    return out


def open_lines(st):
    T = st["tower"]
    here, level = st["morten"]["hex"], st["morten"]["level"]
    tier = tier_now(st)
    out = [f"Open: Morten is in {hex_label(st, here)}; travel 1 day a hex, a d6 each day outside the tower"
           + (" and its garrisoned hexes" if any(s["kind"] == "garrison" for s in sites_of(st, TOWER)) else "")
           + " (1 = encounter)."]
    ms = []
    for s in sites_of(st, hex=here):
        if s["owner"] == TOWER:
            continue
        ms.append(f"Strike {s['id']} ({s['name']}, {fight_word(st, s, level)})")
        if s["kind"] == "works":
            f = st["realms"][s["owner"]]
            ms.append(f"Rob {s['id']} ({fight_word(st, s, level)}, up to {min(ROB_GP * f['force'], f['treasury']):,} GP)")
    for n, f in st["realms"].items():
        g = f["goal"]
        if g and g["target"] != TOWER and aim_hex(st, n) == here and not g["waits"]:
            ms.append(f"Aid {the(n)} with *{goal_text(st, g)}* ({fight_word(st, n, level)})")
    holder = st["hexes"][here]["holder"]
    if holder != TOWER:
        f = st["realms"][holder]
        if f["standing"] <= -2:
            ms.append(f"Contact {the(holder)}: refused (enemy)")
        else:
            ms.append(f"Contact {the(holder)} (Persuasion DC {contact_dc(st, holder)})")
    ms.append(f"Delve floor {st['hexes'][here]['level']}")
    out.append("Open: missions here: " + " · ".join(ms) + ".")
    acts = [f"works@HEX ({PRICE['works']} GP)"]
    if tier >= LORD:
        acts = [f"garrison@HEX ({PRICE['garrison']} GP)", f"walls@HEX ({PRICE['walls']} GP, needs a garrison)"] + acts
    if T["hold"] < HOLD:
        acts.append(f"mend ({PRICE['mend']} GP)")
    acts.append("give REALM=GP")
    if tier >= WARDEN:
        acts.append(f"back or hinder REALM ({PRICE['back']} GP)")
    if tier >= MASTER:
        acts.append("set an ally's goal")
    out.append(f"Open: the purse ({T['treasury']:,} GP): " + " · ".join(acts) + ".")
    g = T["goal"]
    gs = []
    if not g or g["kind"] != "take":
        gs.append("take HEX (2 + the holder's Force marks, +2 if walled)")
    if not g or g["kind"] != "ally":
        fr = [n for n, f in st["realms"].items() if not is_ally(f)]
        gs.append(f"ally REALM (3 marks; {', '.join(fr) or 'nobody left'})")
    ds = [n for n, f in st["realms"].items() if f.get("dissident")]
    if ds and (not g or g["kind"] != "topple"):
        gs.append(f"topple REALM (3 + Force marks; dissidents in {', '.join(ds)})")
    out.append(("Open: the goal " + (f"stays *{goal_text(st, g)}* ({clock_text(g)}), or drop it for: " if g else "to declare: ")
                + " · ".join(gs) + ".") if gs else f"Open: the goal stays *{goal_text(st, g)}* ({clock_text(g)}).")
    return out


def next_month(st):
    return [f"{k}: {t}" for k, t, _, _ in outlook(st)] + open_lines(st)


def rumours(st, at):
    near = {at, *nbrs(at)}
    realms = {st["hexes"][h]["holder"] for h in near} - {TOWER}
    out = []
    for k, t, rs, hs in outlook(st):
        if rs & realms or hs & near:
            out.append(f"{k}: {t}")
    for n in sorted(realms):
        f = st["realms"][n]
        g = f["goal"]
        out.append(f"{cap(who(f))}, {f['leader']['title']} {f['leader']['name']}: *{goal_text(st, g)}*,"
                   f" {clock_text(g)}; standing {f['standing']:+d} ({standing_word(f['standing'])}).")
    return out


def report(st, t, month):
    """Section 13: the plan, what happened, the tower now, next month."""
    happened = []
    for e in t.happened:
        e = dict(e)
        if e["who"] != TOWER:
            n = e["who"]
            close = (near_morten(st, n) or near_tower(st, n) or is_ally(st["realms"][n])
                     or aimed_at_tower(st, st["realms"][n]["goal"])
                     or (st["tower"]["goal"] and st["tower"]["goal"]["target"] == n))
            e["far"] = bool(e["far"] and not close)
        happened.append(e)
    extra = [x for x in t.log if x.startswith("The tower rises") or x.startswith("The tower falls")
             or x.startswith("The tower is Master")]
    return {"month": month, "plan": list(t.plan), "happened": happened, "tower": tower_now(st),
            "next": next_month(st), "notes": extra}


def happened_lines(rep):
    out, far = [], []
    for e in rep["happened"]:
        if e.get("far"):
            far.append(f"{poss(e['who'])} *{e['goal']}* at {e['marks']} of {e['size']}")
        else:
            out.append(e["text"])
    if far:
        out.append("**Elsewhere:** " + "; ".join(far) + ": nothing moved.")
    out += [f"**{x}**" for x in rep.get("notes", [])]
    return out or ["Nothing happened."]


def reply(st, t, month):
    rep = st["report"]
    out = [f"**Month {month} · The world's turn**", "", "**The plan**"]
    out += [f"- {x}" for x in rep["plan"]]
    out += ["", "**What happened**"] + [f"- {x}" for x in happened_lines(rep)]
    out += ["", "**The tower now**"] + [f"- {x}" for x in rep["tower"]]
    out += ["", "**Next month**"] + [f"- {x}" for x in rep["next"]]
    out += ["", "**Realms**"] + [f"- {realm_line(st, f)}" for f in st["realms"].values()]
    out += ["", "**Income**"] + [f"- {x}" for x in t.income]
    out += ["", "**Log**"] + [f"- {x}" for x in t.log]
    return "\n".join(out) + "\n"


def summary(st, at=None):
    out = [f"**Month {st['month']} · World**", "",
           f"**Morten:** {hex_label(st, st['morten']['hex'])} · level {st['morten']['level']}", "",
           "**The tower**"] + [f"- {x}" for x in tower_now(st)]
    out += ["", "**Realms**"] + [f"- {realm_line(st, f)}" for f in st["realms"].values()]
    out += ["", "**Sites**"] + [f"- {site_line(st, s)}" for s in sites_of(st)]
    out += ["", "**Next month**"] + [f"- {x}" for x in next_month(st)]
    if at:
        out += ["", f"**Rumours** (from {at})"] + [f"- {r}" for r in rumours(st, at) or ["none"]]
    return "\n".join(out) + "\n"


def world_md(st):
    river_of = {}
    for i, r in enumerate(st["rivers"], 1):
        for e in r["edges"]:
            river_of[e] = i
    out = [f"# World · Month {st['month']}", "",
           f"Seed {st['seed']}. Realms v3. Rendered by `realms3.py` from `realms.json` after every"
           " turn; don't edit by hand. Everything here is open: every site, goal and clock.", "",
           "## The tower", ""] + [f"- {x}" for x in tower_now(st)]
    out += ["", "## Realms", ""]
    for f in st["realms"].values():
        out.append(f"- {realm_line(st, f)}")
    out += ["", "## Hexes", ""]
    for h in HEXES:
        x = st["hexes"][h]
        rv = [e for e in sorted(river_of, key=EDGES.index) if h in e.split("|")]
        seat = [n for n, f in st["realms"].items() if f["seat"] == h]
        bits = [f"**{h}**", f"L{x['level']}", x["biome"], x["people"], f"held by {x['holder']}",
                f"{hex_income(st, h)} GP"]
        if seat:
            bits.append(f"seat of the {seat[0]}")
        if h == st["warded"]:
            bits.append("the tower (warded)")
        if x["lake"]:
            bits.append("lake")
        if rv:
            bits.append("river " + ", ".join(rv))
        out += ["- " + " · ".join(bits), f"  - next to: {' '.join(nbrs(h))}"]
        for s in sites_of(st, hex=h):
            out.append(f"  - {site_line(st, s, where=False)}")
    out += ["", "## Rivers", ""]
    for i, r in enumerate(st["rivers"], 1):
        src = "the map's edge" if r["from"] == "edge" else f"the lake in {r['from']}"
        out.append(f"- **River {i}** (from {src}): {' · '.join(r['edges'])}")
    out += ["", "## Sites", "", "| Site | Fight (SRD, by the realm's tier) | Modifier |", "|---|---|---|",
            f"| Seat | {', '.join(SEAT_FIGHT)}, tier +1 (max 3) | the court; a Strike costs standing 2 |",
            "| Garrison | tier 1 " + ", ".join(GARRISON_FIGHT[1]) + " · tier 2 " + ", ".join(GARRISON_FIGHT[2])
            + " · tier 3 " + ", ".join(GARRISON_FIGHT[3]) + " | −1 to goal rolls aimed at the hex |",
            "| Works | " + " · ".join(f"{k}: {', '.join(v)}" for k, v in WORKS_FIGHT.items())
            + f", tier −1 (min 1) | income +{WORKS_INCOME} GP; a Rob takes from it |",
            f"| Walls | {', '.join(WALLS_FIGHT)} | −1 to goal rolls aimed at the hex; a take needs {WALLED_TAKE} marks |"]
    out += ["", "## Goals", "", "| Goal | Clock | When full |", "|---|---|---|",
            "| take HEX | 4 (6 walled) | the hex changes holder with its sites |",
            f"| fortify HEX | 3 | walls at HEX, {PRICE['fortify']} GP |",
            f"| raise | 3 | Force +1, {PRICE['raise']} × the new Force GP |",
            f"| raid REALM | 2 | {RAID_GP} × its Force GP from the target (the tower: at most half) |",
            "| press REALM | 3 | its Force +1, the target's −1 |",
            f"| squeeze | 2 | +{SQUEEZE_GP} GP a hex; Contact DC +{SQUEEZE_DC} for {SQUEEZE_MONTHS} months |",
            "| break REALM | 4 | the target's Force −1 |",
            "| break the tower | 4 | Hold −1 and half the treasury; at Hold 0 a hex |",
            "| court the tower | 2 | standing +1 |"]
    out += ["", "## Last month", ""] + [f"- {x}" for x in st.get("log") or ["The world begins."]]
    out += ["", "## Month", "", f"- **Next world's turn:** month {st['month']}", ""]
    return "\n".join(out)


def goal_json(st, g):
    if not g:
        return None
    return {"text": goal_text(st, g), "kind": g["kind"], "target": g["target"], "hex": g["hex"],
            "marks": g["marks"], "size": g["size"], "waits": g.get("waits", 0), "since": g.get("since")}


def map_json(st, campaign):
    T = st["tower"]
    river_of = [e.split("|") for r in st["rivers"] for e in r["edges"]]
    hexes = []
    for h in HEXES:
        x = st["hexes"][h]
        c, r = hkey(h)
        seat = next((n for n, f in st["realms"].items() if f["seat"] == h), TOWER if h == st["warded"] else None)
        assets = [{"id": s["id"], "owner": s["owner"], "name": s["name"], "type": s["kind"],
                   "tier": site_tier(st, s)} for s in sites_of(st, hex=h)]
        hexes.append({"id": h, "col": c, "row": r - 1, "level": x["level"], "biome": x["biome"],
                      "people": x["people"], "holder": x["holder"], "lake": x["lake"],
                      "seat_of": seat, "warded": h == st["warded"], "income": hex_income(st, h),
                      "neighbours": nbrs(h), "assets": assets})
    facs = []
    for n, f in st["realms"].items():
        L = f["leader"]
        facs.append({"name": n, "tower": False,
                     "leader": {"name": L["name"], "title": L["title"], "label": L["label"],
                                "tag": L["tag"], "verb": VERB[L["tag"]]},
                     "income": income_of(st, n), "force": f["force"], "tier": tier_of(f["force"]),
                     "treasury": f["treasury"], "seat": f["seat"], "hexes": hexes_of(st, n),
                     "standing": f["standing"], "standingWord": standing_word(f["standing"]),
                     "ally": is_ally(f), "goal": goal_json(st, f["goal"]),
                     "dissident": f["dissident"], "squeezed": bool(f["squeeze_until"] and st["month"] <= f["squeeze_until"])})
    t = tier_now(st)
    facs.append({"name": TOWER, "tower": True,
                 "leader": {"name": "Morten", "title": "Wizard", "label": None, "tag": None, "verb": None},
                 "income": income_of(st, TOWER), "treasury": T["treasury"], "seat": st["warded"],
                 "hexes": hexes_of(st, TOWER), "standing": None, "standingWord": None, "ally": False,
                 "goal": goal_json(st, T["goal"]), "tier": t, "tierName": tier_name(t),
                 "renown": renown_of(st), "hold": T["hold"], "maxHold": HOLD, "toppled": T["toppled"],
                 "won": T.get("won")})
    rep = st.get("report") or {}
    return {"version": VERSION, "campaign": campaign, "month": st["month"],
            "layout": {"cols": 4, "rows": 5, "orientation": "flat-top", "shift": "odd"},
            "hexes": hexes, "rivers": river_of, "factions": facs,
            "morten": {"hex": st["morten"]["hex"], "level": st["morten"]["level"]},
            "events": st.get("events", []),
            "report": {"month": rep.get("month", 0), "plan": rep.get("plan", []),
                       "happened": [{k: e.get(k) for k in ("who", "label", "goal", "roll", "marks", "size",
                                                           "fired", "far", "waits", "new", "text")}
                                    for e in rep.get("happened", [])],
                       "tower": rep.get("tower", []), "next": rep.get("next", []),
                       "notes": rep.get("notes", [])}}


# ---- Commands ----

def load(d):
    p = Path(d) / "realms.json"
    if not p.exists():
        raise Bad(f"no {p}; run new first")
    st = json.loads(p.read_text())
    v = st.get("version")
    if v != VERSION:
        raise Bad(f"{p} is a Realms v{v} world; play it with "
                  + ("dnd-crunch/tools/realms_v1.py" if v == 1 else "dnd-crunch/tools/realms.py")
                  + ", or start a v3 world with new")
    return st


def save(d, st):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    sync(st)
    (d / "realms.json").write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n")
    (d / "world.md").write_text(world_md(st))
    (d / "map.json").write_text(json.dumps(map_json(st, d.name), indent=1, ensure_ascii=False) + "\n")


def cmd_new(a):
    d = Path(a.campaign)
    if (d / "realms.json").exists() and not a.force:
        raise Bad(f"{d / 'realms.json'} exists; use --force to overwrite")
    st = generate(a.seed, a.level)
    st["report"] = {"month": 0, "plan": [], "happened": [], "tower": tower_now(st),
                    "next": next_month(st), "notes": ["Month 1: the world begins."]}
    save(d, st)
    rng, mons = random.Random(a.seed), load_monsters()
    out = ["# GM secrets · dungeon floors", "",
           f"Floor N lies under the level-N hex (seed {a.seed}, the same floors as"
           f" `gen_dungeon.py --seed {a.seed}`). Mark rooms explored as Morten reaches them."
           " The overworld hides nothing: `realms3.py show` is the whole of it.", ""]
    by_level = {x["level"]: h for h, x in st["hexes"].items()}
    for level in range(1, 21):
        need, total, encs = floor(level, mons, rng)
        h = by_level[level]
        out.append(floor_md(level, need, total, encs,
                            f"Floor {level} · {h} ({st['hexes'][h]['biome']},"
                            f" {st['hexes'][h]['holder']})"))
    (d / "gm-secrets.md").write_text("\n".join(out))
    print(summary(st))
    print(f"Wrote {d / 'realms.json'}, {d / 'world.md'}, {d / 'map.json'}, {d / 'gm-secrets.md'}.")


def cmd_show(a):
    st = load(a.campaign)
    at = a.at.upper() if a.at else None
    if at and at not in st["hexes"]:
        raise Bad(f"no hex '{a.at}' (A1–D5)")
    print(summary(st, at), end="")


def cmd_encounter(a):
    st = load(a.campaign)
    level = a.level or st["morten"]["level"]
    t = Turn(st)
    if a.site:
        s = t.site(a.site)
        if s["owner"] == TOWER:
            raise Bad(f"{s['id']} is the tower's own {s['name']}: nothing to fight")
        print("\n".join(fight_lines(st, s, level)))
        f = st["realms"][s["owner"]]
        n = mark_step(st)
        win = f"- Win: Strike takes {n} marks off {poss(s['owner'])} goal; standing −{2 if s['kind'] == 'seat' else 1}"
        if s["kind"] == "works":
            win += f" · Rob: {min(ROB_GP * f['force'], f['treasury']):,} GP from {the(s['owner'])}; standing −1"
        print(win)
        return
    if a.aid:
        name = t.realm(a.aid)
        f = st["realms"][name]
        if not f["goal"]:
            raise Bad(f"{the(name)} have no goal to aid")
        if f["goal"]["target"] == TOWER:
            raise Bad(f"{poss(name)} goal is {goal_text(st, f['goal'])}: the tower can't aid that")
        print("\n".join(fight_lines(st, name, level)))
        print(f"- Win: {mark_step(st)} marks on {poss(name)} {goal_text(st, f['goal'])}"
              f" ({clock_text(f['goal'])}); standing +1 (to at most +1)")
        return
    if a.contact:
        name = t.realm(a.contact)
        f = st["realms"][name]
        if f["standing"] <= -2:
            print(f"**Contact {the(name)}**: refused, they are enemies (standing −2).")
            return
        bits = [f"{CONTACT_DC}"]
        if f["leader"]["label"] == "bad":
            bits.append(f"+ {CONTACT_BAD} bad ruler")
        if f["standing"]:
            bits.append(f"− 2 × standing {f['standing']:+d}")
        if f["squeeze_until"] and st["month"] <= f["squeeze_until"]:
            bits.append(f"+ {SQUEEZE_DC} squeezed")
        print(f"**Contact {the(name)}** in any of {' '.join(f['hexes'])}: Persuasion (CHA) DC"
              f" {contact_dc(st, name)} ({' '.join(bits)}). Win: standing +1 (to at most +1);"
              f" at +1 a dissident is named.")
        return
    if not a.hex:
        raise Bad("encounter needs --site, --aid, --contact or --hex")
    h = t.hexarg(a.hex)
    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(10 ** 6)
    e = encounter(st["hexes"][h]["level"], random.Random(seed))
    print(f"**Wandering encounter · {hex_label(st, h)}** (seed {seed})\n")
    print(f"- {e['count']}× {e['name']} · CR {e['cr']} · {e['xp']:,} XP each")
    print(f"- {e['total']:,} XP total · {e['diff']} · coins {e['total'] // 10:,} GP")


def cmd_turn(a):
    st = load(a.campaign)
    t = Turn(st)
    month = t.run(a)
    st["report"] = report(st, t, month)
    print(reply(st, t, month), end="")
    if a.dry_run:
        print("\n(dry run: nothing saved)")
    else:
        save(a.campaign, st)


# ---- The sim (section 16) ----

def scripted_orders(st, month):
    """A scripted Morten: Strike the weakest neighbour's garrison every month, then its seat,
    with the tower's goal on that hex; the purse mends Hold when it can."""
    o = argparse.Namespace(**PASSIVE)
    o.buy, o.give, o.plan, o.set = [], [], [], []
    T = st["tower"]
    o.level = 3 if month <= 12 else 4
    g = T["goal"]
    target_hex = None
    if g and g["kind"] == "take":
        target_hex = g["hex"]
    else:
        mine = set(hexes_of(st, TOWER))
        ns = sorted({st["hexes"][n]["holder"] for h in mine for n in nbrs(h)} - {TOWER})
        ns = [n for n in ns if st["realms"][n]["hexes"]]
        if not ns:
            return o
        weak = min(ns, key=lambda n: (st["realms"][n]["force"], n))
        f = st["realms"][weak]
        gar = sites_of(st, weak, kind="garrison")
        target_hex = gar[0]["hex"] if gar else f["seat"]
        o.goal = f"take:{target_hex}"
    if not target_hex:
        return o
    o.at = target_hex
    holder = st["hexes"][target_hex]["holder"]
    ss = sites_of(st, holder, target_hex)
    pick = next((s for s in ss if s["kind"] == "garrison"), None) or next((s for s in ss if s["kind"] == "seat"), None) \
        or (ss[0] if ss else None)
    if pick:
        o.strike = pick["id"]
    if T["hold"] < HOLD and T["treasury"] >= PRICE["mend"]:
        o.buy.append("mend")
    return o


def sim_one(seed, months, scripted=False, verbose=False):
    st = generate(seed)
    stats = Counter()
    start = {n: (f["leader"]["tag"], len(f["hexes"]), f["force"], f["seat"]) for n, f in st["realms"].items()}
    fired_months = []
    last_line, streak, longest = {}, Counter(), Counter()
    rich_months = Counter()
    maxgp = Counter()
    break_picked = 0
    first_hex, tier_at = None, {}
    for m in range(1, months + 1):
        o = scripted_orders(st, m) if scripted else argparse.Namespace(**PASSIVE)
        t = Turn(st)
        try:
            month = t.run(o)
        except Bad as e:
            raise SystemExit(f"sim seed {seed} month {m}: {e}")
        st["report"] = report(st, t, month)
        stats += t.stats
        fired_months.append(t.stats["fired"] + t.stats["tower_took"] + t.stats["allied"] + t.stats["toppled"])
        break_picked += sum(1 for x in t.log if "break the tower (clock" in x)
        for n, f in st["realms"].items():
            g = f["goal"]
            line = (goal_text(st, g), g["marks"]) if g else None
            if last_line.get(n) == line:
                streak[n] += 1
            else:
                streak[n] = 1
            longest[n] = max(longest[n], streak[n])
            last_line[n] = line
            if f["treasury"] >= 2000:
                rich_months[n] += 1
            maxgp[n] = max(maxgp[n], f["treasury"])
        if scripted:
            if first_hex is None and len(hexes_of(st, TOWER)) > 1:
                first_hex = m
            if m in (12, 24, 36):
                tier_at[m] = (tier_now(st), renown_of(st), len(hexes_of(st, TOWER)) - 1)
                stats[f"renown_{m}"] += renown_of(st)
        if verbose:
            print(reply(st, t, month))
    end = {n: (f["leader"]["tag"], len(f["hexes"]), f["force"], f["seat"], f["treasury"], f["standing"])
           for n, f in st["realms"].items()}
    return dict(st=st, stats=stats, start=start, end=end, fired_months=fired_months,
                longest=longest, rich_months=rich_months, maxgp=maxgp, break_picked=break_picked,
                first_hex=first_hex, tier_at=tier_at)


def sim_many(seeds, months, scripted=False, verbose=False):
    """The sim's numbers against section 16's targets: a dict of totals and per-seed rows."""
    tot = Counter()
    rows, conq, stew = [], [], []
    out = dict(seeds=list(seeds), months=months, scripted=scripted, quiet_months=0, long_lines=0,
               landless=0, to_five=0, hexes_moved=[], rich_worlds=0, first_hexes=[],
               tiers=Counter(), break_picked=0, ends=[])
    for s in seeds:
        r = sim_one(s, months, scripted, verbose)
        st, stats = r["st"], r["stats"]
        tot += stats
        T = st["tower"]
        quiet = sum(1 for k in r["fired_months"] if k == 0)
        out["quiet_months"] += quiet
        out["long_lines"] += sum(1 for n, k in r["longest"].items() if k >= 12)
        for n, (tag, h0, f0, seat0) in r["start"].items():
            tag1, h1, f1, seat1, gp, standing = r["end"][n]
            if tag == "Conqueror":
                conq.append((h0, h1))
            if tag == "Steward":
                stew.append(seat1 == seat0)
            if h1 == 0:
                out["landless"] += 1
            if f0 == 1 and f1 == 5:
                out["to_five"] += 1
        moved = stats["hexes_taken"] + stats["tower_took"]
        out["hexes_moved"].append(moved)
        rich = max(r["rich_months"].values(), default=0)
        out["rich_worlds"] += rich >= 12
        out["break_picked"] += r["break_picked"]
        out["first_hexes"].append(r["first_hex"])
        for m, (t, rn, hx) in r["tier_at"].items():
            out["tiers"][(m, t)] += 1
        out["ends"].append(r)
        rows.append(f"seed {s:>3}: fired {stats['fired']} ({quiet} quiet months) · hexes moved {moved}"
                    f" · raids {stats['raids']} for {stats['raid_gp']:,} GP · waits {stats['waits']}"
                    f" ({stats['wait_months']} months) · break the tower picked {r['break_picked']},"
                    f" fired {stats['tower_broken']} · tower Hold {T['hold']}, hexes lost {stats['tower_lost']},"
                    f" {T['treasury']:,} GP · richest {max(r['maxgp'].values()):,} GP ({rich} months at 2,000+)"
                    + (f" · first hex month {r['first_hex']} · tier {tier_now(st)} Renown {renown_of(st)}"
                       f" ({len(hexes_of(st, TOWER)) - 1} hexes, {stats['toppled']} toppled)" if scripted else ""))
    out.update(tot=tot, rows=rows, conq=conq, stew=stew)
    return out


def sim_lines(S):
    tot, n, M = S["tot"], len(S["seeds"]), S["months"]
    out = [f"=== {n} seeds × {M} months ({'scripted Morten' if S['scripted'] else 'passive tower'}) ===",
           f"Goals fired: {tot['fired'] / n:.1f} a world ({tot['fired'] / n / M:.2f} a month) · months with"
           f" nothing fired {S['quiet_months']} of {n * M} · realm lines unchanged 12+ months: {S['long_lines']}"
           f" · goals dropped {tot['goal_drop'] / n:.1f} a world ({tot['drop_time'] / n:.1f} timed out,"
           f" {tot['drop_gone'] / n:.1f} lost their target)",
           f"Hexes changed hands: {sum(S['hexes_moved']) / n:.1f} a world ({', '.join(map(str, S['hexes_moved']))})"
           f" · Conquerors start → end hexes: {', '.join(f'{x}→{y}' for x, y in S['conq'])}"
           f" · Stewards holding their seat: {sum(S['stew'])} of {len(S['stew'])}",
           f"Realms landless at the end: {S['landless']} · Force 1 → 5: {S['to_five']} · raises {tot['raises'] / n:.1f}"
           f" · presses {tot['fired_press'] / n:.1f} · breaks {tot['fired_break'] / n:.1f} a world",
           f"Tower: break the tower picked {S['break_picked']} times ({S['break_picked'] / n:.1f} a world), fired"
           f" {tot['tower_broken']} ({tot['tower_broken'] / n:.1f} a world) · Hold boxes lost"
           f" {tot['hold_lost'] / n:.1f} a world · hexes lost {tot['tower_lost']} · raided {tot['tower_raided']} times",
           f"Treasuries: raids {tot['raids'] / n:.1f} a world moving {tot['raid_gp'] / n:,.0f} GP · fortify and raise"
           f" paid {tot['paid'] / n:,.0f} GP a world · goals that waited {tot['waits'] / n:.1f} a world for"
           f" {tot['wait_months'] / max(1, tot['waits']):.1f} months each · worlds with a realm at 2,000+ GP for a year: {S['rich_worlds']}"]
    if S["scripted"]:
        fh = [x for x in S["first_hexes"] if x]
        tiers = S["tiers"]
        out.append(f"Scripted Morten: first hex in {', '.join(str(x) for x in S['first_hexes'])} months"
                   f" (mean {sum(fh) / max(1, len(fh)):.1f}) · tier at month 12/24/36: "
                   + " · ".join(f"m{m}: " + ", ".join(f"{tiers[(m, t)]}× {tier_name(t)}" for t in range(5) if tiers[(m, t)])
                                for m in (12, 24, 36) if any(tiers[(m, t)] for t in range(5)))
                   + " · mean Renown at 12/24/36: " + "/".join(f"{tot[f'renown_{m}'] / n:.1f}" for m in (12, 24, 36) if tot[f"renown_{m}"])
                   + f" · hexes the tower lost back {tot['tower_lost'] / n:.1f} a world")
    return out


def cmd_sim(a):
    if a.seed is not None:
        seeds = [a.seed]
    else:
        lo, _, hi = a.seeds.partition("-")
        seeds = list(range(int(lo), int(hi or lo) + 1))
    S = sim_many(seeds, a.months, a.scripted, a.verbose)
    if a.seed is not None:
        r = S["ends"][0]
        print("End:")
        for n, (tag, h, f, seat, gp, standing) in r["end"].items():
            print(f"  {n:<10} {tag:<10} hexes {h} (was {r['start'][n][1]}) · Force {f} (was {r['start'][n][2]})"
                  f" · {gp:,} GP · standing {standing:+d} · longest quiet line {r['longest'][n]} months")
        print()
    print("\n".join(S["rows"]))
    print()
    print("\n".join(sim_lines(S)))


def main():
    ap = argparse.ArgumentParser(description="Realms v3 overworld engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--campaign", required=True)
    p.add_argument("--level", type=int, default=3, help="Morten's level")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("show")
    p.add_argument("--campaign", required=True)
    p.add_argument("--at", help="HEX: the rumours from there")
    p = sub.add_parser("encounter")
    p.add_argument("--campaign", required=True)
    p.add_argument("--site", help="a site id (s7): the fight for a Strike or Rob")
    p.add_argument("--aid", help="REALM: the fight for an Aid")
    p.add_argument("--contact", help="REALM: the Contact DC")
    p.add_argument("--hex", help="a wandering encounter for the hex's level")
    p.add_argument("--level", type=int, help="Morten's level (default: the campaign's)")
    p.add_argument("--seed", type=int)
    p = sub.add_parser("turn")
    p.add_argument("--campaign", required=True)
    p.add_argument("--at", help="Morten's hex at the end of his month")
    p.add_argument("--level", type=int, help="Morten's level now")
    p.add_argument("--strike", help="site id (a won Strike)")
    p.add_argument("--rob", help="site id of a works (a won Rob)")
    p.add_argument("--aid", help="REALM (a won Aid)")
    p.add_argument("--contact", help="REALM (a won Contact)")
    p.add_argument("--delve", action="store_true", help="Morten delved this month")
    p.add_argument("--goal", help="take:HEX, ally:REALM, topple:REALM or drop (kept when omitted)")
    p.add_argument("--buy", action="append", default=[], help="garrison@HEX, walls@HEX, works@HEX, mend (repeatable)")
    p.add_argument("--give", action="append", default=[], help="REALM=GP (repeatable)")
    p.add_argument("--back", help="REALM: +1 on its roll (Warden, 100 GP)")
    p.add_argument("--hinder", help="REALM: −1 on its roll (Warden, 100 GP)")
    p.add_argument("--set", action="append", default=[], help="REALM=GOAL: set an ally's goal (Master)")
    p.add_argument("--deposit", type=int, default=0)
    p.add_argument("--withdraw", type=int, default=0)
    p.add_argument("--plan", action="append", default=[], help="a line for The plan: why")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("sim")
    p.add_argument("--seeds", default="1-10")
    p.add_argument("--seed", type=int)
    p.add_argument("--months", type=int, default=24)
    p.add_argument("--scripted", action="store_true", help="a scripted Morten strikes the weakest neighbour")
    p.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    check_fights()
    try:
        {"new": cmd_new, "show": cmd_show, "encounter": cmd_encounter, "turn": cmd_turn,
         "sim": cmd_sim}[a.cmd](a)
    except Bad as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
