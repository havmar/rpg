#!/usr/bin/env python3
"""Tests for realms3.py (Realms v3). Run: python3 dnd-crunch/tools/test_realms3.py"""
import argparse
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import realms3 as R  # noqa: E402

SCRIPT = HERE / "realms3.py"


def world(seed=7):
    return R.generate(seed)


def orders(**kw):
    o = dict(R.PASSIVE)
    o.update(buy=[], give=[], plan=[], set=[])
    o.update(kw)
    return argparse.Namespace(**o)


def hold_hex(st, h, name):
    """Give hex h to name (test setup), keeping the derived lists in step."""
    st["hexes"][h]["holder"] = name
    R.sync(st)


def fixed_die(t, *faces):
    """Make t.d() return the given faces in turn (the last one for ever after)."""
    seq = list(faces)

    def d(n):
        return seq.pop(0) if len(seq) > 1 else seq[0]
    t.d = d


class RollTable(unittest.TestCase):
    def setUp(self):
        self.st = world()
        self.t = R.Turn(self.st)
        self.name = next(iter(self.st["realms"]))
        self.f = self.st["realms"][self.name]
        self.f["goal"] = self.t.new_goal("squeeze")   # no target: no modifiers
        self.f["goal"]["marks"] = 2

    def roll(self, die):
        fixed_die(self.t, die)
        return self.t.roll_goal(self.name)

    def test_natural_1_is_a_setback(self):
        die, total, n, word = self.roll(1)
        self.assertEqual((n, word), (-1, "setback"))
        self.assertEqual(self.f["goal"]["marks"], 1)

    def test_setback_never_below_zero(self):
        self.f["goal"]["marks"] = 0
        self.roll(1)
        self.assertEqual(self.f["goal"]["marks"], 0)

    def test_2_is_nothing(self):
        die, total, n, _ = self.roll(2)
        self.assertEqual(n, 0)
        self.assertEqual(self.f["goal"]["marks"], 2)

    def test_3_to_5_is_one_mark(self):
        for d in (3, 4, 5):
            self.f["goal"]["marks"] = 0
            _, _, n, _ = self.roll(d)
            self.assertEqual(n, 1, d)

    def test_6_is_two_marks(self):
        self.f["goal"]["marks"] = 0
        _, _, n, _ = self.roll(6)
        self.assertEqual(n, 2)
        self.assertEqual(self.f["goal"]["marks"], 2)

    def test_marks_stop_at_the_clock(self):
        self.f["goal"]["marks"] = 1
        self.roll(6)
        self.assertEqual(self.f["goal"]["marks"], 2)

    def test_force_modifier(self):
        other = [n for n in self.st["realms"] if n != self.name][0]
        self.f["force"], self.st["realms"][other]["force"] = 4, 2
        self.f["goal"] = self.t.new_goal("press", other)
        _, total, n, _ = self.roll(5)
        self.assertEqual((total, n), (6, 2))
        self.f["force"], self.st["realms"][other]["force"] = 2, 4
        self.f["goal"] = self.t.new_goal("press", other)
        _, total, n, _ = self.roll(3)
        self.assertEqual((total, n), (2, 0))

    def test_garrison_and_walls_modifiers(self):
        other = [n for n in self.st["realms"] if n != self.name][0]
        h = R.sites_of(self.st, other, kind="garrison")[0]["hex"]
        self.f["force"] = self.st["realms"][other]["force"]
        self.f["goal"] = self.t.new_goal("take", other, h)
        _, total, n, _ = self.roll(4)
        self.assertEqual((total, n), (3, 1))
        R.add_site(self.st, other, "walls", h)
        _, total, n, _ = self.roll(4)
        self.assertEqual((total, n), (2, 0))

    def test_give_and_back_modifiers(self):
        self.t.gave[self.name] = 200
        _, total, n, _ = self.roll(5)
        self.assertEqual((total, n), (6, 2))
        self.t.gave[self.name] = 199
        self.t.backed[self.name] = -1
        _, total, n, _ = self.roll(3)
        self.assertEqual((total, n), (2, 0))
        self.t.backed[self.name] = 1
        _, total, n, _ = self.roll(5)
        self.assertEqual((total, n), (6, 2))

    def test_natural_1_with_a_plus_is_still_a_setback(self):
        self.t.backed[self.name] = 1
        _, total, n, word = self.roll(1)
        self.assertEqual((total, word), (2, "setback"))


