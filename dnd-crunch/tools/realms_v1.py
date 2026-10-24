#!/usr/bin/env python3
"""Realms: the overworld engine for D&D Crunch (rules: dnd-crunch/realms.md).

A 4×5 hex map of six realms, played as monthly domain turns. The campaign's realms.json is
the state and this script owns it; world.md is rendered from it after every change.

Usage:
  python3 dnd-crunch/tools/realms.py new --seed 7 --campaign DIR [--force]
  python3 dnd-crunch/tools/realms.py show --campaign DIR [--at C3]
  python3 dnd-crunch/tools/realms.py encounter --campaign DIR --hex C3 [--seed N]
  python3 dnd-crunch/tools/realms.py turn --campaign DIR [--at HEX] [--strike Orcs:ruler]
      [--rob HEX [--keep-loot]] [--deposit GP] [--withdraw GP] [--fund Orcs:mirror=200]
      [--recruit Elves] [--action conquer:C3|build] [--court conquer=1,defend=1,coup:Orcs=2]
      [--dry-run]
  python3 dnd-crunch/tools/realms.py sim --seed 7 --months 24 [--quiet]
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ noise in the repo
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_dungeon import encounter, floor, floor_md, load_monsters  # noqa: E402

# ---- Constants (realms.md section 10). Change both together. ----
COLS, ROWS = "ABCD", 5
N_REALMS, REALM_SIZE, N_VICIOUS = 6, 3, 4
N_RIVERS, RIVER_LEN, N_LAKES = 2, (3, 6), 2
INCOME = 10            # GP per hex level per month
CRUEL_INCOME = 1.5     # Cruel ruler's income multiplier
SKIM = 0.20            # mirror's cut of its ruler's income, taken out of the ruler's share
UPKEEP_FORCE = 7       # upkeep is Force² × this, GP per month (rulers, tower)
UPKEEP_OFFICER = 5     # GP per court officer per month
BUILD = 100            # Build costs new value × BUILD
RAID = 30              # Raid takes target hex level × RAID GP
ROB = 50               # Morten's Rob takes hex level × ROB GP
STRIKE = 3             # bonus to every roll against a struck faction this month
CLAIM, RIVER = 1, 1    # attacker on a hex of its people / defender across a river edge
BEAT = 0               # "can beat": own Force ≥ the defender's Force + BEAT
DIE = 10               # battle and coup die
BATTLE_LOSS = 1        # Force the loser of a battle loses
ENSLAVE_EXTRA = 1      # and 1 more when an Enslave wins
CRUEL_COUP = 1         # mirror's coup bonus against a Cruel ruler
COUP_FAIL = 1          # failed coup: mirror loses this much Cunning
COUP_DEMOTE = 2        # deposed ruler's Cunning is divided by this (round down)
RECRUIT = 100          # recruit costs new court size × RECRUIT
POOL_CAP, POOL_HIGH = 4, 2   # court pool: 1 per officer up to POOL_CAP, then POOL_HIGH each
OFFICER_DEATH = 1      # a lost backed roll kills an officer on d6 ≤ this
START_DIV = 10         # ruler Force = Cunning = S ÷ START_DIV (rounded, min 1)
START_GP = 10          # ruler Treasury = S × START_GP
MIRROR_GAP = 2         # mirror Cunning = ruler's − MIRROR_GAP (min 1)
TOWER_FORCE, TOWER_GP, TOWER_OFFICERS = 1, 100, 1

BIOMES = {1: ["tundra", "taiga", "mountains"],
          2: ["taiga", "hills", "mountains", "forest"],
          3: ["forest", "plains", "hills", "swamp"],
          4: ["plains", "forest", "swamp", "hills", "savanna"],
          5: ["desert", "savanna", "jungle", "mountains"]}
VICIOUS = ["Greedy", "Rapacious", "Brutal", "Cruel"]
GOOD = ["Neutral", "Altruistic"]
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
TOWER_FOLK = "tower folk"
RUMOUR = {  # the tag in plain words
    "Greedy": "hungers for the deepest ley land in reach",
    "Rapacious": "eyes the fattest treasury next door",
    "Brutal": "drags the weak off to fill the ranks",
    "Cruel": "squeezes the realm's own people and builds",
    "Neutral": "keeps to the realm's own land and builds",
    "Altruistic": "would break vicious neighbours",
}


class Bad(Exception):
    """A bad input: one-line error, no state change."""


# ---- Map ----

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


def verts(e):
    """An edge's two end vertices: 3-hex sets inside the map, ("out", e, i) on its rim."""
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
    """One river by random walk: a list of edges, or None."""
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


def river_ok(r, lakes):
    """Recheck a river: length, real edges, consecutive, no vertex twice, rim/lake ends."""
    es = r["edges"]
    if not RIVER_LEN[0] <= len(es) <= RIVER_LEN[1] or len(set(es)) != len(es):
        return False
    if any(e not in EDGES for e in es):
        return False
    shared = []
    for a, b in zip(es, es[1:]):
        s = set(verts(a)) & set(verts(b))
        if len(s) != 1:
            return False
        shared.append(s.pop())
    first = other(es[0], shared[0])
    last = other(es[-1], shared[-1])
    vs = [first] + shared + [last]
    if len(set(vs)) != len(vs) or not rim(last):
        return False
    if r["from"] == "edge":
        return rim(first)
    return r["from"] in lakes and r["from"] in es[0].split("|")


# ---- World generation ----

def name_for(st, people, rng):
    used = {f.get("leader") for R in st["realms"].values() for f in (R["ruler"], R["mirror"])}
    used |= {o["name"] for o in st["tower"]["officers"]}
    free = [n for n in PEOPLES[people][1] if n not in used]
    if free:
        return rng.choice(free)
    base, k = rng.choice(PEOPLES[people][1]), 2
    while f"{base} {k}" in used:
        k += 1
    return f"{base} {k}"


def leader(st, people, rng, tag):
    return {"leader": name_for(st, people, rng), "title": rng.choice(PEOPLES[people][0]),
            "tag": tag}


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


