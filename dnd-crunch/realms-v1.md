# Realms v1: the overworld

**Version 1, kept for the `realms` campaign**, which plays on it to its end. New campaigns use
Realms v2 (`realms.md`, `tools/realms.py`). The engine is `tools/realms_v1.py`; its reports
now show each leader as *label: verb* ("bad: takes land") and the month's orders as **The
plan** before the log, but its rules and `realms.json` are unchanged.

An overworld for D&D Crunch: a small hex map of six realms, played as monthly domain turns on
top of the dungeon game. Same feel: minimal narration, open numbers, every roll in the log.
Morten is a wizard-lord in his tower. He can play the vigilante (rob the vicious, strike
their leaders, fund the rebels who will overthrow them) or simply conquer.

A campaign with a `realms.json` is played by this file, which adds to `dnd-crunch/CLAUDE.md`.
Where the two differ, this file wins. The script `dnd-crunch/tools/realms_v1.py` runs the world:
it generates the map, rolls the domain turn and keeps `realms.json`. The numbers below are
in one table (Constants) and in the script's constants block; keep the two the same.

## 1. The map

- **4 columns × 5 rows = 20 hexes**, named like the dungeon grid: columns A–D west → east,
  rows 1–5 north → south. A1 is the north-west hex.
- **Layout:** flat-topped hexes in columns; columns B and D sit half a hex south.
- **Neighbours** of a hex: the hexes above and below it in its column, plus two in each
  neighbouring column: rows r−1 and r if the hex is in column A or C, rows r and r+1 if it
  is in B or D. Off-map ones drop out. `world.md` lists every hex's neighbours, since maps
  can't be drawn on the phone.
- **Travel:** entering a hex takes **1 day**. The hex's size in km isn't fixed.

### Hex level

- The levels **1 to 20 are each used once**, shuffled over the hexes. Levels never change.
- In the world, a hex's level is how deep its **ley** runs: deep ley breeds strong monsters
  and rich land.
- The level does three jobs:
  - **Income:** the hex pays its holder **level × 10 GP a month**.
  - **Wandering monsters:** encounters in the hex are built for a character of that level.
  - **Dungeon:** the hex holds **floor N** of the 20-floor dungeon, N = its level.

### Biomes

One biome per hex, colder in the north. Flavour only: no effect on monsters or rolls.

| Row | Biomes |
|---|---|
| 1 | tundra, taiga, mountains |
| 2 | taiga, hills, mountains, forest |
| 3 | forest, plains, hills, swamp |
| 4 | plains, forest, swamp, hills, savanna |
| 5 | desert, savanna, jungle, mountains |

### Water

- **Rivers run along hex edges, never through a hex.** There are **2 rivers**, each 3–6
  edges long, starting at a lake or the map's edge and ending at the map's edge. They don't
  share an edge.
  - `world.md` lists a river as the pairs of hexes that share a river edge, e.g. B2|B3.
  - **When an attack crosses a river edge, the defender gets +1.**
- **Lakes sit inside a hex** and cover at most half of it. There are **2 lakes**, in
  different hexes. Flavour only (and a river can start at one).

### Monsters

As in the dungeon: one random SRD monster type, 1–4 of them, fitting a Low, Moderate or
High budget for the hex's level. Biome doesn't filter them. The `encounter` command rolls
them.

## 2. Peoples and realms

- There are **6 realms**, each of one **people**: **Humans**, **Elves**, **Orcs**,
  **Gnomes**, **Tieflings** and **Goblinkind** (goblins, hobgoblins, bugbears, kobolds and
  gnolls, counted as one people). A realm is named by its people (`Orcs`, `Goblinkind`).
- **Every hex has a people:** at the start, the people of the realm that holds it.
  Conquest changes who holds a hex, never its people.
- **Claim:** a realm gets **+1** when it attacks a hex of its own people. That's all; a
  foreign hex pays full income.
- **Morten's tower** is on the **level 1 hex**. Its people are the **tower folk**, claimed by
  nobody.
