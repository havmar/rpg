# Realms v2: the overworld

An overworld for D&D Crunch: a small hex map of six realms and Morten's tower, played as
monthly domain turns on top of the dungeon game. Same feel: minimal narration, open
numbers, every roll in the log. Every realm and the tower is a **faction** with **assets**
on the map (a militia, a spy ring, a caravan), after the faction rules of *Worlds Without
Number* (the same engine as *Stars Without Number*). Every asset turns into a D&D fight
when Morten goes after it in person.

A campaign with a `realms.json` of version 2 is played by this file, which adds to
`dnd-crunch/CLAUDE.md` and wins where they differ. The script `dnd-crunch/tools/realms.py`
runs the world: it generates the map, rolls the domain turn and keeps `realms.json`. Its
constants block and the table in section 10 hold the same numbers; change both together.
Version 1 (`realms-v1.md`, `tools/realms_v1.py`) still runs the `realms` campaign; v2
refuses a v1 `realms.json`. The design record is `realms-v2-plan.md`.

## 1. The map

As in v1:

- **4 columns × 5 rows = 20 hexes**, columns A–D west → east, rows 1–5 north → south.
  Flat-topped, columns B and D sit half a hex south. `world.md` lists every hex's
  neighbours.
- **Hex level 1–20**, each used once: its ley. A hex pays its holder **level × 10 GP a
  month**, sets the wandering monsters, and holds **floor N** of the dungeon (N = level).
- **Biomes** by row, flavour only (a Mine needs hills or mountains).
- **2 rivers** along hex edges, **2 lakes** inside hexes. An asset that came into its hex
  over a river edge attacks at **+1 to the defender**.
- **Travel:** entering a hex takes 1 day. Each day outside the tower hex, `1d6`: on a 1, a
  wandering encounter for that hex's level (`encounter --hex HEX`).

## 2. Peoples and realms

- **6 peoples, 6 realms:** Humans, Elves, Orcs, Gnomes, Tieflings, Goblinkind. Each realm
  starts with 3 contiguous hexes (one of them 4). Every hex keeps its people; conquest
  changes only the holder.
- **Claim:** +1 to an attack made in a hex of the attacker's own people.
- **The tower** is on the level 1 hex, its people the tower folk. The hex is **warded**: it
  can never be seized, but assets in it can be attacked, and so can the tower itself.

## 3. Factions