class Picker(unittest.TestCase):
    def setUp(self):
        self.st = world()
        self.t = R.Turn(self.st)

    def bad(self, tag):
        for n, f in self.st["realms"].items():
            f["leader"]["label"], f["leader"]["tag"] = "bad", tag
            f["standing"] = 0
            return n, f

    def test_break_the_tower_at_minus_one(self):
        n, f = self.bad("Raider")
        f["standing"] = -1
        self.assertEqual(self.t.pick_goal(n)["kind"], "break_tower")

    def test_break_the_tower_at_warden_on_4_plus(self):
        n, f = self.bad("Raider")
        T = self.st["tower"]
        for h in [h for h in R.HEXES if h != self.st["warded"]][:5]:   # Renown 5: Warden
            hold_hex(self.st, h, R.TOWER)
        self.assertEqual(R.tier_now(self.st), R.WARDEN)
        fixed_die(self.t, 3)
        self.assertNotEqual(self.t.pick_goal(n)["kind"], "break_tower")
        fixed_die(self.t, 4)
        self.assertEqual(self.t.pick_goal(n)["kind"], "break_tower")

    def test_an_ally_never_breaks_the_tower(self):
        n, f = self.bad("Raider")
        f["standing"] = 2
        self.assertNotEqual(self.t.pick_goal(n)["kind"], "break_tower")

    def test_take_back_comes_before_the_tag(self):
        n, f = self.bad("Raider")
        other = [x for x in self.st["realms"] if x != n][0]
        lost = f["hexes"][-1]
        hold_hex(self.st, lost, other)
        f["force"] = self.st["realms"][other]["force"]
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["hex"], g["target"]), ("take", lost, other))
        f["force"] = self.st["realms"][other]["force"] - 1   # too weak: the tag's goal instead
        self.assertEqual(self.t.pick_goal(n)["kind"], "raid")

    def test_court_the_tower_at_lord(self):
        n, f = self.bad("Steward")
        f["leader"]["label"] = "good"
        f["standing"] = 1
        for h in [h for h in R.HEXES if h != self.st["warded"]][:2]:
            hold_hex(self.st, h, R.TOWER)
        self.assertEqual(R.tier_now(self.st), R.LORD)
        fixed_die(self.t, 4)
        self.assertEqual(self.t.pick_goal(n)["kind"], "court")
        fixed_die(self.t, 3)
        self.assertEqual(self.t.pick_goal(n)["kind"], "fortify")

    def test_conqueror_takes_the_deepest_open_border_hex(self):
        n, f = self.bad("Conqueror")
        g = self.t.pick_goal(n)
        self.assertEqual(g["kind"], "take")
        seats = {x["seat"] for x in self.st["realms"].values()}
        self.assertNotIn(g["hex"], seats)
        self.assertNotIn(g["hex"], f["hexes"])
        self.assertTrue(any(g["hex"] in R.nbrs(h) for h in f["hexes"]))

    def test_raider_raids_the_richest_neighbour(self):
        n, f = self.bad("Raider")
        ns = [x for x in R.neighbours_of(self.st, n) if x != R.TOWER]
        for x in ns:
            self.st["realms"][x]["treasury"] = 100
        self.st["realms"][ns[-1]]["treasury"] = 5000
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["target"]), ("raid", ns[-1]))

    def test_raider_raids_the_tower_when_it_is_richest(self):
        n, f = self.bad("Raider")
        for x in R.neighbours_of(self.st, n):
            if x != R.TOWER:
                self.st["realms"][x]["treasury"] = 0
        hold_hex(self.st, [h for h in R.nbrs(f["hexes"][0]) if h not in f["hexes"]][0], R.TOWER)
        self.st["tower"]["treasury"] = 9000
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["target"]), ("raid", R.TOWER))

    def test_slaver_presses_the_weakest_neighbour_above_force_1(self):
        n, f = self.bad("Slaver")
        ns = [x for x in R.neighbours_of(self.st, n) if x != R.TOWER]
        for x in ns:
            self.st["realms"][x]["force"] = 1
        self.assertNotEqual(self.t.pick_goal(n)["kind"], "press")
        self.st["realms"][ns[0]]["force"] = 2
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["target"]), ("press", ns[0]))

    def test_tyrant_cycle(self):
        n, f = self.bad("Tyrant")
        f["last"] = None
        self.assertEqual(self.t.pick_goal(n)["kind"], "squeeze")
        f["last"] = "squeeze"
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["hex"]), ("fortify", f["seat"]))
        R.add_site(self.st, n, "walls", f["seat"])
        f["last"] = "squeeze"
        self.assertEqual(self.t.pick_goal(n)["kind"], "raise")

    def test_steward_and_liberator(self):
        n, f = self.bad("Steward")
        f["leader"]["label"] = "good"
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["hex"]), ("fortify", f["seat"]))
        f["leader"]["tag"] = "Liberator"
        f["force"] = 5
        ns = [x for x in R.neighbours_of(self.st, n) if x != R.TOWER]
        for x in ns:
            self.st["realms"][x]["leader"]["label"] = "bad"
            self.st["realms"][x]["force"] = 2
        g = self.t.pick_goal(n)
        self.assertEqual(g["kind"], "break")
        self.assertIn(g["target"], ns)

    def test_fallback(self):
        n, f = self.bad("Slaver")
        for x in self.st["realms"].values():
            x["force"] = 1
        f["treasury"] = 10000
        self.assertEqual(self.t.pick_goal(n)["kind"], "raise")
        f["treasury"] = 0
        self.assertEqual(self.t.pick_goal(n)["kind"], "fortify")
        R.add_site(self.st, n, "walls", f["seat"])
        self.assertEqual(self.t.pick_goal(n)["kind"], "squeeze")

    def test_a_landless_realm_takes_back(self):
        n, f = self.bad("Raider")
        other = [x for x in self.st["realms"] if x != n][0]
        for h in list(f["hexes"]):
            hold_hex(self.st, h, other)
        f["seat"] = None
        f["force"] = 1
        self.st["realms"][other]["force"] = 5
        g = self.t.pick_goal(n)
        self.assertEqual((g["kind"], g["target"]), ("take", other))


