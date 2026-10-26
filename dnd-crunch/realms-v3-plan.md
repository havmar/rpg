# Realms v3: goal clocks on a hex map (a plan)

**Status: implemented 2026-10-26.** The rules are `realms-v3.md` and the engine
`tools/realms3.py` (tests in `tools/test_realms3.py`); the table plays it (`tools/table.py`,
the Realm tab, a v3 fixture in `web/dev/fixture-v3/`). Realms v2 (`realms.md`,
`tools/realms.py`) keeps running the `realms2` and `realms3` campaigns. Where the build
differs from this plan, `realms-v3.md` wins; section 20 lists the differences and the sim's
numbers are in the rules' sim section. This document stays as the design record.

## 1. Why a third version

Two versions of the overworld have been played. v1 was home-made and illegible. v2 fixed
that by adapting the *Worlds Without Number* faction rules properly: factions with Force,
Cunning and Wealth, assets on the map, d10 duels, HP, hostility, hidden Cunning assets. The
engine works and the sim is tuned, but after two months of `realms3` the heads-up in
`CLAUDE.md` still stands: **the human enjoys the fights and can't follow the domain
turns.**

What the two versions taught:

- **The fights are the game.** A mission that turns into a CR-built D&D fight is the part
  that lands. It never needed the asset duel underneath it.
- **The WWN turn is a GM-side wargame.** Its play reports (few; mostly reviews) agree: it
  shines when the GM wants to be surprised by a world the party is small in, and it is
  "complex and fiddly compared to the rest of the rules". Six realms with four assets each
  plus hidden pieces produce several events a month that don't touch Morten, and every one
  has to be explained.
- **It is symmetric.** The tower is a faction like the others, starting at the bottom, so
  Morten's lever is an economics game of Buy and Raise. The human's vision is an arc: a
  wizard who ends as one of the defining actors of a small world. WWN has no ladder for
  that.
- **Every event should be one sentence about a known goal.** v2's goal line ("bad: takes
  land · goal: take B1, month 3 of it") was the one thing that read well. v3 makes that
  line the whole system.

The simplest well-tested design in the OSR is the *Mausritter* faction turn (two pages:
each faction has a goal with a progress track and a few resources; between sessions roll a
d6 per faction with small modifiers; 4–5 marks one step, 6 marks two; a finished goal
changes the world). *Cairn 2e*'s agendas and *Dungeon World*'s fronts are the same shape
without dice; *Blades in the Dark* adds the two pieces Mausritter lacks and this game
needs: a **status** with each faction and a **tier ladder** for the player's own outfit.
v3 is those three ideas fitted to the 20-hex map.

## 2. The idea in one paragraph

Six **static realms** hold their hexes. Each realm has one **goal** with a **clock** (3 to
6 marks) and rolls one d6 a month for it: a setback, nothing, one mark or two. A full
clock changes the map (a hex changes hands, walls go up, an army grows, the tower is
sacked) and the realm picks its next goal by its ruler's tag. The world's turn is six
sentences. **Morten's missions move the clocks directly:** a won Strike in a realm's hex
takes two marks off its goal; a won Aid adds two to an ally's. The tower has one goal of
its own (take a hex, win an ally, topple a ruler) whose marks come from Morten's deeds,
not dice. **Standing** (−2 enemy to +2 ally) says how each realm treats the tower, and
**Renown** (hexes, allies, rulers toppled) climbs a **ladder of five tiers** from Hermit to
Master, each with one power. The game ends when every realm is an ally or has fallen to
him.

## 3. What stays from v2

- The map: 4 × 5 flat-topped hexes, one level per hex (1–20), biomes by row, two rivers,
  two lakes, `world.md` with every hex's neighbours; the `new --seed N` generator.
- Hex income **level × 10 GP a month** to its holder; a Tyrant's × 1.5.
- Six peoples and six realms of 3 or 4 hexes; rulers with a name, a title and a tag shown
  everywhere as **label: verb**; 4 bad, 2 good at the start.
- The tower on the level 1 hex, **warded**: that hex can never be taken.
- **Morten's month then the world's turn**; 1 day per hex; wandering checks; Delve of the
  floor under the hex; death ends the month and sends him home.
