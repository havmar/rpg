# Realms v3: the overworld

An overworld for D&D Crunch: a small hex map of six realms and Morten's tower, played as
monthly turns on top of the dungeon game. Same feel: minimal narration, open numbers,
every roll in the log. The realms are **static**: each holds its hexes and works on **one
goal with a clock**, rolling one d6 a month for it. Morten's missions move the clocks
directly, the tower has one goal of its own filled by his deeds, and a ladder of five
tiers takes him from Hermit to Master of the twenty hexes. Every event is one sentence
about a goal the map already shows. Nothing is hidden from the tower but the dungeon
floors.

A campaign with a `realms.json` of version 3 is played by this file, which adds to
`dnd-crunch/CLAUDE.md` and wins where they differ. The script `dnd-crunch/tools/realms3.py`
runs the world: it generates the map, rolls the world's turn and keeps `realms.json`. Its
constants block and the table in section 13 hold the same numbers; change both together.
Version 2 (`realms.md`, `tools/realms.py`) still runs the `realms2` and `realms3`
campaigns, version 1 (`realms-v1.md`, `tools/realms_v1.py`) the `realms` campaign; v3
refuses a `realms.json` of version 1 or 2. The design record is `realms-v3-plan.md`.

## 1. The map

As in v2:

- **4 columns × 5 rows = 20 hexes**, columns A–D west → east, rows 1–5 north → south.
  Flat-topped, columns B and D sit half a hex south. `world.md` lists every hex's
  neighbours.
- **Hex level 1–20**, each used once: its ley. A hex pays its holder **level × 10 GP a
  month**, sets the wandering monsters, and holds **floor N** of the dungeon (N = level).
- **Biomes** by row, flavour only (a Mine needs hills or mountains, Caravans plains or
  savanna).
- **2 rivers** along hex edges, **2 lakes** inside hexes, flavour only: nothing attacks
  across them any more.
- **Travel:** entering a hex takes 1 day. Each day outside the tower hex, `1d6`: on a 1, a
  wandering encounter for that hex's level (`encounter --hex HEX`). From Lord on, a tower
  hex with a garrison has no wandering checks either.

## 2. Peoples and realms

- **6 peoples, 6 realms:** Humans, Elves, Orcs, Gnomes, Tieflings, Goblinkind. Each realm
  starts with 3 contiguous hexes (one of them 4). Every hex keeps its people; conquest
  changes only the holder.
- **Neighbours:** two realms are neighbours when a hex of one touches a hex of the other.
  The tower is a neighbour of every realm whose hex touches one of the tower's.
- **The tower** is on the level 1 hex, its people the tower folk. The hex is **warded**: it
  can never be taken, by any goal. The tower itself is hurt only through **Hold** (section
  7).

## 3. A realm

| Field | What it is |
|---|---|
| **Ruler** | name, title, **label: verb** (section 6) |
| **Force** 1–5 | its army. Sets the tier of its fights and gives +1 / −1 on goal rolls against a weaker / stronger realm |
| **Treasury** | GP. Spent on goals that have a price; what Morten robs; what Give adds to |
| **Seat** | the hex the ruler sits in (its deepest hex at the start). A realm whose seat is taken moves it to its deepest hex left |
| **Hexes** | what it holds. They change only when a goal says so |
| **Sites** | the seat, a garrison, works, walls (section 4): the things Morten can strike |
| **Goal** | one line: a kind, a target, a **clock** of N marks, the month it was picked (section 5) |
| **Standing** | with the tower, −2 to +2 (section 7) |
| **Dissident** | the name a won Contact gives the tower, once standing is +1 or more; needed to topple (section 10) |

- **A realm's tier** from its Force: Force 1–2 **tier 1**, 3–4 **tier 2**, 5 **tier 3**.
  Its seat fights one tier up (max 3), its works one tier down (min 1). So a Force-5
  realm's seat is a High fight for Morten's level and its works a Moderate one, and a
  Force-1 neighbour's garrison is a Low fight: weak neighbours first.