class Missions(unittest.TestCase):
    def setUp(self):
        self.st = world()
        self.name = next(iter(self.st["realms"]))
        self.f = self.st["realms"][self.name]
        self.gar = R.sites_of(self.st, self.name, kind="garrison")[0]
        self.seat = R.sites_of(self.st, self.name, kind="seat")[0]
        self.f["goal"]["marks"] = 3
        self.f["goal"]["size"] = 4

    def test_strike_takes_two_and_gives_two(self):
        T = self.st["tower"]
        T["goal"] = {"kind": "take", "target": self.name, "hex": self.gar["hex"], "size": 5,
                     "marks": 0, "since": 1, "waits": 0}
        t = R.Turn(self.st)
        t.land(orders(at=self.gar["hex"], strike=self.gar["id"]))
        self.assertEqual(self.f["goal"]["marks"], 1)
        self.assertEqual(T["goal"]["marks"], 2)
        self.assertEqual(self.f["standing"], 0 - 1 if self.f["leader"]["label"] == "bad" else 0)

    def test_strike_on_the_seat_costs_two_standing(self):
        before = self.f["standing"]
        t = R.Turn(self.st)
        t.land(orders(at=self.seat["hex"], strike=self.seat["id"]))
        self.assertEqual(self.f["standing"], max(-2, before - 2))

    def test_strike_at_power_moves_three(self):
        for h in [h for h in R.HEXES if h != self.st["warded"] and h not in self.f["hexes"]][:9]:
            hold_hex(self.st, h, R.TOWER)
        self.assertEqual(R.tier_now(self.st), R.POWER)
        t = R.Turn(self.st)
        t.land(orders(at=self.gar["hex"], strike=self.gar["id"]))
        self.assertEqual(self.f["goal"]["marks"], 0)

    def test_strike_needs_morten_there(self):
        t = R.Turn(self.st)
        with self.assertRaises(R.Bad):
            t.land(orders(strike=self.gar["id"]))

    def test_one_mission_a_month(self):
        t = R.Turn(self.st)
        with self.assertRaises(R.Bad):
            t.land(orders(at=self.gar["hex"], strike=self.gar["id"], delve=True))

    def test_rob(self):
        works = R.sites_of(self.st, self.name, kind="works")[0]
        self.f["treasury"], self.f["force"] = 250, 3
        T = self.st["tower"]
        t = R.Turn(self.st)
        t.land(orders(at=works["hex"], rob=works["id"]))
        self.assertEqual(self.f["treasury"], 0)
        self.assertEqual(T["treasury"], 100 + 250)

    def test_aid(self):
        self.f["goal"] = {"kind": "fortify", "target": None, "hex": self.f["seat"], "size": 3,
                          "marks": 0, "since": 1, "waits": 0}
        self.f["standing"] = 0
        self.st["tower"]["goal"] = {"kind": "ally", "target": self.name, "hex": None, "size": 3,
                                    "marks": 0, "since": 1, "waits": 0}
        t = R.Turn(self.st)
        t.land(orders(at=self.f["seat"], aid=self.name))
        self.assertEqual(self.f["goal"]["marks"], 2)
        self.assertEqual(self.f["standing"], 1)
        self.assertEqual(self.st["tower"]["goal"]["marks"], 2)
        with self.assertRaises(R.Bad):   # not in the aimed hex
            R.Turn(self.st).land(orders(at=self.gar["hex"], aid=self.name))

    def test_contact(self):
        self.f["standing"] = 0
        t = R.Turn(self.st)
        t.land(orders(at=self.f["seat"], contact=self.name))
        self.assertEqual(self.f["standing"], 1)
        self.assertIsNotNone(self.f["dissident"])
        self.f["standing"] = -2
        with self.assertRaises(R.Bad):
            R.Turn(self.st).land(orders(at=self.f["seat"], contact=self.name))

    def test_contact_dc(self):
        self.f["leader"]["label"] = "bad"
        self.f["standing"] = -1
        self.assertEqual(R.contact_dc(self.st, self.name), 17)
        self.f["leader"]["label"] = "good"
        self.f["standing"] = 1
        self.assertEqual(R.contact_dc(self.st, self.name), 10)
        self.f["squeeze_until"] = self.st["month"] + 2
        self.assertEqual(R.contact_dc(self.st, self.name), 14)


