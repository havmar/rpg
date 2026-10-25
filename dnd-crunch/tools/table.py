#!/usr/bin/env python3
"""The GM's side of the table page: keeps a campaign's record and writes the page's store.

The data contract is dnd-crunch/web/README.md; the design is dnd-crunch/table-plan.md
(sections 5 to 7). The record, in the campaign folder DIR:

  morten.json        the sheet, as game/morten; character.md is rendered from it
  state.json         game/state as last written; state.md is rendered from it, the sheet
                     and map.json (the tower's view)
  story/sNNNN.json   the sections, written once; transcript.md is rendered from them
  live/open.json     the open section's head; live/bNNNN.json its beats
  live/rolls.jsonl   dice from `roll.py --keep DIR` not yet in a beat or section
  page.json          the page: url, each document's version as sent, the batches printed
                     and not yet sent, the moves read and not yet answered, the seq, the wake

It never talks to the network. Each verb writes the documents it changes as JSON under
DIR/page/out/<collection>/<doc_id>.json and prints the ArtifactData batch on stdout
({"writes": [{op, collection, doc_id, file_path, if_version}]}; if_version is left out on a
create), also saved as DIR/page/out/batch.json (batch-2.json, ... past 50 writes). Send it
with ArtifactData action "batch", then run `sent`. Notes go to stderr. game/realm reads
only map.json and the explored rooms of gm-secrets.md, never realms.json's hidden data.

Usage:
  table.py new DIR [--file opening.md] [--month N --day N --clock HH:MM --hex B5 --where TEXT]
  table.py open DIR --kind fight --title TEXT [--where TEXT] [--foes FILE|JSON]
  table.py beat DIR --text TEXT [--round N] [--hp 11/20] [--foe "Darkmantle=13/22" ...]
                [--line "WHO/KIND[/N]: TEXT" ...] [--die "EXPR:FACES[:VS[:RESULT]]" ...]
  table.py section DIR --file s.md [--die ...] [the state options]
  table.py state DIR [--status S] [--awaiting KIND --prompt TEXT] [--orders auto|FILE]
                [--doing TEXT] [--dial who=you ...] [--month N --day N --clock --hex --where]
  table.py morten DIR [--hp 11|+5|-3] [--lose SPELL] [--regain SPELL|all] [--coins "+15 GP"]
                [--xp +150] [--item "Potion of Healing -1"] [--light TEXT] [--conc Sleep] ...
  table.py realm DIR [--rumour "A5=TEXT" ...] [--hex-name "B5=TEXT" ...]
  table.py rules DIR
  table.py aside DIR (--file msg.md | --text TEXT) [--ooc] [--answers m0007|all]
  table.py log DIR TEXT
  table.py moves DIR --file DUMP_DIR|moves.json
  table.py sent DIR [--url URL] [--version game/state=4 ...] [--drop]
  table.py resend DIR
  table.py wake DIR  ·  table.py no-wake DIR
  table.py export DIR OUTDIR
  table.py render DIR

`table.py VERB --help` explains each. TABLE_NOW=2026-10-25T09:00:00Z fixes the clock (one
minute later per stamp), for reproducible fixtures.
"""
import argparse
import copy
import json
import os
import re
import sys
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ noise in the repo
HERE = Path(__file__).resolve().parent
GAME = HERE.parent  # dnd-crunch/
sys.path.insert(0, str(HERE))
import realms as R  # noqa: E402
from gen_dungeon import THRESHOLD  # noqa: E402
from roll import RESULTS, die as make_die, parse as parse_expr  # noqa: E402

MAX_WRITES = 50   # ArtifactData batch limit
SECTION_KINDS = ("orders", "travel", "fight", "rest", "shop", "delve", "domain", "death",
                 "wrap", "aside", "opening")
LINE_WHO = ("morten", "foe", "gm", "world")
LINE_KIND = ("roll", "cast", "attack", "save", "damage", "note", "move")
STATUS = ("awaiting", "playing", "ended")
AWAIT = ("orders", "fight", "turn", "word", "none")
DIALS = {"who": ("dm", "you"), "stop": ("month", "orders", "fight", "round", "matters"),
         "fights": ("live", "turning", "summary", "line"), "world": ("story", "report"),
         "dice": ("key", "all", "none"), "mode": ("open", "closed")}
DEFAULT_TABLE = {"who": "dm", "stop": "month", "fights": "live", "world": "story",
                 "dice": "key", "mode": "open"}
DIAL_WORDS = {"who": {"dm": "the GM", "you": "you"},
              "stop": {"month": "never in the month (at the next month's orders)",
                       "orders": "at each month's orders", "fight": "before each fight",
                       "round": "each round", "matters": "when something matters"},
              "fights": {"live": "live, every round", "turning": "turning points",
                         "summary": "summary after", "line": "one line"},
              "world": {"story": "story", "report": "full report"},
              "dice": {"key": "key rolls", "all": "all", "none": "none"},
              "mode": {"open": "open", "closed": "closed"}}
FOE_STATES = ("healthy", "bloodied", "near death", "dead")
MOVE_KINDS = ("say", "play", "orders", "fight", "turn", "table", "take")
PLAY_SCOPES = ("month", "matters", "fight", "round", "stop")
MISSIONS = ("strike", "rob", "contact", "delve")
ACTION = re.compile(r"^(buy:[a-z_ ]+(@[A-D][1-5])?|raise:(force|cunning|wealth)|repair:(a\d+|tower)"
                    r"|move:a\d+>[A-D][1-5](,a\d+>[A-D][1-5])*"
                    r"|attack:a\d+>(a\d+|[A-Za-z]+)(,a\d+>(a\d+|[A-Za-z]+))*|seize:[A-D][1-5])$")
MAX_TEXT = 4000
COIN = {"PP": 1000, "GP": 100, "EP": 50, "SP": 10, "CP": 1}

# ---- game/realm words (the page knows no rules) ----
WORDS = {
    "force": "Force: soldiers, and the strength to take and hold land.",
    "cunning": "Cunning: spies, informers and friends in the right places.",
    "wealth": "Wealth: trade, land and coffers.",
    "piece": "A piece is something a realm has put on the map: soldiers, spies or income.",
    "regime": "The realm's health as a power; at 0 it falls.",
    "level": "Level N: floor N lies under it, its wanderers are level-N trouble, and it pays "
             "N×10 GP a month.",
    "seat": "The hex the ruler sits in; with no soldiers left there, the court itself fights.",
    "hostile": "A hostile realm spends its month punishing the tower, for 3 months (6 for a seat).",
    "ally": "An ally is a good ruler not hostile to the tower.",
    "tier": "Tier 1, 2 or 3: how big a fight it is when Morten goes after it (Low, Moderate, High).",
    "occupied": "A hex with another realm's soldiers in it pays its holder nothing.",
}
KIND_WHAT = {"thugs": "hired toughs", "militia": "armed townsfolk",
             "beasts": "the people's beasts of war", "walls": "stone walls and a garrison",
             "knights": "mounted soldiers", "warband": "a host of veteran warriors",
             "informers": "eyes and ears in the hex", "smugglers": "a smuggling ring",
             "saboteurs": "wreckers and arsonists", "seditionists": "a plot against the throne",
             "assassins": "killers for hire", "court_mage": "a mage at court",
             "farms": "farmland and its folk", "caravans": "traders on the road",
             "mine": "a working mine", "mercenaries": "paid soldiers",
             "treasury": "a strongroom of gold", "toll_road": "a road that pays its owner"}
KIND_GLYPH = {"thugs": "fight", "militia": "shield", "beasts": "skull", "walls": "door",
              "knights": "sword", "warband": "flag", "informers": "eye", "smugglers": "bag",
              "saboteurs": "spark", "seditionists": "speech", "assassins": "mask",
              "court_mage": "hat", "farms": "globe", "caravans": "cart", "mine": "gear",
              "mercenaries": "hand", "treasury": "coins", "toll_road": "boots"}
ATTR_WORD = {"F": "Force", "C": "Cunning", "W": "Wealth"}
TIER_FIGHT = {1: "Low", 2: "Moderate", 3: "High"}

# ---- game/rules: (id, title, file, heading) cut by heading, so they never drift ----
RULES = [("cast", "Roll to cast", "CLAUDE.md", "### Roll to cast"),
         ("death", "Death and the respawn", "CLAUDE.md", "### Death is a respawn"),
         ("campaign", "This campaign's rules", "rules.md", None),
         ("pieces", "Pieces (assets)", "realms.md", "## 4. Assets"),
         ("missions", "Morten's month: travel and missions", "realms.md", "## 7. Morten's month"),
         ("actions", "The world's turn: actions and prices", "realms.md", "## 5. The domain turn"),
         ("leaders", "Leaders and their labels", "realms.md", "## 8. Leaders"),
         ("report", "Report style", "CLAUDE.md", "## Report style")]


class Bad(Exception):
    """A bad input: one-line error, nothing written."""


def note(*a):
    print(*a, file=sys.stderr)


def jload(p, default=None):
    p = Path(p)
    if not p.exists():
        return copy.deepcopy(default)
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise Bad(f"{p}: not JSON ({e})")