- **Start:** S = the realm's hex levels summed. Force = S ÷ 10, rounded, min 1, max 5.
  Treasury S × 10 GP. The seat at its deepest hex, a garrison on its second-deepest, works
  on its third (a four-hex realm's fourth hex has nothing). 4 rulers bad, 2 good. Good
  rulers start at standing +1, bad at 0. Each realm starts with a goal from its tag and
  0 marks, no dissident.
- **A realm is never destroyed.** With every hex lost it still has a ruler and a treasury,
  holds no land, pays and earns nothing, has no seat site and no hex to be Contacted in,
  and its only goal is *take back* a hex of its people, whatever its Force.
- **The tower** is not a realm: it has no Force and no ruler line. It has a treasury
  (100 GP at the start), **Hold** 3 boxes, **Renown** and a **tier** (section 7), its hexes
  (the warded hex at the start), its sites (none at the start) and one goal (section 10).

## 4. Sites: what Morten can strike

A site sits in one hex and belongs to one realm (or the tower). It doesn't move, has no
HP, never attacks and is never destroyed: a Strike on it moves clocks, nothing more. It
exists to be a fight and to carry a modifier. When a hex changes holder its garrison,
works and walls go with it; a seat is the ruler's and moves with the ruler instead.

| Site | Where | Fight (SRD, by tier) | Modifier |
|---|---|---|---|
| **Seat** | the ruler's hex | the court: Noble, Spy, Tough, Guard, Knight, Guard Captain, at the realm's tier **+1** (max 3) | — |
| **Garrison** | one hex | tier 1 Guard, Scout, Guard Captain · tier 2 Knight, Warrior Veteran, Warhorse · tier 3 Berserker, Warrior Veteran, Gladiator, Ogre, at the realm's tier | **−1** to any goal roll aimed at this hex |
| **Works** | one hex | Farms: Guard, Mastiff, Scout · Mine (hills or mountains): Tough, Guard, Tough Boss · Caravans (plains or savanna): Guard, Scout, Warrior Veteran, Mastiff, at the realm's tier **−1** (min 1) | the holder's **income +50 GP a month**; what Rob takes from |
| **Walls** | a hex a goal or the purse fortified (one per hex) | Animated Armor, Guard, Gargoyle, at the realm's tier | **−1** to goal rolls aimed at this hex; a *take* goal against a walled hex has a 6-mark clock (the tower's, +2) |
| **Beasts** | any hex, for Aid fights (section 9) | the hex's people's beasts: Humans Mastiff, Warhorse, Scout · Elves Giant Owl, Giant Eagle, Giant Elk · Orcs Worg, Dire Wolf, Giant Boar · Gnomes Giant Badger, Giant Goat, Brown Bear · Tieflings Imp, Hell Hound · Goblinkind Giant Hyena, Worg, Gnoll Warrior · the tower folk Mastiff, Giant Owl, Brown Bear | — |

The tower's own sites are never fought: no realm attacks a site, and Morten doesn't
strike his own.

**Mission fights are D&D fights** built from a site's list by `encounter`: **tier 1 a Low
encounter for Morten's level, tier 2 Moderate, tier 3 High** (`Combat Encounters.md`),
at most 4 monsters of at most two kinds, coins a tenth of their XP. The hex level scales
only wandering monsters and the dungeon floor.

Sites are **all open**: the map shows every site, every goal, every clock and every
treasury. `show` prints all of it; there is no `--gm`.

## 5. Goals and clocks

A goal is one line with a kind, a target and a clock. The clock's size is the goal's
weight; marks fill it; a full clock fires the goal's effect at the world's turn. Marks
never go above the size, never below 0.

### The roll

Once a month, each realm rolls **d6** for its goal, plus modifiers:

| Modifier | When |
|---|---|
| +1 / −1 | the goal has a target realm and this realm's Force is higher / lower (never against the tower: it has no Force) |
| −1 | the goal is aimed at a hex with a garrison; −1 more for walls (the tower's sites too; *break the tower* is aimed at the tower hex) |
| +1 | the tower gave this realm 200 GP or more this month (Give) |
| +1 / −1 | the tower backs / hinders it (the Warden's power, section 7) |

| Roll (after modifiers) | Marks |
|---|---|
| natural 1 | **setback:** −1 mark (min 0) |
| 2 or less | nothing |
| 3–5 | +1 |
| 6 or more | +2 |

A plain roll fills 0.67 marks a month, so a 4-clock takes about six months and a 2-clock
three; with +1 it fills about 0.85 a month. Across six realms that is roughly one goal
done somewhere every month, and each realm's line changes about every half year. **A won
Strike takes 2 marks off** (section 9), a full third of a *take* clock: one fight is
visible on the map.

### The catalogue

Every goal the script can hand out, resolve and explain. "Price" is paid from the
realm's treasury when the clock fills; a goal it can't pay **waits full** ("done, waits
for 300 GP") and fires the month the treasury covers it, rolling no more. A goal whose
target is gone (the hex already changed hands, the neighbour already at Force 1, the
tower now an ally for a goal against the tower) is **dropped** and a new one picked.

| Goal | Clock | Target | Price at the end | Effect when the clock is full |
|---|---|---|---|---|
| **take HEX** from REALM (or the tower) | 4 (6 if walled) | the holder | — | the hex changes holder with its garrison, works and walls; a seat there moves to the loser's deepest hex left; the loser **weighs "take back"** first when it next picks a goal |
| **fortify HEX** | 3 | — | 300 GP | Walls at HEX (one per hex) |
| **raise** | 3 | — | 200 × the new Force | Force +1 (max 5) |
| **raid REALM** (or the tower) | 2 | the richest neighbour | — | takes **100 × its own Force GP** from the target's treasury (at most what it holds; from the tower, at most half) |
| **press REALM** | 3 | the weakest neighbour | — | its own Force +1 (max 5), the target's Force −1 (min 1) |
| **squeeze** | 2 | — | — | treasury +100 GP per hex held; Contact in its hexes is DC +4 for the next 3 months |
| **break REALM** | 4 | a bad neighbour with lower Force | — | the target's Force −1 (min 1) |
| **break the tower** | 4 | the tower | — | the tower's **Hold −1** and half its treasury taken; at Hold 0, the tower's deepest hex but the warded one changes holder instead, with its sites (section 7); the realm's standing −1 (it is at war now) |
| **court the tower** | 2 | the tower | — | its standing with the tower +1 (max +2) |

### Who picks what

A realm with no goal (done, or dropped) picks one the moment it needs one at the world's
turn, in this order, the first that applies, and rolls for it from the next month:

1. **Break the tower** if it is bad and at standing −1 or less; or if it is bad, not an
   ally, the tower is Warden or higher and its standing is 0 or less, on a d6 of 4+.
2. **Take back** a hex of its own people it has lost, if its Force is at least the
   holder's (the tower counts as Force 0; a landless realm takes back whatever its
   Force). The deepest such hex.
3. **Court the tower** if it is good, at standing 0 or +1, and the tower is Lord or
   higher, on a d6 of 4+.
4. **Its tag's goal:**

| Label | Tag | Shown as | Goal |
|---|---|---|---|
| bad | Conqueror | bad: takes land | **take** the deepest hex next to its own that is not a seat and not the warded hex |
| bad | Raider | bad: robs its neighbours | **raid** the richest neighbour (the tower counts when it is richest) |
| bad | Slaver | bad: takes people for soldiers | **press** the weakest neighbour (never one at Force 1 already) |
| bad | Tyrant | bad: squeezes its own people | **squeeze**; while its squeeze still runs, **fortify** its seat; when that is walled, **raise** |
| good | Steward | good: keeps the peace | **fortify** its seat, then **raise**, then fortify its other hexes (deepest first) |
| good | Liberator | good: fights tyrants | **break** a bad neighbour with lower Force; else as a Steward |

5. **Raise** if it has the price in hand and is under Force 5; else **fortify** its seat
   if unwalled; else **squeeze**.

An **ally** (+2) never picks *break the tower* or *raid the tower*; one it already holds
is dropped. A goal not done **6 months** after it was picked is dropped at clean-up, its
marks lost, and a new one picked; a goal that waits full is not dropped.

## 6. Rulers

As v2: a name from the people's list, a title, a label and a tag, always shown as
**label: verb** ("Reeve Galen (bad: takes people for soldiers)"), everywhere. Rulers
change only when the tower **topples** them (section 10): the dissident takes the throne
with a random good tag. There is no regime HP and no random collapse; what happens to a
realm is on its goal line.

## 7. Standing, Hold, Renown and the ladder

### Standing

Each realm's attitude to the tower, one number:

| −2 enemy | −1 wary | 0 neutral | +1 friendly | +2 ally |
|---|---|---|---|---|

| Change | Cause |
|---|---|
| −1 | Morten Strikes one of its sites (**−2** for its seat) or Robs it |
| −2 | the tower takes one of its hexes |
| +1 | a won Aid for it; a won Contact; the tower gives it 200 GP or more in a month (once a month). None of these lift it past +1: **ally is the tower's goal** (section 10) |
| +1 | its *court the tower* goal fires (this one can reach +2) |
| = +2 | the tower's *ally* goal is done for it; a ruler the tower put on the throne |
| −1 | its *break the tower* goal fires (it is at war now) |

**An ally** (+2) never picks *break the tower* or *raid the tower*, and adds **+1 mark a
month to the tower's goal**, whatever that goal is (one ally counts; two at Power,
section below). **An enemy** (−2) refuses Contact. Nothing drifts back on its own:
standing moves only by deeds. Standing stays within −2 to +2.

### Hold

The tower's buffer: **3 boxes**. A *break the tower* goal that fires takes one box and
half the treasury; at 0 boxes it takes a hex of the tower's instead (its deepest, never
the warded one), with the sites there. **Mend** a box for 200 GP (a purse action). Hold is
the only thing on the tower that can be hurt, and only by a goal the human watched fill
for months.