class TowerGoal(unittest.TestCase):
    def setUp(self):
        self.st = world()
        self.name = next(iter(self.st["realms"]))
        self.f = self.st["realms"][self.name]
        self.T = self.st["tower"]

    def test_take_fires(self):
        h = R.sites_of(self.st, self.name, kind="garrison")[0]["hex"]
        self.f["standing"] = 1
        self.T["goal"] = {"kind": "take", "target": self.name, "hex": h, "size": 5, "marks": 5,
                          "since": 1, "waits": 0}
        t = R.Turn(self.st)
        t.tower_goal()
        self.assertEqual(self.st["hexes"][h]["holder"], R.TOWER)
        self.assertEqual(R.sites_of(self.st, hex=h)[0]["owner"], R.TOWER)
        self.assertEqual(self.f["standing"], -1)
        self.assertIsNone(self.T["goal"])
        self.assertEqual(R.renown_of(self.st), 1)

    def test_take_of_a_seat_moves_the_seat(self):
        h = self.f["seat"]
        self.T["goal"] = {"kind": "take", "target": self.name, "hex": h, "size": 5, "marks": 5,
                          "since": 1, "waits": 0}
        R.Turn(self.st).tower_goal()
        self.assertNotEqual(self.f["seat"], h)
        self.assertIn(self.f["seat"], self.f["hexes"])
        self.assertEqual(R.site_at(self.st, self.f["seat"], "seat", self.name)["kind"], "seat")
        self.assertIsNone(R.site_at(self.st, h, "seat"))

    def test_ally_fires(self):
        self.f["standing"] = 1
        self.T["goal"] = {"kind": "ally", "target": self.name, "hex": None, "size": 3, "marks": 3,
                          "since": 1, "waits": 0}
        R.Turn(self.st).tower_goal()
        self.assertEqual(self.f["standing"], 2)
        self.assertTrue(R.is_ally(self.f))
        self.assertEqual(R.renown_of(self.st), 1)

    def test_topple_fires(self):
        self.f["dissident"] = {"name": "Edda", "hex": self.f["seat"]}
        self.f["leader"]["label"], self.f["leader"]["tag"] = "bad", "Tyrant"
        self.f["treasury"] = 777
        self.T["goal"] = {"kind": "topple", "target": self.name, "hex": self.f["seat"], "size": 6,
                          "marks": 6, "since": 1, "waits": 0}
        R.Turn(self.st).tower_goal()
        self.assertEqual(self.f["leader"]["name"], "Edda")
        self.assertEqual(self.f["leader"]["label"], "good")
        self.assertIn(self.f["leader"]["tag"], R.GOOD)
        self.assertEqual(self.f["treasury"], 777)
        self.assertEqual(self.f["standing"], 2)
        self.assertIsNotNone(self.f["goal"])
        self.assertEqual(self.f["goal"]["marks"], 0)
        self.assertEqual(self.T["toppled"], 1)
        self.assertEqual(R.renown_of(self.st), 3)

    def test_allies_add_a_mark(self):
        other = [n for n in self.st["realms"] if n != self.name][0]
        self.st["realms"][other]["standing"] = 2
        self.T["goal"] = {"kind": "take", "target": self.name, "hex": self.f["hexes"][-1], "size": 5,
                          "marks": 0, "since": 1, "waits": 0}
        R.Turn(self.st).tower_goal()
        self.assertEqual(self.T["goal"]["marks"], 1)

    def test_declaring_a_goal(self):
        t = R.Turn(self.st)
        h = self.f["hexes"][-1]
        t.set_goal(f"take:{h}")
        self.assertEqual(self.T["goal"]["size"], 2 + self.f["force"])
        R.add_site(self.st, self.name, "walls", h)
        t.set_goal("drop")
        t.set_goal(f"take:{h}")
        self.assertEqual(self.T["goal"]["size"], 4 + self.f["force"])
        with self.assertRaises(R.Bad):
            t.set_goal(f"topple:{self.name}")   # no dissident
        with self.assertRaises(R.Bad):
            t.set_goal(f"take:{self.st['warded']}")


