#!/usr/bin/env python3
"""The Division's day: the ten seats, the ledger of open breaches, spills, deaths, arrivals
and the review. Every die of the day that isn't the player's is rolled here.

  python3 breach2/tools/day.py new breach2/campaigns/<name> --seed 7 [--player-grade 1]
  python3 breach2/tools/day.py show breach2/campaigns/<name> [--role Wren]
  python3 breach2/tools/day.py ledger breach2/campaigns/<name>      # the GM's view, true levels
  python3 breach2/tools/day.py dawn breach2/campaigns/<name> [--player-died]
  python3 breach2/tools/day.py close breach2/campaigns/<name> ID [--left N]  # the player closed
                                    # it; N living groups were left behind and are loose
  python3 breach2/tools/day.py take breach2/campaigns/<name> ID     # the player is sent to it
  python3 breach2/tools/day.py clear breach2/campaigns/<name> N     # loose group N is dealt with
  python3 breach2/tools/day.py report breach2/campaigns/<name>      # rewrite division.md

`dawn` moves the day on by one and prints the day's news for the GM. It does NOT rewrite
division.md: that file is what the player's pair knew when they last reported in (at the
station), and `report` rewrites it.

The player's breach is generated from the ledger's seed; `ledger` prints the line to run.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_breach  # noqa: E402

# ---- Dials -------------------------------------------------------------------------------
BREACH_DIE = 20      # each dawn, per grade: a breach on a 1
SPILL_DIE = 6        # each dawn, per open breach: a group gets out on a 1
SPILLS_TO_EMPTY = 3  # an unattended breach that has spilled this often is empty: struck off
ANOMALY_DIE = 6      # on a 6 the breach has an anomaly: one room from a level higher
REVIEW_DAYS = 60     # the whole ladder moves up a grade
NPC_DAYS = 3         # another pair settles its breach 1dN dawns after it's assigned
NPC_DEATH = 1        # d20: this or lower, the officer dies in it
NPC_WITHDRAW = 4     # d20: this or lower (above death), the pair withdraws and it stays open
VACANCY = (2, 6)     # a dead officer's replacement arrives in 2d6 days
SETTLE_DIE = 20      # each dawn, per loose group older than a week: on a 1 someone has sent
                     # it home or killed it (nothing loose ever settles in the city)
# ------------------------------------------------------------------------------------------

ROLES = ["Lion", "Wolf", "Bear", "Stag", "Hawk", "Raven", "Owl", "Fox", "Hound", "Wren"]
RANKS = [None, "Probationer", "Constable", "Senior Constable", "Sergeant", "Station Sergeant",
         "Inspector", "Chief Inspector", "Superintendent", "Chief Superintendent", "Commander"]

SPECIES = ["Elf", "Gnome", "Human", "Orc", "Tiefling"]
BACKGROUNDS = ["Acolyte", "Criminal", "Sage", "Soldier"]
FRONT = [("Barbarian", "Berserker"), ("Fighter", "Champion"), ("Paladin", "Devotion"),
         ("Monk", "Open Hand"), ("Ranger", "Hunter"), ("Cleric", "Life")]
BACK = [("Wizard", "Evoker"), ("Sorcerer", "Draconic"), ("Warlock", "Fiend"),
        ("Bard", "Lore"), ("Rogue", "Thief"), ("Druid", "Land")]
PRIORITY = {
    "Barbarian": "STR CON DEX WIS CHA INT", "Fighter": "STR CON DEX WIS INT CHA",
    "Paladin": "STR CHA CON WIS DEX INT", "Monk": "DEX WIS CON STR INT CHA",
    "Ranger": "DEX WIS CON STR INT CHA", "Cleric": "WIS CON STR DEX CHA INT",
    "Wizard": "INT DEX CON WIS CHA STR", "Sorcerer": "CHA CON DEX WIS INT STR",
    "Warlock": "CHA CON DEX WIS INT STR", "Bard": "CHA DEX CON WIS INT STR",
    "Rogue": "DEX CON INT WIS CHA STR", "Druid": "WIS CON DEX INT CHA STR",
}

# Plain English names. Elves get the grand ones, orcs the short ones, gnomes the small ones,
# tieflings the virtues. Each species has (men's names, women's names); a dungeoneer is one
# or the other on a coin flip. Automatons are all "he".
NAMES = {
    "Elf": (["Percival", "Sebastian", "Julian", "Leopold", "Ambrose", "Montgomery", "Lionel",
             "Crispin"],
            ["Cordelia", "Evelyn", "Arabella", "Rosalind", "Beatrice", "Genevieve", "Octavia",
             "Vivian", "Cecily"]),
    "Gnome": (["Archie", "Pip", "Alfie", "Bertie", "Wally", "Ned", "Gus", "Sid"],
              ["Nell", "Dot", "Tilly", "Minnie", "Flo", "Posy", "Kit", "Midge"]),
    "Human": (["Arthur", "Thomas", "Henry", "Walter", "George", "Albert", "Frank", "Harold"],
              ["Mary", "Alice", "Ruth", "Edith", "Martha", "Clara", "Agnes", "Ivy"]),
    "Orc": (["Tom", "Bob", "Jack", "Joe", "Sam", "Bill", "Dan", "Jim", "Ben"],
            ["Meg", "Peg", "Bess", "Kate", "Nan", "Moll", "Sal"]),
    "Tiefling": (["Ernest", "Felix", "Clement", "Victor", "Christian", "Chance"],
                 ["Prudence", "Hope", "Constance", "Verity", "Patience", "Grace", "Faith",
                  "Mercy", "Honor", "Amity"]),
}
SURNAMES = ["Ashcombe", "Baker", "Carter", "Cooper", "Dunmore", "Fairweather", "Greaves",
            "Hargreaves", "Kettering", "Lowry", "Marsh", "Northcote", "Oxley", "Pendry",
            "Quayle", "Rooke", "Sallow", "Thorne", "Underhill", "Vance", "Whitlock", "Yarrow",
            "Tanner", "Chandler", "Fletcher", "Mercer", "Sawyer", "Wainwright", "Hobbs", "Pike"]
PRONOUNS = ["he/him", "she/her"]

AUTOMATON_NAMES = ["Alder", "Basset", "Carrow", "Dunstan", "Ellery", "Fenwick", "Garrow",
                   "Hollis", "Ives", "Jessop", "Kemble", "Lowell", "Marlow", "Nettle", "Oakes",
                   "Pennywhistle", "Quill", "Rookwood", "Sedge", "Tamworth", "Upton", "Vickers",
                   "Wimbourne", "Yately", "Abbott", "Brisket", "Candlewick", "Dorrit", "Evershed",
                   "Faraday", "Gaskell", "Hobbes", "Inchbald", "Jarvis", "Kettle", "Lampwick"]
PROTOCOL_SKILLS = ["Perception", "Insight", "Medicine", "History", "Investigation", "Survival",
                   "Persuasion", "Arcana", "Athletics", "Stealth", "Animal Handling", "Sleight of Hand"]

# A d100 of minor quirks: a habit to recognise a seat by, nothing that decides who they are.
QUIRKS = [
    "whistles on stairs", "always has a boiled sweet in one cheek", "counts doors under the breath",
    "polishes the badge with a thumb while thinking", "never sits with their back to a door",
    "hums the same four bars, never the fifth", "keeps a pencil behind one ear and loses it there",
    "eats standing up", "says 'right' before every decision", "cracks the knuckles one at a time",
    "wears the cap a size too large", "takes tea black and scalding", "writes notes on a shirt cuff",
    "taps every lamp post in passing", "carries a pocket watch that runs four minutes fast",
    "laughs a beat late", "ties every knot twice", "sneezes in threes", "walks on the kerb's edge",
    "names the weather before saying good morning", "saves the crusts for pigeons",
    "always knows the tram times", "folds the newspaper into eighths", "chews a matchstick",
    "wears odd socks on purpose", "salutes with the wrong hand when tired",
    "never finishes a cup of tea", "reads the last page first", "keeps a pressed flower in the warrant card",
    "sharpens things that are already sharp", "is early for everything", "is two minutes late for everything",
    "rolls the sleeves to exactly the elbow", "smells faintly of camphor", "carries string, always",
    "talks to cats in the street", "mutters sums while walking", "stands on one leg to think",
    "collects tram tickets", "has ink on the same finger every day", "blows on dice that aren't there",
    "buttons the coat to the throat in any weather", "says 'much obliged' to doors held open and to doors",
    "keeps a lucky farthing in the left boot", "yawns before a fight, never after",
    "scratches one ear when lying", "refuses to step on a drain cover", "keeps the bootlaces waxed",
    "squints at anything written down", "can't pass a street organ without stopping",
    "drums two fingers on the holster", "wears a scarf somebody clearly knitted for them",
    "carries a tin of peppermints and offers them round", "starts sentences with 'now then'",
    "peels an apple in one strip", "wipes the feet on mats that aren't there", "snores, by all accounts",
    "always picks the chair by the stove", "knows one joke and tells it well",
    "hates pigeons and says so", "winds the station clock unasked", "keeps the hair cut very short",
    "wears a flower in the buttonhole on Mondays", "tests a floor with one foot before trusting it",
    "is forever lending a handkerchief", "says grace over a sandwich", "shadow-boxes while waiting",
    "eats pickled onions from the jar", "sings in the wash house", "keeps a diary in a code of ticks",
    "steps over thresholds left foot first", "reads the notices on every wall",
    "calls every dog 'sergeant'", "holds the breath going past a cemetery", "ends the day by shining the boots",
    "wears spectacles on a cord and never on the nose", "stirs tea anticlockwise",
    "has a nod for every lamplighter", "saves buttons in a jar", "is always a little sunburnt or a little chilled",
    "sits on steps rather than chairs", "smokes a pipe that is never lit", "keeps the gloves on indoors",
    "says the day and date aloud on waking", "takes the stairs two at a time",
    "stops to watch any machine working", "carries a bent spoon and won't say why",
    "is a soft touch for a street singer", "chalks a tally mark inside the locker door",
    "slices bread too thick", "is always first to smell rain", "stands very straight when unsure",
    "checks the pockets in the same order, every time", "has a whistle that stops dogs",
    "can't abide a crooked picture", "rubs the bridge of the nose before speaking",
    "wears the collar turned up", "ends every report with 'that's the lot'",
    "keeps a clean handkerchief for the automaton's faceplate", "remembers everyone's tea",
]
assert len(QUIRKS) == 100 and len(set(QUIRKS)) == 100

DISTRICTS = ["Ironmongers' Reach", "Coldharbour", "the Tenters", "Nine Bridges", "Cinder Hill",
             "Saltmarket", "the Lows", "Bell Fields"]
PRECINCTS = ["Tallow Row", "Gasworks", "Pump Lane", "Ropewalk", "Foundry Bank", "Lime Wharf",
             "Bell Yard", "the Shambles", "Tenter Ground", "Soap Lane", "Canal Side",
             "Brick Fields", "Glasshouse", "Knacker's Yard", "Printers' Row", "Chapel Fields",
             "Coal Staithes", "Needle Street", "the Arches", "Dock Road", "Vinegar Yard",
             "Clock Street"]
PRECINCT_TRAITS = [
    "a covered market that never quite closes", "a tram depot and the tramwaymen's union hall",
    "the gasworks, and gas lamps that burn all day", "a canal basin crowded with barges",
    "a foundry whose hammer sets the precinct's hours", "rows of back-to-back tenements, full",
    "a music hall and the streets that live off it", "a cotton mill with a thousand hands",
    "a hospital run by a nursing order", "a rail viaduct and the workshops in its arches",
    "a brewery everyone smells before they see", "a board school for the children of the fallen",
    "a newspaper that dislikes the Board", "a pumping station and the reservoir above it",
    "an infirmary, a workhouse and a long queue", "a street of clockmakers and gunsmiths",
    "a cemetery, full, with a waiting list", "a dog track and its bookmakers",
    "a closed station of the underground railway", "a slaughterhouse and the tanneries downwind",
    "pawnshops, lodging houses and a mission hall", "a goods yard that feeds half the city",
]
# The 3x3 grid: the mast in the middle, the Fringe on its four sides, the Static in the
# corners. Legs are steps from the station (which stands under the mast).
GRID = [("NW", "Static", 2), ("N", "Fringe", 1), ("NE", "Static", 2),
        ("W", "Fringe", 1), ("Centre", "Core", 0), ("E", "Fringe", 1),
        ("SW", "Static", 2), ("S", "Fringe", 1), ("SE", "Static", 2)]
BAND_OF_GRADE = {1: "Core", 2: "Core", 3: "Core", 4: "Fringe", 5: "Fringe", 6: "Fringe",
                 7: "Fringe", 8: "Static", 9: "Static", 10: "Static"}


def d(rng, n):
    return rng.randint(1, n)


def plural(name):
    """Rough English plural of an SRD monster name: Wolf -> Wolves, Harpy -> Harpies."""
    if name.endswith(("folk", "Folk", " People", " Rex")):
        return name
    if name.startswith("Swarm of "):
        return "Swarms" + name[5:]
    if name.endswith("ff"):
        return name + "s"
    if name.endswith(("s", "x", "ch", "sh")):
        return name + "es"
    if name.endswith("f"):
        return name[:-1] + "ves"
    if name.endswith("fe"):
        return name[:-2] + "ves"
    if name.endswith("y") and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    return name + "s"


def scores(rng, cls):
    rolled = sorted((sum(sorted(rng.randint(1, 6) for _ in range(4))[1:]) for _ in range(6)),
                    reverse=True)
    return dict(zip(PRIORITY[cls].split(), rolled))


def new_automaton(rng, side, used_names, day, partner):
    name = rng.choice([n for n in AUTOMATON_NAMES if n not in used_names] or AUTOMATON_NAMES)
    used_names.add(name)
    cls, sub = rng.choice(BACK if side == "Front" else FRONT)
    return {"name": name, "side": "Back" if side == "Front" else "Front", "class": cls,
            "subclass": sub, "protocol_skill": rng.choice(PROTOCOL_SKILLS),
            "scores": scores(rng, cls), "built": day, "partners": [partner]}


def new_holder(rng, day, grade, used_quirks, side=None, level=None):
    """An officer for a seat. `side` is rolled unless given."""
    species = rng.choice(SPECIES)
    if side is None:
        side = "Front" if d(rng, 2) == 1 else "Back"
    cls, sub = rng.choice(FRONT if side == "Front" else BACK)
    quirk = rng.choice([q for q in QUIRKS if q not in used_quirks] or QUIRKS)
    used_quirks.add(quirk)
    sex = rng.randrange(2)
    return {"name": f"{rng.choice(NAMES[species][sex])} {rng.choice(SURNAMES)}",
            "pronouns": PRONOUNS[sex], "species": species,
            "background": rng.choice(BACKGROUNDS), "side": side, "class": cls, "subclass": sub,
            "scores": scores(rng, cls), "since": day, "quirk": quirk,
            "level": level or 2 * grade - d(rng, 2) + 1}


def new_district(rng):
    names = rng.sample(PRECINCTS, 9)
    traits = rng.sample(PRECINCT_TRAITS, 9)
    return {"name": rng.choice(DISTRICTS),
            "precincts": [{"name": n, "pos": pos, "band": band, "legs": legs, "trait": t}
                          for n, t, (pos, band, legs) in zip(names, traits, GRID)]}


def new_breach(c, rng, grade):
    """A breach the mast reads as `grade`. Its level is one of the grade's two; on a 6 the
    breach has an anomaly the Reader can't see: one room holds something from a level
    higher. It opens in the band the grade belongs to."""
    anomaly = d(rng, ANOMALY_DIE) == ANOMALY_DIE
    level = 2 * grade - d(rng, 2) + 1
    p = rng.choice([p for p in c["district"]["precincts"] if p["band"] == BAND_OF_GRADE[grade]])
    seed = rng.randrange(1, 1_000_000)
    b = {"id": c["next_id"], "day": c["day"], "grade": grade, "level": level,
         "precinct": p["name"], "seed": seed, "role": None, "due": None, "spills": 0,
         "withdrawn": False, "anomaly": anomaly, "kind": gen_breach.principal_for(level, seed)["name"]}
    c["next_id"] += 1
    c["ledger"].append(b)
    return b


def seat_of(c, role):
    return next(s for s in c["roster"] if s["role"] == role)


def assign(c, rng, news):
    """Each waiting breach goes to its grade's seat if that officer is alive and free."""
    busy = {b["role"] for b in c["ledger"] if b["role"]}
    for b in sorted(c["ledger"], key=lambda b: b["id"]):
        if b["role"] or b["withdrawn"]:
            continue
        seat = next((s for s in c["roster"] if s["grade"] == b["grade"]), None)
        if not seat or not seat["holder"] or seat["role"] in busy:
            continue
        b["role"] = seat["role"]
        busy.add(seat["role"])
        if seat["role"] == c["player"]:
            news.append(f"ASSIGNED TO YOU: #{b['id']}, grade {b['grade']}, {b['kind']}, "
                        f"{b['precinct']}.")
        else:
            b["due"] = c["day"] + d(rng, NPC_DAYS)


