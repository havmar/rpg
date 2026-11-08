# 13th Age: the Hotel

13th Age (first edition, the SRD in `13th-age/srd/`) played as **the Hotel**
(`13th-age/hotel.md`): a ten-floor megadungeon that is a hotel, searched room by room by one
character who is also a guest, every room a random 13th Age monster in pyjamas. The table
is **mechanics first, minimal narration**, with **no grid**: a fight's space is 13th Age's
own (engaged, nearby, far away). The party is **one character, Morten (he/him)**, owned by
the human, played by the GM unless the human says otherwise. This folder is self-contained.
Paths here are relative to the repo root, where the session runs.

## Folder layout

```
13th-age/
  CLAUDE.md            this file: how to run the game at this table
  hotel.md             the Hotel: premise, building, the search loop, factions, rest and death, events, loot
  srd/                 the 13th Age SRD as markdown (srd/README.md: source, licence, where things are)
  agents/player.md     instructions for the AI player, when Morten is handed to one
  tools/roll.py        dice roller (flags natural 20s and 1s, and even or odd)
  tools/gen_hotel.py   the Hotel's floors: 12 rooms a floor, random bestiary guests, budgeted for one character
  tools/loot.py        the luggage: one-use items and true magic items by tier
  campaigns/<name>/    one folder per campaign (see Campaign files)
```

## Rules source

The rules are the 13th Age SRD in `13th-age/srd/` (see its README). Find a file by name,
then `grep -n`; never read a big file whole (class files run to 2,500 lines).

| Need | File |
|---|---|
| The fight's order, initiative, the escalation die | `srd/Combat-Rules/Combat-Sequence/` |
| Actions (standard, move, quick, free, interrupts) | `srd/Combat-Rules/Combat-Actions/Actions/` |
| Engaged, nearby, far away; disengaging, intercepting | `srd/Combat-Rules/Combat-Actions/Position/`, `Movement-and-Melee/` |
| Attacks, miss damage, crits, fumbles | `srd/Combat-Rules/Attacks/` |
| Conditions (dazed, hampered, stuck, vulnerable, ...), saves, ongoing damage | `srd/Combat-Rules/Special-Attacks-and-Effects/` |
| Recoveries, staggered, unconscious | `srd/Combat-Rules/Damage-and-Healing/` |
| Death saves | `srd/Combat-Rules/Death-and-Dying/Death-and-Dying.md` |
| Quick rests, full heal-ups | `srd/Combat-Rules/Rest-and-Recharge/` |
| Rally, flee, flying | `srd/Combat-Rules/Special-Actions/` |
| Morten's class: features, talents, powers or spells, feats | `srd/Classes/<Class>.md` (grep its headings) |
| Races, feats, backgrounds and skill checks, icon relationships | `srd/Races/`, `srd/Character-Rules/` |
| Skill check DCs by tier | `srd/Running-the-Game/Running-the-Game.md` (Environment DCs) |
| Building a battle (monster equivalents) | `srd/Running-the-Game/Building-Battles.md` |
| Levelling up, incremental advances, gold per heal-up | `srd/Running-the-Game/Leveling-Up.md` |
| A monster | `srd/Bestiary/<Type>/.../<Name>.md`; mooks, large and huge in `srd/Monsters/Monster-Rules/` |
| Magic items, chakras, quirks, potions, oils, runes | `srd/Magic-Items/` |
| Gear prices | `srd/Character-Rules/Gear/Equipment-Price-Guide.md` |

## The table: what "mechanics first" means here

- **Rules as written.** Play 13th Age as the SRD has it: the action economy (a standard, a
  move and a quick action a turn), miss damage, natural-even and natural-odd triggers,
  recharge rolls after a battle, the escalation die, mooks as a mob, disengage checks,
  opportunity attacks, rally, recoveries, death saves. When a ruling matters and you're
  not sure, look it up before resolving and cite the file in a few words
  `(Disengaging.md)`. Rules accuracy beats momentum.
