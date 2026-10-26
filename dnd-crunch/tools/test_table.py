#!/usr/bin/env python3
"""Tests for table.py, check_table.py and roll.py --keep (stdlib unittest).

Usage:
  python3 dnd-crunch/tools/test_table.py          # all
  python3 dnd-crunch/tools/test_table.py -k moves # some

Each test plays in a scratch copy of the realms3 campaign files (realms3 is not touched)
with the fixture's starting sheet; the secrecy tests also read the built fixture campaign
(dnd-crunch/web/dev/fixture-campaign, rebuilt by its play.sh).
"""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_table  # noqa: E402
import table as T  # noqa: E402

GAME = HERE.parent
REALMS3 = GAME / "campaigns" / "realms3"
FIXTURE = GAME / "web" / "dev" / "fixture-campaign"
FIXTURE3 = GAME / "web" / "dev" / "fixture-campaign-v3"
START = FIXTURE / "play" / "morten-start.json"
FOES = json.loads((FIXTURE / "play" / "foes.json").read_text())

# ---- the README's shapes: key → type (a tuple: any of them; None allowed where listed) ----
S, I, B, L, D, N = str, int, bool, list, dict, type(None)
STATE = {"v": I, "campaign": S, "status": S, "lastSeq": I, "lastMove": I, "month": I, "day": I,
         "clock": S, "hex": S, "where": S, "level": I, "xp": I, "deaths": I, "hud": D, "table": D,
         "awaiting": D, "live": (D, N), "latest": (S, N), "lastFight": (S, N), "doing": (S, N),
         "checkIn": (S, N), "wake": D, "url": (S, N)}
HUD = {"hp": I, "maxHp": I, "ac": I, "acArmor": I, "light": (S, N), "conc": (S, N),
       "conditions": L, "exhaustion": I, "reaction": B, "inspiration": B, "freeArmor": B,
       "coins": S, "lost": L}
TABLE = {"who": S, "stop": S, "fights": S, "world": S, "dice": S, "mode": S, "habits": L}
AWAIT = {"kind": S, "prompt": S, "orders": (D, N), "fight": (D, N), "turn": (D, N)}
MORTEN = {"v": I, "name": S, "class": S, "species": S, "background": S, "hp": I, "maxHp": I,
          "hitDice": S, "ac": I, "acArmor": I, "speed": S, "initiative": S, "passivePerception": I,
          "prof": I, "spellAttack": I, "saveDc": I, "abilities": L, "skills": L, "attacks": L,
          "spells": L, "features": L, "light": (S, N), "conc": (S, N), "conditions": L,
          "exhaustion": I, "inspiration": B, "freeArmor": B, "gear": L, "load": D, "coins": D,
          "xp": I, "nextXp": I, "level": I, "deaths": I, "familiar": (S, N), "habits": L}
SPELL = {"name": S, "level": I, "dc": I, "lost": B, "conc": B, "ritual": B, "line": S, "prepared": B}
REALM = {"v": I, "hexes": L, "rivers": L, "factions": L, "morten": D, "events": L, "report": D,
         "layout": D, "month": I, "campaign": S, "words": D, "kinds": D, "rumours": D,
         "floors": D, "days": D, "eventsWords": L, "hexNames": D}
KIND = {"glyph": S, "type": S, "tier": I, "what": S, "cost": I, "hp": I, "hits": S,
        "counter": S, "upkeep": I, "special": S}
KIND3 = {"glyph": S, "type": S, "what": S, "tierWords": S, "fight": S, "effect": S}
ROOM = {"n": S, "monster": (S, N), "cr": (S, N), "state": S}
SECTION = {"v": I, "seq": I, "kind": S, "month": I, "day": I, "clock": (S, N), "hex": (S, N),
           "where": (S, N), "title": S, "headline": S, "prose": L, "bullets": L, "trace": L,
           "answered": L, "after": D, "fight": (D, N), "domain": (D, N), "words": L}
LINE = {"text": S, "who": S, "kind": S, "dice": L}
DIE = {"expr": S, "faces": L, "kept": L, "mod": I, "total": I, "vs": (S, N), "result": (S, N),
       "nat": (I, N)}
FIGHT = {"foes": L, "difficulty": (S, N), "budget": (I, N), "xp": (I, N), "initiative": L,
         "rounds": I, "outcome": S, "verdict": (S, N), "hpTrack": L, "loot": (S, N), "lost": L,
         "potion": B, "xpBefore": (I, N), "xpAfter": (I, N)}
FOE = {"name": S, "cr": S, "ac": I, "hp": (I, N), "maxHp": I, "speed": S, "attacks": L,
       "notes": S, "count": I}
DOMAIN = {"plan": L, "happened": L, "elsewhere": S, "tower": L, "next": D, "income": L, "log": L}
HAPPENED = {"n": I, "who": S, "label": (S, N), "verb": (S, N), "text": S, "from": (S, N), "to": (S, N)}
BEAT = {"v": I, "seq": I, "section": D, "round": (I, N), "text": S, "lines": L, "state": D, "at": S}
LOG = {"v": I, "seq": I, "text": S, "at": S}