def jdump(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def jarg(v):
    """A JSON argument: inline JSON, or a path to a JSON file."""
    if v is None:
        return None
    s = v.strip()
    if s[:1] in "[{\"" or s in ("null", "true", "false"):
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            raise Bad(f"bad JSON: {e}")
    return jload(Path(s)) if Path(s).exists() else _missing(s)


def _missing(s):
    raise Bad(f"no such file: {s}")


def sid(prefix, n):
    return f"{prefix}{n:04d}"


def fmt_int(n):
    return f"{n:,}"


# ---- coins ----

def cp_of(text):
    t = (text or "").replace("−", "-").strip()
    if t.lower() in ("", "none", "0"):
        return 0
    total = 0
    for n, c in re.findall(r"(\d[\d,]*)\s*(PP|GP|EP|SP|CP)", t, re.I):
        total += int(n.replace(",", "")) * COIN[c.upper()]
    if not total and not re.search(r"\d", t):
        raise Bad(f"cannot read coins '{text}' (e.g. 22 GP 7 SP 5 CP)")
    return total


def coins_text(cp):
    if cp <= 0:
        return "none"
    gp, r = divmod(cp, 100)
    sp, c = divmod(r, 10)
    bits = [f"{fmt_int(gp)} GP" if gp else "", f"{sp} SP" if sp else "", f"{c} CP" if c else ""]
    return " ".join(b for b in bits if b)


def coins_change(cur, spec):
    """'+15 GP', '-62 GP 5 SP', '=7 SP 5 CP' (a bare amount sets it)."""
    s = spec.replace("−", "-").strip()
    if s[:1] == "+":
        return coins_text(cp_of(cur) + cp_of(s[1:]))
    if s[:1] == "-":
        left = cp_of(cur) - cp_of(s[1:])
        if left < 0:
            raise Bad(f"only {cur} to spend, not {s[1:].strip()}")
        return coins_text(left)
    return coins_text(cp_of(s.lstrip("=")))


def num_change(cur, spec, lo=None, hi=None):
    s = str(spec).replace("−", "-").strip()
    if not re.fullmatch(r"[+\-=]?\d+", s):
        raise Bad(f"not a number change: '{spec}' (e.g. 11, +5, -3)")
    v = cur + int(s) if s[0] in "+-" else int(s.lstrip("="))
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def now(page):
    base = os.environ.get("TABLE_NOW")
    if base:
        t = datetime.strptime(base, "%Y-%m-%dT%H:%M:%SZ") + timedelta(minutes=page["ticks"])
        page["ticks"] += 1
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- dice and lines ----

def parse_die(spec):
    """'1d20+5:15:DC 11:cast', '2d8:7,6', '1d20+5 adv:14,15:AC 13:hit' → a Die."""
    parts = spec.split(":")
    if len(parts) < 2:
        raise Bad(f"--die '{spec}': expected EXPR:FACES[:VS[:RESULT]]")
    head = parts[0].split()
    expr, flags = head[0], {w.lower() for w in head[1:]}
    p = parse_expr(expr)
    if not p:
        raise Bad(f"--die '{spec}': cannot parse '{expr}'")
    try:
        faces = [int(x) for x in parts[1].replace(" ", "").split(",") if x]
    except ValueError:
        raise Bad(f"--die '{spec}': faces must be numbers")
    count, sides, _, keep, _ = p
    adv, dis = "adv" in flags, "dis" in flags
    want = 2 if (count == 1 and sides == 20 and not keep and adv != dis) else count
    if len(faces) != want or any(not 1 <= f <= sides for f in faces):
        raise Bad(f"--die '{spec}': {want} face(s) of 1–{sides} expected, got {faces}")
    vs = parts[2].strip() or None if len(parts) > 2 else None
    res = parts[3].strip().lower() or None if len(parts) > 3 else None
    if res and res not in RESULTS:
        raise Bad(f"--die '{spec}': result must be one of {', '.join(RESULTS)}")
    return make_die(expr, faces, adv, dis, vs, res)


LINE = re.compile(r"^(?:R(\d+)\s+)?(\w+)/(\w+)(?:/(\d+))?:\s*(.+)$")


def parse_line(spec):
    """'R2 morten/cast/1: Thunderwave holds...' → (round, who, kind, n, text)."""
    m = LINE.match(spec.strip())
    if not m:
        raise Bad(f"line '{spec}': expected [R2 ]WHO/KIND[/N]: TEXT")
    rnd, who, kind, n, text = m.groups()
    if who not in LINE_WHO:
        raise Bad(f"line '{spec}': who must be one of {', '.join(LINE_WHO)}")
    if kind not in LINE_KIND:
        raise Bad(f"line '{spec}': kind must be one of {', '.join(LINE_KIND)}")
    return (int(rnd) if rnd else None, who, kind, int(n) if n is not None else None, text.strip())


def build_lines(specs, dice, rnd=None, default=None, fight=False):
    """Lines from specs, each taking its N dice in order; the last line with no N takes the
    rest. With no specs and some dice, one line from `default`."""
    dice = list(dice)
    parsed = [parse_line(s) for s in specs]
    if not parsed and default and (dice or default):
        parsed = [(None, "gm", "roll" if dice else "note", None, default)]
    last_free = max((i for i, p in enumerate(parsed) if p[3] is None), default=None)
    out = []
    for i, (r, who, kind, n, text) in enumerate(parsed):
        take = n if n is not None else (len(dice) if i == last_free else 0)
        if take > len(dice):
            raise Bad(f"line '{text[:40]}…' takes {take} dice, only {len(dice)} left")
        line = {"text": text, "who": who, "kind": kind}
        r = r if r is not None else rnd
        if fight and r is not None:
            line["round"] = r
        line["dice"] = dice[:take]
        dice = dice[take:]
        out.append(line)
    if dice:
        raise Bad(f"{len(dice)} dice left over with no line to take them (add /N to a line)")
    return out


def die_text(d):
    p = parse_expr(d["expr"])
    sides = p[1] if p else "?"
    if len(d["faces"]) == 1:
        s = f"d{sides} {d['faces'][0]}"
    elif len(d["kept"]) < len(d["faces"]):
        s = f"d{sides} {', '.join(map(str, d['faces']))} keep {'+'.join(map(str, d['kept']))}"
    else:
        s = f"{len(d['faces'])}d{sides}: {'+'.join(map(str, d['faces']))}"
    if d["mod"]:
        s += f" {'+' if d['mod'] > 0 else '−'}{abs(d['mod'])}"
    if d["mod"] or len(d["kept"]) > 1:
        s += f" = {d['total']}"
    if d.get("vs"):
        s += f" vs {d['vs']}"
    if d.get("nat"):
        s += f", NAT {d['nat']}"
    if d.get("result"):
        s += f", {d['result'].upper()}"
    return s


# ---- Markdown in: front matter and body ----

def parse_value(v):
    v = v.strip()
    if not v:
        return None
    if v[0] in "[{\"" or v in ("true", "false", "null") or re.fullmatch(r"-?\d+", v):
        try:
            return json.loads(v)
        except json.JSONDecodeError as e:
            raise Bad(f"front matter value {v[:40]!r}: {e}")
    if len(v) > 1 and v[0] == v[-1] == "'":
        return v[1:-1]
    return v


def parse_md(text):
    """(front matter dict, body). Front matter: `key: value` lines between --- lines;
    a value is JSON when it looks like JSON; indented lines continue the value."""
    lines = text.splitlines()
    fm = {}
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            raise Bad("front matter has no closing ---")
        key, buf = None, []
        for ln in lines[1:end]:
            if ln.strip().startswith("#") and key is None:
                continue
            m = re.match(r"^([A-Za-z]\w*):\s?(.*)$", ln)
            if m and not ln[:1].isspace():
                if key:
                    fm[key] = parse_value("\n".join(buf))
                key, buf = m.group(1), [m.group(2)]
            elif key:
                buf.append(ln)
        if key:
            fm[key] = parse_value("\n".join(buf))
        lines = lines[end + 1:]
    return fm, "\n".join(lines)


def body_parts(body):
    """{heading (lower-case, '' for the top): [lines]} for ## to #### headings."""
    parts, cur = {"": []}, ""
    for ln in body.splitlines():
        m = re.match(r"^#{2,4}\s+(.*?)\s*$", ln)
        if m:
            cur = m.group(1).lower()
            parts.setdefault(cur, [])
            continue
        parts[cur].append(ln)
    return parts


def blocks(lines):
    """(paragraphs, bullets) from Markdown lines; a bullet's indented lines continue it."""
    paras, bullets, buf, cur = [], [], [], None
    for ln in lines + [""]:
        if re.match(r"^\s*[-*]\s+", ln) and not ln.startswith("  "):
            if buf:
                paras.append(" ".join(buf))
                buf = []
            cur = re.sub(r"^\s*[-*]\s+", "", ln).strip()
            bullets.append(cur)
        elif ln.strip() == "":
            if buf:
                paras.append(" ".join(buf))
                buf = []
            cur = None
        elif cur is not None and ln.startswith((" ", "\t")):
            bullets[-1] = bullets[-1] + " " + ln.strip()
        else:
            cur = None
            buf.append(ln.strip())
    return paras, bullets


def label_bullet(b):
    m = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", b) or re.match(r"^\*\*(.+?)\*\*:\s*(.*)$", b)
    return {"label": m.group(1).strip(), "text": m.group(2).strip()} if m else {"label": "", "text": b}


# ---- the record ----

PAGE0 = {"v": 1, "campaign": None, "url": None, "lastSeq": 0, "lastMove": 0, "versions": {},
         "pending": [], "moves": {}, "answered": [], "ticks": 0, "wake": {"on": False},
         "realm": {"rumours": {}, "hexNames": {}}}


class Camp:
    def __init__(self, d, need_page=True):
        self.d = Path(d).resolve()
        if not self.d.is_dir():
            raise Bad(f"no campaign folder {d}")
        pj = self.d / "page.json"
        if need_page and not pj.exists():
            raise Bad(f"no {pj}; run `table.py new {d}` first")
        self.page = copy.deepcopy(PAGE0)
        self.page.update(jload(pj, {}))
        self.out = self.d / "page" / "out"
        self.morten = jload(self.d / "morten.json")
        self.state = jload(self.d / "state.json")
        self.map = jload(self.d / "map.json")
        self.writes = []
        self.mutated = False

    # seq and time
    def next_seq(self):
        self.page["lastSeq"] += 1
        if self.state is not None:
            self.state["lastSeq"] = self.page["lastSeq"]
        return self.page["lastSeq"]

    def now(self):
        return now(self.page)

    # documents
    def out_path(self, coll, doc_id):
        return self.out / coll / f"{doc_id}.json"

    def put(self, coll, doc_id, body):
        body = {"v": 1, **{k: v for k, v in body.items() if k != "v"}}
        jdump(self.out_path(coll, doc_id), body)
        self.writes.append(("set", coll, doc_id))
        return body

    def drop(self, coll, doc_id):
        self.writes.append(("delete", coll, doc_id))

    def sync(self, coll, doc_id, body, force=False):
        """Write a singleton only when it differs from the copy last written."""
        body = {"v": 1, **{k: v for k, v in body.items() if k != "v"}}
        old = jload(self.out_path(coll, doc_id))
        if force or old != body or f"{coll}/{doc_id}" not in self.projected():
            self.put(coll, doc_id, body)

    def projected(self):
        """Each document's version once every pending batch has been sent."""
        v = dict(self.page["versions"])
        for batch in self.page["pending"]:
            for e in batch:
                apply_version(v, e)
        return v

    def flush(self):
        """Pin the writes, split them into batches of 50, save and print them."""
        vers = self.projected()
        last, order = {}, []
        for op, coll, doc_id in self.writes:
            key = (coll, doc_id)
            if key not in last:
                order.append(key)
            last[key] = op
        entries = []
        for coll, doc_id in order:
            op = last[(coll, doc_id)]
            v = vers.get(f"{coll}/{doc_id}")
            if op == "delete" and not v:
                note(f"note: {coll}/{doc_id} is not in the store; no delete")
                continue
            e = {"op": op, "collection": coll, "doc_id": doc_id}
            if op == "set":
                e["file_path"] = str(self.out_path(coll, doc_id))
            if v:
                e["if_version"] = v
            entries.append(e)
        self.writes = []
        self.save()
        for old in self.out.glob("batch*.json"):
            old.unlink()
        if not entries:
            note("nothing to send")
            return []
        chunks = [entries[i:i + MAX_WRITES] for i in range(0, len(entries), MAX_WRITES)]
        files = []
        for i, ch in enumerate(chunks):
            f = self.out / ("batch.json" if i == 0 else f"batch-{i + 1}.json")
            jdump(f, {"writes": ch})
            self.page["pending"].append(ch)
            files.append(f)
        self.save()
        if len(chunks) > 1:
            note(f"{len(entries)} writes: split into {len(chunks)} batches of at most "
                 f"{MAX_WRITES} ({', '.join(f.name for f in files)}); send them in order.")
        note(f"send with ArtifactData batch (url: {self.page['url'] or 'the page'}), then "
             f"`table.py sent {self.rel()}`: " + ", ".join(f.name for f in files))
        for ch in chunks:
            print(json.dumps({"writes": ch}, indent=1, ensure_ascii=False))
        return chunks

    def rel(self):
        try:
            return str(self.d.relative_to(Path.cwd()))
        except ValueError:
            return str(self.d)

    def save(self):
        jdump(self.d / "page.json", self.page)
        if self.morten is not None:
            jdump(self.d / "morten.json", self.morten)
        if self.state is not None:
            jdump(self.d / "state.json", self.state)

    # live section
    def open_head(self):
        return jload(self.d / "live" / "open.json")

    def beats(self):
        return sorted((jload(p) for p in (self.d / "live").glob("b[0-9]*.json")),
                      key=lambda b: b["seq"])

    def take_rolls(self):
        p = self.d / "live" / "rolls.jsonl"
        if not p.exists():
            return []
        out = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]
        p.unlink()
        return out

    def peek_rolls(self):
        p = self.d / "live" / "rolls.jsonl"
        return [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()] if p.exists() else []

    def sections(self):
        return sorted((jload(p) for p in (self.d / "story").glob("s[0-9]*.json")),
                      key=lambda s: s["seq"])

    def need_morten(self):
        if self.morten is None:
            raise Bad(f"no {self.d / 'morten.json'} (the sheet)")
        return self.morten

    def need_map(self):
        if self.map is None:
            raise Bad(f"no {self.d / 'map.json'}")
        return self.map


def apply_version(v, e):
    k = f"{e['collection']}/{e['doc_id']}"
    if e["op"] == "delete":
        v.pop(k, None)
    else:
        v[k] = v.get(k, 0) + 1


# ---- projections ----

def lost_spells(m):
    return [s["name"] for s in m.get("spells", []) if s.get("lost")]


def hud(m, reaction=True):
    return {"hp": m["hp"], "maxHp": m["maxHp"],
            "ac": m.get("acArmor", m["ac"]) if m.get("armorOn") else m["ac"],
            "acArmor": m.get("acArmor"), "armorOn": bool(m.get("armorOn")),
            "light": m.get("light"), "conc": m.get("conc"),
            "conditions": m.get("conditions", []), "exhaustion": m.get("exhaustion", 0),
            "reaction": m.get("reaction", reaction), "inspiration": m.get("inspiration", False),
            "freeArmor": m.get("freeArmor", False), "coins": m.get("coins", {}).get("on", "none"),
            "lost": lost_spells(m)}


def proj_state(c):
    s, m = c.state, c.need_morten()
    s["lastSeq"], s["lastMove"] = c.page["lastSeq"], c.page["lastMove"]
    s["level"], s["xp"], s["deaths"] = m["level"], m["xp"], m.get("deaths", 0)
    s["hud"] = hud(m)
    s["table"] = {**DEFAULT_TABLE, **{k: v for k, v in s.get("table", {}).items() if k in DIALS},
                  "habits": list(m.get("habits", []))}
    s["wake"], s["url"] = c.page["wake"], c.page["url"]
    order = ["campaign", "status", "lastSeq", "lastMove", "month", "day", "clock", "hex",
             "where", "level", "xp", "deaths", "hud", "table", "awaiting", "live", "latest",
             "lastFight", "doing", "checkIn", "wake", "url"]
    doc = {"v": 1, **{k: s.get(k) for k in order}}
    c.state = {k: v for k, v in doc.items() if k != "v"}
    return doc


def proj_morten(c):
    return {"v": 1, **c.need_morten()}


def hex_by_id(mp):
    return {h["id"]: h for h in mp["hexes"]}


def faction(mp, name):
    return next((f for f in mp["factions"] if f["name"] == name), None)


def leader_label(f):
    L = f["leader"] if f else None
    return f"{L['label']}: {L['verb']}" if L and L.get("label") else None


def hex_name(mp, h, extra=None):
    if extra and h in extra:
        return extra[h]
    x = hex_by_id(mp)[h]
    who = "the tower's" if x["holder"] == "tower" else f"the {R.poss(x['holder'])}"
    return f"{who} {x['biome']}" + (" with its lake" if x.get("lake") else "")


def days_from(mp, start):
    H = hex_by_id(mp)
    days, q = {start: 0}, deque([start])
    while q:
        h = q.popleft()
        for n in H[h]["neighbours"]:
            if n not in days:
                days[n] = days[h] + 1
                q.append(n)
    return {h["id"]: days.get(h["id"]) for h in mp["hexes"]}