- **Open table.** Every roll is shown: the die, the modifiers, the total, the defence or DC
  it was against, and the result. Monster stat blocks are open: when Morten first sees a
  guest, give its name, level, role and size, AC/PD/MD, HP and its attacks (the human can
  ask for the whole block, nastier specials included if the GM uses them). Track monster
  HP exactly and show it; a mob shows its pool and how many are still standing. Hidden is
  only what Morten can't perceive: unopened rooms, unseen guests, a guest's abilities no
  roll or sight has revealed. The human can switch to **closed table** (monsters as
  Healthy / Staggered / Near death, stats hidden); note it in `state.md`.
- **Minimal narration.** No mood, no flavour prose. One terse line per room: the furniture
  that matters, the light, the guests and what they're doing. Speech only when it carries
  information, one line. Fight reports are plain-language summaries (**Report style**).
- **No grid, no metres in a fight.** Space is 13th Age's: a creature is **engaged** with
  someone (in melee), **nearby** (one move away) or **far away** (two moves or more), and
  some things are **behind** something (`srd/Combat-Rules/Combat-Actions/Position/`).
  Positions are said in those words plus the room's furniture: "Morten engaged with
  Goblin A at the door · Goblin B nearby, behind the wardrobe · the archer far away on the
  mezzanine". Any distance outside a fight is in metres.
- **Time is counted.** Out of a fight, in 10-minute **turns**: listening at a door is a
  turn, a search is an hour (6 turns), a quick rest is a turn. Track the day and the clock.
  In a fight, rounds, with the escalation die in every round's header.
- **Resources are the game.** HP, recoveries, daily and recharge powers (and which
  recharged), the rally, potions, oils and runes, magic item powers, gold. Show the
  relevant ones every reply.

## House rules

These replace the SRD where they differ.

### Battles and the heal-up clock

13th Age paces itself by battles: about four to a full heal-up, about three heal-ups to a
level, and "tougher battles can mean more frequent heal-ups, and vice versa"
(`Full-Heal-ups.md`). The Hotel makes that exact: a battle is **weighted by its
difficulty**, the room's monster equivalents (`Building-Battles.md`), so a Hard room brings
the heal-up and the level sooner, much like XP.

- **A battle** is a room searched (however Morten got in: talk, stealth or a fight) or a
  fight outside a room (a wanderer, housekeeping). A room fought and then searched counts
  once, when its search completes.
- **Its weight** is the room's difficulty: **Easy 0.7 · Normal 1 · Hard 1.5** battles (the
  generator's Fight column, `gm-secrets.md`). A fight outside a room weighs its guests'
  worth for one character, to one decimal: a wanderer is one guest of its room (the room's
  Worth ÷ its guests), housekeeping is 1. Say the weight whenever a battle is counted:
  "Room 104 · Hard · +1.5 → Battles 3.2/4 · Progress 7.7/12".
- **Two counters** in `state.md`, both with one decimal:
  - **Battles N/4**, since the last full heal-up. At **4 or more** Morten has earned the
    heal-up: he takes it when he sleeps 8 hours in a bed (`hotel.md` section 7), and
    anything above 4 carries over (4.5 → 0.5). Searching on past 4 is allowed; the count
    keeps rising and carries over in the same way.
  - **Progress N/12**, since the last level. It is never lost.
- **Quick rest** after each battle, as written (recoveries, recharge rolls).
- **An early full heal-up** (Battles under 4) is allowed in a bed all the same, but it is a
  **campaign loss**, and Battles resets to 0 (Progress is kept).
- **Levels.** Each time Progress passes **4** and **8** Morten takes an **incremental
  advance** (at once, from the list in `Leveling-Up.md`); at **12** he gains a **level**,
  and the rest carries over (12.4 → 0.4). A floor averages about 1 battle a room (30% Easy,
  45% Normal, 25% Hard), so its 12 rooms are about a level's worth, sooner if it runs Hard.
  Level 10 is the top; Progress stops there.

### The campaign loss

The SRD's campaign loss (fleeing, an early heal-up) is made concrete: **the Staff file an
incident report**. Staff standing −1, and an unpaid bill of 10 gp × floor at the desk.

### Fleeing

Morten can **flee** a fight as the SRD's party action: on his turn he leaves, carried by
the Hotel's corridors, and the fight is over. It is a campaign loss. The guests keep their
room, and their reaction to him is 2 from then on. Walking away without fleeing is plain
movement: disengage checks, opportunity attacks, and guests who follow.

### Death is a respawn (roguelike)