### Renown and the ladder

**Renown** = hexes held beyond the tower hex + allies + 2 × rulers toppled. It is read off
the map after every world's turn, never bought. The tier is the last row Renown reaches:

| Tier | Name | Renown | The power it brings |
|---|---|---|---|
| 0 | Hermit | 0 | — |
| 1 | Lord of the hex | 2 | **Garrison** and **Walls** may be bought for the tower's hexes (purse actions, section 8). Wandering checks stop in a garrisoned tower hex |
| 2 | Warden of the marches | 5 | **Back** or **hinder** one realm's goal roll a month (+1 / −1) for 100 GP |
| 3 | A power in the land | 9 | Morten's Strike and Aid move **3 marks** instead of 2 (on the realm's goal and on the tower's); **two allies** count on the tower's goal |
| 4 | Master of the twenty hexes | 14 | May **set an ally's next goal** from the catalogue each month: the goal that ally picks when its current one ends. Reaching Master with **every realm an ally or toppled** ends the campaign: the world is his |

Renown can fall (a hex lost; a toppled ruler is permanent). The tier falls with it; the
report says so in one line.

**How the realms feel it:** from Warden on, bad rulers who aren't allies start weighing
*break the tower* (section 5, rule 1), and good ones *court the tower* from Lord on.
Rising makes enemies and friends at once, which is what the arc wants.

## 8. Purse actions

Not goals and not limited to one: anything the treasury covers, declared with the month's
orders and paid at the world's turn. A purse action the treasury can't cover, or the tier
doesn't allow, is rejected with the orders.

| Action | Cost | Needs | Effect |
|---|---|---|---|
| **Garrison HEX** | 400 GP | Lord; a hex the tower holds; none there yet | a site: −1 to goal rolls aimed at that hex |
| **Walls HEX** | 600 GP | Lord; a garrison there; none there yet | −1 more; a *take* against it needs 6 marks |
| **Works HEX** | 300 GP | a hex the tower holds; none there yet | income +50 GP a month; a site a realm's Raid can target |
| **Mend** | 200 GP | Hold below 3 | Hold +1 |
| **Give REALM GP** | the GP | — | the gold is theirs. 200 GP or more in one month: +1 on its goal roll this month, standing +1 (once a month, to at most +1), and +1 on the tower's goal when that goal is *ally REALM*. While the tower's goal is *topple REALM*, a Give to REALM goes to its **dissident** instead: +1 on the topple clock (once a month) and nothing else |
| **Back / hinder REALM** | 100 GP | Warden | +1 / −1 on that realm's roll this month; one a month |

