# Realms: the overworld plan

**Implemented as Realms v1.** The rules live in `realms-v1.md` and `tools/realms_v1.py`
(renamed when v2 took `realms.md` and `tools/realms.py`); this plan is kept as the design
record.

An overworld for D&D Crunch: a small hex map of six realms, played as monthly domain turns
on top of the existing dungeon game. It keeps the same feel: minimal narration, open
numbers, every roll in the log. Morten is a wizard-lord in his tower. He can dispense
justice like a vigilante (rob the vicious, strike their leaders, fund the rebels who will
overthrow them) or simply conquer.

This is version one: as barebones as possible. Every number below is a first guess, kept
in one constants block in the script and one table here, to be tuned by a test run (see
Build steps).

Inspiration: domain play, faction turns in *Worlds Without Number*, *Reign*'s companies.
Nothing is copied from those books; the rules are written fresh.

## 1. The map

- **4 columns × 5 rows = 20 hexes**, named like the dungeon grid: columns A–D west → east,
  rows 1–5 north → south. A1 is the north-west hex.
- **Layout:** flat-topped hexes in columns, with columns B and D shifted half a hex south.
  Neighbours of a hex: the hexes above and below it in its column, plus two in each
  neighbouring column. In columns A and C those are rows r−1 and r; in B and D, rows r and
  r+1. Every hex's neighbour list is written out in `world.md`, because maps can't be drawn
  on the phone.
- **Hex size:** not fixed yet. For now, entering a hex takes **1 day**. The km scale comes
  later, once we know what a hex holds.

### Hex level

- The levels **1 to 20 are each used once**, shuffled over the hexes.
- **Ley depth** is the in-world reason. The mini-world sits on a web of ley lines, and a
  hex's level is how deep its ley runs. Deep ley breeds strong monsters and makes the land
  rich, so a level 2 hex is not worth much to a strong realm, and greedy realms fight over
  the deep ones.
- One number does three jobs:
  - **Income:** the hex pays its holder **level × 10 GP a month**.
  - **Wandering monsters:** encounters in the hex are built for a character of that level.
  - **Dungeon:** the hex holds **floor N** of the 20-floor dungeon, where N is its level.
- Hex levels never change.

### Biomes

One ordinary biome per hex, colder in the north and warmer in the south. The generator
rolls from its row's list:

| Row | Biomes |
|---|---|
| 1 | tundra, taiga, mountains |
| 2 | taiga, hills, mountains, forest |
| 3 | forest, plains, hills, swamp |
| 4 | plains, forest, swamp, hills, savanna |
| 5 | desert, savanna, jungle, mountains |

Biomes are flavour in version one: they don't affect monsters or rolls.

### Water

- **Rivers run along hex edges, never through a hex,** so no hex loses its dry land.
  - The generator makes **2 rivers**. Each is a path of 3–6 edge segments along the hex
    boundaries, starting at a lake or the map's edge and ending at the map's edge.
  - In `world.md`, rivers are listed as pairs of hexes that share a river edge
    (e.g. B2|B3).
  - **Rule:** when an attack crosses a river edge, the defender gets **+1**.
- **Lakes sit inside a hex** and cover at most half of it.
  - The generator places **2 lakes**, at most one per hex.
  - A lake is flavour in version one (and the start of a river).

### Monsters

Random, as in the dungeon: one random SRD monster type in a number (1–4) that fits a Low,
Moderate or High budget for the hex's level. Biome doesn't filter them.

## 2. Peoples and realms

- There are **6 realms**, each with its own **people**:
  - **Humans**, **Elves**, **Orcs**, **Gnomes** and **Tieflings**.
  - **Goblinkind:** goblins, hobgoblins, bugbears, kobolds and gnolls, counted as one
    people.
- **Every hex has a people.** At the start, it's the people of the realm that holds it.
  - Conquest changes who holds a hex, never its people. The people stay where they are.
- **Claim:** a realm gets **+1** when it attacks a hex of its own people.
  - That's the whole effect in version one. Foreign hexes pay full income.
- **Morten's tower** is on the **level 1 hex**. Its people are the **tower folk**: mixed,
  and claimed by nobody.
