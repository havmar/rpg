#!/usr/bin/env python3
"""CRB world tool: the map, leaders, dungeons, encounters, difficulty. Run from the repo root.

  python3 crb/tools/crb.py map                         the 16 hexes
  python3 crb/tools/crb.py new DIR [--seed N]          roll a campaign: leaders, known dungeons
  python3 crb/tools/crb.py around HEX [DIR]            the hexes around HEX (with leaders if DIR)
  python3 crb/tools/crb.py folk HEX                    the biome's speaking monsters, by CR
  python3 crb/tools/crb.py rate LEVEL NAME [N] ...     CR, XP and difficulty for the pair
  python3 crb/tools/crb.py encounter HEX [--coast]     travel/rest encounter, with reaction roll
  python3 crb/tools/crb.py hunt HEX LEVEL [low|moderate|high]   a levelled hunt
  python3 crb/tools/crb.py quest DIR HEX               one leader quest done (the last one deposes)
  python3 crb/tools/crb.py cleared DIR ID              mark a dungeon cleared
  python3 crb/tools/crb.py search DIR HEX              one day's search for a hidden dungeon
  python3 crb/tools/crb.py dungeon DIR ID              stock a dungeon (once; then it is fixed)
  python3 crb/tools/crb.py item RARITY                 a random magic item of that rarity
  python3 crb/tools/crb.py pc front|back               a new lord: species, background, class
  python3 crb/tools/crb.py robot front|back            the butler's new class

Every roll is printed. --seed N on any command makes it repeatable.
"""
import json, os, random, re, sys

SRD = "reference/srd"
# ---- dials -------------------------------------------------------------------
PROBLEM_ON = 3          # d6 <= this: the hex's leadership is problematic (1 in 2)
KNOWN_DICE = (4, 10)    # levels of a hex's two known dungeons
HIDDEN_MAX = 3          # hidden dungeons a hex can ever give up
FIND_ON = 1             # d6 <= this finds one, per day of searching
STRAY_ON = 1            # d6 <= this: an encounter comes from a neighbouring hex
THIN = 4                # fewer speaking kinds than this: borrow NPC stat blocks
EVIL = {"Abyss", "Hell", "Graveyard", "Volcano", "Arctic", "Swamp", "Savannah"}
# ------------------------------------------------------------------------------
# Rows 1-4 north to south, columns A-D west to east. Pointy-top hexes; rows 2 and 4 sit
# half a hex further east.
MAP = {
    "A1": "Heaven",    "B1": "Mountain", "C1": "Arctic",   "D1": "Graveyard",
    "A2": "Underdark", "B2": "Forest",   "C2": "City",     "D2": "Wizard's Tower",
    "A3": "Hills",     "B3": "Swamp",    "C3": "Savannah", "D3": "Abyss",
    "A4": "Jungle",    "B4": "Desert",   "C4": "Volcano",  "D4": "Hell",
}
MERGE = {"Fey Grove": "Forest"}
FOLK = {"Savannah": "Gnoll", "Jungle": "Jungle clansman"}
NPCS = ["Tough", "Scout", "Berserker", "Bandit Captain", "Priest", "Warrior Veteran",
        "Tough Boss", "Gladiator", "Mage", "Assassin", "Archmage"]
XP_AT = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000,
         120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
BUDGET = {1: (50, 75, 100), 2: (100, 150, 200), 3: (150, 225, 400), 4: (250, 375, 500),
          5: (500, 750, 1100), 6: (600, 1000, 1400), 7: (750, 1300, 1700),
          8: (1000, 1700, 2100), 9: (1300, 2000, 2600), 10: (1600, 2300, 3100),
          11: (1900, 2900, 4100), 12: (2200, 3700, 4700), 13: (2600, 4200, 5400),
          14: (2900, 4900, 6200), 15: (3300, 5400, 7800), 16: (3800, 6100, 9800),
          17: (4500, 7200, 11700), 18: (5000, 8700, 14200), 19: (5500, 10700, 17200),
          20: (6400, 13200, 22000)}
FRONT = ["Barbarian", "Fighter", "Paladin", "Monk", "Ranger", "Cleric"]
BACK = ["Wizard", "Sorcerer", "Warlock", "Bard", "Rogue", "Druid"]
SPECIES = ["Dragonborn", "Dwarf", "Elf", "Gnome", "Goliath", "Halfling", "Human", "Orc", "Tiefling"]
BACKGROUNDS = ["Acolyte", "Criminal", "Sage", "Soldier"]

R = random.Random()
def d(n, what=""):
    v = R.randint(1, n)
    if what: print(f"  [d{n} {what}: {v}]")
    return v
