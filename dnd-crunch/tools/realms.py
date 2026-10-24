#!/usr/bin/env python3
"""Realms v2: the overworld engine for D&D Crunch (rules: dnd-crunch/realms.md).

A 4×5 hex map of six realms and Morten's tower, played as monthly domain turns. Every realm
and the tower is a faction (Force, Cunning, Wealth, HP, treasury, seat) with assets on the
map, after the faction rules of Worlds/Stars Without Number. realms.json is the state and
this script owns it; world.md (open) and map.json (the tower's view, for the map page) are
written from it after every change. Realms v1 worlds are refused: play them with
realms_v1.py.

Usage:
  python3 dnd-crunch/tools/realms.py new --seed 7 --campaign DIR [--level 4] [--force]
  python3 dnd-crunch/tools/realms.py show --campaign DIR [--at C3] [--gm]
  python3 dnd-crunch/tools/realms.py encounter --campaign DIR (--asset a7 | --asset Orcs
      | --hex C3 [--seed N] | --contact C3)
  python3 dnd-crunch/tools/realms.py turn --campaign DIR [--at HEX] [--level N]
      [--strike a7|REALM | --rob a7 | --contact | --delve] [--keep-loot]
      [--deposit GP] [--withdraw GP] [--give REALM=GP]
      [--action buy:militia[@HEX] | raise:force | repair:a7 | repair:tower
                | move:a7>B3[,a8>C4] | attack:a7>a3[,a8>a3] | attack:a12>Orcs | seize:B3]
      [--plan "why"] [--gm] [--dry-run]
  python3 dnd-crunch/tools/realms.py sim [--seeds 1-10] [--months 24] [--seed N --verbose]
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

VERSION = 2

# ---- Constants (realms.md section 10). Change both together. ----
COLS, ROWS = "ABCD", 5
N_REALMS, REALM_SIZE, N_BAD = 6, 3, 4
N_RIVERS, RIVER_LEN, N_LAKES = 2, (3, 6), 2
INCOME = 10            # GP per hex level per month
TYRANT_INCOME = 1.5    # a Tyrant's hex income multiplier
HP_BASE = 4            # faction HP = HP_BASE + HP_BONUS[rating] for each attribute
HP_BONUS = [0, 1, 2, 4, 6, 9, 12, 16, 20]
RAISE = [0, 0] + [b * 100 for b in HP_BONUS[2:]]   # raise to rating N: HP_BONUS[N] × 100 GP
MAX_RATING = 8
DIE = 10               # attack roll: d10 + attribute vs d10 + attribute; a tie hurts both
RIVER, CLAIM, WALLS = 1, 1, 1
SEAT_COUNTER = "1d4"   # what an attack on a seat takes back when the defence wins
OVER_LIMIT = 100       # GP a month per asset of a type beyond the matching attribute
REPAIR_DIV = 4         # repair an asset fully for a quarter of its cost
REPAIR_HP, REPAIR_HP_GP = "1d6", 100   # faction Repair: 1d6 HP for 100 GP
STRIKE = "2d6"         # Morten's Strike: damage to the asset, or to HP at an unguarded seat
ROB, ROB_GP, ROB_TREASURY = "1d6", 100, 2   # Rob: 1d6 to the asset, tier × 100 GP (× 2)
CONTACT_DC, TYRANT_CONTACT = 10, 4          # Contact: DC 10 + ruler's Cunning (−4 Tyrant)
HOSTILE, HOSTILE_SEAT = 3, 6                # months of "punish the tower"
RAID_SEAT_GP = 200     # a Raider's win on a seat takes this much
SEAT_SEIZED = "1d6"    # HP a faction loses when its seat hex is seized
DISORDER = 1           # months with no action after a fall with no dissident
GOAL_MONTHS = 6        # a goal not done in this many months is dropped
ARMY_EXTRA = ("mercenaries", "saboteurs", "assassins")   # march with the Force assets
HEX_LOST = "1d4"       # HP a faction loses with a hex seized from it (its seat: SEAT_SEIZED)
CONQUER_GUARD = 5      # a Conqueror counts each defender's Force asset near a hex as −5 levels
ARMY_MIN = 2           # the AI buys before it marches while its army is smaller than this
RICH = 1200            # a realm with this much gold buys or raises before its goal
RICH_RESERVE = 0       # what a rich realm keeps back when it buys over its limits
REST = 3               # months a faction leaves alone a faction it just did a goal against
GOAL_XP = {"seize": 2, "break": 1, "raid": 1, "buy": 1, "raise": 0}   # XP for a goal done;
# a faction spends XP on the goal's attribute when it has the new rating's HP_BONUS in XP
START_DIV, START_GP = 10, 10   # realm attributes S ÷ 10 (rounded, min 1), treasury S × 10
START_ASSETS = {"Force": 2, "Cunning": 1, "Wealth": 1}
TOWER_START = dict(force=1, cunning=1, wealth=1, gp=100)
FIGHT_MAX = 4          # most monsters in a mission fight
ATTRS = {"F": "force", "C": "cunning", "W": "wealth"}
TYPE_ATTR = {"Force": "force", "Cunning": "cunning", "Wealth": "wealth"}

# ---- Assets (realms.md section 4). Fight: SRD monsters, picked to the tier's budget. ----
# book: the WWN/SWN entry it is refitted from (cost × 100 GP, HP, attack, counter).


def _a(name, typ, tier, needs, cost, hp, atk, ctr, fight, book, income=0, upkeep=0, move=1,
       special="", land=None):
    return dict(name=name, type=typ, tier=tier, needs=needs, cost=cost, hp=hp, atk=atk, ctr=ctr,
                fight=fight, book=book, income=income, upkeep=upkeep, move=move,
                special=special, land=land)


ASSETS = {
    "thugs": _a("Thugs", "Force", 1, 1, 200, 3, ("F", "F", "1d3+1"), "1d4",
                ["Bandit", "Tough", "Tough Boss"], "Security Personnel (F1: 2, HP 3)"),
    "militia": _a("Militia", "Force", 1, 1, 400, 4, ("F", "F", "1d6"), "1d4+1",
                  ["Guard", "Scout", "Guard Captain"], "Militia Unit (F1: 4, HP 4)"),
    "beasts": _a("Beast pack", "Force", 2, 2, 500, 5, ("F", "F", "2d4"), "1d4+1",
                 None, "Elite Skirmishers (F2)", special="the people's beasts"),
    "walls": _a("Walls", "Force", 2, 3, 600, 10, None, "1d6",
                ["Animated Armor", "Guard", "Gargoyle"], "ours (≈ Hardened Personnel)", move=0,
                special="can't move; +1 to its owner's defence in its hex; the hex can't be seized"),
    "knights": _a("Knights", "Force", 3, 4, 800, 12, ("F", "F", "1d8"), "1d8",
                  ["Knight", "Warrior Veteran", "Warhorse"], "Postech Infantry (F4)",
                  upkeep=100, special="upkeep 100"),
    "warband": _a("Warband", "Force", 3, 6, 1600, 16, ("F", "F", "2d8"), "2d6",
                  ["Berserker", "Warrior Veteran", "Gladiator", "Ogre"],
                  "≈ Pretech Infantry (F6)", upkeep=200, special="upkeep 200"),
    "informers": _a("Informers", "Cunning", 1, 1, 200, 3, None, None,
                    ["Spy", "Bandit", "Noble"], "Informers (C1: 2, HP 3)",
                    special="its owner sees every asset in its hex"),
    "smugglers": _a("Smugglers", "Cunning", 1, 1, 200, 4, ("C", "W", "1d4"), None,
                    ["Bandit", "Pirate", "Bandit Captain"], "Smugglers (C1: 2, HP 4, C vs W 1d4)",
                    income=50, move=2, special="income +50; moves 2 hexes"),
    "saboteurs": _a("Saboteurs", "Cunning", 2, 2, 500, 6, ("C", "C", "2d4"), None,
                    ["Tough", "Spy", "Scout"], "Saboteurs (C2: 5, HP 6, C vs C 2d4)"),
    "seditionists": _a("Seditionists", "Cunning", 2, 2, 600, 6, ("C", "C", "1d6"), None,
                       ["Cultist", "Cultist Fanatic"], "Seditionists (C4: 12, HP 8), refitted",
                       special="coup: attacks the realm's HP from any of its hexes; bought only "
                               "after a Contact; led by the dissident"),
    "assassins": _a("Assassins", "Cunning", 3, 3, 600, 4, ("C", "C", "2d6"), None,
                    ["Spy", "Assassin"], "Cyberninjas (C3: 6, HP 4, C vs C 2d6)",
                    special="a win also does 1d4 to the target faction's HP"),
    "court_mage": _a("Court mage", "Cunning", 3, 5, 1000, 6, ("C", "C", "1d8"), "1d6",
                     ["Mage", "Cultist Fanatic", "Guard", "Imp"], "ours", move=0,
                     special="once a month cancels an attack on its owner's asset in its hex "
                             "(C vs C)"),
    "farms": _a("Farms", "Wealth", 1, 1, 200, 4, None, "1d4",
                ["Guard", "Mastiff", "Scout"], "Harvesters (W1: 2, HP 4)", income=50, move=0,
                special="income +50"),
    "caravans": _a("Caravans", "Wealth", 1, 2, 400, 4, ("W", "W", "1d4"), "1d4-1",
                   ["Guard", "Scout", "Warrior Veteran", "Mastiff"],
                   "Franchise (W1: 2, HP 3, W vs W 1d4)", income=100, move=2,
                   special="income +100; moves 2 hexes"),
    "mine": _a("Mine", "Wealth", 2, 3, 800, 4, None, "1d4",
               ["Tough", "Guard", "Tough Boss"], "Postech Industry (W3: 8, HP 4)", income=150,
               move=0, special="income +150; hills or mountains only",
               land=("hills", "mountains")),
    "mercenaries": _a("Mercenaries", "Wealth", 2, 3, 800, 6, ("W", "F", "2d4+2"), "1d6",
                      ["Warrior Veteran", "Berserker", "Bandit Captain", "Tough"],
                      "Mercenaries (W3)", upkeep=100, special="upkeep 100"),
    "treasury": _a("Treasury", "Wealth", 3, 4, 1200, 8, None, "1d6",
                   ["Guard Captain", "Animated Armor", "Guard"], "≈ Bank (W4)", income=100,
                   move=0, special="income +100; a Rob here takes double"),
    "toll_road": _a("Toll road", "Wealth", 3, 5, 1000, 8, ("W", "W", "1d6"), None,
                    ["Knight", "Warrior Veteran", "Scout", "Guard"], "≈ Marketers (W5: 10, HP 8)",
                    income=250, move=0, special="income +250"),
}
BEASTS = {"Humans": ["Mastiff", "Warhorse", "Scout"],
          "Elves": ["Giant Owl", "Giant Eagle", "Giant Elk"],
          "Orcs": ["Worg", "Dire Wolf", "Giant Boar"],
          "Gnomes": ["Giant Badger", "Giant Goat", "Brown Bear"],
          "Tieflings": ["Imp", "Hell Hound"],
          "Goblinkind": ["Giant Hyena", "Worg", "Gnoll Warrior"],
          "tower folk": ["Mastiff", "Giant Owl", "Brown Bear"]}
SEAT_FIGHT = ["Noble", "Spy", "Tough", "Guard", "Knight", "Guard Captain"]   # a seat with no Force asset
SEAT_TIER = 3

BIOMES = {1: ["tundra", "taiga", "mountains"],
          2: ["taiga", "hills", "mountains", "forest"],
          3: ["forest", "plains", "hills", "swamp"],
          4: ["plains", "forest", "swamp", "hills", "savanna"],
          5: ["desert", "savanna", "jungle", "mountains"]}
BAD = ["Conqueror", "Raider", "Slaver", "Tyrant"]
GOOD = ["Steward", "Liberator"]
VERB = {"Conqueror": "takes land", "Raider": "robs its neighbours",
        "Slaver": "takes people for soldiers", "Tyrant": "squeezes its own people",
        "Steward": "keeps the peace", "Liberator": "fights tyrants", "Tower": "Morten's word"}
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
    """Every Fight monster must be an SRD file."""
    names = {m for a in ASSETS.values() for m in a["fight"] or []}
    names |= {m for v in BEASTS.values() for m in v} | set(SEAT_FIGHT)
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


# ---- Map (as v1) ----

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


def step_toward(a, b, rng):
    """The next hex on a shortest path from a to b."""
    if a == b:
        return a
    d = dist(a, b)
    return rng.choice([n for n in nbrs(a) if dist(n, b) == d - 1])


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

def max_hp(f):
    return HP_BASE + sum(HP_BONUS[f[a]] for a in ("force", "cunning", "wealth"))


def people_of(name):
    return TOWER_FOLK if name == TOWER else name


def hexes_of(st, name):
    return [h for h in HEXES if st["hexes"][h]["holder"] == name]


def assets_of(st, name=None, hex=None, typ=None):
    return [a for a in sorted(st["assets"].values(), key=lambda a: int(a["id"][1:]))
            if (name is None or a["owner"] == name) and (hex is None or a["hex"] == hex)
            and (typ is None or ASSETS[a["kind"]]["type"] == typ)]


def info(a):
    return ASSETS[a["kind"]]


def max_ahp(a):
    return info(a)["hp"]


def poss(name):
    return "the tower's" if name == TOWER else f"{name}'"  if name.endswith("s") else f"{name}'s"


def aname(a):
    return f"{poss(a['owner'])} {info(a)['name']} {a['id']}"


def label(f):
    L = f["leader"]
    return f"{L['label']}: {VERB[L['tag']]}"


def who(f):
    L = f["leader"]
    if f["tower"]:
        return "Tower (Morten)"
    return f"{f['name']} ({L['title']} {L['name']}, {label(f)})"


def hex_income(st, h):
    x = st["hexes"][h]
    f = st["factions"].get(x["holder"])
    mult = TYRANT_INCOME if f and f["leader"]["tag"] == "Tyrant" else 1
    if occupied(st, h):
        return 0
    return int(x["level"] * INCOME * mult)


def occupied(st, h):
    """A hex with another faction's Force asset in it pays its holder nothing."""
    holder = st["hexes"][h]["holder"]
    return any(a["hex"] == h and a["owner"] != holder and ASSETS[a["kind"]]["type"] == "Force"
               for a in st["assets"].values())


