#!/usr/bin/env python3
"""Eclipse Phase 2e dice roller. Every roll is printed.

Usage (from the repo root):
  python3 eclipse-phase/tools/roll.py test 55             # d100 (0-99) skill test vs target 55
  python3 eclipse-phase/tools/roll.py test 55 -20         # same, with a -20 modifier
  python3 eclipse-phase/tools/roll.py test 40 --default   # defaulting to an aptitude: crit successes ignored
  python3 eclipse-phase/tools/roll.py opposed 60 45       # opposed test, side A target vs side B target
  python3 eclipse-phase/tools/roll.py 2d10+3 1d6          # sums of dice (damage, stress, pools)
  add --seed N anywhere to make the rolls repeatable

Test rules (rulebook 03/01-how-to-play.md): roll <= target succeeds; doubles are criticals;
00 is always a critical success, 99 always a critical failure. A success of 33+ is one
superior success, 66+ two; a failure under 66 is one superior failure, under 33 two. A
critical replaces any superior result. Modifiers total at most +/-60 (clamped here).
"""
import random
import re
import sys

DICE = re.compile(r"^(\d*)d(\d+)([+-]\d+)?$")


def test(target, mod=0, default=False, roll=None):
    mod = max(-60, min(60, mod))
    tn = target + mod
    r = random.randint(0, 99) if roll is None else roll
    crit = r % 11 == 0
    ok = r == 0 or (r != 99 and r <= tn)
    if ok:
        sup = 2 if r >= 66 else 1 if r >= 33 else 0
    else:
        sup = 2 if r < 33 else 1 if r < 66 else 0
    if crit and ok and default:
        crit = False  # defaulting ignores critical successes
    word = "SUCCESS" if ok else "FAILURE"
    if crit:
        res = f"CRITICAL {word}"
    elif sup:
        res = f"{word}, {sup} superior"
    else:
        res = word
    return {"roll": r, "tn": tn, "ok": ok, "crit": crit, "sup": 0 if crit else sup,
            "text": f"d100 {r:02d} vs {tn}{f' ({target}{mod:+d})' if mod else ''}: {res}"}


def opposed(a, b):
    ra, rb = test(a), test(b)
    print("A " + ra["text"])
    print("B " + rb["text"])
    if ra["ok"] and not rb["ok"]:
        w = "A wins"
    elif rb["ok"] and not ra["ok"]:
        w = "B wins"
    elif ra["ok"] and rb["ok"]:
        if ra["crit"] != rb["crit"]:
            w = ("A" if ra["crit"] else "B") + " wins (critical beats a higher roll)"
        elif ra["roll"] != rb["roll"]:
            w = ("A" if ra["roll"] > rb["roll"] else "B") + " wins (higher roll)"
        else:
            w = "tie: higher skill wins, else deadlock"
    else:
        w = "both fail: deadlock, or higher roll/skill wins (GM's choice)"
    print(w)


def dice(expr):
    m = DICE.match(expr.lower())
    if not m:
        sys.exit(f"cannot parse '{expr}' (expected e.g. 2d10+3)")
    n, s, mod = int(m.group(1) or 1), int(m.group(2)), int(m.group(3) or 0)
    ds = [random.randint(1, s) for _ in range(n)]
    print(f"{expr}: {ds} {'+' if mod >= 0 else '-'} {abs(mod)} = {sum(ds) + mod}")


def main(argv):
    if "--seed" in argv:
        i = argv.index("--seed")
        random.seed(int(argv[i + 1]))
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "test":
        default = "--default" in argv
        nums = [int(a) for a in argv[1:] if a != "--default"]
        if not nums:
            sys.exit("test needs a target number")
        print(test(nums[0], sum(nums[1:]), default)["text"])
    elif argv[0] == "opposed":
        if len(argv) != 3:
            sys.exit("opposed needs two target numbers")
        opposed(int(argv[1]), int(argv[2]))
    else:
        for e in argv:
            dice(e)


if __name__ == "__main__":
    main(sys.argv[1:])