def crv(s): return eval(s) if "/" in s else float(s)

def load():
    """{name: dict(cr, xp, biome, align, speaks)} for every monster on the map or coast."""
    biome = {}
    for sec in re.split(r"\n## ", open(f"{SRD}/Monsters by Setting.md").read())[1:]:
        name = sec.split("\n")[0].split(". ", 1)[1]
        name = MERGE.get(name, name)
        for m in re.findall(r"\[([^\]]+)\]\(Monsters/", sec): biome[m] = name
    mon = {}
    for m, b in biome.items():
        if b not in MAP.values() and b != "Coast": continue
        t = open(f"{SRD}/Monsters/{m}.md").read()
        cr, xp = re.search(r"\*\*CR\*\* ([\d/]+) \((?:XP )?([\d,]+)", t).groups()
        al = re.search(r"^_.*?, (.*)_$", t, re.M).group(1)
        lang = re.search(r"\*\*Languages\*\* (.*)", t)
        lang = lang.group(1) if lang else "None"
        speaks = not (lang.startswith("None") or lang.lower().startswith("understands"))
        mon[m] = dict(cr=cr, xp=int(xp.replace(",", "")), biome=b, speaks=speaks, align=al,
                      side="evil" if "Evil" in al else "good" if "Good" in al else
                           "unaligned" if "Unaligned" in al else "neutral")
    return mon
MON = load()
def of(b): return sorted((m for m in MON if MON[m]["biome"] == b), key=lambda m: (crv(MON[m]["cr"]), m))
def tag(m, n=1):
    x = MON[m]
    return f"{n} x {m}" * (n > 1) + m * (n == 1) + f" (CR {x['cr']}, {x['xp']*n} XP, {x['side']})"

def folk(b):
    """Speaking monsters of a biome as (label, stat block). Thin biomes borrow NPC blocks."""
    out = [(m, m) for m in of(b) if MON[m]["speaks"]]
    if len(out) < THIN:
        who = FOLK.get(b, b + " native")
        out += [(f"{who} ({n} stat block)", n) for n in NPCS]
        out.sort(key=lambda p: crv(MON[p[1]]["cr"]))
    return out

def around(h):
    c, r = "ABCD".index(h[0]), int(h[1])
    s = 1 if r % 2 == 0 else 0
    spots = {"NW": (c - 1 + s, r - 1), "NE": (c + s, r - 1), "W": (c - 1, r), "E": (c + 1, r),
             "SW": (c - 1 + s, r + 1), "SE": (c + s, r + 1)}
    return {k: ("ABCD"[x] + str(y) if 0 <= x < 4 and 1 <= y <= 4 else None) for k, (x, y) in spots.items()}

def hexarg(h):
    h = h.upper()
    if h not in MAP: sys.exit(f"no hex {h}; hexes are A1..D4")
    return h

def stages(cr): return 1 if cr < 6 else 2 if cr <= 10 else 3

def closest(pool, level, key):
    """The entries nearest under `level`; if none are under, the lowest."""
    under = [p for p in pool if key(p) <= level]
    best = max(key(p) for p in under) if under else min(key(p) for p in pool)
    return [p for p in pool if key(p) == best]

def sig(b, level):
    pool = of(b)
    near = min(abs(crv(MON[m]["cr"]) - level) for m in pool)
    return R.choice([m for m in pool if abs(crv(MON[m]["cr"]) - level) == near])

def rate(level, groups):
    xp = sum(MON[m]["xp"] * n for m, n in groups)
    lo, mo, hi = (2 * v for v in BUDGET[level])
    word = ("Trivial" if xp < lo else "Low" if xp < mo else "Moderate" if xp < hi else
            "High" if xp <= hi * 1.25 else "Deadly" if xp <= hi * 2 else "Beyond the pair")
    return xp, word, (lo, mo, hi)