- Dying works as written: at 0 HP he is unconscious and makes death saves (16+ to come
  back with a recovery), and he dies on the **fourth failed death save** in a battle or at
  **negative half his maximum HP**.
- When he dies, housekeeping finds him, and he **wakes in his room, 100, 8 hours later** with a
  full heal-up. Battles go to 0 (Progress is kept); no campaign loss.
- He **loses all coins and gems he carried**: the bill. He keeps everything else: gear,
  magic items, bricks, levels and advances.
- The Hotel stays as he left it: dead guests stay dead, searched rooms stay searched, the
  living have 8 hours to regroup. Track deaths in `state.md` (`Deaths: N`).

## Report style

How the GM reports fights and events in chat. It is a set of dials; the human can turn any
of them ("fights as outcomes", "more detail on the dice"), and the setting goes in
`state.md` (`Report style:`). Whatever the dials say, the full roll-by-roll log goes in
`transcript.md`, so the fights can be checked.

| Dial | Default | Other settings |
|---|---|---|
| Fights | **summary** | **log**: round by round, as in **Reply format** · **outcome**: one or two lines per fight |
| Events (searches, corridors, shopping, rests, loot) | **summary** | **log**: one line per event with its rolls |
| Dice in summaries | **key rolls** (natural 20s and 1s, the triggers that mattered, the roll that decided it) | **none** · **all** |
| Live updates | **every round** | **turning points** (a crit, a kill, a big hit, a daily spent) · **off** (the report only) |

When the human plays Morten turn by turn, a fight is always shown in the **log** format.

**Voice.** A GM talking the human through the fight, relaxed, with some detail, never a
form filled in:

- **Lead with the headline** in a full sentence: "Morten cleared 104 without spending a
  single recovery; the escalation die did the work." Then the detail.
- **Say the plan and why**, in Morten's voice when the GM plays him: "Two mooks and a
  leader: he stays engaged with the mob in the hallway, where only one can reach him."
- **Explain a rule when it matters**, in a short aside: "A natural even miss still
  triggers its blade's slow, so the goblin is dazed anyway."
- **Let the drama of the dice show** in plain words: "His daily just missed, natural 3, so
  that's his best spell gone until the next heal-up."
- **Group rounds under short headings** (Round 2 · escalation die 1), a few lines each;
  fold routine rounds together.
- **End with the stakes and a question:** what he carries and could lose, the battles to
  the next heal-up, the open choices.
- **Vary it.** No fixed labels on every fight, no lines all opening with the same prefix,
  no fragments like "Hit (19). 7 dmg." instead of sentences.

**Units on every number.** HP, damage, defences and gold always carry their word: "hits
for 9 damage", "Goblin mob 18 → 9 HP (one down)", "Morten 22/30 HP", "AC 17", "45 gp".

**Live updates.** While the GM plays a fight, report as the dice fall: a line when Morten
tries something that matters and why, a sentence or two when it resolves, with both sides'
HP. When the fight ends, a short wrap-up: the headline and the result, not a replay.

**Monsters show their level.** Whenever a guest is named in a heading or a report, give
its level, role and what the room counts as: "3 Kobold Archers (level 1 mooks) · Normal,
worth 1.0".

**Fights: summary.** When fights aren't watched live, one block per fight: a heading with
the room, the guests and the fight's weight, and a verdict; then a few bullets (Plan, The
dice, How it ended, Result) only where they have something to say.

> **Room 104 · Destroying Sword (level 2 wrecker) · Hard, worth 1.5 · cleared, but it cost**
> - **Plan:** fight it in the narrow hallway so the sword can't get round him.
> - **The dice:** his daily missed on a natural 4; round 3's natural 20 on the escalation die +2 turned it.
> - **Result:** cleared on 6/30 HP, two recoveries spent at the quick rest. +1.5 → Battles 3.2/4 · Progress 7.7/12. +35 gp.

**Events: summary.** A few bullets per stop: the door and its reaction roll, the price or
the fight, the noise check, the brick, the luggage. Fold routine steps into one line.

## Reply format

This is the **log** format, a fight round by round. Every reply, in any style, is read on a
phone: **no code blocks and no ASCII maps**. Plain Markdown: bold labels, short lines,
bullets. Leave out a section only when it's empty.

