#!/usr/bin/env python3
"""Tests for loot.py (stdlib unittest).

Usage:
  python3 dnd-crunch/tools/test_loot.py
"""
import contextlib
import io
import random
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loot  # noqa: E402


class Rows(unittest.TestCase):
    def test_every_row_covers_the_d20(self):
        for (lo, hi), row in loot.BANDS:
            tops = [top for top, _ in row]
            self.assertEqual(tops, sorted(tops), (lo, hi))
            self.assertEqual(tops[-1], 20, (lo, hi))
            self.assertIsNone(row[0][1], "each row opens with the miss")
            for face in range(1, 21):
                loot.row_result(row, face)

    def test_bands_cover_floors_1_to_20(self):
        self.assertEqual([loot.band(f) for f in (1, 4, 5, 10, 11, 16, 17, 20)],
                         [0, 0, 1, 1, 2, 2, 3, 3])
        with self.assertRaises(ValueError):
            loot.band(21)

    def test_the_drafted_odds(self):
        def odds(floor):
            row = loot.BANDS[loot.band(floor)][1]
            out = {}
            for face in range(1, 21):
                r = loot.row_result(row, face)
                out[r] = out.get(r, 0) + 1
            return out
        self.assertEqual(odds(1), {None: 10, "Common": 6, "Uncommon": 3, "Rare": 1})
        self.assertEqual(odds(17), {None: 8, "Uncommon": 1, "Rare": 3, "Very Rare": 5,
                                    "Legendary": 3})


class Pool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = loot.load_pool()
        cls.varies = loot.varies_entries()

    def test_every_folder_item_is_in_its_rarity(self):
        for folder in loot.FOLDERS:
            files = {f.stem for f in (loot.ITEMS / folder).glob("*.md")}
            names = {e["name"] for e in self.pool[folder] if e["file"].parent.name == folder}
            self.assertEqual(files, names, folder)

    def test_every_item_has_its_type_line(self):
        for entries in self.pool.values():
            for e in entries:
                self.assertTrue(e["tline"], e["file"])

    def test_every_varies_file_is_spread(self):
        files = {f.stem for f in (loot.ITEMS / "Varies").glob("*.md")}
        seen = {e["file"].stem for e in self.varies}
        self.assertEqual(files, seen)

    def test_varies_counts(self):
        def count(stem):
            return sum(1 for e in self.varies if e["file"].stem == stem)
        self.assertEqual(count("Ioun Stone"), 14)
        self.assertEqual(count("Figurine of Wondrous Power"), 9)
        self.assertEqual(count("Feather Token"), 6)
        self.assertEqual(count("Belt of Giant Strength"), 5)
        self.assertEqual(count("Potions of Healing"), 4)
        self.assertEqual(count("Weapon, +1, +2, or +3"), 3)
        self.assertEqual(count("Spell Scroll"), 10)
        names = {e["name"]: e["rarity"] for e in self.varies}
        self.assertEqual(names["Armor, +1"], "Rare")
        self.assertEqual(names["Shield, +1"], "Uncommon")
        self.assertEqual(names["Ioun Stone (Mastery)"], "Legendary")
        self.assertEqual(names["Potion of Healing (greater)"], "Uncommon")

    def test_every_entry_finishes_with_a_price(self):
        rng = random.Random(1)
        for entries in self.pool.values():
            for e in entries:
                item = loot.finish(e, rng)
                self.assertGreater(item["price"], 0, e["name"])

    def test_every_magic_weapon_and_armour_has_a_base(self):
        for entries in self.pool.values():
            for e in entries:
                spec = loot.base_spec(e["tline"])
                if spec:
                    self.assertTrue(loot.base_options(*spec), (e["name"], spec))

    def test_bases(self):
        names = lambda kind, spec: {n for n, _ in loot.base_options(kind, spec)}
        self.assertEqual(names("Armor", "Shield"), {"Shield"})
        heavy = names("Armor", "Any Medium or Heavy, Except Hide Armor")
        self.assertNotIn("Hide Armor", heavy)
        self.assertNotIn("Leather Armor", heavy)
        self.assertIn("Plate Armor", heavy)
        self.assertNotIn("Shield", names("Armor", "Any Light, Medium, or Heavy"))
        self.assertEqual(names("Weapon", "Longbow or Shortbow"), {"Longbow", "Shortbow"})
        self.assertNotIn("Shortbow", names("Weapon", "Any Melee Weapon"))
        self.assertIn("Arrows ×10", names("Weapon", "Any Ammunition"))

    def test_prices(self):
        rng = random.Random(0)
        by = {e["name"]: e for es in self.pool.values() for e in es}
        self.assertEqual(loot.finish(by["Bag of Holding"], rng)["price"], 400)
        self.assertEqual(loot.finish(by["Potion of Healing (greater)"], rng)["price"], 200)
        self.assertEqual(loot.finish(by["Dust of Dryness"], rng)["price"], 200)
        plate = {"name": "Armor, +1", "rarity": "Rare", "file": by["Armor, +1"]["file"],
                 "tline": "Armor (Plate Armor), Rare"}
        self.assertEqual(loot.finish(plate, rng)["price"], 5500)  # Magic Item Rarity.md
        scroll = {"name": "Spell Scroll", "scroll": 3, "rarity": "Uncommon",
                  "file": by["Bag of Holding"]["file"], "tline": "Scroll"}
        self.assertEqual(loot.finish(scroll, rng)["price"], 300)

    def test_wizard_spells_every_level(self):
        for level in range(10):
            self.assertTrue(loot.wizard_spells(level), level)
        self.assertIn("Fire Bolt", loot.wizard_spells(0))
        self.assertIn("Fireball", loot.wizard_spells(3))


class Rolls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = loot.load_pool()

    def test_sure_never_misses(self):
        rng = random.Random(4)
        for floor in (1, 7, 13, 19):
            for _ in range(50):
                _, item = loot.luggage(floor, rng, self.pool, sure=True)
                self.assertIsNotNone(item)

    def test_band_up(self):
        rng = random.Random(4)
        rolls, _ = loot.luggage(3, rng, self.pool, sure=True, band_up=True)
        self.assertIn("floors 5–10", rolls[0])
        rolls, _ = loot.luggage(18, rng, self.pool, sure=True, band_up=True)
        self.assertIn("floors 17–20", rolls[0])

    def test_rarity_matches_the_row(self):
        rng = random.Random(8)
        for _ in range(200):
            rolls, item = loot.luggage(2, rng, self.pool)
            if item:
                self.assertIn(item["rarity"], ("Common", "Uncommon", "Rare"))
                self.assertTrue(rolls[-1].endswith(item["rarity"]))

    def test_cli(self):
        for argv in (["--floor", "4", "--seed", "1", "--count", "5"],
                     ["--rarity", "Legendary", "--seed", "2"],
                     ["--rarity", "Common", "--seed", "3"],
                     ["--scroll", "0", "--seed", "4"],
                     ["--floor", "15", "--sure", "--band-up", "--seed", "5"]):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                loot.main(argv)
            self.assertTrue(out.getvalue().strip(), argv)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            loot.main(["--floor", "9", "--seed", "11"])
        again = io.StringIO()
        with contextlib.redirect_stdout(again):
            loot.main(["--floor", "9", "--seed", "11"])
        self.assertEqual(out.getvalue(), again.getvalue(), "a seed repeats")


if __name__ == "__main__":
    unittest.main()
