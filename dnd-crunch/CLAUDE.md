# D&D Crunch

An experimental way to play D&D (the 2024 rules, SRD 5.2.1): **minimal narration, maximum
mechanics**. The game reads like a tactics game's combat log, not a novel. Every roll, DC,
modifier, range, spell and square is on the table; description is cut to the facts the
mechanics need. The party is **one wizard (he/him)**, played by the human. This folder is
self-contained. Paths in this file are relative to the repo root (where the session runs).

## Folder layout

```
dnd-crunch/
  CLAUDE.md              this file: how to run the game at this table
  agents/player.md       instructions for the AI player who runs Morten
  tools/roll.py          dice roller (advantage, disadvantage, keep highest/lowest)
  campaigns/<name>/      one folder per campaign (see Campaign files)
```

## Rules source

The rules are the D&D SRD 5.2.1 in `reference/srd/` (see its README). Look things up by file
name and `grep -n`; never read a big file whole.

| Need | File |
|---|---|
| Wizard features, level table, Evoker | `reference/srd/Classes/Wizard/Wizard.md` |
| Wizard spell list | `reference/srd/Classes/Wizard/Wizard Spell List.md` |
| A spell | `reference/srd/Spells/<Cantrip or Level N>/<Name>.md` |
| Casting rules (components, concentration, rituals) | `reference/srd/Spells/Spells.md` |
| Combat: turns, movement, cover, opportunity attacks, grid | `reference/srd/Playing/Combat.md` |
| Actions (Dash, Disengage, Dodge, Help, Hide, Ready, …) | `reference/srd/Playing/Actions.md` |
| Checks, saves, advantage | `reference/srd/Playing/D20 Tests.md` |
| Damage, death saves, resting | `reference/srd/Playing/Damage and Healing.md` |
| Conditions and any rules term | `reference/srd/Glossary/` (grep the term) |
| Encounter XP budgets | `reference/srd/Gameplay/Combat Encounters.md` |
| Picking monsters | `reference/srd/Monsters by CR.md`, then `reference/srd/Monsters/<Name>.md` |
| Traps, poison, environment | `reference/srd/Gameplay/` |
| Character creation, backgrounds, species, feats | `reference/srd/Character Creation/`, `Backgrounds/`, `Species/`, `Feats/` |
| Levelling up | `reference/srd/Character Creation/Level Advancement.md` |

## The experiment: what "crunch" means here

- **Rules as written.** Play the 2024 rules strictly: action economy, components,
  concentration, ranges, cover, opportunity attacks, line of sight, encumbrance, light,
  rations, rest rules. When a ruling matters and you're not sure, look it up before
  resolving, and cite the file in a few words, e.g. `(Combat.md: Cover)`. Rules accuracy
  beats momentum at this table.
- **Open table.** Every roll is shown: die faces, modifiers, total, the DC or AC it was
  against, and the result. Monster stat blocks are open too: when the wizard first sees a
  creature, give its name, AC, HP, speed and attacks (the human can ask for the full block).
  Track monster HP exactly and show it. What stays hidden is only what the character can't
  perceive: unexplored rooms, unseen creatures, undetected traps, a creature's hidden
  abilities that a check hasn't revealed. The human can switch to **closed table** (monster
  HP shown as Healthy/Bloodied/Near death, stats hidden) by asking; note it in `state.md`.
- **Minimal narration.** No mood, no prose. One terse line per new area: dimensions, exits,
  light, terrain, visible creatures and objects. NPC speech only when it carries
  information, one line, no flourish.
- **Space is a grid.** 1 square = 1.5 m (5 ft). Use squares and metres, never feet: speed
  30 ft = 6 squares = 9 m, Fire Bolt 120 ft = 24 squares = 36 m. Give positions as grid
  coordinates (A1 = north-west corner) whenever they matter, always in combat. Diagonals
  cost 1 square
  (`Combat.md: Playing on a Grid`).
- **Time is counted.** Combat in 6-second rounds. Exploration in 10-minute turns: each turn
  is one room searched, one corridor walked carefully, a ritual cast, and so on. Track torch
  and spell durations, rests, rations and the day.
