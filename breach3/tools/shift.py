#!/usr/bin/env python3
"""The precinct's day: the four seats, the board of readings, the breach dice, dispatch, the
other pairs' calls, overdue trouble, relic drops, deaths, arrivals and retirement. Every die
that isn't rolled inside the player's own fight is rolled here.

  python3 breach3/tools/shift.py new    breach3/campaigns/<name> --seed 7
  python3 breach3/tools/shift.py next   breach3/campaigns/<name> [--rest] [--to-call]
  python3 breach3/tools/shift.py done   breach3/campaigns/<name> kill|sent|failed [--xp N] [--helpers N]
  python3 breach3/tools/shift.py take   breach3/campaigns/<name> ID   # the Director sends the player's pair
  python3 breach3/tools/shift.py died   breach3/campaigns/<name>      # the player's dungeoneer died
  python3 breach3/tools/shift.py out    breach3/campaigns/<name> N    # the player's pair is off the street N days
  python3 breach3/tools/shift.py show   breach3/campaigns/<name>      # the player's pair, for the sheet
  python3 breach3/tools/shift.py status breach3/campaigns/<name>      # where the day is, what to run next

`next` moves the day on one round, in a fixed order: MORNING (6 am dice, calls, trouble),
MID-MORNING, LUNCH, MID-AFTERNOON (each: what the other pairs did last round, then calls),
EVENING (the last round's results, 6 pm dice), then MORNING of the next day. It refuses to move while the player's call is open:
settle it with `done`. `--rest` keeps the player's pair in for the round being dispatched.
`--to-call` runs round after round until the player's pair has a call.

Every command rewrites precinct.md, the player's view. It never holds what a monster is
until someone has seen it.
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

# ---- Dials -------------------------------------------------------------------------------
BATCH = 4            # breach dice per batch; a batch at 6 am and one at 6 pm
RETIRE_LEVEL = 12    # a holder who reaches this is called to Head Office
START_LEVELS = [1, 4, 7, 10]
UNDER_ONE_XP = 200   # a roll of 1 that isn't a CR 1: a group of a weaker kind up to this XP
UNDER_ONE_MAX = 8    # ... and never more than this many
DROP_ON = 15         # d20: a kill drops something on this or lower (three in four)
NPC_KILL_ON = 4      # d6: another pair kills (and absorbs the XP) on this or lower, else brings it in
NPC_DEATH_ON = 1     # d6, after a natural 1 on a hard call: dead on this or lower, else badly hurt
VACANCY_DAYS = 4     # a dead officer's replacement arrives in 1dN days
OVERDUE_SLOTS = 2    # a reading this many half-days old (2 = 24 hours) that still has no pair
                     # after the morning's dispatch rolls on the trouble table
TROUBLE_CAP = 2      # after this many trouble rolls Head Office takes the reading off the precinct
TO_CALL_DAYS = 7     # `next --to-call` stops after this many days even with no call
HOSTILE_ON = 2       # d6: a monster that isn't Evil is Hostile anyway on this or lower
# Rarity of a drop by the monster's reading: (Common, Uncommon, Rare, Very Rare) out of 100.
RARITY = [(1, (60, 35, 5, 0)), (4, (50, 40, 10, 0)), (7, (30, 50, 18, 2)), (99, (20, 45, 28, 7))]
# ------------------------------------------------------------------------------------------

SRD = Path(__file__).resolve().parents[2] / "reference" / "srd"
THRESHOLD = [0, 0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
             100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ROUND = ["night", "morning", "mid-morning", "early afternoon", "mid-afternoon"]

ROLES = ["Lion", "Wolf", "Bear", "Stag", "Hawk", "Raven", "Owl", "Fox", "Hound", "Wren"]
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
                   "Persuasion", "Arcana", "Athletics", "Stealth", "Animal Handling",
                   "Sleight of Hand"]
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
    "never finishes a cup of tea", "reads the last page first", "sharpens things that are already sharp",
    "is early for everything", "is two minutes late for everything", "smells faintly of camphor",
    "carries string, always", "talks to cats in the street", "mutters sums while walking",
    "collects tram tickets", "has ink on the same finger every day", "keeps a lucky farthing in the left boot",
    "yawns before a fight, never after", "refuses to step on a drain cover", "drums two fingers on the holster",
    "wears a scarf somebody clearly knitted for them", "carries a tin of peppermints and offers them round",
    "starts sentences with 'now then'", "peels an apple in one strip", "knows one joke and tells it well",
    "hates pigeons and says so", "winds the station clock unasked", "shadow-boxes while waiting",
    "eats pickled onions from the jar", "calls every dog 'sergeant'", "stirs tea anticlockwise",
    "smokes a pipe that is never lit", "keeps the gloves on indoors", "takes the stairs two at a time",
    "stops to watch any machine working", "carries a bent spoon and won't say why",
    "chalks a tally mark inside the locker door", "is always first to smell rain",
    "checks the pockets in the same order, every time", "can't abide a crooked picture",
    "ends every report with 'that's the lot'", "remembers everyone's tea",
    "keeps a clean handkerchief for the automaton's faceplate",
]
PRECINCTS = ["Ironmongers' Reach", "Coldharbour", "the Tenters", "Nine Bridges", "Cinder Hill",
             "Saltmarket", "the Lows", "Bell Fields"]
STREETS = ["Tallow Row", "Gasworks", "Pump Lane", "Ropewalk", "Foundry Bank", "Lime Wharf",
           "Bell Yard", "the Shambles", "Tenter Ground", "Soap Lane", "Canal Side",
           "Brick Fields", "Glasshouse", "Knacker's Yard", "Printers' Row", "Chapel Fields",
           "Coal Staithes", "Needle Street", "the Arches", "Dock Road", "Vinegar Yard",
           "Clock Street"]
STREET_TRAITS = [
    "a covered market that never quite closes", "a tram depot and the tramwaymen's union hall",
    "the gasworks, and gas lamps that burn all day", "a canal basin crowded with barges",
    "a foundry whose hammer sets the neighbourhood's hours", "rows of back-to-back tenements, full",
    "a music hall and the streets that live off it", "a cotton mill with a thousand hands",
    "a hospital run by a nursing order", "a rail viaduct and the workshops in its arches",
    "a brewery everyone smells before they see", "a board school", "a newspaper that dislikes the Board",
    "a pumping station and the reservoir above it", "an infirmary, a workhouse and a long queue",
    "a street of clockmakers and gunsmiths", "a cemetery, full, with a waiting list",
    "a dog track and its bookmakers", "a closed station of the underground railway",
    "a slaughterhouse and the tanneries downwind", "pawnshops, lodging houses and a mission hall",
    "a goods yard that feeds half the city",
]
SPOTS = [
    "a coal cellar under a terrace", "a railway arch", "the loft of a warehouse",
    "a culvert in the Under, ankle-deep", "a chapel between services", "a boiler house",
    "the yard behind a public house", "a tram shed", "a tenement stairwell and its landings",
    "a mill's dye works, vats and all", "a builder's yard behind a hoarding", "a market hall",
    "a schoolyard, the children sent in", "a goods platform", "a rooftop among chimney stacks",
    "a street of shops, shutters coming down",
]
WATER_SPOTS = ["the canal basin", "a flooded culvert in the Under", "the reservoir",
               "a dry dock with the gates open", "a dye works' settling tank"]
SIZES = [(6, 6), (6, 8), (8, 8), (8, 10), (10, 10), (10, 12), (12, 12), (6, 12), (4, 12)]
FEATURES = [
    "pillars, boilers or stacks (full cover)", "rubble or wreckage (difficult terrain, half cover)",
    "knee-deep water (difficult terrain)", "a 3 m ledge or gantry along one side (elevation)",
    "no light at all in half of it", "a drop crossed by a 1.5 m-wide plank or bridge",
    "machinery, carts or stacked cargo (half cover)", "a narrow 1.5 m way in (chokepoint)",
    "open, empty ground", "a high roof (9 m) with gantries, ropes or chains",
    "open fires or a live furnace (bright light, fire)",
    "thick fog or steam (heavily obscured beyond 3 m)", "bystanders who haven't got out yet",
]
HOSTILE = "Hostile: fights; will not be talked round; comes in only held, or dies"
NEUTRAL = "Neutral: no quarrel yet; will not come in unless convinced (GM's discretion) or held"
WILLING = "Willing: knows it is lost and wants to go home; will walk to the station"
TROUBLE = [
    None,
    ("goes berserk", "It is attacking people in the street. The GM says who and how many."),
    ("duplicates", "There are two of it now: a second reading is on the board."),
    ("paints over", "Its world has spread over the street it stands in: its weather, its "
                    "ground, its light. Whoever goes in fights on its terms."),
    ("explodes", "It is gone and so is the building. Nothing to send home, nothing to absorb."),
    ("grows", "The needle reads one higher. It has its maximum hit points."),
    ("calls another through", "One more breach die is rolled now."),
]

CR_LINE = re.compile(r"\*\*CR\*\* (\S+) \((?:XP )?([\d,]+)")
SPEED_LINE = re.compile(r"\*\*Speed\*\* (\d+) ft\.(.*)")
TYPE_LINE = re.compile(r"^_(.+?)_\s*$", re.M)
SIZE_WORDS = ("Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan", "or")
_MONSTERS = {}


def monsters():
    """SRD monsters by CR string: {'1/4': [...], '3': [...]}."""
    if _MONSTERS:
        return _MONSTERS
    for f in sorted((SRD / "Monsters").glob("*.md")):
        text = f.read_text()
        m, t = CR_LINE.search(text), TYPE_LINE.search(text)
        if not m or not t:
            continue
        xp = int(m.group(2).rstrip(",").replace(",", ""))
        if xp <= 0:
            continue
        head, _, align = t.group(1).rpartition(",")
        words = [w for w in head.split() if w not in SIZE_WORDS]
        base = "Swarm" if words[:1] == ["Swarm"] else (words[0] if words else "Monstrosity")
        size = next((w for w in head.split() if w in SIZE_WORDS[:-1]), "Medium")
        sp = SPEED_LINE.search(text)
        _MONSTERS.setdefault(m.group(1), []).append({
            "name": f.stem, "cr": m.group(1), "xp": xp, "type": base, "align": align.strip(),
            "size": size,
            "aquatic": bool(sp) and int(sp.group(1)) <= 10 and "Swim" in sp.group(2)})
    return _MONSTERS


def d(rng, n):
    return rng.randint(1, n)


def level_of(xp):
    return max(l for l in range(1, 21) if xp >= THRESHOLD[l])


def rank(level):
    return ("Probationer" if level < 4 else "Constable" if level < 7 else
            "Sergeant" if level < 10 else "Inspector")


def weekday(day):
    return WEEK[(day - 1) % 7]


def half(c):
    """Half-day index, for a reading's age: 2*day before noon, 2*day+1 after."""
    return 2 * c["day"] + (1 if c["round"] >= 3 else 0)