- **Territory:** each realm starts with **3 contiguous hexes**. The 19th non-tower hex goes
  to the **adjacent realm with the lowest total hex level** (ties: die roll), so one realm
  holds 4.
- Peoples differ only in names. No racial bonuses.

## 3. Factions and leaders

Every realm holds **two factions**:

- **The ruler:** holds the realm's hexes, army and treasury.
- **The mirror:** the rival who wants to take over. No hexes, no army: only Cunning and a
  purse.

Each faction has a named **leader**, and the **tag belongs to the leader**: when a coup swaps
them, the tags go with them.

### Stats

| Stat | Ruler | Mirror |
|---|---|---|
| **Force** | the army: battles, attack and defence | none |
| **Cunning** | defends against coups; sets the order of action | attempts coups |
| **Treasury** | GP: income in, upkeep and purchases out | GP: its skim, plus anything Morten gives it |

### Leader tags

**Vicious:**

| Tag | What it does |
|---|---|
| **Greedy** | Conquers: attacks the deepest hex it can reach. |
| **Rapacious** | Raids: takes gold from the richest neighbour it can. |
| **Brutal** | Enslaves: takes people as soldiers from the weakest neighbour. |
| **Cruel** | Exploits its own people: **+50% income**, but its mirror gets **+1 on coups**. Stays home and builds. |

**Good** (no mechanical edge, only different behaviour):

| Tag | What it does |
|---|---|
| **Neutral** | Builds and defends. Attacks only to retake hexes of its own people. |
| **Altruistic** | Conquers only from vicious rulers it outmatches. Never raids or enslaves. |

- **At the start, 4 rulers are vicious and 2 are good.** Which realms are good is random;
  each tag is rolled from its side's list.
- **A vicious ruler's mirror is good, and a good ruler's mirror is vicious** (tag rolled
  from that side).
- Every leader has a name and a title from their people's list; names are unique in the
  world.

### Starting stats

S = the sum of a realm's hex levels.

- **Ruler:** Force = Cunning = S ÷ 10, rounded, minimum 1. Treasury S × 10 GP.
- **Mirror:** Cunning = ruler's Cunning − 2, minimum 1. Treasury 0.
- **Tower:** Force 1, Treasury 100 GP, 1 officer (section 6). No Cunning, no mirror.

## 4. The month

A month is 30 days, in two parts: **Morten's month**, then the **domain turn**.

### Part 1: Morten's month

**1. Travel.**
- The month starts on **Day 1**. Entering a hex takes 1 day (Day +1).
- Each day he enters a hex other than the tower hex, roll `1d6`: on a **1**, a wandering
  encounter for that hex's level, fought with the normal crunch rules.
- Rest, rations and time follow the normal rules.
- His position carries over to the next month. Going home is travel too.

**2. One mission, in the hex he is in. Or none.**

- **Strike:** pick the **ruler or the mirror** of the realm that holds the hex.
  - The fight is an `encounter` for the hex's level: random monsters standing in for the
    target's guards.
  - **Success:** **+3** to every roll made against that faction this month (section 4,
    Strike bonus).
  - Striking a **ruler** puts the tower **at war** with that realm. Striking a mirror
    doesn't.
- **Rob:** only against a **vicious ruler**, in one of its hexes. The same kind of
  encounter.
  - **Success:** take **hex level × 50 GP** from that ruler's treasury, at most what it has.
    It goes to the tower's treasury (the familiar flies it home), or Morten keeps it on him.
  - Rob doesn't cause war.
- **Delve:** run the hex's dungeon floor with the normal crunch rules. A floor's rooms stay
  cleared, and its gold pays out once.
- **Success** in a Strike or Rob means Morten wins the fight: every foe dead, fled or
  surrendered. If he flees or dies, it fails.
- The tower hex and tower-held hexes have no ruler to Strike or Rob; Morten can Delve
  anywhere.