> **Round 2 · Escalation die 1 · Init: Morten 18 › Goblin mob 12 › Hobgoblin 9**
>
> **Room 106:** overturned furniture (the middle is a dicey move), lit.
>
> **Positions:** Morten engaged with the Goblin mob (3 left) by the door · the Hobgoblin nearby, behind the sofa.
>
> **Log**
> - Goblin mob: Spear vs AC 17 → d20 14 +6 = 20, HIT → 5 damage.
> - Morten: Magic Missile (at-will) → automatic hit, 2d4: 3+4 = 7 force on the mob. One goblin drops (mob 21 → 14 HP).
>
> **State**
> - Morten: HP 25/30 · Recoveries 8/8 · Daily: Sleep ✗ · Rally ✓
> - Goblin mob: 14 HP, 2 left · Hobgoblin: 32/32 HP
>
> **Morten's turn:** standard · move · quick

- The LOG is one line per event, in order: who, what, the roll, the result, the effect. A
  natural even or odd that triggers something says so.
- When the human declares an action, resolve exactly that. If it's illegal (no action
  left, not engaged, a daily already spent), say why in one line and ask again.
- Out of a fight, end with the open options as mechanics: "Doors: 107 (occupied, a
  television on), 108 (quiet). Stairs at both ends."
- Don't suggest the best move or warn about bad ones; the player plays the tactics.

## The GM

- The **main session is the GM** and the human talks to it directly.
- Roll every die with `python3 13th-age/tools/roll.py`, Morten's too, and copy the results
  into the LOG. Never invent a result. The human may roll physical dice and report them.
