#!/usr/bin/env python3
"""Smoke tests for loot.py (stdlib unittest): nothing in the SRD crashes it.

Usage:
  python3 tools/test_loot.py
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


class Smoke(unittest.TestCase):
    def test_every_item_can_be_rolled(self):
        """A rare item that breaks would take weeks of play to turn up, so try them all."""
        rng = random.Random(1)
        for entries in loot.load_pool().values():
            for e in entries:
                item = loot.finish(e, rng)
                self.assertGreater(item["price"], 0, e["name"])
                loot.describe(item)

    def test_cli(self):
        for argv in (["--level", "4", "--seed", "1", "--count", "5"],
                     ["--rarity", "Legendary", "--seed", "2"],
                     ["--rarity", "Common", "--seed", "3"],
                     ["--scroll", "0", "--seed", "4"],
                     ["--level", "15", "--sure", "--seed", "5"]):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                loot.main(argv)
            self.assertTrue(out.getvalue().strip(), argv)


if __name__ == "__main__":
    unittest.main()