**3. The month ends after the mission** (or when he decides to take none).
- Gold he carries can go to the tower treasury (**deposit**), and he can take gold out of
  it (**withdraw**, at most what it holds). The familiar carries it either way.

**4. Death ends Morten's month.**
- The mission fails, and he loses the coins and gems he was carrying.
- He revives **at the tower** (not a dungeon camp), with the usual respawn effects: full HP,
  all spells back, conditions and Exhaustion cleared.
- The domain turn goes ahead with the tower's declared orders.

**The trader is at the tower,** with the same stock and prices as the dungeon camps. Morten
must be in the tower hex to trade.

### Part 2: the domain turn

The script runs it, in this order:

0. **Morten's month lands:** a successful Strike sets its +3; a successful Rob moves the
   gold; deposit and withdraw happen.
1. **Income.**
   - Each ruler gets its hexes' levels × 10 GP (Cruel: × 1.5, rounded down).
   - Its mirror skims **20%** of that (rounded down), taken out of the ruler's share.
   - The tower gets its own hexes' income (the tower hex pays 10 GP).
2. **Upkeep.**
   - Rulers and the tower pay **Force² × 7 GP** (Force 4: 112 GP, Force 10: 700 GP); the
     tower also pays **5 GP per officer**. Mirrors pay nothing. The starting tower pays 12
     GP a month against its 10 GP of income.
   - A faction that can't pay **disbands Force**, 1 at a time, until it can, then pays. (The
     tower at Force 0 still short for its officers pays what it has.)