def strip_ids(t):
    return re.sub(r"\s+a\d+\b", "", t or "")


def event_text(e, mp):
    who = "Morten" if e["actor"] == "tower" else f"The {e['actor']}"
    tgt, res = strip_ids(e.get("target")), e.get("result") or ""
    to, fr = e.get("to_hex"), e.get("from_hex")
    act = e.get("action")
    if act == "Mission":
        return f"Morten's mission: {tgt} ({res})."
    if act == "Buy":
        tgt = re.sub(r"^\S+' |^\S+'s ", "", tgt)
        return f"{who} bought {tgt} in {to} ({res})."
    if act == "Move":
        return f"{who} moved {tgt} from {fr} into {to}."
    if act == "Attack":
        return f"{who} attacked {tgt} in {to}: {res}."
    if act == "Seize":
        return f"{who} moved to seize {tgt}: {res}."
    if act == "Goal":
        return f"{who} reached a goal: {tgt} ({res})."
    return f"{who}: {act} {tgt} ({res})."


def events_words(mp):
    return [{"n": i, "who": e["actor"], "from": e.get("from_hex"), "to": e.get("to_hex"),
             "action": e.get("action"), "text": event_text(e, mp)}
            for i, e in enumerate(mp.get("events", []), 1)]


def rumours_of(mp, at):
    """realms.py's rumours, from map.json alone (the tower's view)."""
    H = hex_by_id(mp)
    near = {at, *H[at]["neighbours"]}
    out = []
    for f in mp["factions"]:
        if f["tower"] or not near & set(f["hexes"]):
            continue
        L = f["leader"]
        ev = [e for e in mp.get("events", []) if e["actor"] == f["name"] and e["action"] != "Move"]
        last = "; ".join(f"{e['action'].lower()} {strip_ids(e['target'])} ({e['result']})"
                         for e in ev[:3]) or "quiet"
        out.append(f"{L['title']} {L['name']} of the {f['name']} ({leader_label(f)}) is after: "
                   f"{strip_ids(f['goal']) or 'nothing yet'}. Last month: {last}. The regime "
                   f"stands at {f['hp']}/{f['max_hp']} HP.")
    return out


def kinds():
    out = {}
    for k, A in R.ASSETS.items():
        atk = A["atk"]
        out[A["name"]] = {
            "glyph": KIND_GLYPH.get(k, "hex"), "type": A["type"][0], "tier": A["tier"],
            "needs": f"{A['type'][0]}{A['needs']}", "what": KIND_WHAT.get(k, ""),
            "cost": A["cost"], "hp": A["hp"],
            "hits": (f"hits with {ATTR_WORD[atk[0]]} against {ATTR_WORD[atk[1]]} for {atk[2]}"
                     if atk else "doesn't attack"),
            "counter": f"hits back {A['ctr']}" if A["ctr"] else "doesn't hit back",
            "upkeep": A["upkeep"], "income": A["income"], "moves": A["move"],
            "special": A["special"], "fight": TIER_FIGHT[A["tier"]] + " fight"}
    return out


FLOOR_HEAD = re.compile(r"^## Floor (\d+) · ([A-D][1-5])\b")
ROOM_CELL = re.compile(r"^(\d+\.\d+)\s*(✓)?\s*(?:\((.*)\))?\s*$")


def parse_secrets(path):
    """gm-secrets.md's floors: {hex: {"floor": N, "rooms": [{n, explored, note, encounter,
    cr, xp, difficulty, size, feature, coins}]}}. Only the GM's tools read this."""
    floors, cur = {}, None
    if not Path(path).exists():
        return floors
    for ln in Path(path).read_text().splitlines():
        m = FLOOR_HEAD.match(ln)
        if m:
            cur = {"floor": int(m.group(1)), "rooms": []}
            floors[m.group(2)] = cur
            continue
        if ln.startswith("## "):
            cur = None
            continue
        if cur is None or not ln.startswith("|"):
            continue
        cells = [x.strip() for x in ln.strip().strip("|").split("|")]
        rm = ROOM_CELL.match(cells[0]) if cells else None
        if not rm or len(cells) < 8:
            continue
        cur["rooms"].append({"n": rm.group(1), "explored": bool(rm.group(2)),
                             "note": rm.group(3), "encounter": cells[1], "cr": cells[2],
                             "xp": cells[3], "difficulty": cells[4], "size": cells[5],
                             "feature": cells[6], "coins": cells[7]})
    return floors


def plural(name, n):
    if n == 1:
        return name
    if name.startswith("Swarm"):
        return name.replace("Swarm", "Swarms", 1)
    if name.endswith("lf"):
        return name[:-1] + "ves"
    if name.endswith(("s", "x", "sh", "ch")):
        return name + "es"
    return name + "s"


def monster_words(enc):
    m = re.match(r"^(\d+)×\s*(.+)$", enc)
    if not m:
        return enc
    n, name = int(m.group(1)), m.group(2)
    return plural(name, n) if n == 1 else f"{n} {plural(name, n)}"


def floors_public(c):
    """The explored rooms by hex; an entered floor's other rooms as unknown, with no monster;
    a floor never entered has no rooms listed."""
    out = {}
    for h, f in parse_secrets(c.d / "gm-secrets.md").items():
        seen = [r for r in f["rooms"] if r["explored"]]
        rooms = []
        if seen:
            for r in f["rooms"]:
                if r["explored"]:
                    rooms.append({"n": r["n"], "monster": monster_words(r["encounter"]),
                                  "cr": r["cr"], "state": "cleared", "xp": r["xp"],
                                  "difficulty": r["difficulty"], "size": r["size"],
                                  "feature": r["feature"], "note": r["note"]})
                else:
                    rooms.append({"n": r["n"], "monster": None, "cr": None, "state": "unknown"})
        out[h] = {"floor": f["floor"], "rooms": rooms,
                  "cleared": bool(seen) and len(seen) == len(f["rooms"])}
    return out


def proj_realm(c):
    mp = copy.deepcopy(c.need_map())
    extra = c.page.get("realm", {})
    rum = {h["id"]: rumours_of(mp, h["id"]) + extra.get("rumours", {}).get(h["id"], [])
           for h in mp["hexes"]}
    return {"v": 1, **mp, "words": WORDS, "kinds": kinds(), "rumours": rum,
            "floors": floors_public(c), "days": days_from(mp, mp["morten"]["hex"]),
            "eventsWords": events_words(mp),
            "hexNames": {h["id"]: hex_name(mp, h["id"], extra.get("hexNames")) for h in mp["hexes"]}}


def cut(text, heading):
    """The section under `heading` (a line prefix), up to the next heading of its level or
    higher; nested headings become ###, quote marks are dropped."""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    start = next((i for i, ln in enumerate(lines) if ln.startswith(heading)), None)
    if start is None:
        raise Bad(f"heading '{heading}' not found (the rules moved: fix RULES in table.py)")
    out = []
    for ln in lines[start + 1:]:
        m = re.match(r"^(#+)\s", ln)
        if m and len(m.group(1)) <= level:
            break
        if m:
            ln = "### " + ln[len(m.group(1)):].strip()
        out.append(re.sub(r"^>\s?", "", ln))
    return "\n".join(out).strip() + "\n"


def proj_rules(c):
    secs = []
    for sid_, title, src, heading in RULES:
        p = (c.d / src) if src == "rules.md" else (GAME / src)
        if not p.exists():
            continue
        text = p.read_text()
        if heading:
            md = cut(text, heading)
        else:
            md = "\n".join(ln for ln in text.splitlines() if not ln.startswith("# ")).strip() + "\n"
        secs.append({"id": sid_, "title": title, "md": md})
    return {"v": 1, "sections": secs}


# ---- awaiting: the orders form's choices ----

def orders_auto(c):
    mp, m = c.need_map(), c.need_morten()
    H = hex_by_id(mp)
    here = mp["morten"]["hex"]
    days = days_from(mp, here)
    extra = c.page.get("realm", {}).get("hexNames")
    tower = next(f for f in mp["factions"] if f["tower"])
    floors = floors_public(c)
    hexes = sorted(({"id": h, "name": hex_name(mp, h, extra), "days": days[h]} for h in H),
                   key=lambda x: (x["days"], x["id"]))
    missions = []
    for hx in hexes:
        h, d = hx["id"], hx["days"]
        x = H[h]
        for a in x["assets"]:
            if a["owner"] == "tower":
                continue
            missions.append({"type": "strike", "target": a["id"], "hex": h, "days": d,
                             "label": f"Strike the {R.poss(a['owner'])} {a['name']} in {h} "
                                      f"({TIER_FIGHT[a['tier']]} fight, 2d6 to it)"})
            if a["type"] == "Wealth":
                gp = a["tier"] * R.ROB_GP * (R.ROB_TREASURY if a["name"] == "Treasury" else 1)
                missions.append({"type": "rob", "target": a["id"], "hex": h, "days": d,
                                 "label": f"Rob the {R.poss(a['owner'])} {a['name']} in {h} "
                                          f"(up to {fmt_int(gp)} GP, {TIER_FIGHT[a['tier']]} fight)"})
        holder = x["holder"]
        if holder != "tower":
            f = faction(mp, holder)
            if f and f["seat"] == h and not any(a["owner"] == holder and a["type"] == "Force"
                                                for a in x["assets"]):
                missions.append({"type": "strike", "target": holder, "hex": h, "days": d,
                                 "label": f"Strike the {R.poss(holder)} unguarded seat in {h} "
                                          f"(High fight, 2d6 to their {f['hp']}/{f['max_hp']} HP)"})
            if f:
                dc = R.CONTACT_DC + f["cunning"] - (R.TYRANT_CONTACT if f["leader"].get("tag") == "Tyrant" else 0)
                missions.append({"type": "contact", "target": h, "hex": h, "days": d,
                                 "label": f"Contact the {holder} of {h} (Persuasion DC {dc})"})
        fl = floors.get(h)
        if fl:
            state = " (cleared)" if fl["cleared"] else ""
            missions.append({"type": "delve", "target": f"floor {fl['floor']}", "hex": h, "days": d,
                             "label": f"Delve floor {fl['floor']} under {h}{state}"})
    funds = tower["treasury"] + max(0, tower.get("income", 0))
    actions = []
    homes = [h for h in tower["hexes"] if h == tower["seat"] or any(
        a["owner"] == "tower" and a["type"] == "Force" for a in H[h]["assets"])]
    for k, A in R.ASSETS.items():
        if k == "seditionists" or A["land"]:
            continue
        if tower[R.TYPE_ATTR[A["type"]]] < A["needs"]:
            continue
        for h in homes:
            actions.append({"action": f"buy:{k}@{h}", "label": f"Buy {A['name']} in {h}",
                            "cost": A["cost"], "affordable": A["cost"] <= funds})
    for attr in ("force", "cunning", "wealth"):
        if tower[attr] < R.MAX_RATING:
            cost = R.RAISE[tower[attr] + 1]
            actions.append({"action": f"raise:{attr}", "label": f"Raise {attr.capitalize()} to "
                            f"{tower[attr] + 1}", "cost": cost, "affordable": cost <= funds})
    for h in H.values():
        for a in h["assets"]:
            if a["owner"] == "tower" and a["hp"] < a["max_hp"]:
                key = next(k for k, A in R.ASSETS.items() if A["name"] == a["name"])
                cost = R.ASSETS[key]["cost"] // R.REPAIR_DIV
                actions.append({"action": f"repair:{a['id']}", "label": f"Repair the "
                                f"{a['name']} in {h['id']}", "cost": cost, "affordable": cost <= funds})
    if tower["hp"] < tower["max_hp"]:
        actions.append({"action": "repair:tower", "label": "Repair the tower (1d6 HP)",
                        "cost": R.REPAIR_HP_GP, "affordable": R.REPAIR_HP_GP <= funds})
    realms_ = [f["name"] for f in sorted((f for f in mp["factions"] if not f["tower"]),
                                         key=lambda f: (not f["ally"], f["name"]))]
    return {"hexes": hexes, "missions": missions, "actions": actions, "realms": realms_,
            "funds": {"treasury": tower["treasury"], "income": tower.get("income", 0),
                      "onMorten": m.get("coins", {}).get("on", "none"),
                      "text": f"{fmt_int(tower['treasury'])} GP in the treasury, "
                              f"+{fmt_int(tower.get('income', 0))} GP income before the tower acts"}}


# ---- moves ----

def is_str(x, empty=True):
    return isinstance(x, str) and (empty or x.strip()) and len(x) <= MAX_TEXT