class RealmGoals(unittest.TestCase):
    def setUp(self):
        self.st = world()
        self.name = next(iter(self.st["realms"]))
        self.f = self.st["realms"][self.name]
        self.T = self.st["tower"]

    def full(self, kind, target=None, hex=None):
        t = R.Turn(self.st)
        g = t.new_goal(kind, target, hex)
        g["marks"] = g["size"]
        self.f["goal"] = g
        return t

    def test_raid_on_the_tower_is_capped_at_half(self):
        self.T["treasury"] = 300
        self.f["force"] = 5
        t = self.full("raid", R.TOWER)
        t.fire(self.name)
        self.assertEqual(self.T["treasury"], 150)
        self.f["treasury"] += 0
        self.T["treasury"] = 2000
        t = self.full("raid", R.TOWER)
        before = self.f["treasury"]
        t.fire(self.name)
        self.assertEqual(self.T["treasury"], 1500)
        self.assertEqual(self.f["treasury"], before + 500)

    def test_raid_on_a_realm_takes_what_it_holds(self):
        other = [n for n in self.st["realms"] if n != self.name][0]
        self.st["realms"][other]["treasury"] = 120
        self.f["force"] = 3
        t = self.full("raid", other)
        t.fire(self.name)
        self.assertEqual(self.st["realms"][other]["treasury"], 0)

    def test_break_the_tower_takes_a_hold_box(self):
        self.T["treasury"] = 400
        self.f["standing"] = 0
        t = self.full("break_tower", R.TOWER)
        t.fire(self.name)
        self.assertEqual((self.T["hold"], self.T["treasury"], self.f["standing"]), (2, 200, -1))

    def test_hold_at_zero_takes_a_hex(self):
        extra = [h for h in R.HEXES if h != self.st["warded"] and h not in self.f["hexes"]][0]
        hold_hex(self.st, extra, R.TOWER)
        self.T["hold"] = 0
        t = self.full("break_tower", R.TOWER)
        t.fire(self.name)
        self.assertEqual(self.st["hexes"][extra]["holder"], self.name)
        self.assertEqual(self.st["hexes"][self.st["warded"]]["holder"], R.TOWER)
        self.assertEqual(self.T["hold"], 0)

    def test_the_warded_hex_is_never_taken(self):
        self.T["hold"] = 0
        t = self.full("break_tower", R.TOWER)
        t.fire(self.name)
        self.assertEqual(self.st["hexes"][self.st["warded"]]["holder"], R.TOWER)

    def test_fortify_waits_for_the_price(self):
        self.f["treasury"] = 100
        t = self.full("fortify", None, self.f["seat"])
        res = t.fire(self.name)
        self.assertIn("waits", res)
        self.assertEqual(self.f["goal"]["waits"], 300)
        self.f["treasury"] = 300
        t.fire(self.name)
        self.assertTrue(R.walled(self.st, self.f["seat"]))
        self.assertEqual(self.f["treasury"], 0)

    def test_raise_and_press(self):
        self.f["force"], self.f["treasury"] = 2, 1000
        t = self.full("raise")
        t.fire(self.name)
        self.assertEqual((self.f["force"], self.f["treasury"]), (3, 400))
        other = [n for n in self.st["realms"] if n != self.name][0]
        self.st["realms"][other]["force"] = 1
        self.f["force"] = 5
        t = self.full("press", other)
        t.fire(self.name)
        self.assertEqual((self.f["force"], self.st["realms"][other]["force"]), (5, 1))

    def test_take_by_a_realm(self):
        other = [n for n in self.st["realms"] if n != self.name][0]
        h = R.sites_of(self.st, other, kind="works")[0]["hex"]
        t = self.full("take", other, h)
        t.fire(self.name)
        self.assertEqual(self.st["hexes"][h]["holder"], self.name)
        self.assertEqual(R.site_at(self.st, h, "works")["owner"], self.name)

    def test_court(self):
        self.f["standing"] = 0
        t = self.full("court", R.TOWER)
        t.fire(self.name)
        self.assertEqual(self.f["standing"], 1)

    def test_goal_dropped_when_its_target_is_gone(self):
        other = [n for n in self.st["realms"] if n != self.name][0]
        self.st["realms"][other]["force"] = 1
        self.f["goal"] = R.Turn(self.st).new_goal("press", other)
        t = R.Turn(self.st)
        self.assertIsNotNone(t.gone(self.name))
        t.world()
        self.assertNotEqual((self.f["goal"]["kind"], self.f["goal"]["target"]), ("press", other))

    def test_old_goals_are_dropped(self):
        self.st["month"] = R.GOAL_MONTHS
        for f in self.st["realms"].values():
            f["goal"]["since"] = R.GOAL_MONTHS   # fresh
        self.f["goal"]["since"] = 1
        t = R.Turn(self.st)
        t.cleanup()
        self.assertEqual(self.f["goal"]["since"], R.GOAL_MONTHS)
        self.assertEqual(t.stats["drop_time"], 1)