def go_loose(c, b, why):
    for lo in c["loose"]:
        if lo.get("breach") == b["id"]:
            lo["groups"] += 1
            return
    c["loose"].append({"breach": b["id"], "kind": b["kind"], "level": b["level"],
                       "precinct": b["precinct"], "since": c["day"], "groups": 1, "why": why})


def vacate(c, rng, seat, b, news, where):
    h = seat["holder"]
    c["fallen"].append({"role": seat["role"], "name": h["name"], "grade": seat["grade"],
                        "day": c["day"], "precinct": b["precinct"] if b else None,
                        "kind": b["kind"] if b else None})
    seat["holder"] = None
    seat["arrives"] = c["day"] + sum(d(rng, VACANCY[1]) for _ in range(VACANCY[0]))
    news.append(f"The {seat['role']}, {h['name']} ({RANKS[seat['grade']]}), died {where}. "
                f"{seat['automaton']['name']}, bound to {h['pronouns'].split('/')[1]}, went "
                f"dark. The seat is empty until day {seat['arrives']}.")


def fill(c, rng, seat, news, used_quirks, level=None):
    # The bond is to one officer: a new holder comes with a new automaton.
    h = new_holder(rng, c["day"], seat["grade"], used_quirks, level=level)
    used_names = {s["automaton"]["name"] for s in c["roster"]}
    a = new_automaton(rng, h["side"], used_names, c["day"], h["name"])
    seat["holder"], seat["arrives"], seat["automaton"] = h, None, a
    you = " THIS IS YOUR SEAT: the human plays them." if seat["role"] == c["player"] else ""
    news.append(f"The new {seat['role']} is {h['name']} ({h['pronouns']}, {h['species']} "
                f"{h['class']}), {RANKS[seat['grade']]}, with a new automaton, {a['name']} "
                f"({a['class']}).{you}")


