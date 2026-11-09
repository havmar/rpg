#!/usr/bin/env python3
"""The Company's month: the roster of twenty roles, the board of breaches, deaths, levels,
graduations and recruits. All the dice of the month that aren't the player's are rolled here.

  python3 breach/tools/month.py new breach/campaigns/<name> --seed 7 [--player-rank 1] [--company 9]
  python3 breach/tools/month.py show breach/campaigns/<name> [--role Wren]
  python3 breach/tools/month.py board breach/campaigns/<name>
  python3 breach/tools/month.py end breach/campaigns/<name> [--player-died] [--player-left-open]

`new` writes campaign.json (the GM's record, with the breaches' true levels and seeds),
roster.md (the player's view: the roster, the board, what's loose, the wall) and county.md
(the settlements; written once, the GM adds to it by hand). `end` resolves the month and
rolls the next board, then rewrites roster.md. The ladder holds: one role per rank, 1 to 20.

The player's own breach is generated from the board's seed:
  python3 breach/tools/gen_breach.py --seed <seed> --level <true level> --reported <rank>
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_breach  # noqa: E402

ROLES = ["Lion", "Wolf", "Bear", "Stag", "Boar", "Hawk", "Raven", "Owl", "Heron", "Fox",
         "Hare", "Badger", "Otter", "Adder", "Lynx", "Ram", "Bull", "Hound", "Crane", "Wren"]

RANKS = [None, "Recruit", "Prentice", "Yeoman", "Lancer", "Corporal", "Sergeant",
         "Sergeant-Major", "Cornet", "Ensign", "Lieutenant", "Captain", "Senior Captain",
         "Major", "Warden", "High Warden", "Commander", "Knight-Commander", "Colonel",
         "Marshal", "Lord Marshal"]

SPECIES = ["Elf", "Gnome", "Human", "Orc", "Tiefling"]
BACKGROUNDS = ["Acolyte", "Criminal", "Sage", "Soldier"]
FRONT = [("Barbarian", "Berserker"), ("Fighter", "Champion"), ("Paladin", "Devotion"),
         ("Monk", "Open Hand"), ("Ranger", "Hunter"), ("Cleric", "Life")]
BACK = [("Wizard", "Evoker"), ("Sorcerer", "Draconic"), ("Warlock", "Fiend"),
        ("Bard", "Lore"), ("Rogue", "Thief"), ("Druid", "Land")]
# Where a class puts its rolled scores, best first.
PRIORITY = {
    "Barbarian": "STR CON DEX WIS CHA INT", "Fighter": "STR CON DEX WIS INT CHA",
    "Paladin": "STR CHA CON WIS DEX INT", "Monk": "DEX WIS CON STR INT CHA",
    "Ranger": "DEX WIS CON STR INT CHA", "Cleric": "WIS CON STR DEX CHA INT",
    "Wizard": "INT DEX CON WIS CHA STR", "Sorcerer": "CHA CON DEX WIS INT STR",
    "Warlock": "CHA CON DEX WIS INT STR", "Bard": "CHA DEX CON WIS INT STR",
    "Rogue": "DEX CON INT WIS CHA STR", "Druid": "WIS CON DEX INT CHA STR",
}

NAMES = {
    "Elf": ["Aelar", "Birel", "Caelynn", "Dayereth", "Enna", "Galinndan", "Ielenia", "Keyleth",
            "Laucian", "Mialee", "Naivara", "Quarion", "Riardon", "Shanairra", "Thia", "Varis"],
    "Gnome": ["Alston", "Bimpnottin", "Carlin", "Dimble", "Ellyjobell", "Fonkin", "Gimble",
              "Loopmottin", "Nissa", "Orryn", "Roondar", "Seebo", "Tana", "Warryn", "Zanna", "Wrenn"],
    "Human": ["Ansel", "Bertha", "Cuthbert", "Dagny", "Edric", "Fenna", "Gilles", "Hilde",
              "Isolde", "Jorund", "Katla", "Leofric", "Maud", "Osric", "Piers", "Rowena"],
    "Orc": ["Besk", "Dench", "Feng", "Gell", "Holg", "Imsh", "Kansif", "Lagazi", "Mord",
            "Neega", "Ovak", "Ront", "Shump", "Thokk", "Vola", "Yevelda"],
    "Tiefling": ["Akmenos", "Bryseis", "Damaia", "Ekemon", "Kallista", "Leucis", "Makaria",
                 "Mordai", "Nemeia", "Orianna", "Pelaios", "Rieta", "Skamos", "Therai", "Zaidon", "Verin"],
}
SURNAMES = ["Ashcombe", "Brandt", "Coldwater", "Dunmore", "Fairweather", "Greaves", "Halloran",
            "Ironside", "Kettering", "Lowry", "Marsh", "Northcote", "Oxley", "Pendry", "Quayle",
            "Rooke", "Sallow", "Thorne", "Underhill", "Vance", "Whitlock", "Yarrow", "of the Fen",
            "the Younger", "Half-Orc", "Nine-Fingers", "Redhand", "Stillwater", "Tallow", "Wick"]
PRONOUNS = ["he/him"] * 9 + ["she/her"] * 9 + ["they/them"] * 2

AUTOMATON_NAMES = ["Alder", "Basset", "Carrow", "Dunstan", "Ellery", "Fenwick", "Garrow",
                   "Hollis", "Ives", "Jessop", "Kemble", "Lowell", "Marlow", "Nettle", "Oakes",
                   "Pennywhistle", "Quill", "Rookwood", "Sedge", "Tamsin", "Upton", "Verity",
                   "Wimbourne", "Yately", "Abbott", "Brisket", "Candlewick", "Dorrit", "Evershed",
                   "Faraday", "Gaskell", "Hobbes", "Inchbald", "Jarvis", "Kettle", "Lampwick"]
PROTOCOL_SKILLS = ["Perception", "Insight", "Medicine", "History", "Investigation", "Survival",
                   "Persuasion", "Arcana", "Athletics", "Stealth", "Animal Handling", "Sleight of Hand"]

TRAITS = [
    "wants to graduate before an older sibling who is already in the Capital",
    "keeps a tally of deportations and thinks kills are a failure of manners",
    "gambles with the quartermaster's clerks and owes them",
    "sends every coin home to a village the board never names",
    "was recruited out of a cell and the Company knows it",
    "collects a knick-knack from every breach and labels them",
    "thinks the breaches are a punishment and prays before the board",
    "is courting someone in a settlement two days out",
    "argues with their automaton in public and loses",
    "has buried three partners' cores and visits them",
    "wants the Marshal's job and says so",
    "writes the Company's songs, badly",
    "drinks after every breach, not before",
    "is studying the rifts and asks the chronicler for records",
    "fosters the children of the fallen when no one else will",
    "never takes a stowaway's side and never explains why",
    "has a running bet with another role on who graduates first",
    "cheats at cards, is caught, is forgiven",
    "trains recruits unasked and is good at it",
    "believes the automatons are people and treats them so",
    "lost a settlement to a loose breach and hasn't forgiven the board",
    "is the Marshal's favourite and hates it",
    "deserted once, came back, and was allowed to",
    "speaks to every peaceful denizen first, whatever the risk",
    "sells breach coins to collectors in the city for twice their worth",
    "has a map of every breach the Company has closed, pinned to a wall",
    "is deaf in one ear from a thunderclap and says the tin hears for two",
    "takes the smallest room, eats last, and is adored for it",
    "wants out, and has one month left before they can resign",
    "has never been in a city and talks about the Capital constantly",
]

CITIES = ["Kingsmere", "Thornmouth", "Oldbridge", "Castelgard"]
TOWNS = ["Ashford", "Wetherby", "Marlow", "Hadley", "Coombe", "Fenwick", "Rushden", "Selby"]
VILLAGES = ["Little Marsh", "Hogsbarrow", "Nether Wick", "Cold Harbour", "Elmstead", "Upper Pike",
            "Saltby", "Duck End", "Threefords", "Hollins", "Barrowden", "Goose Green", "Wyvern Cross",
            "Mill Hollow", "Crookham", "Sorrel's Reach"]
COUNTY = ["Ashcombe", "Wealdmoor", "the Fenmarch", "Harrowdale", "Coldshire", "Brackenfold"]
SETTLEMENT_TRAITS = [
    "market every tenth day", "a shrine with a relic that hums when a breach is near",
    "a ferry and a toll", "a mill and a miller who sells rumours", "a garrison of six, bored",
    "a famous inn", "a hedge-wizard who dislikes the Company", "an orchard and a cider press",
    "a quarry", "a horse fair in spring", "a reeve who keeps immaculate records",
    "a bridge that is the only one for a day's ride", "a leper house outside the ward",
    "a tannery everyone smells before they see", "a boarding school for the children of the fallen",
    "a tower, empty, that the ward stone sits in", "sheep, and nothing but sheep",
    "a shipwright, two days from any sea", "a hiring hall for the Company's scouts",
    "a monastery that brews", "a smuggler's reputation", "a wall that was never finished",
]


def d(rng, n):
    return rng.randint(1, n)


def plural(name):
    """Rough English plural of an SRD monster name: Wolf -> Wolves, Harpy -> Harpies."""
    if name.endswith(("s", "x", "ch", "sh")):
        return name + "es"
    if name.endswith("f"):
        return name[:-1] + "ves"
    if name.endswith("fe"):
        return name[:-2] + "ves"
    if name.endswith("y") and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    if name.endswith((" Folk", " People", " Rex")):
        return name
    return name + "s"


def scores(rng, cls):
    rolled = sorted((sum(sorted(rng.randint(1, 6) for _ in range(4))[1:]) for _ in range(6)),
                    reverse=True)
    return dict(zip(PRIORITY[cls].split(), rolled))


def new_automaton(rng, side, used_names, month, partner):
    name = rng.choice([n for n in AUTOMATON_NAMES if n not in used_names] or AUTOMATON_NAMES)
    used_names.add(name)
    cls, sub = rng.choice(BACK if side == "Front" else FRONT)
    return {"name": name, "side": "Back" if side == "Front" else "Front", "class": cls,
            "subclass": sub, "protocol_skill": rng.choice(PROTOCOL_SKILLS),
            "scores": scores(rng, cls), "built": month, "partners": [partner]}


def new_dungeoneer(rng, month, used_traits, side=None):
    """A recruit. `side` is forced when they inherit an automaton: the pair covers both."""
    species = rng.choice(SPECIES)
    if side is None:
        side = "Front" if d(rng, 2) == 1 else "Back"
    cls, sub = rng.choice(FRONT if side == "Front" else BACK)
    trait = rng.choice([t for t in TRAITS if t not in used_traits] or TRAITS)
    used_traits.add(trait)
    return {"name": f"{rng.choice(NAMES[species])} {rng.choice(SURNAMES)}",
            "pronouns": rng.choice(PRONOUNS), "species": species,
            "background": rng.choice(BACKGROUNDS), "side": side, "class": cls, "subclass": sub,
            "scores": scores(rng, cls), "since": month, "trait": trait}


def new_county(rng):
    name = rng.choice(COUNTY)
    sets = []
    if d(rng, 2) == 1:
        sets.append({"name": rng.choice(CITIES), "kind": "city"})
    for n in rng.sample(TOWNS, d(rng, 2) + 1):
        sets.append({"name": n, "kind": "town"})
    for n in rng.sample(VILLAGES, d(rng, 3) + 2):
        sets.append({"name": n, "kind": "village"})
    seat = sets[0]["name"]  # the city if there is one, else the first town
    traits = rng.sample(SETTLEMENT_TRAITS, len(sets))
    for i, s in enumerate(sets):
        s["days"] = 0 if s["name"] == seat else d(rng, 3)
        s["trait"] = traits[i]
    sets.sort(key=lambda s: (s["days"], s["name"]))
    return {"name": name, "seat": seat, "settlements": sets}


def roll_board(c, rng):
    """One breach per role at its rank (true level one higher on a 6), plus 1d4+1 that no one
    can be sent to. The scouts' report is the kind and the rank; the true level stays here."""
    board = []
    sets = c["county"]["settlements"]
    for r in c["roster"]:
        level = r["rank"]
        true = min(20, level + 1) if d(rng, 6) == 6 else level
        s = rng.choice(sets)
        seed = rng.randrange(1, 1_000_000)
        board.append({"role": r["role"], "reported": level, "level": true, "near": s["name"],
                      "days": s["days"] + d(rng, 2) - 1, "seed": seed,
                      "kind": gen_breach.principal_for(true, seed)["name"]})
    for _ in range(d(rng, 4) + 1):
        level = min(d(rng, 20), d(rng, 20))  # the unhandled skew low; the dial is here
        s = rng.choice(sets)
        seed = rng.randrange(1, 1_000_000)
        board.append({"role": None, "reported": level, "level": level, "near": s["name"],
                      "days": s["days"] + d(rng, 2) - 1, "seed": seed,
                      "kind": gen_breach.principal_for(level, seed)["name"]})
    board.sort(key=lambda b: (-b["reported"], b["near"]))
    return board