**Deposit and withdraw** move gold between Morten's purse and the tower's treasury, free,
with the orders. The treasury pays purse actions and goal prices; the purse buys at the
trader.

## 9. Morten's month

Travel as in section 1, one hex a day, wandering checks. Then **one mission in the hex he
is in, or none.** Strike, Rob and Aid are D&D fights built by `encounter`; Contact is a
check.

| Mission | Where | The fight | On a win |
|---|---|---|---|
| **Strike SITE** | a realm's hex with one of its sites | the site's list at its tier (section 4): seat tier +1, garrison the realm's tier, works tier −1, walls the realm's tier | the realm's goal **−2 marks** (min 0); standing −1 (seat −2); and marks on the tower's goal where section 10 says so |
| **Rob** | a realm's hex with its works | the works' list at the realm's tier −1 (the same fight as a Strike on them) | **100 × its Force GP** from its treasury (at most what it holds) to the tower's treasury; standing −1; the tower's goal +0 |
| **Aid REALM** | the hex its goal is aimed at (*take*, *fortify*); the aided realm's seat for goals with no hex | the obstacle: a goal against another realm, that realm's garrison list at that realm's tier; otherwise the hex's beasts at the aided realm's tier. A goal aimed at the tower can't be aided | the realm's goal **+2 marks**; standing +1 (to at most +1); and **+2 on the tower's goal** if it is *ally REALM* |
| **Contact REALM** | any of its hexes | no fight: Persuasion (CHA) vs **DC 12 + 3 if the ruler is bad − 2 × standing + 4 while it is squeezed** (a wary bad ruler DC 17, a neutral good one DC 12, a friendly good one DC 10). Standing −2 refuses | standing +1 (to at most +1); at +1 or more after that, a **dissident** is named (needed to topple, section 10); +1 on the tower's goal if it is *ally REALM* |
| **Delve** | the floor under the hex | as in the dungeon game | no domain effect |

A win means every foe dead, fled or surrendered, or the check made. Pass a mission to
`turn` only when it succeeded. **Death** ends the month: the mission fails, he loses the
coins and gems he carried, he wakes at the tower; purse actions stand. The trader is at
the tower.

At Power (tier 3) the 2s above are 3s: a Strike takes 3 marks off and gives 3, an Aid
adds 3 and gives 3. Contact's and Give's +1 stay +1.

## 10. The tower's goal

The tower keeps **one goal at a time**, declared by the human with the month's orders and
kept until done or dropped (dropping loses its marks). Its marks come from Morten's
missions and from allies, never from a die. Its clock is set when it is declared and
doesn't change after. A full clock fires at the world's turn, and the tower has no goal
until the human declares the next.