def new(path, seed, player_grade):
    rng = random.Random(seed)
    used_names, used_quirks = set(), set()
    grades = list(range(1, 11))
    rng.shuffle(grades)
    roster = []
    for role, grade in zip(ROLES, grades):
        h = new_holder(rng, 1 - 30 * grade, grade, used_quirks,
                       level=2 * grade - 1 if grade == player_grade else None)
        roster.append({"role": role, "grade": grade, "holder": h, "arrives": None,
                       "automaton": new_automaton(rng, h["side"], used_names, 1 - 30 * grade,
                                                  h["name"])})
    roster.sort(key=lambda s: s["grade"])
    player = next(s for s in roster if s["grade"] == player_grade)
    c = {"name": path.name, "seed": seed, "division": f"{rng.choice('BCDEFGHJKLMNPRSTVW')} Division",
         "day": 1, "last_review": 1, "player": player["role"], "roster": roster,
         "district": new_district(rng), "ledger": [], "next_id": 1, "loose": [], "fallen": [],
         "graduated": [], "news": []}
    # What was already loose before the campaign: something to meet in the street.
    for _ in range(3):
        g = min(d(rng, 10), d(rng, 10))
        b = new_breach(c, rng, g)
        c["ledger"].remove(b)
        go_loose(c, b, "from before your time")
        c["loose"][-1]["since"] = -d(rng, 20)
    news = []
    new_breach(c, rng, player_grade)  # the player's first, so day 1 opens on a dispatch
    for g in range(1, 11):
        if g != player_grade and d(rng, BREACH_DIE) == 1:
            new_breach(c, rng, g)
    assign(c, rng, news)
    c["news"] = news
    path.mkdir(parents=True, exist_ok=True)
    save(c, path)
    (path / "division.md").write_text(division_md(c))
    (path / "district.md").write_text(district_md(c))
    return c