3. **The tower acts,** on orders declared at the start of the month, in this order:
   - **Fund:** any GP from the tower treasury to any ruler or mirror.
   - **Recruit** (section 6).
   - Then one action: **Conquer** or **Build**.
   - An order the script can't carry out is **rejected**: one the treasury can't cover at
     that point (Withdraw, Fund, Recruit, Build) or an illegal one (Conquer at Force 0, a hex
     not next to the tower's). The script prints a one-line error, exits and saves nothing;
     the GM fixes the order and reruns `turn`.
4. **Rulers act** in order of Cunning, highest first; ties by d10, rerolling ties. Each takes
   one action by section 5.
5. **Mirrors act,** in the same order as their rulers: a coup or a build (section 5).
6. **Clean up.**
   - A realm with no hexes is gone: both factions disappear and its wars end. Its people
     stay.
   - Rumours update (section 8). The month number goes up by 1.

### Actions

| Action | Who | How it works |
|---|---|---|
| **Conquer** | rulers, tower | Battle for a hex next to one of yours. Win: you take the hex. |
| **Raid** | rulers | Battle a neighbour over its hex next to yours (the deepest such hex). Win: take **that hex's level × 30 GP** from the neighbour, at most what it has. |
| **Enslave** | rulers | Battle a neighbour over its hex next to yours (die roll among them). Win: **+1 Force** to you, **−2 Force** to the loser. |
| **Build** | everyone | +1 Force (rulers, tower) or +1 Cunning (rulers, mirrors). Costs **the new value × 100 GP**. The tower builds Force only. |
| **Fund** | tower | Give GP to any ruler or mirror. Free. |
| **Recruit** | tower | Section 6. Free. |
| **Coup** | mirrors | Section 5. |

- A **neighbour** of a ruler is any other realm, or the tower, holding a hex next to one of
  the ruler's hexes.
- The tower can only Conquer, Build, Fund and Recruit. It has **no claim** anywhere.
- **The tower hex is warded:** it can be raided or enslaved, never conquered. A raid on the
  tower takes from the tower treasury; an enslave takes tower Force.
- A conquered hex keeps its people.

### Battle

- **Roll:** each side rolls **d10 + Force + modifiers**. Higher total wins; **a tie goes to
  the defender**.
- **The loser loses 1 Force** (minimum 0). An Enslave the attacker wins takes 1 more.
- **Origin:** the attacker attacks from one of its hexes next to the target. If that edge
  is a river, the defender gets +1. The script picks a river-free origin when one exists
  (die roll among equals).
- **Force 0:** a ruler or tower with Force 0 can't attack, and defends at d10 + 0.

| Modifier | Size |
|---|---|
| River edge (defender) | +1 |
| Claim: the target hex is the attacker's people (attacker) | +1 |
| Strike: Morten struck the other side this month | +3 |
| Court points (tower only) | section 6 |

**Strike bonus.** A struck faction has +3 against it on every roll this month:
- **Struck ruler:** whoever battles it (attacking or defending) gets +3, and its mirror gets
  +3 on a coup.
- **Struck mirror:** its ruler gets +3 on the defence roll against its coup.

## 5. How rival factions decide

The script follows these rules; no GM judgement is needed. Ties between targets are broken by
a die roll.

**"Can beat"** compares Force only: own Force ≥ the defender's Force.

### A ruler's action, in priority order

1. **Guard the throne.** If the mirror's Cunning (+1 if the ruler is Cruel) is at least the
   ruler's Cunning, and the ruler can afford it, it builds Cunning.
2. **Arm.** If it can afford the next point of Force, it builds Force.
3. **Act on its tag:**
   - **Greedy:** conquers the deepest hex it can beat, next to its own. Targets can be any
     realm's hexes or tower-held hexes (never the tower hex).
   - **Rapacious:** raids the neighbour it can beat with the largest treasury, skipping
     neighbours with 0 GP. The tower can be that neighbour.
   - **Brutal:** enslaves the neighbour it can beat with the lowest Force, skipping
     neighbours at Force 0. The tower can be that neighbour.
   - **Cruel:** no tag action (it stays home; step 2 already builds its Force).
   - **Neutral:** conquers the deepest hex of its own people whose holder it can beat. It
     attacks the tower only when at war with it.
   - **Altruistic:** conquers the deepest hex of a vicious ruler whose Force is strictly
     lower than its own. When at war with the tower, the tower's hexes are targets too, also
     only if the tower's Force is strictly lower.
4. **Otherwise it saves.**

A ruler that can't afford what a rule calls for, or has no target, falls through to the next
rule. A ruler at Force 0 can't attack.

### A mirror's action

- **Coup**, if its Cunning + bonuses is at least the ruler's Cunning.
  - **Bonuses:** +1 against a Cruel ruler, +3 if Morten struck the ruler this month, and
    court points the tower put behind it (section 6). Court points count in this test, so
    backing can make an attempt happen.
  - **Roll:** d10 + mirror's Cunning + bonuses vs d10 + ruler's Cunning (+3 if Morten struck
    the mirror). The mirror must roll **higher**.
  - **Win:** the leaders swap. The mirror's leader rules, with its tag and its Cunning, and
    takes the realm's Force and treasury; its own purse goes into that treasury. The old
    ruler becomes the mirror, with its Cunning **halved** (rounded down) and Treasury 0. The
    tower's war with that realm ends.
  - **Loss:** the mirror loses 1 Cunning (minimum 0).
- **Otherwise it builds Cunning** if it can afford it, or saves. A mirror at Cunning 0 can
  still build.

## 6. Morten's court

Named officers who run the domain while Morten is in the field.

- **The start:** 1 officer, a human, with a name.
- **Recruit** (free, in the domain turn):
  - Pay **100 GP × the new court size** (the 2nd officer costs 200 GP, the 5th 500) to an
    **ally** (section 7), into its ruler's treasury. At most one recruit per realm a month.
  - The officer is of that realm's people and gets a generated name.
- **The court pool:** points refreshed every month, **1 per officer for the first 4, then 2
  per officer after that** (4 officers: 4 points; 6 officers: 8).
- **Spending points,** declared at the start of the month, total at most the pool:
  - **conquer:** added to the tower's Conquer roll.
  - **defend:** added to the first battle the tower defends this month. Unused points are
    lost.
  - **coup:REALM:** added to that realm's mirror's coup, only if the tower funded that
    mirror this month and the mirror attempts a coup.
- **Losses:** each roll the court backs and loses: `1d6`, on a 1 a random officer dies
  (logged).
- **Upkeep:** 5 GP per officer per month.
- **In replies:** a **Court** line lists the officers by name and people, and shows the pool.

## 7. War and allies

- **At war:** the tower is at war with a realm when that realm's current ruler fought a
  battle against a tower hex, or the tower attacked it (Conquer, win or lose) or struck its
  ruler.
  - War ends when a coup changes the realm's ruler, or when the realm is gone.
- **Allies:** realms with a **good ruler** not at war with the tower. Only allies supply
  recruits.
- Realms have no wars or alliances with each other; their behaviour comes from their tags.

## 8. Open information and rumours

- **Everything is open:** the map, every hex's level, people and holder, every faction's
  stats, leader and tag, the wars and the court. It's all in `world.md`.
- **Hidden:** dungeon rooms Morten hasn't explored and monsters that haven't shown up, as in
  the dungeon game.
- **Rumours:** when Morten is in or next to a realm's hex, the field reply shows a rumour
  line for its ruler and its mirror. The tag in plain words, plus last month's real events:
  - "Rumour (Orcs): Warlord Grukk took C3 from the Elves last month (Greedy). His rival
    Shaya (Altruistic) gathers support, Cunning 2 vs his 4."
  - The script writes them: `show --at HEX`.

## 9. Running a month

The script is `python3 dnd-crunch/tools/realms_v1.py`; DIR is the campaign folder,
`dnd-crunch/campaigns/<name>`.

| Command | What it does |
|---|---|
| `new --seed N --campaign DIR` | Generates the world: writes `realms.json`, `world.md`, and the 20 floors into `gm-secrets.md`. |
| `show --campaign DIR [--at HEX]` | The world summary; with `--at`, the rumours visible from that hex. |
| `encounter --campaign DIR --hex HEX` | Rolls a wandering or mission encounter for the hex's level. |
| `turn --campaign DIR [tower options] [--dry-run]` | Runs the domain turn, prints the log, saves `realms.json` and `world.md`. `--dry-run` only prints. |
| `sim --seed N --months M` | Runs months with a passive tower, for tuning. |

**Tower options** for `turn`:

| Option | Meaning |
|---|---|
| `--at HEX` | Where Morten ends the month (default: where he was). `--rob HEX` moves him to HEX; `--strike` must name the realm holding his hex. |
| `--strike REALM:ruler` / `REALM:mirror` | Morten's Strike succeeded against that faction. |
| `--rob HEX` | Morten's Rob in HEX succeeded. |
| `--keep-loot` | The Rob gold stays on Morten instead of going to the tower. |
| `--deposit GP` / `--withdraw GP` | Gold to or from the tower treasury. |
| `--fund REALM:ruler=GP` / `REALM:mirror=GP` | Fund; repeatable. |
| `--recruit REALM` | Recruit from that ally; repeatable. |
| `--action conquer:HEX` / `--action build` | The tower's one action. |
| `--court conquer=N,defend=N,coup:REALM=N` | Court points. |

Pass `--strike` and `--rob` only for a mission that succeeded.

### Steps

1. **Start of the month: choices.** The GM stops and offers that month's choices: travel,
   mission, tower action, Fund, Recruit, court points. The human decides, or says "you
   decide" and the GM chooses as Morten (shown as **Morten (GM):** lines with one line of
   reasoning). In AI player mode, the player agent chooses. Tower orders are fixed from
   here.