def build(b, level, budget, cap=None, only=None):
    """Spend an XP budget on one or two kinds of the biome's monsters."""
    pool = [m for m in of(b) if MON[m]["xp"] <= budget and (cap is None or crv(MON[m]["cr"]) <= cap)
            and (only is None or only(m))]
    pool = [m for m in pool if MON[m]["xp"] * 8 >= budget] or pool[-3:]
    if not pool: return []
    m = R.choice(pool)
    n = max(1, min(8, budget // MON[m]["xp"]))
    out, left = [(m, n)], budget - n * MON[m]["xp"]
    extra = [x for x in pool if x != m and MON[x]["xp"] <= left and MON[x]["xp"] * 4 >= left]
    if extra:
        x = R.choice(extra); out.append((x, left // MON[x]["xp"]))
    return out

def reaction(m):
    mod = {"evil": -2, "good": 2}.get(MON[m]["side"], 0)
    a, b = d(6), d(6); t = a + b + mod
    word = ("attacks" if t <= 3 else "hostile: threatens, drives the pair off, attacks if pressed"
            if t <= 5 else "wary: keeps its distance" if t <= 8 else
            "indifferent or curious: will talk if it can" if t <= 10 else "friendly: helps if asked")
    return f"reaction 2d6 [{a}+{b}]{mod:+d} = {t}: {word}"

def appearing(m):
    c = crv(MON[m]["cr"])
    return d(4) + d(4) if c <= 0.25 else d(4) if c <= 1 else d(2) if c <= 4 else 1

def world(dirn): return json.load(open(f"{dirn}/world.json"))
def save(dirn, w):
    json.dump(w, open(f"{dirn}/world.json", "w"), indent=1)
    L = ["# The world", "", "Written by `crb.py`; don't edit. The butler knows all of this.", "",
         "| Hex | Biome | Side | Leader | CR | Rule | Quests to depose |", "|---|---|---|---|---|---|---|"]
    for h, x in w["hexes"].items():
        rule = "**problem**" if x["problem"] and not x["deposed"] else "deposed" if x["deposed"] else "quiet"
        q = f"{x['done']}/{x['stages']}" if x["problem"] else "–"
        L.append(f"| {h} | {x['biome']} | {'evil' if x['biome'] in EVIL else 'good'} | {x['leader']} | {x['cr']} | {rule} | {q} |")
    L += ["", "## Dungeons", "", "| ID | Hex | Level | Its monster | CR | State |", "|---|---|---|---|---|---|"]
    for i, x in w["dungeons"].items():
        L.append(f"| {i} | {x['hex']} {MAP[x['hex']]} | {x['level']} | {x['monster']} | {MON[x['monster']]['cr']} | {x['state']} |")
    open(f"{dirn}/world.md", "w").write("\n".join(L) + "\n")

def add_dungeon(w, h, level, state):
    i = f"{h}-{1 + sum(1 for x in w['dungeons'].values() if x['hex'] == h)}"
    w["dungeons"][i] = dict(hex=h, level=level, monster=sig(MAP[h], level), state=state)
    return i

def main(a):
    global R
    if "--seed" in a:
        i = a.index("--seed"); R = random.Random(int(a[i + 1])); del a[i:i + 2]
    if not a: sys.exit(__doc__)
    cmd, a = a[0], a[1:]
    if cmd == "map":
        for r in "1234":
            print(("      " if r in "24" else "") + "  ".join(f"{c+r} {MAP[c+r]:<14}" for c in "ABCD"))
        print("Coast: the outer side of every hex except B2, C2, B3, C3.")
    elif cmd == "new":
        os.makedirs(a[0], exist_ok=True)
        if os.path.exists(f"{a[0]}/world.json"): sys.exit("world.json exists")
        w = dict(hexes={}, dungeons={})
        for h, b in MAP.items():
            prob = d(6) <= PROBLEM_ON
            roll = d(20)
            label, block = R.choice(closest(folk(b), roll, lambda p: crv(MON[p[1]]["cr"])))
            cr = MON[block]["cr"]
            w["hexes"][h] = dict(biome=b, problem=prob, roll=roll, leader=label, block=block, cr=cr,
                                 stages=stages(crv(cr)), done=0, deposed=False, hidden_found=0)
            for die in KNOWN_DICE: add_dungeon(w, h, d(die), "known")
        save(a[0], w); print(open(f"{a[0]}/world.md").read())
    elif cmd == "around":
        h = hexarg(a[0]); w = world(a[1]) if len(a) > 1 else None
        def line(x):
            s = f"{x} {MAP[x]} ({'evil' if MAP[x] in EVIL else 'good'})"
            if w:
                q = w["hexes"][x]
                s += f": {q['leader']}, CR {q['cr']}, " + ("deposed" if q["deposed"] else
                     f"PROBLEM, {q['done']}/{q['stages']} quests done" if q["problem"] else "quiet")
            return s
        print("Here:", line(h))
        for k, x in around(h).items():
            print(f"  {k:<2}", line(x) if x else "the sea (Coast)")
    elif cmd == "folk":
        b = MAP[hexarg(a[0])]
        for label, block in folk(b): print(f"CR {MON[block]['cr']:<4} {label}  [{MON[block]['align']}]")
    elif cmd == "rate":
        level, groups, i = int(a[0]), [], 1
        while i < len(a):
            n = int(a[i + 1]) if i + 1 < len(a) and a[i + 1].isdigit() else 1
            if a[i] not in MON: sys.exit(f"unknown monster {a[i]!r}")
            groups.append((a[i], n)); i += 2 if n > 1 or (i + 1 < len(a) and a[i + 1].isdigit()) else 1
        xp, word, (lo, mo, hi) = rate(level, groups)
        print("; ".join(tag(m, n) for m, n in groups))
        print(f"Total {xp} XP ({xp // 2} each). For a pair of level {level} (Low {lo}, Moderate {mo}, High {hi}): {word}.")
    elif cmd == "encounter":
        h = hexarg(a[0]); b = MAP[h]
        if "--coast" in a: b = "Coast"
        elif d(6, "stray") <= STRAY_ON:
            nb = [x for x in around(h).values() if x]
            ev = [x for x in nb if MAP[x] in EVIL] or nb
            x = R.choice(ev); b = MAP[x]; print(f"  strayed in from {x} {b}")
        m = R.choice(of(b)); n = appearing(m)
        print(tag(m, n)); print(reaction(m))
    elif cmd == "hunt":
        h, level = hexarg(a[0]), int(a[1]); diff = a[2] if len(a) > 2 else "moderate"
        budget = 2 * BUDGET[level][["low", "moderate", "high"].index(diff)]
        g = build(MAP[h], level, budget, only=lambda m: MON[m]["side"] in ("evil", "unaligned"))
        xp, word, _ = rate(level, g)
        print("; ".join(tag(m, n) for m, n in g)); print(f"Total {xp} XP ({xp // 2} each): {word} for a pair of level {level}.")
    elif cmd == "quest":
        w = world(a[0]); h = hexarg(a[1]); q = w["hexes"][h]
        if not q["problem"] or q["deposed"]: sys.exit("no problem leader there")
        q["done"] += 1; q["deposed"] = q["done"] >= q["stages"]; save(a[0], w)
        left = sum(1 for x in w["hexes"].values() if x["problem"] and not x["deposed"])
        print(f"{h} {q['biome']}: {q['leader']} " + ("DEPOSED" if q["deposed"] else f"{q['done']}/{q['stages']}") +
              f". Problem leaders left: {left}." + (" THE GAME IS WON." if not left else ""))
    elif cmd == "cleared":
        w = world(a[0]); w["dungeons"][a[1]]["state"] = "cleared"; save(a[0], w); print(a[1], "cleared")
    elif cmd == "search":
        w = world(a[0]); h = hexarg(a[1]); q = w["hexes"][h]
        if q["hidden_found"] >= HIDDEN_MAX: print("Nothing: this hex has no more hidden dungeons.")
        elif d(6, "search") <= FIND_ON:
            q["hidden_found"] += 1; i = add_dungeon(w, h, d(20, "level"), "found")
            x = w["dungeons"][i]; save(a[0], w)
            print(f"Found {i}: level {x['level']}, {tag(x['monster'])}")
        else: print("Nothing today.")
    elif cmd == "dungeon":
        w = world(a[0]); x = w["dungeons"][a[1]]
        if "rooms" not in x:
            L = x["level"]; b = MAP[x["hex"]]
            total = XP_AT[min(L, 19)] - XP_AT[min(L, 19) - 1]   # one level-up gap, shared by two
            boss = x["monster"]; left = total - MON[boss]["xp"]; rooms = []
            while left > 0 and len(rooms) < 12:
                g = build(b, L, min(left, 2 * BUDGET[L][1]), cap=max(L, 1))
                if not g: break
                rooms.append(g); left -= sum(MON[m]["xp"] * n for m, n in g)
            x["rooms"] = rooms; x["total"] = total; save(a[0], w)
        print(f"{a[1]}: {MAP[x['hex']]}, level {x['level']}, worth about {x['total']} XP ({x['total'] // 2} each).")
        for i, g in enumerate(x["rooms"], 1): print(f"  {i}. " + "; ".join(tag(m, n) for m, n in g))
        print(f"  Last. {tag(x['monster'])}, with the magic item")
    elif cmd == "item":
        rar = a[0].title()
        fs = [f[:-3] for f in os.listdir(f"{SRD}/Magic Items/{rar}") if f.endswith(".md")]
        print(f"{rar}: {R.choice(fs)}")
    elif cmd in ("pc", "robot"):
        cls = R.choice(FRONT if a[0] == "front" else BACK)
        if cmd == "pc": print(f"{R.choice(SPECIES)} {cls} ({a[0]}), background {R.choice(BACKGROUNDS)}, male")
        else: print(f"The butler is rebuilt as a {cls} ({a[0]}).")
    else: sys.exit(__doc__)

if __name__ == "__main__": main(sys.argv[1:])