def dawn(c, rng, player_died=False):
    news = []
    c["day"] += 1
    day = c["day"]
    used_quirks = {s["holder"]["quirk"] for s in c["roster"] if s["holder"]}
    player = seat_of(c, c["player"])

    if player_died and player["holder"]:
        b = next((b for b in c["ledger"] if b["role"] == c["player"]), None)
        vacate(c, rng, player, b, news, f"in the breach at {b['precinct']}" if b else "on duty")
        if b:
            b["role"] = None

    # The review: the whole ladder moves up a grade. The Commander goes to Head Office.
    if day - c["last_review"] >= REVIEW_DAYS:
        c["last_review"] = day
        news.append("REVIEW DAY: every seat moves up a grade.")
        for s in c["roster"]:
            h = s["holder"]
            if s["grade"] == 10:
                if h:
                    c["graduated"].append({"role": s["role"], "name": h["name"], "day": day})
                    news.append(f"The {s['role']}, {h['name']}, Commander, is called to Head "
                                f"Office, and {s['automaton']['name']} with them.")
                s["grade"] = 1
                fill(c, rng, s, news, used_quirks, level=1)
            else:
                s["grade"] += 1
                if h and s["role"] != c["player"]:
                    h["level"] = min(20, h["level"] + 2)
        c["roster"].sort(key=lambda s: s["grade"])

    for s in c["roster"]:
        if not s["holder"] and s["arrives"] is not None and s["arrives"] <= day:
            fill(c, rng, s, news, used_quirks)

    # The other pairs' breaches that come due today.
    for b in list(c["ledger"]):
        if not b["role"] or b["role"] == c["player"] or b["due"] is None or b["due"] > day:
            continue
        seat, roll = seat_of(c, b["role"]), d(rng, 20)
        if roll <= NPC_DEATH:
            vacate(c, rng, seat, b, news, f"in the {b['kind']} breach at {b['precinct']}")
            b["role"], b["due"], b["withdrawn"] = None, None, True
        elif roll <= NPC_WITHDRAW:
            news.append(f"The {seat['role']} withdrew from #{b['id']} ({b['kind']}, "
                        f"{b['precinct']}). It stays open, with no one on it.")
            b["role"], b["due"], b["withdrawn"] = None, None, True
        else:
            news.append(f"The {seat['role']} closed #{b['id']} ({b['kind']}, {b['precinct']}).")
            c["ledger"].remove(b)

    # Spills: every breach that was open overnight.
    for b in list(c["ledger"]):
        if b["day"] >= day or d(rng, SPILL_DIE) != 1:
            continue
        if b["role"] == c["player"]:
            news.append(f"SPILL FROM YOUR BREACH #{b['id']}: its strongest remaining group is "
                        f"out in {b['precinct']}. The GM picks the group and marks the room.")
        else:
            b["spills"] += 1
            news.append(f"#{b['id']} ({b['kind']}, grade {b['grade']}) spilled into "
                        f"{b['precinct']}.")
        go_loose(c, b, "spilled")
        if b["spills"] >= SPILLS_TO_EMPTY:
            c["ledger"].remove(b)
            news.append(f"#{b['id']} is struck off: nothing left inside. Its "
                        f"{plural(b['kind'])} are {b['precinct']}'s problem now.")

    for g in range(1, 11):
        if d(rng, BREACH_DIE) == 1:
            b = new_breach(c, rng, g)
            news.append(f"NEW BREACH #{b['id']}: the mast reads grade {g}, {b['kind']}, "
                        f"{b['precinct']}.")
    assign(c, rng, news)
    for b in c["ledger"]:
        if not b["role"] and b["day"] == day:
            news.append(f"#{b['id']} has no one to take it.")

    still = []
    for lo in c["loose"]:
        if day - lo["since"] > 7 and d(rng, SETTLE_DIE) == 1:
            news.append(f"The {plural(lo['kind'])} loose in {lo['precinct']} have been dealt "
                        "with: sent home or killed. The GM says by whom.")
        else:
            still.append(lo)
    c["loose"] = still
    c["news"] = news
    return news