- **Mission fights are D&D fights built from SRD monsters** by tier: tier 1 a Low encounter
  for his level, tier 2 Moderate, tier 3 High; at most 4 monsters of at most two kinds;
  coins a tenth of their XP. The fight lists (by people and by site) are v2's.
- The report in four parts: The plan, What happened, The tower now, Next month.
- `--dry-run` first; a rejected order prints one line and saves nothing; the script owns
  `realms.json`; `world.md` and `map.json` are rendered after every turn; the map page and
  the table's Realm tab read `map.json`.

## 4. What goes

Cunning and Wealth as attributes; faction HP; assets as movable pieces and their d10
duels; Buy, Move, Raise, Repair, Seize as a menu of actions; upkeep and asset limits;
hidden Cunning assets and Informers; hostility timers; Seditionists and the coup; disorder;
the faction XP table. Each has a replacement below, and every replacement is a sentence
the report can print.

## 5. A realm

| Field | What it is |
|---|---|
| **Ruler** | name, title, **label: verb** (section 8) |
| **Force** 1–5 | its army. Sets the tier of its fights and gives +1/−1 on goal rolls against a weaker/stronger realm |
| **Treasury** | GP. Spent on goals that have a price; what Morten robs; what Give adds to |
| **Seat** | the hex the ruler sits in (its deepest hex at the start). A realm whose seat is taken moves it to its deepest hex left |
| **Hexes** | what it holds. They change only when a goal says so |
| **Sites** | the seat, a garrison, works, walls (section 6): the things Morten can strike |
| **Goal** | one line, a **clock** of N marks, the month it was picked (section 7) |
| **Standing** | with the tower, −2 to +2 (section 9) |

