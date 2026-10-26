"""Write the month's domain section from map.json's report (the v3 report is one sentence
per realm, the tower's goal line first): domain.py DIR OUT.md"""
import json
import re
import sys
from pathlib import Path

d, out = Path(sys.argv[1]), Path(sys.argv[2])
mp = json.loads((d / "map.json").read_text())
rep = mp["report"]
tower = next(f for f in mp["factions"] if f["tower"])
clean = lambda s: re.sub(r"\s+s\d+\b", "", s).replace("**", "").replace("*", "")  # noqa: E731
near = [h for h in rep["happened"] if not h.get("far")]
far = [h for h in rep["happened"] if h.get("far")]
lines = ["---", "kind: domain", f"title: Month {rep['month']} · the world's turn", f"month: {rep['month']}",
         "day: 30", 'clock: "20:00"', "hex: B5", "where: the tower (B5)",
         "headline: The tower has no goal yet, so the clocks moved without it: "
         + "; ".join(f"the {h['who']}{chr(39) if h['who'].endswith('s') else chr(39) + 's'} {h['goal']} at {h['marks']} of {h['size']}" for h in near if h["who"] != "tower"
                     and h["marks"]) + ".",
         "---", "### The plan"] + [f"- {clean(p)}" for p in rep["plan"]]
lines += ["", "### What happened"] + [f"- who={h['who']}: {clean(h['text'])}" for h in near]
if far:
    lines += ["", "### Elsewhere", " ".join(clean(h["text"]) for h in far)]
lines += ["", "### The tower now",
          f"- Gold: 105 GP → {tower['treasury']:,} GP",
          f"- Tier: {tower['tierName']} (Renown {tower['renown']}) → {tower['tierName']} (Renown {tower['renown']})",
          f"- Hold: {tower['hold']} of {tower['maxHold']} → {tower['hold']} of {tower['maxHold']}",
          "- Morten's XP: 900 → 950",
          "", "### Next month"] + [f"- {clean(x)}" for x in rep["next"]]
out.write_text("\n".join(lines) + "\n")
