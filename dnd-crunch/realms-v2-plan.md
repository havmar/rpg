# Realms v2: factions with assets (a plan)

**Status: implemented 2026-10-24.** The rules are `realms.md` (v2) and the engine
`tools/realms.py`; v1 moved to `realms-v1.md` and `tools/realms_v1.py`, where the `realms`
campaign still plays. The new campaign is `campaigns/realms2` (seed 8). Where the build
differs from this plan, `realms.md` wins; the main differences are listed in section 14,
the sim numbers are in `realms.md` section 12, and section 11 below now says what was
checked against the book. This document stays as the design record.

## 1. Why a second version

Five months of play (by the AI, watched by the human) showed what works and what doesn't.

**Works:**
- Fights are D&D. They are the best part and must stay that way.
- One currency: dungeon loot and realm treasuries are both GP, so a good delve changes the
  domain.
- The script runs the world; the GM only feeds it Morten's month.

**Doesn't:**
- **Illegible.** Cunning is a bare number; "Brutal" names an action nobody remembers;
  rivals are six more names from month 1; the roll log hides the plan. The human couldn't
  follow the domain turns.
- **War means nothing.** Only good rulers care about it; bad rulers attack you either way.
  Striking Kallista "started a war" that changed nothing.
- **Funding is a loophole.** The court may back a coup only for a rival "funded this month",
  with no minimum, so 1 GP unlocks it. Gold should *be* the support, not a key.
- **Home-made procedures.** v1 took the stat names from *Worlds Without Number* (Force,
  Cunning, Wealth) but not the structure that makes them concrete. The result is a system
  of our own with no reference to argue with.

The fix in this plan: adapt the WWN faction rules properly, because their core unit, the
**asset** (a named thing on the map: a militia, a spy ring, a caravan), is exactly what the
domain game lacks, and because **every asset can cash out as a D&D fight** when Morten goes
after it in person.

**Source.** The structure below follows the faction chapter of *Worlds Without Number*
(free edition), which is the same engine as *Stars Without Number*. The rules text is not
copied; the mechanics are restated and refitted to a 20-hex map. **Every number marked
"check" is from memory and must be checked against the book before coding;** where ours
deliberately differ from the book, the table in section 11 says so.

Three other decisions from the same discussion, recorded here so they aren't lost:
- **A map UI** (an artifact page) is planned in its own session. Section 9 says what the
  data must expose for it.
- **Display fixes** apply whatever the rules: bad/good labels, tags as verbs, the plan
  before the log, and a report filtered to what Morten can know.
- **Direct adaptation beats invention.** When a question comes up during the build, the
  answer is "what does WWN do?", and only then "what fits the map?".

## 2. What stays from v1

- The map: 4 × 5 flat-topped hexes, one level per hex (1–20), biomes, two rivers, two
  lakes, river edges giving defenders +1 where a roll crosses one.
- Hex income: **level × 10 GP a month** to the holder. (v1's income, kept instead of the
  book's attribute-based income, so the map stays the thing worth fighting over.)
- Six peoples, six realms, named leaders with titles, a claim bonus for a people's own hex.
- Morten's month then the domain turn; 1 day per hex; wandering checks; the 20-floor dungeon
  under the hexes; Delve; death ends the month and sends him home.
- The tower on the level 1 hex, warded against conquest.
- Rumours when Morten is in or next to a realm.
- `realms.py` owns `realms.json`; `world.md` is rendered from it; `--dry-run` first.

Dropped: mirrors as standing factions, the court and its points, "at war" as a flag, Build
as the only way to grow, Enslave/Raid as battle types. Each has a replacement below.

## 3. A faction

Every realm is a faction, and so is the tower. A faction has:

| Field | What it is |
|---|---|
| **Force** 1–8 | its armies and the fear of them |
| **Cunning** 1–8 | its spies, informers and friends in the right places |
| **Wealth** 1–8 | its trade, land and coffers |
| **HP** | how far it is from collapse: **4 + bonus per attribute** (table, section 11; check) |
| **Treasury** | GP |
| **Seat** | the hex its ruler sits in; the faction's base. Damage to the seat hurts HP |
| **Leader** | name, title, a **moral label** (bad/good) and a **tag** (section 8) |
| **Goal** | what it is working on, visible to all (section 8) |
| **Assets** | section 4 |
| **Hexes** | what it holds |

**Attributes gate assets:** a faction can only buy an asset whose requirement is at or below
the matching attribute. Raising an attribute costs **the new rating's price** (table,
section 11; check) and is a turn's action, so a realm that wants knights must first become
the kind of realm that can field them. That's what Cunning now means in play: *the rating
says which spies you can afford to run.*