def validate_move(m, hexes=None):
    """(errors, warnings) for one move against the README's move table."""
    errs, warn = [], []
    if not isinstance(m, dict):
        return ["not an object"], []
    if m.get("v") != 1:
        errs.append("v must be 1")
    if not isinstance(m.get("seq"), int) or isinstance(m.get("seq"), bool) or m.get("seq", 0) < 1:
        errs.append("seq must be a whole number ≥ 1")
    if not is_str(m.get("at"), False):
        errs.append("at must be a time string")
    k = m.get("kind")
    fields = {"say": ("text", "ooc"), "play": ("scope", "text"),
              "orders": ("travel", "mission", "action", "give", "plan"),
              "fight": ("choice", "text"), "turn": ("text",), "table": ("table",),
              "take": ("who",)}
    if k not in fields:
        errs.append(f"kind must be one of {', '.join(MOVE_KINDS)}")
        return errs, warn
    extra = set(m) - {"v", "seq", "at", "kind", *fields[k]}
    if extra:
        warn.append(f"ignored fields: {', '.join(sorted(extra))}")
    if k == "say":
        if not is_str(m.get("text"), False):
            errs.append("say.text must be a non-empty string (≤ 4,000 characters)")
        if not isinstance(m.get("ooc"), bool):
            errs.append("say.ooc must be true or false")
    elif k == "play":
        if m.get("scope") not in PLAY_SCOPES:
            errs.append(f"play.scope must be one of {', '.join(PLAY_SCOPES)}")
        if m.get("text") is not None and not is_str(m.get("text")):
            errs.append("play.text must be a string")
    elif k == "orders":
        t = m.get("travel")
        if not isinstance(t, str) or (hexes is not None and t not in hexes) or (
                hexes is None and not re.fullmatch(r"[A-D][1-5]", t or "")):
            errs.append("orders.travel must be a hex id on the map")
        mi = m.get("mission")
        if mi is not None and not (isinstance(mi, dict) and mi.get("type") in MISSIONS
                                   and is_str(mi.get("target"), False)):
            errs.append(f"orders.mission must be null or {{type: {'/'.join(MISSIONS)}, target}}")
        ac = m.get("action")
        if ac is not None and not (isinstance(ac, str) and ACTION.match(ac)):
            errs.append("orders.action must be null or the engine's --action (e.g. buy:farms@B5)")
        g = m.get("give")
        if g is not None and not (isinstance(g, dict) and is_str(g.get("realm"), False)
                                  and isinstance(g.get("gp"), int) and not isinstance(g.get("gp"), bool)
                                  and g["gp"] >= 1):
            errs.append("orders.give must be null or {realm, gp ≥ 1}")
        if not is_str(m.get("plan")):
            errs.append("orders.plan must be a string")
        for key in ("mission", "action", "give"):
            if key not in m:
                errs.append(f"orders.{key} is missing (null for none)")
    elif k == "fight":
        if m.get("choice") not in ("fight", "avoid", "plan"):
            errs.append("fight.choice must be fight, avoid or plan")
        if not is_str(m.get("text")):
            errs.append("fight.text must be a string")
    elif k == "turn":
        if not is_str(m.get("text"), False):
            errs.append("turn.text must be a non-empty string")
    elif k == "table":
        t = m.get("table")
        if not isinstance(t, dict):
            errs.append("table.table must be the dials object")
        else:
            for d, vals in DIALS.items():
                if t.get(d) not in vals:
                    errs.append(f"table.{d} must be one of {', '.join(vals)}")
            h = t.get("habits")
            if h is not None and not (isinstance(h, list) and all(is_str(x, False) for x in h)):
                errs.append("table.habits must be a list of strings")
            bad = set(t) - set(DIALS) - {"habits"}
            if bad:
                warn.append(f"ignored dials: {', '.join(sorted(bad))}")
    elif k == "take":
        if m.get("who") not in ("you", "dm"):
            errs.append("take.who must be you or dm")
    return errs, warn


def move_words(m, mp=None):
    k = m.get("kind")
    q = lambda s: json.dumps(s, ensure_ascii=False)  # noqa: E731
    if k == "say":
        return f"{'asks out of game' if m.get('ooc') else 'says (in game)'}: {q(m.get('text'))}"
    if k == "play":
        return f"play, scope {m.get('scope')}" + (f", steer {q(m['text'])}" if m.get("text") else "")
    if k == "orders":
        mi, g = m.get("mission"), m.get("give")
        t = m.get("travel")
        name = ""
        if mp and t in hex_by_id(mp):
            name = f" ({hex_name(mp, t)}, {days_from(mp, mp['morten']['hex'])[t]} days)"
        bits = [f"travel to {t}{name}",
                f"mission {mi['type']} {mi['target']}" if mi else "no mission",
                f"tower action {m.get('action')}" if m.get("action") else "no tower action",
                f"give {g['gp']} GP to the {g['realm']}" if g else "no gift"]
        return "orders: " + " · ".join(bits) + (f"; plan {q(m['plan'])}" if m.get("plan") else "")
    if k == "fight":
        return f"before the fight: {m.get('choice')}" + (f", {q(m['text'])}" if m.get("text") else "")
    if k == "turn":
        return f"Morten's turn: {q(m.get('text'))}"
    if k == "table":
        t = m.get("table") or {}
        return "table dials: " + ", ".join(f"{d} {t.get(d)}" for d in DIALS) + (
            f"; habits {q(t['habits'])}" if t.get("habits") is not None else "")
    if k == "take":
        return "takes Morten over" if m.get("who") == "you" else "hands Morten back to the GM"
    return f"unknown kind {q(k)}"


def move_text(m):
    k = m.get("kind")
    if k in ("say", "turn"):
        return m.get("text")
    if k == "fight":
        return f"{m.get('choice')}: {m.get('text') or ''}".strip(": ")
    if k == "orders":
        return m.get("plan") or move_words(m)
    if k == "play":
        return f"{m.get('scope')}" + (f": {m['text']}" if m.get("text") else "")
    return move_words(m)


def read_moves(src):
    """[(doc_id, version, body)] from an ArtifactData out_dir dump or a JSON file."""
    src = Path(src)
    found = []

    def unwrap(obj, default_id):
        if isinstance(obj, dict) and isinstance(obj.get("data"), dict):
            body, ver = obj["data"], obj.get("version")
            did = obj.get("doc_id") or obj.get("id") or default_id
        elif isinstance(obj, dict) and "version" in obj and "kind" in obj:
            ver = obj["version"]
            did = obj.get("doc_id") or obj.get("id") or default_id
            body = {k: v for k, v in obj.items() if k not in ("version", "doc_id", "id", "collection")}
        else:
            body, ver, did = obj, None, default_id
        if did is None and isinstance(body, dict) and isinstance(body.get("seq"), int):
            did = sid("m", body["seq"])
        found.append((did, ver if isinstance(ver, int) else 1, body))

    if src.is_dir():
        files = sorted(p for p in src.rglob("*.json") if p.parent.name == "moves") or sorted(src.rglob("*.json"))
        for p in files:
            unwrap(jload(p), p.stem)
        return found
    obj = jload(src)
    if obj is None:
        raise Bad(f"no such file: {src}")
    items = None
    if isinstance(obj, list):
        items = obj
    elif isinstance(obj, dict):
        items = next((obj[k] for k in ("moves", "documents") if isinstance(obj.get(k), list)), None)
    if items is not None:
        for it in items:
            unwrap(it, None)
    elif isinstance(obj, dict) and obj and all(isinstance(v, dict) and re.fullmatch(r"m\d{4}", k)
                                               for k, v in obj.items()):
        for k, v in obj.items():
            unwrap(v, k)
    else:
        unwrap(obj, None)
    return found


def answer_moves(c, ids):
    """Delete the moves `ids` (pinned) and return (answered ids, words)."""
    answered, words = [], []
    for mid in ids:
        mv = c.page["moves"].pop(mid, None)
        if mv is None:
            continue
        c.drop("moves", mid)
        c.page["answered"].append(mid)
        c.page["lastMove"] = max(c.page["lastMove"], mv["seq"])
        if mv["ok"]:
            answered.append(mid)
            if mv.get("text"):
                words.append({"move": mid, "text": mv["text"]})
    return answered, words


def pick_moves(c, spec):
    if not spec:
        return []
    if spec == ["all"] or spec == "all":
        return sorted(c.page["moves"])
    out = []
    for s in spec:
        for mid in s.split(","):
            mid = mid.strip()
            if mid not in c.page["moves"]:
                raise Bad(f"move {mid} is not among the moves read (run `moves` first)")
            out.append(mid)
    return out


# ---- state options (state, section, open) ----

def add_state_opts(p):
    g = p.add_argument_group("game/state")
    g.add_argument("--status", choices=STATUS)
    g.add_argument("--awaiting", choices=AWAIT, help="what the player is asked for now")
    g.add_argument("--prompt", help="the answer box's line, e.g. \"Month 3's orders\"")
    g.add_argument("--orders", help="awaiting orders: 'auto' (from map.json) or a JSON file/inline")
    g.add_argument("--fight", help="awaiting fight: {title, foes, difficulty, xp} (file or JSON)")
    g.add_argument("--turn", help="awaiting turn: {board, lines, options} (file or JSON)")
    g.add_argument("--doing", help="what the GM is doing now ('' clears it)")
    g.add_argument("--check-in", dest="check_in", help="the check-in line ('' clears it)")
    g.add_argument("--dial", action="append", default=[], help="who=you, stop=fight, fights=summary, …")
    g.add_argument("--table", help="the whole dials object (file or JSON)")
    for k in ("month", "day"):
        g.add_argument(f"--{k}", type=int)
    for k in ("clock", "hex", "where"):
        g.add_argument(f"--{k}")


def apply_state_opts(c, a):
    s = c.state
    for k in ("month", "day", "clock", "hex", "where"):
        if getattr(a, k, None) is not None:
            s[k] = getattr(a, k)
    if getattr(a, "table", None):
        t = jarg(a.table)
        if not isinstance(t, dict):
            raise Bad("--table must be an object of dials")
        a.dial = a.dial + [f"{k}={v}" for k, v in t.items() if k in DIALS]
        if isinstance(t.get("habits"), list):
            c.need_morten()["habits"] = [str(x) for x in t["habits"]]
    for d in a.dial or []:
        k, _, v = d.partition("=")
        if k not in DIALS or v not in DIALS[k]:
            raise Bad(f"--dial {d}: dials are " + "; ".join(f"{k}: {'/'.join(v)}" for k, v in DIALS.items()))
        s.setdefault("table", dict(DEFAULT_TABLE))[k] = v
    if a.awaiting:
        aw = {"kind": a.awaiting, "prompt": a.prompt or "", "orders": None, "fight": None, "turn": None}
        if a.awaiting == "orders":
            aw["orders"] = orders_auto(c) if (a.orders or "auto") == "auto" else jarg(a.orders)
        if a.awaiting == "fight":
            if not a.fight:
                raise Bad("--awaiting fight needs --fight {title, foes, difficulty, xp}")
            aw["fight"] = jarg(a.fight)
        if a.awaiting == "turn":
            if not a.turn:
                raise Bad("--awaiting turn needs --turn {board, lines, options}")
            aw["turn"] = jarg(a.turn)
        s["awaiting"] = aw
        if not a.status:
            s["status"] = "playing" if a.awaiting == "none" else "awaiting"
    elif a.prompt is not None and s.get("awaiting"):
        s["awaiting"]["prompt"] = a.prompt
    if a.status:
        s["status"] = a.status
    if a.doing is not None:
        s["doing"] = a.doing or None
    if a.check_in is not None:
        s["checkIn"] = a.check_in or None


def fresh_state(c, a):
    mp = c.map or {}
    hx = a.hex or (mp.get("morten") or {}).get("hex")
    return {"campaign": c.page.get("campaign") or c.d.name, "status": "playing",
            "month": a.month or mp.get("month") or 1, "day": a.day or 1,
            "clock": a.clock or "08:00", "hex": hx,
            "where": a.where or (hex_name(mp, hx) if mp and hx else ""),
            "table": dict(DEFAULT_TABLE),
            "awaiting": {"kind": "none", "prompt": "", "orders": None, "fight": None, "turn": None},
            "live": None, "latest": None, "lastFight": None, "doing": None, "checkIn": None}


def finish(c, *, morten=True, realm=False, rules=False, state=True):
    """Common tail: sync the singletons, write game/state, render, flush."""
    if morten and c.morten is not None:
        c.sync("game", "morten", proj_morten(c))
    if realm and c.map is not None:
        c.sync("game", "realm", proj_realm(c))
    if rules:
        c.sync("game", "rules", proj_rules(c))
    if state and c.state is not None:
        c.put("game", "state", proj_state(c))
    render_all(c)
    return c.flush()


# ---- verbs ----

def cmd_new(a):
    c = Camp(a.dir, need_page=False)
    if (c.d / "page.json").exists() and not a.force:
        raise Bad(f"{c.d / 'page.json'} exists: this campaign has a page (--force to reseed)")
    c.need_morten()
    c.need_map()
    if a.force:
        keep = {k: c.page[k] for k in ("url", "versions", "pending", "lastSeq", "lastMove", "ticks")}
        c.page = copy.deepcopy(PAGE0)
        c.page.update(keep)
    c.page["campaign"] = a.campaign or c.d.name
    c.state = fresh_state(c, a)
    c.put("game", "morten", proj_morten(c))
    c.put("game", "realm", proj_realm(c))
    c.put("game", "rules", proj_rules(c))
    if a.file:
        write_section(c, Path(a.file).read_text(), [], kind_default="opening", close=False)
    finish(c, morten=False)