def is_ally(f):
    return not f["tower"] and f["leader"]["label"] == "good" and not f["hostile"]


def tower_sees(st):
    """Hexes where the tower sees Cunning assets: its Informers' hexes and Morten's."""
    return {a["hex"] for a in assets_of(st, TOWER, typ="Cunning")
            if a["kind"] == "informers"} | {st["morten"]}


def visible(st, a, sees=None):
    if a["owner"] == TOWER or info(a)["type"] != "Cunning" or a.get("seen"):
        return True
    return a["hex"] in (sees if sees is not None else tower_sees(st))


def known_to(st, name, a):
    """Can realm name see asset a? The realms know each other's assets; the tower's Cunning
    assets only once they have attacked, or where name has Informers."""
    if a["owner"] != TOWER or ASSETS[a["kind"]]["type"] != "Cunning" or a.get("exposed"):
        return True
    return any(x["kind"] == "informers" and x["hex"] == a["hex"] for x in assets_of(st, name))


def kind_of(s):
    k = s.strip().lower().replace(" ", "_").replace("-", "_")
    for key, a in ASSETS.items():
        if k in (key, a["name"].lower().replace(" ", "_")):
            return key
    raise Bad(f"no asset kind '{s}' (kinds: {', '.join(ASSETS)})")


def goal_text(st, f):
    if f["disorder"]:
        return f"none: in disorder ({f['disorder']} month{'s' if f['disorder'] > 1 else ''})"
    if f["tower"]:
        return None
    if f["hostile"]:
        return f"punish the tower ({f['hostile']} month{'s' if f['hostile'] > 1 else ''} left)"
    if f["hp"] * 2 < max_hp(f):
        return "recover (Repair: below half HP)"
    g = f["goal"]
    if not g:
        return None
    k = st["month"] - g["since"] + 1
    return f"{g['text']} (month {k} of it)"


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


def add_asset(st, owner, kind, hex, leader=None, realm=None):
    i = st["next_id"]
    st["next_id"] += 1
    a = {"id": f"a{i}", "owner": owner, "kind": kind, "hex": hex, "hp": ASSETS[kind]["hp"],
         "from": None, "seen": False, "leader": leader}
    if realm:
        a["realm"] = realm
    st["assets"][a["id"]] = a
    return a


def generate(seed, level=4):
    rng = random.Random(seed)
    levels = list(range(1, len(HEXES) + 1))
    rng.shuffle(levels)
    lv = dict(zip(HEXES, levels))
    tower = next(h for h in HEXES if lv[h] == 1)
    realms = carve(rng, [h for h in HEXES if h != tower], lv)
    peoples = list(PEOPLES)
    rng.shuffle(peoples)
    st = {"version": VERSION, "seed": seed, "month": 1, "rng": 0, "level": level,
          "hexes": {}, "rivers": [], "factions": {}, "assets": {}, "next_id": 1,
          "names": ["Morten"], "fallen": [], "morten": tower, "events": [], "report": {},
          "log": []}
    for h in HEXES:
        st["hexes"][h] = {"level": lv[h], "biome": rng.choice(BIOMES[hkey(h)[1]]),
                          "people": TOWER_FOLK, "holder": TOWER, "lake": False}
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
    for people in sorted(peoples, key=peoples.index):
        mine = hexes_of(st, people)
        s = sum(lv[h] for h in mine)
        c = max(1, min(MAX_RATING, int(s / START_DIV + 0.5)))
        seat = max(mine, key=lambda h: lv[h])
        f = {"name": people, "tower": False,
             "leader": new_leader(st, people, rng, "good" if people in good else "bad"),
             "goal": None, "force": c, "cunning": c, "wealth": c, "gp": s * START_GP,
             "seat": seat, "hostile": 0, "disorder": 0, "dissident": None, "xp": 0}
        f["hp"] = max_hp(f)
        st["factions"][people] = f
        for typ, n in START_ASSETS.items():
            for k in range(n):
                opts = [key for key, a in ASSETS.items() if a["type"] == typ
                        and a["needs"] <= c and key not in ("seditionists", "walls")
                        and (not a["land"] or any(st["hexes"][h]["biome"] in a["land"]
                                                  for h in mine))]
                key = rng.choice(sorted(opts))
                where = [h for h in mine if not ASSETS[key]["land"]
                         or st["hexes"][h]["biome"] in ASSETS[key]["land"]]
                h = seat if typ == "Force" and k == 0 else rng.choice(where)
                add_asset(st, people, key, h)
    t = {"name": TOWER, "tower": True,
         "leader": {"name": "Morten", "title": "Wizard", "label": "tower", "tag": "Tower"},
         "goal": None, "gp": TOWER_START["gp"], "seat": tower, "hostile": 0, "disorder": 0,
         "dissident": None, "xp": 0}
    t.update({k: TOWER_START[k] for k in ("force", "cunning", "wealth")})
    t["hp"] = max_hp(t)
    st["factions"][TOWER] = t
    st["rng"] = rng.getrandbits(32)
    t = Turn(st)  # every realm starts with a goal
    for n in st["factions"]:
        if n != TOWER:
            t.pick_goal(n)
    st["rng"] = t.rng.getrandbits(32)
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
    """target: an asset dict, or a faction name for its seat."""
    if isinstance(target, dict):
        A = info(target)
        names = A["fight"] or BEASTS[people_of(target["owner"])]
        tier, title = A["tier"], f"{aname(target)} in {target['hex']}"
    else:
        f = st["factions"][target]
        names, tier = SEAT_FIGHT, SEAT_TIER
        title = f"{poss(target)} seat in {f['seat']} ({f['leader']['title']} {f['leader']['name']}'s court)"
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


# ---- The domain turn ----

PASSIVE = dict(at=None, level=None, strike=None, rob=None, contact=False, delve=False,
               keep_loot=False, deposit=0, withdraw=0, give=[], action=None, plan=[], gm=False)