def save(c, path):
    (path / "campaign.json").write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n")


def load(path):
    return json.loads((path / "campaign.json").read_text())


def division_md(c):
    nxt = c["last_review"] + REVIEW_DAYS
    out = [f"# {c['division']} · {c['district']['name']} · as of day {c['day']}", "",
           f"You are **the {c['player']}**. This is what you knew when you last reported in. "
           f"Next review: day {nxt}.", "", "## The seats", ""]
    for s in sorted(c["roster"], key=lambda s: -s["grade"]):
        you = " **(you)**" if s["role"] == c["player"] else ""
        a, h = s["automaton"], s["holder"]
        if h:
            lvl = "" if s["role"] == c["player"] else f", level {h['level']}"
            who = (f"{h['name']} ({h['pronouns']}), {h['species']} {h['class']}{lvl}; with "
                   f"{a['name']}, {a['class']}")
        else:
            who = f"*empty until day {s['arrives']}*; {a['name']} waits"
        out.append(f"- **{s['grade']} · {RANKS[s['grade']]} · the {s['role']}**{you}: {who}.")
    out += ["", "## The ledger", "",
            "Open breaches, as the mast reads them. The Reader does not see everything.", ""]
    if not c["ledger"]:
        out.append("- Nothing open.")
    for b in sorted(c["ledger"], key=lambda b: b["id"]):
        who = f"the {b['role']}" if b["role"] else "**no one**"
        if b["role"] == c["player"]:
            who = "**you**"
        age = c["day"] - b["day"]
        out.append(f"- #{b['id']} · grade {b['grade']} · {b['kind']} · {b['precinct']} · open "
                   f"{age} day{'s' if age != 1 else ''} · {who}"
                   + (" · withdrawn from" if b["withdrawn"] else ""))
    if c["loose"]:
        out += ["", "## Loose in the district", ""]
        for i, lo in enumerate(c["loose"], 1):
            n = f"{lo['groups']} groups of " if lo["groups"] > 1 else ""
            out.append(f"- {i}. {n}{plural(lo['kind'])} (from a level {lo['level']} breach) in "
                       f"{lo['precinct']} ({lo['why']}).")
    if c["news"]:
        out += ["", f"## This morning (day {c['day']})", ""] + [f"- {n}" for n in c["news"]]
    if c["fallen"]:
        out += ["", "## The wall", ""]
        for f in c["fallen"]:
            where = f"in the {f['kind']} breach at {f['precinct']}" if f["kind"] else "on duty"
            out.append(f"- Day {f['day']}: the {f['role']}, {f['name']}, {RANKS[f['grade']]}, "
                       f"{where}.")
    if c["graduated"]:
        out += ["", "## Called to Head Office", ""]
        out += [f"- Day {g['day']}: the {g['role']}, {g['name']}." for g in c["graduated"]]
    return "\n".join(out) + "\n"