- **Territory:**
  - The other 19 hexes go to the realms: **3 contiguous hexes each**.
  - The 1 hex left over goes to the **adjacent realm with the lowest total hex level**, so
    one realm holds 4.
- **Races differ only in people and names** in version one. There are no racial bonuses.

## 3. Factions and leaders

Every realm holds **two factions**:

- **The ruler:** holds the realm's hexes, army and treasury.
- **The mirror:** the rival in the same niche, who wants to take over. It has no hexes and
  no army, only Cunning and a small purse.

Each faction has a named **leader**, and the **tag belongs to the leader**. When a coup
swaps them, the tags swap with them.

### Stats

| Stat | Ruler | Mirror |
|---|---|---|
| **Force** | the army: battles, attack and defence | none |
| **Cunning** | defends against coups; sets the order of action | attempts coups |
| **Treasury** | GP: income in, upkeep and purchases out | GP: its skim, plus anything Morten gives it |

### Leader tags

Variety is in the vices. The good side has only two tags, and they give no mechanical
advantage, only different behaviour.

**Vicious:**

| Tag | What it does |
|---|---|
| **Greedy** | Conquers: attacks the deepest hex it can reach. |
| **Rapacious** | Raids: takes gold from the richest neighbour it can. |
| **Brutal** | Enslaves: takes people as soldiers from the weakest neighbour. |
| **Cruel** | Exploits its own people: **+50% income**, but its mirror gets **+2 on coups**. It stays home and builds. |

**Good:**

| Tag | What it does |
|---|---|
| **Neutral** | Builds and defends. Attacks only to retake hexes of its own people. |
| **Altruistic** | Conquers only from vicious rulers it outmatches. Never raids or enslaves. |

- **At the start, 4 of the 6 rulers are vicious and 2 are good.** Each tag is rolled.
- **A vicious ruler's mirror is good, and a good ruler's mirror is vicious.** So good
  realms are in danger from their own mirror, not just from their neighbours.

### Starting stats

- Let S be the sum of a realm's hex levels.
- **Ruler:** Force = Cunning = S ÷ 10, rounded, minimum 1. Treasury = S × 10 GP.
- **Mirror:** Cunning = ruler's Cunning − 2, minimum 1. Treasury 0.
- **Morten's tower:** Force 1, Treasury 0, 1 officer (section 6).
  - The tower has no Cunning and no mirror.

## 4. The month

Time runs in months, 30 days each. A month has two parts.

### Part 1: Morten's month

**1. Travel.**
- Entering a hex takes 1 day.
- Each day outside the tower hex, roll `1d6`. On a 1, a wandering encounter for that hex's
  level arrives, fought with the normal crunch rules.
- Morten's position carries over from month to month. Going home is travel too.

**2. One mission, in the hex he is in. Or none.**

- **Strike:**
  - Pick the ruler or the mirror of the realm that holds the hex.
  - The fight is an encounter built for the hex's level: random monsters, standing in for
    the target's guards.
  - **Success:** **+3** to every roll made against that faction this month: battles, a
    coup by it, or a coup against it.
  - Striking a good ruler puts the tower **at war** with that realm (section 7).
- **Rob:**
  - Only against a **vicious ruler**, in one of its hexes. It uses the same kind of
    encounter.
  - **Success:** take **hex level × 50 GP** from that ruler's treasury, at most what it
    has.
- **Delve:**
  - Run the hex's dungeon floor with the normal crunch rules.
  - A floor's rooms stay cleared, and its gold pays out once.

**3. The month ends after the mission.**
- Gold Morten is carrying goes to the tower's treasury (his familiar flies it home), or he
  keeps it on him.

**4. Death ends Morten's month.**
- The mission fails, and he loses the coins and gems he was carrying.
- He revives at the tower with the usual respawn effects (full HP, all spells back,
  conditions cleared).
- The domain turn goes ahead without him.

**The trader is at the tower,** with the same stock and prices as the dungeon camps.

### Part 2: the domain turn

Run by the script, in this order:

