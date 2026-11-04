#!/usr/bin/env python3
"""Roll dice. Usage: roll.py 1d20+5 2d6 d20 adv d20 dis"""
import random, re, sys

def roll(expr):
    m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", expr)
    if not m:
        sys.exit(f"bad dice: {expr}")
    n, sides, mod = int(m[1] or 1), int(m[2]), int(m[3] or 0)
    rolls = [random.randint(1, sides) for _ in range(n)]
    return rolls, mod

args = sys.argv[1:]
mode = None
for a in args:
    if a in ("adv", "dis"):
        mode = a
        continue
    rolls, mod = roll(a)
    if mode:
        rolls += roll(a)[0]
        pick = max(rolls) if mode == "adv" else min(rolls)
        print(f"{a} {mode}: {rolls} -> {pick + mod}")
        mode = None
    else:
        print(f"{a}: {rolls} -> {sum(rolls) + mod}")