def rnd(c):
    """Index of the working round, four a day: 4*day + 0..3."""
    return 4 * c["day"] + max(c["round"], 1) - 1


def when(t):
    return f"{weekday(t // 2)} {'6 pm' if t % 2 else '6 am'}"


# ---- People ------------------------------------------------------------------------------

def scores(rng, cls):
    rolled = sorted((sum(sorted(rng.randint(1, 6) for _ in range(4))[1:]) for _ in range(6)),
                    reverse=True)
    return dict(zip(PRIORITY[cls].split(), rolled))


def new_pair(c, rng, seat, level):
    """A new holder for the seat and a new automaton bound to them."""
    used_q = {s["holder"]["quirk"] for s in c["seats"] if s.get("holder")}
    used_a = {s["automaton"]["name"] for s in c["seats"] if s.get("automaton")}
    species, sex = rng.choice(SPECIES), rng.randrange(2)
    side = "Front" if d(rng, 2) == 1 else "Back"
    cls, sub = rng.choice(FRONT if side == "Front" else BACK)
    acls, asub = rng.choice(BACK if side == "Front" else FRONT)
    seat["holder"] = {
        "name": f"{rng.choice(NAMES[species][sex])} {rng.choice(SURNAMES)}",
        "pronouns": PRONOUNS[sex], "species": species, "background": rng.choice(BACKGROUNDS),
        "side": side, "class": cls, "subclass": sub, "scores": scores(rng, cls),
        "since": c["day"], "quirk": rng.choice([q for q in QUIRKS if q not in used_q]),
        "xp": THRESHOLD[level]}
    seat["automaton"] = {
        "name": rng.choice([n for n in AUTOMATON_NAMES if n not in used_a]),
        "side": "Back" if side == "Front" else "Front", "class": acls, "subclass": asub,
        "protocol_skill": rng.choice(PROTOCOL_SKILLS), "scores": scores(rng, acls)}
    seat["arrives"], seat["back"] = None, 0