1. **Income.**
   - Each ruler gets the sum of its hexes' levels × 10 GP (Cruel: × 1.5).
   - Its mirror skims **10%** of that.
   - The tower gets its own hexes' income.
2. **Upkeep.**
   - Rulers and the tower pay **Force × 10 GP**, plus **10 GP per officer** for the tower.
   - A faction that can't pay loses 1 Force, and its treasury goes to 0.
3. **The tower acts** (Morten's choices, declared at the start of the month):
   - Free actions: **Fund** (any amount of GP to any faction, ruler or mirror) and
     **Recruit** (section 6).
   - Then one action: **Conquer** or **Build**.
4. **Rulers act** in order of Cunning, highest first; ties are broken by a d10 roll.
   - Each ruler takes one action, chosen by the rules in section 5.
5. **Mirrors act:** each one either attempts a coup or builds (section 5).
6. **Clean up.**
   - A realm with no hexes left is gone: both its factions disappear, and its people
     stay.
   - Rumours update (section 8).

### Actions

| Action | Who | How it works |
|---|---|---|
| **Conquer** | rulers, tower | Battle for a hex next to one of your own. Win: you take the hex. |
| **Raid** | rulers | Battle against a neighbour's hex. Win: take **its level × 30 GP** from that ruler, at most what it has. |
| **Enslave** | rulers | Battle against a neighbour's hex. Win: **+1 Force** to you, and the loser loses 1 more. |
| **Build** | everyone | Raise Force (mirrors: Cunning) by 1. Costs **the new value × 100 GP**. Rulers can raise Cunning too. |
| **Fund** | tower | Give GP to any faction. Free action. |
| **Coup** | mirrors | Section 5. |

The tower can only Conquer, Build, Fund and Recruit. Morten can't be vicious except by
conquering.

**The tower hex is warded:** it can be raided or enslaved, but it can't be conquered.

### Battle (mass combat, version one)

- **Roll:** each side rolls d10 + Force + modifiers. **The higher total wins; on a tie the
  defender wins.**
- **The loser loses 1 Force** (Enslave takes 1 more).
- **The attacker names an origin:** one of its hexes next to the target. If that edge has a
  river, the defender gets +1. The script picks a river-free origin when one exists.
- **Modifiers:**

| Modifier | Size |
|---|---|
| River edge (defender) | +1 |
| Claim: the target is the attacker's people (attacker) | +1 |
| Morten's Strike against the other side | +3 |
| Court officers (tower only) | section 6 |

- **Force 0:** a ruler with Force 0 can't attack, and defends at d10 + 0.

## 5. How rival factions decide

The script follows these rules, so no GM judgement is needed. Ties between targets are
broken by a die roll.

"Can beat" means: own Force ≥ the defender's Force − 1.

### A ruler's action, in priority order

1. **Guard the throne.**
   - If the mirror's Cunning (+2 if the ruler is Cruel) is at least the ruler's Cunning,
     and the ruler can afford it, it builds Cunning.
2. **Act on its tag:**
   - **Greedy:** conquers the deepest hex it can beat, next to its own. Targets can be
     another realm's hexes or the tower's conquered hexes.
   - **Rapacious:** raids the neighbour it can beat with the largest treasury.
   - **Brutal:** enslaves the neighbour it can beat with the lowest Force.
   - **Cruel:** builds Force.
   - **Neutral:** conquers a hex of its own people if it can beat the holder.
     - It never attacks the tower unless they're at war.
   - **Altruistic:** conquers the deepest hex of a vicious ruler whose Force is strictly
     lower than its own.
     - It also attacks the tower's hexes if they're at war.
3. **Otherwise it builds Force** if it can afford it, or saves.

### A mirror's action

- **Coup**, if its Cunning plus bonuses is at least the ruler's Cunning.
  - Bonuses: +2 against a Cruel ruler, +3 if Morten struck the ruler this month, and court
    officers the tower assigned to it.
  - The roll: d10 + mirror's Cunning + bonuses vs d10 + ruler's Cunning. The mirror must
    roll **higher**.
  - **Win:** the leaders swap. The mirror's leader rules, with its tag, the realm's Force
    and its Treasury. The old ruler becomes the mirror, with its Cunning **halved**
    (rounded down) and an empty purse.
  - **Loss:** the mirror loses 1 Cunning (minimum 0).
- **Otherwise it builds Cunning** if it can afford it, or saves.

## 6. Morten's court

The court is a straight-up resource: named officers who run the domain while Morten is out
in the field. There are no posts to fill.

- **The start:** 1 officer, a human, with a name.
- **Recruit** (a free action in the domain turn):
  - Pay **100 GP × the new court size** to an **ally** (section 7), at most one recruit
    per ally per month. The 2nd officer costs 200 GP, the 5th 500.
  - The officer is of the ally's people and gets a generated name.
- **The court bonus** is a pool of points, refreshed every month:
  - **1 point per officer for the first 4, then 2 points for each officer after that.**
    So 4 officers give 4 points, and 6 give 8.
  - Points can be split over any of the tower's rolls that month, battles in attack or
    defence, or put behind a coup by a mirror the tower funded this month.
  - Points are assigned before the roll.
- **Losses:** each roll the court backs and loses kills one random officer on a `1d6`
  roll of 1.
- **Upkeep:** 10 GP per officer per month.
- **In replies:** a **Court** line lists the officers by name and people, and shows the
  pool.

## 7. War and allies

- **At war:** the tower is at war with a realm when its current ruler was attacked or
  struck by the tower, or attacked the tower.
  - It ends when that realm's ruler changes (a coup).
- **Allies:** realms with a **good ruler** that are **not at war** with the tower. Only
  allies supply recruits.
- Realms have no wars or alliances with each other in version one. Their behaviour comes
  from their tags alone.

## 8. Open information and rumours

- **Everything is open:** the map, every hex's level, people and holder, every faction's
  stats, leader and tag, and the court.
- **What stays hidden:** dungeon rooms Morten hasn't explored and monsters that haven't
  shown up yet, as in the dungeon game.
- **Rumours:**
  - When Morten is in or next to a realm's hex, the reply shows a **rumour line** for its
    ruler and its mirror. It doesn't matter whether he has been to a tavern.
  - A rumour is the tag in plain words plus last month's real events, for example:
    "Rumour (Orcs): Warlord Grukk took C3 from the Elves last month (Greedy). His rival
    Shaya (Altruistic) gathers support, Cunning 2 vs his 4."
  - The script writes each one from a short template per tag.

## 9. Files

**`dnd-crunch/realms.md`: the rules.**
- Sections 1–8 of this plan, rewritten as rules, with the constants table.
- `dnd-crunch/CLAUDE.md` gets a short section pointing to it, plus the new reply format.

**`dnd-crunch/tools/realms.py`: one script.**
- **Shared code:**
  - It imports the encounter and floor code from `gen_dungeon.py`.
  - That needs a small refactor: an `encounter(level, rng)` function, split out of
    `floor()`.
  - It prints every die it rolls in the log.
- **Subcommands:**
  - `new --seed N --campaign DIR`: generates the world and writes `realms.json` and
    `world.md`.
    - It also writes the 20 dungeon floors (floor N in the level-N hex) into
      `gm-secrets.md`.
    - It checks the constraints: levels 1–20 each used once, the tower on level 1,
      contiguous realms, rivers only on interior edges, at most 1 lake per hex.
  - `show [--at HEX]`: prints the phone-friendly world summary, and the rumours visible
    from that hex.
  - `encounter --hex HEX`: rolls a wandering or mission encounter for that hex's level.
  - `turn --campaign DIR [tower options]`: runs one domain turn.
    - It applies the tower's declared Fund, Recruit, action, officer points and Morten's
      mission result.
    - It prints the log, then updates `realms.json` and `world.md`.
    - `--dry-run` prints the log without saving.
  - `sim --seed N --months M`: runs months with a passive tower, for tuning.

**`dnd-crunch/campaigns/<name>/`:**

| File | What's in it |
|---|---|
| `realms.json` | the domain state: map, factions, court, wars, month, last events. The script owns it. |
| `world.md` | rendered from the JSON after every turn. Open; the human reads it. |
| `character.md` | Morten's sheet, copied from the demo dungeon at his current level. |
| `state.md` | Morten's live state as before, plus month, day and hex. |
| `transcript.md` | every reply, as before. |
| `gm-secrets.md` | only the unexplored dungeon floors. |

## 10. Reply formats

These are plain Markdown for the phone, with no code blocks or ASCII maps, the same as the
dungeon game.

**In the field** (travel, missions, dungeons):
- The current crunch format.
- The header adds the month, the day and the hex, e.g.
  "Month 3 · Day 4 · C2 (L9, forest, Elves)".
- A **Rumours** section appears when there are any.

**The domain turn:**
- **Month 3 · Domain turn**
- **Income:** one line per faction.
- **Log:** one line per action or roll, for example:
  - "Orcs (Grukk, Greedy): Conquer C3 (Elves, L9) from B3 → d10 7 + F5 = 12 vs d10 4 + F3
    + 1 river = 8, WIN. C3 → Orcs. Elves F3 → 2."
- **Realms:** one line each, for example:
  - "Orcs · Grukk (Greedy) F5 C4 820 GP · B2 B3 C3 · mirror Shaya (Altruistic) C2 40 GP"
- **Tower:** Force, treasury, hexes, wars.
- **Court:** officers and pool.
- **Next month:** Morten's position, then the open choices: travel, mission, tower action,
  Fund, Recruit.

**Who plays Morten:**
- In GM-plays-Morten mode, the GM stops at the start of each month to offer the choices
  for that month, since they're the real decisions.
- The human can say "you decide".
- Fights inside a mission play on as before.

## 11. Constants (first guesses)

| Constant | Value |
|---|---|
| Income | hex level × 10 GP a month |
| Cruel income | × 1.5 |
| Mirror skim | 10% of its ruler's income |
| Upkeep | Force × 10 GP; officers 10 GP each |
| Build | new value × 100 GP |
| Raid | target hex level × 30 GP |
| Rob (Morten) | hex level × 50 GP |
| Mission bonus (Strike) | +3 |
| Claim / river | +1 / +1 |
| Cruel ruler's mirror | +2 on coups |
| Failed coup | mirror Cunning −1 |
| Successful coup | the old ruler's Cunning halved |
| Recruit | 100 GP × new court size |
| Court pool | 1 per officer up to 4, then 2 per officer |
| Starting ruler | Force = Cunning = S ÷ 10 (rounded, minimum 1), Treasury S × 10 |
| Starting mirror | Cunning = ruler's − 2 (minimum 1) |
| Starting tower | Force 1, 0 GP, 1 officer |

For scale: dungeon floor N pays about (XP for level N → N+1) ÷ 10 in gold. Floor 4 pays
about 380 GP, floor 10 about 2,100. A typical realm (S ≈ 35) earns about 350 GP a month.

## 12. Build steps

1. **Rules:** write `realms.md` from this plan, and add the pointer section and reply
   format to `CLAUDE.md`.
2. **Generator:**
   - Refactor `gen_dungeon.py` to expose `encounter()`.
   - Write `realms.py new` and `show`.
   - Generate a few seeds and check the constraints and how the maps read on the phone.
3. **Turn engine:** write `realms.py turn` and `sim`.
4. **Tuning:**
   - Run `sim` for 24 months on 5 seeds with a passive tower.
   - Targets:
     - At least 4 of 6 realms still standing after 12 months.
     - Some coups, but no realm flipping every month.
     - No Force above about 12.
     - Treasuries neither stuck at 0 nor piling up forever.
   - Adjust the constants and record the final values in `realms.md`.
5. **Campaign:**
   - Create the campaign: `new` with a seed, copy Morten's sheet, write `state.md`.
   - Play month 1.

## 13. Left for later

These are kept out of version one on purpose:
- Clocks, unrest and reputation.
- Racial bonuses and biome effects.
- Alliances between realms.
- Fallen realms coming back.
- Morten in person on the battlefield (Fireball on an army).
- Ley crystals as a wizard's resource.
- The km scale of a hex.