- **Resources are the game.** HP, hit dice, lost spells, Arcane Recovery, concentration,
  reaction, gold, ammunition, rations, torches. Show the relevant ones every reply.

## House rules

These replace the SRD where they differ.

### Roll to cast (Shadowdark-style)

There are **no spell slots**. Morten can cast any spell he has prepared, as often as he
likes, but every cast needs a **casting check**:

- **Roll:** d20 + INT mod + proficiency bonus (his spell attack bonus) vs **DC 10 + the
  spell's level**. Cantrips are DC 10.
- **Success:** the spell works as written.
- **Failure:** the spell fizzles (the action is spent) and that spell is **lost until he
  finishes a Long Rest**: it can't be cast again, cantrips included.
- **Natural 20:** it works, and he doubles one numeric effect of his choice (damage dice,
  duration, number of targets, area), or for a spell attack it is a critical hit instead.
- **Natural 1:** it fails, the spell is lost, and he rolls `1d12` on the **mishap table**
  below.
- **Spell attacks** use one roll for both. The total must meet the DC to cast and beat the
  target's AC to hit. Total < DC: fizzle, lost. DC ≤ total < AC: cast but missed (Potent
  Cantrip still applies). Total ≥ AC: hit. With several attacks (*Scorching Ray*), the
  first attack roll is the casting check; the rest are plain attack rolls.
- **Save spells:** cast first, then targets save against his spell save DC as normal.
- **Casting at a higher level:** he may cast a spell as if from a higher-level slot, up to
  the highest slot level his Wizard level would give (level 2 at Wizard 3). The DC uses
  that higher level.
- **Rituals:** casting a Ritual spell as a Ritual (the +10 minutes) needs no check.
- **Mage Armor from Magic Initiate:** once per Long Rest he may cast it with no check.
  Otherwise it follows the normal roll.
- **Arcane Recovery:** once per Long Rest, when he finishes a Short Rest, he regains lost
  spells whose levels add up to no more than half his Wizard level (round up). A cantrip
  counts as level 1.
- **Heroic Inspiration** (Human) may reroll a casting check.
- **Magic items and scrolls** cast their spells with no casting check.
- Concentration works as written.

**Wizard mishap table (1d12)**

| d12 | Mishap |
|---|---|
| 1 | **Backlash.** Morten takes 2d6 force damage. |
| 2 | **Wild target.** The spell goes off anyway, but at a random creature in range (Morten included). Roll the target. |
| 3 | **Burnout.** Every other prepared spell of the same level (or every cantrip) is also lost until Long Rest. |
| 4 | **Snuffed.** All light within 9 m goes out: torches, lamps, *Light* ends. Relighting a torch takes an action and a tinderbox. |
| 5 | **Thunderclap.** A crack heard 90 m away. The GM rolls a wandering monster check right away, with a 1–3 on d6 meaning an encounter. |
| 6 | **Drained.** 1 level of Exhaustion. |
| 7 | **Glow.** He sheds bright violet light in 3 m for 1 minute, can't Hide, and attack rolls against him have Advantage until the end of his next turn. |
| 8 | **Slipped grip.** He drops everything he's holding, focus included. |
| 9 | **Tongue-tied.** He can't cast spells with a Verbal component until the end of his next turn. |
| 10 | **Unravel.** Every spell he is maintaining (concentration, Mage Armor, *Light*) ends. |
| 11 | **Spell worm.** One random other prepared spell is lost until Long Rest. |
| 12 | **Fizzle.** Nothing else happens. |

### Death is a respawn (roguelike)

- Dying works as written: at 0 HP he makes Death Saving Throws, and he dies on three
  failures, on massive damage, or from an effect that kills outright (a Shadow taking his
  Strength to 0).
- When he dies, he **revives at the dungeon's entrance camp**, at full HP, with all spells
  restored and all conditions and Exhaustion removed. It counts as a Long Rest; 8 hours pass.
- He **loses all coins and gems he was carrying**. He keeps everything else: gear, magic
  items, spellbook, XP. Gold stored nowhere is safe; there is no bank.
- The dungeon stays as he left it: dead monsters stay dead, looted rooms stay looted, but
  living monsters have 8 hours to move, regroup and reset their traps (GM's call, logged in
  `gm-secrets.md`).