def cmd_open(a):
    c = Camp(a.dir)
    if c.open_head():
        raise Bad(f"a section is open ({c.open_head()['title']}); settle it with `section` first")
    if a.kind not in SECTION_KINDS or a.kind == "aside":
        raise Bad(f"--kind must be one of {', '.join(k for k in SECTION_KINDS if k != 'aside')}")
    m, s = c.need_morten(), c.state
    foes = jarg(a.foes) if a.foes else []
    if not isinstance(foes, list) or not all(isinstance(f, dict) and f.get("name") for f in foes):
        raise Bad("--foes must be a list of Foe objects with a name")
    at = c.now()
    head = {"kind": a.kind, "title": a.title, "month": s["month"], "day": a.day or s["day"],
            "clock": a.clock or s.get("clock"), "hex": s.get("hex"), "where": a.where or s.get("where"),
            "foes": foes, "openedAt": at, "morten": {"hp": m["hp"], "maxHp": m["maxHp"]},
            "lost": lost_spells(m), "xp": m["xp"]}
    jdump(c.d / "live" / "open.json", head)
    s["live"] = {"kind": a.kind, "title": a.title, "month": head["month"], "day": head["day"],
                 "openedAt": at}
    s["status"] = "playing"
    for k in ("where", "clock", "day"):
        if getattr(a, k):
            s[k] = getattr(a, k)
    if a.doing is not None:
        s["doing"] = a.doing or None
    finish(c)


def foe_names(foes):
    out = []
    for f in foes:
        n = f.get("count", 1) or 1
        if n > 1:
            out += [(f"{f['name']} {chr(65 + i)}", f) for i in range(n)]
        else:
            out.append((f["name"], f))
    return out


def cmd_beat(a):
    c = Camp(a.dir)
    head = c.open_head()
    if not head:
        raise Bad("no open section: `table.py open DIR --kind fight --title …` first")
    m = c.need_morten()
    dice = c.peek_rolls() + [parse_die(d) for d in a.die]
    lines = build_lines(a.line, dice, a.round, default=a.text, fight=head["kind"] == "fight")
    prev = (c.beats() or [None])[-1]
    st = copy.deepcopy(prev["state"]) if prev else {
        "morten": dict(head["morten"]),
        "foes": [{"name": n, "hp": f.get("hp"), "maxHp": f.get("maxHp", f.get("hp"))}
                 for n, f in foe_names(head["foes"])]}
    if a.hp:
        hp, _, mx = a.hp.partition("/")
        st["morten"] = {"hp": int(hp), "maxHp": int(mx or m["maxHp"])}
        m["hp"] = int(hp)
    for spec in a.foe:
        name, _, val = spec.partition("=")
        if not name or not val:
            raise Bad(f"--foe '{spec}': expected NAME=13/22 or NAME=bloodied")
        row = next((f for f in st["foes"] if f["name"] == name), None)
        if row is None:
            row = {"name": name}
            st["foes"].append(row)
        if re.fullmatch(r"\d+(/\d+)?", val):
            hp, _, mx = val.partition("/")
            row["hp"] = int(hp)
            if mx:
                row["maxHp"] = int(mx)
            row.pop("state", None)
        elif val in FOE_STATES:
            row["hp"], row["state"] = None, val
        else:
            raise Bad(f"--foe '{spec}': HP as 13/22 or a state ({', '.join(FOE_STATES)})")
    seq = c.next_seq()
    beat = {"seq": seq, "section": {k: head[k] for k in ("kind", "title", "month", "day", "where", "foes")},
            "round": a.round, "text": a.text, "lines": lines, "state": st, "at": c.now()}
    c.take_rolls()
    beat = c.put("live", sid("b", seq), beat)
    jdump(c.d / "live" / f"{sid('b', seq)}.json", beat)
    c.save()
    render_all(c)
    c.flush()


def hp_track(head, beats, rounds):
    names = [("Morten", head["morten"]["maxHp"], head["morten"]["hp"])]
    for n, f in foe_names(head.get("foes", [])):
        names.append((n, f.get("maxHp", f.get("hp")), f.get("hp")))
    for b in beats:
        for f in b["state"].get("foes", []):
            if f["name"] not in [x[0] for x in names]:
                names.append((f["name"], f.get("maxHp"), f.get("hp")))
    track = []
    for name, mx, start in names:
        hp, cur = [start], start
        for r in range(1, rounds + 1):
            for b in beats:
                if (b.get("round") or 0) != r:
                    continue
                row = b["state"]["morten"] if name == "Morten" else next(
                    (f for f in b["state"].get("foes", []) if f["name"] == name), None)
                if row and "hp" in row:
                    cur = row["hp"]
                    mx = row.get("maxHp", mx)
            hp.append(cur)
        track.append({"name": name, "max": mx, "hp": hp})
    return track


def build_fight(fm, head, beats, m):
    head = head or {"morten": {"hp": m["hp"], "maxHp": m["maxHp"]}, "foes": fm.get("foes") or [],
                    "lost": [], "xp": m["xp"]}
    rounds = fm.get("rounds") or max([b.get("round") or 0 for b in beats] or [0])
    init = fm.get("initiative") or []
    if isinstance(init, str):
        init = [x.strip() for x in re.split(r"\s*[›>,]\s*", init) if x.strip()]
    lost = fm.get("lost")
    if lost is None:
        lost = [s for s in lost_spells(m) if s not in head.get("lost", [])]
    track = fm.get("hpTrack") or (hp_track(head, beats, rounds) if beats else [])
    return {"foes": fm.get("foes") or head.get("foes") or [], "difficulty": fm.get("difficulty"),
            "budget": fm.get("budget"), "xp": fm.get("xp"), "initiative": init, "rounds": rounds,
            "outcome": fm.get("outcome") or "cleared", "verdict": fm.get("verdict"),
            "hpTrack": track, "loot": fm.get("loot"), "lost": lost,
            "potion": bool(fm.get("potion", False)),
            "xpBefore": fm.get("xpBefore", head.get("xp")), "xpAfter": fm.get("xpAfter", m["xp"])}


def build_domain(fm, parts, c):
    mp = c.need_map()
    ev = {e["n"]: e for e in events_words(mp)}

    def bul(*names):
        for n in names:
            if n in parts:
                return blocks(parts[n])
        return [], []

    plan = bul("the plan", "plan")
    hap = []
    for b in bul("what happened", "happened")[1]:
        mm = re.match(r"^n=(\d+)(?:\s+who=(\S+))?:\s*(.+)$", b)
        if not mm:
            raise Bad(f"what happened: '{b[:50]}…' must start with n=N: (an event of map.json)")
        n = int(mm.group(1))
        if n not in ev:
            raise Bad(f"what happened: no event {n} in map.json (1–{len(ev)})")
        e = ev[n]
        who = mm.group(2) or e["who"]
        f = faction(mp, who)
        lab = (f or {}).get("leader", {})
        hap.append({"n": n, "who": who, "label": lab.get("label"), "verb": lab.get("verb"),
                    "text": mm.group(3).strip(), "from": e["from"], "to": e["to"]})
    paras, bl = bul("elsewhere")
    elsewhere = " ".join(paras + bl)
    tower = []
    for b in bul("the tower now", "tower")[1]:
        mm = re.match(r"^(.+?):\s*(.+?)\s*(?:→|->)\s*(.+)$", b)
        tower.append({"what": mm.group(1).strip("* "), "before": mm.group(2), "after": mm.group(3)}
                     if mm else {"what": b, "before": None, "after": None})
    nxt = {"threats": [], "chances": [], "open": []}
    for b in bul("next month", "next")[1]:
        mm = re.match(r"^\**(Threats?|Chances?|Open)\**:\**\s*(.+)$", b, re.I)
        if not mm:
            raise Bad(f"next month: '{b[:50]}…' must start with Threat:, Chance: or Open:")
        key = {"t": "threats", "c": "chances", "o": "open"}[mm.group(1)[0].lower()]
        nxt[key].append(mm.group(2).strip())
    for key in ("threats", "chances", "open"):
        nxt[key] += bul(key)[1]
    income = bul("income")[1]
    log = bul("log")[1]
    if not log:
        log = (jload(c.d / "realms.json") or {}).get("log", [])  # the engine keeps only public lines
    return {"plan": plan[1] or plan[0] or mp.get("report", {}).get("plan", []), "happened": hap,
            "elsewhere": elsewhere, "tower": tower, "next": nxt, "income": income, "log": log}


def write_section(c, text, extra_dice, kind_default=None, close=True, answers=None, ooc=False):
    fm, body = parse_md(text)
    head = c.open_head() if close else None
    beats = c.beats() if head else []
    kind = fm.get("kind") or (head or {}).get("kind") or kind_default
    if kind not in SECTION_KINDS:
        raise Bad(f"kind must be one of {', '.join(SECTION_KINDS)} (front matter `kind:`)")
    if not fm.get("title") and not (head or {}).get("title") and kind != "aside":
        raise Bad("a section needs a title (front matter `title:`)")
    m, s = c.need_morten(), c.state
    parts = body_parts(body)
    paras, bullets = blocks(parts[""])
    trace = [ln for b in beats for ln in b["lines"]]
    tl = blocks(parts["trace"])[1] if "trace" in parts else []
    dice = c.peek_rolls() + extra_dice
    if tl or dice:
        trace += build_lines(tl, dice, fight=kind == "fight",
                             default=None if tl else "Dice rolled for this section.")
    c.take_rolls()
    ids = pick_moves(c, answers) if answers is not None else sorted(c.page["moves"])
    answered, words = answer_moves(c, ids)
    seq = c.next_seq()
    src = head or {}
    sec = {"seq": seq, "kind": kind,
           "month": fm.get("month", src.get("month", s.get("month"))),
           "day": fm.get("day", src.get("day", s.get("day"))),
           "clock": fm.get("clock", s.get("clock")), "hex": fm.get("hex", src.get("hex", s.get("hex"))),
           "where": fm.get("where", src.get("where", s.get("where"))),
           "title": fm.get("title", src.get("title", "")),
           "headline": fm.get("headline") or (paras.pop(0) if kind != "aside" and paras else ""),
           "prose": paras, "bullets": [label_bullet(b) for b in bullets], "trace": trace,
           "answered": answered,
           "after": {"hp": m["hp"], "maxHp": m["maxHp"], "xp": m["xp"],
                     "coins": m.get("coins", {}).get("on", "none"), "lost": lost_spells(m)},
           "fight": build_fight(fm, head, beats, m) if kind == "fight" else None,
           "domain": build_domain(fm, parts, c) if kind == "domain" else None,
           "words": words}
    if kind == "aside":
        sec["ooc"] = bool(fm.get("ooc", ooc))
    doc_id = sid("s", seq)
    sec = c.put("story", doc_id, sec)
    jdump(c.d / "story" / f"{doc_id}.json", sec)
    s["latest"] = doc_id
    if kind == "fight":
        s["lastFight"] = doc_id
    for k in ("month", "day", "clock", "hex", "where"):
        if k in fm:
            s[k] = fm[k]
    if head:
        for b in beats:
            c.drop("live", sid("b", b["seq"]))
            (c.d / "live" / f"{sid('b', b['seq'])}.json").unlink()
        (c.d / "live" / "open.json").unlink()
        s["live"] = None
    if kind != "aside":
        for k in sorted(c.projected()):
            if k.startswith("log/"):
                c.drop("log", k[4:])
        for k in sorted(c.projected()):  # beats left from an earlier open section
            if k.startswith("live/") and head is None and not (c.d / "live" / f"{k[5:]}.json").exists():
                c.drop("live", k[5:])
    return sec


def cmd_section(a):
    c = Camp(a.dir)
    keep = c.state, c.morten  # check the state options before anything is written
    c.state, c.morten = copy.deepcopy(keep[0]), copy.deepcopy(keep[1])
    apply_state_opts(c, a)
    c.state, c.morten = keep
    sec = write_section(c, Path(a.file).read_text(), [parse_die(d) for d in a.die],
                        answers=a.answers or None)
    apply_state_opts(c, a)
    note(f"section {sid('s', sec['seq'])} ({sec['kind']}): {sec['title']}")
    finish(c, realm=sec["kind"] == "domain")


def cmd_state(a):
    c = Camp(a.dir)
    applied = []
    for mid, mv in sorted(c.page["moves"].items()):
        if not mv["ok"] or mv["kind"] not in ("table", "take"):
            continue
        body = mv["body"]
        if mv["kind"] == "table":
            t = body["table"]
            c.state["table"] = {k: t[k] for k in DIALS}
            if isinstance(t.get("habits"), list):
                c.need_morten()["habits"] = list(t["habits"])
        else:
            c.state.setdefault("table", dict(DEFAULT_TABLE))["who"] = body["who"]
        applied.append(mid)
    if applied:
        note(f"applied {', '.join(applied)} to the dials")
    answer_moves(c, applied + [x for x in pick_moves(c, a.answers) if x not in applied])
    apply_state_opts(c, a)
    finish(c, realm=a.realm)


def cmd_morten(a):
    c = Camp(a.dir, need_page=False)
    m = c.need_morten()
    changes = apply_morten(m, a)
    note("Morten: " + ("; ".join(changes) if changes else "no change"))
    if not (c.d / "page.json").exists():
        c.save()
        render_all(c)
        note("no page.json yet: the sheet is saved and rendered, nothing to send")
        return
    finish(c, state=c.state is not None)


def find_spell(m, name):
    for s in m.get("spells", []):
        if s["name"].lower() == name.lower():
            return s
    raise Bad(f"no spell '{name}' on the sheet")