| Field | What it is |
|---|---|
| **Force** 1–8 | armies and the fear of them |
| **Cunning** 1–8 | spies, informers, friends in the right places |
| **Wealth** 1–8 | trade, land, coffers |
| **HP** | the regime's health: **4 + the bonus of each attribute** (1→1, 2→2, 3→4, 4→6, 5→9, 6→12, 7→16, 8→20). At 0 the ruler falls (section 7) |
| **Treasury** | GP |
| **Seat** | the hex the ruler sits in (a realm's deepest hex at the start; the tower hex for the tower) |
| **Leader** | name, title, **label: verb** (section 8) |
| **Goal** | what it is working on, one line, shown to all |
| **XP** | from goals done; spent on the goal's attribute |
| **Hostile** | months left of "punish the tower" |

- **Attributes gate assets:** an asset needs its type's attribute at its **Needs** or more.
- **Limits:** a faction may hold as many assets of a type as the matching attribute; each
  one over costs **100 GP a month**.
- **Start:** S = the realm's hex levels summed. Force = Cunning = Wealth = S ÷ 10, rounded,
  min 1. Treasury S × 10 GP. Assets: 2 Force (one at the seat), 1 Cunning, 1 Wealth, each
  random among those its attribute allows. 4 rulers bad, 2 good; each realm starts with a
  goal.
- **The tower:** F1 C1 W1, HP 7, 100 GP, no assets. Its leader is Morten.

## 4. Assets

An asset sits in one hex and belongs to one faction. **Attack** "X vs Y, damage": the
attacker's X against the defender's Y, the damage on a win. **Counter**: what the attacker
takes when the defence wins. **Fight**: what Morten meets when he goes after it (section 6).
Costs are the book's FacCreds × 100 GP; the book's entry is in the script (`book`).

**Force**

| Asset | Tier | Needs | Cost | HP | Attack | Counter | Special | Fight |
|---|---|---|---|---|---|---|---|---|
| Thugs | 1 | F1 | 200 | 3 | F vs F, 1d3+1 | 1d4 | | Bandit, Tough, Tough Boss |
| Militia | 1 | F1 | 400 | 4 | F vs F, 1d6 | 1d4+1 | | Guard, Scout, Guard Captain |
| Beast pack | 2 | F2 | 500 | 5 | F vs F, 2d4 | 1d4+1 | the people's beasts | by people (below) |
| Walls | 2 | F3 | 600 | 10 | none | 1d6 | can't move; owner +1 on defence in its hex; the hex can't be seized | Animated Armor, Guard, Gargoyle |
| Knights | 3 | F4 | 800 | 12 | F vs F, 1d8 | 1d8 | upkeep 100 | Knight, Warrior Veteran, Warhorse |
| Warband | 3 | F6 | 1,600 | 16 | F vs F, 2d8 | 2d6 | upkeep 200 | Berserker, Warrior Veteran, Gladiator, Ogre |

**Cunning**

| Asset | Tier | Needs | Cost | HP | Attack | Counter | Special | Fight |
|---|---|---|---|---|---|---|---|---|
| Informers | 1 | C1 | 200 | 3 | none | none | its owner sees every asset in its hex | Spy, Bandit, Noble |
| Smugglers | 1 | C1 | 200 | 4 | C vs W, 1d4 | none | income +50; moves 2 | Bandit, Pirate, Bandit Captain |
| Saboteurs | 2 | C2 | 500 | 6 | C vs C, 2d4 | none | | Tough, Spy, Scout |
| Seditionists | 2 | C2 | 600 | 6 | C vs C, 1d6 | none | **coup** (section 7); only after a Contact; led by the dissident | Cultist, Cultist Fanatic |
| Assassins | 3 | C3 | 600 | 4 | C vs C, 2d6 | none | a win also does 1d4 to the target faction's HP | Spy, Assassin |
| Court mage | 3 | C5 | 1,000 | 6 | C vs C, 1d8 | 1d6 | can't move; once a month cancels an attack on its owner's asset in its hex (C vs C) | Mage, Cultist Fanatic, Guard, Imp |

**Wealth**

| Asset | Tier | Needs | Cost | HP | Attack | Counter | Special | Fight |
|---|---|---|---|---|---|---|---|---|
| Farms | 1 | W1 | 200 | 4 | none | 1d4 | income +50; can't move | Guard, Mastiff, Scout |
| Caravans | 1 | W2 | 400 | 4 | W vs W, 1d4 | 1d4−1 | income +100; moves 2 | Guard, Scout, Warrior Veteran, Mastiff |
| Mine | 2 | W3 | 800 | 4 | none | 1d4 | income +150; hills or mountains; can't move | Tough, Guard, Tough Boss |
| Mercenaries | 2 | W3 | 800 | 6 | W vs F, 2d4+2 | 1d6 | upkeep 100 | Warrior Veteran, Berserker, Bandit Captain, Tough |
| Treasury | 3 | W4 | 1,200 | 8 | none | 1d6 | income +100; a Rob here takes double; can't move | Guard Captain, Animated Armor, Guard |
| Toll road | 3 | W5 | 1,000 | 8 | W vs W, 1d6 | none | income +250; can't move | Knight, Warrior Veteran, Scout, Guard |

**Beast packs:** Humans Mastiff, Warhorse, Scout · Elves Giant Owl, Giant Eagle, Giant Elk ·
Orcs Worg, Dire Wolf, Giant Boar · Gnomes Giant Badger, Giant Goat, Brown Bear · Tieflings
Imp, Hell Hound · Goblinkind Giant Hyena, Worg, Gnoll Warrior · the tower Mastiff, Giant
Owl, Brown Bear. **A seat with no Force asset** fights as the ruler's court: Noble, Spy,
Tough, Guard, Knight, Guard Captain, tier 3.

**Seen and hidden.** Force and Wealth assets are open. Another faction's Cunning asset is
shown only where the tower has Informers, where Morten has been, or once it has attacked
the tower or been attacked by it. The realms see the tower's Cunning assets only where they
have Informers, or once those assets have attacked.

## 5. The domain turn

Every month, after Morten's month, the script runs:

1. **Morten's month lands:** the mission's result, deposit and withdraw, Give (section 6).
2. **Income and upkeep:** hex income (none from a hex with another faction's Force asset
   in it: it's occupied), asset income, then upkeep (assets that have it, and 100 for each
   asset over a limit). A faction that can't pay loses its cheapest charged asset until it
   can.
3. **Each faction takes one action,** in order of Cunning, highest first; ties by d10, the
   tower first on its own tie.
4. **Goals:** a goal done gives XP (section 8); a faction without one picks one by its tag.
5. **Clean-up:** seizes resolve, hostility and disorder count down, a realm with no hexes
   is gone, a faction at 0 HP falls (section 7), the month advances.

**Actions** (one per faction per month):

| Action | What it does |
|---|---|
| **Attack** | Its assets in one hex each attack once (section 6). Seditionists attack from anywhere in their realm. |
| **Move** | Any number of its assets one hex each (Smugglers, Caravans two). Walls, Farms, Mine, Treasury, Toll road, Court mage can't move. |
| **Buy** | One asset, in a hex it holds where it has its seat or a Force asset. Seditionists: in the hex of the Contact. |
| **Raise** | One attribute +1: 200 GP to rating 2, 400 → 3, 600 → 4, 900 → 5, 1,200 → 6, 1,600 → 7, 2,000 → 8. Max HP rises with it. |
| **Repair** | One asset back to full for a quarter of its cost, or the faction 1d6 HP for 100 GP. |
| **Seize** | A hex where it has a Force asset and the holder has none (and no Walls). It changes hands at clean-up if that still holds. |

**Give** (the tower only): GP to any realm, free, not an action. The gold is theirs to spend.

## 6. Attacks, seats, hexes, hostility

- **An attack:** d10 + attacker's X vs d10 + defender's Y. Higher wins: the target takes
  the attack's damage. Defence higher: the attacker takes the target's counter. **A tie:
  both.** An asset at 0 HP is destroyed.
- **Modifiers:** +1 claim (attacker, its own people's hex) · +1 river (defender, the
  attacker came in over a river edge) · +1 Walls (defender, its Walls stand in the hex).
- **The seat under attack:** damage to a Force asset in its owner's seat is also done to
  the owner's HP. With no Force asset left at the seat, assets in the hex attack the seat
  itself: the defence rolls the attack's Y, the damage goes to HP, the counter is 1d4.
- **Hexes:** a hex seized from a faction costs it 1d4 HP; its seat, 1d6, and the seat moves
  to its deepest hex left.
- **Hostility:** a faction whose asset the tower or Morten attacks (a Strike, a Rob, a tower
  Attack) turns **hostile for 3 months** (this one and the next two); its seat, **6**. A
  hostile faction's action goes against the tower's assets, marching toward them, or
  against the tower itself when it has none it can see. Any fall ends it.
- **Allies** are good rulers not hostile to the tower.
- **The tower at 0 HP is sacked:** whoever brought it down carries off half its treasury;
  its HP is restored and every hostility is spent. The wards hold the hex.

## 7. Morten's month

Travel as in section 1. Then **one mission in the hex he is in, or none.** Strike, Rob and a
Contact that turns into a fight are D&D fights built from the target's Fight list by
`encounter --asset ID`: **tier 1 a Low encounter for his level, tier 2 Moderate, tier 3
High** (`Combat Encounters.md`), at most 4 monsters of at most two kinds, coins a tenth of
their XP. The hex level scales only wandering monsters and the dungeon floor.

| Mission | Against | On a win |
|---|---|---|
| **Strike** | any asset in the hex, or a realm's seat with no Force asset in it | the asset takes **2d6**; the seat, 2d6 to the realm's HP. Hostile 3 months (seat 6) |
| **Rob** | a Wealth asset | it takes 1d6, and Morten takes **tier × 100 GP** from the owner's treasury (× 2 at a Treasury), at most what it holds. Hostile 3 months |
| **Contact** | the people of a realm's hex | Persuasion (CHA) **DC 10 + the ruler's Cunning** (−4 under a Tyrant), or, if that realm's Informers are in the hex, a fight with them. A win names a **dissident** and lets the tower buy **Seditionists** there. No hostility |
| **Delve** | the floor under the hex | as in the dungeon game; no domain effect |

Success means Morten wins the fight (every foe dead, fled or surrendered) or the check.
Pass a mission to `turn` only when it succeeded. **Death** ends the month: the mission
fails, he loses the coins he carried, he wakes at the tower; the tower's action stands.
**The trader** is at the tower.

**Regime change.** When a realm's HP reaches 0, its ruler falls at clean-up (a regime at 0
takes no action meanwhile):
- If the tower has **Seditionists** in that realm, their dissident takes the throne with a
  good tag (Steward or Liberator), full HP; the Seditionists become the new court (the
  asset is gone). The realm is an ally.