def new(path, seed, player_rank, company):
    rng = random.Random(seed)
    used_names, used_traits = set(), set()
    roster = []
    ranks = list(range(1, 21))
    rng.shuffle(ranks)
    for role, rank in zip(ROLES, ranks):
        dg = new_dungeoneer(rng, 2 - rank, used_traits)  # a Recruit joined this month
        dg["role"], dg["rank"] = role, rank
        dg["automaton"] = new_automaton(rng, dg["side"], used_names, 2 - rank, dg["name"])
        roster.append(dg)
    roster.sort(key=lambda r: r["rank"])
    player = next(r for r in roster if r["rank"] == player_rank)
    c = {"name": path.name, "seed": seed, "company": f"{company or d(rng, 12) + 1}th Company",
         "month": 1, "player": player["role"], "roster": roster, "county": new_county(rng),
         "loose": [], "fallen": [], "graduated": [], "news": []}
    c["company"] = c["company"].replace("1th", "1st").replace("2th", "2nd").replace("3th", "3rd") \
        .replace("11st", "11th").replace("12nd", "12th").replace("13rd", "13th")
    c["board"] = roll_board(c, rng)
    path.mkdir(parents=True, exist_ok=True)
    save(c, path)
    (path / "county.md").write_text(county_md(c))
    return c