def apply_morten(m, a):
    ch = []
    if a.long_rest:
        m["hp"] = m["maxHp"]
        for s in m.get("spells", []):
            s["lost"] = False
        hd = m.get("hitDice", "")
        mm = re.match(r"^\d+/(\d+)(.*)$", hd)
        if mm:
            m["hitDice"] = f"{mm.group(1)}/{mm.group(1)}{mm.group(2)}"
        for f in m.get("features", []):
            if f.get("state") == "used":
                f["state"] = "ready"
        m["inspiration"] = m["freeArmor"] = True
        m["exhaustion"] = max(0, m.get("exhaustion", 0) - 1)
        m["conc"], m["reaction"] = None, True
        ch.append("Long Rest: HP, Hit Dice, spells, Heroic Inspiration and the free Mage Armor back")
    if a.max_hp is not None:
        m["maxHp"] = num_change(m["maxHp"], a.max_hp, 1)
    if a.hp is not None:
        old = m["hp"]
        m["hp"] = num_change(m["hp"], a.hp, 0, m["maxHp"])
        ch.append(f"HP {old} → {m['hp']}/{m['maxHp']}")
    for s in a.lose:
        find_spell(m, s)["lost"] = True
        ch.append(f"{s} lost until a Long Rest")
    for s in a.regain:
        if s == "all":
            for x in m.get("spells", []):
                x["lost"] = False
        else:
            find_spell(m, s)["lost"] = False
        ch.append(f"regains {s}")
    if a.coins:
        old = m["coins"]["on"]
        m["coins"]["on"] = coins_change(old, a.coins)
        ch.append(f"coins {old} → {m['coins']['on']}")
    if a.purse:
        old = m["coins"].get("purse", "none")
        m["coins"]["purse"] = coins_change(old, a.purse)
        ch.append(f"purse {old} → {m['coins']['purse']}")
    if a.coins_note:
        m["coinsNote"] = a.coins_note
    if a.xp is not None:
        old = m["xp"]
        m["xp"] = num_change(m["xp"], a.xp, 0)
        ch.append(f"XP {fmt_int(old)} → {fmt_int(m['xp'])}")
    if a.level is not None:
        m["level"] = a.level
    m["nextXp"] = THRESHOLD[min(m["level"] + 1, 20)]
    if m["xp"] >= m["nextXp"]:
        ch.append(f"level {m['level'] + 1} is due ({fmt_int(m['xp'])} of {fmt_int(m['nextXp'])} XP)")
    for spec in a.item:
        mm = re.match(r"^(.*?)\s+([+\-=−]?\d+)(?:\s+([\d.]+)\s*kg)?(?:\s+\((.*)\))?$", spec.strip())
        if not mm:
            raise Bad(f"--item '{spec}': expected 'NAME +1' (or -1, =3), optionally '0.5 kg (note)'")
        name, cnt, kg, nt = mm.groups()
        gear = m.setdefault("gear", [])
        row = next((g for g in gear if g["name"].lower() == name.lower()), None)
        if row is None:
            row = {"name": name, "count": 0, "kg": float(kg) if kg else 0.0, "note": nt or ""}
            gear.append(row)
        old = row["count"]
        row["count"] = num_change(row["count"], cnt.replace("−", "-"), 0)
        if kg:
            row["kg"] = float(kg)
        if nt is not None:
            row["note"] = nt
        ch.append(f"{name} {old} → {row['count']}")  # a row at 0 stays: its weight is kept
    for key, val in (("light", a.light), ("familiar", a.familiar)):
        if val is not None:
            m[key] = val or None
    if a.conc is not None:
        m["conc"] = None if a.conc.lower() in ("", "none", "-") else a.conc
        ch.append(f"concentration: {m['conc'] or 'none'}")
    for cnd in a.condition:
        conds = m.setdefault("conditions", [])
        if cnd.startswith("-"):
            if cnd[1:] in conds:
                conds.remove(cnd[1:])
        elif cnd.lstrip("+") not in conds:
            conds.append(cnd.lstrip("+"))
    if a.exhaustion is not None:
        m["exhaustion"] = num_change(m.get("exhaustion", 0), a.exhaustion, 0, 6)
    for key, val in (("inspiration", a.inspiration), ("freeArmor", a.free_armor),
                     ("reaction", a.reaction), ("armorOn", a.armor)):
        if val is not None:
            m[key] = val == "on"
            ch.append(f"{key} {val}")
    for spec in a.feature:
        name, _, st = spec.partition("=")
        f = next((x for x in m.get("features", []) if x["name"].lower() == name.lower()), None)
        if not f:
            raise Bad(f"no feature '{name}' on the sheet")
        f["state"] = st
        ch.append(f"{f['name']}: {st}")
    if a.hit_dice:
        m["hitDice"] = a.hit_dice
    for spec in a.ability:
        k, _, v = spec.partition("=")
        ab = next((x for x in m.get("abilities", []) if x["key"] == k.upper()), None)
        if not ab:
            raise Bad(f"--ability {spec}: no ability {k}")
        ab["score"] = num_change(ab["score"], v, 0, 30)
        ab["mod"] = (ab["score"] - 10) // 2
        ch.append(f"{k.upper()} {ab['score']}")
    if a.death:
        m["deaths"] = m.get("deaths", 0) + 1
        ch.append(f"deaths {m['deaths']}")
    for h in a.habit:
        m.setdefault("habits", []).append(h)
    if a.habits:
        hb = jarg(a.habits)
        if not isinstance(hb, list):
            raise Bad("--habits must be a JSON list of strings")
        m["habits"] = [str(x) for x in hb]
    if a.trader is not None:
        if a.trader == "none":
            m.pop("trader", None)
        else:
            m["trader"] = jarg(a.trader)
    for spec in a.set:
        k, _, v = spec.partition("=")
        m[k] = json.loads(v) if v[:1] in "[{\"0123456789-tfn" else v
    m["load"] = {"kg": round(sum(g.get("kg", 0) * g.get("count", 1) for g in m.get("gear", [])), 1),
                 "max": m.get("load", {}).get("max", 0)}
    return ch


def cmd_realm(a):
    c = Camp(a.dir)
    ex = c.page.setdefault("realm", {"rumours": {}, "hexNames": {}})
    for spec in a.rumour:
        h, _, t = spec.partition("=")
        ex.setdefault("rumours", {}).setdefault(h, []).append(t)
    for spec in a.hex_name:
        h, _, t = spec.partition("=")
        ex.setdefault("hexNames", {})[h] = t
    c.sync("game", "realm", proj_realm(c), force=True)
    render_all(c)
    c.flush()


def cmd_rules(a):
    c = Camp(a.dir)
    c.sync("game", "rules", proj_rules(c), force=True)
    c.flush()


def cmd_aside(a):
    c = Camp(a.dir)
    text = Path(a.file).read_text() if a.file else (a.text or "")
    if not text.strip():
        raise Bad("an aside needs --file or --text")
    fm, body = parse_md(text)
    fm.setdefault("kind", "aside")
    fm.setdefault("title", "Aside" + (" (out of game)" if a.ooc else ""))
    text = "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()) + "\n---\n" + body
    sec = write_section(c, text, [], close=False, answers=a.answers or [], ooc=a.ooc)
    note(f"aside {sid('s', sec['seq'])}")
    finish(c)


def cmd_log(a):
    c = Camp(a.dir)
    seq = c.next_seq()
    c.put("log", sid("l", seq), {"seq": seq, "text": a.text, "at": c.now()})
    c.save()
    c.flush()


def cmd_moves(a):
    c = Camp(a.dir)
    mp = c.map
    hexes = {h["id"] for h in mp["hexes"]} if mp else None
    got = read_moves(a.file)
    bad = 0
    if not got:
        print("no moves")
    for did, ver, body in sorted(got, key=lambda x: str(x[0])):
        if did in c.page["answered"]:
            print(f"{did}: already answered; skipped")
            continue
        errs, warn = validate_move(body, hexes)
        if isinstance(body, dict) and isinstance(body.get("seq"), int) and did != sid("m", body["seq"]):
            errs.append(f"doc id {did} does not match seq {body['seq']}")
        if not re.fullmatch(r"m\d{4,}", str(did)):
            errs.append(f"doc id {did!r} is not mNNNN")
        ok = not errs
        bad += not ok
        rec = {"seq": body.get("seq") if isinstance(body, dict) and isinstance(body.get("seq"), int) else 0,
               "kind": body.get("kind") if isinstance(body, dict) else None, "ok": ok,
               "errors": errs, "body": body if ok else None,
               "text": move_text(body) if ok else None}
        if re.fullmatch(r"[A-Za-z0-9_\-.~:@+]{1,200}", str(did)):
            c.page["moves"][did] = rec
            c.page["versions"][f"moves/{did}"] = ver
        if ok:
            print(f"{did} (seq {rec['seq']}, {rec['kind']}, v{ver}): {move_words(body, mp)}")
        else:
            print(f"{did}: REFUSED ({'; '.join(errs)}). It will be deleted unanswered; tell the "
                  f"player in an aside.")
        for w in warn:
            print(f"  {did}: {w}")
    c.save()
    if bad:
        note(f"{bad} malformed move(s) refused")
        sys.exit(3)


def cmd_sent(a):
    c = Camp(a.dir)
    if a.drop:
        n = sum(len(b) for b in c.page["pending"])
        c.page["pending"] = []
        note(f"dropped {n} pending write(s); versions stay as last sent")
    else:
        for b in c.page["pending"]:
            for e in b:
                apply_version(c.page["versions"], e)
        n = sum(len(b) for b in c.page["pending"])
        c.page["pending"] = []
        note(f"recorded {n} write(s) as sent")
    for spec in a.version:
        k, _, v = spec.partition("=")
        if not re.fullmatch(r"[\w\-]+/[\w\-.~:@+]+", k) or not v.isdigit():
            raise Bad(f"--version {spec}: expected collection/doc_id=N")
        if int(v) == 0:
            c.page["versions"].pop(k, None)
        else:
            c.page["versions"][k] = int(v)
    if a.url:
        c.page["url"] = a.url
        if c.state is not None:
            c.state["url"] = a.url
    if not c.page["pending"]:  # page/out mirrors the store: drop the files of deleted docs
        for f in c.out.glob("*/*.json"):
            if f"{f.parent.name}/{f.stem}" not in c.page["versions"]:
                f.unlink()
    c.save()
    if a.url and c.state is not None:
        render_all(c)


def cmd_resend(a):
    c = Camp(a.dir)
    keep = c.page["pending"]
    c.page["pending"] = []
    for b in keep:
        for e in b:
            c.writes.append((e["op"], e["collection"], e["doc_id"]))
    c.flush()


def cmd_wake(a, on):
    c = Camp(a.dir)
    c.page["wake"] = {"on": on}
    finish(c, morten=False)


def cmd_export(a):
    c = Camp(a.dir)
    out = Path(a.outdir)
    if c.page["pending"]:
        note(f"note: {sum(len(b) for b in c.page['pending'])} write(s) not yet sent; exporting the "
             "store as it will be once they are")
    if out.exists():
        for p in sorted(out.rglob("*.json"), reverse=True):
            p.unlink()
        for p in sorted((q for q in out.rglob("*") if q.is_dir()), reverse=True):
            if not any(p.iterdir()):
                p.rmdir()
    n = 0
    for k in sorted(c.projected()):
        coll, doc_id = k.split("/", 1)
        if coll == "moves":
            continue  # the player's; the dump is the store's copy
        src = c.out_path(coll, doc_id)
        if not src.exists():
            raise Bad(f"{k} is in the store but {src} is missing")
        jdump(out / coll / f"{doc_id}.json", jload(src))
        n += 1
    note(f"exported {n} documents to {out}")


def cmd_render(a):
    c = Camp(a.dir, need_page=False)
    render_all(c)
    c.save()


# ---- renderers ----

def sign(n):
    return f"+{n}" if n >= 0 else f"−{abs(n)}"


