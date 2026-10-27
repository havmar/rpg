#!/usr/bin/env python3
"""Magic items for the Hotel's luggage (dnd-crunch/hotel.md, section 12).

Every guest's luggage may hold a magic item: a d20 on the floor's row gives nothing or a
rarity, and the item is a random SRD file of that rarity (reference/srd/Magic Items/),
with the Varies folder spread into its rarities. Common is its own d6.

Usage:
  python3 dnd-crunch/tools/loot.py --floor 4                 # the luggage roll for a floor-4 guest
  python3 dnd-crunch/tools/loot.py --floor 4 --sure          # reroll misses (lost and found)
  python3 dnd-crunch/tools/loot.py --floor 4 --sure --band-up  # a Resident's or the Ark's suite
  python3 dnd-crunch/tools/loot.py --rarity Uncommon         # one item of a rarity (the shop window)
  python3 dnd-crunch/tools/loot.py --scroll 1 --count 3      # wizard Spell Scrolls (the shop's shelf)
  python3 dnd-crunch/tools/loot.py --seed 7 --floor 12       # repeatable

Each item prints its name, category and rarity, attunement, list price (the SRD's rarity
values; the gift shop buys at half) and its file.
"""
import argparse
import random
import re
from pathlib import Path

SRD = Path(__file__).resolve().parents[2] / "reference" / "srd"
ITEMS = SRD / "Magic Items"
EQUIP = SRD / "Equipment"
SPELL_LIST = SRD / "Classes" / "Wizard" / "Wizard Spell List.md"

RARITIES = ["Common", "Uncommon", "Rare", "Very Rare", "Legendary"]
FOLDERS = ["Uncommon", "Rare", "Very Rare", "Legendary"]  # Common is the d6 below

# hotel.md section 12: the luggage roll. Per floor band, the highest d20 face for each
# result in order; None is a miss.
BANDS = [
    ((1, 4), [(10, None), (16, "Common"), (19, "Uncommon"), (20, "Rare")]),
    ((5, 10), [(9, None), (12, "Common"), (17, "Uncommon"), (20, "Rare")]),
    ((11, 16), [(8, None), (9, "Common"), (12, "Uncommon"), (16, "Rare"),
                (19, "Very Rare"), (20, "Legendary")]),
    ((17, 20), [(8, None), (9, "Uncommon"), (12, "Rare"), (17, "Very Rare"),
                (20, "Legendary")]),
]

# Magic Item Rarity.md, and Scribing Spell Scrolls.md for the scrolls (value = 2 × cost).
VALUE = {"Common": 100, "Uncommon": 400, "Rare": 4000, "Very Rare": 40000,
         "Legendary": 200000}
SCRIBE = [15, 25, 100, 150, 1000, 1500, 10000, 12500, 15000, 50000]
SCROLL_RARITY = ["Common", "Common", "Uncommon", "Uncommon", "Rare", "Rare",
                 "Very Rare", "Very Rare", "Very Rare", "Legendary"]
# Halve the value for a consumable other than a Spell Scroll. Potions are the category;
# these are the other single-use items in the SRD's folders.
CONSUMABLE = re.compile(r"^(Ammunition|Bead of|Dust of|Elemental Gem|Feather Token)")

TYPE_LINE = re.compile(r"^_(.+)_$")
BOLD_VARIANT = re.compile(r"^_\*\*(.+?) \((Uncommon|Rare|Very Rare|Legendary)\)\.\*\*_")
TABLE_VARIANT = re.compile(r"^\| ([A-Z][^|]+?) +\|.*\| (Common|Uncommon|Rare|Very Rare|"
                           r"Legendary) +\|$")
PLUS_VARIANT = re.compile(r"(Uncommon|Rare|Very Rare|Legendary) \(\+(\d)\)")


def band(floor):
    for i, ((lo, hi), _) in enumerate(BANDS):
        if lo <= floor <= hi:
            return i
    raise ValueError(f"floor {floor} is not 1 to 20")


def row_result(row, face):
    for top, result in row:
        if face <= top:
            return result
    raise ValueError(face)


def type_line(path):
    lines = path.read_text().splitlines()
    m = TYPE_LINE.match(lines[2]) if len(lines) > 2 else None
    return m.group(1) if m else ""


def category(tline):
    return re.split(r"[,(]", tline)[0].strip()


def base_spec(tline):
    """'Weapon (Any Melee Weapon), Rare' -> ('Weapon', 'Any Melee Weapon')."""
    m = re.match(r"(Weapon|Armor) \(([^)]*)\)", tline)
    return (m.group(1), m.group(2)) if m else None