| Goal | Clock | Needs | Marks from | When the clock is full |
|---|---|---|---|---|
| **take HEX** from REALM | 2 + the holder's Force (3–7; +2 if walled) | HEX held by a realm | a won Strike on any site in HEX +2; an ally +1 a month | the hex is the tower's with its garrison, works and walls (a seat there moves to the loser's deepest hex left); standing with the loser −2; Renown +1 |
| **ally REALM** | 3 | REALM not an ally | Contact +1; Aid +2; Give 200 GP +1 (once a month); an ally +1 a month | standing +2; Renown +1 |
| **topple REALM** | 3 + its Force (4–8) | a **dissident** named there | a Strike on its seat +2; on its garrison, works or walls +1; Give 200 GP to the dissident +1 (once a month); an ally +1 a month | the dissident rules with a random good tag, full treasury kept, Force kept, standing +2, the realm picks a new goal by its new tag, the dissident is cleared; Renown +2 |

At Power the 2s are 3s (the garrison's +1 stays). A Strike on a site of the target realm
outside HEX adds nothing to *take HEX*; a Strike adds nothing to *ally REALM*. A realm
that courts its way to +2 while the tower's goal is *ally REALM* ends that goal at once.

So the road to the throne is a thing you can watch fill: Contact twice to find the
dissident, then Strike the seat while an ally adds a mark a month. And "conquer the world"
is literal on the map: take the hexes you want, ally the good rulers, topple the bad ones.

## 11. The world's turn

Every month, after Morten's month, the script runs:

1. **Morten's month lands:** the mission's result (marks on his target's goal and on the
   tower's, standing changes, Rob's gold), deposit and withdraw, purse actions, Give,
   back or hinder.
2. **Income:** hex level × 10 GP to each holder (Tyrant × 1.5), works +50 GP each, the
   tower's hexes to the tower's treasury.
3. **Each realm rolls its goal,** highest Force first (ties by d6): marks, a full clock
   fires (and pays, or waits), a new goal is picked where needed.
4. **The tower's goal:** allies' marks; a full clock fires.
5. **Clean-up:** Renown and tier; goals 6 months old dropped and replaced; squeeze
   timers count down; the month advances.

Nothing else happens. Six rolls, at most six effects, one for the tower.

## 12. Running a month

The script is `python3 dnd-crunch/tools/realms3.py`; DIR is the campaign folder.

| Command | What it does |
|---|---|
| `new --seed N --campaign DIR [--level 3]` | The world: `realms.json` (version 3), `world.md`, `map.json`, and the 20 floors in `gm-secrets.md`. |
| `show --campaign DIR [--at HEX]` | The world: every realm's line, goal and clock, sites and treasury; `--at`, the rumours from a hex (the goals and clocks in and next to it). Nothing is hidden, so there is no `--gm`. |
| `encounter --campaign DIR --site ID` | The fight for a Strike or Rob on that site (its id as `show` prints it). |
| `encounter --campaign DIR --aid REALM` | The fight for an Aid, and the hex it is fought in. |
| `encounter --campaign DIR --contact REALM` | The Contact DC. |
| `encounter --campaign DIR --hex HEX` | A wandering encounter for the hex's level. |
| `turn --campaign DIR [options] [--dry-run]` | The world's turn: prints the report, saves `realms.json`, `world.md`, `map.json`. |
| `sim [--seeds 1-10] [--months 24]` | Passive-tower months for tuning. |

**`turn` options:**

| Option | Meaning |
|---|---|
| `--at HEX` · `--level N` | where Morten ends the month · his level now |
| `--strike ID` · `--rob ID` · `--aid REALM` · `--contact REALM` · `--delve` | the month's won mission (one) |
| `--goal take:HEX` · `ally:REALM` · `topple:REALM` · `drop` | the tower's goal (kept when omitted) |
| `--buy garrison@HEX` · `walls@HEX` · `works@HEX` · `mend` | purse actions (repeatable) |
| `--give REALM=GP` · `--back REALM` · `--hinder REALM` | repeatable Give; one back or hinder |
| `--deposit GP` · `--withdraw GP` | gold moved between the purse and the treasury |
| `--plan "why"` | a line for The plan (repeatable) |

The Master's set-goal is declared with the orders too (the engine's own option names it;
`turn --help`).

Orders are checked before anything happens: a Strike or Rob needs Morten in the site's
hex, an Aid in the goal's hex, a Contact in the realm's hex; a purse action needs the
tier and the gold; a goal its conditions (a dissident for *topple*, a realm's hex for
*take*). One rejected order prints one line and saves nothing: fix it and rerun.
**Always `--dry-run` first.**

### Steps

1. **Start of the month: choices.** The human (or the GM as Morten) picks travel, the
   mission, the tower's goal if it has none or changes it, the purse actions, Give. The
   orders are fixed from here.
2. **Travel**, one hex a day, wandering checks; `show --at HEX` for the rumours.
3. **The mission:** `encounter --site ID` (or `--aid REALM`, `--contact REALM`), then the
   fight or the check as usual. Delve: the floor from `gm-secrets.md`.
4. **The world's turn:** `turn` with the month's options, `--dry-run` first. Update
   `character.md` for gold moved, then reply in the world's-turn format below.
5. **The map:** a campaign at the table refreshes its Realm tab with `table.py realm`
   after every world's turn (`web/README.md`); the old map page (`ui/realms-map.html`)
   is v2's and doesn't draw a v3 world.
6. Update `state.md` and `transcript.md`, commit and push, as in CLAUDE.md.

### The world's-turn reply

The script prints it in this order; the chat reply keeps it (plain Markdown, no code
blocks), written as the **Report style** dials say (domain **summary** by default):

1. **The plan:** Morten's mission, the tower's goal and purse actions, and what they were
   for (`--plan`).
2. **What happened:** the **tower's goal line first** ("Take B4 from the Gnomes: 4 of 6
   marks, +2 for the Strike on their garrison, +1 from the Humans"), then **one sentence
   per realm**: who (*label: verb*), the goal, the roll in two words, the marks now, and
   the effect if it fired. Realms far from Morten and the tower that rolled nothing fold
   into one **Elsewhere** line.
3. **The tower now:** tier and Renown, Hold, gold, hexes and sites, allies and enemies,
   the goal and its clock.
4. **Next month:** `Threat:` every goal aimed at the tower or its hexes, with marks left
   and the roll's odds in words; `Chance:` clocks one Strike from empty or one Aid from
   full, realms one Contact from ally, treasuries worth a Rob; `Open:` where Morten is,
   the missions there with their tier, the purse actions with prices.

Then the realms (one line each, with the goal and clock), the income lines and the roll
log (every d6 with its modifiers), which go to `transcript.md`. A month, as it reads:

> **The plan.** Morten walks to B4 (the Gnomes' plains, Force 4) to Strike their garrison:
> the tower's goal is *take B4* (clock 6, 1 mark from the Humans last month), and the
> Gnomes' own goal, *raid the tower*, is at 1 of 2. The purse buys nothing; 140 GP stays
> for Walls later.
>
> **What happened.**
> - **The tower:** *take B4 from the Gnomes*, **4 of 6** (+2 the Strike, +1 the Humans).
> - **Gnomes** (bad: robs its neighbours), *raid the tower*: the Strike cost them 2 marks,
>   and a 3 put one back: **1 of 2**. Standing −1, wary.
> - **Humans** (good: keeps the peace), *fortify A4*: a 5, **3 of 3, done**, 300 GP paid.
>   Walls stand at their seat. New goal: *raise* (3).
> - **Elsewhere:** the Orcs' *raid the Gnomes* at 1 of 2; the Elves' *take B1* at 2 of 4;
>   the Tieflings and Goblinkind rolled nothing.
>
> **The tower now.** Hermit (Renown 1: the Humans). Hold 3 of 3 · 140 GP · hex B5 · no
> sites · allies: Humans · enemies: none · goal *take B4*, 4 of 6.
>
> **Next month.** Threat: the Gnomes' *raid the tower* needs 1 mark; a 3 or more does it
> (two in three), and takes up to 70 GP. Chance: one more Strike in B4 (Moderate fight,
> Knights) and the Humans' mark end the goal next month; the Goblinkind (good, friendly)
> would be a quick *ally* goal: 3 marks, Contact at DC 10. Open: Morten in B4; Strike the
> garrison (Moderate) · Rob the works (Low, 400 GP) · Delve floor 10 · travel.

Six lines, and every number on them is a thing the map shows.

### Campaign files

| File | What's in it |
|---|---|
| `realms.json` | The domain state, version 3. **The script owns it**; never edit it. |
| `world.md` | Rendered after every turn; the whole world (nothing is hidden). |
| `map.json` | The world for the table's Realm tab: hexes with their sites, the realms with their clocks and standing, the tower with its tier, Renown and Hold, last month's events and the report. |
| `character.md`, `state.md`, `transcript.md` | as before; `state.md` adds month, day and hex |
| `gm-secrets.md` | The dungeon floors by hex. Mark rooms explored. |

**In the field** the header adds month, day and hex: "Month 3 · Day 4 · C2 (L9, forest,
Elves)", and a **Rumours** section appears in or next to a realm's hex (`show --at`): its
goal, its clock and its standing, in words.

## 13. Constants

| Constant | Value | Source |
|---|---|---|
| Hex income | level × 10 GP; Tyrant × 1.5; works +50 GP | v2 |
| Force | 1–5; start S ÷ 10, rounded, min 1 | v2's start, capped |
| Tier from Force | 1–2 → 1, 3–4 → 2, 5 → 3; seat +1 (max 3), works −1 (min 1) | ours |
| Mission fights | tier 1/2/3 = Low/Moderate/High for his level; ≤ 4 monsters of ≤ 2 kinds; coins a tenth of XP | v2 |
| Goal roll | d6; natural 1 −1 mark, ≤ 2 nothing, 3–5 +1, 6+ +2 | Mausritter's shape (4–5 one, 6 two), shifted one step so an unmodified clock moves |
| Roll mods | ±1 Force, −1 garrison, −1 walls, +1 Give ≥ 200 GP, ±1 back/hinder | Mausritter's resources, cut to five |
| Clocks | take 4 (6 walled) · fortify 3 · raise 3 · raid 2 · press 3 · squeeze 2 · break 4 · break the tower 4 · court 2 | ours; Blades' 4/6/8 cut in half for monthly ticks |
| Tower's clocks | take 2 + Force (+2 walled) · ally 3 · topple 3 + Force | ours |
| Morten's marks | Strike −2 / +2 (topple: seat +2, other sites +1) · Aid +2 · Contact +1 · Give +1; 2s are 3s at Power | Mausritter's "player involvement: 1–3 marks" |
| Ally's marks | +1 a month on the tower's goal; two allies at Power | ours |
| Prices | fortify 300 · raise 200 × new Force · garrison 400 · walls 600 · works 300 · mend 200 · back/hinder 100 | ours |
| Raid · Rob | 100 × Force GP; a raid on the tower at most half its treasury | ours |
| Squeeze | +100 GP per hex; Contact DC +4 for 3 months | ours |
| Press | own Force +1, target −1 | ours |
| Break REALM · the tower | target Force −1 · Hold −1 and half the treasury (a hex at Hold 0) | ours |
| Contact DC | 12 + 3 bad − 2 × standing (+4 squeezed); refused at −2 | ours |
| Standing | −2..+2; the table in section 7 | Blades' status, −3..+3 cut to five |
| Hold | 3 boxes; mend 200 GP | Blades' hold, as boxes |
| Renown | hexes beyond the tower hex + allies + 2 × toppled; tiers at 2, 5, 9, 14 | ours; Blades' tier ladder |
| Picker | break the tower (bad, standing ≤ −1; or bad, Warden+, standing ≤ 0, d6 4+) · take back · court (good, 0 or +1, Lord+, d6 4+) · the tag · raise, fortify, squeeze | ours |
| Goal dropped | 6 months after it was picked | v2 |
| Turn order | highest Force first, ties by d6 | ours |
| Start | seat + garrison + works on a realm's three deepest hexes; good +1 standing, bad 0; 4 bad, 2 good; tower Hold 3, 100 GP, Hermit, no sites, the warded hex | ours |
| End | Master with every realm an ally or toppled | ours |

## 14. Left for later

- **Morten on the battlefield** (Fireball on an army): not in this build. His missions
  hit one site; mass combat waits.
- Alliances between realms, realms coming back from nothing by any road but *take back*,
  racial bonuses and biome effects.
- Ley crystals as a wizard's resource; the km scale of a hex.
- Hidden anything: v3 shows the whole world on purpose.

## 15. The sim

The numbers are filled in after the engine's `sim` (seeds 1–10, 24 months each, the
tower taking no action; then a second sim with a scripted Morten striking the weakest
neighbour's garrison, then its seat). The targets, from the plan: about one goal fires
somewhere every month and no realm's line goes a year unchanged; two to four hexes change
hands per world in two years, a Conqueror grows, a Steward holds its seat; no realm loses
all its hexes and none reaches Force 5 from 1; the tower at rest is targeted by a *break
the tower* once or twice in two years, loses one Hold box about once and never a hex at
Hold 3; raids move gold and goals get paid without a realm sitting on 2,000 GP for a year;
a scripted Morten takes a hex in 3–5 months at level 3–4 and can reach Master in about
three years of play.