2. **Travel,** one hex per day. Each day outside the tower hex: `python3
   dnd-crunch/tools/roll.py 1d6`; on a 1, `encounter --hex HEX` and fight it with the
   normal crunch rules. Run `show --at HEX` when he arrives and put its rumours in the
   reply.
3. **The mission.** Strike or Rob: `encounter --hex HEX`, then the fight as usual. Delve:
   the hex's floor from `gm-secrets.md`. The fights play on as before (CLAUDE.md: Who plays
   Morten).
4. **The domain turn.** Run `turn` with the month's tower options. A `--dry-run` first
   catches typos and rejected orders (a rejected order saves nothing). Update
   `character.md` for gold moved (Rob with `--keep-loot`, deposit, withdraw), then reply in
   the domain-turn format.
5. Update `state.md` and `transcript.md`, commit and push the campaign folder, as in
   CLAUDE.md.

### Campaign files

Each realms campaign lives in `dnd-crunch/campaigns/<name>/`:

| File | What's in it |
|---|---|
| `realms.json` | The domain state: map, factions, court, wars, month, last events, the dice seed. **The script owns it**; never edit it by hand. |
| `world.md` | Rendered from `realms.json` after every turn. Open; the human reads it. |
| `character.md` | Morten's sheet, as before. |
| `state.md` | Morten's live state as before, plus **month, day and hex**. |
| `transcript.md` | Every reply, as before. |
| `gm-secrets.md` | The dungeon floors, keyed by hex (floor N in the level-N hex). Mark rooms explored as he reaches them. |