**HP** is the regime's health bar. At **0 HP the ruler falls** (section 7). HP comes back
by the Repair action.

**Start:** S = the realm's hex levels summed. Force = Cunning = Wealth = S ÷ 10, rounded,
minimum 1. Treasury S × 10 GP. One starting asset of each type, tier ≤ the attribute, placed
on its hexes (Force at the seat). The tower: F1 C1 W1, HP 7, 100 GP, no assets.

## 4. Assets

An asset is a named unit, sitting in one hex, owned by one faction. It is the only thing
that acts in the domain: attacks are asset against asset.

| Field | What it is |
|---|---|
| **Type** | Force, Cunning or Wealth |
| **Tier** 1–3 | its weight; also sets the D&D fight it turns into |
| **Needs** | the owner's attribute rating required to buy it |
| **Cost** | GP, paid once (1 FacCred in the book = **100 GP** here) |
| **Upkeep** | GP a month for some assets |
| **HP** | damage it can take before it's destroyed |
| **Attack** | "X vs Y, damage": the attacker's attribute X against the defender's Y, and the damage on a win |
| **Counter** | damage the attacker takes if the defence wins |
| **Special** | a rule of its own (income, reveal, coup, can't move) |
| **Fight** | what Morten meets if he goes after it himself (section 7) |

### The first list

One page, to tune. Names are fantasy stand-ins for the book's entries; the three columns
that matter (type, tier, what it does) follow the book's shape.

**Force**

| Asset | Tier | Needs | Cost | HP | Attack | Counter | Special | Fight (monsters) |
|---|---|---|---|---|---|---|---|---|
| Thugs | 1 | F1 | 200 | 3 | F vs F, 1d4 | 1d4 | | Bandits |
| Militia | 1 | F1 | 400 | 4 | F vs F, 1d6 | 1d4 | | Guards |
| Beast pack | 2 | F2 | 600 | 5 | F vs F, 1d6 | 1d6 | the people's beasts (Orcs: Worgs, Goblinkind: hyenas) | that beast |
| Men-at-arms | 2 | F3 | 800 | 6 | F vs F, 1d8 | 1d6 | | Veterans |
| Walls | 2 | F3 | 600 | 10 | none | 1d8 | can't move; its hex can't be seized while it stands | Animated Armors + Guards |
| Knights | 3 | F5 | 1,200 | 8 | F vs F, 2d6 | 1d8 | upkeep 100 | Knight + Veterans |
| Warband | 3 | F6 | 1,600 | 10 | F vs F, 2d8 | 1d10 | upkeep 200 | Berserkers + a Champion |

**Cunning**

| Asset | Tier | Needs | Cost | HP | Attack | Counter | Special | Fight |
|---|---|---|---|---|---|---|---|---|
| Informers | 1 | C1 | 200 | 3 | C vs C, 1d4 | none | reveals every asset in its hex to its owner | Spies |
| Smugglers | 1 | C2 | 400 | 4 | C vs W, 1d4 | none | income +50 | Bandit Captain + Bandits |
| Seditionists | 2 | C2 | 600 | 4 | C vs C, 1d6 | none | **coup:** may attack the seat's faction HP directly; led by a named NPC (section 7) | Cult Fanatic + Cultists |
| Saboteurs | 2 | C3 | 800 | 4 | C vs F, 2d4 | 1d4 | | Thugs + a Spy |
| Court mage | 3 | C4 | 1,200 | 4 | C vs C, 1d8 | 1d4 | once a turn, cancels one attack on an asset in its hex (roll C vs C) | Mage + Guards |
| Assassins | 3 | C5 | 1,600 | 4 | C vs C, 2d6 | none | on a win, also 1d4 to the target faction's HP | Assassin |

**Wealth**

| Asset | Tier | Needs | Cost | HP | Attack | Counter | Special | Fight |
|---|---|---|---|---|---|---|---|---|
| Farms | 1 | W1 | 200 | 4 | none | none | income +50 | Guard + Mastiffs |
| Caravans | 1 | W2 | 400 | 4 | W vs W, 1d4 | none | income +100; may move 2 hexes | Veterans (caravan guards) |
| Mine | 2 | W3 | 800 | 6 | none | 1d4 | income +200; only in hills or mountains | Guard Captain + Thugs |
| Mercenaries | 2 | W3 | 800 | 6 | W vs F, 2d4 | 1d6 | upkeep 100 | Veterans + Berserkers |
| Treasury | 3 | W4 | 1,200 | 8 | none | 1d6 | Rob here pays double | Guard Captain + Guards |
| Toll road | 3 | W5 | 1,600 | 6 | W vs W, 1d8 | none | income +300 | Knights (the toll's escort) |

Rules of thumb from the book to keep when tuning: Force kills things, Cunning kills Cunning
and chips the regime, Wealth buys time and pays for the rest; the strongest assets have
upkeep so a faction can't hoard them; most assets can't hurt a faction's HP, only its
assets, so regimes fall from the inside (Seditionists, Assassins, the seat under attack),
not from one battle.

## 5. The domain turn

Order of play, every month, run by the script after Morten's month lands:

1. **Morten's month lands** (section 7).
2. **Income:** hex income to each holder; asset income; then **upkeep** for assets that
   have it. A faction that can't pay upkeep loses the asset it can't pay for (its choice:
   the cheapest).
3. **Each faction takes one action,** in order of Cunning, highest first (ties by d10). The
   tower goes first if its Cunning ties.
4. **Goals** update: a faction that completed its goal gains an attribute point (the book's
   XP, simplified to +1 to the attribute the goal was about); every faction without a goal
   picks one by its tag.
5. **Clean-up:** hexes seized change hands; a faction at 0 HP falls; rumours update; the
   month advances.

**Actions** (one per faction per month, the book's list refitted):

| Action | What it does |
|---|---|
| **Attack** | One of your assets attacks an asset in the same hex (section 6). |
| **Move** | Move any number of your assets one hex each (Caravans two). Moving into a hex another faction holds is allowed; it's how attacks start. |
| **Buy** | Buy one asset, placed in a hex you hold where you have a Force asset or your seat, at its cost. |
| **Raise** | Raise one attribute by 1 at its price. |
| **Repair** | Heal one asset fully for a quarter of its cost, or heal the faction 1d6 HP for 100 GP. |
| **Seize** | Claim a hex where you have a Force asset and the holder has none (and no Walls). Resolves at clean-up. |
| **Give** | Send GP to another faction. Free. (The tower funds its friends this way; the gold is simply theirs.) |

The tower takes its action like any faction, declared by Morten at the start of the month
(so the script can reject an illegal one before anything else happens, as now).

## 6. Attacks, hexes and hostility

**An attack:** the attacker names one of its assets and a target asset in the same hex.
Roll **d10 + attacker's attribute X** vs **d10 + defender's attribute Y**, X and Y from the
attacking asset's "X vs Y". Higher wins; on a tie both take their damage (check). The
attacker's win does the asset's attack damage to the target; the defender's win does the
target's counter damage to the attacker. An asset at 0 HP is destroyed. Modifiers: river
edge +1 to the defender (the attacking asset came in over it), claim +1 to a people's own
hex, Walls in the hex +1 to everything the holder defends with.

**Attacking the seat.** If the target hex is the defender's seat and the attacker wins
against the last Force asset there (or there is none), the damage goes to the **faction's
HP** instead. Seditionists' coup attacks go to HP directly without that condition. This is
how regimes fall.

**Hexes** are held, not fought over as a whole. A faction with a Force asset standing in a
hex whose holder has none there may **Seize** it; if nobody contests it that month, it's
theirs at clean-up. The tower hex can be seized from nobody (warded), but its assets can be
attacked like any.

**Hostility replaces war.** A faction whose asset the tower (or Morten in person) attacked
gets the goal **Punish the tower** for 3 months: its next actions go against tower assets,
moving toward the tower if it must, which puts fights at Morten's door. Striking a seat
makes it 6 months. Good rulers drop it when their regime changes; bad rulers only when the
months run out or they fall. **Allies** are good rulers not hostile to the tower.

## 7. Morten's month

Travel and wandering monsters as in v1. Then one mission in the hex he's in, or none.
Every mission is a D&D fight built from the asset's **Fight** column, with the encounter
budget set by the asset's **tier**: tier 1 is a Low encounter for Morten's level, tier 2
Moderate, tier 3 High. The hex level no longer scales missions, only wandering monsters and
the dungeon floor.

| Mission | Against | On a win |
|---|---|---|
| **Strike** | any asset in the hex | the asset takes **2d6 damage** (so a tier-1 asset usually dies and a Warband takes three visits); at the seat, with no Force asset left there, the damage goes to the faction's HP |
| **Rob** | a Wealth asset | the asset takes 1d6 and Morten takes **tier × 100 GP** from the owner's treasury (× 2 at a Treasury), at most what it holds |
| **Contact** | the people of a realm's hex | no fight unless the roll says so: a Persuasion check (DC 10 + the ruler's Cunning), or a fight against the ruler's Informers if they're in the hex; a win finds a **named dissident** and lets the tower buy **Seditionists** in that realm |
| **Delve** | the floor under the hex | as now |

Morten doesn't need to be at the seat to matter: he can go after a caravan on the road,
or the knights garrisoning a hex he wants the tower to seize next month.

**Regime change (the rivals, rebuilt).** When a faction's HP reaches 0, the ruler falls.
- If the tower has **Seditionists** in that realm, their named dissident takes the throne:
  the faction keeps its hexes and assets, gets the dissident as leader with a **good** tag,
  full HP, and the Seditionists asset is dissolved into the new court. It is now an ally.
- Otherwise, a new leader is rolled from the people's name list, with a random tag (bad
  more often than good, as at the start), and the realm is in disorder for a month (no
  action).
- Either way the old ruler is gone from the game (v1's "becomes the mirror" is dropped).

So the v1 arc "strike the ruler, fund the rival, back the coup" becomes: Contact the
dissidents, buy Seditionists, let them chip at the regime while Morten strikes its seat,
and watch the HP bar. Everything in that chain is a thing you can see.

**Death** ends the month as now. Gold Morten carries is lost; the tower's assets stand.

## 8. Goals, tags and labels

Each leader has a **label** and a **tag**, shown together everywhere as *label: verb*:

| Label | Tag | Shown as | Goal it keeps picking |
|---|---|---|---|
| bad | Conqueror | "bad: takes land" | **Seize** the deepest hex next to its own that it can reach with a Force asset; buys or moves Force to get there |
| bad | Raider | "bad: robs its neighbours" | **Attack** the richest neighbour's Wealth assets; on wins takes tier × 100 GP |
| bad | Slaver | "bad: takes people for soldiers" | **Attack** the weakest neighbour's Force assets; a destroyed one is rebuilt as its own Thugs for free |
| bad | Tyrant | "bad: squeezes its own people" | **Buy** and **Raise** at home; income +50%; its own hexes count as unrest: Contact there is DC −4 |
| good | Steward | "good: keeps the peace" | **Repair**, **Buy** Walls and Farms, **Seize** only its own people's hexes |
| good | Liberator | "good: fights tyrants" | **Attack** bad rulers' Force assets next door when its Force is higher |

And every faction, over its tag, takes **Punish the tower** while hostile, and **Recover**
(Repair) when below half HP.

A faction's current goal is always shown: "Galen (bad: takes people for soldiers) · goal:
break the Orcs' Militia in B3 (month 2 of it)". That one line tells the human what's
coming.

## 9. Reporting and the map

The domain report, in this order, before any roll:

1. **The plan:** what Morten's mission and the tower's action were for.
2. **What happened,** one bullet per event that touched the tower, an ally, or a realm
   Morten is in or next to: who, what (as the goal line explains it), the roll in short, the
   result. Far-away realms get one line between them ("Elsewhere: Gnomes bought Walls in
   C1").
3. **The tower now:** HP, attributes, gold, assets by hex, hexes, who's hostile, allies.
4. **Next month:** threats (hostile assets within a move of a tower hex), chances (a seat
   with no Force asset, a caravan on the road, a regime under 5 HP), and the open choices.

The full roll log stays in `transcript.md`.

**For the map UI** (its own session), the script must write, after every turn, a JSON the
page can read without knowing the rules: for each hex its level, biome, people, holder,
rivers, and the assets in it (owner, name, type, tier, HP); for each faction its label,
tag, goal, HP, attributes, gold, seat; Morten's hex; and **last month's events as a list of
`{month, actor, action, from_hex, to_hex, target, result}`** so the page can draw arrows.
`realms.json` can be that file if it's kept flat; otherwise the script writes `map.json`
beside it.

## 10. Bug fixes carried by this plan

| v1 problem | v2 answer |
|---|---|
| 1 GP funding unlocks the court | no court; **Give** sends gold the receiver actually spends; support for a rebellion is an asset you buy |
| war changes nothing for bad rulers | **hostility** gives any faction a goal against the tower, with a timer |
| Cunning is a bare number | it gates which Cunning assets you can run; the assets are on the map |
| "Brutal" explains nothing | label + verb everywhere; the goal line says what's coming |
| six rivals from month 1 | no rivals until Morten **Contacts** a dissident; then one, named, as an asset |
| the roll log hides the plan | report order fixed in section 9; far realms summarised |
| Build is the only growth | Buy, Raise, Repair, Seize, Move |
| Strike is abstract (+3 somewhere) | Strike damages a thing you can see; at the seat, the regime's HP |

## 11. Constants (checked 2026-10-24)

The book itself (WWN, SWN) couldn't be fetched from the session (its sites are outside the
network allowlist). What was checked, against open-source implementations of the SWN
Revised faction rules (the same engine) on GitHub:
[thatguy14/faction_manager](https://github.com/thatguy14/faction_manager) (`faction.py`:
the rating table and HP = 4 + the table's value per attribute),
[orffen/swn](https://github.com/orffen/swn) (`faction.js`: the sample factions' HP 15, 29
and 49 for ratings 4/3/1, 6/5/3 and 8/7/5, which the table reproduces; the asset names by
attribute and rating), [David-Dodge/SWN-faction-turn-sim](https://github.com/David-Dodge/SWN-faction-turn-sim)
(`CombatFunctions.php`: the tie) and
[Zer0-Vector/swn-faction-tracker](https://github.com/Zer0-Vector/swn-faction-tracker)
(`Assets.ts`: HP, cost, attack and counter of the rating-1 to 3 assets). WWN's own asset
names are not verified.

| Constant | Value | Check |
|---|---|---|
| 1 FacCred | 100 GP | ours |
| Faction HP | 4 + 1, 2, 4, 6, 9, 12, 16, 20 for ratings 1–8 | **verified** (faction_manager, orffen/swn) |
| Raise an attribute | the new rating's value × 100 GP | the progression **verified** (faction_manager's one table serves HP and XP); paying it in GP instead of XP is ours |
| Attack roll | d10 + attribute vs d10 + attribute; **tie: both take damage** | **verified** (SWN-faction-turn-sim) |
| Actions | one a turn | from memory (as the book); the Attack action lets every asset in one hex attack once, from memory of the book |
| Asset limit | assets of a type up to the attribute; each over costs upkeep | from memory (SWN: 1 FacCred each; ours 100 GP) |
| Income | hex level × 10 GP + asset income | ours (v1), not the book's attribute-based income, which was not checked |
| Goals | XP, spent on attributes at the table's costs | the book's shape (XP), our amounts (2 for a hex, 1 for the rest) |
| Base of Influence | damage to it also hits faction HP | from memory; ours: the seat, and every Force asset at the seat |
| Asset tiers | 1 / 2 / 3 = Low / Moderate / High encounter for Morten's level | ours |
| Strike damage | 2d6 to the asset, or to HP at an unguarded seat | ours |
| Rob | tier × 100 GP, × 2 at a Treasury | ours |
| Contact DC | 10 + ruler's Cunning (−4 under a Tyrant) | ours |
| Hostility | 3 months; 6 for a Strike on the seat | ours |
| Repair | asset: ¼ cost; faction: 1d6 HP for 100 GP | ours |
| Hex income | level × 10 GP; nothing while another faction's Force asset stands in it | v1; occupation ours |
| River / claim / Walls | +1 / +1 / +1 | v1 + Walls |
| Hex lost / seat lost | 1d4 / 1d6 HP | ours |
| Starting attributes | S ÷ 10 each, min 1; treasury S × 10; 2 Force + 1 Cunning + 1 Wealth asset | v1 shape; the second Force asset ours |
| Tower start | F1 C1 W1, HP 7, 100 GP | ours |
| Disorder after a fall with no dissident | 1 month, no action | ours |

Asset stats checked against the SWN rating-1 to 3 entries (FacCreds × 100 GP): Thugs =
Security Personnel (2, HP 3, F v F 1d3+1, counter 1d4); Militia = Militia Unit (4, HP 4, F v
F 1d6, counter 1d4+1); Informers (2, HP 3); Smugglers (2, HP 4, C v W 1d4); Saboteurs (5,
HP 6, C v C 2d4); Assassins = Cyberninjas (6, HP 4, C v C 2d6); Farms = Harvesters (2, HP
4, counter 1d4); Caravans after Franchise (2, HP 3, W v W 1d4, counter 1d4−1); Mine after
Postech Industry (8, HP 4, counter 1d4). Seditionists are the book's rating-4 asset (12,
HP 8) refitted as the coup asset (600 GP, HP 6, Cunning 2) so the tower can reach it.
Beast pack, Knights, Warband, Mercenaries, Treasury, Toll road follow the book's entries
named in `realms.py` (`book`) from memory; Walls and Court mage are ours.

## 12. Build steps

1. **Read the book's faction chapter** (WWN free edition) and fix every "check" above;
   note each deliberate difference in the table.
2. **Rules:** write `realms.md` v2 from this plan (keep v1 as `realms-v1.md` while the
   `realms` campaign still runs on it, or finish that campaign first).
3. **Script:** new data model (factions with HP, attributes, assets, goals, hostility),
   the turn, the actions, the AI for goals, `new`, `show`, `turn`, `encounter` (now takes
   an asset), `sim`. Keep `--dry-run` and the rejected-order behaviour.
4. **Output:** the report format of section 9 and the flat JSON for the map.
5. **Sim:** 24 passive months, 10 seeds. Check that regimes fall sometimes but not every
   year, that a Conqueror grows and a Steward holds, that upkeep bites, that the tower at
   rest isn't wiped out and isn't ignored.
6. **Play:** a new campaign, Morten at his current level, 3 months with the human reading
   the reports. Tune the asset list and the labels from what they can't follow.
7. **CLAUDE.md:** update the Realms section and the folder layout.

## 13. Open questions for the human

- **Rivals:** keep them only as the Contact → Seditionists → regime-change chain above
  (my recommendation), or also keep a standing "rival" line per realm for flavour?
- **Scale:** are tier-by-encounter fights right (a tier-3 asset is always a High fight for
  Morten's level), or should the hex level still weigh in?
- **The court:** gone in this plan. Keep named officers purely as the leaders of tower
  assets (Doran captains the Militia)?
- **Seizing hexes** by standing unopposed vs v1's single battle roll: the book's way is
  slower but visible a month ahead. Fine?
- **Morten on the battlefield** (Fireball on a Warband) stays "left for later" unless you
  want it in the first build.

## 14. What the build decided (2026-10-24)

The open questions, decided by the main session with the human's leave:
- **Rivals** only through Contact → Seditionists → regime change; no standing rival line.
- **Scale:** asset fights by tier only; the hex level scales wandering monsters and floors.
- **The court** is gone; an asset may carry a named leader (the Seditionists' dissident).
- **Seizing** is the book's way: stand unopposed, resolve at clean-up.
- **Morten on the battlefield** is left for later.

Differences from sections 3–8 found in the sim (24 months × 10 seeds; numbers in
`realms.md` section 12):
- Asset list refitted toward the book (section 11); about six per type.
- The seat: damage to *any* Force asset at a seat also hits HP (the book's Base of
  Influence), not only the last guard; a hex seized costs 1d4 HP, a seat 1d6.
- An occupied hex (another faction's Force asset in it) pays no income.
- A regime at 0 HP takes no action before it falls (no Repair out of it).
- Realms start with two Force assets and a goal; goals give XP, not a free point.
- The AI: recover, defend, punish, spend when rich (1,200 GP), goal, grow; a faction rests
  3 months from one it just beat; a Slaver takes from the tower when it is the weakest
  neighbour (so a passive tower is raided about twice a year).
- Visibility: another faction's Cunning assets are hidden from the tower unless Informers,
  Morten or an attack reveal them, and the realms see the tower's the same way.
- The report and `map.json` follow section 9 and the map page's contract.