def end(c, rng, player_died=False, player_left_open=False):
    news = []
    roster = c["roster"]
    player = c["player"]
    month = c["month"]
    used_names = {r["automaton"]["name"] for r in roster}
    used_traits = {r["trait"] for r in roster}
    by_role = {b["role"]: b for b in c["board"] if b["role"]}

    # Who dies among the other nineteen: 1d2 deaths, 1d20 for which rank, rerolling the
    # player's role and a repeat.
    dead = set()
    for _ in range(d(rng, 2)):
        for _try in range(100):
            rank = d(rng, 20)
            victim = next(r for r in roster if r["rank"] == rank)
            if victim["role"] != player and victim["role"] not in dead:
                dead.add(victim["role"])
                break

    def go_loose(b, why):
        c["loose"].append({"kind": b["kind"], "level": b["level"], "near": b["near"],
                           "since": month, "why": why})

    for r in roster:
        b = by_role.get(r["role"])
        died = r["role"] in dead or (r["role"] == player and player_died)
        if died:
            c["fallen"].append({"role": r["role"], "name": r["name"], "rank": r["rank"],
                                "month": month, "near": b["near"] if b else None,
                                "kind": b["kind"] if b else None})
            if b:
                go_loose(b, f"the {r['role']} fell there")
            news.append(f"The {r['role']}, {r['name']} ({RANKS[r['rank']]}), died in the "
                        f"{b['kind'] if b else 'breach'} breach near {b['near'] if b else '?'}. "
                        f"The automaton {r['automaton']['name']} came home.")
            new_rank = 1 if r["rank"] == 20 else r["rank"] + 1
            recruit = new_dungeoneer(rng, month + 1, used_traits,
                                     "Back" if r["automaton"]["side"] == "Front" else "Front")
            recruit["role"], recruit["rank"] = r["role"], new_rank
            recruit["automaton"] = r["automaton"]
            recruit["automaton"]["partners"].append(recruit["name"])
            r.clear()
            r.update(recruit)
            news.append(f"The new {r['role']} is {r['name']} ({r['pronouns']}, {r['species']} "
                        f"{r['class']}), {RANKS[new_rank]}, paired with {r['automaton']['name']}.")
            continue
        if r["role"] == player and player_left_open and b:
            go_loose(b, "the player left it open")
            news.append(f"Your breach near {b['near']} was left open: its {plural(b['kind'])} are loose.")
        if r["rank"] == 20:
            c["graduated"].append({"role": r["role"], "name": r["name"], "month": month})
            news.append(f"The {r['role']}, {r['name']}, Lord Marshal, has graduated and left for "
                        f"the Capital. {r['automaton']['name']} stays with the Company.")
            recruit = new_dungeoneer(rng, month + 1, used_traits,
                                     "Back" if r["automaton"]["side"] == "Front" else "Front")
            recruit["role"], recruit["rank"] = r["role"], 1
            recruit["automaton"] = r["automaton"]
            recruit["automaton"]["partners"].append(recruit["name"])
            r.clear()
            r.update(recruit)
            news.append(f"The new {r['role']} is {r['name']} ({r['pronouns']}, {r['species']} "
                        f"{r['class']}), Recruit, paired with {r['automaton']['name']}.")
        else:
            r["rank"] += 1

    for b in c["board"]:
        if b["role"] is None:
            go_loose(b, "no one was sent")
    unhandled = [b for b in c["board"] if b["role"] is None]
    if unhandled:
        news.append("Unhandled this month, now loose: " + "; ".join(
            f"{plural(b['kind'])} (level {b['level']}) near {b['near']}" for b in unhandled) + ".")

    # Loose denizens settle on a 1 to 3: they've gone to ground, joined the county, or died
    # of it. The GM says which.
    still = []
    for lo in c["loose"]:
        if lo["since"] < month and d(rng, 6) <= 3:
            news.append(f"The {plural(lo['kind'])} loose near {lo['near']} since month {lo['since']} "
                        f"are no longer a problem; the GM says what became of them.")
        else:
            still.append(lo)
    c["loose"] = still

    c["month"] = month + 1
    c["news"] = news
    c["board"] = roll_board(c, rng)
    return news