class Standing(unittest.TestCase):
    def test_plus_one_never_lifts_past_friendly(self):
        st = world()
        n = next(iter(st["realms"]))
        f = st["realms"][n]
        f["standing"] = 1
        t = R.Turn(st)
        t.stand(n, 1, cap=1)
        self.assertEqual(f["standing"], 1)
        f["standing"] = -2
        t.stand(n, 1, cap=1)
        self.assertEqual(f["standing"], -1)

    def test_clamped(self):
        st = world()
        n = next(iter(st["realms"]))
        f = st["realms"][n]
        f["standing"] = -2
        R.Turn(st).stand(n, -2)
        self.assertEqual(f["standing"], -2)

    def test_give_raises_standing_once_a_month(self):
        st = world()
        n = next(iter(st["realms"]))
        f = st["realms"][n]
        f["standing"] = 0
        st["tower"]["treasury"] = 1000
        t = R.Turn(st)
        t.land(orders(give=[f"{n}=100", f"{n}=100"]))
        self.assertEqual(f["standing"], 1)
        self.assertEqual(f["treasury"], 200 + sum(st["hexes"][h]["level"] for h in f["hexes"]) * 10)


class RenownAndTiers(unittest.TestCase):
    def test_ladder(self):
        st = world()
        self.assertEqual((R.renown_of(st), R.tier_now(st)), (0, 0))
        free = [h for h in R.HEXES if h != st["warded"]]
        hold_hex(st, free[0], R.TOWER)
        self.assertEqual((R.renown_of(st), R.tier_now(st)), (1, 0))
        hold_hex(st, free[1], R.TOWER)
        self.assertEqual((R.renown_of(st), R.tier_now(st)), (2, 1))
        n = next(iter(st["realms"]))
        st["realms"][n]["standing"] = 2
        self.assertEqual(R.renown_of(st), 3)
        st["tower"]["toppled"] = 1
        self.assertEqual((R.renown_of(st), R.tier_now(st)), (5, 2))
        self.assertEqual(R.tier_for(9), 3)
        self.assertEqual(R.tier_for(13), 3)
        self.assertEqual(R.tier_for(14), 4)
        self.assertEqual(R.mark_step(st), 2)
        st["tower"]["toppled"] = 3
        self.assertEqual(R.mark_step(st), 3)

    def test_purse_actions_need_the_tier(self):
        st = world()
        st["tower"]["treasury"] = 5000
        t = R.Turn(st)
        with self.assertRaises(R.Bad):
            t.buy(f"garrison@{st['warded']}")
        with self.assertRaises(R.Bad):
            t.back(next(iter(st["realms"])), 1)
        free = [h for h in R.HEXES if h != st["warded"]][:2]
        for h in free:
            hold_hex(st, h, R.TOWER)
        t.buy(f"garrison@{free[0]}")
        self.assertIsNotNone(R.site_at(st, free[0], "garrison", R.TOWER))
        with self.assertRaises(R.Bad):
            t.buy(f"walls@{free[1]}")   # no garrison there
        t.buy(f"walls@{free[0]}")
        self.assertEqual(st["tower"]["treasury"], 4000)
        with self.assertRaises(R.Bad):
            t.buy("mend")   # Hold is full
        st["tower"]["hold"] = 1
        t.buy("mend")
        self.assertEqual(st["tower"]["hold"], 2)
        with self.assertRaises(R.Bad):
            t.buy(f"garrison@{free[0]}")   # one already