- Otherwise a new ruler from the people's names, bad two times in three, with a random tag;
  full HP; **disorder for 1 month** (no action).
- Either way the old ruler is gone, the goal and hostility end.

So the road to a friendly throne: **Contact** a dissident, **Raise** Cunning to 2, **Buy**
Seditionists, keep them out of the hostile realm's reach, and **Attack** its HP with them
each month while Morten Strikes the seat's guards.

## 8. Leaders, goals and the AI

Every leader is shown as **label: verb**, everywhere.

| Label | Tag | Shown as | Goal it picks |
|---|---|---|---|
| bad | Conqueror | bad: takes land | **take** the best border hex: deep ley, few defenders near, not a seat |
| bad | Raider | bad: robs its neighbours | **rob** the richest neighbour's nearest Wealth asset (or raid its seat if it has none); each win takes tier × 100 GP, a seat 200 |
| bad | Slaver | bad: takes people for soldiers | **take** the weakest neighbour's (lowest Force) nearest Force asset, or its seat if it has none; a destroyed one, or a won seat, becomes its own Thugs (within its Force limit) |
| bad | Tyrant | bad: squeezes its own people | **buy** the dearest asset it can field and lacks, else raise its lowest attribute; hex income × 1.5; Contact in its land −4 DC |
| good | Steward | good: keeps the peace | **take back** its own people's hexes; else Walls at the seat, two Farms, then raise its lowest attribute |
| good | Liberator | good: fights tyrants | **break** a bad neighbour's Force asset next door when its Force is higher; else as a Steward |