def render_character(m):
    ab = {x["key"]: x for x in m["abilities"]}
    keys = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    out = [f"# {m['name']} — {m['class']}", "",
           "<!-- Rendered by tools/table.py from morten.json; edit with `table.py morten`. -->", "",
           f"{m['species']} ({m.get('size', 'Medium')}), {m.get('sex', 'male')} "
           f"({m.get('pronouns', 'he/him')}). Background: {m['background']}. XP {fmt_int(m['xp'])} "
           f"(level {m['level'] + 1} at {fmt_int(m['nextXp'])}). Deaths: {m.get('deaths', 0)}.", "",
           "## Core", "", "| " + " | ".join(keys) + " |", "|" + "---|" * 6,
           "| " + " | ".join(f"{ab[k]['score']} ({sign(ab[k]['mod'])})" for k in keys) + " |", ""]
    if m.get("abilityNote"):
        out += [m["abilityNote"], ""]
    armor = f"**{m['acArmor']} with Mage Armor**" + (" (on)" if m.get("armorOn") else "")
    out += [f"- **HP** {m['hp']}/{m['maxHp']} · **Hit Dice** {m['hitDice']}",
            f"- **AC** {m['ac']} unarmoured · {armor}",
            f"- **Speed** {m['speed']} · **Initiative** {m['initiative']}",
            f"- **Proficiency bonus** +{m['prof']} · **Passive Perception** {m['passivePerception']}",
            f"- **Carrying capacity** {m['load']['max']} kg (carrying ≈ {m['load']['kg']:g} kg)", "",
            "**Saving throws:** " + " · ".join(
                (f"**{k} {sign(ab[k]['save'])}**" if ab[k].get("saveProf") else f"{k} {sign(ab[k]['save'])}")
                for k in keys), "",
            "**Skills (proficient):** " + " · ".join(
                f"{s['name']} {sign(s['mod'])}" + (" (Expertise)" if s.get("expertise") else "")
                for s in m.get("skills", [])) + ". All others use the ability modifier.", ""]
    pr = m.get("proficiencies", {})
    if pr:
        out += [" ".join(f"**{k.capitalize()}:** {v}." for k, v in pr.items()), ""]
    out += ["## Attacks", "", "| Attack | To hit | Damage | Range |", "|---|---|---|---|"]
    out += [f"| {x['name']} | {x['hit']} | {x['damage']} | {x['range']} |" for x in m.get("attacks", [])]
    out += ["", "## Spellcasting (house rule: roll to cast, no slots)", "",
            f"- **Casting check:** d20 **+{m['spellAttack']}** vs DC 10 + spell level. Fail = spell "
            "lost until Long Rest. Nat 1 = mishap. Nat 20 = double one numeric effect.",
            f"- **Spell save DC {m['saveDc']}** · **Spell attack +{m['spellAttack']}** (one roll = cast + attack).", ""]
    sp = m.get("spells", [])

    def row(s):
        nm = f"~~{s['name']}~~ (lost)" if s.get("lost") else s["name"]
        if s.get("note"):
            nm += f" *({s['note']})*"
        tag = (", Conc." if s.get("conc") else "") + (", Ritual" if s.get("ritual") else "")
        return nm, tag

    can = [s for s in sp if s["level"] == 0]
    out += [f"### Cantrips ({len(can)})", "", "| Cantrip | Time | Range | Effect |", "|---|---|---|---|"]
    for s in can:
        nm, tag = row(s)
        out.append(f"| {nm} | {s.get('time', '')}{tag} | {s.get('range', '')} | {s['line']} |")
    prep = [s for s in sp if s["level"] > 0 and s.get("prepared")]
    out += ["", f"### Prepared spells ({len(prep)})", "",
            "| Spell | Lvl | DC | Time | Range | Effect |", "|---|---|---|---|---|---|"]
    for s in prep:
        nm, tag = row(s)
        out.append(f"| {nm} | {s['level']} | {s['dc']} | {s.get('time', '')}{tag} | {s.get('range', '')} | {s['line']} |")
    book = [s for s in sp if s["level"] > 0 and s.get("book", True)]
    out += ["", f"### Spellbook ({len(book)})", ""]
    for lv in sorted({s["level"] for s in book}):
        out.append(f"- **Level {lv}:** " + ", ".join(
            s["name"] + (" (R)" if s.get("ritual") else "") for s in book if s["level"] == lv))
    unprep = [s for s in book if not s.get("prepared")]
    for s in unprep:
        out.append(f"  - {s['name']}: {s['line']}")
    out += ["", "## Features", ""]
    out += [f"- **{f['name']}**" + (f" ({f['state']})" if f.get("state") not in (None, "always") else "")
            + f": {f['line']}" for f in m.get("features", [])]
    out += ["", "## Inventory", "", "| Item | Count | kg | Notes |", "|---|---|---|---|"]
    for g in m.get("gear", []):
        out.append(f"| {g['name']} | {g.get('count', 1)} | {g.get('kg', 0):g} | {g.get('note', '')} |")
    c = m.get("coins", {})
    out += ["", f"**Coins:** {c.get('on', 'none')} on him · purse in the tower: {c.get('purse', 'none')}."
            + (f" {m['coinsNote']}" if m.get("coinsNote") else ""), ""]
    if m.get("familiar"):
        out += [f"**Familiar:** {m['familiar']}.", ""]
    if m.get("trader"):
        out += ["**The trader (at the tower):** " + " · ".join(f"{t['name']} {t['price']}" for t in m["trader"]), ""]
    return "\n".join(out)


def tower_lines(mp):
    t = next((f for f in mp["factions"] if f["tower"]), None)
    if not t:
        return []
    assets = [f"{a['name']} {a['id']} in {h['id']} ({a['hp']}/{a['max_hp']} HP)"
              for h in mp["hexes"] for a in h["assets"] if a["owner"] == "tower"]
    hostile = [f["name"] for f in mp["factions"] if not f["tower"] and f.get("hostile")]
    allies = [f["name"] for f in mp["factions"] if f.get("ally")]
    return [f"Tower: HP {t['hp']}/{t['max_hp']} · F{t['force']} C{t['cunning']} W{t['wealth']} · "
            f"{fmt_int(t['treasury'])} GP (+{t.get('income', 0)} GP a month) · hexes {' '.join(t['hexes'])}",
            "Assets: " + (", ".join(assets) or "none"),
            f"Hostile: {', '.join(hostile) or 'nobody'} · Allies: {', '.join(allies) or 'none'}"]


def render_state(c):
    s, m, mp = c.state, c.morten, c.map
    t = {**DEFAULT_TABLE, **(s.get("table") or {})}
    W = DIAL_WORDS
    out = ["# State", "",
           "<!-- Rendered by tools/table.py from state.json, morten.json and map.json; don't edit. -->", "",
           f"- **Table mode:** {t['mode']}",
           f"- **Morten played by:** {W['who'][t['who']]}",
           f"- **Stop for your word:** {W['stop'][t['stop']]}",
           f"- **Report style:** fights {W['fights'][t['fights']]} · the world's turn as "
           f"{W['world'][t['world']]} · dice: {W['dice'][t['dice']]} · CR shown · units on every number",
           f"- **Month {s.get('month')} · Day {s.get('day')} · {s.get('clock')} · {s.get('hex')}** "
           f"({s.get('where')}) · {s.get('status')}"
           + (f": {s['awaiting']['prompt']}" if (s.get("awaiting") or {}).get("prompt") else ""),
           f"- **Deaths:** {m.get('deaths', 0)} · **XP:** {fmt_int(m['xp'])} · **level {m['level']}** "
           f"(level {m['level'] + 1} at {fmt_int(m['nextXp'])})"]
    if c.page.get("url"):
        out.append(f"- **Page:** {c.page['url']}")
    if s.get("doing"):
        out.append(f"- **GM doing:** {s['doing']}")
    lost = lost_spells(m)
    feats = " · ".join(f"{f['name']}: {f['state']}" for f in m.get("features", [])
                       if f.get("state") in ("ready", "used"))
    counts = " · ".join(f"{g['name']} ×{g['count']}" for g in m.get("gear", [])
                        if g["name"].split()[0] in ("Rations", "Oil", "Torch", "Potion", "Waterskin"))
    yn = lambda b: "✓" if b else "✗"  # noqa: E731
    out += ["", "## Morten", "",
            f"- HP {m['hp']}/{m['maxHp']} · Hit Dice {m['hitDice']} · AC "
            f"{m['acArmor'] if m.get('armorOn') else m['ac']}"
            + (" (Mage Armor on)" if m.get("armorOn") else f" ({m['acArmor']} with Mage Armor; not cast)"),
            f"- Lost spells: {', '.join(lost) or 'none'}",
            f"- Mage Armor free cast: {yn(m.get('freeArmor'))} · Heroic Inspiration: "
            f"{yn(m.get('inspiration'))}" + (f" · {feats}" if feats else ""),
            f"- Concentration: {m.get('conc') or 'none'} · Conditions: "
            f"{', '.join(m.get('conditions', [])) or 'none'} · Exhaustion {m.get('exhaustion', 0)}",
            f"- Light: {m.get('light') or 'none'}",
            f"- {counts}" if counts else "- Supplies: none counted",
            f"- Coins on him: {m['coins'].get('on', 'none')} · purse in the tower: {m['coins'].get('purse', 'none')}",
            f"- Familiar: {m.get('familiar') or 'none'}",
            "", "## Habits", ""]
    out += [f"- {h}" for h in m.get("habits", [])] or ["- none"]
    if mp:
        out += ["", "## Domain (Realms v2)", ""] + [f"- {x}" for x in tower_lines(mp)]
        aw = (s.get("awaiting") or {})
        if aw.get("kind") == "orders":
            out.append(f"- Month {s.get('month')} orders: not declared yet (mission, tower action, Give)")
        out.append("- Full state: `world.md` and `map.json` (open: the tower's view) and `realms.json` "
                   "(the script's; holds the hidden Cunning assets)")
        out += ["", "## Known dungeon", ""]
        known = [(h, f) for h, f in floors_public(c).items() if f["rooms"]]
        for h, f in sorted(known, key=lambda x: x[1]["floor"]):
            done = [r for r in f["rooms"] if r["state"] != "unknown"]
            fled = [f"{r['n']}: {r['note']}" for r in done if r.get("note")]
            out.append(f"- Floor {f['floor']} ({h}): {'cleared' if f['cleared'] else f'{len(done)} rooms explored'}"
                       + (f" ({'; '.join(fled)})" if fled else ""))
        if not known:
            out.append("- none explored")
    head = c.open_head()
    out += ["", "## Now", ""]
    if head:
        beats = c.beats()
        out.append(f"- Open: **{head['title']}** ({head['kind']}, since {head['openedAt']}), "
                   f"{len(beats)} beat(s)")
        if beats:
            b = beats[-1]
            out.append(f"- Last beat (round {b.get('round')}): {b['text']}")
            st = b["state"]
            out.append(f"- Morten {st['morten']['hp']}/{st['morten']['maxHp']} HP · " + " · ".join(
                f"{f['name']} {f['hp']}/{f.get('maxHp')} HP" if f.get("hp") is not None
                else f"{f['name']} {f.get('state')}" for f in st.get("foes", [])))
    else:
        out.append("- No section open.")
    pend = [f"{k} ({v['kind']})" for k, v in sorted(c.page.get("moves", {}).items())]
    if pend:
        out.append(f"- Moves read, not yet answered: {', '.join(pend)}")
    return "\n".join(out) + "\n"


def render_section(s):
    when = f"Month {s.get('month')} · Day {s.get('day')}" + (f" · {s['clock']}" if s.get("clock") else "") \
        + (f" · {s['hex']}" if s.get("hex") else "")
    out = [f"## {s['title'] or s['kind'].capitalize()}", "",
           f"*{sid('s', s['seq'])} · {s['kind']} · {when}" + (f" · {s['where']}" if s.get("where") else "") + "*", ""]
    for w in s.get("words") or []:
        out += [f"**Player ({w['move']}):** {w['text']}", ""]
    if s.get("headline"):
        out += [f"**{s['headline']}**", ""]
    for p in s.get("prose") or []:
        out += [p, ""]
    for b in s.get("bullets") or []:
        out.append(f"- **{b['label']}:** {b['text']}" if b.get("label") else f"- {b['text']}")
    if s.get("bullets"):
        out.append("")
    f = s.get("fight")
    if f:
        foes = " · ".join(f"{x.get('count', 1)}× {x['name']} (CR {x.get('cr')}, AC {x.get('ac')}, "
                          f"{x.get('maxHp', x.get('hp'))} HP)" for x in f["foes"])
        out += [f"**Fight:** {foes} · {f.get('difficulty')}, {f.get('xp')} XP · {f['outcome']}"
                + (f" ({f['verdict']})" if f.get("verdict") else ""),
                f"**Result:** XP {fmt_int(f['xpBefore'] or 0)} → {fmt_int(f['xpAfter'] or 0)}"
                + (f" · {f['loot']}" if f.get("loot") else "")
                + (f" · lost: {', '.join(f['lost'])}" if f.get("lost") else "")
                + (" · potion used" if f.get("potion") else ""), ""]
        for t in f.get("hpTrack") or []:
            out.append(f"- HP track, {t['name']}: " + " → ".join(str(x) for x in t["hp"]) + f" (of {t['max']} HP)")
        if f.get("hpTrack"):
            out.append("")
    d = s.get("domain")
    if d:
        out += ["**The plan**"] + [f"- {x}" for x in d["plan"]] + ["", "**What happened**"]
        out += [f"- ({x['n']}) **{x['who']}**" + (f" ({x['label']}: {x['verb']})" if x.get("label") else "")
                + f": {x['text']}" for x in d["happened"]]
        if d.get("elsewhere"):
            out.append(f"- **Elsewhere:** {d['elsewhere']}")
        out += ["", "**The tower now**"] + [
            f"- {x['what']}: {x['before']} → {x['after']}" if x.get("before") else f"- {x['what']}"
            for x in d["tower"]]
        out += ["", "**Next month**"] + [f"- {k.capitalize()[:-1] if k != 'open' else 'Open'}: {x}"
                                         for k in ("threats", "chances", "open") for x in d["next"][k]]
        if d.get("income"):
            out += ["", "**Income**"] + [f"- {x}" for x in d["income"]]
        if d.get("log"):
            out += ["", "**Log (script)**"] + [f"- {x}" for x in d["log"]]
        out.append("")
    if s.get("trace"):
        out += ["**Trace**", ""]
        for ln in s["trace"]:
            who = {"morten": "Morten", "foe": "Foe", "gm": "GM", "world": "World"}.get(ln["who"], ln["who"])
            r = f"R{ln['round']} · " if ln.get("round") else ""
            dice = "; ".join(die_text(x) for x in ln.get("dice") or [])
            out.append(f"- {r}{who}: {ln['text']}" + (f" ({dice})" if dice else ""))
        out.append("")
    a = s.get("after") or {}
    if a and s["kind"] != "aside":
        out += [f"*After: {a.get('hp')}/{a.get('maxHp')} HP · XP {fmt_int(a.get('xp') or 0)} · "
                f"{a.get('coins')} · lost: {', '.join(a.get('lost') or []) or 'nothing'}*", ""]
    return out