class Files(unittest.TestCase):
    def test_load_refuses_v1_and_v2(self):
        with tempfile.TemporaryDirectory() as d:
            for v in (1, 2):
                (Path(d) / "realms.json").write_text(json.dumps({"version": v}))
                with self.assertRaises(R.Bad) as cm:
                    R.load(d)
                self.assertIn(f"v{v}", str(cm.exception))

    def test_new_is_deterministic(self):
        a, b = R.generate(11), R.generate(11)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertNotEqual(json.dumps(a, sort_keys=True), json.dumps(R.generate(12), sort_keys=True))

    def test_turn_is_deterministic(self):
        outs = []
        for _ in range(2):
            st = R.generate(11)
            t = R.Turn(st)
            t.run(orders())
            st["report"] = R.report(st, t, 1)
            outs.append(json.dumps(st, sort_keys=True))
        self.assertEqual(outs[0], outs[1])

    def test_start(self):
        st = world()
        for n, f in st["realms"].items():
            S = sum(st["hexes"][h]["level"] for h in f["hexes"])
            self.assertEqual(f["force"], max(1, min(5, int(S / 10 + 0.5))))
            self.assertEqual(f["treasury"], S * 10)
            kinds = [s["kind"] for s in R.sites_of(st, n)]
            self.assertEqual(sorted(kinds), ["garrison", "seat", "works"])
            self.assertEqual(R.site_at(st, f["seat"], "seat", n)["hex"], f["seat"])
            self.assertEqual(f["standing"], 1 if f["leader"]["label"] == "good" else 0)
            self.assertEqual(f["goal"]["marks"], 0)
        T = st["tower"]
        self.assertEqual((T["hold"], T["treasury"], R.tier_now(st)), (3, 100, 0))
        self.assertEqual(st["hexes"][st["warded"]]["level"], 1)

    def test_map_json_shape(self):
        st = world()
        t = R.Turn(st)
        gar = R.sites_of(st, next(iter(st["realms"])), kind="garrison")[0]
        t.run(orders(at=gar["hex"], strike=gar["id"], goal=f"take:{gar['hex']}"))
        st["report"] = R.report(st, t, 1)
        m = R.map_json(st, "x")
        self.assertEqual(list(m), ["version", "campaign", "month", "layout", "hexes", "rivers",
                                   "factions", "morten", "events", "report"])
        self.assertEqual(m["version"], 3)
        self.assertEqual(len(m["hexes"]), 20)
        a = [a for h in m["hexes"] for a in h["assets"]][0]
        self.assertEqual(sorted(a), ["id", "name", "owner", "tier", "type"])
        self.assertIn(a["type"], ("seat", "garrison", "works", "walls"))
        tower = m["factions"][-1]
        for k in ("tier", "tierName", "renown", "hold", "maxHold", "goal", "force"):
            self.assertIn(k, tower) if k != "force" else self.assertNotIn(k, tower)
        f = m["factions"][0]
        for k in ("force", "treasury", "seat", "hexes", "standing", "standingWord", "goal"):
            self.assertIn(k, f)
        for k in ("hp", "cunning", "wealth", "hostile", "disorder"):
            self.assertNotIn(k, f)
        self.assertEqual(sorted(f["goal"]), ["hex", "kind", "marks", "since", "size", "target", "text", "waits"])
        e = m["events"][0]
        self.assertEqual(sorted(e), ["action", "actor", "from_hex", "month", "result", "target", "to_hex"])
        h = m["report"]["happened"]
        self.assertEqual(h[0]["who"], "tower")
        for k in ("who", "goal", "roll", "marks", "size", "fired", "text"):
            self.assertIn(k, h[1])
        for k in ("plan", "happened", "tower", "next"):
            self.assertIn(k, m["report"])