def save(c, path):
    (path / "campaign.json").write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n")
    (path / "roster.md").write_text(roster_md(c))


def load(path):
    return json.loads((path / "campaign.json").read_text())


def roster_md(c):
    out = [f"# The {c['company']} · {c['county']['name']} · Month {c['month']}", "",
           f"You are **the {c['player']}**. The ladder: one role per rank, every survivor a rank "
           "higher each month.", "",
           "| Rank | | Role | Dungeoneer | Species · class | Automaton · class | Since |",
           "|---|---|---|---|---|---|---|"]
    for r in sorted(c["roster"], key=lambda r: -r["rank"]):
        you = " **(you)**" if r["role"] == c["player"] else ""
        a = r["automaton"]
        since = f"month {r['since']}" if r["since"] >= 1 else f"{1 - r['since']} months before"
        out.append(f"| {r['rank']} | {RANKS[r['rank']]} | **{r['role']}**{you} | {r['name']} "
                   f"({r['pronouns']}) | {r['species']} {r['class']} ({r['subclass']}) | "
                   f"{a['name']} · {a['class']} ({a['subclass']}) | {since} |")
    out += ["", f"## The board, month {c['month']}", "",
            "One breach per role, at its rank; the rest have no one to send. The scouts' "
            "report is the kind and the level; scouts are sometimes wrong.", "",
            "| Level | Kind | Near | Days | Assigned |", "|---|---|---|---|---|"]
    for b in c["board"]:
        who = f"the {b['role']}" if b["role"] else "*no one to send*"
        if b["role"] == c["player"]:
            who = f"**the {b['role']} (you)**"
        out.append(f"| {b['reported']} | {b['kind']} | {b['near']} | {b['days']} | {who} |")
    if c["loose"]:
        out += ["", "## Loose in the county", "",
                "Breaches no one closed. The opening is gone; the denizens are not. Hunting "
                "them is a downtime move.", ""]
        for lo in c["loose"]:
            out.append(f"- {plural(lo['kind'])} of a level {lo['level']} breach near {lo['near']}, "
                       f"since month {lo['since']} ({lo['why']}).")
    if c["news"]:
        out += ["", f"## News of month {c['month'] - 1}", ""]
        out += [f"- {n}" for n in c["news"]]
    if c["fallen"]:
        out += ["", "## The wall", ""]
        for f in c["fallen"]:
            out.append(f"- Month {f['month']}: the {f['role']}, {f['name']}, {RANKS[f['rank']]}, "
                       f"in the {f['kind']} breach near {f['near']}.")
    if c["graduated"]:
        out += ["", "## Gone to the Capital", ""]
        out += [f"- Month {g['month']}: the {g['role']}, {g['name']}." for g in c["graduated"]]
    return "\n".join(out) + "\n"


