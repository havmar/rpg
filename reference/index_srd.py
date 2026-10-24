"""Write reference/srd/Monsters by CR.md, a table of every stat block by challenge rating.

Run it after refreshing reference/srd (see reference/srd/README.md).
"""
import re
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote

SRD = Path(__file__).parent / "srd"


def field(text, name):
    m = re.search(rf"^- \*\*{name}\*\* (.+)$", text, re.M)
    return m.group(1).strip() if m else ""


rows = []
for path in sorted((SRD / "Monsters").glob("*.md")):
    text = path.read_text()
    kind = re.search(r"^_(.+)_$", text, re.M).group(1).split(",")[0]
    cr = field(text, "CR").split(" ")[0]
    ac = field(text, "AC").split(" ")[0]
    hp = field(text, "HP").split(" ")[0]
    rows.append((Fraction(cr), path.stem, cr, kind, ac, hp))
rows.sort()

out = ["# Monsters by CR", "",
       "Every stat block in `Monsters/`, by challenge rating. Written by `reference/index_srd.py`.", "",
       "| CR | Monster | Size and type | AC | HP |", "| --- | --- | --- | --- | --- |"]
out += [f"| {cr} | [{name}](Monsters/{quote(name)}.md) | {kind} | {ac} | {hp} |"
        for _, name, cr, kind, ac, hp in rows]
(SRD / "Monsters by CR.md").write_text("\n".join(out) + "\n")
print(len(rows), "monsters")