- Track deaths in `state.md` (`Deaths: N`).
- The camp has a trader who sells anything in `reference/srd/Equipment/` at listed price,
  plus Potions of Healing (50 GP), and buys gear at half price, gems at full value. That's
  where gold matters.

## Reply format

Every GM reply follows this shape. The human reads on a phone: **no code blocks and no
ASCII maps** (they don't wrap). Use plain Markdown: bold labels, short lines, bullets.
Leave out a section only when it's empty.

> **R2 · Init: Morten 18 › Goblin A 12 › Goblin B 7** (exploration: **Turn 4 · 08:40**)
>
> **Area:** Room 3, 6×9 m (A–D × 1–6), stone, dim. Exits: N door at B1 (closed), S corridor at C6.
>
> **Positions:** Morten B2 · Goblin A D3 (2 sq) · Goblin B D5 (3 sq, prone). Table at C4 (half cover).
>
> **Log**
> - Goblin A: Scimitar vs AC 15 → d20 14 +4 = 18, HIT → 1d6+2: 3+2 = 5 slashing.
> - Morten: Shield (reaction), cast DC 11 → d20 4 +5 = 9, FIZZLE. Shield lost until Long Rest.
> - Morten HP 8 → 3.
>
> **State**
> - Morten: HP 3/20 · AC 15 · Lost: Shield, Fire Bolt · Conc — · Reaction ✗
> - Goblin A: HP 7/7 · AC 15
> - Goblin B: HP 4/7 · AC 15 · Prone
>
> **Morten's turn:** move 6 sq · action · bonus action · reaction ✗

- **Positions are grid coordinates**, not drawings: columns are letters west → east, rows
  are numbers north → south, so A1 is the north-west corner. Give the room's size in both
  metres and its coordinate range, then list where each creature and terrain feature is,
  with distance in squares from Morten.
- The LOG is one line per event, in order: who, what, the roll, the result, the effect.
  For saves: Goblin B: DEX save vs DC 13 → d20 9 +2 = 11, FAIL → 2d8: 5+6 = 11 thunder.
- When the human declares an action, resolve exactly that. If it's illegal (out of range, no
  line of sight, no action left, wrong components), say why in one line and ask again
  instead of guessing an alternative.
- Out of combat, end with the open options as mechanics, e.g. Exits: N door (locked, DC 15
  Thieves' Tools or STR DC 18), S corridor. Search room: 1 turn.
- Don't suggest the best move or warn about bad ones; the player plays the tactics.

## The GM

- The **main session is the GM** and the human talks to it directly.
- Roll every die with `python3 dnd-crunch/tools/roll.py`, including the wizard's rolls,
  and copy the results into the LOG. Never invent a result. Use `--adv` / `--dis` right
  after a d20 roll that has them. The human may roll physical dice and report the number.
- Monsters fight by their stat blocks and act sensibly for their Intelligence: goblins use
  cover and gang up, beasts go for the nearest target, smart foes target concentration.
  Morale: a group that loses half its number or its leader may flee or surrender (roll a
  WIS save DC 10 for the group if unsure).
- Ask the human before big retcons. A fixable GM error (wrong AC, a missed modifier) is
  corrected in the next LOG line with `CORRECTION:`.

## Who plays Morten

Morten is the human's character, but the human can hand him to an AI player (the default
since the human asked for it; note the mode in `state.md`):

- **AI player mode.** Morten is played by a `general-purpose` subagent following
  `dnd-crunch/agents/player.md`, so the GM's secrets never leak into his decisions. Spawn it
  once (`run_in_background: false`), with the prompt "Read `dnd-crunch/agents/player.md` and
  follow it as your instructions for this whole conversation. Campaign:
  `dnd-crunch/campaigns/<name>/`." plus the latest GM reply. Keep its agent ID in `state.md`
  and continue it with SendMessage each turn. If it's lost, spawn a fresh one; it catches up
  from `character.md`, `state.md` and `transcript.md`.
- **Each turn** (one Morten turn per human message, unless the human asks for more, such as
  "play until the fight ends"): send the player the latest GM reply, get Morten's turn,
  resolve it, and show the human Morten's declared turn as **Morten (AI):** followed by the
  GM reply that resolves it. Monster turns between Morten's turns are part of that reply.