def generate(seed):
    rng = random.Random(seed)
    levels = list(range(1, len(HEXES) + 1))
    rng.shuffle(levels)
    level = dict(zip(HEXES, levels))
    tower = next(h for h in HEXES if level[h] == 1)
    realms = carve(rng, [h for h in HEXES if h != tower], level)
    peoples = list(PEOPLES)
    rng.shuffle(peoples)
    st = {"seed": seed, "month": 1, "rng": 0, "hexes": {}, "rivers": [], "realms": {},
          "fallen": [], "tower": {"hex": tower, "force": TOWER_FORCE, "gp": TOWER_GP,
                                  "officers": [], "morten": tower, "events": []}}
    for h in HEXES:
        st["hexes"][h] = {"level": level[h], "biome": rng.choice(BIOMES[hkey(h)[1]]),
                          "people": TOWER_FOLK, "holder": "tower", "lake": False}
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
    good = set(rng.sample(peoples, N_REALMS - N_VICIOUS))
    for people in peoples:
        st["realms"][people] = {"ruler": {}, "mirror": {}, "war": False, "events": []}
    for people in peoples:
        R = st["realms"][people]
        s = sum(level[h] for h in HEXES if st["hexes"][h]["holder"] == people)
        c = max(1, int(s / START_DIV + 0.5))
        rt, mt = (GOOD, VICIOUS) if people in good else (VICIOUS, GOOD)
        R["ruler"] = leader(st, people, rng, rng.choice(rt))
        R["ruler"].update(force=c, cunning=c, gp=s * START_GP)
        R["mirror"] = leader(st, people, rng, rng.choice(mt))
        R["mirror"].update(cunning=max(1, c - MIRROR_GAP), gp=0)
    for _ in range(TOWER_OFFICERS):
        st["tower"]["officers"].append({"name": name_for(st, "Humans", rng), "people": "Humans"})
    st["rng"] = rng.getrandbits(32)
    check(st)
    return st


def check(st):
    """Fail loudly if the world breaks a constraint."""
    def fail(msg):
        raise SystemExit(f"error: constraint broken: {msg}")
    hx = st["hexes"]
    if sorted(x["level"] for x in hx.values()) != list(range(1, len(HEXES) + 1)):
        fail("levels are not 1–20 once each")
    t = st["tower"]["hex"]
    if hx[t]["level"] != 1 or hx[t]["holder"] != "tower":
        fail("tower is not on the level 1 hex")
    sizes = []
    for name in st["realms"]:
        mine = [h for h in HEXES if hx[h]["holder"] == name]
        seen, todo = set(), mine[:1]
        while todo:
            h = todo.pop()
            seen.add(h)
            todo += [n for n in nbrs(h) if n in mine and n not in seen]
        if seen != set(mine):
            fail(f"{name} is not contiguous")
        sizes.append(len(mine))
    if sorted(sizes) != [REALM_SIZE] * (N_REALMS - 1) + [REALM_SIZE + 1]:
        fail(f"realm sizes {sorted(sizes)}")
    lakes = [h for h in HEXES if hx[h]["lake"]]
    if len(lakes) != N_LAKES:
        fail("lake count")
    if len(st["rivers"]) != N_RIVERS:
        fail("river count")
    for i, r in enumerate(st["rivers"], 1):
        if not river_ok(r, lakes):
            fail(f"river {i} is malformed: {r}")
    es = [e for r in st["rivers"] for e in r["edges"]]
    if len(set(es)) != len(es):
        fail("rivers share an edge")
    names = [f["leader"] for R in st["realms"].values() for f in (R["ruler"], R["mirror"])]
    names += [o["name"] for o in st["tower"]["officers"]]
    if len(set(names)) != len(names):
        fail("names are not unique")


# ---- Shared views ----

def hexes_of(st, side):
    return [h for h in HEXES if st["hexes"][h]["holder"] == side]


def realm_s(st, name):
    return sum(st["hexes"][h]["level"] for h in hexes_of(st, name))


def pool(n):
    return min(n, POOL_CAP) + POOL_HIGH * max(0, n - POOL_CAP)


def allies(st):
    return [n for n, R in sorted(st["realms"].items())
            if R["ruler"]["tag"] in GOOD and not R["war"]]


def hex_label(st, h):
    x = st["hexes"][h]
    holder = "tower" if x["holder"] == "tower" else x["holder"]
    return f"{h} (L{x['level']}, {x['biome']}, {holder})"


def realm_line(st, name):
    R = st["realms"][name]
    r, m = R["ruler"], R["mirror"]
    war = " · at war with the tower" if R["war"] else ""
    return (f"{name} · {r['leader']} ({r['tag']}) F{r['force']} C{r['cunning']} {r['gp']:,} GP"
            f" · {' '.join(hexes_of(st, name))} · mirror {m['leader']} ({m['tag']})"
            f" C{m['cunning']} {m['gp']:,} GP{war}")


def tower_line(st):
    T = st["tower"]
    wars = ", ".join(n for n, R in sorted(st["realms"].items()) if R["war"]) or "none"
    return f"F{T['force']} · {T['gp']:,} GP · hexes {' '.join(hexes_of(st, 'tower'))} · wars: {wars}"


def court_line(st):
    offs = st["tower"]["officers"]
    names = ", ".join(f"{o['name']} ({o['people']})" for o in offs) or "empty"
    return f"{names} · pool {pool(len(offs))}"


def rumours(st, at):
    near = {at} | set(nbrs(at))
    out = []
    for name, R in sorted(st["realms"].items()):
        if not near & set(hexes_of(st, name)):
            continue
        r, m = R["ruler"], R["mirror"]
        ev = "; ".join(R["events"]) or "quiet"
        threat = m["cunning"] + (CRUEL_COUP if r["tag"] == "Cruel" else 0)
        mood = "plots a coup" if threat >= r["cunning"] else "gathers support"
        out.append(f"Rumour ({name}): {r['title']} {r['leader']} ({r['tag']}) {RUMOUR[r['tag']]}."
                   f" Last month: {ev}. Rival {m['title']} {m['leader']} ({m['tag']}) {mood},"
                   f" Cunning {m['cunning']} vs {r['cunning']}.")
    return out