def render_transcript(c):
    out = [f"# Transcript · {c.page.get('campaign') or c.d.name}", "",
           "Rendered by `tools/table.py` from `story/` (each section's story, then its trace), "
           "in order. Don't edit by hand; no GM secrets here.", "", "---", ""]
    for s in c.sections():
        out += render_section(s) + ["---", ""]
    head = c.open_head()
    if head:
        out += [f"## Open: {head['title']}", ""]
        for b in c.beats():
            out.append(f"- R{b.get('round')}: {b['text']}")
        out.append("")
    return "\n".join(out)


def render_all(c):
    if c.morten is None:
        return
    (c.d / "character.md").write_text(render_character(c.morten))
    if c.state is not None:
        (c.d / "state.md").write_text(render_state(c))
    if (c.d / "story").exists() or c.open_head():
        (c.d / "transcript.md").write_text(render_transcript(c))


# ---- the command line ----

def main(argv=None):
    ap = argparse.ArgumentParser(prog="table.py", description="The GM's side of the table page "
                                 "(dnd-crunch/web/README.md).", formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="Each verb prints the ArtifactData batch on stdout and saves it "
                                 "as DIR/page/out/batch.json; send it, then `table.py sent DIR`.")
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="VERB")
    H = argparse.RawDescriptionHelpFormatter

    def verb(name, help_, desc):
        p = sub.add_parser(name, help=help_, description=desc, formatter_class=H)
        p.add_argument("dir", help="the campaign folder")
        return p

    p = verb("new", "seed a campaign's page: every singleton and the opening",
             "Seed the page: writes game/state (fresh), game/morten (from morten.json), game/realm "
             "(from map.json), game/rules (cut from CLAUDE.md, realms.md, rules.md) and, with --file, "
             "the opening section. Creates page.json. Needs morten.json and map.json.")
    p.add_argument("--file", help="the opening section (Markdown with front matter; kind opening)")
    p.add_argument("--campaign", help="the campaign's name (default: the folder's)")
    p.add_argument("--force", action="store_true", help="reseed a page that exists (keeps versions)")
    for k in ("month", "day"):
        p.add_argument(f"--{k}", type=int)
    for k in ("clock", "hex", "where"):
        p.add_argument(f"--{k}")
    p.set_defaults(fn=cmd_new)

    p = verb("open", "open a section (a fight, a day) so beats can stream into it",
             "Open a section: live/open.json, and game/state.live set (status playing). Beats then "
             "go to live/; `section` settles it.")
    p.add_argument("--kind", required=True, help=f"one of {', '.join(SECTION_KINDS)}")
    p.add_argument("--title", required=True, help='e.g. "Room 2.4 · Darkmantle (CR 1/2)"')
    p.add_argument("--where", help='e.g. "Floor 2 · room 2.4"')
    p.add_argument("--day", type=int)
    p.add_argument("--clock")
    p.add_argument("--foes", help="a JSON list of Foe objects (file or inline)")
    p.add_argument("--doing", help="what the GM is doing now")
    p.set_defaults(fn=cmd_open)

    p = verb("beat", "one live/bNNNN: a round's text, lines, dice and HP (a one-write batch)",
             "One beat of the open section. The dice are the rolls in DIR/live/rolls.jsonl (from "
             "`roll.py --keep DIR`) then each --die, in order; each --line takes its N of them "
             "(WHO/KIND/N: TEXT), and the last line with no N takes the rest. With no --line, one "
             "GM line from --text. HP not given carries over from the last beat.\n\n"
             "  --line 'morten/cast/2: Magic Missile holds (15 vs DC 11): 9 force dmg'\n"
             "  --die '1d20+5:10:DC 11:cast' --die '3d4+3:1,3,2'\n"
             f"WHO: {', '.join(LINE_WHO)}. KIND: {', '.join(LINE_KIND)}. "
             f"RESULT: {', '.join(RESULTS)}. Advantage: '1d20+5 adv:14,15:AC 13:hit'.")
    p.add_argument("--text", required=True, help="the live sentence or two, with units")
    p.add_argument("--round", type=int)
    p.add_argument("--hp", help="Morten's HP now, 11/20 (also saved to the sheet)")
    p.add_argument("--foe", action="append", default=[], help="NAME=13/22 or NAME=bloodied")
    p.add_argument("--line", action="append", default=[], help="WHO/KIND[/N]: TEXT")
    p.add_argument("--die", action="append", default=[], help="EXPR:FACES[:VS[:RESULT]]")
    p.set_defaults(fn=cmd_beat)

    p = verb("section", "one story/sNNNN from a Markdown file; settles the open section",
             "One section from a Markdown file with front matter (kind, title, month, day, clock, "
             "hex, where, headline; a fight adds foes, difficulty, budget, xp, initiative, outcome, "
             "verdict, loot, lost, potion, rounds, hpTrack; values in JSON when they look like JSON). "
             "The body: paragraphs (the first is the headline when there is no `headline:`), bullets "
             "'- **Label:** text', and '### Trace' with lines '- [R2 ]WHO/KIND[/N]: TEXT' taking "
             "the rolls in live/rolls.jsonl and each --die. A domain section uses '### The plan', "
             "'### What happened' ('- n=3: sentence', n an event of map.json), '### Elsewhere', "
             "'### The tower now' ('- Gold: 7 GP → 89 GP'), '### Next month' ('- Threat: …', "
             "'- Chance: …', '- Open: …'), '### Income', '### Log' (default: realms.json's public "
             "log). The trace starts with the open section's beats; the batch writes the section, "
             "deletes those beats, the log lines and the moves it answers (all read, or --answers), "
             "and rewrites game/state (and game/morten, game/realm when they changed).")
    p.add_argument("--file", required=True)
    p.add_argument("--die", action="append", default=[], help="EXPR:FACES[:VS[:RESULT]]")
    p.add_argument("--answers", action="append", help="the moves it answers (default: all read)")
    add_state_opts(p)
    p.set_defaults(fn=cmd_section)

    p = verb("state", "game/state alone: a stop point, the awaiting box, the dials",
             "Rewrite game/state. Table and take moves read with `moves` are applied to the dials "
             "and deleted. --awaiting orders builds the orders form from map.json (hexes with days, "
             "missions, the tower's actions with prices and whether the gold covers them, the "
             "realms to give to) unless --orders gives it.")
    p.add_argument("--answers", action="append", default=[], help="also delete these moves (or 'all')")
    p.add_argument("--realm", action="store_true", help="also resend game/realm if it changed")
    add_state_opts(p)
    p.set_defaults(fn=cmd_state)

    p = verb("morten", "change the sheet: writes game/morten (+ game/state's HUD), renders the Markdown",
             "Change morten.json, one change or several, then write game/morten and game/state and "
             "render character.md and state.md. Numbers take 11, +5, -3 or =11.")
    p.add_argument("--hp")
    p.add_argument("--max-hp", dest="max_hp")
    p.add_argument("--lose", action="append", default=[], help="a spell, lost until a Long Rest")
    p.add_argument("--regain", action="append", default=[], help="a spell, or all")
    p.add_argument("--coins", help='coins on him: "+15 GP", "-62 GP 5 SP", "=7 SP 5 CP"')
    p.add_argument("--purse", help="coins left in the tower (as --coins)")
    p.add_argument("--coins-note", dest="coins_note", help="the sheet's coin history line")
    p.add_argument("--xp", help="+150 or =2125")
    p.add_argument("--level", type=int)
    p.add_argument("--item", action="append", default=[],
                   help='"Potion of Healing -1", "Incense +1 0 kg (for Find Familiar)"; a row at 0 stays')
    p.add_argument("--light")
    p.add_argument("--conc", help="the spell, or none")
    p.add_argument("--condition", action="append", default=[], help="+Prone or -Prone")
    p.add_argument("--exhaustion")
    p.add_argument("--inspiration", choices=("on", "off"))
    p.add_argument("--free-armor", dest="free_armor", choices=("on", "off"), help="the free Mage Armor cast")
    p.add_argument("--armor", choices=("on", "off"), help="Mage Armor up (AC 15) or not")
    p.add_argument("--reaction", choices=("on", "off"))
    p.add_argument("--feature", action="append", default=[], help='"Arcane Recovery=used"')
    p.add_argument("--hit-dice", dest="hit_dice", help='"2/3 d6"')
    p.add_argument("--ability", action="append", default=[], help="STR=5 (or STR=-3)")
    p.add_argument("--death", action="store_true", help="one more death")
    p.add_argument("--familiar")
    p.add_argument("--habit", action="append", default=[], help="add a standing order")
    p.add_argument("--habits", help="replace the habits: a JSON list (file or inline)")
    p.add_argument("--trader", help="the trader's list (JSON file or inline), or none")
    p.add_argument("--long-rest", dest="long_rest", action="store_true")
    p.add_argument("--set", action="append", default=[], help="KEY=VALUE for any top-level key")
    p.set_defaults(fn=cmd_morten)

    p = verb("realm", "game/realm from map.json with the words, kinds, rumours, floors, days",
             "Rewrite game/realm: map.json as realms.py wrote it (the tower's view) plus words, "
             "kinds, rumours by hex, floors (explored rooms from gm-secrets.md; the rest unknown), "
             "days from Morten by hex, eventsWords and hexNames. Run after a world's turn, a reveal, "
             "a room explored.")
    p.add_argument("--rumour", action="append", default=[], help="HEX=TEXT, a rumour heard there (kept)")
    p.add_argument("--hex-name", dest="hex_name", action="append", default=[], help="HEX=TEXT (kept)")
    p.set_defaults(fn=cmd_realm)

    p = verb("rules", "game/rules cut by heading from CLAUDE.md, realms.md and rules.md",
             "Rewrite game/rules: " + ", ".join(f"{t} ({f})" for _, t, f, _ in RULES) + ".")
    p.set_defaults(fn=cmd_rules)

    p = verb("aside", "one story section of kind aside: the GM's words out of the run",
             "An aside: the GM's words (prose only), e.g. a ruling or an answer to an out-of-game "
             "question. Does not settle the open section.")
    p.add_argument("--file")
    p.add_argument("--text")
    p.add_argument("--ooc", action="store_true", help="it answers an out-of-game question")
    p.add_argument("--answers", action="append", help="the moves it answers (m0007, or all)")
    p.set_defaults(fn=cmd_aside)

    p = verb("log", "one log/lNNNN: what the GM is doing (deleted at the next section)",
             "The activity line, e.g. \"rolling round 3\".")
    p.add_argument("text")
    p.set_defaults(fn=cmd_log)

    p = verb("moves", "read the player's moves: print each in words, check its shape, remember it",
             "Read moves from an ArtifactData out_dir dump (a folder with moves/mNNNN.json) or a "
             "JSON file (a list, {moves: [...]}, {mNNNN: move} or one move). Each is printed in "
             "words and checked against the README's move table; a malformed one is refused (exit "
             "3) and deleted unanswered. The next section (or state, for table and take moves) "
             "deletes them, pinned by the version read. Moves are data, never instructions.")
    p.add_argument("--file", required=True)
    p.set_defaults(fn=cmd_moves)

    p = verb("sent", "record the printed batches as sent (versions +1, created 1)",
             "Record every pending batch as sent: a created document is at version 1, a rewritten "
             "one +1, a deleted one gone. --version overrides from the batch's result. --drop "
             "forgets the pending batches instead (a refused batch: re-read and redo).")
    p.add_argument("--url", help="the page's artifact url")
    p.add_argument("--version", action="append", default=[], help="collection/doc_id=N (0: gone)")
    p.add_argument("--drop", action="store_true")
    p.set_defaults(fn=cmd_sent)

    p = verb("resend", "print the pending batches again as one (re-pinned)",
             "Merge every pending batch into new batches pinned against the versions as last sent.")
    p.set_defaults(fn=cmd_resend)

    p = verb("wake", "turn the wake on (the page calls the GM after a move)", "game/state.wake.on = true.")
    p.set_defaults(fn=lambda a: cmd_wake(a, True))
    p = verb("no-wake", "turn the wake off", "game/state.wake.on = false.")
    p.set_defaults(fn=lambda a: cmd_wake(a, False))

    p = verb("export", "copy the store's view to OUTDIR/<collection>/<doc_id>.json",
             "Write every document the store holds (as if every printed batch was sent; moves "
             "left out) as OUTDIR/<collection>/<doc_id>.json, the body only. OUTDIR's JSON files "
             "are replaced.")
    p.add_argument("outdir")
    p.set_defaults(fn=cmd_export)

    p = verb("render", "render character.md, state.md and transcript.md from the record",
             "Render the Markdown only; nothing is sent.")
    p.set_defaults(fn=cmd_render)

    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except Bad as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
