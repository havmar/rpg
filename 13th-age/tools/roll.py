#!/usr/bin/env python3
"""Dice roller for table play. Every roll is printed with its individual dice.

Usage:
  python3 13th-age/tools/roll.py 1d20+5            # sum of dice plus modifier
  python3 13th-age/tools/roll.py 4d6kh3            # keep highest 3
  python3 13th-age/tools/roll.py 2d20kl1+3         # keep lowest 1
  python3 13th-age/tools/roll.py 1d20+7 3d8+4 1d6  # several at once

A natural 20 or 1 on a d20 is flagged as NAT20 / NAT1, and on a single d20 the line also
says whether it is even or odd (13th Age powers trigger on "natural even hit" and the like).
13th Age has no advantage; there are no --adv/--dis flags.
"""
import random
import re
import sys

DICE = re.compile(r"^(\d*)d(\d+)(?:k([hl])(\d+))?([+-]\d+)?$")


def roll(expr):
    m = DICE.match(expr.lower().strip())
    if not m:
        sys.exit(f"cannot parse '{expr}' (expected e.g. 1d20+3, 4d6kh3, 2d20kl1)")
    count, sides = int(m.group(1) or 1), int(m.group(2))
    keep_dir, keep = m.group(3), int(m.group(4)) if m.group(4) else None
    mod = int(m.group(5) or 0)
    dice = [random.randint(1, sides) for _ in range(count)]
    if keep:
        kept = sorted(dice, reverse=(keep_dir == "h"))[:keep]
        note = f" keep {kept}"
    else:
        kept, note = dice, ""
    flag = ""
    if sides == 20 and len(kept) == 1:
        nat = kept[0]
        flag = " NAT20" if nat == 20 else " NAT1" if nat == 1 else ""
        flag += " (even)" if nat % 2 == 0 else " (odd)"
    return f"{expr}: {dice}{note} {'+' if mod >= 0 else '-'} {abs(mod)} = {sum(kept) + mod}{flag}"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    for a in argv:
        print(roll(a))


if __name__ == "__main__":
    main(sys.argv[1:])