class Smoke(unittest.TestCase):
    def run_cmd(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            self.assertEqual(p.returncode, 2, p.stdout)
            self.assertTrue(p.stderr.startswith("error: "), p.stderr)
            self.assertEqual(len(p.stderr.strip().splitlines()), 1)
        return p.stdout

    def test_every_command(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.run_cmd("new", "--seed", "7", "--campaign", d)
            self.assertIn("Wrote", out)
            for f in ("realms.json", "world.md", "map.json", "gm-secrets.md"):
                self.assertTrue((Path(d) / f).exists(), f)
            self.assertIn("## Floor 20", (Path(d) / "gm-secrets.md").read_text())
            st = json.loads((Path(d) / "realms.json").read_text())
            self.assertEqual(st["version"], 3)
            self.run_cmd("new", "--seed", "7", "--campaign", d, ok=False)
            out = self.run_cmd("show", "--campaign", d)
            self.assertIn("**Realms**", out)
            name = next(iter(st["realms"]))
            f = st["realms"][name]
            gar = next(s for s in st["sites"].values() if s["owner"] == name and s["kind"] == "garrison")
            works = next(s for s in st["sites"].values() if s["owner"] == name and s["kind"] == "works")
            out = self.run_cmd("show", "--campaign", d, "--at", gar["hex"])
            self.assertIn("**Rumours**", out)
            out = self.run_cmd("encounter", "--campaign", d, "--site", works["id"])
            self.assertIn("Rob:", out)
            self.assertIn("XP total", out)
            self.run_cmd("encounter", "--campaign", d, "--aid", name)
            out = self.run_cmd("encounter", "--campaign", d, "--contact", name)
            self.assertIn("DC", out)
            out = self.run_cmd("encounter", "--campaign", d, "--hex", "A1", "--seed", "3")
            self.assertIn("Wandering encounter", out)
            self.run_cmd("encounter", "--campaign", d, ok=False)
            before = (Path(d) / "realms.json").read_text()
            out = self.run_cmd("turn", "--campaign", d, "--dry-run")
            self.assertIn("(dry run: nothing saved)", out)
            self.assertEqual(before, (Path(d) / "realms.json").read_text())
            self.run_cmd("turn", "--campaign", d, "--strike", gar["id"], ok=False)   # not there
            self.assertEqual(before, (Path(d) / "realms.json").read_text())
            out = self.run_cmd("turn", "--campaign", d, "--at", gar["hex"], "--strike", gar["id"],
                               "--goal", f"take:{gar['hex']}", "--plan", "why", "--deposit", "50")
            for part in ("**The plan**", "**What happened**", "**The tower now**", "**Next month**",
                         "**Realms**", "**Income**", "**Log**", "**The tower:**", "d6 "):
                self.assertIn(part, out)
            st = json.loads((Path(d) / "realms.json").read_text())
            self.assertEqual(st["month"], 2)
            self.assertEqual(st["tower"]["goal"]["marks"], 2)
            self.assertEqual(st["tower"]["treasury"], 150 + sum(
                st["hexes"][h]["level"] * 10 for h in st["tower"]["hexes"]))
            m = json.loads((Path(d) / "map.json").read_text())
            self.assertEqual(m["month"], 2)
            self.assertTrue(m["events"])
            self.assertIn("Month 2", (Path(d) / "world.md").read_text())
            out = self.run_cmd("turn", "--campaign", d, "--at", f["seat"], "--contact", name,
                               "--goal", "ally:" + name, "--give", f"{name}=100")
            self.assertIn("Contact", out)
            self.run_cmd("turn", "--campaign", d, "--buy", "mend", ok=False)
            self.run_cmd("turn", "--campaign", d, "--goal", "topple:Nobody", ok=False)
            self.run_cmd("turn", "--campaign", d, "--back", name, ok=False)
        out = self.run_cmd("sim", "--seeds", "1-2", "--months", "3")
        self.assertIn("2 seeds × 3 months (passive tower)", out)
        out = self.run_cmd("sim", "--seeds", "1-2", "--months", "3", "--scripted")
        self.assertIn("Scripted Morten", out)

    def test_v2_campaign_refused(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "realms.json").write_text(json.dumps({"version": 2}))
            p = subprocess.run([sys.executable, str(SCRIPT), "show", "--campaign", d],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn("v2", p.stderr)


if __name__ == "__main__":
    unittest.main()