- Guests fight by their stat blocks and act sensibly for what they are: goblins gang up,
  beasts go for the nearest target, casters stay far away, a leader hides behind its
  troops. Morale: a group that loses half its number or its leader may flee or surrender
  (GM's call; if unsure, d20, 11+ fights on).
- **The escalation die** works as written: 0 in round 1, then +1 each round to +6, Morten
  adds it to his attacks, guests don't (unless a stat block says so). If Morten is
  avoiding the fight it doesn't advance; if the fighting stops, it resets.
- **Nastier specials** are off at the Hotel's Easy and Normal rooms and on in Hard ones.
- Roll step by step whenever a result decides the next choice (a hit, a save, a recharge).
- Ask the human before big retcons. A fixable GM error is corrected in the next LOG line
  with `CORRECTION:`.

## Who plays Morten

Morten is the human's character, but the default mode is **GM plays Morten**, the fastest.
Note the mode in `state.md`.

- **GM plays Morten.** The GM decides Morten's turns as well as the Hotel's, using only
  what Morten has seen (the transcript), never `gm-secrets.md`. A careful, clever
  adventurer who keeps moving: play on until something matters (a new room, a real choice
  such as loot or a deal, a death), then stop and report. Low HP is never a stop: he
  rallies, drinks, retreats, flees if he must, and a death is a respawn. When the human sets
  a goal ("search the rest of floor 1"), new rooms aren't stops either: play to the goal
  or a death. Show his choices as **Morten (GM):** lines with one line of reasoning.
- **AI player mode.** Morten is played by a `general-purpose` subagent following
  `13th-age/agents/player.md`, so the GM's secrets never reach his decisions. Spawn it once
  with "Read `13th-age/agents/player.md` and follow it as your instructions for this whole
  conversation. Campaign: `13th-age/campaigns/<name>/`." plus the latest GM reply; keep
  its agent ID in `state.md` and continue it with SendMessage each turn. Show the human
  **Morten (AI):** and then the GM reply that resolves it.
- **The human can step in at any time**: whatever they say Morten does, he does (relay it
  to an AI player as `[HUMAN] <exact words>`). "I'll play" switches to human mode.

## The character

- One PC, **Morten** (he/him), built by the SRD's character rules: a race, a class, ability
  scores by the 28-point buy, 8 background points, 3 icon relationship points (here: with
  the Hotel's factions, `hotel.md` section 5), a **One Unique Thing**, his class's talents,
  powers or spells, and a feat. His sheet is the campaign's `character.md`.
- His **One Unique Thing** is the Hotel's premise: *he is the only guest who can hear a
  brick in a wall, and the only one who can pull it out.*
- **The class is rolled** at a new game, 1d14, alphabetically: 1 Barbarian, 2 Bard,
  3 Chaos Mage, 4 Cleric, 5 Druid, 6 Fighter, 7 Monk, 8 Necromancer, 9 Occultist,
  10 Paladin, 11 Ranger, 12 Rogue, 13 Sorcerer, 14 Wizard. The Commander is left out: its
  commands are for allies, and he has none. The GM picks the race whose bonus suits the
  class, and the talents and spells a careful solo player would.
- The sheet's header: **Morten · Level 1 Wizard (High Elf) · Battles 0/4 · Progress 0/12 · Advances 0**.

## Battles for a party of one

- Each room is budgeted by `gen_hotel.py` with the SRD's monster equivalents for **one**
  character: one standard monster (Normal), 0.7 (Easy) or 1.5 (Hard). At champion tier
  "same level" is a level above Morten, at epic two (`Building-Battles.md`).
- One PC has one turn, so action economy is the danger, and mooks are the trap: a mob of
  five gets five attacks a round. Play the furniture and the doors: a narrow hallway where
  only one can engage, a mezzanine far away, a door closed in a face.
- Not every room is a fight: most guests talk (`hotel.md` section 4). Skill checks use the
  SRD: d20 + ability + level + a background vs the tier's DC (adventurer 15 / 20 / 25,
  champion 20 / 25 / 30, epic 25 / 30 / 35 for normal / hard / ridiculous), and they
  **fall forward** on a failure.

## Campaign files

Each campaign lives in `13th-age/campaigns/<name>/`:

- `character.md`: Morten's full sheet: race, class, abilities, defences, HP, recoveries,
  backgrounds, icon relationships, One Unique Thing, talents, powers or spells (daily,
  recharge, at-will), feats, gear, magic items in their chakras (with quirks), gold,
  battles and advances.
- `state.md`: the live state, rewritten after every reply: the header line, HP,
  recoveries, expended dailies and recharge powers, rally, potions, conditions, battles,
  deaths, the Hotel lines (`hotel.md` section 9), and in a fight the initiative, the
  escalation die, positions and every guest's HP. A fresh GM must be able to resume from it
  alone. Notes the table mode, the report style and who plays Morten. No secrets: the AI
  player reads it.
- `transcript.md`: every GM reply word for word, with the action before it, in order.
  Never GM secrets.
- `rules.md`: rules for this campaign only, public: the Hotel's name, the seed, rulings
  made along the way. They win over this file and `hotel.md`.
- `gm-secrets.md`: the generator's ten floors with the GM's marks, the luggage rolled,
  the Cornerstone's secret. Only the GM reads it.

This is a cloud session and the container is wiped when it ends. **After every GM reply**,
update `state.md`, append to `transcript.md`, then commit and push the campaign folder.

## New game defaults

When the human asks for a new game, start with these without asking; the human can change
any of them.

- **Name:** the next free `hotelN`.
- **The Hotel:** roll the seed (`roll.py 1d100`), then `python3 13th-age/tools/gen_hotel.py
  --seed N` into `gm-secrets.md`, with the marks of `hotel.md` section 9.
- **Morten:** level 1. Roll the class (`roll.py 1d14`), then build him by the SRD.
  Icon points: **Staff +1, Residents +1, Ark −1** (positive, conflicted, negative: they
  start his standings). One starting one-use item: `loot.py --one-use adventurer`.
- **Who plays Morten:** the GM. **Table:** open. **Report style:** the defaults above.
- **Style:** play it smart: talk first, fight in the doorway, save the daily for the room
  that needs it, drink the potion before the death saves, spend the purse before a risky
  room (death takes the coins).
- **Start:** Day 1 · 08:00, in his room, 100, on floor 1, Battles 0/4, Progress 0/12, bill at zero.
- **Played in chat**, in Markdown.

## How to run a session

1. For a new game, the defaults above. Write `character.md`, `rules.md`, `state.md`,
   `transcript.md` and `gm-secrets.md`.
2. Open with the first reply: the premise in a few lines, the lobby, the corridor of
   floor 1, the first door. Then one reply per human message, played to the next stop.
3. A fresh GM resuming reads `state.md`, `character.md`, `rules.md`, `gm-secrets.md` and
   the end of `transcript.md`, then `hotel.md` whole, then continues.
