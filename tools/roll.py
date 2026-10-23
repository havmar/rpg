#!/usr/bin/env python3
"""Dice roller for table play. Every roll is printed with its individual dice.

Usage:
  python3 tools/roll.py 1d20+3          # sum of dice plus modifier
  python3 tools/roll.py 4d6kh3          # keep highest 3 (attribute generation)
  python3 tools/roll.py 2d20kh1+5       # D&D advantage (keep highest 1)
  python3 tools/roll.py 2d20kl1+5       # D&D disadvantage (keep lowest 1)
  python3 tools/roll.py 5d6+2 --gb      # Godbound damage: each die read on the
                                        # damage chart, modifier on the best die
  python3 tools/roll.py 1d20 1d8 2d6    # several rolls at once

--gb applies to every roll in the call, so roll damage separately from hit rolls.
"""
import random
import re
import sys

DICE = re.compile(r"^(\d*)d(\d+)(?:(kh|kl)(\d+))?([+-]\d+)?$")


def godbound_damage(value):
    if value <= 1:
        return 0
    if value <= 5:
        return 1
    if value <= 9:
        return 2
    return 4


def roll(expr, gb=False):
    m = DICE.match(expr.lower())
    if not m:
        sys.exit(f"cannot parse '{expr}' (expected e.g. 1d20+3, 4d6kh3, 5d6)")
    count, sides = int(m.group(1) or 1), int(m.group(2))
    keep_mode, keep_n, mod = m.group(3), m.group(4), int(m.group(5) or 0)
    dice = [random.randint(1, sides) for _ in range(count)]

    if gb:
        # Modifier goes on whichever die it helps most.
        best = max(range(count), key=lambda i: godbound_damage(dice[i] + mod) - godbound_damage(dice[i]))
        parts = [dice[i] + (mod if i == best else 0) for i in range(count)]
        dmg = [godbound_damage(p) for p in parts]
        return f"{expr}: dice {dice} -> with mod {parts} -> damage {dmg} = {sum(dmg)}"

    kept = sorted(dice, reverse=keep_mode == "kh")[: int(keep_n)] if keep_mode else dice
    note = f" keep {kept}" if keep_mode else ""
    return f"{expr}: {dice}{note} {'+' if mod >= 0 else '-'} {abs(mod)} = {sum(kept) + mod}"


if __name__ == "__main__":
    args = sys.argv[1:]
    gb = "--gb" in args
    exprs = [a for a in args if a != "--gb"]
    if not exprs:
        sys.exit(__doc__)
    for e in exprs:
        print(roll(e, gb))