- **Goal done:** XP (take a hex 2; break, rob, buy 1; raise 0). When its XP reaches the bonus
  of the goal's attribute's next rating (2, 4, 6, 9, 12, 16, 20), it spends it and the
  attribute rises. A goal against a faction leaves that faction alone for 3 months after.
  A goal not done in 6 months, or whose target is gone or out of reach, is dropped.
- **Each realm's action**, in order: in disorder, nothing · at 0 HP, nothing · below half
  HP, Repair itself (**recover**) · an enemy Force asset in one of its hexes: attack it, or
  bring Force in (**defend**) · hostile: **punish the tower** · 1,200 GP or more: buy (over
  its limits if it must) or raise · **its goal** · otherwise buy within its limits, raise,
  or save.
- **Marching:** the army (Force assets, Mercenaries, Saboteurs, Assassins) moves toward the
  target; a realm buys first while its army is under 2, and never moves the seat's last
  Force asset away.

The goal line always says what's coming, e.g. "Humans · Reeve Galen (bad: takes people for
soldiers) · goal: take people from the tower's seat in C4 (month 1 of it)".

## 9. Running a month

The script is `python3 dnd-crunch/tools/realms.py`; DIR is the campaign folder.

| Command | What it does |
|---|---|
| `new --seed N --campaign DIR [--level 4]` | The world: `realms.json`, `world.md`, `map.json`, and the 20 floors in `gm-secrets.md`. |
| `show --campaign DIR [--at HEX] [--gm]` | The world as the tower knows it; `--at`, the rumours from a hex; `--gm`, the hidden assets too (never in chat). |
| `encounter --campaign DIR --asset ID` | The fight for a Strike or Rob on that asset (or `--asset REALM` for its unguarded seat). |
| `encounter --campaign DIR --contact HEX` | The Contact DC, or the Informers fight (GM only: it can reveal them). |
| `encounter --campaign DIR --hex HEX` | A wandering encounter for the hex's level. |
| `turn --campaign DIR [options] [--dry-run]` | The domain turn: prints the report, saves `realms.json`, `world.md`, `map.json`. |
| `sim [--seeds 1-10] [--months 24]` | Passive-tower months for tuning; `--seed N --verbose` prints every month. |