**Start:** S = the realm's hex levels summed. Force = S ÷ 10, rounded, min 1, max 5.
Treasury S × 10 GP. The seat at the deepest hex, a garrison on its second hex, works on
its third (a four-hex realm's fourth hex has nothing). Good rulers start at standing +1,
bad at 0. Each realm starts with a goal and 0 marks.

A realm is never destroyed. With every hex lost it still has a ruler and a treasury, holds
no land, pays nothing, and its only goal is to take a hex back.

## 6. Sites: what Morten can strike

A site sits in one hex and belongs to one realm (or the tower). It doesn't move, has no
HP and never attacks. It exists to be a fight and to carry a modifier.

| Site | Where | Fight (SRD, by tier) | Modifier |
|---|---|---|---|
| **Seat** | the ruler's hex | the court: Noble, Spy, Tough, Guard, Knight, Guard Captain, at the realm's tier **+1** (max 3) | — |
| **Garrison** | one hex | tier 1 Guard, Scout, Guard Captain · tier 2 Knight, Warrior Veteran, Warhorse · tier 3 Berserker, Warrior Veteran, Gladiator, Ogre, at the realm's tier | **−1** to any goal roll aimed at this hex |
| **Works** | one hex | Farms: Guard, Mastiff, Scout · Mine (hills or mountains): Tough, Guard, Tough Boss · Caravans (plains or savanna): Guard, Scout, Warrior Veteran, Mastiff, at the realm's tier **−1** (min 1) | the realm's **income +50 GP**; the thing Rob takes from |
| **Walls** | a hex a goal fortified | Animated Armor, Guard, Gargoyle, at the realm's tier | **−1** to goal rolls aimed at this hex; a *take* goal against a walled hex has a 6-mark clock |
| **Beasts** | any hex, for Aid fights (section 10) | the people's beasts, as v2: Humans Mastiff, Warhorse, Scout · Elves Giant Owl, Giant Eagle, Giant Elk · Orcs Worg, Dire Wolf, Giant Boar · Gnomes Giant Badger, Giant Goat, Brown Bear · Tieflings Imp, Hell Hound · Goblinkind Giant Hyena, Worg, Gnoll Warrior | — |

**A realm's tier** from its Force: Force 1–2 **tier 1**, 3–4 **tier 2**, 5 **tier 3**. So a
Force-5 realm's seat is a High fight for Morten's level and its works a Moderate one, and
a Force-1 neighbour's garrison is a Low fight. That is the arc: weak neighbours first.

Sites are **all open**: the map shows every site, every goal and every clock. Nothing in
v3 is hidden from the tower except the dungeon floors.

## 7. Goals and clocks

A goal is one line with a kind, a target and a clock. The clock's size is the goal's
weight; marks fill it; a full clock fires the goal's effect at the world's turn.

### The roll

Once a month, each realm rolls **d6** for its goal, plus modifiers:

| Modifier | When |
|---|---|
| +1 / −1 | the goal has a target realm and this realm's Force is higher / lower |
| −1 | the goal is aimed at a hex with a garrison; −1 more for walls (the tower's too) |
| +1 | the tower gave this realm 200 GP or more this month (Give) |
| +1 / −1 | the tower backs / hinders it (the Warden's power, section 9) |

| Roll (after modifiers) | Marks |
|---|---|
| natural 1 | **setback:** −1 mark (min 0) |
| 2 or less | nothing |
| 3–5 | +1 |
| 6 or more | +2 |

A plain roll fills 0.67 marks a month, so a 4-clock takes about six months and a 2-clock
three; with +1 it fills about 0.85 a month. Across six realms that is roughly one goal
done somewhere every month, and each realm changes every half year. **A won Strike takes
2 marks off** (section 10), a full third of a *take* clock: one fight is visible on the
map.

### The catalogue

Every goal the script can hand out, resolve and explain:

| Goal | Clock | Target | Price at the end | Effect when the clock is full |
|---|---|---|---|---|
| **take HEX** from REALM (or the tower) | 4 (6 if walled) | the holder | — | the hex changes holder; its garrison or works there become the taker's; the loser's standing with the taker is not tracked, but the loser **weighs "take back"** first |
| **fortify HEX** | 3 | — | 300 GP | Walls at HEX (one per hex) |
| **raise** | 3 | — | 200 × the new Force | Force +1 (max 5) |
| **raid REALM** (or the tower) | 2 | the richest neighbour | — | takes **100 × its own Force GP** from the target's treasury (at most what it holds; from the tower, at most half) |
| **press REALM** | 3 | the weakest neighbour | — | its own Force +1 (max 5), the target's Force −1 (min 1) |
| **squeeze** | 2 | — | — | treasury +100 GP per hex; Contact in its hexes is DC +4 for the next 3 months |
| **break REALM** | 4 | a bad neighbour with lower Force | — | the target's Force −1 (min 1) |
| **break the tower** | 4 | the tower | — | the tower's **Hold −1** and half its treasury taken; at Hold 0, one hex of the tower's instead (never the warded one) (section 9) |
| **court the tower** | 2 | the tower | — | standing with the tower +1 |

### Who picks what

A realm with no goal (done, or dropped after 6 months) picks one at the world's turn, in
this order, the first that applies:

1. **Break the tower** if it is bad and at standing −1 or less; or bad, not an ally, and
   the tower is Warden or higher (section 9) and standing is 0 or less, on a d6 of 4+.
2. **Take back** a hex of its own people it has lost, if its Force is at least the
   holder's.
3. **Court the tower** if it is good, at standing 0 or +1, and the tower is Lord or higher,
   on a d6 of 4+.
4. **Its tag's goal:**

| Label | Tag | Shown as | Goal |
|---|---|---|---|
| bad | Conqueror | bad: takes land | **take** the deepest border hex it can reach that is not a seat |
| bad | Raider | bad: robs its neighbours | **raid** the richest neighbour (the tower counts when it is richest) |
| bad | Slaver | bad: takes people for soldiers | **press** the weakest neighbour (never one at Force 1 already) |
| bad | Tyrant | bad: squeezes its own people | **squeeze**, then **fortify** its seat, then **raise** |
| good | Steward | good: keeps the peace | **fortify** its seat, then **raise**, then fortify its other hexes |
| good | Liberator | good: fights tyrants | **break** a bad neighbour with lower Force; else as a Steward |

5. **Raise** if it has the price in hand; else **fortify** its seat if unwalled; else
   **squeeze**.

A goal that can't be paid when its clock fills **waits full** ("done, waits for 300 GP")
and fires the month the treasury covers it. A goal whose target is gone (the hex already
changed hands, the neighbour already at Force 1) is dropped and a new one picked.

## 8. Rulers

As v2: a name from the people's list, a title, a label and a tag, always shown as
*label: verb*. Rulers change only when the tower **topples** them (section 11): the
dissident takes the throne with a random good tag. There is no regime HP and no random
collapse; what happens to a realm is on its goal line.

## 9. Standing, Hold, Renown and the ladder

### Standing

Each realm's attitude to the tower, one number:

| −2 enemy | −1 wary | 0 neutral | +1 friendly | +2 ally |
|---|---|---|---|---|

| Change | Cause |
|---|---|
| −1 | Morten Strikes one of its sites (**−2** for its seat) or Robs it |
| −2 | the tower takes one of its hexes |
| +1 | a won Aid for it; a won Contact; the tower gives it 200 GP or more in a month (once a month). None of these lift it past +1: **ally is the tower's goal** (section 11) |
| = +2 | the tower's *ally* goal is done for it; a ruler the tower put on the throne |
| −1 | its *break the tower* goal fires (it is at war now) |

**An ally** (+2) never picks *break the tower* or *raid the tower*, and adds **+1 mark a
month to the tower's goal** (one ally counts; two from Power, section below). **An enemy**
(−2) refuses Contact. Nothing drifts back on its own: standing moves only by deeds.

### Hold

The tower's buffer: **3 boxes**. A *break the tower* goal that fires takes one box and
half the treasury; at 0 boxes it takes a hex of the tower's instead (the warded hex never).
**Mend** a box for 200 GP (a purse action). Hold is the only thing on the tower that can be
hurt, and only by a goal the human watched fill for months.

### Renown and the ladder

**Renown** = hexes held beyond the tower hex + allies + 2 × rulers toppled. It is read off
the map, never bought. The tier is the first row Renown reaches:

| Tier | Name | Renown | The power it brings |
|---|---|---|---|
| 0 | Hermit | 0 | — |
| 1 | Lord of the hex | 2 | **Garrison** and **Walls** may be bought for the tower's hexes (purse actions). Wandering checks stop in a garrisoned tower hex |
| 2 | Warden of the marches | 5 | **Back** or **hinder** one realm's goal roll a month (+1 / −1) for 100 GP |
| 3 | A power in the land | 9 | Morten's Strike and Aid move **3 marks** instead of 2; **two allies** count on the tower's goal |
| 4 | Master of the twenty hexes | 14 | May **set an ally's next goal** from the catalogue each month. Reaching Master with **every realm an ally or toppled** ends the campaign: the world is his |

Renown can fall (a hex lost, a toppled ruler is permanent). The tier falls with it; the
report says so in one line.

**How the realms feel it:** from Warden on, bad rulers who aren't allies start weighing
*break the tower* (section 7, rule 1), and good ones *court the tower*. Rising makes
enemies and friends at once, which is what the arc wants.

### Purse actions

Not goals and not limited to one: anything the treasury covers, declared with the month's
orders.

| Action | Cost | Needs | Effect |
|---|---|---|---|
| **Garrison HEX** | 400 GP | Lord; a hex the tower holds; none there yet | a site: −1 to goal rolls aimed at that hex |
| **Walls HEX** | 600 GP | Lord; a garrison there | −1 more; a *take* against it needs 6 marks |
| **Works HEX** | 300 GP | a hex the tower holds; none there yet | income +50 GP; a site a realm's Raid can target |
| **Mend** | 200 GP | Hold below 3 | Hold +1 |
| **Give REALM GP** | the GP | — | the gold is theirs (section 7's +1; standing, section 9) |
| **Back / hinder REALM** | 100 GP | Warden | ±1 on that realm's roll this month |

## 10. Morten's month

Travel as before, one hex a day, wandering checks. Then **one mission in the hex he is in,
or none.** Strike, Rob and Aid are D&D fights built by `encounter`; Contact is a check.

| Mission | Where | The fight | On a win |
|---|---|---|---|
| **Strike SITE** | a realm's hex with a site | the site's list at its tier (section 6) | the realm's goal **−2 marks** (min 0); standing −1 (seat −2); and **+2 marks on the tower's goal** if it targets that realm or that hex |
| **Rob** | a realm's hex with works | the works' list at tier −1 | **100 × its Force GP** from its treasury (at most what it holds); standing −1; the tower's goal +0 |
| **Aid REALM** | the hex its goal is aimed at (its seat for goals with no hex) | the obstacle: against another realm, that realm's garrison list at that realm's tier; otherwise the hex's beasts at the aided realm's tier | the realm's goal **+2 marks**; standing +1; and **+2 on the tower's goal** if it is *ally REALM* |
| **Contact REALM** | any of its hexes | no fight: Persuasion (CHA) vs **DC 12 + 3 if the ruler is bad − 2 × standing** (so an enemy is DC 19, a friendly good ruler DC 10; squeeze adds 4). Standing −2 refuses | standing +1 (to at most +1); at +1 or more, a **dissident** is named (needed to topple, section 11) |
| **Delve** | the floor under the hex | as now | no domain effect |

A win means every foe dead, fled or surrendered, or the check made. Pass a mission to
`turn` only when it succeeded. **Death** ends the month: the mission fails, he loses what
he carried, he wakes at the tower; purse actions stand. The trader is at the tower.

At Power (tier 3) the 2s above are 3s.

## 11. The tower's goal

The tower keeps **one goal at a time**, declared by the human with the month's orders and
kept until done or dropped (dropping loses its marks). Its marks come from Morten's
missions and from allies, never from a die:

| Goal | Clock | Marks from | When the clock is full |
|---|---|---|---|
| **take HEX** from REALM | 2 + the holder's Force (4–7; +2 if walled) | a won Strike in HEX +2; an ally +1 a month | the hex is the tower's with its sites; standing with the loser −2; Renown +1 |
| **ally REALM** | 3 | Contact +1; Aid +2; Give 200 GP +1 (once a month) | standing +2; Renown +1 |
| **topple REALM** | 3 + its Force (4–8); **needs a dissident** named there | a Strike on its seat +2; on its garrison or works +1; Give 200 GP to the dissident +1 (once a month); an ally +1 a month | the dissident rules with a random good tag, full treasury kept, standing +2, its goal reset; Renown +2 |

So the road to the throne is a thing you can watch fill: Contact twice to find the
dissident, then Strike the seat while an ally adds a mark a month. And "conquer the world"
is literal on the map: take the hexes you want, ally the good rulers, topple the bad ones.

## 12. The world's turn

Every month, after Morten's month, the script runs:

1. **Morten's month lands:** mission results (marks on his target's goal and the tower's,
   standing changes, Rob's gold), deposit and withdraw, purse actions, Give, back/hinder.
2. **Income:** hex level × 10 GP to each holder (Tyrant × 1.5), works +50.
3. **Each realm rolls its goal,** highest Force first (ties by d6): marks, a full clock
   fires (and pays, or waits), a new goal is picked where needed.
4. **The tower's goal:** allies' marks; a full clock fires.
5. **Clean-up:** Renown and tier; goals 6 months old dropped; squeeze timers; the month
   advances.

Nothing else happens. Six rolls, at most six effects, one for the tower.

## 13. Reporting

The same four parts, in chat and on the page, by the **Report style** dials:

1. **The plan:** Morten's mission and the tower's goal and purse actions, and why.
2. **What happened:** the **tower's goal line first** ("Take B4 from the Gnomes: 4 of 6
   marks, +2 for the Strike on their garrison, +1 from the Humans"), then **one sentence
   per realm**: who (*label: verb*), the goal, the roll in two words, the marks now, and
   the effect if it fired ("The Orcs (bad: robs its neighbours) rolled a 6 on *raid the
   Gnomes*: 2 of 2, done, 400 GP taken."). Realms far from Morten and the tower that
   rolled nothing fold into one **Elsewhere** line.
3. **The tower now:** tier and Renown, Hold, gold, hexes and sites, allies and enemies,
   the goal and its clock.
4. **Next month:** `Threat:` every goal aimed at the tower or its hexes, with marks left
   and the roll's odds in words; `Chance:` clocks one Strike from empty or one Aid from
   full, realms one Contact from ally, treasuries worth a Rob; `Open:` where Morten is,
   the missions there with their tier, the purse actions with prices.

The roll log (every d6 with its modifiers) goes to `transcript.md` as now.

## 14. The script and the data

`tools/realms3.py`, copied from `realms.py` and cut down (the map generator, the hex
helpers, `build_fight`, `roll`, the renderers' skeletons stay; the asset engine, the AI's
marching and the faction HP go). It refuses a `realms.json` of version 1 or 2.

| Command | What it does |
|---|---|
| `new --seed N --campaign DIR [--level 3]` | the world: `realms.json` (version 3), `world.md`, `map.json`, the 20 floors in `gm-secrets.md` |
| `show --campaign DIR [--at HEX]` | the world; `--at`, the rumours from a hex (there is no `--gm`: nothing is hidden) |
| `encounter --campaign DIR --site ID` | the fight for a Strike or Rob on that site |
| `encounter --campaign DIR --aid REALM` | the fight for an Aid |
| `encounter --campaign DIR --contact REALM` | the Contact DC |
| `encounter --campaign DIR --hex HEX` | a wandering encounter for the hex's level |
| `turn --campaign DIR [options] [--dry-run]` | the world's turn: prints the report, saves `realms.json`, `world.md`, `map.json` |
| `sim [--seeds 1-10] [--months 24]` | passive-tower months for tuning |

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

Orders are checked before anything happens (a Strike needs Morten in the site's hex, a
purse action needs the tier and the gold, a goal its conditions); one rejected order
prints one line and saves nothing.

**`realms.json`** (version 3), flat: `month`, `hexes` (as v2, with `sites: [id]`),
`sites: {id: {owner, kind, hex, name}}`, `realms: {name: {leader, force, treasury, seat,
hexes, standing, goal: {kind, target, hex, size, marks, since, waits}, squeeze_until,
dissident}}`, `tower: {treasury, hold, renown, tier, goal, sites}`, `morten: {hex, level}`,
`events`, `log`.

**`map.json`** keeps v2's top-level keys (`version` 3, `layout`, `hexes`, `rivers`,
`factions`, `morten`, `events`, `report`) so the page's map still draws. Changes: a hex's
`assets` list holds **sites** (`{id, owner, name, type: seat|garrison|works|walls, tier}`);
a faction has `force`, `treasury`, `seat`, `hexes`, `standing`, `standingWord`, `goal:
{text, kind, target, hex, marks, size, waits}` and no `hp`, `cunning`, `wealth`, `hostile`,
`disorder`; the tower adds `tier`, `tierName`, `renown`, `hold`, `maxHold`;
`report.happened[]` carries `{who, goal, roll, marks, size, fired}` so the page can draw
each realm's clock. `events` keep `{month, actor, action, from_hex, to_hex, target,
result}`.

**The table page and `table.py`:** `proj_realm` branches on `version`; for 3, `WORDS`
explain force, standing, clock, hold, renown and tier (no cunning, wealth, regime,
piece); `kinds()` lists the four sites; the tower card shows tier, Renown, Hold, the goal's
clock; a realm row shows its goal as a clock (marks of size) and its standing word; the
orders form offers the missions in the hex, the tower's goal (take/ally/topple with the
valid targets), the purse actions with `affordable`; the `orders` move's `action` string
becomes a list of `--buy`/`--give`/`--back` strings and a `goal`. The v2 paths stay for
`realms3` and the fixture.

## 15. Constants

| Constant | Value | Source |
|---|---|---|
| Hex income | level × 10 GP; Tyrant × 1.5; works +50 | v2 |
| Force | 1–5; start S ÷ 10, min 1 | v2's start, capped |
| Tier from Force | 1–2 → 1, 3–4 → 2, 5 → 3; seat +1, works −1 | ours |
| Goal roll | d6; nat 1 −1, ≤2 nothing, 3–5 +1, 6+ +2 | Mausritter's shape (4–5 one, 6 two), shifted one step so an unmodified clock moves |
| Roll mods | ±1 Force, −1 garrison, −1 walls, +1 Give ≥ 200, ±1 back/hinder | Mausritter's resources, cut to five |
| Clocks | take 4 (6 walled) · fortify 3 · raise 3 · raid 2 · press 3 · squeeze 2 · break 4 · break the tower 4 · court 2 | ours; Blades' 4/6/8 cut in half for monthly ticks |
| Tower's clocks | take 2 + Force · ally 3 · topple 3 + Force | ours |
| Morten's marks | Strike −2 / +2 · Aid +2 · Contact +1 · Give +1; 3s at Power | Mausritter's "player involvement: 1–3 marks" |
| Prices | fortify 300 · raise 200 × new Force · garrison 400 · walls 600 · works 300 · mend 200 · back/hinder 100 | ours |
| Raid | 100 × Force GP; from the tower at most half | ours |
| Contact DC | 12 + 3 bad − 2 × standing (+4 squeezed) | ours |
| Standing | −2..+2; the table in section 9 | Blades' status, −3..+3 cut to five |
| Hold | 3; mend 200 | Blades' hold, as boxes |
| Renown | hexes + allies + 2 × toppled; tiers at 2, 5, 9, 14 | ours; Blades' tier ladder |
| Goal dropped | after 6 months | v2 |
| Start | seat + garrison + works; good +1 standing; tower Hold 3, 100 GP, Hermit | ours |

## 16. The sim and what it must show

`sim`, seeds 1–10, 24 months each, the tower taking no action. Targets, to tune the
clocks and the catalogue against:

- **Every month something fires somewhere** (about one goal a month across six realms),
  and **no realm goes a year without a change** on its line.
- **Two to four hexes change hands per world** in two years; a Conqueror grows; a Steward
  holds its seat.
- **No realm loses all its hexes** in two years, and no realm reaches Force 5 from 1.
- **The tower at rest** is targeted by a *break the tower* once or twice in two years and
  loses one Hold box about once; it never loses a hex at Hold 3.
- **Treasuries matter:** Raids move gold; fortify and raise get paid without a realm
  sitting on 2,000 GP for a year.

And a second sim with a scripted Morten (Strike the weakest neighbour's garrison every
month, then its seat): a hex taken in 3–5 months at level 3–4; Master reachable in about
three years of play.

## 17. Build steps

1. **Rules:** write `realms-v3.md` from this plan, in `realms.md`'s shape (sections
   1–12, the constants table, the sim results). `realms.md` stays v2 for `realms3`.
2. **Engine:** `tools/realms3.py`: data model, `new` (reuse the map generator and the
   floors), the goal catalogue and the picker, the roll, the tower's goal, purse actions,
   missions, `encounter`, the report, `world_md`, `map_json`, `sim`. Version 3 in
   `realms.json`; refuse 1 and 2.
3. **Sim** to the targets in section 16; record the numbers in the rules file.
4. **The table:** `table.py` (`proj_realm`, `WORDS`, `kinds`, the orders' validation and
   `awaiting.orders`, the tower line), `web/src/js/70-realm.js` (tower card, realm rows
   with clocks, sites in the hex entry, the orders form), `web/README.md`'s `game/realm`
   contract; `check_table.py` has nothing new to hide. A v3 fixture beside the v2 one.
5. **Templates:** `templates/realms-rules.md` for v3 (the engine's name, the tower's
   start, the mission list); `CLAUDE.md`'s Realms section, folder layout and New game
   defaults point at v3.
6. **Play:** `realms4`, Morten fresh at level 3, three months at the table with the
   human reading the world's turn. Tune the sentences before the numbers.
7. When `realms3` ends: rename v2's files to `realms-v2.md` and `tools/realms_v2.py`, and
   v3's to `realms.md` and `tools/realms.py`, as v1 was moved aside.

## 18. A month, as it would read

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

## 19. Open questions, with a recommendation each

- **Everything open?** Yes: goals, clocks, sites and treasuries are all visible. Hidden
  pieces were a third of v2's explaining. Rumours become the Chance lines.
- **Can the tower change its goal mid-way?** Only by dropping it and losing its marks.
  Commitment is what makes the clock a story.
- **Force-5 realms at level 3?** Their seat is a High fight and their works Moderate;
  Morten picks weaker neighbours first and grows into them. If the sim shows him stuck,
  lower the seat's +1 before touching the clocks.
- **New files or rename now?** New files (`realms-v3.md`, `tools/realms3.py`) while
  `realms3` plays on v2; rename when it ends (step 7).
- **Realms fighting each other without the tower:** kept to *take*, *raid*, *press* and
  *break* between neighbours, resolved by one roll each. There is no battle between two
  realms' dice, by design: two sentences a month about the neighbours is the right amount
  of world.

## 20. What the build decided (2026-10-26)

Built by four agents from this plan (engine, rules, the table, a reconciliation) and
reviewed by a fifth playing four months by hand. The readings taken where the plan was
silent, and the places the build moved away from it:

- **Court the tower reaches ally.** A good ruler courting twice becomes an ally on its own,
  and a running *ally REALM* goal for it fires. Deeds by the tower (Contact, Aid, Give)
  still cap at +1; the tower's *ally* goal is its own road to +2. Court needs the tower at
  Lord or higher (section 7's text), not Warden.
- **Allies never aim a goal at the tower,** a *take* of a tower hex included.
- **The tower has no Force:** no ±1 for or against it on goal rolls; for *take back* it
  counts as 0.
- **Aid's hex:** for *take* and *fortify*, the hex named; for *raid*, *press* and *break*,
  the target's seat; for the rest, the aided realm's seat. A goal aimed at the tower can't
  be aided.
- **Which Strikes mark which tower goal:** *take HEX* only from a Strike in HEX; *topple*
  from its seat (+2) and its garrison or works (+1); *ally* from none. Rob marks nothing
  and its gold goes to the tower's treasury at the world's turn. Give while the tower's
  goal is *topple REALM* goes to the dissident (+1 on the clock, no roll bonus).
- **`--goal` with a different goal replaces the current one and loses its marks;** the
  same goal keeps it.
- **Break the tower at Hold 0** takes a hex of the tower's and still half its treasury.
- **Goals time out after 12 months, not 6:** a *take* at −1 or −2 needs 8–12 months, and
  at 6 realms dropped and re-picked the same goal at 0 marks. The Conqueror prefers an
  unguarded border hex. A Liberator's *break* needs a target at Force 2 or more.
- **Three rules the sim asked for.** *Menace:* a bad neighbour of the tower at standing 0
  weighs *break the tower* on a d6 of 6 when it picks a goal, at any tier (a passive tower
  was never threatened: standing never drops by itself). *Rest:* a realm whose *break the
  tower* fired doesn't weigh it again for 12 months (without it the −1 after a fire chained
  the wars). *Rich:* a realm with 1,000 GP or more whose tag's goal has no price picks
  *raise* first (at Force 5, *fortify*), alternating with its tag's goal.
- **The Master's power** is a `turn` option, `--set REALM=GOAL`, one per ally a month; it
  replaces the ally's goal at 0 marks.
- **A landless realm** keeps its ruler and treasury, gets a seat back with its first hex,
  and picks *take back* before anything.
- **The world's dice don't depend on the orders:** the realms' d6s come from a stream
  seeded by the seed and the month, so the same month rolls the same whatever Morten did.
- **Sim against section 16** (passive, seeds 1–10, 24 months): about 1.4 goals fire a
  month, no realm line a year unchanged, Stewards hold 12 of 12 seats, no realm landless,
  none to Force 5; the tower at rest sees *break the tower* picked 2.3 and fired 1.6 times
  a world and loses 1.5 Hold boxes, never a hex. Missed: hexes change hands 1.6 a world
  (0 in a world with no Conqueror; 4–5 with one), and every world still has a realm
  sitting on 2,000 GP for a year, since nothing drains a treasury but goals with a price
  (the next lever, if wanted, is an army's pay: Force × 50 GP a month). Scripted (Strike
  the weakest neighbour's garrison, then its seat): the first hex in month 3; by three
  years 2 worlds in 10 reach Master and 8 Power, by conquest alone.
