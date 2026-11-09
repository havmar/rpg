# The setting

## The kingdom and the breaches

Somewhere in the kingdom, every day, the world tears. A **breach** is a place where another
reality has pushed through and stapled itself onto this one: a pocket of somewhere else,
with its own weather and its own people, sitting in a barley field. Where pirates come
through, there is suddenly a lake and a ship on it. Where a basilisk comes through, the
hedgerows are a warren of bones. Inside the breach the land folds into rooms, and at its
deepest point is the **rift**: the tear itself, a humming seam in the air that leads home for
anything that came through it and nowhere for anything that didn't.

Breaches are not evil and their denizens are not invaders. They are lost. Some of them know
it and want to go home; some are frightened and fight; some are hungry; some were monsters
where they came from and are monsters here. A breach left alone does one of two things. If
its denizens die or go home, it closes and the land heals in a day. If they don't, it
eventually collapses with them on this side of it, and then the county has pirates.

Nobody knows why it started, or why it is worse in some counties than others, or why a
breach's denizens so often match the level of whoever is nearest when it opens, as if the
world were offering a fair fight. The Capital has a college studying it. Every chapter has a
chronicler collecting records for that college. The answer, if there is one, is the long
question of the campaign, and the GM keeps it in `gm-secrets.md`.

**Wards.** Every settlement of any size has a ward stone and a ward: a circle inside which
the world holds its shape. A breach cannot open inside a ward, and a breach that opens beside
one does not warp the streets. Wards are why there is still a kingdom. They are narrative
only: no mechanic, no level, no saving throw. They keep settlements stable and cover nothing
else, no field, no road, no mill a kilometre out of town. That is what the Order is for.

## The Order and the Company

The **Order of the Gate** answers to the Crown and keeps a chapter, called a **Company**, in
every county, numbered and known by that number: the 3rd Company, the 11th. A Company has
exactly twenty dungeoneers, because that is what the Crown pays for, and it never has
enough, because a breach a month for each of them is less than the county opens.

The magic a denizen leaks when it dies is absorbed by whoever is there, and shared among
them if there are several. That is why there are no parties. One dungeoneer and one automaton
take everything a breach gives; four dungeoneers would take a quarter each and the Company
would train four times as slowly. The pair is doctrine.

**The ladder.** A dungeoneer is a **role** before they are a person: the Company has twenty
seats named after animals, the Lion, the Wolf, the Bear, the Stag, the Boar, the Hawk, the
Raven, the Owl, the Heron, the Fox, the Hare, the Badger, the Otter, the Adder, the Lynx, the
Ram, the Bull, the Hound, the Crane and the Wren, and the roster always runs one seat per
rank from Recruit to Lord Marshal. A dungeoneer is addressed by rank and spoken of by role:
"the Fox is late", "the new Lion". After twenty months a Lord Marshal is done and leaves for
the Capital, where the Order's veterans go and from which they do not write. Every month, one
or two don't come back, and the seat is filled the month after by a recruit at the rank the
seat has reached.

**The chapter house** is in the county's seat, a city or the largest town. It has: the
**Marshal**, who sets the board on the first of the month and sends people to die by it; the
**chronicler**, who wants every breach described for the college and keeps the wall; the
**quartermaster**, who issues gear and magic items at the ranks the Order allows; the
**artificer**, who rebuilds automatons and talks to them more than to people; the **Crown's
liaison**, who counts; and the **wall** itself, where the fallen are named by role, name and
month. The GM writes these people in `county.md` as play meets them, one line each: who they
are, what they want.

**The board.** On the first of each month the scouts' reports are chalked up: a breach's
reported level, its kind, the nearest settlement, the days to get there. One per role, at
the role's rank; the rest are listed too, with no one beside them. The Marshal does not
discuss the board. Scouts are sometimes wrong by a level.

## Automatons

An **automaton** is a magical construct in the shape of a person, built by the Order's
artificers from a design the college does not share. Each is bound to one dungeoneer at a
time by a rite at the chapter house, and from then on it gains what its partner gains: a
level when they level, nothing when they don't. It absorbs no breach-magic of its own, which
is the point. The pair is the party.

They are **people**, with the manner of a very good servant: formal, unhurried, dry,
observant, deferential in address and immovable in opinion. They call their partner by rank
("if the Yeoman would step back"). They narrate tactics as service ("I have taken the liberty
of oiling the stair"). They count kills as matters attended to and deportations as matters
resolved, and most of them, if asked, prefer the latter. They are **programmed to cheese**:
the artificers' protocol of economy makes an automaton propose, always, the cheapest legal
way to end a fight, and it will say so before every fight unless told to hold its tongue.

An automaton **remembers**. Its core carries every partner it has had, and a recruit who
inherits a dead dungeoneer's automaton inherits its grief, expressed as correctness. "The
previous Fox preferred the left-hand stair. I mention it only for completeness."

### Species: Automaton

For the automaton's character sheet, in place of an SRD species.

- **Creature Type:** Humanoid (built, not born; healed and affected as a Humanoid).
- **Size:** Medium. **Speed:** 9 m (30 ft).
- **Constructed Resilience.** Advantage on saving throws against the Poisoned condition, and
  Resistance to Poison damage. Immune to disease. Needs no food, drink or air. Doesn't sleep
  and can't be put to sleep by magic.
- **Sentry's Rest.** A Long Rest is 6 hours spent motionless and aware instead of 8 asleep.
- **Integrated Protection.** +1 to AC. Armour worn becomes part of the body: an hour to don
  or doff, and it can't be removed against the automaton's will.
- **Protocol.** Proficiency in one skill (rolled by `month.py`) and with Tinker's Tools.
- **Bound.** Gains no XP; is always the level of its partner. Its **core** (1 kg) survives the
  body's destruction and holds its memory. A rebuilt body costs the Company the month's
  downtime and nothing else.
- **Languages:** Common and one other.

## The county

The Company's county is rolled by `month.py new`: a name, a seat (a city if there is one,
else the largest town), one or two towns, three to five villages, each with the days of
travel from the chapter house and one thing it's known for. The GM fills it in as play goes
there and never all at once. Between settlements is the countryside: fields, woods, roads,
mills, shrines, farms, none of it warded, all of it where breaches open.

A breach's days on the board are travel from the chapter house. Travel is a scene if the
county has something to show (a loose breach's leavings, a settlement's trouble, another pair
on the road) and a line if not.

**Loose denizens.** Every month some breaches get no one, and some get someone who dies in
them. At month's end those collapse and whatever was alive inside is in the county: pirates
on the river road, a hill giant in the quarry, a swarm in the mill. They are the overworld's
monsters and the downtime's work. Most groups go to ground within a few months, join the
county (the pirates run the ferry now), or die of it; the GM says which when the script says
they're no longer a problem. Until then they are trouble, and the only XP outside a breach.

## Coins and things

A denizen's room holds coins worth a tenth of its XP, in the currency of wherever it came
from, which the county's moneychangers take at face because the Company vouches for it. Every
breach also leaves one **thing** of its reality behind, which the GM names in a few words
when the breach closes: a ship's bell, a basilisk's dulled eye, a pirate's letter in no
language. They are worth little and dungeoneers keep them.