def summary(st, at=None):
    T = st["tower"]
    out = [f"**Month {st['month']} · World**", "",
           f"**Morten:** {hex_label(st, T['morten'])}", "", "**Realms**"]
    out += [f"- {realm_line(st, n)}" for n in sorted(st["realms"])]
    if st["fallen"]:
        out.append("- Fallen: " + ", ".join(f"{f['realm']} (month {f['month']})"
                                            for f in st["fallen"]))
    out += ["", f"**Tower:** {tower_line(st)}", "", f"**Court:** {court_line(st)}", "",
            "**Hexes**"]
    for h in HEXES:
        x = st["hexes"][h]
        held = "" if x["holder"] == x["people"] or x["holder"] == "tower" else f", held by {x['holder']}"
        who = "tower" if x["holder"] == "tower" else x["people"] + held
        out.append(f"- {h} L{x['level']} {x['biome']} · {who}{' · lake' if x['lake'] else ''}")
    out += ["", "**Rivers**"]
    out += [f"- River {i}: {' · '.join(r['edges'])}" for i, r in enumerate(st["rivers"], 1)]
    if at:
        rs = rumours(st, at)
        out += ["", f"**Rumours** (from {at})"] + [f"- {r}" for r in rs or ["none"]]
    return "\n".join(out) + "\n"


def world_md(st):
    T = st["tower"]
    river_of = {}
    for i, r in enumerate(st["rivers"], 1):
        for e in r["edges"]:
            river_of[e] = i
    out = [f"# World · Month {st['month']}", "",
           f"Seed {st['seed']}. Rendered by `realms.py` from `realms.json` after every turn;"
           " don't edit by hand.", "", "## Hexes", ""]
    for h in HEXES:
        x = st["hexes"][h]
        holder = "tower" if x["holder"] == "tower" else x["holder"]
        rv = [e for e in sorted(river_of, key=EDGES.index) if h in e.split("|")]
        bits = [f"**{h}**", f"L{x['level']}", x["biome"], x["people"], f"held by {holder}"]
        if x["lake"]:
            bits.append("lake")
        if rv:
            bits.append("river " + ", ".join(rv))
        out += ["- " + " · ".join(bits), f"  - next to: {' '.join(nbrs(h))}"]
    out += ["", "## Rivers", ""]
    for i, r in enumerate(st["rivers"], 1):
        src = "the map's edge" if r["from"] == "edge" else f"the lake in {r['from']}"
        out.append(f"- **River {i}** (from {src}): {' · '.join(r['edges'])}")
    out += ["", "## Realms", ""] + [f"- {realm_line(st, n)}" for n in sorted(st["realms"])]
    if st["fallen"]:
        out.append("- Fallen: " + ", ".join(f"{f['realm']} (month {f['month']})"
                                            for f in st["fallen"]))
    out += ["", "## Factions"]
    for n, R in sorted(st["realms"].items()):
        r, m = R["ruler"], R["mirror"]
        out += ["", f"### {n}", "",
                f"- **Ruler:** {r['title']} {r['leader']} · {r['tag']} · Force {r['force']}"
                f" · Cunning {r['cunning']} · {r['gp']:,} GP",
                f"- **Mirror:** {m['title']} {m['leader']} · {m['tag']} · Cunning {m['cunning']}"
                f" · {m['gp']:,} GP",
                f"- **Hexes:** {' '.join(hexes_of(st, n))} · levels {realm_s(st, n)}",
                f"- **At war with the tower:** {'yes' if R['war'] else 'no'}"]
    out += ["", "## Tower", "",
            f"- **Force** {T['force']} · **Treasury** {T['gp']:,} GP",
            f"- **Hexes:** {' '.join(hexes_of(st, 'tower'))}",
            "- **Wars:** " + (", ".join(n for n, R in sorted(st["realms"].items()) if R["war"])
                              or "none"),
            f"- **Morten:** {hex_label(st, T['morten'])}",
            "", "## Court", ""]
    out += [f"- {o['name']} ({o['people']})" for o in T["officers"]] or ["- empty"]
    out += [f"- **Pool:** {pool(len(T['officers']))}", "", "## Month", "",
            f"- **Next domain turn:** month {st['month']}", ""]
    return "\n".join(out)


# ---- The domain turn ----

PASSIVE = dict(at=None, strike=None, rob=None, keep_loot=False, deposit=0, withdraw=0,
               fund=[], recruit=[], action=None, court=None)