**`turn` options:**

| Option | Meaning |
|---|---|
| `--at HEX` · `--level N` | where Morten ends the month · his level now |
| `--strike ID` / `--strike REALM` | a won Strike on that asset / that realm's unguarded seat, in his hex |
| `--rob ID` [`--keep-loot`] | a won Rob on that Wealth asset in his hex (the gold goes to the tower unless he keeps it) |
| `--contact` · `--delve` | a won Contact in his hex · he delved |
| `--deposit GP` · `--withdraw GP` · `--give REALM=GP` | gold moved (Give repeatable) |
| `--action buy:KIND[@HEX]` | e.g. `buy:militia`, `buy:seditionists@B3` |
| `--action raise:force` · `repair:ID` · `repair:tower` | |
| `--action move:ID>HEX[,ID>HEX]` | |
| `--action attack:ID>ID[,ID>ID]` · `attack:ID>REALM` | assets in one hex; `>REALM` hits its seat (Seditionists: its HP from anywhere in it) |
| `--action seize:HEX` | |
| `--plan "why"` | a line for The plan (repeatable) |
| `--gm` | the hidden events too (never in chat or the transcript) |

The tower's action is checked before anything happens; one the treasury can't cover when
the tower acts is rejected too. A rejected order prints one line and saves nothing: fix it
and rerun. **Always `--dry-run` first.**

### Steps

1. **Start of the month: choices.** The human (or the GM as Morten) picks travel, the
   mission, the tower's action, Give. The orders are fixed from here.
2. **Travel**, one hex a day, wandering checks; `show --at HEX` for the rumours.
3. **The mission:** `encounter --asset ID` (or `--contact HEX`), then the fight as usual.
   Delve: the floor from `gm-secrets.md`.
4. **The domain turn:** `turn` with the month's options, `--dry-run` first. Update
   `character.md` for gold moved, then reply in the domain-turn format below.
5. **The map page:** `python3 dnd-crunch/tools/realms_page.py dnd-crunch/campaigns/<name>`
   and republish the page (`ui/README.md`); its link is in `state.md`.
6. Update `state.md` and `transcript.md`, commit and push, as in CLAUDE.md.

### The domain-turn reply

The script prints it in this order; the chat reply keeps it (plain Markdown, no code blocks):

1. **The plan:** Morten's mission and the tower's action, and what they were for (`--plan`).
2. **What happened:** one bullet per event that touched the tower, an ally, or a realm
   Morten is in or next to, each with who (label: verb), what (the goal it served), the
   roll in short and the result. Everything else in one **Elsewhere** line.
3. **The tower now:** HP, attributes, gold, assets by hex, hexes, hostile, allies,
   dissidents.