class Case(unittest.TestCase):
    def shape(self, doc, spec, where=""):
        for k, t in spec.items():
            self.assertIn(k, doc, f"{where}: missing {k}")
            if t is I:
                self.assertTrue(isinstance(doc[k], int) and not isinstance(doc[k], bool),
                                f"{where}.{k} = {doc[k]!r} is not an int")
            else:
                self.assertIsInstance(doc[k], t, f"{where}.{k} = {doc[k]!r}")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="table-test-"))
        self.d = self.tmp / "camp"
        self.d.mkdir()
        for f in ("map.json", "realms.json", "gm-secrets.md", "rules.md", "world.md"):
            shutil.copy(REALMS3 / f, self.d / f)
        shutil.copy(START, self.d / "morten.json")
        os.environ["TABLE_NOW"] = "2026-10-25T09:00:00Z"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def t(self, *args):
        """Run a verb in-process; → (stdout, stderr). A Bad exits 2 (SystemExit)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            T.main([str(a) for a in args])
        return out.getvalue(), err.getvalue()

    def batches(self, out):
        """The batch JSON objects printed on stdout."""
        dec, i, found = json.JSONDecoder(), 0, []
        while True:
            j = out.find("{", i)
            if j < 0:
                return found
            obj, i = dec.raw_decode(out, j)
            found.append(obj)

    def doc(self, coll, doc_id):
        return json.loads((self.d / "page" / "out" / coll / f"{doc_id}.json").read_text())

    def md(self, name, text):
        p = self.tmp / name
        p.write_text(text)
        return p

    def new(self):
        self.t("new", self.d, "--month", 2, "--day", 1, "--hex", "B5", "--where", "the tower (B5)")
        self.t("sent", self.d)

    def fight(self):
        """Open a fight, two beats, settle it: → the section."""
        self.t("open", self.d, "--kind", "fight", "--title", "Room 2.4 · Darkmantle (CR 1/2)",
               "--where", "Floor 2 · room 2.4", "--foes", json.dumps(FOES["darkmantle"]))
        self.t("sent", self.d)
        self.t("beat", self.d, "--round", 1, "--text", "Magic Missile: 9 force dmg; it is on 13/22 HP.",
               "--line", "foe/attack/1: Crush: miss.",
               "--line", "morten/cast: Magic Missile holds: 9 force dmg.",
               "--die", "1d20+5:2:AC 15:miss", "--die", "1d20+5:10:DC 11:cast", "--die", "3d4+3:1,3,2",
               "--foe", "Darkmantle=13/22")
        self.t("sent", self.d)
        self.t("log", self.d, "rolling round 2")
        self.t("sent", self.d)
        self.t("beat", self.d, "--round", 2, "--text", "A crit for 10 dmg; Thunderwave kills it.",
               "--line", "foe/attack/2: Crush, a natural 20: 10 bludgeoning dmg.",
               "--line", "morten/cast/3: Thunderwave: 13 thunder dmg. Dead.",
               "--die", "1d20+5:20:AC 15:hit", "--die", "2d6+3:3,4",
               "--die", "1d20+5:15:DC 11:cast", "--die", "1d20+1:8:DC 13:fail", "--die", "2d8:7,6",
               "--hp", "10/20", "--foe", "Darkmantle=0")
        self.t("sent", self.d)
        self.t("morten", self.d, "--xp", "+100", "--coins", "+10 GP")
        self.t("sent", self.d)
        f = self.md("s.md", "---\ntitle: Room 2.4 · Darkmantle (CR 1/2) · Moderate, 100 XP · cleared\n"
                    "difficulty: Moderate\nxp: 100\ninitiative: Darkmantle 21 › Morten 17\nloot: +10 GP\n---\n"
                    "The Darkmantle crit him and Thunderwave blew it off.\n\n- **The dice:** a natural 20.\n")
        out, _ = self.t("section", self.d, "--file", f)
        return out, json.loads((self.d / "story" / "s0004.json").read_text())


class Projections(Case):
    def test_new_writes_every_singleton_in_shape(self):
        out, _ = self.t("new", self.d, "--month", 2, "--day", 1, "--hex", "B5")
        writes = self.batches(out)[0]["writes"]
        self.assertEqual({(w["collection"], w["doc_id"]) for w in writes},
                         {("game", "state"), ("game", "morten"), ("game", "realm"), ("game", "rules")})
        self.assertTrue(all("if_version" not in w and w["op"] == "set" for w in writes))
        st = self.doc("game", "state")
        self.shape(st, STATE, "game/state")
        self.shape(st["hud"], HUD, "hud")
        self.shape(st["table"], TABLE, "table")
        self.shape(st["awaiting"], AWAIT, "awaiting")
        m = self.doc("game", "morten")
        self.shape(m, MORTEN, "game/morten")
        for s in m["spells"]:
            self.shape(s, SPELL, s["name"])
        r = self.doc("game", "realm")
        self.shape(r, REALM, "game/realm")
        for name, k in r["kinds"].items():
            self.shape(k, KIND, name)
        self.assertEqual(r["days"]["B5"], 0)
        self.assertEqual(r["days"]["A5"], 1)
        self.assertEqual(r["hexNames"]["A5"], "the Humans' savanna")
        for e in r["eventsWords"]:
            self.assertEqual(set(e) >= {"n", "who", "from", "to", "text"}, True)
        for h, f in r["floors"].items():
            for room in f["rooms"]:
                self.shape(room, ROOM, h)
                if room["state"] == "unknown":
                    self.assertIsNone(room["monster"])
        self.assertEqual(r["floors"]["A5"]["rooms"][0]["monster"], "3 Grimlocks")
        self.assertEqual(r["floors"]["B3"]["rooms"], [])  # never entered
        ru = self.doc("game", "rules")
        self.assertEqual([s["id"] for s in ru["sections"]],
                         ["cast", "death", "campaign", "pieces", "missions", "actions", "leaders", "report"])
        cast = ru["sections"][0]["md"]
        self.assertIn("Wizard mishap table", cast)
        self.assertNotRegex(cast, r"(?m)^#{1,2} ")
        for s in ru["sections"]:
            self.assertTrue(s["md"].strip(), s["id"])

    def test_realm_hides_unexplored_rooms(self):
        gm = (self.d / "gm-secrets.md").read_text().replace("| 2.4 ✓ |", "| 2.4 |").replace("| 2.5 ✓ |", "| 2.5 |")
        (self.d / "gm-secrets.md").write_text(gm)
        self.new()
        rooms = {r["n"]: r for r in self.doc("game", "realm")["floors"]["A5"]["rooms"]}
        self.assertEqual(rooms["2.3"]["state"], "cleared")
        self.assertEqual(rooms["2.4"], {"n": "2.4", "monster": None, "cr": None, "state": "unknown"})
        self.assertNotIn("Giant Wolf Spider", json.dumps(self.doc("game", "realm")))

    def test_rules_drift_is_loud(self):
        with self.assertRaises(T.Bad):
            T.cut("## A\ntext\n", "## 4. Assets")

    def test_orders_auto(self):
        self.new()
        self.t("state", self.d, "--awaiting", "orders", "--prompt", "Month 3's orders")
        aw = self.doc("game", "state")["awaiting"]
        self.assertEqual(aw["kind"], "orders")
        o = aw["orders"]
        self.assertEqual(o["hexes"][0], {"id": "B5", "name": "the tower's desert", "days": 0})
        self.assertTrue(all(isinstance(h["days"], int) for h in o["hexes"]))
        self.assertIn({"type": "delve", "target": "floor 2"},
                      [{"type": m["type"], "target": m["target"]} for m in o["missions"]])
        acts = {a["action"]: a for a in o["actions"]}
        self.assertEqual(acts["buy:farms@B5"]["cost"], 200)
        self.assertEqual(acts["raise:cunning"]["cost"], 200)
        self.assertFalse(acts["buy:thugs@B5"]["affordable"])  # 89 GP + 60 GP income
        self.assertEqual(o["realms"][:2], ["Goblinkind", "Humans"])  # allies first
        for a in o["actions"]:
            self.assertRegex(a["action"], T.ACTION)
        self.assertEqual(self.doc("game", "state")["status"], "awaiting")


class Story(Case):
    def test_seq_ordering_and_beats_to_trace(self):
        self.new()
        out, sec = self.fight()
        self.shape(sec, SECTION, "section")
        # one counter: beat 1, log 2, beat 3, the section 4 (open and morten take none)
        seqs = {p.stem: json.loads(p.read_text())["seq"]
                for p in (self.d / "page" / "out").rglob("*.json") if re.fullmatch(r"[sbl]\d{4}", p.stem)}
        self.assertEqual(seqs, {"b0001": 1, "l0002": 2, "b0003": 3, "s0004": 4})
        # the trace is the beats' lines, in order, with their rounds and dice
        self.assertEqual([ln["text"][:5] for ln in sec["trace"]], ["Crush", "Magic", "Crush", "Thund"])
        self.assertEqual([ln["round"] for ln in sec["trace"]], [1, 1, 2, 2])
        self.assertEqual([len(ln["dice"]) for ln in sec["trace"]], [1, 2, 2, 3])
        for ln in sec["trace"]:
            self.shape(ln, LINE, "line")
            for dd in ln["dice"]:
                self.shape(dd, DIE, "die")
        self.assertEqual(sec["trace"][2]["dice"][0]["nat"], 20)
        self.assertEqual(sec["trace"][1]["dice"][1]["total"], 9)
        f = sec["fight"]
        self.shape(f, FIGHT, "fight")
        for foe in f["foes"]:
            self.shape(foe, FOE, "foe")
        self.assertEqual(f["hpTrack"], [{"name": "Morten", "max": 20, "hp": [20, 20, 10]},
                                        {"name": "Darkmantle", "max": 22, "hp": [22, 13, 0]}])
        self.assertEqual((f["rounds"], f["xpBefore"], f["xpAfter"]), (2, 1275, 1375))
        self.assertEqual(f["initiative"], ["Darkmantle 21", "Morten 17"])
        self.assertEqual(sec["headline"], "The Darkmantle crit him and Thunderwave blew it off.")
        self.assertEqual(sec["bullets"], [{"label": "The dice", "text": "a natural 20."}])
        # the batch: the section, its beats and the log line deleted (pinned), game/state
        w = {(x["collection"], x["doc_id"]): x for x in self.batches(out)[0]["writes"]}
        self.assertNotIn("if_version", w[("story", "s0004")])
        self.assertEqual(w[("live", "b0001")], {"op": "delete", "collection": "live", "doc_id": "b0001", "if_version": 1})
        self.assertEqual(w[("live", "b0003")]["op"], "delete")
        self.assertEqual(w[("log", "l0002")]["op"], "delete")
        self.assertEqual(w[("game", "state")]["op"], "set")
        st = self.doc("game", "state")
        self.assertIsNone(st["live"])
        self.assertEqual((st["latest"], st["lastFight"], st["lastSeq"]), ("s0004", "s0004", 4))
        self.assertFalse((self.d / "live" / "open.json").exists())
        self.assertEqual(list((self.d / "live").glob("b*.json")), [])

    def test_beat_shape_and_live_state(self):
        self.new()
        self.t("open", self.d, "--kind", "fight", "--title", "Room 2.5", "--foes", json.dumps(FOES["spiders"]))
        st = self.doc("game", "state")
        self.assertEqual(st["live"]["title"], "Room 2.5")
        self.assertEqual(st["status"], "playing")
        out, _ = self.t("beat", self.d, "--round", 1, "--text", "A bite misses.", "--line",
                        "foe/attack: A bites: miss.", "--die", "1d20+5:8:AC 15:miss",
                        "--foe", "Giant Wolf Spider A=bloodied")
        writes = self.batches(out)[0]["writes"]
        self.assertEqual(len(writes), 1)  # a beat is a one-write batch
        b = self.doc("live", "b0001")
        self.shape(b, BEAT, "beat")
        self.assertEqual([f["name"] for f in b["state"]["foes"]],
                         ["Giant Wolf Spider A", "Giant Wolf Spider B", "Giant Wolf Spider C"])
        self.assertEqual(b["state"]["foes"][0], {"name": "Giant Wolf Spider A", "hp": None, "maxHp": 11,
                                                 "state": "bloodied"})
        with self.assertRaises(SystemExit):  # a second open while one is open
            self.t("open", self.d, "--kind", "fight", "--title", "again")

    def test_dice_from_roll_keep(self):
        self.new()
        self.t("open", self.d, "--kind", "fight", "--title", "Test fight")
        roll = [sys.executable, str(HERE / "roll.py")]
        r = subprocess.run(roll + ["--keep", str(self.d), "1d20+5", "--adv", "--vs", "AC 13",
                                   "--result", "hit", "2d6"], capture_output=True, text=True, check=True)
        self.assertRegex(r.stdout.splitlines()[0], r"^1d20\+5: \[\d+, \d+\] keep \[\d+\] \+ 5 = \d+")
        self.t("beat", self.d, "--round", 1, "--text", "Scorching Ray.", "--line",
               "morten/attack: Scorching Ray: a hit.")
        dice = self.doc("live", "b0001")["lines"][0]["dice"]
        self.assertEqual([x["expr"] for x in dice], ["1d20+5", "2d6"])
        self.assertEqual((dice[0]["vs"], dice[0]["result"], len(dice[0]["faces"])), ("AC 13", "hit", 2))
        self.assertEqual(dice[0]["kept"], [max(dice[0]["faces"])])
        self.assertIsNone(dice[1]["vs"])
        self.assertFalse((self.d / "live" / "rolls.jsonl").exists())

    def test_domain_section(self):
        self.new()
        f = self.md("d.md", "---\nkind: domain\ntitle: Month 2 · the world's turn\n---\nQuiet.\n\n"
                    "### The plan\n- Delve floor 2.\n### What happened\n- n=2: The Tieflings built a Treasury.\n"
                    "### Elsewhere\nThe Orcs bought Knights.\n### The tower now\n- Gold: 7 GP → 89 GP\n"
                    "### Next month\n- Threat: none.\n- Chance: the Elves' seat A2 is unguarded.\n- Open: floor 3.\n")
        self.t("section", self.d, "--file", f)
        d = json.loads((self.d / "story" / "s0001.json").read_text())["domain"]
        self.shape(d, DOMAIN, "domain")
        self.shape(d["happened"][0], HAPPENED, "happened")
        self.assertEqual(d["happened"][0]["label"], "bad")
        self.assertEqual(d["happened"][0]["to"], "D5")
        self.assertEqual(d["tower"], [{"what": "Gold", "before": "7 GP", "after": "89 GP"}])
        self.assertEqual(d["next"], {"threats": ["none."], "chances": ["the Elves' seat A2 is unguarded."],
                                     "open": ["floor 3."]})
        self.assertTrue(d["log"])  # realms.json's public lines
        bad = self.md("e.md", "---\nkind: domain\ntitle: x\n---\n### What happened\n- n=99: nothing.\n")
        with self.assertRaises(SystemExit):
            self.t("section", self.d, "--file", bad)

    def test_aside(self):
        self.new()
        self.t("aside", self.d, "--text", "A ruling: pushing a Darkmantle away detaches it.")
        s = json.loads((self.d / "story" / "s0001.json").read_text())
        self.assertEqual((s["kind"], s["ooc"], s["prose"]),
                         ("aside", False, ["A ruling: pushing a Darkmantle away detaches it."]))

    def test_dice_and_lines_errors(self):
        self.assertEqual(T.parse_die("1d20+5 dis:14,3:AC 13:miss")["kept"], [3])
        self.assertEqual(T.parse_die("4d6kh3:1,5,4,3")["total"], 12)
        self.assertEqual(T.parse_die("1d20-1:1")["nat"], 1)
        for bad in ("1d20+5", "1d20+5:21", "2d6:3", "1d20:5:AC 1:smash", "x:1"):
            with self.assertRaises(T.Bad, msg=bad):
                T.parse_die(bad)
        with self.assertRaises(T.Bad):
            T.build_lines(["morten/cast/1: x"], [T.parse_die("1d6:1"), T.parse_die("1d6:2")])
        with self.assertRaises(T.Bad):
            T.parse_line("wizard/cast: x")


class Moves(Case):
    GOOD = [
        {"v": 1, "seq": 1, "at": "2026-10-25T09:00:00Z", "kind": "say", "text": "Where is floor 3?", "ooc": True},
        {"v": 1, "seq": 2, "at": "2026-10-25T09:01:00Z", "kind": "play", "scope": "month"},
        {"v": 1, "seq": 3, "at": "2026-10-25T09:02:00Z", "kind": "orders", "travel": "A5",
         "mission": {"type": "delve", "target": "floor 2"}, "action": "buy:farms@B5",
         "give": {"realm": "Humans", "gp": 10}, "plan": "XP at low risk"},
        {"v": 1, "seq": 4, "at": "2026-10-25T09:03:00Z", "kind": "fight", "choice": "avoid", "text": ""},
        {"v": 1, "seq": 5, "at": "2026-10-25T09:04:00Z", "kind": "turn", "text": "Fire Bolt the goblin"},
        {"v": 1, "seq": 6, "at": "2026-10-25T09:05:00Z", "kind": "table",
         "table": {"who": "you", "stop": "fight", "fights": "summary", "world": "report", "dice": "all",
                   "mode": "closed", "habits": ["Shield at AC 20."]}},
        {"v": 1, "seq": 7, "at": "2026-10-25T09:06:00Z", "kind": "take", "who": "you"},
    ]
    BAD = [
        ({"v": 1, "seq": 8, "at": "x", "kind": "say", "text": ""}, "say.text"),
        ({"v": 1, "seq": 9, "at": "x", "kind": "say", "text": "hi", "ooc": "yes"}, "say.ooc"),
        ({"v": 1, "seq": 10, "at": "x", "kind": "play", "scope": "forever"}, "play.scope"),
        ({"v": 1, "seq": 11, "at": "x", "kind": "orders", "travel": "Z9", "mission": None, "action": None,
          "give": None, "plan": ""}, "orders.travel"),
        ({"v": 1, "seq": 12, "at": "x", "kind": "orders", "travel": "A5", "mission": None,
          "action": "rm -rf /", "give": None, "plan": ""}, "orders.action"),
        ({"v": 1, "seq": 13, "at": "x", "kind": "orders", "travel": "A5", "plan": ""}, "orders.mission is missing"),
        ({"v": 1, "seq": 14, "at": "x", "kind": "orders", "travel": "A5", "mission": None, "action": None,
          "give": {"realm": "Humans", "gp": -5}, "plan": ""}, "orders.give"),
        ({"v": 1, "seq": 15, "at": "x", "kind": "table", "table": {"who": "you"}}, "table.stop"),
        ({"v": 1, "seq": 16, "at": "x", "kind": "take", "who": "nobody"}, "take.who"),
        ({"v": 2, "seq": 17, "at": "x", "kind": "turn", "text": "go"}, "v must be 1"),
        ({"v": 1, "seq": "18", "at": "x", "kind": "turn", "text": "go"}, "seq"),
        ({"v": 1, "seq": 19, "at": "x", "kind": "dance"}, "kind must be"),
        ({"v": 1, "seq": 20, "at": "x", "kind": "say", "text": "x" * 5000, "ooc": False}, "say.text"),
    ]

    def test_validate_good_and_bad(self):
        hexes = {f"{c}{r}" for c in "ABCD" for r in range(1, 6)}
        for m in self.GOOD:
            errs, _ = T.validate_move(m, hexes)
            self.assertEqual(errs, [], m["kind"])
            self.assertTrue(T.move_words(m))
        for m, want in self.BAD:
            errs, _ = T.validate_move(m, hexes)
            self.assertTrue(any(want in e for e in errs), f"{m} → {errs}")
        _, warn = T.validate_move({**self.GOOD[0], "client": "x"}, hexes)
        self.assertEqual(warn, ["ignored fields: client"])

    def dump(self, moves, versions=None):
        """An out_dir dump as db.mjs moves --out writes it."""
        root = self.tmp / "dump"
        shutil.rmtree(root, ignore_errors=True)
        for m in moves:
            did = f"m{m['seq']:04d}"
            p = root / "moves" / f"{did}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"collection": "moves", "doc_id": did,
                                     "version": (versions or {}).get(did, 1), "data": m}))
        return root

    def test_moves_read_answered_and_deleted_pinned(self):
        self.new()
        root = self.dump(self.GOOD[:3], {"m0002": 3})
        out, _ = self.t("moves", self.d, "--file", root)
        self.assertIn("m0003 (seq 3, orders, v1): orders: travel to A5 (the Humans' savanna, 1 days)", out)
        self.assertIn('asks out of game: "Where is floor 3?"', out)
        f = self.md("s.md", "---\nkind: orders\ntitle: Month 2's orders\n---\nDelve floor 2.\n")
        out, _ = self.t("section", self.d, "--file", f)
        w = {(x["collection"], x["doc_id"]): x for x in self.batches(out)[0]["writes"]}
        self.assertEqual(w[("moves", "m0002")], {"op": "delete", "collection": "moves", "doc_id": "m0002", "if_version": 3})
        self.assertEqual(w[("moves", "m0001")]["if_version"], 1)
        s = json.loads((self.d / "story" / "s0001.json").read_text())
        self.assertEqual(s["answered"], ["m0001", "m0002", "m0003"])
        self.assertEqual(s["words"][0], {"move": "m0001", "text": "Where is floor 3?"})
        self.assertEqual(self.doc("game", "state")["lastMove"], 3)
        self.t("sent", self.d)
        out, _ = self.t("moves", self.d, "--file", root)  # the same dump again: already answered
        self.assertIn("m0001, m0002, m0003: already answered", out)
        self.assertIn("nothing new", out)

    def test_malformed_moves_refused(self):
        self.new()
        root = self.dump([self.BAD[0][0], self.GOOD[1]])
        with self.assertRaises(SystemExit) as cm:
            self.t("moves", self.d, "--file", root)
        self.assertEqual(cm.exception.code, 3)
        page = json.loads((self.d / "page.json").read_text())
        self.assertFalse(page["moves"]["m0008"]["ok"])
        self.assertIsNone(page["moves"]["m0008"]["body"])
        f = self.md("s.md", "---\nkind: orders\ntitle: x\n---\nx\n")
        out, _ = self.t("section", self.d, "--file", f)
        s = json.loads((self.d / "story" / "s0001.json").read_text())
        self.assertEqual(s["answered"], ["m0002"])  # the refused one is deleted, not answered
        self.assertIn(("moves", "m0008"), {(x["collection"], x["doc_id"]) for x in self.batches(out)[0]["writes"]})

    def test_table_and_take_moves_applied_by_state(self):
        self.new()
        self.t("moves", self.d, "--file", self.dump(self.GOOD[5:7]))
        out, _ = self.t("state", self.d)
        st = self.doc("game", "state")
        self.assertEqual({k: st["table"][k] for k in T.DIALS},
                         {"who": "you", "stop": "fight", "fights": "summary", "world": "report", "dice": "all", "mode": "closed"})
        self.assertEqual(st["table"]["habits"], ["Shield at AC 20."])
        kinds = {(x["collection"], x["doc_id"], x["op"]) for x in self.batches(out)[0]["writes"]}
        self.assertTrue({("moves", "m0006", "delete"), ("moves", "m0007", "delete")} <= kinds)

    def test_read_moves_formats(self):
        f = self.tmp / "m.json"
        f.write_text(json.dumps({"moves": self.GOOD[:2]}))
        self.assertEqual([x[0] for x in T.read_moves(f)], ["m0001", "m0002"])
        f.write_text(json.dumps({"m0005": self.GOOD[4]}))
        self.assertEqual(T.read_moves(f)[0][:2], ("m0005", 1))
        f.write_text(json.dumps({**self.GOOD[0], "version": 4, "doc_id": "m0001"}))
        did, ver, body = T.read_moves(f)[0]
        self.assertEqual((did, ver, "version" in body), ("m0001", 4, False))


class Versions(Case):
    def test_pinning_pending_and_sent(self):
        self.new()  # sent: game/* at 1
        out, _ = self.t("state", self.d, "--doing", "a")
        self.assertEqual(self.batches(out)[0]["writes"][0]["if_version"], 1)
        out, _ = self.t("state", self.d, "--doing", "b")  # not sent yet: pinned past the pending one
        self.assertEqual(self.batches(out)[0]["writes"][0]["if_version"], 2)
        self.t("sent", self.d)
        page = json.loads((self.d / "page.json").read_text())
        self.assertEqual((page["versions"]["game/state"], page["pending"]), (3, []))
        self.t("sent", self.d, "--version", "game/state=7", "--url", "https://claude.ai/artifact/x")
        out, _ = self.t("state", self.d)
        self.assertEqual(self.batches(out)[0]["writes"][0]["if_version"], 7)
        self.assertEqual(self.doc("game", "state")["url"], "https://claude.ai/artifact/x")
        self.t("sent", self.d, "--drop")
        page = json.loads((self.d / "page.json").read_text())
        self.assertEqual((page["versions"]["game/state"], page["pending"]), (7, []))
        self.assertFalse((self.d / "page" / "out" / "batch.json").exists())  # the dropped batch goes

    def test_split_past_50(self):
        self.new()
        for i in range(55):
            self.t("log", self.d, f"line {i}")
        self.t("sent", self.d)
        f = self.md("s.md", "---\nkind: rest\ntitle: A rest\n---\nRested.\n")
        out, err = self.t("section", self.d, "--file", f)
        bs = self.batches(out)
        self.assertEqual([len(b["writes"]) for b in bs], [50, 7])  # 55 deletes, the section, game/state
        self.assertIn("split into 2 batches", err)
        self.assertTrue((self.d / "page" / "out" / "batch-2.json").exists())
        for b in bs:
            self.assertEqual(len({(w["collection"], w["doc_id"]) for w in b["writes"]}), len(b["writes"]))

    def test_morten_and_export(self):
        self.new()
        out, err = self.t("morten", self.d, "--hp", "-9", "--lose", "Shield", "--coins", "-1 SP",
                          "--item", "Rations -1", "--xp", "+100", "--conc", "Sleep")
        self.assertIn("HP 20 → 11/20", err)
        m = self.doc("game", "morten")
        self.assertEqual((m["hp"], m["coins"]["on"], m["xp"], m["conc"]), (11, "1 SP 5 CP", 1375, "Sleep"))
        self.assertEqual(self.doc("game", "state")["hud"]["lost"], ["Shield"])
        self.assertEqual({(w["collection"], w["doc_id"]) for w in self.batches(out)[0]["writes"]},
                         {("game", "morten"), ("game", "state")})
        with self.assertRaises(SystemExit):
            self.t("morten", self.d, "--coins", "-50 GP")
        self.t("sent", self.d)
        self.t("log", self.d, "x")
        exp = self.tmp / "export"
        self.t("export", self.d, exp)
        got = sorted(str(p.relative_to(exp)) for p in exp.rglob("*.json"))
        self.assertEqual(got, ["game/morten.json", "game/realm.json", "game/rules.json",
                               "game/state.json", "log/l0001.json"])
        self.assertEqual(json.loads((exp / "log" / "l0001.json").read_text())["text"], "x")


    def record(self):
        return json.loads((self.d / "page.json").read_text())

    def test_order_content_then_state_then_deletes(self):
        self.new()
        self.t("moves", self.d, "--file", Moves.dump(self, Moves.GOOD[:1]))
        self.t("open", self.d, "--kind", "fight", "--title", "Room 2.4", "--foes", json.dumps(FOES["darkmantle"]))
        self.t("beat", self.d, "--round", 1, "--text", "A miss.")
        self.t("log", self.d, "rolling round 2")
        self.t("sent", self.d)
        out, _ = self.t("section", self.d, "--file", self.md("s.md", "---\ntitle: Room 2.4 · cleared\n---\nDone.\n"))
        got = [(w["op"], w["collection"], w["doc_id"]) for w in self.batches(out)[0]["writes"]]
        self.assertEqual(got, [("set", "story", "s0003"), ("set", "game", "state"), ("delete", "live", "b0001"),
                               ("delete", "log", "l0002"), ("delete", "moves", "m0001")])

    def test_drop_puts_the_record_back(self):
        self.new()
        self.t("moves", self.d, "--file", Moves.dump(self, Moves.GOOD[:2]))
        self.t("open", self.d, "--kind", "fight", "--title", "Room 2.4", "--foes", json.dumps(FOES["darkmantle"]))
        self.t("beat", self.d, "--round", 1, "--text", "A miss.", "--hp", "15/20")
        self.t("sent", self.d)
        before = {f: (self.d / f).read_text() for f in ("page.json", "state.json", "morten.json", "transcript.md")}
        state_out = self.doc("game", "state")
        subprocess.run([sys.executable, str(HERE / "roll.py"), "--keep", str(self.d), "1d20+5"],
                       capture_output=True, check=True)
        rolls = (self.d / "live" / "rolls.jsonl").read_text()
        f = self.md("s.md", "---\ntitle: Room 2.4 · cleared\n---\nDone.\n")
        self.t("section", self.d, "--file", f)  # never sent
        self.t("morten", self.d, "--xp", "+100")  # nor this
        self.assertTrue((self.d / "story" / "s0002.json").exists())
        _, err = self.t("sent", self.d, "--drop")
        self.assertIn("the record is back", err)
        for name, text in before.items():
            self.assertEqual((self.d / name).read_text(), text, name)
        self.assertFalse((self.d / "story" / "s0002.json").exists())
        self.assertFalse((self.d / "page" / "out" / "story" / "s0002.json").exists())
        self.assertTrue((self.d / "live" / "open.json").exists())
        self.assertTrue((self.d / "live" / "b0001.json").exists())
        self.assertEqual((self.d / "live" / "rolls.jsonl").read_text(), rolls)
        self.assertEqual(self.doc("game", "state"), state_out)
        self.assertEqual(sorted(self.record()["moves"]), ["m0001", "m0002"])  # still to answer
        self.assertFalse((self.d / "page" / "undo").exists())
        # redo: the same section, the same id, the moves deleted after all
        out, _ = self.t("section", self.d, "--file", f)
        w = {(x["collection"], x["doc_id"]) for x in self.batches(out)[0]["writes"]}
        self.assertTrue({("story", "s0002"), ("moves", "m0001"), ("moves", "m0002"), ("live", "b0001")} <= w)
        self.t("sent", self.d)
        self.assertFalse((self.d / "page" / "undo").exists())

    def test_drop_of_new_unseeds(self):
        self.t("new", self.d, "--month", 2)
        self.t("sent", self.d, "--drop")
        self.assertFalse((self.d / "page.json").exists())
        self.new()  # and seeds again
        self.assertEqual(self.record()["versions"]["game/state"], 1)

    def test_landed_part_way(self):
        self.new()
        for i in range(55):
            self.t("log", self.d, f"line {i}")
        self.t("sent", self.d)
        out, err = self.t("section", self.d, "--file", self.md("s.md", "---\nkind: rest\ntitle: A rest\n---\nRested.\n"))
        first, second = self.batches(out)
        self.assertEqual([(w["collection"], w["doc_id"]) for w in first["writes"][:2]],
                         [("story", "s0056"), ("game", "state")])  # the page is right after batch 1
        self.assertIn("batch.json writes 1–50; batch-2.json writes 51–57", err)
        out, err = self.t("sent", self.d, "--landed", 50)  # batch-2.json was refused
        v = self.record()["versions"]
        self.assertEqual((v["story/s0056"], v["game/state"], "log/l0001" in v, "log/l0055" in v), (1, 2, False, True))
        again = self.batches(out)
        self.assertEqual(len(again), 1)
        self.assertEqual(again[0]["writes"], second["writes"])  # the rest, pinned as before
        self.assertEqual(len(self.record()["pending"]), 1)
        self.t("sent", self.d)
        self.assertFalse(any(k.startswith("log/") for k in self.record()["versions"]))
        with self.assertRaises(SystemExit):
            self.t("sent", self.d, "--landed", 3)  # nothing pending

    def test_resend_after_a_refused_pin(self):
        self.new()
        out, _ = self.t("state", self.d, "--doing", "a")
        self.assertEqual(self.batches(out)[0]["writes"][0]["if_version"], 1)
        # refused: "game/state is at version 4" (the record was behind)
        out, err = self.t("resend", self.d, "--version", "game/state=4")
        self.assertIn("game/state: version 1 → 4", err)
        self.assertEqual(self.batches(out)[0]["writes"][0]["if_version"], 4)
        self.t("sent", self.d)
        self.assertEqual(self.record()["versions"]["game/state"], 5)

    def test_versions_from_a_listing(self):
        self.new()
        dump = self.tmp / "dump.json"  # db.mjs dump
        dump.write_text(json.dumps([{"collection": "game", "doc_id": "state", "version": 6, "data": {}},
                                    {"collection": "game", "doc_id": "morten", "version": 3, "data": {}}]))
        self.t("sent", self.d, "--from", dump)
        self.assertEqual({k: v for k, v in self.record()["versions"].items() if k in ("game/state", "game/morten")},
                         {"game/state": 6, "game/morten": 3})
        od = self.tmp / "od"  # an ArtifactData out_dir: <out_dir>/<collection>/<doc_id>.json
        (od / "game").mkdir(parents=True)
        (od / "game" / "state.json").write_text(json.dumps({"version": 9, "data": {"v": 1}}))
        self.assertEqual(T.read_versions(od), {"game/state": 9})
        (od / "game" / "state.json").write_text(json.dumps({"v": 1, "status": "awaiting"}))
        with self.assertRaises(T.Bad):  # no version: say so, never guess
            T.read_versions(od)

    def test_log_line_lifecycle(self):
        self.new()
        self.t("log", self.d, "  reading\n your   move ")
        self.assertEqual(self.doc("log", "l0001")["text"], "reading your move")
        _, err = self.t("log", self.d, "x" * 300)
        self.assertEqual(len(self.doc("log", "l0002")["text"]), T.LOG_MAX)
        with self.assertRaises(SystemExit):
            self.t("log", self.d, "   ")
        self.t("sent", self.d)
        out, _ = self.t("state", self.d, "--doing", "still playing")  # not a stop: the lines stay
        self.assertNotIn("delete", out)
        self.t("sent", self.d)
        out, _ = self.t("state", self.d, "--awaiting", "word", "--prompt", "Your word")  # a stop
        dels = {w["doc_id"] for w in self.batches(out)[0]["writes"] if w["op"] == "delete"}
        self.assertEqual(dels, {"l0001", "l0002"})

    def test_unconfirmed_log_line_dropped_not_deleted(self):
        self.new()
        self.t("log", self.d, "sent and confirmed")
        self.t("sent", self.d)
        self.t("log", self.d, "never confirmed")  # its batch is never recorded
        out, err = self.t("state", self.d, "--awaiting", "word", "--prompt", "Your word")
        self.assertIn("log/l0002 was never confirmed sent", err)
        dels = [w["doc_id"] for w in self.batches(out)[0]["writes"] if w["op"] == "delete"]
        self.assertEqual(dels, ["l0001"])
        pend = [e["doc_id"] for b in self.record()["pending"] for e in b]
        self.assertNotIn("l0002", pend)
        self.t("sent", self.d)
        self.assertNotIn("log/l0002", self.record()["versions"])
        self.assertFalse((self.d / "page" / "out" / "log" / "l0002.json").exists())

    def test_refused_moves_deleted_by_state(self):
        self.new()
        with self.assertRaises(SystemExit):
            self.t("moves", self.d, "--file", Moves.dump(self, [Moves.BAD[0][0]]))
        out, _ = self.t("state", self.d)
        self.assertIn({"op": "delete", "collection": "moves", "doc_id": "m0008", "if_version": 1},
                      self.batches(out)[0]["writes"])

    def test_page_json_read_defensively(self):
        self.new()
        pj = self.record()
        pj.update({"versions": {"game/state": 2, "game/morten": "x", "game/rules": 0}, "wake": True})
        (self.d / "page.json").write_text(json.dumps(pj))
        out, _ = self.t("state", self.d)
        w = {(x["collection"], x["doc_id"]): x for x in self.batches(out)[0]["writes"]}
        self.assertEqual(w[("game", "state")]["if_version"], 2)
        self.assertNotIn("if_version", w[("game", "morten")])  # "x" is no version: resent as a create
        self.assertEqual(self.doc("game", "state")["wake"], {"on": True})

    def test_document_cap(self):
        self.new()
        with self.assertRaises(SystemExit):
            self.t("aside", self.d, "--text", "word " * 60000)
        self.assertFalse((self.d / "story" / "s0001.json").exists())


class Renderers(Case):
    def test_markdown_renders(self):
        self.new()
        self.fight()
        ch = (self.d / "character.md").read_text()
        self.assertTrue(ch.startswith("# Morten — Wizard 3 (Evoker)"))
        self.assertIn("| Thunderwave | 1 | 11 |", ch)
        st = (self.d / "state.md").read_text()
        for want in ("## Morten", "## Habits", "## Domain (Realms v2)", "HP 10/20", "Floor 2 (A5)",
                     "Morten played by:** the GM"):
            self.assertIn(want, st)
        self.assertNotIn("Smugglers", st)  # the tower's view only
        tr = (self.d / "transcript.md").read_text()
        self.assertIn("## Room 2.4 · Darkmantle", tr)
        self.assertIn("R2 · Foe: Crush, a natural 20: 10 bludgeoning dmg. (d20 20 +5 = 25 vs AC 15, NAT 20, HIT;", tr)
        self.assertIn("HP track, Darkmantle: 22 → 13 → 0 (of 22 HP)", tr)

    def test_roll_cli_unchanged(self):
        r = subprocess.run([sys.executable, str(HERE / "roll.py"), "1d20+5", "--adv", "4d6kh3", "2d6-1"],
                           capture_output=True, text=True, check=True)
        lines = r.stdout.splitlines()
        self.assertRegex(lines[0], r"^1d20\+5: \[\d+, \d+\] keep \[\d+\] \+ 5 = \d+( NAT20| NAT1)?$")
        self.assertRegex(lines[1], r"^4d6kh3: \[\d, \d, \d, \d\] keep \[\d, \d, \d\] \+ 0 = \d+$")
        self.assertRegex(lines[2], r"^2d6-1: \[\d, \d\] - 1 = \d+$")


class Fixture(unittest.TestCase):
    """The exported fixture (web/dev/fixture, fixture-live) holds the README's shapes."""

    def test_fixture_shapes(self):
        for name in ("fixture", "fixture-live", "fixture-v3"):
            root = GAME / "web" / "dev" / name
            if not (root / "game" / "state.json").exists():
                self.skipTest(f"{name} not built")
            c = Case("shape")
            st = json.loads((root / "game" / "state.json").read_text())
            c.shape(st, STATE, f"{name} game/state")
            c.shape(st["hud"], HUD, "hud")
            c.shape(json.loads((root / "game" / "morten.json").read_text()), MORTEN, "game/morten")
            c.shape(json.loads((root / "game" / "realm.json").read_text()), REALM, "game/realm")
            secs = sorted((json.loads(p.read_text()) for p in (root / "story").glob("*.json")),
                          key=lambda x: x["seq"])
            kinds = {x["kind"] for x in secs}
            if name == "fixture-v3":
                self.assertTrue({"opening", "orders", "delve", "fight", "rest", "domain"} <= kinds, kinds)
            else:
                self.assertTrue({"opening", "aside", "orders", "travel", "fight", "rest"} <= kinds, kinds)
            for x in secs:
                c.shape(x, SECTION, f"{name} {x['seq']}")
                for ln in x["trace"]:
                    c.shape(ln, LINE, "line")
                    for dd in ln["dice"]:
                        c.shape(dd, DIE, "die")
                if x["fight"]:
                    c.shape(x["fight"], FIGHT, "fight")
                    for t in x["fight"]["hpTrack"]:
                        self.assertEqual(len(t["hp"]), x["fight"]["rounds"] + 1, x["title"])
                if x["domain"]:
                    c.shape(x["domain"], DOMAIN, "domain")
            beats = [json.loads(p.read_text()) for p in (root / "live").glob("*.json")] if (root / "live").exists() else []
            for b in beats:
                c.shape(b, BEAT, "beat")
            ids = [st.get("latest")] + [f"s{x['seq']:04d}" for x in secs]
            self.assertEqual(st["latest"], ids[-1])
            if name == "fixture-v3":
                self.assertEqual((st["status"], st["awaiting"]["kind"], st["month"]), ("awaiting", "orders", 2))
                self.assertEqual(st["awaiting"]["orders"]["version"], 3)
                r = json.loads((root / "game" / "realm.json").read_text())
                self.assertEqual(r["version"], 3)
                for k in r["kinds"].values():
                    c.shape(k, KIND3, "kind")
            elif name == "fixture":
                self.assertEqual((st["status"], st["awaiting"]["kind"], st["month"]), ("awaiting", "orders", 3))
                self.assertIn("domain", kinds)
                self.assertEqual(beats, [])
            else:
                self.assertEqual((st["status"], st["live"]["kind"], len(beats)), ("playing", "fight", 2))
                self.assertTrue(list((root / "log").glob("*.json")))


