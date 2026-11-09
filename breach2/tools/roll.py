#!/usr/bin/env python3
"""Dice roller. Every roll is printed with its individual dice.

Usage:
  python3 breach2/tools/roll.py 1d20+5          # sum of dice plus modifier
  python3 breach2/tools/roll.py 1d20+5 --adv    # advantage: 2d20, keep the higher
  python3 breach2/tools/roll.py 1d20+5 --dis    # disadvantage: 2d20, keep the lower
  python3 breach2/tools/roll.py 4d6kh3          # keep highest 3 (ability scores)
  python3 breach2/tools/roll.py 2d20kl1+3       # keep lowest 1
  python3 breach2/tools/roll.py 1d20+5 --adv 1d10 --dis 1d20+2   # several at once

--adv and --dis apply to the roll just before them, and only to a plain 1d20. A natural
20 or 1 on a d20 is flagged as NAT20 / NAT1.
"""
import random
import re
import sys

DICE = re.compile(r"^(\d*)d(\d+)(?:k([hl])(\d+))?([+-]\d+)?$")


def parse(expr):
    m = DICE.match(expr.lower().strip())
    if not m:
        return None
    return (int(m.group(1) or 1), int(m.group(2)), m.group(3),
            int(m.group(4)) if m.group(4) else None, int(m.group(5) or 0))


def roll(expr, adv=False, dis=False):
    p = parse(expr)
    if not p:
        sys.exit(f"cannot parse '{expr}' (expected e.g. 1d20+3, 4d6kh3, 2d20kl1)")
    count, sides, keep_dir, keep, mod = p
    if count == 1 and sides == 20 and not keep and adv != dis:
        count, keep_dir, keep = 2, "h" if adv else "l", 1
    dice = [random.randint(1, sides) for _ in range(count)]
    if keep:
        kept = sorted(dice, reverse=(keep_dir == "h"))[:keep]
        note = f" keep {kept}"
    else:
        kept, note = dice, ""
    flag = ""
    if sides == 20 and len(kept) == 1:
        flag = " NAT20" if kept[0] == 20 else " NAT1" if kept[0] == 1 else ""
    return f"{expr}: {dice}{note} {'+' if mod >= 0 else '-'} {abs(mod)} = {sum(kept) + mod}{flag}"


def main(argv):
    rolls = []
    for a in argv:
        if a in ("--adv", "--dis"):
            if not rolls:
                sys.exit(f"{a} must follow a roll")
            rolls[-1][1 if a == "--adv" else 2] = True
        else:
            rolls.append([a, False, False])
    if not rolls:
        sys.exit(__doc__)
    for e, adv, dis in rolls:
        print(roll(e, adv, dis))


if __name__ == "__main__":
    main(sys.argv[1:])