def attunement(tline):
    m = re.search(r"\((Requires Attunement[^)]*)\)", tline)
    return m.group(1) if m else "no attunement"


def load_pool():
    """{rarity: [entry]} for Uncommon and up. An entry is a dict: name, rarity, file,
    tline, and for a variant of a Varies file the variant's name."""
    pool = {r: [] for r in FOLDERS}
    for folder in FOLDERS:
        for f in sorted((ITEMS / folder).glob("*.md")):
            pool[folder].append({"name": f.stem, "rarity": folder, "file": f,
                                 "tline": type_line(f)})
    for v in varies_entries():
        if v["rarity"] in pool:
            pool[v["rarity"]].append(v)
    return pool


def varies_entries():
    out = []
    for f in sorted((ITEMS / "Varies").glob("*.md")):
        tline = type_line(f)
        text = f.read_text().splitlines()
        if f.stem == "Spell Scroll":
            for level, rarity in enumerate(SCROLL_RARITY):
                out.append({"name": "Spell Scroll", "scroll": level, "rarity": rarity,
                            "file": f, "tline": tline})
            continue
        plus = PLUS_VARIANT.findall(tline)
        if plus:
            stem = f.stem.split(",")[0]
            for rarity, n in plus:
                out.append({"name": f"{stem}, +{n}", "rarity": rarity, "file": f,
                            "tline": tline})
            continue
        bold = [m.groups() for m in map(BOLD_VARIANT.match, text) if m]
        if bold:
            for name, rarity in bold:
                out.append({"name": f"{f.stem} ({name})", "rarity": rarity, "file": f,
                            "tline": tline})
            continue
        for line in text:
            m = TABLE_VARIANT.match(line)
            if m:
                out.append({"name": m.group(1).strip(), "rarity": m.group(2), "file": f,
                            "tline": tline})
    return out


def money(text):
    m = re.match(r"([\d,]+) (GP|SP|CP)", text.strip())
    if not m:
        return 0
    n = int(m.group(1).replace(",", ""))
    return {"GP": n, "SP": n / 10, "CP": n / 100}[m.group(2)]


def equipment_table(path):
    """[(section heading, name, cost in GP)] from an Equipment file's tables."""
    rows, head = [], None
    for line in path.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or set(line) <= set("|- "):
            continue
        if cells[-1] == "Cost":
            head = cells[0]
            continue
        if head:
            rows.append((head, cells[0], money(cells[-1])))
    return rows


def base_options(kind, spec):
    """The base items a magic weapon or armour can be: [(name, cost)]."""
    if kind == "Weapon":
        if spec == "Any Ammunition":
            rows = equipment_table(EQUIP / "Ammunition.md")
            return [(f"{n} ×10", 0) for _, n, _ in rows if n != "Type"]
        rows = equipment_table(EQUIP / "Weapons.md")
        if spec == "Any Melee Weapon":
            rows = [r for r in rows if "Melee" in r[0]]
        elif spec != "Any Simple or Martial":
            names = names_in(spec)
            rows = [r for r in rows if r[1] in names]
    else:
        rows = [r for r in equipment_table(EQUIP / "Armor.md")]
        if spec == "Shield":
            rows = [r for r in rows if r[1] == "Shield"]
        elif spec.startswith("Any"):
            rows = [r for r in rows if r[1] != "Shield"]
            if "Light" not in spec:
                rows = [r for r in rows if not r[0].startswith("Light")]
            for excluded in re.findall(r"Except ([^,]+)", spec):
                rows = [r for r in rows if r[1] != excluded.strip()]
        else:
            names = names_in(spec)
            rows = [r for r in rows if r[1] in names]
    return [(n, c) for _, n, c in rows]


def names_in(spec):
    return {n.strip() for n in re.split(r",|\bor\b", spec) if n.strip()}


def wizard_spells(level):
    text = SPELL_LIST.read_text()
    heads = list(re.finditer(r"^## (Cantrips|Level (\d) Wizard Spells)", text, re.M))
    for i, h in enumerate(heads):
        lv = 0 if h.group(1) == "Cantrips" else int(h.group(2))
        if lv == level:
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return re.findall(r"^\| _(.+?)_ +\|", text[h.start():end], re.M)
    raise ValueError(level)