class Secrecy(Case):
    def test_fixture_is_clean(self):
        if not (FIXTURE / "page.json").exists():
            self.skipTest("fixture not built (bash dnd-crunch/web/dev/fixture-campaign/play.sh)")
        docs = [str(GAME / "web" / "dev" / x) for x in ("fixture", "fixture-live") if (GAME / "web" / "dev" / x).exists()]
        args = [str(FIXTURE)] + [a for d in docs for a in ("--docs", d)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_table.main(args), 0)
        if (FIXTURE3 / "page.json").exists():
            args = [str(FIXTURE3), "--docs", str(GAME / "web" / "dev" / "fixture-v3")]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_table.main(args), 0)

    def planted(self, mutate):
        self.tearDown()
        self.setUp()
        self.new()
        self.t("aside", self.d, "--text", "Nothing to see.")
        p = self.d / "page" / "out" / "story" / "s0001.json"
        doc = json.loads(p.read_text())
        mutate(doc)
        p.write_text(json.dumps(doc))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = check_table.main([str(self.d)])
        return code, out.getvalue()

    def test_clean_campaign_passes(self):
        code, out = self.planted(lambda d: None)
        self.assertEqual(code, 0, out)

    def test_catches_planted_secrets(self):
        cases = [
            ("room 3.5 holds two Goblin Bosses", "unexplored room 3.5"),
            ("a Gelatinous Cube somewhere", "only in unexplored rooms: Gelatinous Cube"),
            ("thick fog (heavily obscured beyond 3 m) ahead", "room feature only in unexplored rooms"),
            ("the Elves' Smugglers move", "hidden asset a19 by name"),
            ("asset a23 is near", "hidden asset a23"),
            ("Saboteurs sit in C5", "hidden asset a23 by kind and hex"),
            ("**Assets** (GM: all)", "--gm"),
            ("floor total: 1,900 · 9 encounters", "floor's totals"),
        ]
        for text, want in cases:
            code, out = self.planted(lambda d, t=text: d["prose"].append(t))
            self.assertEqual(code, 1, text)
            self.assertIn(want, out, text)
            self.assertIn("s0001.json at prose[1]", out)
        code, out = self.planted(lambda d: d.update({"dissident": "Ilyana"}))
        self.assertEqual(code, 1)
        self.assertIn("private key 'dissident'", out)

    def test_catches_unexplored_room_in_realm(self):
        self.new()
        p = self.d / "page" / "out" / "game" / "realm.json"
        r = json.loads(p.read_text())
        r["floors"]["B3"]["rooms"] = [{"n": "3.1", "monster": None, "cr": None, "state": "cleared"}]
        p.write_text(json.dumps(r))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check_table.main([str(self.d)]), 1)
        self.assertIn("room 3.1 is shown but not explored", out.getvalue())


    def test_fresh_worlds_leak_nothing(self):
        """As Dream's test_secrets: worlds the fixture never saw, played a few months, projected
        and checked. Hidden assets and the --gm lines of each turn must not reach the store."""
        realms = [sys.executable, str(HERE / "realms.py")]
        for seed in (11, 23, 37):
            d = self.tmp / f"w{seed}"
            subprocess.run(realms + ["new", "--seed", str(seed), "--campaign", str(d), "--level", "3"],
                           capture_output=True, check=True)
            shutil.copy(START, d / "morten.json")
            tower = json.loads((d / "map.json").read_text())["morten"]["hex"]
            self.t("new", d, "--hex", tower)
            self.t("sent", d)
            hidden = []
            for month in range(3):
                turn = realms + ["turn", "--campaign", str(d), "--at", tower]
                gm = subprocess.run(turn + ["--gm", "--dry-run"], capture_output=True, text=True, check=True).stdout
                pub = subprocess.run(turn, capture_output=True, text=True, check=True).stdout
                hidden += [ln for ln in gm.splitlines() if ln.strip() and ln not in pub.splitlines()
                           and re.search(r"\ba\d+\b", ln)]
                f = self.md("d.md", f"---\nkind: domain\ntitle: Month {month + 1} · the world's turn\n---\nThe world moved.\n")
                self.t("section", d, "--file", f)
                self.t("state", d, "--awaiting", "orders", "--prompt", "Orders", "--realm")
                self.t("sent", d)
            pats, _ = check_table.secrets(d)
            self.assertTrue(any(w.startswith("hidden asset") for w, _ in pats), f"seed {seed}: nothing hidden to test")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(check_table.main([str(d)]), 0, f"seed {seed}: {out.getvalue()}")
            whole = "\n".join(p.read_text() for p in (d / "page" / "out").rglob("*.json"))
            self.assertTrue(hidden, f"seed {seed}: no hidden events in three months")
            for ln in hidden:  # "- Gnomes (…): Move Assassins a15 B1 → C2 (goal: …)": the deed itself
                deed = ln.split("): ", 1)[-1].split(" (goal")[0]
                self.assertNotIn(deed, whole, f"seed {seed}: a --gm line reached the store: {ln}")