### Reply formats

Plain Markdown for the phone, no code blocks or ASCII maps.

**In the field** (travel, missions, dungeons): the normal crunch format, plus:
- The header adds month, day and hex: "Month 3 · Day 4 · C2 (L9, forest, Elves)" (level,
  biome, holder).
- A **Rumours** section when there are any.

**The domain turn:**
- **Month 3 · Domain turn**
- **Income:** one line per faction.
- **Log:** one line per action or roll, e.g.
  - "Orcs (Grukk, Greedy): Conquer C3 (Elves, L9) from B3 → d10 7 + F5 = 12 vs d10 4 + F3
    + 1 river = 8, WIN. C3 → Orcs. Elves F3 → 2."
- **Realms:** one line each, e.g.
  - "Orcs · Grukk (Greedy) F5 C4 820 GP · B2 B3 C3 · mirror Shaya (Altruistic) C2 40 GP"
- **Tower:** Force, treasury, hexes, wars.
- **Court:** officers and pool.
- **Next month:** Morten's position, then the open choices: travel, mission, tower action,
  Fund, Recruit, court points.

## 10. Constants (current values)

The script's constants block holds the same numbers; change both together.

| Constant | Value |
|---|---|
| Income | hex level × 10 GP a month |
| Cruel income | × 1.5 (rounded down) |
| Mirror skim | 20% of its ruler's income (rounded down) |
| Upkeep | Force² × 7 GP; officers 5 GP each |
| Upkeep short | disband Force until the rest can be paid |
| Can beat | own Force ≥ the defender's Force |
| Build | new value × 100 GP |
| Raid | target hex level × 30 GP |
| Rob (Morten) | hex level × 50 GP |
| Strike bonus | +3 |
| Claim / river | +1 / +1 |
| Cruel ruler's mirror | +1 on coups |
| Failed coup | mirror Cunning −1 |
| Successful coup | the old ruler's Cunning halved |
| Recruit | 100 GP × new court size |
| Court pool | 1 per officer up to 4, then 2 per officer |
| Officer loss | 1d6, 1 on a lost backed roll |
| Starting ruler | Force = Cunning = S ÷ 10 (rounded, minimum 1), Treasury S × 10 |
| Starting mirror | Cunning = ruler's − 2 (minimum 1) |
| Starting tower | Force 1, 100 GP, 1 officer |

For scale: dungeon floor N pays about (XP for level N → N+1) ÷ 10 in gold: floor 4 about
380 GP, floor 10 about 2,100. A typical realm (S ≈ 35) earns about 350 GP a month.

## 11. Left for later

- Clocks, unrest and reputation.
- Racial bonuses and biome effects.
- Alliances between realms.
- Fallen realms coming back.
- Morten in person on the battlefield (Fireball on an army).
- Ley crystals as a wizard's resource.
- The km scale of a hex.
