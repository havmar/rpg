#!/usr/bin/env python3
"""The Hotel's luggage: one-use items and true magic items from the 13th Age SRD.

  python3 13th-age/tools/loot.py --floor 3            # a room's luggage roll (d20, hotel.md section 12)
  python3 13th-age/tools/loot.py --floor 3 --sure     # always an item: the d20 is rerolled 10+
  python3 13th-age/tools/loot.py --true champion      # one random true magic item of that tier
  python3 13th-age/tools/loot.py --one-use adventurer --count 3   # potions, oils, runes
  python3 13th-age/tools/loot.py --list epic          # every true item usable at that tier

A true magic item is picked by chakra first (each chakra file equally likely, so weapons
don't crowd out rings), then an item from that file listed at the tier or below: items
listed at a lower tier scale up with their "(champion: ...; epic: ...)" numbers. One true
item in ten is cursed instead (Cursed-Magic-Items.md). Bracers are monk-only weapon
powers and are rolled as a weapon. Prices are the SRD's for one-use items
(One-Use-Items.md); true magic items have no SRD price, so the Hotel's are in hotel.md.
"""
import argparse
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "srd" / "Magic-Items" / "Magic-Item-Descriptions"
TIERS = ["adventurer", "champion", "epic"]
SKIP = {"default bonus", "optional default bonus", "general"}
ENERGY = ["acid", "cold", "fire", "force", "holy", "lightning", "negative energy",
          "poison", "psychic", "thunder"]
HEALING = {"adventurer": ("Healing potion (adventurer)", "a recovery +1d8 hp, cap 30", 50),
           "champion": ("Healing potion (champion)", "a recovery +2d8 hp, cap 60", 100),
           "epic": ("Healing potion (epic)", "a recovery +3d8 hp, cap 100", 200)}
BONUS = {"adventurer": 1, "champion": 2, "epic": 3}


def tier_of_floor(floor):
    return "adventurer" if floor <= 4 else "champion" if floor <= 7 else "epic"


def parse(path):
    """[(name, tier or None, text)] for one item file."""
    items, tier, cur = [], None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(#{2,6})\s+(.*\S)\s*$", line)
        if m:
            level, title = len(m.group(1)), m.group(2)
            low = title.lower()
            if cur:
                items.append(cur)
                cur = None
            if level <= 2:
                tier = None
            elif low in TIERS:
                tier = low
            elif low in SKIP or low.endswith("magic items") or low == "shadow dragons":
                pass
            else:
                cur = [title, tier, []]
            continue
        if cur is not None and not line.startswith("---"):
            cur[2].append(line)
    if cur:
        items.append(cur)
    return [(n, t, "\n".join(x).strip()) for n, t, x in items]


def chakra_files():
    out = []
    for f in sorted(ITEMS.glob("*.md")):
        if f.stem in ("Magic-Item-Descriptions", "Cursed-Magic-Items", "Bracers"):
            continue
        out.append(f)
    return out


def pool(path, tier):
    rank = TIERS.index(tier)
    return [(n, t, x) for n, t, x in parse(path)
            if t is None or TIERS.index(t) <= rank]


def true_item(rng, tier):
    cursed = rng.randint(1, 10) == 1
    if cursed:
        path = ITEMS / "Cursed-Magic-Items.md"
        choices = pool(path, tier)
    else:
        files = [f for f in chakra_files() if pool(f, tier)]
        path = rng.choice(files)
        choices = pool(path, tier)
    name, listed, text = rng.choice(choices)
    chakra = path.stem.replace("-", " ")
    head = (f"TRUE MAGIC ITEM ({tier}{', CURSED' if cursed else ''}): {name} · "
            f"chakra: {chakra} · listed at {listed or 'any tier'} · "
            f"`{path.relative_to(ROOT.parent)}`")
    return head + "\n" + "\n".join("    " + ln for ln in text.splitlines() if ln.strip())


def one_use(rng, tier):
    r = rng.randint(1, 6)
    if r <= 3:
        name, what, gp = HEALING[tier]
        return f"ONE-USE: {name}: {what} · {gp} gp"
    if r == 4:
        e = rng.choice(ENERGY)
        gp = {"adventurer": 100, "champion": 200, "epic": 400}[tier]
        return f"ONE-USE: Potion of {e} resistance ({tier}): resist {e} 16+ for a battle · {gp} gp"
    b = BONUS[tier]
    if r == 5:
        gp = {"adventurer": 100, "champion": 200, "epic": 400}[tier]
        return f"ONE-USE: +{b} oil ({tier}): weapon, implement or armour, one battle · {gp} gp"
    gp = {"adventurer": 150, "champion": 300, "epic": 600}[tier]
    return (f"ONE-USE: +{b} rune ({tier}): as an oil, plus a d100 effect rolled when applied "
            f"(One-Use-Items.md: Runes) · {gp} gp")


def luggage(rng, floor, sure=False):
    tier = tier_of_floor(floor)
    d = rng.randint(1, 20)
    while sure and d < 10:
        d = rng.randint(1, 20)
    head = f"Luggage roll, floor {floor} ({tier}): d20 = {d}"
    if d <= 9:
        return head + " → nothing magic"
    if d <= 16:
        return head + " → " + one_use(rng, tier)
    return head + " → " + true_item(rng, tier)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--floor", type=int)
    ap.add_argument("--sure", action="store_true")
    ap.add_argument("--true", dest="true_tier", choices=TIERS)
    ap.add_argument("--one-use", dest="one_tier", choices=TIERS)
    ap.add_argument("--list", dest="list_tier", choices=TIERS)
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    if a.list_tier:
        for f in chakra_files():
            for n, t, _ in pool(f, a.list_tier):
                print(f"{f.stem}: {n} ({t or 'any'})")
        return
    for _ in range(a.count):
        if a.floor:
            print(luggage(rng, a.floor, a.sure))
        elif a.true_tier:
            print(true_item(rng, a.true_tier))
        elif a.one_tier:
            print(one_use(rng, a.one_tier))
        else:
            ap.error("give --floor N, --true TIER, --one-use TIER or --list TIER")


if __name__ == "__main__":
    main()