class RealmsV3(Case):
    """A Realms v3 campaign (tools/realms3.py) at the table: the projection, the orders form
    and the orders move, the tower line, the domain section, the secrecy check."""

    def setUp(self):
        super().setUp()
        for f in ("map.json", "realms.json", "gm-secrets.md", "rules.md", "world.md"):
            (self.d / f).unlink()
        subprocess.run([sys.executable, str(HERE / "realms3.py"), "new", "--seed", "7", "--campaign",
                        str(self.d), "--level", "3"], capture_output=True, check=True)
        shutil.copy(GAME / "templates" / "realms-rules.md", self.d / "rules.md")
        (self.d / "morten.json").unlink()

    def new(self):
        self.t("new", self.d, "--sheet", "fresh", "--hex", "B5", "--where", "the tower (B5)")
        self.t("sent", self.d)

    def turn(self, *args):
        subprocess.run([sys.executable, str(HERE / "realms3.py"), "turn", "--campaign", str(self.d), *args],
                       capture_output=True, check=True, text=True)

    def test_realm_projection(self):
        self.new()
        r = self.doc("game", "realm")
        self.shape(r, REALM, "game/realm")
        self.assertEqual(r["version"], 3)
        self.assertEqual(set(r["words"]) & {"force", "standing", "clock", "hold", "renown", "tier", "site"},
                         {"force", "standing", "clock", "hold", "renown", "tier", "site"})
        self.assertFalse({"cunning", "wealth", "regime", "piece"} & set(r["words"]))
        self.assertEqual(set(r["kinds"]), {"Seat", "Garrison", "Farms", "Mine", "Caravans", "Walls"})
        for k in r["kinds"].values():
            self.shape(k, KIND3, "kind")
        self.assertEqual(r["kinds"]["Walls"]["type"], "walls")
        self.assertIn("Gargoyle", r["kinds"]["Walls"]["fight"])
        # every site the engine lists is on the map with its fight tier, as a site (not a piece)
        sites = [a for h in r["hexes"] for a in h["assets"]]
        self.assertEqual(len(sites), 18)
        self.assertTrue(all(a["type"] in ("seat", "garrison", "works", "walls") and 1 <= a["tier"] <= 3 for a in sites))
        self.assertTrue(all("hp" not in a for a in sites))
        # rumours from a hex: the engine's, with no site ids; the goal in words
        heard = r["rumours"]["A5"]
        self.assertTrue(any("Gnomes" in x and "raid the Elves" in x and "standing" in x for x in heard), heard)
        self.assertFalse(any(re.search(r"\bs\d+\b", x) for x in heard), heard)
        self.assertFalse(any("*" in x for x in heard), heard)
        self.assertFalse(any(re.search(r"\bs\d+\b", x) for x in r["nextWords"]), r["nextWords"])
        self.assertIn("take", r["goalWords"])
        self.assertEqual(r["dissidents"], [])
        tower = next(f for f in r["factions"] if f["tower"])
        self.assertEqual((tower["tierName"], tower["renown"], tower["hold"], tower["maxHold"]), ("Hermit", 0, 3, 3))
        self.assertEqual(r["hexNames"]["B5"], "the tower's mountains")
        ru = self.doc("game", "rules")
        self.assertEqual([x["id"] for x in ru["sections"]],
                         ["cast", "death", "campaign", "sites", "goals", "standing", "purse", "missions", "goal", "rulers", "report"])
        self.assertIn("Garrison", ru["sections"][3]["md"])

    def test_orders_auto(self):
        self.new()
        self.t("state", self.d, "--awaiting", "orders", "--prompt", "Month 1's orders")
        o = self.doc("game", "state")["awaiting"]["orders"]
        self.assertEqual(o["version"], 3)
        self.assertEqual(o["hexes"][0], {"id": "B5", "name": "the tower's mountains", "days": 0})
        here = [(m["type"], m["target"], m["turn"]) for m in o["missions"] if m["hex"] == "B5"]
        self.assertEqual(here, [("delve", "floor 1", "--delve")])
        a5 = {m["type"]: m for m in o["missions"] if m["hex"] == "A5"}
        self.assertEqual(a5["strike"]["turn"], "--strike s14")
        self.assertRegex(a5["strike"]["label"], r"^Strike the Gnomes' Garrison in A5 \((Low|Moderate|High), .*; 2 marks off their goal\)$")
        self.assertEqual(a5["contact"]["turn"], "--contact Gnomes")
        self.assertIn("Persuasion DC 15", a5["contact"]["label"])
        robs = [m for m in o["missions"] if m["type"] == "rob"]
        self.assertTrue(robs and all(m["turn"].startswith("--rob s") for m in robs))
        aids = [m for m in o["missions"] if m["type"] == "aid"]
        self.assertTrue(aids and all(m["turn"] == f"--aid {m['target']}" for m in aids))
        self.assertTrue(all(m["days"] >= 0 for m in o["missions"]))
        goals = {g["goal"]: g for g in o["goals"]}
        self.assertEqual((goals["take:A5"]["size"], goals["take:A5"]["target"]), (5, "Gnomes"))
        self.assertEqual(goals["ally:Humans"]["size"], 3)
        self.assertFalse([g for g in goals if g.startswith("topple:")])  # no dissident named yet
        self.assertNotIn("take:B5", goals)  # the tower's own hex
        self.assertNotIn("drop", goals)
        self.assertIsNone(o["goal"])
        for g in o["goals"]:
            self.assertRegex(g["goal"], T.GOAL3)
        self.assertEqual([(a["action"], a["cost"], a["affordable"]) for a in o["actions"]],
                         [("--buy works@B5", 300, False)])  # Hermit: no garrison or walls yet; 100 GP
        for a in o["actions"]:
            self.assertRegex(a["action"], T.ACTION3)
        self.assertEqual(o["realms"][:2], ["Elves", "Gnomes"])
        self.assertEqual(o["funds"]["treasury"], 100)
        # with a goal declared and a dissident named, the form offers keep (null), drop and topple
        self.turn("--at", "B5", "--delve", "--goal", "take:A5")
        st = json.loads((self.d / "realms.json").read_text())
        st["realms"]["Humans"]["dissident"] = {"name": "Edda", "hex": "D3"}
        (self.d / "realms.json").write_text(json.dumps(st))
        self.t("state", self.d, "--awaiting", "orders", "--prompt", "Month 2's orders", "--realm")
        o = self.doc("game", "state")["awaiting"]["orders"]
        self.assertEqual(o["goal"], {"goal": "take:A5", "text": "take A5 from the Gnomes", "marks": 0, "size": 5})
        goals = {g["goal"]: g for g in o["goals"]}
        self.assertNotIn("take:A5", goals)
        self.assertIn("drop", goals)
        self.assertEqual(goals["topple:Humans"]["size"], 6)
        self.assertIn("Edda", goals["topple:Humans"]["label"])
        self.assertEqual(self.doc("game", "realm")["dissidents"], [{"realm": "Humans", "name": "Edda", "hex": "D3"}])

    def test_orders_move_validated_as_v3(self):
        hexes = {f"{c}{r}" for c in "ABCD" for r in range(1, 6)}
        good = {"v": 1, "seq": 1, "at": "2026-10-26T09:00:00Z", "kind": "orders", "travel": "A5",
                "mission": {"type": "aid", "target": "Humans"}, "goal": "take:A5",
                "actions": ["--buy works@B5", "--buy mend", "--back Humans", "--set Humans=take:C4"],
                "give": {"realm": "Humans", "gp": 200}, "plan": "Weakest neighbour first."}
        self.assertEqual(T.validate_move(good, hexes, 3), ([], []))
        self.assertEqual(T.validate_move({**good, "goal": None, "actions": []}, hexes, 3), ([], []))
        self.assertIn("goal take:A5", T.move_words(good))
        self.assertIn("purse --buy works@B5 --buy mend", T.move_words(good))
        bad = [({**good, "goal": "take:Z9"}, "orders.goal"),
               ({**good, "goal": "raid:Humans"}, "orders.goal"),
               ({**good, "actions": "--buy mend"}, "orders.actions"),
               ({**good, "actions": ["--buy farms@B5"]}, "orders.actions"),
               ({**good, "actions": ["rm -rf /"]}, "orders.actions"),
               ({**good, "actions": ["--buy mend", "--buy mend"]}, "repeats"),
               ({**good, "actions": ["--back Humans", "--hinder Elves"]}, "one back or hinder"),
               ({**good, "mission": {"type": "seize", "target": "A5"}}, "orders.mission"),
               ({k: v for k, v in good.items() if k not in ("goal", "actions")}, "orders.goal is missing"),
               ({k: v for k, v in good.items() if k not in ("goal", "actions")}, "orders.actions is missing")]
        for m, want in bad:
            errs, _ = T.validate_move(m, hexes, 3)
            self.assertTrue(any(want in e for e in errs), f"{m} → {errs}")
        # a v2 move against a v2 world still validates as before; the v3 keys are ignored fields there
        v2 = {**good, "action": "buy:farms@B5"}
        del v2["goal"]
        del v2["actions"]
        v2["mission"] = {"type": "delve", "target": "floor 2"}
        self.assertEqual(T.validate_move(v2, hexes)[0], [])
        _, warn = T.validate_move({**v2, "goal": None, "actions": []}, hexes)
        self.assertEqual(warn, ["ignored fields: actions, goal"])
        # the moves verb reads a v3 move and words it from the form's labels
        self.new()
        self.t("state", self.d, "--awaiting", "orders", "--prompt", "Orders")
        self.t("sent", self.d)
        mv = {**good, "travel": "B5", "mission": {"type": "delve", "target": "floor 1"},
              "actions": ["--buy works@B5"], "give": None}
        out, _ = self.t("moves", self.d, "--file", self.md("m.json", json.dumps([mv])))
        self.assertIn("goal take:A5", out)
        text = T.Camp(self.d).page["moves"]["m0001"]["text"]
        self.assertIn("the goal: Take A5 from the Gnomes (a clock of 5)", text)
        self.assertIn("the purse: Mine at B5", text)
        self.assertIn("Delve floor 1 under B5", text)
        with self.assertRaises(SystemExit):
            self.t("moves", self.d, "--file", self.md("m2.json", json.dumps([{**v2, "seq": 2}])))

    def test_tower_line_and_domain_section(self):
        self.new()
        md = (self.d / "state.md").read_text()
        self.assertIn("## Domain (Realms v3)", md)
        self.assertIn("- Tower: Hermit (tier 0, Renown 0) · Hold 3 of 3 · 100 GP (+10 GP a month) · hexes B5 · goal none", md)
        self.assertIn("- Allies: none · Enemies: nobody", md)
        self.assertNotIn("Cunning", md)
        self.turn("--at", "A5", "--strike", "s14", "--goal", "take:A5", "--plan", "weakest neighbour first")
        f = self.md("d.md", "---\nkind: domain\ntitle: Month 1 · the world's turn\n---\nThe clocks moved.\n\n"
                    "### What happened\n- who=tower: The tower's take A5 from the Gnomes: 2 of 5.\n"
                    "- n=2: Morten struck the Gnomes' Garrison in A5.\n- who=Elves: The Elves rolled a 4: 1 of 4.\n"
                    "### The tower now\n- Goal: none → take A5 from the Gnomes, 2 of 5\n"
                    "### Next month\n- Open: Strike the garrison again.\n")
        self.t("section", self.d, "--file", f)
        self.t("realm", self.d)
        d = json.loads((self.d / "story" / "s0001.json").read_text())["domain"]
        self.shape(d, DOMAIN, "domain")
        self.assertEqual([(h["n"], h["who"], h["label"]) for h in d["happened"]],
                         [(None, "tower", None), (2, "tower", None), (None, "Elves", "good")])
        self.assertEqual(d["happened"][1]["to"], "A5")
        self.assertTrue(d["log"])
        md = (self.d / "state.md").read_text()
        self.assertIn("· goal take A5 from the Gnomes, 2 of 5", md)
        r = self.doc("game", "realm")
        self.assertEqual([e["text"] for e in r["eventsWords"]][:2],
                         ["The tower's goal: take A5 from the Gnomes (declared, clock 5).",
                          "Morten struck the Gnomes' Garrison in A5: won: their raid the Elves 0 → 0 of 2; standing -1, wary."])
        gn = next(x for x in r["factions"] if x["name"] == "Gnomes")
        self.assertEqual((gn["standing"], gn["standingWord"]), (-1, "wary"))
        bad = self.md("e.md", "---\nkind: domain\ntitle: x\n---\n### What happened\n- The Elves rolled.\n")
        with self.assertRaises(SystemExit):
            self.t("section", self.d, "--file", bad)

    def test_two_months_leak_nothing(self):
        """A v3 world hides nothing but its dice: two months played, projected and checked."""
        self.new()
        for month in range(2):
            self.turn("--at", "B5", "--delve")
            f = self.md("d.md", f"---\nkind: domain\ntitle: Month {month + 1} · the world's turn\n---\nThe world moved.\n")
            self.t("section", self.d, "--file", f)
            self.t("state", self.d, "--awaiting", "orders", "--prompt", "Orders", "--realm")
            self.t("sent", self.d)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check_table.main([str(self.d)]), 0, out.getvalue())
        rng = json.loads((self.d / "realms.json").read_text())["rng"]
        whole = "\n".join(p.read_text() for p in (self.d / "page" / "out").rglob("*.json"))
        self.assertNotIn(str(rng), whole)
        self.assertIn('"dissident"', whole)  # public in v3 (named by a won Contact; null until then)