def lvl(seat):
    return level_of(seat["holder"]["xp"])


def pair_line(seat):
    h, a = seat["holder"], seat["automaton"]
    return (f"the {seat['role']}: {h['name']} ({h['pronouns']}), {h['species']} "
            f"{h['background']}, {h['class']} ({h['subclass']}) {lvl(seat)}, {h['side']}; "
            f"quirk: {h['quirk']}. Automaton: {a['name']}, {a['class']} ({a['subclass']}), "
            f"{a['side']}, protocol skill {a['protocol_skill']}.")


def show(c):
    s = player_seat(c)
    h, a = s["holder"], s["automaton"]
    sc = lambda x: " ".join(f"{k} {v}" for k, v in x.items())
    return "\n".join([
        f"YOUR SEAT: the {s['role']} · {rank(lvl(s))} · level {lvl(s)} · {h['xp']:,} XP "
        f"(level {lvl(s) + 1} at {THRESHOLD[lvl(s) + 1]:,}) · day off {s['off']}",
        f"Dungeoneer: {h['name']} ({h['pronouns']}), {h['species']}, {h['background']}, "
        f"{h['class']} ({h['subclass']}), {h['side']}. Scores as placed: {sc(h['scores'])}. "
        f"Quirk: {h['quirk']}.",
        f"Automaton: {a['name']} (he/him), {a['class']} ({a['subclass']}), {a['side']}, "
        f"protocol skill {a['protocol_skill']}. Scores as placed: {sc(a['scores'])}.",
    ])