class Turn:
    def __init__(self, st):
        self.st = st
        self.rng = random.Random(st["rng"])
        self.rivers = {e for r in st["rivers"] for e in r["edges"]}
        self.log, self.income = [], []
        self.struck, self.funded = set(), set()
        self.court = {"conquer": 0, "defend": 0, "coup": {}}
        self.coups, self.stats = [], Counter()

    # -- helpers --
    def d(self, n):
        return self.rng.randint(1, n)

    def pick(self, opts, what):
        if len(opts) == 1:
            return opts[0], ""
        k = self.d(len(opts))
        return opts[k - 1], f" ({what} tie: d{len(opts)} {k})"

    def holder(self, h):
        return self.st["hexes"][h]["holder"]

    def force(self, side):
        return self.st["tower"]["force"] if side == "tower" else self.ruler(side)["force"]

    def set_force(self, side, v):
        (self.st["tower"] if side == "tower" else self.ruler(side))["force"] = max(0, v)

    def gp(self, side):
        return self.st["tower"]["gp"] if side == "tower" else self.ruler(side)["gp"]

    def add_gp(self, side, v):
        (self.st["tower"] if side == "tower" else self.ruler(side))["gp"] += v

    def ruler(self, name):
        return self.st["realms"][name]["ruler"]

    def mirror(self, name):
        return self.st["realms"][name]["mirror"]

    def nm(self, side):
        return "Tower" if side == "tower" else side

    def head(self, name):
        r = self.ruler(name)
        return f"{name} ({r['leader']}, {r['tag']})"

    def event(self, side, text):
        if side == "tower":
            self.st["tower"]["events"].append(text)
        else:
            self.st["realms"][side]["events"].append(text)

    def war(self, name):
        if name != "tower" and not self.st["realms"][name]["war"]:
            self.st["realms"][name]["war"] = True
            return f" War: tower vs {name}."
        return ""

    def realm(self, s):
        for n in self.st["realms"]:
            if n.lower() == s.lower():
                return n
        if any(f["realm"].lower() == s.lower() for f in self.st["fallen"]):
            raise Bad(f"{s} has fallen")
        raise Bad(f"no realm '{s}' (realms: {', '.join(sorted(self.st['realms']))})")

    def hexarg(self, s):
        h = s.upper()
        if h not in self.st["hexes"]:
            raise Bad(f"no hex '{s}' (A1–D5)")
        return h

    def faction(self, s):
        realm, _, role = s.partition(":")
        if role not in ("ruler", "mirror"):
            raise Bad(f"'{s}': want REALM:ruler or REALM:mirror")
        return self.realm(realm), role

    def court_risk(self, why):
        offs = self.st["tower"]["officers"]
        k = self.d(6)
        line = f"Court risk ({why}): d6 {k}"
        if k <= OFFICER_DEATH and offs:
            o, note = self.pick(offs, "officer")
            offs.remove(o)
            line += f", {o['name']} ({o['people']}) dies{note}. Court {len(offs)}."
            self.stats["officer_deaths"] += 1
        else:
            line += ", no loss."
        self.log.append(line)

    def build(self, side, role, stat, head):
        f = self.st["tower"] if side == "tower" else self.st["realms"][side][role]
        cost = (f[stat] + 1) * BUILD
        if f["gp"] < cost:
            return None
        f["gp"] -= cost
        f[stat] += 1
        word = stat.capitalize()
        self.log.append(f"{head}: Build {word} {f[stat] - 1} → {f[stat]}, −{cost:,} GP"
                        f" ({f['gp'] + cost:,} → {f['gp']:,}).")
        if side != "tower":
            who = "rival" if role == "mirror" else ""
            self.event(side, f"{who + ' ' if who else ''}built {word} to {f[stat]}")
        self.stats[f"build_{stat}"] += 1
        return True

    def build_or_save(self, side, role, stat, head):
        if not self.build(side, role, stat, head):
            f = self.st["realms"][side][role]
            self.log.append(f"{head}: saves ({f['gp']:,} GP; {stat.capitalize()} {f[stat] + 1}"
                            f" costs {(f[stat] + 1) * BUILD:,}).")

    # -- battle --
    def battle(self, att, dfn, target, kind, head):
        hx = self.st["hexes"][target]
        origins = [h for h in nbrs(target) if self.holder(h) == att]
        dry = [h for h in origins if edge(h, target) not in self.rivers]
        origin, note = self.pick(dry or origins, "origin")
        am, dm = [], []
        if att != "tower" and hx["people"] == att:
            am.append((CLAIM, "claim"))
        if (dfn, "ruler") in self.struck:
            am.append((STRIKE, "strike"))
        backed = False
        if att == "tower" and self.court["conquer"]:
            am.append((self.court["conquer"], "court"))
            backed = True
        if not dry:
            dm.append((RIVER, "river"))
        if (att, "ruler") in self.struck:
            dm.append((STRIKE, "strike"))
        if dfn == "tower" and self.court["defend"]:
            dm.append((self.court["defend"], "court"))
            self.court["defend"] = 0
            backed = True
        fa, fd = self.force(att), self.force(dfn)
        ra, rd = self.d(DIE), self.d(DIE)
        ta, td = ra + fa + sum(m for m, _ in am), rd + fd + sum(m for m, _ in dm)
        win = ta > td
        mods = lambda ms: "".join(f" + {m} {w}" for m, w in ms)
        line = (f"{head} from {origin}{note} → d{DIE} {ra} + F{fa}{mods(am)} = {ta} vs d{DIE} {rd}"
                f" + F{fd}{mods(dm)} = {td}, {'WIN' if win else 'LOSS'}.")
        loser = dfn if win else att
        loss = BATTLE_LOSS + (ENSLAVE_EXTRA if kind == "enslave" and win else 0)
        fx = []
        if kind == "conquer" and win:
            hx["holder"] = att
            fx.append(f"{target} → {self.nm(att)}.")
            self.event(att, f"took {target} from {self.nm(dfn)}")
            self.event(dfn, f"lost {target} to {self.nm(att)}")
            if dfn == "tower":
                self.stats["tower_lost"] += 1
        elif kind == "raid" and win:
            amt = min(hx["level"] * RAID, self.gp(dfn))
            self.add_gp(dfn, -amt)
            self.add_gp(att, amt)
            fx.append(f"Takes {amt:,} GP ({self.nm(dfn)} {self.gp(dfn) + amt:,} → {self.gp(dfn):,}).")
            self.event(att, f"raided {self.nm(dfn)} for {amt:,} GP")
            self.event(dfn, f"was raided by {self.nm(att)} for {amt:,} GP")
            if dfn == "tower":
                self.stats["tower_raided"] += 1
        elif kind == "enslave" and win:
            self.set_force(att, fa + 1)
            fx.append(f"{self.nm(att)} F{fa} → {fa + 1}.")
            self.event(att, f"enslaved {self.nm(dfn)}'s people as soldiers")
            self.event(dfn, f"lost people to {self.nm(att)}'s slavers")
            if dfn == "tower":
                self.stats["tower_enslaved"] += 1
        elif not win:
            self.event(att, f"failed to {kind} {self.nm(dfn)} at {target}")
            self.event(dfn, f"beat off {self.nm(att)} at {target}")
        old = self.force(loser)
        self.set_force(loser, old - loss)
        fx.append(f"{self.nm(loser)} F{old} → {self.force(loser)}.")
        if "tower" in (att, dfn):
            fx.append(self.war(dfn if att == "tower" else att).strip())
        self.log.append(" ".join([line] + [x for x in fx if x]))
        self.stats[kind] += 1
        if backed and loser == "tower":
            self.court_risk(f"backed {kind} lost")

    # -- steps --
    def morten(self, o):
        st, T = self.st, self.st["tower"]
        if o.at:
            T["morten"] = self.hexarg(o.at)
        if o.strike and o.rob:
            raise Bad("one mission a month: --strike or --rob, not both")
        if o.keep_loot and not o.rob:
            raise Bad("--keep-loot needs --rob")
        if o.rob:
            h = self.hexarg(o.rob)
            if o.at and T["morten"] != h:
                raise Bad(f"--rob {h} but --at {T['morten']}: Morten robs where he is")
            name = self.holder(h)
            if name == "tower":
                raise Bad(f"{h} is the tower's; no ruler to rob")
            r = self.ruler(name)
            if r["tag"] not in VICIOUS:
                raise Bad(f"Rob only a vicious ruler: {name} ruler {r['leader']} is {r['tag']}")
            T["morten"] = h
            amt = min(st["hexes"][h]["level"] * ROB, r["gp"])
            r["gp"] -= amt
            where = "Morten keeps it" if o.keep_loot else f"tower {T['gp']:,} → {T['gp'] + amt:,}"
            if not o.keep_loot:
                T["gp"] += amt
            self.log.append(f"Morten: Rob {name} ({r['leader']}) in {h} (L{st['hexes'][h]['level']})"
                            f" → {amt:,} GP ({name} {r['gp'] + amt:,} → {r['gp']:,}), {where}.")
            self.event(name, f"was robbed of {amt:,} GP by the wizard")
        if o.strike:
            name, role = self.faction(o.strike)
            here = T["morten"]
            if self.holder(here) != name:
                raise Bad(f"Strike needs Morten in a hex of {name}; he is at {here} (use --at HEX)")
            self.struck.add((name, role))
            f = self.st["realms"][name][role]
            war = self.war(name) if role == "ruler" else ""
            self.log.append(f"Morten: Strike on {name} {role} {f['leader']} in {here}: +{STRIKE}"
                            f" to every roll against {f['leader']} this month.{war}")
            self.event(name, f"the wizard struck {'ruler' if role == 'ruler' else 'rival'}"
                             f" {f['leader']}")
        if o.deposit:
            if o.deposit < 0:
                raise Bad("--deposit must be positive")
            T["gp"] += o.deposit
            self.log.append(f"Morten: deposit {o.deposit:,} GP → tower {T['gp']:,} GP.")
        if o.withdraw:
            if not 0 < o.withdraw <= T["gp"]:
                raise Bad(f"--withdraw {o.withdraw:,}: tower holds {T['gp']:,} GP")
            T["gp"] -= o.withdraw
            self.log.append(f"Morten: withdraw {o.withdraw:,} GP → tower {T['gp']:,} GP.")

    def upkeep(self, f, extra=0):
        """Pay Force² × UPKEEP_FORCE (+ extra); short of gold, disband Force until it can."""
        cost = lambda: f["force"] ** 2 * UPKEEP_FORCE + extra
        old, up = f["force"], cost()
        while f["force"] and f["gp"] < cost():
            f["force"] -= 1
        paid = min(cost(), f["gp"])
        f["gp"] -= paid
        if f["force"] == old and paid == up:
            return f" → {f['gp']:,} GP", False
        return f": can't pay, F{old} → {f['force']}, pays {paid:,} → {f['gp']:,} GP", True

    def economy(self):
        st, T = self.st, self.st["tower"]
        for n in sorted(st["realms"]):
            r, m = self.ruler(n), self.mirror(n)
            lv = realm_s(st, n)
            cruel = r["tag"] == "Cruel"
            inc = int(lv * INCOME * (CRUEL_INCOME if cruel else 1))
            skim = int(inc * SKIM)
            r["gp"] += inc - skim
            m["gp"] += skim
            line = (f"{n} · {r['leader']}: L{lv} × {INCOME}{f' × {CRUEL_INCOME:g} Cruel' if cruel else ''}"
                    f" = {inc:,}, skim −{skim:,}, upkeep −{r['force'] ** 2 * UPKEEP_FORCE:,}"
                    f" (F{r['force']}²)")
            paid, short = self.upkeep(r)
            if short:
                self.event(n, "couldn't pay the army")
                self.stats["upkeep_fail"] += 1
            self.income.append(line + paid)
            self.income.append(f"{n} mirror · {m['leader']}: skim +{skim:,} → {m['gp']:,} GP")
        lv = sum(st["hexes"][h]["level"] for h in hexes_of(st, "tower"))
        T["gp"] += lv * INCOME
        offs = len(T["officers"]) * UPKEEP_OFFICER
        line = (f"Tower: L{lv} × {INCOME} = {lv * INCOME:,}, upkeep"
                f" −{T['force'] ** 2 * UPKEEP_FORCE + offs:,} (F{T['force']}²,"
                f" officers {len(T['officers'])})")
        paid, short = self.upkeep(T, offs)
        if short:
            self.stats["tower_upkeep_fail"] += 1
        self.income.append(line + paid)

    def tower(self, o):
        T = self.st["tower"]
        for spec in o.fund:
            fac, _, amt = spec.partition("=")
            name, role = self.faction(fac)
            try:
                amt = int(amt)
            except ValueError:
                raise Bad(f"--fund {spec}: want REALM:ruler=GP or REALM:mirror=GP")
            if amt <= 0:
                raise Bad(f"--fund {spec}: GP must be positive")
            if amt > T["gp"]:
                raise Bad(f"--fund {spec}: tower has {T['gp']:,} GP at that point")
            f = self.st["realms"][name][role]
            T["gp"] -= amt
            f["gp"] += amt
            if role == "mirror":
                self.funded.add(name)
            self.log.append(f"Tower: Fund {name} {role} {f['leader']} {amt:,} GP → {f['gp']:,} GP."
                            f" Tower {T['gp'] + amt:,} → {T['gp']:,}.")
            self.event(name, f"the tower sent {amt:,} GP to {f['leader']}")
        seen = set()
        for s in o.recruit:
            name = self.realm(s)
            if name in seen:
                raise Bad(f"one recruit per realm a month ({name} twice)")
            seen.add(name)
            if name not in allies(self.st):
                R = self.st["realms"][name]
                why = "at war with the tower" if R["war"] else f"ruler is {R['ruler']['tag']}"
                raise Bad(f"recruit only from allies: {name} is not one ({why})")
            cost = RECRUIT * (len(T["officers"]) + 1)
            if cost > T["gp"]:
                raise Bad(f"--recruit {name}: officer {len(T['officers']) + 1} costs {cost:,},"
                          f" tower has {T['gp']:,} GP at that point")
            T["gp"] -= cost
            self.ruler(name)["gp"] += cost
            off = {"name": name_for(self.st, name, self.rng), "people": name}
            T["officers"].append(off)
            self.log.append(f"Tower: Recruit {off['name']} ({name}) for {cost:,} GP, paid to"
                            f" {self.ruler(name)['leader']}. Court {len(T['officers'])}.")
            self.event(name, f"{off['name']} joined the wizard's court")
        act = (o.action or "").lower()
        if act and act != "build" and not act.startswith("conquer:"):
            raise Bad(f"--action {o.action}: want conquer:HEX or build")
        if o.court:
            pts = {"conquer": 0, "defend": 0, "coup": {}}
            for part in o.court.split(","):
                k, _, v = part.partition("=")
                try:
                    v = int(v)
                except ValueError:
                    raise Bad(f"--court {part}: want NAME=N")
                if v < 0:
                    raise Bad(f"--court {part}: points must be ≥ 0")
                if k.startswith("coup:"):
                    name = self.realm(k[5:])
                    if name not in self.funded:
                        raise Bad(f"--court {part}: back a coup only by a mirror funded this month")
                    pts["coup"][name] = pts["coup"].get(name, 0) + v
                elif k in ("conquer", "defend"):
                    pts[k] += v
                else:
                    raise Bad(f"--court {part}: want conquer=N, defend=N or coup:REALM=N")
            if pts["conquer"] and not act.startswith("conquer:"):
                raise Bad("--court conquer=N needs --action conquer:HEX")
            total = pts["conquer"] + pts["defend"] + sum(pts["coup"].values())
            if total > pool(len(T["officers"])):
                raise Bad(f"--court spends {total}, pool is {pool(len(T['officers']))}")
            self.court = pts
            self.log.append(f"Tower: court points: conquer {pts['conquer']}, defend {pts['defend']}"
                            + "".join(f", coup {n} {v}" for n, v in pts["coup"].items())
                            + f" (pool {pool(len(T['officers']))}).")
        if act == "build":
            cost = (T["force"] + 1) * BUILD
            if cost > T["gp"]:
                raise Bad(f"--action build: Force {T['force'] + 1} costs {cost:,},"
                          f" tower has {T['gp']:,} GP at that point")
            self.build("tower", None, "force", "Tower")
        elif act.startswith("conquer:"):
            h = self.hexarg(act[8:])
            dfn = self.holder(h)
            if dfn == "tower":
                raise Bad(f"{h} is already the tower's")
            if not set(nbrs(h)) & set(hexes_of(self.st, "tower")):
                raise Bad(f"{h} is not next to a tower hex")
            if T["force"] < 1:
                raise Bad("tower at Force 0 can't attack")
            lv = self.st["hexes"][h]["level"]
            self.battle("tower", dfn, h, "conquer", f"Tower: Conquer {h} ({dfn}, L{lv})")

    def order(self):
        names = [n for n in sorted(self.st["realms"]) if hexes_of(self.st, n)]
        rolls = {n: [] for n in names}
        by_c = Counter(self.ruler(n)["cunning"] for n in names)
        for c, k in by_c.items():
            if k < 2:
                continue
            grp = [n for n in names if self.ruler(n)["cunning"] == c]
            while True:
                for n in grp:
                    rolls[n].append(self.d(DIE))
                if len({rolls[n][-1] for n in grp}) == len(grp):
                    break
        names.sort(key=lambda n: (-self.ruler(n)["cunning"], -(rolls[n] or [0])[-1]))
        bits = [f"{n} C{self.ruler(n)['cunning']}"
                + (f" (d{DIE} {', '.join(map(str, rolls[n]))})" if rolls[n] else "") for n in names]
        self.log.append("Order: " + " · ".join(bits) + ".")
        return names

    def target(self, name):
        """The ruler's tag action as (kind, defender, hex, note), or None."""
        st, r = self.st, self.ruler(name)
        F, tag = r["force"], r["tag"]
        if F <= 0 or tag == "Cruel":
            return None
        th = st["tower"]["hex"]
        war = st["realms"][name]["war"]
        mine = hexes_of(st, name)
        border = sorted({n for h in mine for n in nbrs(h) if self.holder(n) != name}, key=hkey)
        beat = lambda s: F >= self.force(s) + BEAT
        lvl = lambda h: st["hexes"][h]["level"]
        cands = []
        if tag == "Greedy":
            cands = [h for h in border if h != th and beat(self.holder(h))]
        elif tag == "Neutral":
            cands = [h for h in border if st["hexes"][h]["people"] == name and h != th
                     and (self.holder(h) != "tower" or war) and beat(self.holder(h))]
        elif tag == "Altruistic":
            for h in border:
                s = self.holder(h)
                if h == th or self.force(s) >= F:
                    continue
                if (s == "tower" and war) or (s != "tower" and self.ruler(s)["tag"] in VICIOUS):
                    cands.append(h)
        if cands:
            h = max(cands, key=lvl)
            return "conquer", self.holder(h), h, ""
        if tag in ("Rapacious", "Brutal"):
            nb = sorted({self.holder(h) for h in border})
            has = lambda s: self.force(s) if tag == "Brutal" else self.gp(s)  # skip empty targets
            nb = [s for s in nb if beat(s) and has(s) > 0]
            if not nb:
                return None
            if tag == "Rapacious":
                best = max(self.gp(s) for s in nb)
                s, note = self.pick([s for s in nb if self.gp(s) == best], "target")
                h = max([h for h in border if self.holder(h) == s], key=lvl)
                return "raid", s, h, note
            low = min(self.force(s) for s in nb)
            s, note = self.pick([s for s in nb if self.force(s) == low], "target")
            h, n2 = self.pick([h for h in border if self.holder(h) == s], "hex")
            return "enslave", s, h, note + n2
        return None

    def ruler_acts(self, name):
        r, m = self.ruler(name), self.mirror(name)
        head = self.head(name)
        threat = m["cunning"] + (CRUEL_COUP if r["tag"] == "Cruel" else 0)
        if threat >= r["cunning"] and self.build(name, "ruler", "cunning",
                                                  f"{head}: guards the throne,"):
            return
        if self.build(name, "ruler", "force", head):  # arms first whenever it can afford to
            return
        t = self.target(name)
        if t:
            kind, dfn, h, note = t
            lv = self.st["hexes"][h]["level"]
            if kind == "conquer":
                what = f"Conquer {h} ({self.nm(dfn)}, L{lv})"
            else:
                what = f"{kind.capitalize()} {self.nm(dfn)} at {h} (L{lv})"
            self.battle(name, dfn, h, kind, f"{head}: {what}{note}")
            return
        self.build_or_save(name, "ruler", "force", head)

    def mirror_acts(self, name):
        R = self.st["realms"][name]
        r, m = R["ruler"], R["mirror"]
        head = f"{name} mirror ({m['leader']}, {m['tag']})"
        bon = []
        if r["tag"] == "Cruel":
            bon.append((CRUEL_COUP, "Cruel"))
        if (name, "ruler") in self.struck:
            bon.append((STRIKE, "strike"))
        pts = self.court["coup"].get(name, 0) if name in self.funded else 0
        if pts:
            bon.append((pts, "court"))
        if m["cunning"] + sum(b for b, _ in bon) < r["cunning"]:
            self.build_or_save(name, "mirror", "cunning", head)
            return
        dm = [(STRIKE, "strike")] if (name, "mirror") in self.struck else []
        rm, rr = self.d(DIE), self.d(DIE)
        tm = rm + m["cunning"] + sum(b for b, _ in bon)
        tr = rr + r["cunning"] + sum(b for b, _ in dm)
        mods = lambda ms: "".join(f" + {b} {w}" for b, w in ms)
        win = tm > tr
        line = (f"{head}: Coup vs {r['leader']} → d{DIE} {rm} + C{m['cunning']}{mods(bon)} = {tm}"
                f" vs d{DIE} {rr} + C{r['cunning']}{mods(dm)} = {tr}, {'WIN' if win else 'LOSS'}.")
        if win:
            new = {"leader": m["leader"], "title": m["title"], "tag": m["tag"],
                   "force": r["force"], "cunning": m["cunning"], "gp": r["gp"] + m["gp"]}
            old = {"leader": r["leader"], "title": r["title"], "tag": r["tag"],
                   "cunning": r["cunning"] // COUP_DEMOTE, "gp": 0}
            purse = f", purse {m['gp']:,} GP into the treasury" if m["gp"] else ""
            line += (f" {m['leader']} ({m['tag']}) rules {name}{purse}."
                     f" {r['leader']} becomes the rival, C{r['cunning']} → {old['cunning']}.")
            if R["war"]:
                R["war"] = False
                line += " War with the tower ends."
            R["ruler"], R["mirror"] = new, old
            self.coups.append(name)
            self.event(name, f"{new['leader']} overthrew {old['leader']}")
        else:
            m["cunning"] = max(0, m["cunning"] - COUP_FAIL)
            line += f" {m['leader']} C{m['cunning'] + COUP_FAIL} → {m['cunning']}."
            self.event(name, f"rival {m['leader']}'s coup failed")
            self.stats["coup_fail"] += 1
        self.log.append(line)
        if pts and not win:
            self.court_risk(f"backed coup in {name} lost")

    def cleanup(self):
        st = self.st
        for n in sorted(st["realms"]):
            if not hexes_of(st, n):
                R = st["realms"].pop(n)
                st["fallen"].append({"realm": n, "month": st["month"]})
                self.log.append(f"{n} fall: no hexes left. {R['ruler']['leader']} and"
                                f" {R['mirror']['leader']} are gone; the {n} stay on their land.")
        st["month"] += 1
        st["rng"] = self.rng.getrandbits(32)

    def run(self, o):
        st = self.st
        month = st["month"]
        for R in st["realms"].values():
            R["events"] = []
        st["tower"]["events"] = []
        self.morten(o)
        self.economy()
        self.tower(o)
        names = self.order()
        for n in names:
            if n in st["realms"] and hexes_of(st, n):
                self.ruler_acts(n)
        for n in names:
            if n in st["realms"] and hexes_of(st, n):
                self.mirror_acts(n)
        self.cleanup()
        return month

    def reply(self, month):
        st, T = self.st, self.st["tower"]
        out = [f"**Month {month} · Domain turn**", "", "**Income**"]
        out += [f"- {x}" for x in self.income]
        out += ["", "**Log**"] + [f"- {x}" for x in self.log or ["Nothing happens."]]
        out += ["", "**Realms**"] + [f"- {realm_line(st, n)}" for n in sorted(st["realms"])]
        if st["fallen"]:
            out.append("- Fallen: " + ", ".join(f"{f['realm']} (month {f['month']})"
                                                for f in st["fallen"]))
        out += ["", f"**Tower:** {tower_line(st)}", "", f"**Court:** {court_line(st)}", ""]
        out += ["**Next month**"] + [f"- {x}" for x in next_month(st)]
        return "\n".join(out) + "\n"


def next_month(st):
    T = st["tower"]
    here = T["morten"]
    x = st["hexes"][here]
    out = [f"Morten: {hex_label(st, here)}",
           f"Travel: 1 day per hex; d6 each day outside {T['hex']}, 1 = encounter"]
    if x["holder"] == "tower":
        out.append(f"Mission here: Delve floor {x['level']}")
    else:
        R = st["realms"][x["holder"]]
        rob = " · Rob" if R["ruler"]["tag"] in VICIOUS else ""
        out.append(f"Mission here: Strike {x['holder']} ruler {R['ruler']['leader']} or mirror"
                   f" {R['mirror']['leader']}{rob} · Delve floor {x['level']}")
    mine = hexes_of(st, "tower")
    border = sorted({n for h in mine for n in nbrs(h) if st["hexes"][n]["holder"] != "tower"},
                    key=hkey)
    if T["force"] >= 1:
        conq = " / ".join(f"{h} ({st['hexes'][h]['holder']} L{st['hexes'][h]['level']},"
                          f" F{st['realms'][st['hexes'][h]['holder']]['ruler']['force']})"
                          for h in border)
        conq = f"Conquer {conq}"
    else:
        conq = "Conquer: needs Force 1"
    out.append(f"Tower action: {conq} · or Build F{T['force'] + 1} for {(T['force'] + 1) * BUILD:,} GP")
    out.append("Fund: any ruler or mirror")
    al = allies(st)
    cost = RECRUIT * (len(T["officers"]) + 1)
    out.append(f"Recruit (next officer {cost:,} GP): {', '.join(al) if al else 'no allies'}")
    out.append(f"Court points: {pool(len(T['officers']))} (conquer, defend, coup:REALM)")
    return out


# ---- Commands ----

def load(d):
    p = Path(d) / "realms.json"
    if not p.exists():
        raise Bad(f"no {p}; run new first")
    return json.loads(p.read_text())


def save(d, st):
    Path(d, "realms.json").write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n")
    Path(d, "world.md").write_text(world_md(st))


def cmd_new(a):
    d = Path(a.campaign)
    if (d / "realms.json").exists() and not a.force:
        raise Bad(f"{d / 'realms.json'} exists; use --force to overwrite")
    st = generate(a.seed)
    d.mkdir(parents=True, exist_ok=True)
    save(d, st)
    rng, monsters = random.Random(a.seed), load_monsters()
    out = ["# GM secrets · dungeon floors", "",
           f"Floor N lies under the level-N hex (seed {a.seed}, the same floors as"
           f" `gen_dungeon.py --seed {a.seed}`). Mark rooms explored as Morten reaches them.", ""]
    by_level = {x["level"]: h for h, x in st["hexes"].items()}
    for level in range(1, 21):
        need, total, encs = floor(level, monsters, rng)
        h = by_level[level]
        out.append(floor_md(level, need, total, encs,
                            f"Floor {level} · {h} ({st['hexes'][h]['biome']},"
                            f" {st['hexes'][h]['holder']})"))
    (d / "gm-secrets.md").write_text("\n".join(out))
    print(summary(st))
    print(f"Wrote {d / 'realms.json'}, {d / 'world.md'}, {d / 'gm-secrets.md'}.")


def cmd_show(a):
    st = load(a.campaign)
    at = a.at.upper() if a.at else None
    if at and at not in st["hexes"]:
        raise Bad(f"no hex '{a.at}' (A1–D5)")
    print(summary(st, at), end="")


def cmd_encounter(a):
    st = load(a.campaign)
    h = a.hex.upper()
    if h not in st["hexes"]:
        raise Bad(f"no hex '{a.hex}' (A1–D5)")
    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(10 ** 6)
    e = encounter(st["hexes"][h]["level"], random.Random(seed))
    print(f"**Encounter · {hex_label(st, h)}** (seed {seed})\n")
    print(f"- {e['count']}× {e['name']} · CR {e['cr']} · {e['xp']:,} XP each")
    print(f"- {e['total']:,} XP total · {e['diff']} · coins {e['total'] // 10:,} GP")


def cmd_turn(a):
    st = load(a.campaign)
    t = Turn(st)
    month = t.run(a)
    print(t.reply(month), end="")
    if a.dry_run:
        print("\n(dry run: nothing saved)")
    else:
        save(a.campaign, st)


def cmd_sim(a):
    st = generate(a.seed)
    who = lambda r: f"{r['leader']} ({r['tag']})"
    start = {n: who(st["realms"][n]["ruler"]) for n in st["realms"]}
    names = sorted(st["realms"])
    coups = {n: [] for n in names}
    gps = {n: [] for n in names}
    zero = Counter()
    maxf = (0, "", 0)
    stats, standing12 = Counter(), None
    o = argparse.Namespace(**PASSIVE)
    for _ in range(a.months):
        t = Turn(st)
        month = t.run(o)
        stats += t.stats
        for n in t.coups:
            coups[n].append(month)
        for n, R in st["realms"].items():
            r = R["ruler"]
            gps[n].append(r["gp"])
            zero[n] += r["gp"] == 0
            if r["force"] > maxf[0]:
                maxf = (r["force"], n, month)
        if month == 12:
            standing12 = len(st["realms"])
        if a.quiet:
            fs = " · ".join(f"{n} F{R['ruler']['force']} C{R['ruler']['cunning']}"
                            f" {R['ruler']['gp']}" for n, R in sorted(st["realms"].items()))
            c = f" · coups: {', '.join(t.coups)}" if t.coups else ""
            print(f"M{month:<2} {len(st['realms'])} realms · {fs}{c}")
        else:
            print(t.reply(month))
    fell = ", ".join(f"{f['realm']} m{f['month']}" for f in st["fallen"]) or "none"
    twice = [(n, m) for n in names for m in coups[n] if m - 1 in coups[n]]
    T = st["tower"]
    out = ["", f"=== Sim summary · seed {a.seed} · {a.months} months ===",
           f"Realms standing: month 12: {standing12 if standing12 is not None else '-'}/{N_REALMS}"
           f" · end: {len(st['realms'])}/{N_REALMS} · fell: {fell}",
           f"Coups: {sum(len(v) for v in coups.values())} total · failed {stats['coup_fail']} · "
           + ", ".join(f"{n} {len(coups[n])}" for n in names),
           f"Back-to-back coups (ruler changed two months running): {len(twice)}"
           + (" · " + ", ".join(f"{n} m{m - 1}-{m}" for n, m in twice) if twice else ""),
           f"Max Force: {maxf[0]} ({maxf[1]}, month {maxf[2]})",
           f"Actions: conquer {stats['conquer']} · raid {stats['raid']} · enslave {stats['enslave']}"
           f" · build Force {stats['build_force']} · build Cunning {stats['build_cunning']}"
           f" · upkeep fails {stats['upkeep_fail']}",
           "Ruler treasury min / max / end (months at 0 GP):"]
    for n in names:
        g = gps[n]
        end = f"{g[-1]:,}" if n in st["realms"] else "fallen"
        now = who(st["realms"][n]["ruler"]) if n in st["realms"] else "-"
        out.append(f"  {n:<10} {min(g):>6,} / {max(g):>6,} / {end:>6}  ({zero[n]})"
                   f"  ruler: {start[n]} → {now}")
    out.append(f"Tower: hexes lost {stats['tower_lost']} · raided {stats['tower_raided']}"
               f" · enslaved {stats['tower_enslaved']} · upkeep fails {stats['tower_upkeep_fail']}"
               f" · end F{T['force']} {T['gp']:,} GP")
    print("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description="Realms overworld engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--campaign", required=True)
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("show")
    p.add_argument("--campaign", required=True)
    p.add_argument("--at")
    p = sub.add_parser("encounter")
    p.add_argument("--campaign", required=True)
    p.add_argument("--hex", required=True)
    p.add_argument("--seed", type=int)
    p = sub.add_parser("turn")
    p.add_argument("--campaign", required=True)
    p.add_argument("--at", help="Morten's hex at the end of his month")
    p.add_argument("--strike", help="REALM:ruler or REALM:mirror (a successful Strike)")
    p.add_argument("--rob", help="HEX (a successful Rob)")
    p.add_argument("--keep-loot", action="store_true")
    p.add_argument("--deposit", type=int, default=0)
    p.add_argument("--withdraw", type=int, default=0)
    p.add_argument("--fund", action="append", default=[], help="REALM:ruler=GP or REALM:mirror=GP")
    p.add_argument("--recruit", action="append", default=[], help="REALM (an ally)")
    p.add_argument("--action", help="conquer:HEX or build")
    p.add_argument("--court", help="conquer=N,defend=N,coup:REALM=N")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("sim")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--months", type=int, default=24)
    p.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    try:
        {"new": cmd_new, "show": cmd_show, "encounter": cmd_encounter, "turn": cmd_turn,
         "sim": cmd_sim}[a.cmd](a)
    except Bad as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
