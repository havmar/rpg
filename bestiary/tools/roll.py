#!/usr/bin/env python3
"""Dice roller for table play. Every roll is printed with its individual dice.

Usage:
  python3 tools/roll.py 1d20+5          # sum of dice plus modifier
  python3 tools/roll.py 1d20+5 --adv    # advantage: 2d20, keep the higher
  python3 tools/roll.py 1d20+5 --dis    # disadvantage: 2d20, keep the lower
  python3 tools/roll.py 4d6kh3          # keep highest 3 (ability scores)
  python3 tools/roll.py 2d20kl1+3       # keep lowest 1
  python3 tools/roll.py 1d20+5 --adv 1d10 --dis 1d20+2   # several at once

  python3 tools/roll.py --keep DIR 1d20+5 --vs "AC 15" --result hit 1d10
                                                   # also log each roll for the table page

--adv and --dis apply to the roll just before them, and only to a plain 1d20. A natural
20 or 1 on a d20 is flagged as NAT20 / NAT1.

--keep DIR (a campaign folder, anywhere on the line) appends each roll, structured, to
DIR/live/rolls.jsonl as one JSON object a line (the table's Die: expr, faces, kept, mod,
total, vs, result, nat); `table.py beat` and `section` pick them up and clear the file.
--vs TEXT ("AC 15", "DC 11") and --result (hit · miss · cast · fizzle · save · fail) label
the roll just before them in that log; the printed line is unchanged.

  python3 tools/roll.py --keep DIR --label fizzle
  python3 tools/roll.py --keep DIR --label hit --label - --label "miss:AC 15"

--label RESULT[:VS] (no dice on the line) labels a roll already kept, once its result is
known (a cast that turned out a fizzle): one --label names the last kept roll, several name
the last few in order, oldest first; `-` leaves one as it is.
"""
import json
import random
import re
import sys
from pathlib import Path

DICE = re.compile(r"^(\d*)d(\d+)(?:k([hl])(\d+))?([+-]\d+)?$")
RESULTS = ("hit", "miss", "cast", "fizzle", "save", "fail")


def parse(expr):
    """(count, sides, keep_dir, keep, mod) or None."""
    m = DICE.match(expr.lower().strip())
    if not m:
        return None
    return (int(m.group(1) or 1), int(m.group(2)), m.group(3),
            int(m.group(4)) if m.group(4) else None, int(m.group(5) or 0))


def die(expr, faces, adv=False, dis=False, vs=None, result=None):
    """The table's Die from an expression and the faces rolled (advantage keeps the higher
    of two d20s, disadvantage the lower; kh/kl keep as written)."""
    p = parse(expr)
    if not p:
        raise ValueError(f"cannot parse '{expr}' (expected e.g. 1d20+3, 4d6kh3, 2d20kl1)")
    count, sides, keep_dir, keep, mod = p
    if count == 1 and sides == 20 and not keep and adv != dis:
        keep_dir, keep = "h" if adv else "l", 1
    if keep:
        kept = sorted(faces, reverse=(keep_dir == "h"))[:keep]
    else:
        kept = list(faces)
    nat = None
    if sides == 20 and len(kept) == 1 and kept[0] in (1, 20):
        nat = kept[0]
    return {"expr": expr, "faces": list(faces), "kept": kept, "mod": mod,
            "total": sum(kept) + mod, "vs": vs, "result": result, "nat": nat}


def roll(expr, adv=False, dis=False, keep_log=None):
    p = parse(expr)
    if not p:
        sys.exit(f"cannot parse '{expr}' (expected e.g. 1d20+3, 4d6kh3, 2d20kl1)")
    count, sides, keep_dir, keep, mod = p

    # Advantage and disadvantage cancel out, as in the rules.
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
    if keep_log is not None:
        keep_log.append(die(expr, dice, adv, dis))
    return f"{expr}: {dice}{note} {'+' if mod >= 0 else '-'} {abs(mod)} = {sum(kept) + mod}{flag}"


def main(argv):
    rolls = []  # [expr, adv, dis, vs, result]
    labels = []
    keep_dir = None
    args = list(argv)
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--adv", "--dis"):
            if not rolls:
                sys.exit(f"{a} must follow a roll")
            rolls[-1][1 if a == "--adv" else 2] = True
        elif a == "--label":
            if i + 1 >= len(args):
                sys.exit("--label needs a value")
            labels.append(args[i + 1])
            i += 1
        elif a in ("--keep", "--vs", "--result"):
            if i + 1 >= len(args):
                sys.exit(f"{a} needs a value")
            v = args[i + 1]
            i += 1
            if a == "--keep":
                keep_dir = Path(v)
            elif not rolls:
                sys.exit(f"{a} must follow a roll")
            elif a == "--vs":
                rolls[-1][3] = v
            else:
                if v.lower() not in RESULTS:
                    sys.exit(f"--result must be one of {', '.join(RESULTS)}")
                rolls[-1][4] = v.lower()
        else:
            rolls.append([a, False, False, None, None])
        i += 1
    if labels:
        if rolls:
            sys.exit("--label labels rolls already kept: give it no dice (or use --vs/--result on a new roll)")
        if keep_dir is None:
            sys.exit("--label needs --keep DIR (the campaign whose kept rolls to label)")
        relabel(keep_dir, labels)
        return
    if not rolls:
        sys.exit(__doc__)
    log = [] if keep_dir is not None else None
    for e, adv, dis, vs, res in rolls:
        print(roll(e, adv, dis, log))
        if log is not None:
            log[-1]["vs"], log[-1]["result"] = vs, res
    print("(narrate in chat before the next roll)")
    if log:
        live = keep_dir / "live"
        live.mkdir(parents=True, exist_ok=True)
        with open(live / "rolls.jsonl", "a") as f:
            for d in log:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")


def relabel(keep_dir, labels):
    p = Path(keep_dir) / "live" / "rolls.jsonl"
    kept = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()] if p.exists() else []
    if len(labels) > len(kept):
        sys.exit(f"--label: {len(labels)} label(s) but only {len(kept)} roll(s) kept in {p} "
                 "(the next table.py beat or section took the earlier ones)")
    for d, lab in zip(kept[len(kept) - len(labels):], labels):
        if lab == "-":
            continue
        res, _, vs = lab.partition(":")
        if res.lower() not in RESULTS:
            sys.exit(f"--label '{lab}': the result must be one of {', '.join(RESULTS)} (or - to skip)")
        d["result"] = res.lower()
        if vs:
            d["vs"] = vs
    p.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in kept))
    for d in kept[len(kept) - len(labels):]:
        print(f"{d['expr']}: {d['faces']} = {d['total']}" + (f" vs {d['vs']}" if d.get("vs") else "")
              + (f", {d['result']}" if d.get("result") else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