def player_seat(c):
    return next((s for s in c["seats"] if s["role"] == c["player"]), None)


# ---- Monsters ----------------------------------------------------------------------------

def disposition(m, rng):
    if "Evil" in m["align"]:
        return HOSTILE
    roll = d(rng, 6)
    if roll <= HOSTILE_ON:
        return HOSTILE
    if roll == 6 and m["type"] not in ("Swarm", "Ooze", "Plant", "Construct"):
        return WILLING
    return NEUTRAL


def kinds_at(cr):
    """Kinds of this CR, or of the nearest CR below that has any (the SRD has no CR 18)."""
    while str(cr) not in monsters():
        cr -= 1
    return monsters()[str(cr)]


def breach_die(c, rng, t, news):
    """One d20. 1: CR 1 or lower. 2 to 10: that CR. 11: 10 + d10. 12 and up: nothing."""
    roll = d(rng, 20)
    if roll >= 12:
        return None
    count, reads, n = 1, str(roll), roll
    if roll == 1 and d(rng, 2) == 1:
        k = rng.choice([k for cr in ("0", "1/8", "1/4", "1/2") for k in monsters()[cr]])
        count = max(1, min(UNDER_ONE_MAX, UNDER_ONE_XP // k["xp"]))
        reads, n = "under 1", 0
    elif roll == 11:
        n = 10 + d(rng, 10)
        k, reads = rng.choice(kinds_at(n)), str(n)
    else:
        k = rng.choice(kinds_at(roll))
    w, h = rng.choice(SIZES)
    m = {"id": c["next_id"], "reads": reads, "n": n, "kind": k["name"], "cr": k["cr"],
         "count": count, "xp": k["xp"] * count, "type": k["type"], "align": k["align"],
         "size": k["size"], "street": rng.choice(c["streets"])["name"],
         "spot": rng.choice(WATER_SPOTS if k["aquatic"] else SPOTS),
         "room": f"{w}×{h} sq ({w * 1.5:g}×{h * 1.5:g} m)", "feature": rng.choice(FEATURES),
         "disposition": disposition(k, rng), "born": t, "pair": None, "tried": [],
         "notes": [], "seen": False}
    c["next_id"] += 1
    c["board"].append(m)
    news.append(f"NEW READING #{m['id']}: reads {reads}, {m['street']}.")
    return m


def what(m):
    return (f"{m['count']}× {m['kind']}" if m["count"] > 1 else f"the {m['kind']}") + \
        f" (#{m['id']}, read {m['reads']}, {m['street']})"


def call_card(c, m):
    stat = f"reference/srd/Monsters/{m['kind']}.md"
    return "\n".join([
        f"YOUR CALL: #{m['id']} · the needle reads {m['reads']} · {m['street']}"
        + (f" · {'; '.join(m['notes'])}" if m["notes"] else ""),
        "  GM only until the pair sees it:",
        f"  What: {m['count']}× {m['kind']} (CR {m['cr']}, {m['size']} {m['type']}, "
        f"{m['align']}), {m['xp']:,} XP in all. Stat block: {stat}",
        f"  Where: {m['spot']}; {m['room']}; {m['feature']}.",
        f"  Disposition: {m['disposition']}.",
        f"  Coins on a kill: {m['xp'] // 10:,} GP.",
        f"  When it is settled: shift.py done {c['path']} kill|sent|failed",
    ])


# ---- The day -----------------------------------------------------------------------------

def free(c, seat, q):
    return (seat["holder"] and seat["back"] <= q and seat["off"] != weekday(q // 4)
            and not any(m["pair"] == seat["role"] for m in c["board"]))


def specialists(c, news):
    """Head Office takes what no pair on the roster could: over 10, or over the top level."""
    top = max([lvl(s) for s in c["seats"] if s["holder"]] or [0])
    for m in list(c["board"]):
        if not m["pair"] and (m["n"] > 10 or m["n"] > top):
            c["board"].remove(m)
            news.append(f"Head Office's specialists dealt with {what(m)}. Nobody here saw it done.")


def dispatch(c, news, rest=False):
    """Oldest first, then strongest: each waiting reading goes to the lowest-level free pair
    whose level is at least the reading, and who hasn't already come back without it."""
    out = []
    for m in sorted(c["board"], key=lambda m: (m["born"], -m["n"])):
        if m["pair"]:
            continue
        able = [s for s in c["seats"] if free(c, s, rnd(c)) and lvl(s) >= m["n"]
                and s["role"] not in m["tried"] and not (rest and s["role"] == c["player"])]
        if not able:
            news.append(f"#{m['id']} (reads {m['reads']}, {m['street']}) waits: no pair free "
                        "that can take it.")
            continue
        seat = min(able, key=lambda s: (lvl(s), s["n"]))
        m["pair"] = seat["role"]
        if seat["role"] == c["player"]:
            out.append(call_card(c, m))
        else:
            news.append(f"The {seat['role']} is sent to #{m['id']} (reads {m['reads']}, "
                        f"{m['street']}).")
    return out


def gain(c, seat, xp, news):
    before = lvl(seat)
    seat["holder"]["xp"] += xp
    if lvl(seat) > before:
        you = "YOUR PAIR: " if seat["role"] == c["player"] else ""
        news.append(f"{you}The {seat['role']} is level {lvl(seat)} now ({rank(lvl(seat))}), "
                    "and the automaton with them.")


def fall(c, rng, seat, m, news):
    h = seat["holder"]
    c["wall"].append({"role": seat["role"], "name": h["name"], "rank": rank(lvl(seat)),
                      "day": c["day"], "street": m["street"] if m else None,
                      "kind": m["kind"] if m else None})
    level = lvl(seat)
    seat["holder"], seat["vacant_level"] = None, level
    seat["arrives"] = c["day"] + (1 if seat["role"] == c["player"] else d(rng, VACANCY_DAYS))
    news.append(f"The {seat['role']}, {h['name']} ({rank(level)}), is dead"
                + (f", killed by {what(m)}" if m else "") + f". {seat['automaton']['name']} "
                f"went dark. A transfer takes the seat on {weekday(seat['arrives'])}.")


def resolve_npcs(c, rng, news):
    """The other pairs' calls of the round just ended. One d20 each; never a fight."""
    q = rnd(c)
    for m in list(c["board"]):
        if not m["pair"] or m["pair"] == c["player"]:
            continue
        seat = next(s for s in c["seats"] if s["role"] == m["pair"])
        hard, roll = m["n"] >= lvl(seat) - 1, d(rng, 20)
        m["pair"], m["seen"] = None, True
        who = f"The {seat['role']}"
        if hard and roll == 1:
            m["tried"].append(seat["role"])
            if d(rng, 6) <= NPC_DEATH_ON:
                fall(c, rng, seat, m, news)
            else:
                days = d(rng, 3)
                seat["back"] = q + 1 + 4 * days
                news.append(f"{who} was carried in from {what(m)}, badly hurt: off the street "
                            f"{days} day(s). It is still out there.")
            continue
        if (hard and roll in (4, 5)) or (not hard and roll == 3):
            m["tried"].append(seat["role"])
            news.append(f"{who} came back without {what(m)}. It is still out there.")
            continue
        hurt = (hard and roll in (2, 3)) or (not hard and roll <= 2)
        if hurt:
            seat["back"] = q + 2
        tail = " Hurt doing it: stays in for the next round." if hurt else ""
        c["board"].remove(m)
        if d(rng, 6) <= NPC_KILL_ON:
            news.append(f"{who} killed {what(m)}.{tail}")
            gain(c, seat, m["xp"], news)
        else:
            news.append(f"{who} brought {what(m)} in, and it was sent home.{tail}")


def trouble(c, rng, t, news):
    for m in list(c["board"]):
        if m["pair"] or t - m["born"] < OVERDUE_SLOTS:
            continue
        if m.get("troubles", 0) >= TROUBLE_CAP:
            c["board"].remove(m)
            news.append(f"TAKEN OFF THE PRECINCT: Head Office's specialists came for {what(m)} "
                        f"after {TROUBLE_CAP} days of trouble. The Auditor has written it down.")
            continue
        m["troubles"] = m.get("troubles", 0) + 1
        roll = d(rng, 6)
        name, text = TROUBLE[roll]
        news.append(f"OVERDUE #{m['id']} (reads {m['reads']}, {m['street']}, on the board since "
                    f"{when(m['born'])}): it {name}. {text}")
        if roll in (1, 3):
            label = {1: "berserk", 3: "painted over"}[roll]
            if label not in m["notes"]:
                m["notes"].append(label)
        elif roll == 2:
            twin = dict(m, id=c["next_id"], born=t, pair=None, tried=[], notes=[], troubles=0)
            c["next_id"] += 1
            c["board"].append(twin)
        elif roll == 4:
            c["board"].remove(m)
        elif roll == 5:
            m["n"] += 1
            m["reads"] = str(m["n"])
            if "maximum hit points" not in m["notes"]:
                m["notes"].append("maximum hit points")
        elif roll == 6:
            breach_die_until(c, rng, t, news)


def breach_die_until(c, rng, t, news):
    """An extra die that always brings something."""
    while not breach_die(c, rng, t, news):
        pass


def retire(c, rng, news):
    for s in c["seats"]:
        if s["holder"] and lvl(s) >= RETIRE_LEVEL:
            h = s["holder"]
            c["retired"].append({"role": s["role"], "name": h["name"], "day": c["day"]})
            you = (" THIS IS YOUR SEAT: the human plays the new Probationer; the seat's "
                   "relics went with the Inspector.") if s["role"] == c["player"] else ""
            news.append(f"The {s['role']}, {h['name']}, is called to Head Office, and "
                        f"{s['automaton']['name']} too. A Probationer takes the seat in the "
                        f"morning.{you}")
            s["holder"], s["vacant_level"], s["arrives"] = None, 1, c["day"] + 1


def arrivals(c, rng, news):
    for s in c["seats"]:
        if not s["holder"] and s["arrives"] is not None and s["arrives"] <= c["day"]:
            new_pair(c, rng, s, s["vacant_level"])
            you = " THIS IS YOUR SEAT (run `show`)." if s["role"] == c["player"] else ""
            news.append(f"New on the seat: {pair_line(s)}{you}")


def step(c, rest=False):
    """Move the day on one round. Returns (headline, news, the player's call cards)."""
    if any(m["pair"] == c["player"] for m in c["board"]):
        sys.exit(f"Your call is still open. Settle it first:\n  shift.py done {c['path']} "
                 "kill|sent|failed")
    news, r = [], c["round"]
    if r == 0:
        c["day"] += 1
    rng = random.Random(f"{c['seed']}:{c['day']}:{r}")
    today = f"day {c['day']}, {weekday(c['day'])}"
    if r == 0:
        c["round"] = 1
        arrivals(c, rng, news)
        for m in c["board"]:
            m["tried"] = []  # a new day: a pair that came back without it may be sent again
        for _ in range(BATCH):
            breach_die(c, rng, half(c), news)
        off = [f"the {s['role']}" for s in c["seats"] if s["off"] == weekday(c["day"])]
        if off:
            news.insert(0, f"Day off: {' and '.join(off)}.")
        head = f"MORNING · {today}, 6 am"
    elif r < 4:
        resolve_npcs(c, rng, news)
        c["round"] = r + 1
        head = f"{['MID-MORNING', 'LUNCH', 'MID-AFTERNOON'][r - 1]} · {today}"
    else:
        resolve_npcs(c, rng, news)
        for _ in range(BATCH):
            breach_die(c, rng, half(c), news)
        retire(c, rng, news)
        c["round"] = 0
        head = f"EVENING · {today}, 6 pm"
    specialists(c, news)
    cards = dispatch(c, news, rest) if c["round"] else []
    if r == 0:
        trouble(c, rng, half(c), news)
    c["news"] = [head] + news
    return head, news, cards


def next_hint(c):
    if any(m["pair"] == c["player"] for m in c["board"]):
        return f"Next: play the call, then `shift.py done {c['path']} kill|sent|failed`."
    after = ["the morning", "mid-morning", "lunch", "mid-afternoon", "the evening drink"]
    return (f"Next: `shift.py next {c['path']}` for {after[c['round']]}"
            + (" (add --rest to keep your pair in for that round)." if c["round"] < 4 else "."))


# ---- The player's verbs ------------------------------------------------------------------

def drop(rng, m):
    """Three kills in four leave something. The stronger the reading, the better the odds
    of a good one."""
    if d(rng, 20) > DROP_ON:
        return "Nothing left behind."
    weights = next(w for top, w in RARITY if m["n"] <= top)
    rarity = rng.choices(["Common", "Uncommon", "Rare", "Very Rare"], weights)[0]
    if rarity == "Common":
        item = rng.choice(["Potion of Healing"] * 4 + ["Spell Scroll (a level 1 spell, the "
                          "GM's pick from either of the pair's lists)", "Potion of Climbing"])
        return (f"DROP (Common, a consumable, not a relic): {item}. "
                      "See reference/srd/Magic Items/Varies/ or Common/.")
    plus = {"Uncommon": 1, "Rare": 2, "Very Rare": 3}[rarity]
    pool = [f.stem for f in sorted((SRD / "Magic Items" / rarity).glob("*.md"))]
    pool += [f"Weapon, +{plus} (a weapon one of the pair uses)", f"Shield, +{plus}",
             f"Wand of the War Mage, +{plus}",
             f"Potion of Healing ({['greater', 'superior', 'supreme'][plus - 1]})"]
    if plus > 1:
        pool.append(f"Armor, +{plus - 1} (armour one of the pair wears)")
    item = rng.choice(pool)
    return (f"DROP ({rarity}): {item}. reference/srd/Magic Items/{rarity}/ or Varies/. "
                  "If it is not a consumable it is a RELIC of the seat: dress it as a thing "
                  f"of the {m['kind']}'s world and add it to character.md.")


def done(c, outcome, xp, helpers):
    seat = player_seat(c)
    m = next((m for m in c["board"] if m["pair"] == c["player"]), None)
    if not m:
        sys.exit("The player's pair has no open call.")
    rng = random.Random(f"{c['seed']}:done:{m['id']}:{c['day']}:{c['round']}")
    m["pair"], m["seen"] = None, True
    out = []
    if outcome == "failed":
        m["tried"].append(c["player"])
        out.append(f"{what(m)} is still out there, back on the board. It goes to the next pair "
                   "up that is free, or waits. (`take` sends your pair back to it.)")
    else:
        c["board"].remove(m)
        out.append(f"#{m['id']} is off the board: " +
                   ("killed." if outcome == "kill" else "brought in and sent home."))
    share = (m["xp"] if xp is None else xp) if (outcome == "kill" or xp) else 0
    share //= helpers + 1
    if share:
        gain(c, seat, share, out)
        out.append(f"XP absorbed: {share:,}. Total {seat['holder']['xp']:,} "
                   f"(level {lvl(seat) + 1} at {THRESHOLD[lvl(seat) + 1]:,}).")
    if outcome == "kill":
        out.append(f"Coins: {m['xp'] // 10:,} GP.")
        out.append(drop(rng, m))
    c["news"].append("You: " + out[0])
    return out


def take(c, mid):
    seat = player_seat(c)
    m = next((m for m in c["board"] if m["id"] == mid), None)
    if not m:
        sys.exit(f"No reading #{mid} on the board.")
    if c["round"] == 0:
        sys.exit("Nobody is sent out at night. Run `next` for the morning first.")
    if not seat["holder"] or any(x["pair"] == c["player"] for x in c["board"]):
        sys.exit("The player's pair is not free to take it.")
    other = m["pair"]
    m["pair"] = c["player"]
    if c["player"] in m["tried"]:
        m["tried"].remove(c["player"])
    return ([f"The {other} is on it too: they fight beside you (settle with --helpers 1)."]
            if other else []) + [call_card(c, m)]


def died(c):
    seat = player_seat(c)
    if not seat["holder"]:
        sys.exit("The seat is already empty.")
    rng = random.Random(f"{c['seed']}:died:{c['day']}:{c['round']}")
    m = next((m for m in c["board"] if m["pair"] == c["player"]), None)
    if m:
        m["pair"], m["seen"] = None, True
        m["tried"].append(c["player"])
    news = []
    fall(c, rng, seat, m, news)
    news.append("The seat's relics are rebuilt on the Mechanic's bench for the transfer, who "
                "comes at the same level with a new automaton. Run `next` through the rest of "
                "today as news; `show` after the morning.")
    c["news"] += news
    return news


# ---- Files -------------------------------------------------------------------------------

def precinct_md(c):
    out = [f"# {c['precinct']} Precinct · day {c['day']}, {weekday(c['day'])}, {ROUND[c['round']]}", "",
           "## The seats", "",
           "| Seat | Rank | Level | Pair | Day off | Now |", "|---|---|---|---|---|---|"]
    for s in sorted(c["seats"], key=lambda s: -(lvl(s) if s["holder"] else 0)):
        if not s["holder"]:
            out.append(f"| the {s['role']} | | | empty | {s['off']} | a transfer comes "
                       f"{weekday(s['arrives'])} |")
            continue
        h, a = s["holder"], s["automaton"]
        on = next((m for m in c["board"] if m["pair"] == s["role"]), None)
        now = (f"out on #{on['id']}" if on else "day off" if s["off"] == weekday(c["day"])
               else "hurt, in" if s["back"] > rnd(c) else "in")
        you = " **(you)**" if s["role"] == c["player"] else ""
        out.append(f"| the {s['role']}{you} | {rank(lvl(s))} | {lvl(s)} | {h['class']} and "
                   f"{a['class']} automaton; {h['quirk']} | {s['off']} | {now} |")
    out += ["", "## The board", ""]
    if c["board"]:
        out += ["| # | Reads | Where | Since | Who | Notes |", "|---|---|---|---|---|---|"]
        for m in c["board"]:
            seen = [f"{m['count']}× {m['kind']}"] if m["seen"] else []
            tried = [f"the {r} came back without it" for r in m["tried"]]
            out.append(f"| {m['id']} | {m['reads']} | {m['street']} | {when(m['born'])} | "
                       f"{'the ' + m['pair'] if m['pair'] else 'no one'} | "
                       f"{'; '.join(seen + m['notes'] + tried)} |")
    else:
        out.append("Clear.")
    out += ["", "## Last heard", ""] + [f"- {n}" for n in c["news"]
                                         if not n.startswith(("YOUR CALL", "  "))]
    out += ["", "## The neighbourhoods", ""] + [f"- **{s['name']}**: {s['trait']}"
                                                 for s in c["streets"]]
    if c["wall"]:
        out += ["", "## The wall", ""] + [
            f"- the {w['role']}, {w['name']}, {w['rank']}, day {w['day']}"
            + (f", {w['street']}" if w["street"] else "") for w in c["wall"]]
    if c["retired"]:
        out += ["", "## Called to Head Office", ""] + [
            f"- the {r['role']}, {r['name']}, day {r['day']}" for r in c["retired"]]
    return "\n".join(out) + "\n"


def load(path):
    f = Path(path) / "campaign.json"
    if not f.exists():
        sys.exit(f"no campaign at {path}")
    c = json.loads(f.read_text())
    c["path"] = str(path)
    return c


def save(c, path):
    (Path(path) / "campaign.json").write_text(
        json.dumps({k: v for k, v in c.items() if k != "path"}, indent=1) + "\n")
    (Path(path) / "precinct.md").write_text(precinct_md(c))


def new(path, seed):
    rng = random.Random(seed)
    names = rng.sample(STREETS, 6)
    c = {"name": Path(path).name, "seed": seed, "path": str(path), "day": 0, "round": 0,
         "precinct": rng.choice(PRECINCTS), "seats": [], "board": [], "next_id": 1,
         "wall": [], "retired": [], "news": [],
         "streets": [{"name": n, "trait": t}
                     for n, t in zip(names, rng.sample(STREET_TRAITS, 6))]}
    for n, (role, level) in enumerate(zip(rng.sample(ROLES, 4), START_LEVELS), 1):
        seat = {"n": n, "role": role, "off": "Saturday" if n % 2 else "Sunday"}
        c["seats"].append(seat)
        new_pair(c, rng, seat, level)
        if n > 1:  # the others are partway through their level
            seat["holder"]["xp"] += rng.randrange((THRESHOLD[level + 1] - THRESHOLD[level]) // 2)
            seat["holder"]["since"] = -30 * level
    c["player"] = c["seats"][0]["role"]
    Path(path).mkdir(parents=True, exist_ok=True)
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=["new", "next", "done", "take", "died", "out", "show",
                                     "status"])
    ap.add_argument("campaign")
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--rest", action="store_true", help="next: keep the player's pair in")
    ap.add_argument("--to-call", action="store_true",
                    help="next: keep going, round after round, until the player's pair has "
                         "a call or news of its own (a week at most)")
    ap.add_argument("--xp", type=int, help="done: XP of what was killed, if not all of it")
    ap.add_argument("--helpers", type=int, default=0, help="done: others who fought beside")
    a = ap.parse_args()
    if a.verb == "new":
        if a.seed is None:
            sys.exit("new needs --seed N")
        c = new(a.campaign, a.seed)
        out = [f"{c['precinct']} Precinct.", show(c), "The other seats:"]
        out += ["- " + pair_line(s) for s in c["seats"][1:]]
    else:
        c = load(a.campaign)
        if a.verb == "next":
            out = []
            for _ in range(5 * TO_CALL_DAYS if a.to_call else 1):
                head, news, cards = step(c, a.rest)
                out += [head] + [f"- {n}" for n in news or ["Nothing new."]] + cards
                if cards or any("YOUR" in n for n in news):
                    break
            if not cards and c["round"]:
                out.append("No call for your pair this round.")
        elif a.verb == "done":
            if a.arg not in ("kill", "sent", "failed"):
                sys.exit("done needs kill, sent or failed")
            out = done(c, a.arg, a.xp, a.helpers)
        elif a.verb == "take":
            out = take(c, int(a.arg or 0))
        elif a.verb == "died":
            out = died(c)
        elif a.verb == "out":
            nxt = 4 * c["day"] + c["round"] if c["round"] else 4 * (c["day"] + 1)
            player_seat(c)["back"] = nxt + 4 * int(a.arg or 1)
            out = [f"Your pair is off the street for {int(a.arg or 1)} day(s)."]
        elif a.verb == "show":
            out = [show(c)]
        else:
            m = next((m for m in c["board"] if m["pair"] == c["player"]), None)
            out = [f"Day {c['day']}, {weekday(c['day'])}, {ROUND[c['round']]}."]
            out += [call_card(c, m)] if m else []
    save(c, a.campaign)
    print("\n".join(out))
    print(next_hint(c))


if __name__ == "__main__":
    main()