def district_md(c):
    di = c["district"]
    out = [f"# {di['name']}", "",
           f"{c['division']}'s ground: nine precincts under one mast. The station stands under "
           "the mast in the centre. A leg is one precinct's crossing, about an hour by tram and "
           "on foot; the encounter die is rolled once a leg.", ""]
    for band, what in (("Core", "under the mast: grades 1 to 3"),
                       ("Fringe", "the mast's edge: grades 4 to 7"),
                       ("Static", "the corners, where no mast reaches: grades 8 to 10")):
        out += [f"## The {band} ({what})", ""]
        for p in di["precincts"]:
            if p["band"] == band:
                legs = "the station is here" if p["legs"] == 0 else \
                    f"{p['legs']} leg{'s' if p['legs'] > 1 else ''} from the station"
                out.append(f"- **{p['name']}** ({p['pos']}, {legs}): {p['trait']}.")
        out.append("")
    out += ["## People of the station", "",
            "The GM writes these as play meets them: the Director, the Reader, the ledger "
            "Clerk, the Mechanic, the Auditor. By title, no names. One line each: what they "
            "are like and what they want.", "", "## GM notes", ""]
    return "\n".join(out) + "\n"


def pair_md(s):
    a, h = s["automaton"], s["holder"]
    asc = " ".join(f"{k} {v}" for k, v in a["scores"].items())
    lines = [f"**The {s['role']}** · grade {s['grade']} {RANKS[s['grade']]}"]
    if h:
        sc = " ".join(f"{k} {v}" for k, v in h["scores"].items())
        lines += [f"- Dungeoneer: {h['name']} ({h['pronouns']}), {h['species']} "
                  f"{h['background']}, {h['side']}: {h['class']} ({h['subclass']}), level "
                  f"{h['level']}, since day {h['since']}. Scores {sc}.",
                  f"- Quirk: {h['quirk']}."]
    else:
        lines.append(f"- The seat is empty until day {s['arrives']}.")
    lines.append(f"- Automaton: {a['name']}, {a['side']}: {a['class']} ({a['subclass']}), "
                 f"protocol skill {a['protocol_skill']}. Scores {asc}. Bound to "
                 + a["partners"][-1] + ".")
    return "\n".join(lines)