4. **Next month:** `Threat:` lines (hostile assets within a move, goals aimed at the tower),
   `Chance:` lines (unguarded seats, regimes under 5 HP, caravans near Morten), `Open:`
   lines (where Morten is, the missions there, the tower's actions with prices).

Then the realms (one line each, with the goal), the income lines and the full log, which
go to `transcript.md`. The report holds only what the tower can know; hidden events are
counted, not shown.

### Campaign files

| File | What's in it |
|---|---|
| `realms.json` | The domain state, hidden assets included. **The script owns it**; never edit it. |
| `world.md` | Rendered after every turn; open (the tower's view). |
| `map.json` | The tower's view for the map page (`ui/realms-map.html`, built by `tools/realms_page.py`). |
| `character.md`, `state.md`, `transcript.md` | as before; `state.md` adds month, day, hex and the page's link |
| `gm-secrets.md` | The dungeon floors by hex. Mark rooms explored. |

**In the field** the header adds month, day and hex: "Month 3 · Day 4 · C2 (L9, forest,
Elves)", and a **Rumours** section appears in or next to a realm's hex (`show --at`).

## 10. Constants

| Constant | Value | Source |
|---|---|---|
| Hex income | level × 10 GP (none while occupied) | v1 (occupation ours) |
| Faction HP | 4 + 1/2/4/6/9/12/16/20 per attribute 1–8 | WWN/SWN |
| Raise | the new rating's bonus × 100 GP | ours (the book raises with XP at the same costs) |
| Goal XP | take 2 · break, rob, buy 1 · raise 0; spent at the bonus of the next rating | book's XP, our amounts |
| Attack | d10 + attribute vs d10 + attribute; tie: both take damage | WWN/SWN |
| Asset limit | as many of a type as the attribute; 100 GP a month each over | WWN/SWN (from memory) |
| Claim · river · Walls | +1 · +1 · +1 | v1, ours |
| Seat | damage to a Force asset at the seat also hits HP; unguarded seat counter 1d4 | after the book's Base of Influence |
| Hex lost · seat lost | 1d4 · 1d6 HP | ours |
| Repair | asset ¼ cost; faction 1d6 HP for 100 GP | ours |
| Strike · Rob | 2d6 · 1d6 and tier × 100 GP (× 2 Treasury) | ours |
| Contact | DC 10 + ruler's Cunning (−4 Tyrant) | ours |
| Hostility | 3 months; 6 for a seat | ours |
| Raider on a seat | 200 GP | ours |
| Disorder | 1 month | ours |
| Tyrant income | × 1.5 | v1 |
| Mission fights | tier 1/2/3 = Low/Moderate/High for his level; ≤ 4 monsters | ours |
| Start | attributes S ÷ 10 (min 1), treasury S × 10, 2 Force + 1 Cunning + 1 Wealth asset | v1 shape |
| Tower start | F1 C1 W1, HP 7, 100 GP | ours |
| AI | rich at 1,200 GP · buys first while its army is under 2 · rests 3 months from a beaten faction · drops a goal after 6 months · a Conqueror counts each defender near a hex as −5 levels | ours (tuning) |

## 11. Left for later

- **Morten on the battlefield** (Fireball on a Warband): not in this build. His missions
  hit one asset; mass combat waits.
- Alliances between realms, realms coming back, racial bonuses and biome effects.
- Ley crystals as a wizard's resource; the km scale of a hex.

## 12. The sim (passive tower)

`sim`, seeds 1–10, 24 months each, the tower taking no action:

- **Regimes fall sometimes, not every year:** 7 falls in 10 worlds (0.35 a world a year;
  over 60 months and 30 seeds, 0.6 a world a year, 3 realms gone).
- **Conquerors grow:** 8 of 14 end bigger than they started (3 → 4 or 5 hexes in two
  years; up to 10 hexes in five).
- **Stewards hold:** every Steward kept its land in 24 months.
- **Upkeep bites:** a quarter of the realms' income goes to upkeep in two years (45% over
  five, when 1.5 assets a world are disbanded for want of pay).
- **The tower at rest** is attacked about twice a year by a Slaver or Raider next door and
  sacked about once in 18 months (half its gold), never loses a hex and is never wiped out.