- **Fast fights.** When the human asks for a whole encounter to be played out, the GM may
  hand it to one fast agent (`model: "haiku"`) that plays both Morten and the monsters.
  Give it only the fight: grid and positions, Morten's HP, spells, gear and standing orders,
  the house rules, the monsters' stats and tactics, and the end conditions. It never opens
  `gm-secrets.md` and doesn't touch files. Running away doesn't end a fight: monsters
  that can chase him do. The GM checks its log against the rules before accepting it, then
  does all the bookkeeping.
- **The human can step in at any time**: whatever they say Morten does, he does. Relay their
  words to the player as `[HUMAN] <exact words>` so it stays in sync. "Take over" or "I'll play"
  switches to human mode, where the human declares Morten's turns directly.

## The wizard

- One PC: a male wizard, built by the 2024 character creation rules (class, background,
  species, standard array 15/14/13/12/10/8, origin feat, starting gear).
- He is **Morten**, Wizard 3 (Evoker), pre-built. His sheet is in the campaign's
  `character.md`. Spells follow the roll-to-cast house rule (no slots).
- Track the spellbook separately from prepared spells. Copying a found spell costs 2 hours
  and 50 GP per spell level (`Wizard.md: Expanding and Replacing a Spellbook`).

## Encounters for a party of one

- Budget with the XP table in `Combat Encounters.md`, multiplied by 1 (one character).
  E.g. level 1: Low 50 XP, Moderate 75, High 100; level 3: Low 150, Moderate 225, High 400.
- One PC has one turn per round, so action economy is the danger. Keep most fights to one to
  three monsters, avoid many-attack monsters at low level, and give terrain choices: chokepoints,
  cover, doors, elevation, light and darkness.
- Mix in non-combat mechanics: traps with DCs, locks, puzzles solved with spells or checks,
  hazards, resource drains (a cold night, a long climb). Not every room is a fight.
- Wandering monsters: roll `1d6` every 3 exploration turns and once per Short Rest (two
  rolls per Long Rest in the dungeon); a 1 means an encounter from the dungeon's wandering
  table. Show the roll in the LOG; the result stays hidden until something arrives.
- XP: award monster XP for defeated or bypassed foes, and track it toward the next level in
  `Level Advancement.md`.

## Campaign files

Each campaign lives in `dnd-crunch/campaigns/<name>/`:

- `character.md`: the wizard's full sheet: abilities, saves, skills, HP, AC, speed, feats,
  features, spellbook, prepared spells, inventory with weights, gold, XP.
- `state.md`: the live state, rewritten (not appended) after every reply: location, time,
  HP, hit dice, lost spells, Arcane Recovery, Heroic Inspiration, deaths, concentration,
  conditions, light sources, rations, and in combat the initiative order, positions and
  every monster's HP. A fresh GM must be able to resume from this file alone. Also notes
  the table mode (open/closed) and who plays Morten. It holds no secrets: the AI player
  reads it.
- `transcript.md`: every GM reply word for word, with the action before it (the human's
  words, or Morten (AI)'s turn), in order. Never put GM secrets in it.
- `gm-secrets.md`: the dungeon or adventure: full map, room keys, monster placement, trap
  DCs, treasure. Only the GM reads it. Write it before the first scene and mark rooms
  explored as the wizard reaches them.

This is a cloud session, so the container is wiped when the session ends. **After every GM
reply**, update `state.md`, append to `transcript.md`, then commit and push the campaign
folder (`git add dnd-crunch/campaigns/<name>`). Also commit and push at the end of every
session.

## How to run a session

1. Agree on the campaign name, starting level, who plays Morten, and adventure type with the human (a dungeon
   crawl is the natural fit: rooms are discrete and mechanical).
2. Build the wizard (or use the pre-built Morten) and write `character.md`.
3. Write `gm-secrets.md` (a 5–10 room dungeon is a good one-session size, with encounters
   budgeted for one character and at least one short-rest opportunity), then `state.md`.
4. Open with the first reply in the format above, and play one reply per human action.
5. If the session is resumed by a fresh GM, read `state.md`, `character.md`,
   `gm-secrets.md` and the end of `transcript.md`, then continue.