class Turn:
    def __init__(self, st):
        self.st = st
        self.rng = random.Random(st["rng"])
        self.rivers = {e for r in st["rivers"] for e in r["edges"]}
        self.month = st["month"]
        self.log = []          # (text, secret)
        self.income = []
        self.events = []       # dicts; "secret" ones never reach the tower's view
        self.plan = []
        self.stats = Counter()
        self.seizes = []       # (faction, hex)
        self.mage_used = set()
        self.won = set()       # (attacker faction, target id or "seat:NAME") won this month
        self.bought = set()    # (faction, kind)
        self.last_hit = {}     # faction → who last hurt its HP

    # -- small helpers --
    def d(self, n):
        return self.rng.randint(1, n)

    def f(self, name):
        return self.st["factions"][name]

    def holder(self, h):
        return self.st["hexes"][h]["holder"]

    def say(self, text, secret=False):
        self.log.append((text, secret))

    def event(self, actor, action, frm, to, target, result, text, secret=False, involves=()):
        self.events.append({"month": self.month, "actor": actor, "action": action,
                            "from_hex": frm, "to_hex": to, "target": target, "result": result,
                            "text": text, "secret": secret,
                            "involves": sorted({actor, *involves} - {None})})
        self.say(text, secret)

    def hidden(self, a):
        """True when the tower can't see this asset (its acts are secret)."""
        return not visible(self.st, a)

    def gp(self, name, v):
        self.f(name)["gp"] += v

    def asset(self, aid, owner=None):
        a = self.st["assets"].get(aid)
        if not a:
            raise Bad(f"no asset '{aid}'")
        if owner and a["owner"] != owner:
            raise Bad(f"{aid} is {aname(a)}, not the {owner}'s")
        return a

    def realm(self, s):
        for n in self.st["factions"]:
            if n.lower() == s.lower() and n != TOWER:
                return n
        if any(x["realm"].lower() == s.lower() for x in self.st["fallen"]):
            raise Bad(f"{s} has fallen")
        raise Bad(f"no realm '{s}' (realms: {', '.join(r for r in self.st['factions'] if r != TOWER)})")

    def hexarg(self, s):
        h = s.strip().upper()
        if h not in self.st["hexes"]:
            raise Bad(f"no hex '{s}' (A1–D5)")
        return h

    def can_attack(self, a):
        return info(a)["atk"] is not None and a["kind"] != "seditionists"

    def mobile(self, a):
        return info(a)["move"] > 0

    def force_in(self, name, h):
        return [a for a in assets_of(self.st, name, h, "Force")]

    def guarded(self, name, h):
        return bool(self.force_in(name, h))

    def buy_points(self, name):
        f = self.f(name)
        pts = {f["seat"]} | {a["hex"] for a in assets_of(self.st, name, typ="Force")}
        return sorted((h for h in pts if self.holder(h) == name), key=hkey)

    def limit_counts(self, name):
        return Counter(info(a)["type"] for a in assets_of(self.st, name))

    def destroy(self, a, why):
        self.st["assets"].pop(a["id"], None)
        self.stats["destroyed"] += 1
        return f" {info(a)['name']} {a['id']} destroyed{why}."

    def hurt_faction(self, name, n, by):
        f = self.f(name)
        old = f["hp"]
        f["hp"] = max(0, f["hp"] - n)
        self.last_hit[name] = by
        if name != TOWER:
            self.stats["hp_damage"] += old - f["hp"]
            self.stats["hp_hits"] += 1
        return f"{name if name != TOWER else 'Tower'} HP {old} → {f['hp']}"

    # -- Morten's month --
    def land(self, o):
        st, T = self.st, self.f(TOWER)
        if o.level:
            if not 1 <= o.level <= 20:
                raise Bad("--level must be 1–20")
            st["level"] = o.level
        if o.at:
            st["morten"] = self.hexarg(o.at)
        here = st["morten"]
        missions = [m for m in ("strike", "rob", "contact", "delve") if getattr(o, m)]
        if len(missions) > 1:
            raise Bad(f"one mission a month, not {' and '.join(missions)}")
        if o.keep_loot and not o.rob:
            raise Bad("--keep-loot needs --rob")
        for line in o.plan:
            self.plan.append(line)
        for a in assets_of(st, hex=here):  # Morten sees what's in his hex
            a["seen"] = a.get("seen") or "Morten was here"
        if o.strike:
            tgt = o.strike.strip()
            if tgt.lower().startswith("a") and tgt[1:].isdigit():
                a = self.asset(tgt.lower())
                if a["owner"] == TOWER:
                    raise Bad(f"{a['id']} is the tower's own")
                if a["hex"] != here:
                    raise Bad(f"{aname(a)} is in {a['hex']}; Morten is in {here} (use --at)")
                n, txt = roll(self.rng, STRIKE)
                old = a["hp"]
                a["hp"] -= n
                res = f"{info(a)['name']} HP {old} → {max(0, a['hp'])}"
                tail = self.destroy(a, " by Morten") if a["hp"] <= 0 else ""
                self.set_hostile(a["owner"], HOSTILE)
                self.plan.insert(0, f"Morten: Strike {aname(a)} in {here} (tier {info(a)['tier']}).")
                self.event(TOWER, "Mission", here, here, aname(a), f"won: {res}",
                           f"Morten: Strike on {aname(a)} in {here}, won → {txt}: {res}.{tail}"
                           f" {a['owner']} hostile {self.f(a['owner'])['hostile']} months.",
                           involves=[a["owner"]])
            else:
                name = self.realm(tgt)
                f = self.f(name)
                if f["seat"] != here:
                    raise Bad(f"the {poss(name)} seat is {f['seat']}; Morten is in {here}")
                if self.guarded(name, here):
                    g = ", ".join(x["id"] for x in self.force_in(name, here))
                    raise Bad(f"the {poss(name)} seat is guarded ({g}): Strike a Force asset first")
                n, txt = roll(self.rng, STRIKE)
                res = self.hurt_faction(name, n, TOWER)
                self.set_hostile(name, HOSTILE_SEAT)
                self.plan.insert(0, f"Morten: Strike the {poss(name)} unguarded seat in {here}.")
                self.event(TOWER, "Mission", here, here, f"{poss(name)} seat", f"won: {res}",
                           f"Morten: Strike on the {poss(name)} seat in {here}, won → {txt}: {res}."
                           f" {name} hostile {f['hostile']} months.", involves=[name])
        if o.rob:
            a = self.asset(o.rob.strip().lower())
            if info(a)["type"] != "Wealth" or a["owner"] == TOWER:
                raise Bad(f"Rob needs another faction's Wealth asset; {a['id']} is {aname(a)}")
            if a["hex"] != here:
                raise Bad(f"{aname(a)} is in {a['hex']}; Morten is in {here} (use --at)")
            n, txt = roll(self.rng, ROB)
            old = a["hp"]
            a["hp"] -= n
            res = f"{info(a)['name']} HP {old} → {max(0, a['hp'])}"
            tail = self.destroy(a, " by Morten") if a["hp"] <= 0 else ""
            owner = self.f(a["owner"])
            want = info(a)["tier"] * ROB_GP * (ROB_TREASURY if a["kind"] == "treasury" else 1)
            amt = min(want, owner["gp"])
            owner["gp"] -= amt
            if o.keep_loot:
                where = "Morten keeps it"
            else:
                T["gp"] += amt
                where = f"tower {T['gp'] - amt:,} → {T['gp']:,} GP"
            self.set_hostile(a["owner"], HOSTILE)
            self.plan.insert(0, f"Morten: Rob {aname(a)} in {here}.")
            self.event(TOWER, "Mission", here, here, aname(a), f"won: {amt:,} GP, {res}",
                       f"Morten: Rob {aname(a)} in {here}, won → {txt}: {res}.{tail} Takes"
                       f" {amt:,} GP ({a['owner']} {owner['gp'] + amt:,} → {owner['gp']:,}),"
                       f" {where}. {a['owner']} hostile {owner['hostile']} months.",
                       involves=[a["owner"]])
        if o.contact:
            name = self.holder(here)
            if name == TOWER:
                raise Bad(f"Contact needs a realm's hex; {here} is the tower's")
            f = self.f(name)
            dn = name_for(st, name, self.rng)
            f["dissident"] = {"name": dn, "hex": here}
            self.plan.insert(0, f"Morten: Contact the {name} in {here}, to find a dissident.")
            self.event(TOWER, "Mission", here, here, f"{name} dissidents",
                       f"won: {dn} will lead Seditionists",
                       f"Morten: Contact in {here} succeeded: {dn} of the {name} will lead the"
                       f" tower's Seditionists (buy them in {here} at C2+).", involves=[name])
        if o.delve:
            lv = st["hexes"][here]["level"]
            self.plan.insert(0, f"Morten: Delve floor {lv} under {here}.")
            self.event(TOWER, "Mission", here, here, f"floor {lv}", "delved",
                       f"Morten: Delve floor {lv} under {here} (the dungeon game; no domain effect).")
        if o.deposit:
            if o.deposit < 0:
                raise Bad("--deposit must be positive")
            T["gp"] += o.deposit
            self.say(f"Morten: deposit {o.deposit:,} GP → tower {T['gp']:,} GP.")
        if o.withdraw:
            if not 0 < o.withdraw <= T["gp"]:
                raise Bad(f"--withdraw {o.withdraw:,}: tower holds {T['gp']:,} GP")
            T["gp"] -= o.withdraw
            self.say(f"Morten: withdraw {o.withdraw:,} GP → tower {T['gp']:,} GP.")
        for spec in o.give:
            r, _, amt = spec.partition("=")
            name = self.realm(r)
            try:
                amt = int(amt)
            except ValueError:
                raise Bad(f"--give {spec}: want REALM=GP")
            if not 0 < amt <= T["gp"]:
                raise Bad(f"--give {spec}: tower has {T['gp']:,} GP at that point")
            T["gp"] -= amt
            self.gp(name, amt)
            self.plan.append(f"Tower: Give {amt:,} GP to the {name}.")
            self.event(TOWER, "Give", None, None, name, f"{amt:,} GP",
                       f"Tower: Give {amt:,} GP to the {name} → {self.f(name)['gp']:,} GP."
                       f" Tower {T['gp'] + amt:,} → {T['gp']:,}.", involves=[name])

    def set_hostile(self, name, months):
        if name == TOWER:
            return
        f = self.f(name)
        f["hostile"] = max(f["hostile"], months)
        f["goal"] = None if f["goal"] and f["goal"].get("kind") != "punish" else f["goal"]

    # -- income and upkeep --
    def economy(self):
        st = self.st
        for name in self.order_names():
            f = self.f(name)
            hx = sum(hex_income(st, h) for h in hexes_of(st, name))
            ai = sum(info(a)["income"] for a in assets_of(st, name))
            f["gp"] += hx + ai
            if name != TOWER:
                self.stats["income"] += hx + ai
            lost = []
            while True:
                charges = self.upkeep_list(name)
                due = sum(c for c, _ in charges)
                if due <= f["gp"] or not charges:
                    break
                c, a = min(charges, key=lambda x: (info(x[1])["cost"], int(x[1]["id"][1:])))
                lost.append(a)
                self.st["assets"].pop(a["id"])
                self.stats["upkeep_loss"] += 1
                if name == TOWER:
                    self.stats["tower_upkeep_loss"] += 1
            due = min(due, f["gp"])
            f["gp"] -= due
            self.stats["upkeep_paid"] += due
            nm = "Tower" if name == TOWER else name
            line = f"{nm}: hexes +{hx:,}" + (f", assets +{ai:,}" if ai else "") + \
                   (f", upkeep −{due:,}" if due else "") + f" → {f['gp']:,} GP"
            for a in lost:
                line += f"; can't pay: loses {info(a)['name']} {a['id']}"
                self.event(name, "Fall", a["hex"], a["hex"], aname(a), "disbanded (upkeep)",
                           f"{nm}: can't pay upkeep, {aname(a)} in {a['hex']} disbands.",
                           secret=self.hidden(a))
            self.income.append(line)

    def upkeep_list(self, name):
        return upkeep_list(self.st, name)

    # -- order --
    def order_names(self):
        return [n for n in self.st["factions"]]

    def order(self):
        names = list(self.st["factions"])
        rolls = {n: self.d(DIE) for n in names}
        names.sort(key=lambda n: (-self.f(n)["cunning"], n != TOWER, -rolls[n], n))
        self.say("Order: " + " · ".join(f"{'Tower' if n == TOWER else n} C{self.f(n)['cunning']}"
                                        f" (d10 {rolls[n]})" for n in names) + ".")
        return names

    # -- attacks --
    def attack(self, a, target, why=""):
        """a attacks target (asset dict, or ("seat", name)). Returns True if a still stands."""
        st = self.st
        A = info(a)
        X, Y, dmg = A["atk"]
        att = self.f(a["owner"])
        h = a["hex"]
        if isinstance(target, tuple):
            dname = target[1]
            tlabel = f"the {poss(dname)} seat" if dname != TOWER else "the tower itself"
            ctr = SEAT_COUNTER
        else:
            dname = target["owner"]
            tlabel = aname(target)
            ctr = info(target)["ctr"]
            # a court mage may cancel it
            for m in assets_of(st, dname, h):
                if m["kind"] == "court_mage" and m["id"] not in self.mage_used:
                    self.mage_used.add(m["id"])
                    r1, r2 = self.d(DIE), self.d(DIE)
                    t1, t2 = r1 + self.f(dname)["cunning"], r2 + att["cunning"]
                    if t1 > t2:
                        secret = self.hidden(a) and dname != TOWER
                        self.event(a["owner"], "Attack", h, h, tlabel, "cancelled by a court mage",
                                   f"{who(att)}: {info(a)['name']} {a['id']} attacks {tlabel} in {h}"
                                   f" → {poss(dname)} Court mage {m['id']} cancels it (d10 {r1} +"
                                   f" C{self.f(dname)['cunning']} = {t1} vs d10 {r2} +"
                                   f" C{att['cunning']} = {t2}).", secret=secret,
                                   involves=[dname])
                        return True
        dfn = self.f(dname)
        am, dm = [], []
        if st["hexes"][h]["people"] == a["owner"]:
            am.append((CLAIM, "claim"))
        if a.get("from") and edge(a["from"], h) in self.rivers:
            dm.append((RIVER, "river"))
        if self.holder(h) == dname and any(x["kind"] == "walls" for x in assets_of(st, dname, h)):
            dm.append((WALLS, "walls"))
        ra, rd = self.d(DIE), self.d(DIE)
        xa, yd = att[ATTRS[X]], dfn[ATTRS[Y]]
        ta = ra + xa + sum(m for m, _ in am)
        td = rd + yd + sum(m for m, _ in dm)
        mods = lambda ms: "".join(f" + {m} {w}" for m, w in ms)
        res = "WIN" if ta > td else "LOSS" if ta < td else "TIE"
        where = f"from {h}" if isinstance(target, tuple) and dfn["seat"] != h else f"in {h}"
        line = (f"{who(att)}: {info(a)['name']} {a['id']} attacks {tlabel} {where}{why} →"
                f" d10 {ra} + {X}{xa}{mods(am)} = {ta} vs d10 {rd} + {Y}{yd}{mods(dm)} = {td},"
                f" {res}.")
        result = []
        stands = True
        if ta >= td:  # the attack lands
            n, txt = roll(self.rng, dmg)
            if isinstance(target, tuple):
                r = self.hurt_faction(dname, n, a["owner"])
                line += f" {txt}: {r}."
                result.append(r)
                self.won.add((a["owner"], f"seat:{dname}"))
                if att["leader"]["tag"] == "Slaver" and not att["tower"] and \
                        len(assets_of(st, a["owner"], typ="Force")) < att["force"]:
                    b = add_asset(st, a["owner"], "thugs", h)
                    line += f" Captives become {poss(a['owner'])} Thugs {b['id']}."
                    self.stats["enslaved"] += 1
                if self.f(a["owner"])["leader"]["tag"] == "Raider" and dname != a["owner"]:
                    amt = min(RAID_SEAT_GP, dfn["gp"])
                    dfn["gp"] -= amt
                    att["gp"] += amt
                    line += f" Raids {amt:,} GP."
                    result.append(f"takes {amt:,} GP")
            else:
                old = target["hp"]
                last_guard = info(target)["type"] == "Force" and dfn["seat"] == h
                target["hp"] -= n
                r = f"{info(target)['name']} {old} → {max(0, target['hp'])} HP"
                line += f" {txt}: {r}."
                result.append(r)
                if last_guard:  # a guard of the seat: the regime bleeds with it
                    r2 = self.hurt_faction(dname, n, a["owner"])
                    line += f" The seat under attack: {r2}."
                    result.append(r2)
                self.won.add((a["owner"], target["id"]))
                if a["kind"] == "assassins":
                    n2, t2 = roll(self.rng, "1d4")
                    line += f" Assassins: {t2} to the {dname}: {self.hurt_faction(dname, n2, a['owner'])}."
                if att["leader"]["tag"] == "Raider" and not att["tower"]:
                    amt = min(info(target)["tier"] * ROB_GP, dfn["gp"])
                    if amt:
                        dfn["gp"] -= amt
                        att["gp"] += amt
                        line += f" Raids {amt:,} GP."
                        result.append(f"takes {amt:,} GP")
                if target["hp"] <= 0:
                    line += self.destroy(target, "")
                    result.append("destroyed")
                    if att["leader"]["tag"] == "Slaver" and info(target)["type"] == "Force" \
                            and not att["tower"] and \
                            len(assets_of(st, a["owner"], typ="Force")) < att["force"]:
                        b = add_asset(st, a["owner"], "thugs", h)
                        line += f" Its people become {poss(a['owner'])} Thugs {b['id']}."
                        self.stats["enslaved"] += 1
        if ta <= td and ctr:  # the defence hits back
            n, txt = roll(self.rng, ctr)
            old = a["hp"]
            a["hp"] -= n
            line += f" Counter {txt}: {info(a)['name']} {old} → {max(0, a['hp'])} HP."
            result.append(f"counter {n}")
            if a["hp"] <= 0:
                line += self.destroy(a, "")
                result.append("attacker destroyed")
                stands = False
        # hostility, visibility
        if a["owner"] == TOWER:
            self.set_hostile(dname, HOSTILE_SEAT if isinstance(target, tuple) else HOSTILE)
            if not isinstance(target, tuple):
                target["seen"] = target.get("seen") or "revealed"
        if dname == TOWER:
            a["seen"] = a.get("seen") or "revealed"
            self.stats["tower_attacked"] += 1
        if a["owner"] == TOWER:
            a["exposed"] = True
        secret = (self.hidden(a) and dname != TOWER) or (
            not isinstance(target, tuple) and self.hidden(target) and a["owner"] != TOWER)
        self.event(a["owner"], "Attack", h, h, tlabel,
                   ("won: " if ta > td else "lost: " if ta < td else "tie: ") + ", ".join(result),
                   line, secret=secret, involves=[dname])
        self.stats["attacks"] += 1
        return stands

    def targets_in(self, name, h, owner=None, prefer_force=True):
        ts = [x for x in assets_of(self.st, hex=h) if x["owner"] != name
              and (owner is None or x["owner"] == owner) and known_to(self.st, name, x)]
        return sorted(ts, key=lambda x: (not (prefer_force and info(x)["type"] == "Force"),
                                         x["hp"], int(x["id"][1:])))

    def attack_all(self, name, h, first=None, owner=None):
        """Every attack-capable asset of name in h attacks once (first target first)."""
        mine = [a for a in assets_of(self.st, name, h) if self.can_attack(a)]
        done = False
        for a in mine:
            if a["id"] not in self.st["assets"]:
                continue
            tgt = None
            if first is not None:
                if isinstance(first, tuple):
                    if not self.guarded(first[1], h) and self.f(first[1])["hp"] > 0:
                        tgt = first
                elif first["id"] in self.st["assets"]:
                    tgt = first
            if tgt is None:
                ts = self.targets_in(name, h, owner)
                if ts:
                    tgt = ts[0]
                elif owner and self.f(owner)["seat"] == h and not self.guarded(owner, h) \
                        and self.f(owner)["hp"] > 0:
                    tgt = ("seat", owner)
            if tgt is None:
                break
            self.attack(a, tgt)
            done = True
        return done

    # -- moving and buying --
    def move(self, name, moves, why=""):
        """moves: [(asset, hex)]."""
        parts = []
        for a, h in moves:
            frm = a["hex"]
            a["from"], a["hex"] = frm, h
            parts.append(f"{info(a)['name']} {a['id']} {frm} → {h}")
            secret = self.hidden(a)
            self.events.append({"month": self.month, "actor": name, "action": "Move",
                                "from_hex": frm, "to_hex": h, "target": aname(a),
                                "result": "moved", "text": "", "secret": secret,
                                "involves": [name, self.holder(h)]})
        vis = [p for (a, h), p in zip(moves, parts) if not self.hidden(a)]
        hid = [p for (a, h), p in zip(moves, parts) if self.hidden(a)]
        n_ev = len(moves)
        if vis:
            text = f"{who(self.f(name))}: Move {', '.join(vis)}{why}."
            self.say(text)
            for e in self.events[-n_ev:]:
                if not e["secret"]:
                    e["text"] = text
        if hid:
            self.say(f"{who(self.f(name))}: Move {', '.join(hid)}{why}.", True)
        self.stats["moves"] += 1

    def buy(self, name, kind, h, why=""):
        f = self.f(name)
        A = ASSETS[kind]
        f["gp"] -= A["cost"]
        leader = None
        realm = None
        if kind == "seditionists":
            realm = self.holder(h)
            leader = self.f(realm)["dissident"]["name"]
        a = add_asset(self.st, name, kind, h, leader, realm)
        self.bought.add((name, kind))
        self.event(name, "Buy", h, h, aname(a), f"{A['cost']:,} GP",
                   f"{who(f)}: Buy {A['name']} {a['id']} in {h}{why}, −{A['cost']:,} GP →"
                   f" {f['gp']:,} GP.", secret=self.hidden(a))
        self.stats["buys"] += 1
        return a

    def raise_(self, name, attr, why=""):
        f = self.f(name)
        new = f[attr] + 1
        cost = RAISE[new]
        old_max = max_hp(f)
        f["gp"] -= cost
        f[attr] = new
        f["hp"] += max_hp(f) - old_max
        self.event(name, "Raise", None, None, attr.capitalize(), f"{new - 1} → {new}",
                   f"{who(f)}: Raise {attr.capitalize()} {new - 1} → {new}{why}, −{cost:,} GP →"
                   f" {f['gp']:,} GP. HP {f['hp']}/{max_hp(f)}.")
        self.stats["raises"] += 1

    def repair_faction(self, name):
        f = self.f(name)
        f["gp"] -= REPAIR_HP_GP
        n, txt = roll(self.rng, REPAIR_HP)
        old = f["hp"]
        f["hp"] = min(max_hp(f), f["hp"] + n)
        self.event(name, "Repair", f["seat"], f["seat"], "itself", f"HP {old} → {f['hp']}",
                   f"{who(f)}: Repair, −{REPAIR_HP_GP} GP → {txt}: HP {old} → {f['hp']}/{max_hp(f)}.")
        self.stats["repairs"] += 1

    def repair_asset(self, name, a):
        f = self.f(name)
        cost = info(a)["cost"] // REPAIR_DIV
        f["gp"] -= cost
        old = a["hp"]
        a["hp"] = max_ahp(a)
        self.event(name, "Repair", a["hex"], a["hex"], aname(a), f"{old} → {a['hp']} HP",
                   f"{who(f)}: Repair {info(a)['name']} {a['id']} in {a['hex']}, −{cost:,} GP:"
                   f" HP {old} → {a['hp']}.", secret=self.hidden(a))
        self.stats["repairs"] += 1

    def can_buy(self, name, kind):
        f, A = self.f(name), ASSETS[kind]
        return f[TYPE_ATTR[A["type"]]] >= A["needs"] and f["gp"] >= A["cost"]

    def best_buy(self, name, types, attackers=False, reserve=0):
        f = self.f(name)
        opts = [k for k, A in ASSETS.items() if A["type"] in types and k != "seditionists"
                and f[TYPE_ATTR[A["type"]]] >= A["needs"] and f["gp"] - reserve >= A["cost"]
                and (not attackers or A["atk"]) and not A["land"]]
        if not opts:
            return None
        return max(opts, key=lambda k: (ASSETS[k]["tier"], ASSETS[k]["cost"], k))

    # -- the AI's moves toward a hex --
    def army(self, a):
        """Assets the AI marches: Force attackers and Mercenaries."""
        return self.can_attack(a) and self.mobile(a) and (
            info(a)["type"] == "Force" or a["kind"] in ARMY_EXTRA)

    def bring(self, name, T, why="", force_only=False):
        """Get its army into T: buy while the army is short of its Force rating, else move.
        True if it acted."""
        f = self.f(name)
        seat = f["seat"]
        pts = self.buy_points(name)
        n_army = len([a for a in assets_of(self.st, name) if self.army(a)])
        if pts and n_army < ARMY_MIN:
            k = self.best_buy(name, ("Force",), attackers=True)
            if k:
                h = min(pts, key=lambda p: (dist(p, T), hkey(p)))
                self.buy(name, k, h, why)
                return True
        cands = [a for a in assets_of(self.st, name) if self.army(a) and a["hex"] != T
                 and (not force_only or info(a)["type"] == "Force")]
        # never strip the seat of its last Force asset
        seat_force = self.force_in(name, seat)
        if len(seat_force) == 1:
            cands = [a for a in cands if a["id"] != seat_force[0]["id"]]
        moves = []
        for a in cands:
            d = dist(a["hex"], T)
            if d <= info(a)["move"]:
                moves.append((a, T))
            elif d <= 4:
                h = a["hex"]
                for _ in range(info(a)["move"]):
                    h = step_toward(h, T, self.rng)
                moves.append((a, h))
        if moves:
            self.move(name, moves, why)
            return True
        if pts:
            k = self.best_buy(name, ("Force",), attackers=True)
            if k:
                h = min(pts, key=lambda p: (dist(p, T), hkey(p)))
                self.buy(name, k, h, why)
                return True
        return False

    def go_attack(self, name, target, why=""):
        """Attack target (asset or ("seat", n)) or work toward it."""
        h = target["hex"] if isinstance(target, dict) else self.f(target[1])["seat"]
        owner = target["owner"] if isinstance(target, dict) else target[1]
        if any(self.can_attack(a) for a in assets_of(self.st, name, h)):
            first = target
            if isinstance(target, tuple) and self.guarded(owner, h):
                first = None
            return self.attack_all(name, h, first, owner)
        return self.bring(name, h, why=why)

    def go_seize(self, name, T, why=""):
        holder = self.holder(T)
        if holder == name:
            return False
        if self.force_in(name, T):
            if self.force_in(holder, T) or any(x["kind"] == "walls"
                                               for x in assets_of(self.st, holder, T)):
                if any(self.can_attack(a) for a in assets_of(self.st, name, T)):
                    return self.attack_all(name, T, None, holder)
                return self.bring(name, T, why, force_only=True)
            self.seizes.append((name, T))
            f = self.f(name)
            self.event(name, "Seize", T, T, f"{T} ({poss(holder)})", "resolves at clean-up",
                       f"{who(f)}: Seize {T} (L{self.st['hexes'][T]['level']}, {poss(holder)}){why}:"
                       f" no defender there; it changes hands at clean-up unless contested.",
                       involves=[holder])
            return True
        return self.bring(name, T, why, force_only=True)

    # -- the realms' AI (realms.md section 8) --
    def neighbours(self, name):
        """Factions next to its hexes, less those it is resting from (REST)."""
        mine = set(hexes_of(self.st, name))
        rest = self.f(name).get("rest", {})
        out = {self.holder(n) for h in mine for n in nbrs(h)} - {name}
        return sorted(n for n in out if rest.get(n, 0) <= self.month)

    def border(self, name):
        mine = set(hexes_of(self.st, name))
        return sorted({n for h in mine for n in nbrs(h)} - mine, key=hkey)

    def pick_goal(self, name):
        st, f = self.st, self.f(name)
        tag = f["leader"]["tag"]
        lvl = lambda h: st["hexes"][h]["level"]
        near = lambda a: min(dist(a["hex"], h) for h in hexes_of(st, name))
        g = None
        if tag in ("Liberator",):
            foes = [n for n in self.neighbours(name) if n != TOWER
                    and self.f(n)["leader"]["label"] == "bad" and self.f(n)["force"] < f["force"]]
            ts = [a for n in foes for a in assets_of(st, n, typ="Force") if near(a) <= 1]
            if ts:
                a = min(ts, key=lambda a: (a["hp"], near(a), int(a["id"][1:])))
                g = {"kind": "break", "target": a["id"], "attr": "force",
                     "text": f"break {aname(a)} in {a['hex']}"}
        if tag == "Conqueror":
            hs = [h for h in self.border(name) if h != st["factions"][TOWER]["seat"]
                  and self.holder(h) in self.neighbours(name)]

            def worth(h):  # deep ley, few defenders near, not a seat
                o = self.holder(h)
                near_f = len([a for a in assets_of(st, o, typ="Force") if dist(a["hex"], h) <= 1])
                return (lvl(h) - CONQUER_GUARD * near_f
                        - CONQUER_GUARD * (st["factions"][o]["seat"] == h), h)
            if hs:
                h = max(hs, key=worth)
                g = {"kind": "seize", "hex": h, "attr": "force",
                     "text": f"take {h} (L{lvl(h)}, {poss(self.holder(h))})"}
        elif tag == "Raider":
            best = None
            for n in self.neighbours(name):
                nf = self.f(n)
                score = nf["gp"] - 100 * len(assets_of(st, n, typ="Force"))
                ws = [a for a in assets_of(st, n, typ="Wealth") if near(a) <= 2]
                if ws:
                    tgt = min(ws, key=lambda a: (near(a), -info(a)["tier"], int(a["id"][1:])))
                elif dist_to_set(nf["seat"], hexes_of(st, name)) <= 1:
                    tgt = ("seat", n)
                else:
                    continue
                if best is None or score > best[0]:
                    best = (score, tgt)
            if best:
                tgt = best[1]
                if isinstance(tgt, tuple):
                    g = {"kind": "raid", "target": f"seat:{tgt[1]}", "attr": "wealth",
                         "text": f"raid {poss(tgt[1])} seat in {self.f(tgt[1])['seat']}"}
                else:
                    g = {"kind": "raid", "target": tgt["id"], "attr": "wealth",
                         "text": f"rob {aname(tgt)} in {tgt['hex']}"}
        elif tag == "Slaver":
            foes = self.neighbours(name)
            if foes:
                n = min(foes, key=lambda n: (self.f(n)["force"], self.f(n)["hp"], n))
                fa = [a for a in assets_of(st, n, typ="Force") if near(a) <= 2]
                if fa:
                    a = min(fa, key=lambda a: (near(a), a["hp"], int(a["id"][1:])))
                    g = {"kind": "break", "target": a["id"], "attr": "force",
                         "text": f"take {poss(n)} {info(a)['name']} {a['id']} in {a['hex']} for soldiers"}
                elif not assets_of(st, n, typ="Force"):
                    g = {"kind": "raid", "target": f"seat:{n}", "attr": "force",
                         "text": f"take people from {poss(n)} seat in {self.f(n)['seat']}"}
        elif tag == "Tyrant":
            owned = {a["kind"] for a in assets_of(st, name)}
            opts = [k for k, A in ASSETS.items() if k != "seditionists" and not A["land"]
                    and f[TYPE_ATTR[A["type"]]] >= A["needs"] and k not in owned]
            if opts:
                k = max(opts, key=lambda k: (ASSETS[k]["cost"], k))
                g = {"kind": "buy", "asset": k, "attr": TYPE_ATTR[ASSETS[k]["type"]],
                     "text": f"buy {ASSETS[k]['name']} ({ASSETS[k]['cost']:,} GP)"}
            else:
                attr = min(("force", "cunning", "wealth"), key=lambda x: (f[x], x))
                if f[attr] < MAX_RATING:
                    g = {"kind": "raise", "attr": attr, "to": f[attr] + 1,
                         "text": f"raise {attr.capitalize()} to {f[attr] + 1}"}
        if g is None and tag in ("Steward", "Liberator"):
            own = [h for h in self.border(name) if st["hexes"][h]["people"] == name]
            seat_walls = any(a["kind"] == "walls" for a in assets_of(st, name, f["seat"]))
            farms = len([a for a in assets_of(st, name) if a["kind"] == "farms"])
            if own:
                h = max(own, key=lambda h: (lvl(h), h))
                g = {"kind": "seize", "hex": h, "attr": "force",
                     "text": f"take back {h} (L{lvl(h)}, {poss(self.holder(h))})"}
            elif not seat_walls and f["force"] >= ASSETS["walls"]["needs"]:
                g = {"kind": "buy", "asset": "walls", "attr": "force",
                     "text": f"build Walls at {f['seat']}"}
            elif farms < 2:
                g = {"kind": "buy", "asset": "farms", "attr": "wealth", "text": "buy Farms"}
            else:
                attr = min(("force", "cunning", "wealth"), key=lambda x: (f[x], x))
                if f[attr] < MAX_RATING:
                    g = {"kind": "raise", "attr": attr, "to": f[attr] + 1,
                         "text": f"raise {attr.capitalize()} to {f[attr] + 1}"}
        if g:
            g["since"] = self.month
            t = g.get("target", "")
            g["against"] = (t[5:] if t.startswith("seat:") else st["assets"][t]["owner"] if t
                            else self.holder(g["hex"]) if g.get("hex") else None)
            f["goal"] = g
            self.event(name, "Goal", None, None, g["text"], "new goal",
                       f"{who(f)}: new goal: {g['text']}.")
        return g

    def goal_target(self, g):
        t = g.get("target")
        if t and t.startswith("seat:"):
            n = t[5:]
            return ("seat", n) if n in self.st["factions"] else None
        return self.st["assets"].get(t) if t else None

    def realm_act(self, name):
        st, f = self.st, self.f(name)
        if f["disorder"]:
            self.say(f"{who(f)}: in disorder, no action.")
            return
        if f["hp"] <= 0:
            self.say(f"{who(f)}: the regime is collapsing (HP 0), no action.")
            return
        # 1. recover
        if f["hp"] * 2 < max_hp(f) and f["gp"] >= REPAIR_HP_GP:
            self.repair_faction(name)
            return
        # 2. defend its hexes
        for h in sorted(hexes_of(st, name), key=lambda h: -st["hexes"][h]["level"]):
            foes = [a for a in assets_of(st, hex=h, typ="Force") if a["owner"] != name]
            if foes:
                if any(self.can_attack(a) for a in assets_of(st, name, h)):
                    self.attack_all(name, h, foes[0], foes[0]["owner"])
                    return
                if self.bring(name, h, f" (to drive the {foes[0]['owner']} out of {h})", True):
                    return
        # 3. punish the tower
        if f["hostile"]:
            ts = [a for a in assets_of(st, TOWER) if known_to(st, name, a)]
            if ts:
                tgt = min(ts, key=lambda a: (dist_to_set(a["hex"], hexes_of(st, name)),
                                             a["hp"], int(a["id"][1:])))
            else:
                tgt = ("seat", TOWER)
            if self.go_attack(name, tgt, " (to punish the tower)"):
                return
        # 4. a full treasury buys
        if f["gp"] >= RICH and self.develop(name, rich=True):
            return
        # 5. the tag's goal
        g = f["goal"]
        if g is None or not self.goal_live(name, g):
            f["goal"] = None
            g = self.pick_goal(name)
        if g and self.pursue(name, g):
            return
        # 6. grow
        self.develop(name)

    def goal_live(self, name, g):
        if self.month - g["since"] >= GOAL_MONTHS:
            self.say(f"{who(self.f(name))}: drops its goal ({g['text']}): {GOAL_MONTHS} months.")
            self.stats["goal_drop"] += 1
            return False
        if g["kind"] in ("break", "raid"):
            t = self.goal_target(g)
            if t is None:
                return False
            h = t["hex"] if isinstance(t, dict) else self.f(t[1])["seat"]
            return dist_to_set(h, hexes_of(self.st, name)) <= 2
        if g["kind"] == "seize":
            return self.holder(g["hex"]) != name
        return True

    def pursue(self, name, g):
        f = self.f(name)
        why = f" (goal: {g['text']})"
        if g["kind"] == "seize":
            return self.go_seize(name, g["hex"], why)
        if g["kind"] in ("break", "raid"):
            return self.go_attack(name, self.goal_target(g), why)
        if g["kind"] == "buy":
            k = g["asset"]
            if self.can_buy(name, k):
                pts = self.buy_points(name)
                if not pts:
                    return False
                h = f["seat"] if f["seat"] in pts else pts[0]
                self.buy(name, k, h, why)
                return True
            if f[TYPE_ATTR[ASSETS[k]["type"]]] < ASSETS[k]["needs"]:
                return False
            self.say(f"{who(f)}: saves for {ASSETS[k]['name']} ({f['gp']:,}/{ASSETS[k]['cost']:,} GP).")
            return True
        if g["kind"] == "raise":
            if f[g["attr"]] >= g["to"]:
                return False
            if f["gp"] >= RAISE[g["to"]]:
                self.raise_(name, g["attr"], why)
                return True
            self.say(f"{who(f)}: saves to raise {g['attr'].capitalize()}"
                     f" ({f['gp']:,}/{RAISE[g['to']]:,} GP).")
            return True
        return False

    def develop(self, name, rich=False):
        """Repair, buy within its limits, raise, or (rich) buy over them. True if it acted."""
        st, f = self.st, self.f(name)
        hurt = [a for a in assets_of(st, name) if a["hp"] * 2 <= max_ahp(a)
                and f["gp"] >= info(a)["cost"] // REPAIR_DIV]
        if hurt:
            self.repair_asset(name, max(hurt, key=lambda a: info(a)["cost"]))
            return True
        counts = self.limit_counts(name)
        pts = self.buy_points(name)
        room = [t for t, attr in TYPE_ATTR.items() if counts[t] < f[attr]]
        if pts and room:
            k = self.best_buy(name, room)
            if k:
                h = f["seat"] if f["seat"] in pts else pts[0]
                self.buy(name, k, h, " (it has the gold)" if rich else "")
                return True
        full = [attr for t, attr in TYPE_ATTR.items() if counts[t] >= f[attr] and f[attr] < MAX_RATING]
        if full:
            attr = min(full, key=lambda x: (f[x], x))
            if f["gp"] >= RAISE[f[attr] + 1]:
                self.raise_(name, attr, " (it has the gold)" if rich else "")
                return True
        if rich and pts:
            k = self.best_buy(name, ("Force",), attackers=True, reserve=RICH_RESERVE)
            if k:
                self.buy(name, k, f["seat"] if f["seat"] in pts else pts[0],
                         " (over its limit: it has the gold)")
                return True
        if not rich:
            self.say(f"{who(f)}: saves ({f['gp']:,} GP).")
        return False

    # -- the tower's declared action --
    def check_action(self, o):
        """Parse and check the tower's action before anything happens. Returns a plan."""
        if not o.action:
            return None
        st, T = self.st, self.f(TOWER)
        verb, _, arg = o.action.partition(":")
        verb = verb.strip().lower()
        if verb == "buy":
            k, _, h = arg.partition("@")
            k = kind_of(k)
            A = ASSETS[k]
            if T[TYPE_ATTR[A["type"]]] < A["needs"]:
                raise Bad(f"buy {A['name']}: needs {A['type']} {A['needs']}, tower has"
                          f" {T[TYPE_ATTR[A['type']]]}")
            if k == "seditionists":
                h = self.hexarg(h) if h else None
                ds = [n for n, f in st["factions"].items() if f["dissident"]]
                if h is None:
                    if len(ds) != 1:
                        raise Bad("buy seditionists@HEX: name the hex (a hex of a contacted realm)")
                    h = self.f(ds[0])["dissident"]["hex"]
                r = self.holder(h)
                if r == TOWER or not self.f(r)["dissident"]:
                    raise Bad(f"Seditionists need a dissident: Contact the {r} first"
                              if r != TOWER else f"{h} is the tower's")
                if any(a["kind"] == "seditionists" and a.get("realm") == r
                       for a in assets_of(st, TOWER)):
                    raise Bad(f"the tower already has Seditionists among the {r}")
            else:
                h = self.hexarg(h) if h else T["seat"]
                pts = self.buy_points(TOWER)
                if h not in pts:
                    raise Bad(f"buy in a tower hex with the seat or a tower Force asset: {', '.join(pts)}")
                if A["land"] and st["hexes"][h]["biome"] not in A["land"]:
                    raise Bad(f"{A['name']} only in {' or '.join(A['land'])}; {h} is"
                              f" {st['hexes'][h]['biome']}")
            return ("buy", k, h)
        if verb == "raise":
            attr = arg.strip().lower()
            if attr not in ("force", "cunning", "wealth"):
                raise Bad("raise:force, raise:cunning or raise:wealth")
            if T[attr] >= MAX_RATING:
                raise Bad(f"{attr} is already {MAX_RATING}")
            return ("raise", attr)
        if verb == "repair":
            if arg.strip().lower() == "tower":
                return ("repair", None)
            a = self.asset(arg.strip().lower(), TOWER)
            return ("repair", a["id"])
        if verb == "move":
            moves = []
            for part in arg.split(","):
                aid, _, h = part.partition(">")
                a = self.asset(aid.strip().lower(), TOWER)
                h = self.hexarg(h)
                if not self.mobile(a):
                    raise Bad(f"{info(a)['name']} can't move")
                if not 0 < dist(a["hex"], h) <= info(a)["move"]:
                    raise Bad(f"{a['id']} in {a['hex']} moves {info(a)['move']} hex; {h} is"
                              f" {dist(a['hex'], h)} away")
                moves.append((a["id"], h))
            return ("move", moves)
        if verb == "attack":
            pairs, where = [], set()
            for part in arg.split(","):
                aid, _, t = part.partition(">")
                a = self.asset(aid.strip().lower(), TOWER)
                t = t.strip()
                if not info(a)["atk"]:
                    raise Bad(f"{info(a)['name']} {a['id']} has no attack")
                if t.lower().startswith("a") and t[1:].isdigit():
                    b = self.asset(t.lower())
                    if b["owner"] == TOWER:
                        raise Bad(f"{b['id']} is the tower's own")
                    if b["hex"] != a["hex"]:
                        raise Bad(f"{a['id']} is in {a['hex']}, {b['id']} in {b['hex']}")
                    if not visible(st, b):
                        raise Bad(f"no asset '{b['id']}'")
                    if a["kind"] == "seditionists":
                        raise Bad("Seditionists only attack the realm's HP (attack:aN>REALM)")
                    pairs.append((a["id"], b["id"]))
                    where.add(a["hex"])
                else:
                    r = self.realm(t)
                    if a["kind"] == "seditionists":
                        if a.get("realm") != r:
                            raise Bad(f"these Seditionists are among the {a.get('realm')}")
                        if self.holder(a["hex"]) != r:
                            raise Bad(f"the Seditionists' hex {a['hex']} is no longer the {r}'")
                    else:
                        if a["hex"] != self.f(r)["seat"]:
                            raise Bad(f"{a['id']} must stand in the {poss(r)} seat {self.f(r)['seat']}")
                        if self.guarded(r, a["hex"]):
                            raise Bad(f"the {poss(r)} seat is guarded: attack its Force assets first")
                        where.add(a["hex"])
                    pairs.append((a["id"], f"seat:{r}"))
            if len(where) > 1:
                raise Bad("an Attack is made in one hex (Seditionists excepted)")
            if len({p[0] for p in pairs}) != len(pairs):
                raise Bad("each asset attacks once")
            return ("attack", pairs)
        if verb == "seize":
            h = self.hexarg(arg)
            holder = self.holder(h)
            if holder == TOWER:
                raise Bad(f"{h} is already the tower's")
            if not self.force_in(TOWER, h):
                raise Bad(f"seize needs a tower Force asset in {h}")
            if self.force_in(holder, h) or any(a["kind"] == "walls" for a in assets_of(st, holder, h)):
                raise Bad(f"the {holder} still have a Force asset in {h}")
            return ("seize", h)
        raise Bad(f"--action {o.action}: want buy:, raise:, repair:, move:, attack: or seize:")

    def tower_act(self, plan):
        st, T = self.st, self.f(TOWER)
        if plan is None:
            self.say("Tower: no action.")
            return
        verb = plan[0]
        if verb == "buy":
            _, k, h = plan
            A = ASSETS[k]
            if T["gp"] < A["cost"]:
                raise Bad(f"buy {A['name']}: costs {A['cost']:,}, tower has {T['gp']:,} GP at that point")
            self.buy(TOWER, k, h)
        elif verb == "raise":
            cost = RAISE[T[plan[1]] + 1]
            if T["gp"] < cost:
                raise Bad(f"raise {plan[1]}: costs {cost:,}, tower has {T['gp']:,} GP at that point")
            self.raise_(TOWER, plan[1])
        elif verb == "repair":
            if plan[1] is None:
                if T["gp"] < REPAIR_HP_GP:
                    raise Bad(f"repair:tower costs {REPAIR_HP_GP}, tower has {T['gp']:,} GP at that point")
                self.repair_faction(TOWER)
            else:
                a = st["assets"].get(plan[1])
                if not a:
                    self.say(f"Tower: Repair {plan[1]}: it was destroyed before the tower acted.")
                    return
                cost = info(a)["cost"] // REPAIR_DIV
                if T["gp"] < cost:
                    raise Bad(f"repair {a['id']}: costs {cost:,}, tower has {T['gp']:,} GP at that point")
                self.repair_asset(TOWER, a)
        elif verb == "move":
            moves = [(st["assets"][i], h) for i, h in plan[1] if i in st["assets"]]
            if moves:
                self.move(TOWER, moves)
        elif verb == "attack":
            for i, t in plan[1]:
                a = st["assets"].get(i)
                if not a:
                    continue
                if t.startswith("seat:"):
                    r = t[5:]
                    if r not in st["factions"]:
                        continue
                    if a["kind"] != "seditionists" and self.guarded(r, a["hex"]):
                        self.say(f"Tower: {a['id']} can't reach the {poss(r)} seat: guarded now.")
                        continue
                    self.attack(a, ("seat", r), " (coup)" if a["kind"] == "seditionists" else "")
                else:
                    b = st["assets"].get(t)
                    if b and b["hex"] == a["hex"]:
                        self.attack(a, b)
                    else:
                        self.say(f"Tower: {i}'s target {t} is gone.")
        elif verb == "seize":
            h = plan[1]
            self.seizes.append((TOWER, h))
            self.event(TOWER, "Seize", h, h, f"{h} ({poss(self.holder(h))})", "resolves at clean-up",
                       f"Tower: Seize {h}: it changes hands at clean-up unless contested.",
                       involves=[self.holder(h)])

    # -- goals, clean-up --
    def goals(self):
        st = self.st
        for name, f in st["factions"].items():
            g = f["goal"]
            if f["tower"] or not g:
                continue
            done = False
            if g["kind"] == "seize":
                done = self.holder(g["hex"]) == name
            elif g["kind"] == "break":
                done = g["target"] not in st["assets"] and (name, g["target"]) in self.won
            elif g["kind"] == "raid":
                done = (name, g["target"]) in self.won
            elif g["kind"] == "buy":
                done = (name, g["asset"]) in self.bought
            elif g["kind"] == "raise":
                done = f[g["attr"]] >= g["to"]
            if done:
                attr = g["attr"]
                f["goal"] = None
                if g.get("against"):
                    f.setdefault("rest", {})[g["against"]] = self.month + REST
                xp = GOAL_XP.get(g["kind"], 1)
                f["xp"] = f.get("xp", 0) + xp
                gain = f": +{xp} XP ({f['xp']})"
                if f[attr] < MAX_RATING and f["xp"] >= HP_BONUS[f[attr] + 1]:
                    f["xp"] -= HP_BONUS[f[attr] + 1]
                    old = max_hp(f)
                    f[attr] += 1
                    f["hp"] += max_hp(f) - old
                    gain += f", spent on {attr.capitalize()} {f[attr] - 1} → {f[attr]}"
                self.event(name, "Goal", None, None, g["text"], "done" + gain,
                           f"{who(f)}: goal done ({g['text']}){gain}.")
                self.stats["goals_done"] += 1

    def cleanup(self):
        st = self.st
        for name, h in self.seizes:
            if name not in st["factions"]:
                continue
            holder = self.holder(h)
            if holder == name:
                continue
            ok = self.force_in(name, h) and not self.force_in(holder, h) and not any(
                a["kind"] == "walls" for a in assets_of(st, holder, h))
            if not ok:
                self.event(name, "Seize", h, h, h, "failed: contested",
                           f"{who(self.f(name))}: Seize {h} fails: contested.", involves=[holder])
                continue
            st["hexes"][h]["holder"] = name
            self.stats["seized"] += 1
            if holder == TOWER:
                self.stats["tower_lost"] += 1
            line = f"{who(self.f(name))}: takes {h} (L{st['hexes'][h]['level']}) from the {holder}."
            hf = self.f(holder)
            if hf["seat"] == h:
                n, txt = roll(self.rng, SEAT_SEIZED)
                line += f" It was their seat: {txt}: {self.hurt_faction(holder, n, name)}."
            elif holder != TOWER:
                n, txt = roll(self.rng, HEX_LOST)
                line += f" The regime loses face: {txt}: {self.hurt_faction(holder, n, name)}."
            if hf["seat"] == h:
                rest = hexes_of(st, holder)
                if rest:
                    hf["seat"] = max(rest, key=lambda x: st["hexes"][x]["level"])
                    line += f" Seat moves to {hf['seat']}."
            self.event(name, "Seize", h, h, f"{h} ({poss(holder)})", "taken", line,
                       involves=[holder])
        # timers
        for f in st["factions"].values():
            if f["hostile"]:
                f["hostile"] -= 1
            if f["disorder"]:
                f["disorder"] -= 1
        # realms with no hexes are gone
        for name in [n for n in st["factions"] if n != TOWER and not hexes_of(st, n)]:
            f = st["factions"].pop(name)
            for a in assets_of(st, name):
                st["assets"].pop(a["id"])
            for a in assets_of(st, TOWER):
                if a.get("realm") == name:
                    st["assets"].pop(a["id"])
            st["fallen"].append({"realm": name, "month": self.month})
            self.stats["realm_gone"] += 1
            self.event(name, "Fall", None, None, name, "gone",
                       f"{name}: no hexes left. {f['leader']['title']} {f['leader']['name']} is"
                       f" gone, and the realm with them; the {name} stay on their land.")
        # falls
        for name, f in list(st["factions"].items()):
            if f["hp"] > 0:
                continue
            self.stats["falls"] += 1
            if f["tower"]:
                by = self.last_hit.get(TOWER)
                amt = f["gp"] // 2
                f["gp"] -= amt
                if by in st["factions"]:
                    self.gp(by, amt)
                f["hp"] = max_hp(f)
                for g in st["factions"].values():
                    g["hostile"] = 0
                self.stats["tower_sacked"] += 1
                self.event(TOWER, "Fall", f["seat"], f["seat"], "the tower",
                           f"sacked: −{amt:,} GP",
                           f"The tower is sacked: HP 0. {amt:,} GP carried off"
                           + (f" by the {by}" if by in st["factions"] else "") +
                           f"; the wards hold the hex. HP back to {f['hp']}; every hostility"
                           f" is spent.", involves=[by] if by else ())
                continue
            old = f["leader"]
            sed = [a for a in assets_of(st, TOWER, typ="Cunning")
                   if a["kind"] == "seditionists" and a.get("realm") == name]
            if sed:
                a = sed[0]
                f["leader"] = {"name": a["leader"], "title": rng_choice(self.rng, PEOPLES[name][0]),
                               "label": "good", "tag": rng_choice(self.rng, GOOD)}
                st["assets"].pop(a["id"])
                f["disorder"] = 0
                how = (f"{a['leader']}, the tower's dissident, takes the throne"
                       f" ({label(f)}); the Seditionists {a['id']} become the new court.")
                self.stats["dissident_rule"] += 1
            else:
                f["leader"] = new_leader(st, name, self.rng,
                                         "bad" if self.d(3) > 1 else "good")
                f["disorder"] = DISORDER
                how = (f"{f['leader']['title']} {f['leader']['name']} ({label(f)}) takes"
                       f" the throne; disorder for {DISORDER} month.")
            f["hp"] = max_hp(f)
            f["hostile"] = 0
            f["goal"] = None
            f["dissident"] = None
            self.event(name, "Fall", f["seat"], f["seat"], f"{old['title']} {old['name']}",
                       "the ruler falls",
                       f"{name}: HP 0, {old['title']} {old['name']} falls. {how}")
        st["month"] += 1
        st["rng"] = self.rng.getrandbits(32)

    def run(self, o):
        st = self.st
        plan = self.check_action(o)
        self.land(o)
        if plan:
            self.plan.append(f"Tower: {describe_action(st, plan)}.")
        self.economy()
        for name in self.order():
            if name not in st["factions"]:
                continue
            if name == TOWER:
                self.tower_act(plan)
            else:
                self.realm_act(name)
        self.goals()
        self.cleanup()
        st["events"] = [{k: e[k] for k in ("month", "actor", "action", "from_hex", "to_hex",
                                           "target", "result")}
                        for e in self.events if not e["secret"]]
        st["log"] = [t for t, s in self.log if not s]
        return self.month


def upkeep_list(st, name):
    """[(GP, asset)]: assets with upkeep, and each asset of a type beyond its attribute."""
    f = st["factions"][name]
    out = [(info(a)["upkeep"], a) for a in assets_of(st, name) if info(a)["upkeep"]]
    for typ, attr in TYPE_ATTR.items():
        mine = sorted(assets_of(st, name, typ=typ), key=lambda a: -info(a)["cost"])
        out += [(OVER_LIMIT, a) for a in mine[f[attr]:]]
    return out


def net_income(st, name):
    return (sum(hex_income(st, h) for h in hexes_of(st, name))
            + sum(info(a)["income"] for a in assets_of(st, name))
            - sum(c for c, _ in upkeep_list(st, name)))


def rng_choice(rng, xs):
    return xs[rng.randrange(len(xs))]


def dist_to_set(h, hs):
    return min((dist(h, x) for x in hs), default=99)


def describe_action(st, plan):
    v = plan[0]
    if v == "buy":
        return f"Buy {ASSETS[plan[1]]['name']} in {plan[2]}"
    if v == "raise":
        f = st["factions"][TOWER]
        return f"Raise {plan[1].capitalize()} to {f[plan[1]] + 1}"
    if v == "repair":
        return "Repair the tower" if plan[1] is None else f"Repair {plan[1]}"
    if v == "move":
        return "Move " + ", ".join(f"{i} → {h}" for i, h in plan[1])
    if v == "attack":
        return "Attack: " + ", ".join(f"{i} → {t.replace('seat:', 'the seat of ')}"
                                      for i, t in plan[1])
    if v == "seize":
        return f"Seize {plan[1]}"
    return str(plan)


# ---- Views ----

def hex_label(st, h):
    x = st["hexes"][h]
    return f"{h} (L{x['level']}, {x['biome']}, {x['holder']})"


def asset_line(st, a, where=True):
    A = info(a)
    atk = f"{A['atk'][0]} vs {A['atk'][1]} {A['atk'][2]}" if A["atk"] else "no attack"
    ctr = f"counter {A['ctr']}" if A["ctr"] else "no counter"
    lead = f", led by {a['leader']}" if a.get("leader") else ""
    loc = f" in {a['hex']}" if where else ""
    return (f"{a['id']} {poss(a['owner'])} {A['name']}{loc} · T{A['tier']} · HP {a['hp']}/{A['hp']}"
            f" · {atk} · {ctr}{lead}")


def faction_line(st, f):
    if f["tower"]:
        return (f"Tower · HP {f['hp']}/{max_hp(f)} · F{f['force']} C{f['cunning']} W{f['wealth']}"
                f" · {f['gp']:,} GP · hexes {' '.join(hexes_of(st, TOWER))}")
    L = f["leader"]
    g = goal_text(st, f)
    bits = [f"{f['name']} · {L['title']} {L['name']} ({label(f)})",
            f"HP {f['hp']}/{max_hp(f)}", f"F{f['force']} C{f['cunning']} W{f['wealth']}",
            f"{f['gp']:,} GP", f"seat {f['seat']}", f"hexes {' '.join(hexes_of(st, f['name']))}"]
    if g:
        bits.append(f"goal: {g}")
    if f["hostile"]:
        bits.append(f"hostile to the tower {f['hostile']} mo")
    elif is_ally(f):
        bits.append("ally")
    return " · ".join(bits)


def seen_assets(st, gm=False):
    sees = tower_sees(st)
    return [a for a in assets_of(st) if gm or visible(st, a, sees)]


def near_morten(st, name):
    h = st["morten"]
    return bool({h, *nbrs(h)} & set(hexes_of(st, name)))


def report(st, t, month):
    """Section 9: plan, what happened, the tower now, next month (the tower's view)."""
    T = st["factions"][TOWER]
    plan = t.plan or ["Morten: no mission. Tower: no action."]
    if not any(p.startswith("Tower:") for p in plan):
        plan.append("Tower: no action.")
    happened, elsewhere, said = [], [], set()
    for e in t.events:
        if e["secret"] or e["text"] in said:
            continue
        said.add(e["text"])
        inv = set(e["involves"])
        close = TOWER in inv or any(n in st["factions"] and (is_ally(st["factions"][n])
                                                             or near_morten(st, n)) for n in inv) \
            or e["action"] == "Fall"
        if close:
            happened.append(e["text"])
        elif e["action"] != "Move":
            elsewhere.append(short(e))
    if elsewhere:
        happened.append("Elsewhere: " + "; ".join(elsewhere) + ".")
    if not happened:
        happened = ["Nothing that reached the tower."]
    return {"month": month, "plan": plan, "happened": happened, "tower": tower_now(st),
            "next": next_month(st)}


def short(e):
    """An event in a few words, for the Elsewhere line."""
    a, t, r = e["action"], e["target"], e["result"]
    own = poss(e["actor"]) + " "
    t = t[len(own):] if t.startswith(own) else t
    if a == "Goal":
        return f"{e['actor']} {'set out to ' + t if r == 'new goal' else 'did: ' + t}"
    verb = {"Buy": "bought", "Attack": "attacked", "Seize": "seized", "Raise": "raised",
            "Repair": "repaired", "Give": "gave", "Mission": "met Morten:"}.get(a, a.lower())
    tail = f" in {e['to_hex']}" if a == "Buy" and e["to_hex"] else ""
    res = f" ({r})" if a in ("Attack", "Seize", "Raise") else ""
    return f"{e['actor']} {verb} {t}{tail}{res}"


def tower_now(st):
    T = st["factions"][TOWER]
    out = [f"HP {T['hp']}/{max_hp(T)} · Force {T['force']} · Cunning {T['cunning']} · Wealth"
           f" {T['wealth']} · {T['gp']:,} GP · Morten level {st['level']}"]
    mine = assets_of(st, TOWER)
    out.append("Assets: " + ("; ".join(asset_line(st, a) for a in mine) if mine else "none"))
    out.append(f"Hexes: {' '.join(hexes_of(st, TOWER))}")
    hos = [f"{n} ({f['hostile']} mo)" for n, f in st["factions"].items() if f["hostile"]]
    out.append("Hostile: " + (", ".join(hos) if hos else "nobody"))
    al = [n for n, f in st["factions"].items() if is_ally(f)]
    out.append("Allies: " + (", ".join(al) if al else "none"))
    ds = [f"{f['dissident']['name']} ({n}, {f['dissident']['hex']})"
          for n, f in st["factions"].items() if f.get("dissident")]
    if ds:
        out.append("Dissidents found: " + ", ".join(ds))
    return out


def next_month(st):
    T = st["factions"][TOWER]
    here = st["morten"]
    out = []
    # threats
    th = hexes_of(st, TOWER) + [a["hex"] for a in assets_of(st, TOWER)]
    sees = tower_sees(st)
    for n, f in st["factions"].items():
        if f["tower"] or not f["hostile"]:
            continue
        near = [a for a in assets_of(st, n) if info(a)["atk"] and visible(st, a, sees)
                and dist_to_set(a["hex"], th) <= info(a)["move"]]
        if near:
            out.append(f"Threat: the {n} are hostile ({f['hostile']} mo) and "
                       + ", ".join(f"{info(a)['name']} {a['id']} in {a['hex']}" for a in near)
                       + " can reach the tower next month.")
        else:
            out.append(f"Threat: the {n} are hostile ({f['hostile']} mo); nothing of theirs is"
                       f" within a move yet.")
    for n, f in st["factions"].items():
        if f["tower"]:
            continue
        g = f["goal"]
        if g and ((g["kind"] == "seize" and st["hexes"][g["hex"]]["holder"] == TOWER)
                  or (g.get("target", "") == f"seat:{TOWER}")
                  or (g.get("target") in st["assets"]
                      and st["assets"][g["target"]]["owner"] == TOWER)):
            out.append(f"Threat: the {n} ({label(f)}) goal: {g['text']}.")
    # chances
    for n, f in st["factions"].items():
        if f["tower"]:
            continue
        if not any(a["hex"] == f["seat"] for a in assets_of(st, n, typ="Force")):
            out.append(f"Chance: the {poss(n)} seat {f['seat']} has no Force asset (Strike it for"
                       f" 2d6 to their HP {f['hp']}/{max_hp(f)}).")
        if f["hp"] < 5:
            out.append(f"Chance: the {n} regime is down to {f['hp']} HP.")
    for a in assets_of(st):
        if a["kind"] == "caravans" and a["owner"] != TOWER and dist(a["hex"], here) <= 1:
            out.append(f"Chance: {aname(a)} on the road in {a['hex']} (Rob: 1d6 and 100 GP).")
    # choices
    out.append(f"Open: Morten is in {hex_label(st, here)}; travel 1 day a hex, d6 each day outside"
               f" {T['seat']} (1 = encounter).")
    ms = []
    holder = st["hexes"][here]["holder"]
    for a in assets_of(st, hex=here):
        if a["owner"] == TOWER or not visible(st, a, sees):
            continue
        ms.append(f"Strike {a['id']} ({info(a)['name']}, T{info(a)['tier']})")
        if info(a)["type"] == "Wealth":
            k = info(a)["tier"] * ROB_GP * (ROB_TREASURY if a["kind"] == "treasury" else 1)
            ms.append(f"Rob {a['id']} (up to {k} GP)")
    if holder != TOWER:
        f = st["factions"][holder]
        if f["seat"] == here and not any(a["hex"] == here for a in assets_of(st, holder, typ="Force")):
            ms.append(f"Strike the {poss(holder)} seat (2d6 to HP)")
        dc = CONTACT_DC + f["cunning"] - (TYRANT_CONTACT if f["leader"]["tag"] == "Tyrant" else 0)
        ms.append(f"Contact the {holder} (Persuasion DC {dc}, or a fight with their Informers)")
    ms.append(f"Delve floor {st['hexes'][here]['level']}")
    out.append("Open: missions here: " + " · ".join(ms) + ".")
    acts = []
    for k, A in ASSETS.items():
        if k == "seditionists":
            if any(f.get("dissident") for f in st["factions"].values()) and T["cunning"] >= A["needs"]:
                acts.append(f"buy Seditionists ({A['cost']:,})")
            continue
        if T[TYPE_ATTR[A["type"]]] >= A["needs"] and not A["land"]:
            acts.append(f"buy {A['name']} ({A['cost']:,})")
    for attr in ("force", "cunning", "wealth"):
        if T[attr] < MAX_RATING:
            acts.append(f"raise {attr.capitalize()} to {T[attr] + 1} ({RAISE[T[attr] + 1]:,})")
    out.append(f"Open: the tower's one action ({T['gp']:,} GP now): " + " · ".join(acts)
               + " · move · attack · seize · repair. Give is free.")
    return out


def reply(st, t, month, gm=False):
    rep = st["report"]
    out = [f"**Month {month} · Domain turn**", "", "**The plan**"]
    out += [f"- {x}" for x in rep["plan"]]
    out += ["", "**What happened**"] + [f"- {x}" for x in rep["happened"]]
    out += ["", "**The tower now**"] + [f"- {x}" for x in rep["tower"]]
    out += ["", "**Next month**"] + [f"- {x}" for x in rep["next"]]
    out += ["", "**Realms**"]
    out += [f"- {faction_line(st, f)}" for n, f in st["factions"].items() if not f["tower"]]
    if st["fallen"]:
        out.append("- Gone: " + ", ".join(f"{x['realm']} (month {x['month']})" for x in st["fallen"]))
    out += ["", "**Income**"] + [f"- {x}" for x in t.income]
    out += ["", "**Log**"] + [f"- {x}" for x, s in t.log if gm or not s]
    hidden = sum(1 for _, s in t.log if s)
    if hidden and not gm:
        out.append(f"- ({hidden} hidden event{'s' if hidden > 1 else ''}: Cunning assets the tower"
                   f" can't see; `--gm` shows them)")
    return "\n".join(out) + "\n"


def summary(st, at=None, gm=False):
    out = [f"**Month {st['month']} · World**", "",
           f"**Morten:** {hex_label(st, st['morten'])} · level {st['level']}", "", "**Factions**"]
    out += [f"- {faction_line(st, f)}" for f in st["factions"].values()]
    if st["fallen"]:
        out.append("- Gone: " + ", ".join(f"{x['realm']} (month {x['month']})" for x in st["fallen"]))
    out += ["", "**Assets**" + (" (GM: all)" if gm else " (what the tower knows)")]
    out += [f"- {asset_line(st, a)}" for a in seen_assets(st, gm)] or ["- none"]
    out += ["", "**Tower**"] + [f"- {x}" for x in tower_now(st)]
    out += ["", "**Next month**"] + [f"- {x}" for x in next_month(st)]
    if at:
        out += ["", f"**Rumours** (from {at})"] + [f"- {r}" for r in rumours(st, at) or ["none"]]
    return "\n".join(out) + "\n"


def rumours(st, at):
    near = {at, *nbrs(at)}
    out = []
    for n, f in st["factions"].items():
        if f["tower"] or not near & set(hexes_of(st, n)):
            continue
        L = f["leader"]
        g = goal_text(st, f) or "nothing yet"
        ev = [e for e in st["events"] if e["actor"] == n and e["action"] != "Move"]
        last = "; ".join(f"{e['action'].lower()} {e['target']} ({e['result']})" for e in ev[:3]) or "quiet"
        out.append(f"Rumour ({n}): {L['title']} {L['name']} ({label(f)}) is after: {g}."
                   f" Last month: {last}. The regime stands at {f['hp']}/{max_hp(f)}.")
    return out


def world_md(st):
    river_of = {}
    for i, r in enumerate(st["rivers"], 1):
        for e in r["edges"]:
            river_of[e] = i
    sees = tower_sees(st)
    out = [f"# World · Month {st['month']}", "",
           f"Seed {st['seed']}. Realms v2. Rendered by `realms.py` from `realms.json` after every"
           " turn; don't edit by hand. Open: what the tower knows (other factions' Cunning assets"
           " show only where the tower has Informers or Morten has been, or once they act against"
           " the tower).", "", "## Factions", ""]
    for f in st["factions"].values():
        out.append(f"- {faction_line(st, f)}")
    if st["fallen"]:
        out.append("- Gone: " + ", ".join(f"{x['realm']} (month {x['month']})" for x in st["fallen"]))
    out += ["", "## Hexes", ""]
    for h in HEXES:
        x = st["hexes"][h]
        rv = [e for e in sorted(river_of, key=EDGES.index) if h in e.split("|")]
        seat = [n for n, f in st["factions"].items() if f["seat"] == h]
        bits = [f"**{h}**", f"L{x['level']}", x["biome"], x["people"], f"held by {x['holder']}",
                f"{hex_income(st, h)} GP"]
        if seat:
            bits.append(f"seat of the {seat[0]}" if seat[0] != TOWER else "the tower")
        if x["lake"]:
            bits.append("lake")
        if rv:
            bits.append("river " + ", ".join(rv))
        out += ["- " + " · ".join(bits), f"  - next to: {' '.join(nbrs(h))}"]
        for a in assets_of(st, hex=h):
            if visible(st, a, sees):
                out.append(f"  - {asset_line(st, a, where=False)}")
    out += ["", "## Rivers", ""]
    for i, r in enumerate(st["rivers"], 1):
        src = "the map's edge" if r["from"] == "edge" else f"the lake in {r['from']}"
        out.append(f"- **River {i}** (from {src}): {' · '.join(r['edges'])}")
    out += ["", "## Asset kinds", "",
            "| Asset | Type | Tier | Needs | Cost | HP | Attack | Counter | Special |",
            "|---|---|---|---|---|---|---|---|---|"]
    for k, A in ASSETS.items():
        atk = f"{A['atk'][0]} vs {A['atk'][1]}, {A['atk'][2]}" if A["atk"] else "none"
        out.append(f"| {A['name']} | {A['type']} | {A['tier']} | {A['type'][0]}{A['needs']} |"
                   f" {A['cost']:,} | {A['hp']} | {atk} | {A['ctr'] or 'none'} | {A['special']} |")
    out += ["", "## Last month", ""] + [f"- {x}" for x in st.get("log") or ["The world begins."]]
    out += ["", "## Month", "", f"- **Next domain turn:** month {st['month']}", ""]
    return "\n".join(out)


def map_json(st, campaign):
    sees = tower_sees(st)
    river_of = [e.split("|") for r in st["rivers"] for e in r["edges"]]
    hexes = []
    for h in HEXES:
        x = st["hexes"][h]
        c, r = hkey(h)
        seat = next((n for n, f in st["factions"].items() if f["seat"] == h), None)
        assets = []
        informed = {a["hex"] for a in assets_of(st, TOWER) if a["kind"] == "informers"}
        for a in assets_of(st, hex=h):
            if not visible(st, a, sees):
                continue
            A = info(a)
            d = {"id": a["id"], "owner": a["owner"], "name": A["name"],
                 "type": A["type"], "tier": A["tier"], "hp": a["hp"],
                 "max_hp": A["hp"], "leader": a.get("leader"),
                 "attack": f"{A['atk'][0]} vs {A['atk'][1]}, {A['atk'][2]}" if A["atk"] else None,
                 "counter": A["ctr"], "special": A["special"]}
            if a["owner"] != TOWER and A["type"] == "Cunning":
                d["seen"] = ("Informers" if h in informed else
                             a.get("seen") if isinstance(a.get("seen"), str) else
                             "Morten was here")
            assets.append(d)
        hexes.append({"id": h, "col": c, "row": r - 1, "level": x["level"], "biome": x["biome"],
                      "people": x["people"], "holder": x["holder"], "lake": x["lake"],
                      "seat_of": seat, "income": hex_income(st, h), "neighbours": nbrs(h),
                      "assets": assets})
    facs = []
    order = [n for n in st["factions"] if n != TOWER] + [TOWER]
    for n in order:
        f = st["factions"][n]
        L = f["leader"]
        lead = ({"name": L["name"], "title": L["title"], "label": None, "tag": None,
                 "verb": None} if f["tower"] else
                {"name": L["name"], "title": L["title"], "label": L["label"], "tag": L["tag"],
                 "verb": VERB[L["tag"]]})
        facs.append({"name": n, "tower": f["tower"], "leader": lead,
                     "income": net_income(st, n),
                     "goal": goal_text(st, f), "hp": f["hp"], "max_hp": max_hp(f),
                     "force": f["force"], "cunning": f["cunning"], "wealth": f["wealth"],
                     "treasury": f["gp"], "seat": f["seat"], "hexes": hexes_of(st, n),
                     "hostile": f["hostile"], "ally": is_ally(f), "disorder": f["disorder"]})
    rep = st.get("report") or {}
    return {"version": VERSION, "campaign": campaign, "month": st["month"],
            "layout": {"cols": 4, "rows": 5, "orientation": "flat-top", "shift": "odd"},
            "hexes": hexes, "rivers": river_of, "factions": facs,
            "morten": {"hex": st["morten"], "level": st["level"]},
            "events": st.get("events", []),
            "report": {"month": rep.get("month", 0),
                       **{k: rep.get(k, []) for k in ("plan", "happened", "tower", "next")}}}


# ---- Commands ----

def load(d):
    p = Path(d) / "realms.json"
    if not p.exists():
        raise Bad(f"no {p}; run new first")
    st = json.loads(p.read_text())
    if st.get("version") != VERSION:
        raise Bad(f"{p} is a Realms v1 world (rulers and mirrors); play it with"
                  " dnd-crunch/tools/realms_v1.py, or start a v2 world with new")
    return st


def save(d, st):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    (d / "realms.json").write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n")
    (d / "world.md").write_text(world_md(st))
    (d / "map.json").write_text(json.dumps(map_json(st, d.name), indent=1, ensure_ascii=False) + "\n")


def cmd_new(a):
    d = Path(a.campaign)
    if (d / "realms.json").exists() and not a.force:
        raise Bad(f"{d / 'realms.json'} exists; use --force to overwrite")
    st = generate(a.seed, a.level)
    st["report"] = {"month": 0, "plan": [], "happened": ["Month 1: the world begins."],
                    "tower": tower_now(st), "next": next_month(st)}
    save(d, st)
    rng, mons = random.Random(a.seed), load_monsters()
    out = ["# GM secrets · dungeon floors", "",
           f"Floor N lies under the level-N hex (seed {a.seed}, the same floors as"
           f" `gen_dungeon.py --seed {a.seed}`). Mark rooms explored as Morten reaches them."
           " The realms' hidden Cunning assets are in `realms.json`"
           " (`realms.py show --gm`).", ""]
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
    print(summary(st, at, a.gm), end="")


def cmd_encounter(a):
    st = load(a.campaign)
    level = a.level or st["level"]
    if a.asset:
        s = a.asset.strip()
        if s.lower().startswith("a") and s[1:].isdigit():
            x = st["assets"].get(s.lower())
            if not x:
                raise Bad(f"no asset '{s}'")
            print("\n".join(fight_lines(st, x, level)))
            rob = (f" · Rob: 1d6 to it and up to {info(x)['tier'] * ROB_GP * (ROB_TREASURY if x['kind'] == 'treasury' else 1)}"
                   f" GP from the {x['owner']}" if info(x)["type"] == "Wealth" else "")
            print(f"- Win: Strike 2d6 to it{rob}")
        else:
            t = Turn(st)
            name = t.realm(s)
            print("\n".join(fight_lines(st, name, level)))
            g = [x["id"] for x in assets_of(st, name, st["factions"][name]["seat"], "Force")]
            print(f"- Win: 2d6 to the {poss(name)} HP" + (f" (only once {', '.join(g)} {'is' if len(g) == 1 else 'are'} gone)" if g else ""))
        return
    if a.contact:
        h = a.contact.upper()
        if h not in st["hexes"]:
            raise Bad(f"no hex '{a.contact}'")
        name = st["hexes"][h]["holder"]
        if name == TOWER:
            raise Bad(f"{h} is the tower's")
        f = st["factions"][name]
        inf = [x for x in assets_of(st, name, h) if x["kind"] == "informers"]
        if inf:
            print(f"**Contact · {hex_label(st, h)}** (GM: the {poss(name)} Informers {inf[0]['id']} are"
                  " here: the Contact is a fight)\n")
            print("\n".join(fight_lines(st, inf[0], level)))
        else:
            dc = CONTACT_DC + f["cunning"] - (TYRANT_CONTACT if f["leader"]["tag"] == "Tyrant" else 0)
            print(f"**Contact · {hex_label(st, h)}**: Persuasion (CHA) DC {dc}"
                  f" (10 + {L(f)} Cunning {f['cunning']}"
                  + (f" − {TYRANT_CONTACT} Tyrant" if f["leader"]["tag"] == "Tyrant" else "") + ")")
        return
    if not a.hex:
        raise Bad("encounter needs --asset, --hex or --contact")
    h = a.hex.upper()
    if h not in st["hexes"]:
        raise Bad(f"no hex '{a.hex}' (A1–D5)")
    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(10 ** 6)
    e = encounter(st["hexes"][h]["level"], random.Random(seed))
    print(f"**Wandering encounter · {hex_label(st, h)}** (seed {seed})\n")
    print(f"- {e['count']}× {e['name']} · CR {e['cr']} · {e['xp']:,} XP each")
    print(f"- {e['total']:,} XP total · {e['diff']} · coins {e['total'] // 10:,} GP")


def L(f):
    return f"{f['leader']['title']} {f['leader']['name']}'s"


def cmd_turn(a):
    st = load(a.campaign)
    t = Turn(st)
    month = t.run(a)
    st["report"] = report(st, t, month)
    print(reply(st, t, month, a.gm), end="")
    if a.dry_run:
        print("\n(dry run: nothing saved)")
    else:
        save(a.campaign, st)


def sim_one(seed, months, verbose=False):
    st = generate(seed)
    o = argparse.Namespace(**PASSIVE)
    start = {n: (f["leader"]["tag"], len(hexes_of(st, n))) for n, f in st["factions"].items()
             if n != TOWER}
    stats, rulers = Counter(), {n: 0 for n in start}
    maxh = Counter()
    for _ in range(months):
        t = Turn(st)
        before = {n: f["leader"]["name"] for n, f in st["factions"].items()}
        month = t.run(o)
        st["report"] = report(st, t, month)
        stats += t.stats
        for n, f in st["factions"].items():
            if n in before and before[n] != f["leader"]["name"]:
                rulers[n] += 1
            maxh[n] = max(maxh[n], len(hexes_of(st, n)))
        if verbose:
            print(reply(st, t, month, gm=True))
    end = {n: (f["leader"]["tag"], len(hexes_of(st, n)), f["hp"], max_hp(f), f["gp"],
               len(assets_of(st, n))) for n, f in st["factions"].items()}
    return st, stats, start, end, rulers, maxh


def cmd_sim(a):
    if a.seed is not None:
        seeds = [a.seed]
    else:
        lo, _, hi = a.seeds.partition("-")
        seeds = list(range(int(lo), int(hi or lo) + 1))
    tot = Counter()
    rows = []
    conq, stew = [], []
    for s in seeds:
        st, stats, start, end, rulers, maxh = sim_one(s, a.months, a.verbose)
        tot += stats
        T = st["factions"][TOWER]
        for n, (tag, h0) in start.items():
            h1 = end[n][1] if n in end else 0
            if tag == "Conqueror":
                conq.append((h0, maxh[n], h1))
            if tag == "Steward":
                stew.append((h0, h1))
        falls = stats["falls"] - stats["tower_sacked"]
        rows.append(f"seed {s:>3}: falls {falls} · realms gone {stats['realm_gone']} · hexes"
                    f" seized {stats['seized']} · upkeep losses {stats['upkeep_loss']} · tower"
                    f" attacked {stats['tower_attacked']}, sacked {stats['tower_sacked']}, hexes"
                    f" lost {stats['tower_lost']} · tower end HP {T['hp']}/{max_hp(T)}"
                    f" {T['gp']:,} GP")
        if a.seed is not None:
            print("\nEnd:")
            for n, (tag, h, hp, mhp, gp, na) in end.items():
                print(f"  {n:<10} {tag:<10} hexes {h} · HP {hp}/{mhp} · {gp:,} GP · {na} assets")
    n = len(seeds)
    falls = tot["falls"] - tot["tower_sacked"]
    print("\n".join(rows))
    print(f"\n=== {n} seeds × {a.months} months (passive tower) ===")
    print(f"Regime falls: {falls} ({falls / n:.1f} a world, {falls / n / a.months * 12:.2f} a world-year)"
          f" · realms gone: {tot['realm_gone']}")
    print(f"Hexes seized: {tot['seized']} ({tot['seized'] / n:.1f} a world) · attacks"
          f" {tot['attacks'] / n:.0f} · buys {tot['buys'] / n:.0f} · raises {tot['raises'] / n:.0f}"
          f" · regime HP lost {tot['hp_damage'] / n:.0f} in {tot['hp_hits'] / n:.0f} hits"
          f" · goals done {tot['goals_done'] / n:.1f} · dropped {tot['goal_drop'] / n:.1f} a world")
    print(f"Upkeep: assets lost {tot['upkeep_loss']} ({tot['upkeep_loss'] / n:.1f} a world) · GP"
          f" paid {tot['upkeep_paid'] / n:,.0f} a world, {tot['upkeep_paid'] / max(1, tot['income']):.0%}"
          f" of the realms' income")
    if conq:
        print("Conquerors (start → most → end hexes): " + ", ".join(f"{a}→{b}→{c}" for a, b, c in conq))
    if stew:
        print("Stewards (start → end hexes): " + ", ".join(f"{a}→{b}" for a, b in stew))
    print(f"Tower at rest: attacked {tot['tower_attacked']} times ({tot['tower_attacked'] / n:.1f}"
          f" a world) · sacked {tot['tower_sacked']} · hexes lost {tot['tower_lost']}")


def main():
    ap = argparse.ArgumentParser(description="Realms v2 overworld engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--campaign", required=True)
    p.add_argument("--level", type=int, default=4, help="Morten's level")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("show")
    p.add_argument("--campaign", required=True)
    p.add_argument("--at")
    p.add_argument("--gm", action="store_true", help="also the hidden Cunning assets")
    p = sub.add_parser("encounter")
    p.add_argument("--campaign", required=True)
    p.add_argument("--asset", help="an asset id (a7), or a realm for its unguarded seat")
    p.add_argument("--hex", help="a wandering encounter for the hex's level")
    p.add_argument("--contact", help="HEX: the Contact check, or the fight with Informers")
    p.add_argument("--level", type=int, help="Morten's level (default: the campaign's)")
    p.add_argument("--seed", type=int)
    p = sub.add_parser("turn")
    p.add_argument("--campaign", required=True)
    p.add_argument("--at", help="Morten's hex at the end of his month")
    p.add_argument("--level", type=int, help="Morten's level now")
    p.add_argument("--strike", help="asset id, or REALM for its unguarded seat (a won Strike)")
    p.add_argument("--rob", help="asset id of a Wealth asset (a won Rob)")
    p.add_argument("--contact", action="store_true", help="a won Contact in Morten's hex")
    p.add_argument("--delve", action="store_true", help="Morten delved this month")
    p.add_argument("--keep-loot", action="store_true")
    p.add_argument("--deposit", type=int, default=0)
    p.add_argument("--withdraw", type=int, default=0)
    p.add_argument("--give", action="append", default=[], help="REALM=GP (free; repeatable)")
    p.add_argument("--action", help="the tower's one action (see the usage)")
    p.add_argument("--plan", action="append", default=[], help="a line for The plan: why")
    p.add_argument("--gm", action="store_true", help="show the hidden events too")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("sim")
    p.add_argument("--seeds", default="1-10")
    p.add_argument("--seed", type=int)
    p.add_argument("--months", type=int, default=24)
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