def common_item(rng):
    """hotel.md section 12: Common is a d6."""
    face = rng.randint(1, 6)
    if face <= 2:
        item = {"name": "Potion of Healing", "rarity": "Common",
                "file": ITEMS / "Varies" / "Potions of Healing.md", "tline": "Potion, Common"}
    elif face == 3:
        f = ITEMS / "Common" / "Potion of Climbing.md"
        item = {"name": f.stem, "rarity": "Common", "file": f, "tline": type_line(f)}
    elif face == 4:
        f = ITEMS / "Common" / "Bead of Nourishment.md"
        item = {"name": f.stem, "rarity": "Common", "file": f, "tline": type_line(f)}
    else:
        item = {"name": "Spell Scroll", "scroll": 1, "rarity": "Common",
                "file": ITEMS / "Varies" / "Spell Scroll.md", "tline": "Scroll, Common"}
    return face, item


def finish(item, rng):
    """Roll what a picked entry leaves open (a scroll's spell, a base weapon) and price it."""
    item = dict(item)
    rarity = item["rarity"]
    price = VALUE[rarity]
    if "scroll" in item:
        level = item["scroll"]
        spell = rng.choice(wizard_spells(level))
        lv = "cantrip" if level == 0 else f"level {level}"
        item["name"] = f"Spell Scroll ({lv}): {spell}"
        price = 2 * SCRIBE[level]
    else:
        if category(item["tline"]) == "Potion" or CONSUMABLE.match(item["name"]):
            price //= 2
        spec = base_spec(item["tline"])
        if spec:
            options = base_options(*spec)
            if options:
                base, cost = rng.choice(options)
                item["name"] += f" ({base})"
                price += cost
    item["price"] = price
    return item


def pick(rarity, rng, pool):
    if rarity == "Common":
        return common_item(rng)[1]
    return rng.choice(pool[rarity])


def gp(n):
    return f"{n:,.0f} GP" if n == int(n) else f"{n:,.1f} GP"


def describe(item):
    rel = item["file"].relative_to(SRD.parents[1])
    cat = category(item["tline"]) or "Item"
    return "\n".join([
        f"Item: {item['name']} ({cat}, {item['rarity']})",
        f"Attunement: {attunement(item['tline'])}",
        f"Price: {gp(item['price'])} (the gift shop buys at {gp(item['price'] / 2)})",
        f"File: {rel}",
    ])


def luggage(floor, rng, pool, sure=False, band_up=False):
    """The luggage roll. Returns (lines of rolls, item or None)."""
    i = band(floor)
    if band_up:
        i = min(i + 1, len(BANDS) - 1)
    (lo, hi), row = BANDS[i]
    rolls = []
    while True:
        face = rng.randint(1, 20)
        rarity = row_result(row, face)
        rolls.append(f"d20 [{face}] on floors {lo}–{hi}: {rarity or 'nothing magic'}")
        if rarity or not sure:
            break
    if not rarity:
        return rolls, None
    return rolls, finish(pick(rarity, rng, pool), rng)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    what = ap.add_mutually_exclusive_group(required=True)
    what.add_argument("--floor", type=int, help="the luggage roll for a guest on this floor")
    what.add_argument("--rarity", choices=RARITIES, help="one random item of this rarity")
    what.add_argument("--scroll", type=int, choices=range(0, 10), metavar="LEVEL",
                      help="a wizard Spell Scroll of this level (0 = cantrip)")
    ap.add_argument("--sure", action="store_true", help="reroll misses")
    ap.add_argument("--band-up", action="store_true", help="roll on the next band's row")
    ap.add_argument("--count", type=int, default=1, help="how many (default 1)")
    ap.add_argument("--seed", type=int, help="seed the dice (repeatable output)")
    args = ap.parse_args(argv)
    rng = random.Random(args.seed)
    pool = load_pool()
    blocks = []
    for _ in range(args.count):
        if args.floor is not None:
            rolls, item = luggage(args.floor, rng, pool, args.sure, args.band_up)
            blocks.append("\n".join(rolls + ([describe(item)] if item else [])))
        elif args.rarity:
            blocks.append(describe(finish(pick(args.rarity, rng, pool), rng)))
        else:
            item = {"name": "Spell Scroll", "scroll": args.scroll,
                    "rarity": SCROLL_RARITY[args.scroll],
                    "file": ITEMS / "Varies" / "Spell Scroll.md", "tline": "Scroll"}
            blocks.append(describe(finish(item, rng)))
    print("\n\n".join(blocks))


if __name__ == "__main__":
    main()