class Playtest(Case):
    """What the table's two-month playtest (sessions/2026-10-25-table-playtest.md) fixed."""

    def test_new_with_a_fresh_sheet(self):
        (self.d / "morten.json").unlink()
        _, err = self.t("new", self.d, "--sheet", "fresh", "--hex", "B5")
        self.assertIn("fresh Wizard 3", err)
        m = self.doc("game", "morten")
        self.assertEqual((m["xp"], m["coins"]["on"], m["hp"]), (900, "47 GP 7 SP 5 CP", 20))
        self.shape(m, MORTEN, "game/morten")

    def test_fight_told_after_gets_an_hp_track(self):
        self.new()
        f = self.md("f.md", "---\nkind: fight\ntitle: Room 1.2 · 2 Warrior Infantry (CR 1/8 each)\n"
                    'foes: [{"name": "Warrior Infantry", "cr": "1/8", "ac": 13, "hp": 9, "maxHp": 9, '
                    '"speed": "6 sq (9 m)", "attacks": ["Spear +3, 1d6+1 piercing"], "notes": "", "count": 2}]\n'
                    "rounds: 3\nhpBefore: 20\n---\nCleared.\n\n### Trace\n"
                    "- R1 foe/attack: Warrior A stabs: 7 piercing dmg. Morten 20 → 13 HP.\n"
                    "- R2 morten/cast: Magic Missile: 9 force dmg. Warrior A 9 → 0 HP, dead.\n"
                    "- R3 morten/cast: Thunderwave: B dead.\n")
        self.t("section", self.d, "--file", f)
        s = json.loads(sorted((self.d / "story").glob("s*.json"))[-1].read_text())
        track = {t["name"]: t["hp"] for t in s["fight"]["hpTrack"]}
        self.assertEqual(track, {"Morten": [20, 13, 13, 13], "Warrior Infantry A": [9, 9, 0, 0],
                                 "Warrior Infantry B": [9, 9, 9, 0]})
        # nothing to go by in the trace: the start and the end, the rounds between unknown
        g = self.md("g.md", "---\nkind: fight\ntitle: Room 1.3 · Panther (CR 1/4)\n"
                    'foes: [{"name": "Panther", "cr": "1/4", "ac": 13, "hp": 13, "maxHp": 13, "speed": "10 sq", '
                    '"attacks": [], "notes": "", "count": 1}]\nrounds: 2\n---\nOne blast.\n')
        self.t("section", self.d, "--file", g)
        s = json.loads(sorted((self.d / "story").glob("s*.json"))[-1].read_text())
        self.assertEqual([t["hp"] for t in s["fight"]["hpTrack"]], [[20, None, 20], [13, None, 0]])

    def test_beat_hp_moves_the_hud_and_the_sheet(self):
        self.new()
        self.t("open", self.d, "--kind", "fight", "--title", "Room 2.4 · Darkmantle (CR 1/2)",
               "--foes", json.dumps(FOES["darkmantle"]))
        self.t("sent", self.d)
        out, _ = self.t("beat", self.d, "--round", 1, "--text", "A crit: 10 dmg.", "--hp", "10/20")
        got = [(w["collection"], w["doc_id"]) for w in self.batches(out)[0]["writes"]]
        self.assertEqual(got[0][0], "live")
        self.assertIn(("game", "state"), got)
        self.assertEqual(self.doc("game", "state")["hud"]["hp"], 10)
        self.assertEqual(self.doc("game", "morten")["hp"], 10)
        self.t("sent", self.d)
        out, _ = self.t("beat", self.d, "--round", 2, "--text", "A miss.", "--hp", "10/20")
        self.assertEqual(len(self.batches(out)[0]["writes"]), 1, "HP unchanged: the beat alone")

    def test_words_and_small_verbs(self):
        self.new()
        self.t("state", self.d, "--awaiting", "orders", "--prompt", "Orders")
        self.t("sent", self.d)
        mv = [{"v": 1, "seq": 1, "at": "2026-10-25T09:00:00Z", "kind": "orders", "travel": "B5",
               "mission": {"type": "delve", "target": "floor 1"}, "action": None, "give": None, "plan": "Safe XP."},
              {"v": 1, "seq": 2, "at": "2026-10-25T09:01:00Z", "kind": "play", "scope": "stop", "text": "Fire Bolt them."}]
        self.t("moves", self.d, "--file", self.md("m.json", json.dumps(mv)))
        self.assertEqual(T.Camp(self.d).page["moves"]["m0001"]["text"],
                         "Orders: to the tower's desert (B5) · Delve floor 1 under B5 (cleared) · the tower saves. Safe XP.")
        self.assertEqual(T.Camp(self.d).page["moves"]["m0002"]["text"], "Stop after this: Fire Bolt them.")
        _, err = self.t("morten", self.d, "--condition", "-Prone", "--condition", "+Poisoned", "--habit", "Purse home.")
        self.assertIn("condition Poisoned", err)
        self.assertIn("habit added", err)
        f = self.md("r.md", "---\nkind: rest\ntitle: A rest\n---\nRested.\n")
        self.t("section", self.d, "--file", f, "--answers", "none")
        self.assertEqual(sorted(T.Camp(self.d).page["moves"]), ["m0001", "m0002"], "--answers none answers nothing")
        self.t("sent", self.d)
        self.t("realm", self.d)
        _, err = self.t("realm", self.d)
        self.assertIn("unchanged", err)

    def test_rules_and_next_month_in_words(self):
        self.new()
        rules = self.doc("game", "rules")
        for s in rules["sections"]:
            self.assertNotRegex(s["md"], r"`|python3|\.json\b|dnd-crunch/", s["id"])
        realm = self.doc("game", "realm")
        self.assertEqual(len(realm["nextWords"]), len(realm["report"]["next"]))
        for ln in realm["nextWords"]:
            self.assertNotRegex(ln, r"\ba\d+\b|\bT\d\b|\(L\d|1 = encounter", ln)
        self.assertEqual(realm["dissidents"], [])
        self.assertNotIn("the Goblinkind's", json.dumps(self.doc("game", "state")))

    def test_roll_label_after_the_fact(self):
        roll = [sys.executable, str(HERE / "roll.py"), "--keep", str(self.d)]
        subprocess.run(roll + ["1d20+5", "--vs", "DC 11", "1d20+4"], capture_output=True, check=True)
        subprocess.run(roll + ["--label", "fizzle", "--label", "hit:AC 14"], capture_output=True, check=True)
        kept = [json.loads(x) for x in (self.d / "live" / "rolls.jsonl").read_text().splitlines()]
        self.assertEqual([(d["result"], d["vs"]) for d in kept], [("fizzle", "DC 11"), ("hit", "AC 14")])
        bad = subprocess.run(roll + ["--label", "hit", "--label", "hit", "--label", "hit"], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
