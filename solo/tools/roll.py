#!/usr/bin/env python3
"""Dice roller for the solo Godbound game. Every roll is printed with its individual dice.

Usage (from the repo root):
  python3 solo/tools/roll.py 1d20+1+4 --vs 20     # hit roll: d20 + attack bonus + target AC, 20 hits
  python3 solo/tools/roll.py 1d20 --vs 14         # saving throw or attribute check against a target
  python3 solo/tools/roll.py 1d20+4 --vs 9        # attribute check with a Fact (+4), check target 9
  python3 solo/tools/roll.py 1d8+2 --gb           # Godbound damage: each die read on the damage
  python3 solo/tools/roll.py 5d6+2 --gb           # chart, the modifier on the die it helps most
  python3 solo/tools/roll.py 4d6kh3 4d6kh3        # keep highest 3 (attributes); several rolls at once
  python3 solo/tools/roll.py 2d6 --for "reaction: ferryman"   # label the roll

  --vs N    success if the total is N or more; a natural 1 fails and a natural 20 succeeds
            (only for single-d20 rolls)
  --gb      read each die on the Godbound damage chart (1- none, 2-5 one, 6-9 two, 10+ four)
  --for X   label printed with the roll and written to the log
  --log F   append every result line to file F (the campaign's rolls.md)

The flags apply to every roll in the call, so roll damage separately from hit rolls.
"""
import argparse
import datetime
import random
import re
import sys

DICE = re.compile(r"^(\d*)d(\d+)(?:kh(\d+))?((?:[+-]\d+)*)$")


def godbound_damage(value):
    if value <= 1:
        return 0
    if value <= 5:
        return 1
    if value <= 9:
        return 2
    return 4


def roll(expr, gb=False, vs=None):
    m = DICE.match(expr.lower().replace(" ", ""))
    if not m:
        sys.exit(f"cannot parse '{expr}' (expected e.g. 1d20+3, 1d20+1+5, 4d6kh3, 5d6)")
    count, sides = int(m.group(1) or 1), int(m.group(2))
    keep = m.group(3)
    mod = sum(int(x) for x in re.findall(r"[+-]\d+", m.group(4)))
    dice = [random.randint(1, sides) for _ in range(count)]

    if gb:
        # Modifier goes on whichever die it helps most.
        best = max(range(count), key=lambda i: godbound_damage(dice[i] + mod) - godbound_damage(dice[i]))
        parts = [dice[i] + (mod if i == best else 0) for i in range(count)]
        dmg = [godbound_damage(p) for p in parts]
        return f"{expr}: dice {dice} -> with mod {parts} -> damage {dmg} = {sum(dmg)}"

    kept = sorted(dice, reverse=True)[: int(keep)] if keep else dice
    total = sum(kept) + mod
    note = f" keep {kept}" if keep else ""
    line = f"{expr}: {dice}{note} {'+' if mod >= 0 else '-'} {abs(mod)} = {total}"
    if vs is not None:
        if count == 1 and sides == 20 and dice[0] in (1, 20):
            ok, why = dice[0] == 20, f"natural {dice[0]}"
        else:
            ok, why = total >= vs, f"{total} vs {vs}"
        line += f" -> {'SUCCESS' if ok else 'FAILURE'} ({why})"
    return line


if __name__ == "__main__":
    p = argparse.ArgumentParser(usage=__doc__, add_help=False)
    p.add_argument("exprs", nargs="*")
    p.add_argument("--gb", action="store_true")
    p.add_argument("--vs", type=int)
    p.add_argument("--for", dest="label")
    p.add_argument("--log")
    a = p.parse_args()
    if not a.exprs:
        sys.exit(__doc__)
    label = f"[{a.label}] " if a.label else ""
    lines = [label + roll(e, a.gb, a.vs) for e in a.exprs]
    print("\n".join(lines))
    if a.log:
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(a.log, "a") as f:
            f.writelines(f"- {stamp} {l}\n" for l in lines)