def county_md(c):
    co = c["county"]
    out = [f"# {co['name']}", "",
           f"The {c['company']}'s county. The chapter house is in **{co['seat']}**. Days are travel "
           "from the chapter house. Wards keep a settlement's streets as they were when a breach "
           "opens nearby; they are narrative, not a mechanic, and they cover no field or road.", "",
           "| Settlement | Kind | Days | Known for |", "|---|---|---|---|"]
    for s in co["settlements"]:
        out.append(f"| {s['name']} | {s['kind']} | {s['days']} | {s['trait']} |")
    out += ["", "## People of the chapter house", "",
            "The GM writes these as play meets them: the Marshal who sets the board, the "
            "chronicler, the quartermaster, the artificer who rebuilds automatons, the Crown's "
            "liaison. One line each: who they are and what they want.", "",
            "## GM notes", ""]
    return "\n".join(out) + "\n"


def pair_md(r):
    a = r["automaton"]
    sc = " ".join(f"{k} {v}" for k, v in r["scores"].items())
    asc = " ".join(f"{k} {v}" for k, v in a["scores"].items())
    return "\n".join([
        f"**The {r['role']}** · rank {r['rank']} {RANKS[r['rank']]} · since month {r['since']}",
        f"- Dungeoneer: {r['name']} ({r['pronouns']}), {r['species']} {r['background']}, "
        f"{r['side']}: {r['class']} ({r['subclass']}). Scores {sc}.",
        f"- {r['trait'][0].upper()}{r['trait'][1:]}.",
        f"- Automaton: {a['name']}, {a['side']}: {a['class']} ({a['subclass']}), protocol skill "
        f"{a['protocol_skill']}. Scores {asc}. Built month {a['built']}; partners: "
        + ", ".join(a["partners"]) + ".",
    ])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=["new", "show", "board", "end"])
    ap.add_argument("campaign", type=Path)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--player-rank", type=int, default=1)
    ap.add_argument("--company", type=int)
    ap.add_argument("--role")
    ap.add_argument("--player-died", action="store_true")
    ap.add_argument("--player-left-open", action="store_true")
    a = ap.parse_args()

    if a.verb == "new":
        if a.seed is None:
            sys.exit("new needs --seed (roll it: roll.py 1d1000)")
        if (a.campaign / "campaign.json").exists():
            sys.exit(f"{a.campaign} already exists")
        c = new(a.campaign, a.seed, a.player_rank, a.company)
        print(f"{c['company']}, {c['county']['name']}, seat {c['county']['seat']}. You are the "
              f"{c['player']}.\n")
        print(pair_md(next(r for r in c["roster"] if r["role"] == c["player"])))
        print(f"\nWrote {a.campaign}/campaign.json, roster.md, county.md.")
        return
    c = load(a.campaign)
    if a.verb == "show":
        roles = [r for r in c["roster"] if not a.role or r["role"].lower() == a.role.lower()]
        print("\n\n".join(pair_md(r) for r in sorted(roles, key=lambda r: r["rank"])))
    elif a.verb == "board":
        for b in c["board"]:
            who = f"the {b['role']}" if b["role"] else "no one"
            true = f" (truly {b['level']})" if b["level"] != b["reported"] else ""
            print(f"level {b['reported']}{true} · {b['kind']} · near {b['near']}, {b['days']} day(s) · "
                  f"{who} · seed {b['seed']}")
    elif a.verb == "end":
        rng = random.Random(f"{c['seed']}:{c['month']}")
        news = end(c, rng, a.player_died, a.player_left_open)
        save(c, a.campaign)
        print(f"Month {c['month'] - 1} ends.\n")
        print("\n".join(f"- {n}" for n in news))
        print(f"\nMonth {c['month']}: the board is in roster.md; your breach:")
        b = next(b for b in c["board"] if b["role"] == c["player"])
        print(f"  level {b['reported']} (truly {b['level']}) · {b['kind']} · near {b['near']}, "
              f"{b['days']} day(s) · seed {b['seed']}")
        print(f"  python3 breach/tools/gen_breach.py --seed {b['seed']} --level {b['level']} "
              f"--reported {b['reported']}")


if __name__ == "__main__":
    main()