def ledger_lines(c):
    out = []
    for b in sorted(c["ledger"], key=lambda b: b["id"]):
        who = f"the {b['role']}" if b["role"] else "no one"
        legs = next(p["legs"] for p in c["district"]["precincts"] if p["name"] == b["precinct"])
        out.append(f"#{b['id']} · grade {b['grade']} (level {b['level']}{', anomaly' if b.get('anomaly') else ''}) · {b['kind']} · "
                   f"{b['precinct']}, {legs} leg(s) · open since day {b['day']} · {who}"
                   + (f" · due day {b['due']}" if b["due"] else "")
                   + (f" · spills {b['spills']}" if b["spills"] else ""))
        if b["role"] == c["player"]:
            out.append(f"    python3 breach2/tools/gen_breach.py --seed {b['seed']} --level "
                       f"{b['level']}" + (" --anomaly" if b.get("anomaly") else ""))
    return out or ["Nothing open."]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=["new", "show", "ledger", "dawn", "close", "take", "clear",
                                     "report"])
    ap.add_argument("campaign", type=Path)
    ap.add_argument("n", type=int, nargs="?")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--player-grade", type=int, default=1)
    ap.add_argument("--role")
    ap.add_argument("--player-died", action="store_true")
    ap.add_argument("--left", type=int, default=0)
    a = ap.parse_args()

    if a.verb == "new":
        if a.seed is None:
            sys.exit("new needs --seed (roll it: roll.py 1d1000)")
        if (a.campaign / "campaign.json").exists():
            sys.exit(f"{a.campaign} already exists")
        c = new(a.campaign, a.seed, a.player_grade)
        print(f"{c['division']}, {c['district']['name']}. You are the {c['player']}.\n")
        print(pair_md(seat_of(c, c["player"])))
        print("\nDay 1:")
        print("\n".join(ledger_lines(c)))
        print(f"\nWrote {a.campaign}/campaign.json, division.md, district.md.")
        return
    c = load(a.campaign)
    if a.verb == "show":
        seats = [s for s in c["roster"] if not a.role or s["role"].lower() == a.role.lower()]
        print("\n\n".join(pair_md(s) for s in seats))
        return
    if a.verb == "ledger":
        print(f"Day {c['day']}.")
        print("\n".join(ledger_lines(c)))
        for i, lo in enumerate(c["loose"], 1):
            print(f"loose {i} · {lo['groups']}× group of {plural(lo['kind'])} · level "
                  f"{lo['level']} · {lo['precinct']} · since day {lo['since']}")
            # A hunt for it; a second group of the same kind takes the next seed up.
            print(f"    python3 breach2/tools/gen_breach.py --seed "
                  f"{lo['breach'] * 1000 + abs(lo['since'])} --level {lo['level']} --kind "
                  f"\"{lo['kind']}\"")
        return
    if a.verb == "report":
        (a.campaign / "division.md").write_text(division_md(c))
        print(f"division.md rewritten as of day {c['day']}.")
        return
    if a.verb == "dawn":
        news = dawn(c, random.Random(f"{c['seed']}:{c['day'] + 1}"), a.player_died)
        save(c, a.campaign)
        print(f"Day {c['day']}.")
        print("\n".join(f"- {n}" for n in news) or "- A quiet morning.")
        return
    if a.n is None:
        sys.exit(f"{a.verb} needs a number")
    if a.verb == "clear":
        if not 1 <= a.n <= len(c["loose"]):
            sys.exit("no such loose group (see `ledger`)")
        lo = c["loose"].pop(a.n - 1)
        print(f"The {plural(lo['kind'])} in {lo['precinct']} are struck from the loose list.")
    else:
        b = next((b for b in c["ledger"] if b["id"] == a.n), None)
        if not b:
            sys.exit(f"no open breach #{a.n}")
        if a.verb == "close":
            c["ledger"].remove(b)
            for _ in range(a.left):
                go_loose(c, b, "left behind")
            print(f"#{b['id']} ({b['kind']}, {b['precinct']}) is closed."
                  + (f" {a.left} group(s) left behind are loose in {b['precinct']}."
                     if a.left else ""))
        else:
            b["role"], b["due"], b["withdrawn"] = c["player"], None, False
            print(f"#{b['id']} is yours.")
            print("\n".join(l for l in ledger_lines(c) if l.startswith(f"#{b['id']} ")
                            or f"--seed {b['seed']} " in l))
    save(c, a.campaign)


if __name__ == "__main__":
    main()
