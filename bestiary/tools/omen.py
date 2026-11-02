#!/usr/bin/env python3
"""The omen: a random SRD monster that themes the next scene (bestiary/CLAUDE.md, The omen).

Picks one stat block at random from reference/srd/Monsters by CR.md (every monster
equally likely), rolls what it is to the next scene on a d4 (an NPC, an enemy, a place or
a faction), and says how its CR sits against the party's level.

Usage:
  python3 bestiary/tools/omen.py --level 3          # the next omen for a level 3 party
  python3 bestiary/tools/omen.py --level 3 --seed 7 # repeatable
"""
import argparse
import random
import re
import sys
from fractions import Fraction
from pathlib import Path

SRD = Path(__file__).resolve().parents[2] / "reference" / "srd"
INDEX = SRD / "Monsters by CR.md"
ROW = re.compile(r"^\| ([\d/]+) \| \[(.+?)\]\((.+?)\) \| (.+?) \| (\d+)\D*? \| (\d+)\D*? \|$")

ROLES = {
    1: ("NPC", "someone to deal with: a patron, a rival, a witness, a prisoner, a "
               "merchant. Met with the reaction roll; a fight only if it goes that way."),
    2: ("Enemy", "the scene's opposition: a fight built around it, or its agents if it "
                 "is beyond the party."),
    3: ("Place", "a location made by it or for it: its lair, its shrine, its ruin, its "
                 "grave, a town named after it, a tavern where it drinks."),
    4: ("Faction", "a group that is it, serves it, hunts it, worships it or trades in it: "
                   "it gets a standing and an agenda on the faction sheet."),
}


def cr_value(text):
    return Fraction(text)


def monsters():
    out = []
    for line in INDEX.read_text().splitlines():
        m = ROW.match(line)
        if m:
            cr, name, link, kind, ac, hp = m.groups()
            out.append({"cr": cr, "name": name, "kind": kind, "ac": ac, "hp": hp,
                        "file": f"reference/srd/Monsters/{name}.md"})
    return out


def scale(cr, level):
    """How the monster's CR sits against the party's level."""
    c = cr_value(cr)
    if c <= Fraction(level, 4):
        return "Small fry: a pushover alone, a nuisance in numbers."
    if c <= level:
        return "Within reach: it can be met head on."
    if c <= level + 3:
        return "Dangerous: a fight with it is High or worse; parley, cheese or numbers."
    return ("Beyond them: it is not fought this scene. It is felt through its servants, "
            "its lair, its name, or seen from far off.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--level", type=int, required=True, help="the party's level")
    p.add_argument("--seed", type=int, help="seed for a repeatable omen")
    a = p.parse_args(argv)
    rng = random.Random(a.seed)
    pool = monsters()
    if not pool:
        sys.exit(f"no monsters found in {INDEX}")
    pick = rng.randrange(len(pool))
    mon = pool[pick]
    role = rng.randint(1, 4)
    name, what = ROLES[role]
    print(f"Omen d{len(pool)} [{pick + 1}]: {mon['name']} (CR {mon['cr']}, {mon['kind']}, "
          f"AC {mon['ac']}, {mon['hp']} HP)")
    print(f"As d4 [{role}]: {name}: {what}")
    print(f"Scale vs level {a.level}: {scale(mon['cr'], a.level)}")
    print(f"File: {mon['file']}")


if __name__ == "__main__":
    main()
