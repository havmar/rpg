#!/usr/bin/env python3
"""Smoke test for omen.py: the index parses and an omen prints."""
import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import omen  # noqa: E402


class TestOmen(unittest.TestCase):
    def test_index_parses(self):
        pool = omen.monsters()
        self.assertGreater(len(pool), 300)
        self.assertTrue(all((omen.SRD.parent.parent / m["file"]).exists() for m in pool))

    def test_prints(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            omen.main(["--level", "3", "--seed", "1"])
        out = buf.getvalue()
        self.assertIn("Omen d", out)
        self.assertIn("As d4", out)


if __name__ == "__main__":
    unittest.main()
