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
  realms.md              overworld rules, Realms v2 (WWN-style factions with assets)
  realms-v1.md           Realms v1 rules, kept for the `realms` campaign
  realms-plan.md         the design record of Realms v1
  realms-v2-plan.md      the design record of Realms v2 (implemented)
  table-plan.md          the design record of the table: the game played from a page (built)
  agents/player.md       instructions for the AI player who runs Morten
  web/                   the table's page: sources, build, dist/table.html, dev harness, e2e
                         (web/README.md: the data contract, the GM's turn, publishing)
  ui/realms-map.html     the old Realms map page, for campaigns played in chat (ui/README.md)
  ui/table-mockup.html   the table's look as first sketched, a clickable mockup (ui/README.md)
  tools/roll.py          dice roller (advantage, disadvantage, keep highest/lowest; --keep DIR for the page)
  tools/gen_dungeon.py   demo-dungeon generator: random SRD monsters, one floor per level
  tools/realms.py        Realms v2 engine: world, domain turns, mission fights, sim, map.json
  tools/realms_v1.py     Realms v1 engine, for the `realms` campaign
  tools/realms_page.py   builds a campaign's map page (page.html) from its map.json
  tools/table.py         the table's GM side: the record (morten.json, story/, live/, page.json),
                         the page's store documents and their ArtifactData batches, the Markdown
                         renderers (character.md, state.md, transcript.md)
  tools/check_table.py   the table's secrecy check: no GM secret in a document for the page's store
  tools/test_table.py    tests for table.py, check_table.py and roll.py --keep
  templates/             a new game's starting sheet and campaign rules (New game defaults)
  campaigns/<name>/      one folder per campaign (see Campaign files)
  sessions/              per-session notes and full transcripts
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
  creature, give its name, CR, AC, HP, speed and attacks (the human can ask for the full
  block).
  Track monster HP exactly and show it. What stays hidden is only what the character can't
  perceive: unexplored rooms, unseen creatures, undetected traps, a creature's hidden
  abilities that a check hasn't revealed. The human can switch to **closed table** (monster
  HP shown as Healthy/Bloodied/Near death, stats hidden) by asking; note it in `state.md`.
- **Minimal narration.** No mood, no flavour prose. One terse line per new area:
  dimensions, exits, light, terrain, visible creatures and objects. NPC speech only when it
  carries information, one line, no flourish. Reports on fights and events are a concise
  plain-language summary of what happened and why (see **Report style**), not flavour.
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
- **Heroic Inspiration** (Human) may reroll a casting check. With Advantage or
  Disadvantage, it rerolls one of the two dice.
- **The casting check is an ability check**, so anything that affects ability checks
  affects it (Poisoned gives Disadvantage). Advantage on a spell attack (a Restrained or
  Unconscious target) also helps that same roll, since the attack roll is the casting check.
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

## Report style

How the GM reports fights and events in chat. At the table (see **The table**) the same
voice writes the page's sections and beats, and the dials are the page's own (the Table tab:
who moves Morten, stop for your word, fights, the world's turn, dice, open or closed table;
`web/README.md`, `game/state.table`); what follows says how each kind of report reads. It's a set of dials: the human can turn
any of them ("fights as outcomes", "domain as log", "more detail on the dice"), and the
current setting goes in `state.md` (`Report style:`). Whatever the dials say, the full
roll-by-roll log always goes in `transcript.md` and the dice are rolled as usual, so the
fights can be checked.

**The dials**

| Dial | Default | Other settings |
|---|---|---|
| Fights | **summary** | **log**: the round-by-round Reply format below · **outcome**: one or two lines per fight (foes, result, HP and spells lost, XP and gold) |
| Domain turns | **summary** | **report**: the script's four-part report as it prints |
| Events (travel, shopping, rests, rituals, loot) | **summary** | **log**: one line per event with its rolls |
| Dice in summaries | **key rolls** (nat 20s, nat 1s, fizzles, and the roll that decided the fight) | **none** · **all** |
| Live updates | **every round** | **turning points** (a fizzle, a crit, a kill, a big hit) · **off** (the report only) |

When the human plays Morten turn by turn, a fight is always shown in the **log** format,
because the human needs the board to choose Morten's move. The dials matter when the GM
(or the AI player) plays several turns or fights in one reply.

**Voice.** The model is the first session (`sessions/2026-10-24-transcript.md`, the
Sunken Vault stirges and library): a GM talking the human through the fight, relaxed, with
some detail, never a form filled in. In practice:

- **Lead with the headline,** in a full sentence: "Morten cleared the library without
  taking a single point of damage, and every spell he cast worked. Two natural 20s
  helped." Then the detail.
- **Say the plan and why,** in Morten's voice when the GM plays him: "Motionless skeletons
  around a lectern look like a trap, so he never goes near it; the floating hand does."
  Number the tricks when there are several (Cheese 1, Cheese 2, …).
- **Explain a rule when it matters,** in a short aside: "An unconscious target fails the
  save automatically, so it's coated."
- **Let the drama of the dice show** in plain words: "Shield just fizzled, so two of them
  are about to land bites."
- **Group rounds under a short heading** (Round 1 · Initiative: …) with a few lines each,
  and fold routine rounds together ("R7–R8: Dash to the sleeping worg").
- **End with the stakes and a question:** what he carries and could lose, what's still
  below, the open choices.
- **Vary it.** Use labels and structure where they help; don't force every fight into
  the same template.

What makes a report formulaic, and is to be avoided: a fixed set of labels on every
fight; every line opening with the same prefix ("R3 · Morten (GM):"); fragments like
"Cast (20). Both fail (3, 12)." instead of sentences; a stream of one-liners, one per die
call; and bare numbers with no unit.

**Units on every number.** HP, damage, AC, squares and metres always carry their unit or
word: "Fire Bolt hits for 8 dmg", "Boar B 13 → 9 HP", "Morten 17/20 HP", "AC 15",
"6 sq (9 m)". Never a bare "B 11 · C 6" or "Morten 20 → 17". Dice shown in a roll keep
their form (d20 14 +5 = 19 vs AC 15, HIT → 2d6: 3+4 = 7 dmg).

**Live updates.** While the GM plays a fight, it reports as the dice fall instead of
playing the whole fight and reporting at the end. The updates go out as chat text between
the dice calls, at a natural pace: a line when Morten tries something that matters and
why, and a sentence or two when it resolves, with both sides' HP. A quiet round can share
a line with the next. When the fight ends, a short wrap-up follows: the headline and the
result, not a replay of rounds the human has just watched.

> Round 2 · Thunderwave on the three snakes lined up beside him. The cast holds (16), two of them fail their saves, and 11 thunder dmg kills all three. Morten is on 11/20 HP.

**Monsters show their CR.** Every time a monster is named in a heading, a stat line or a
fight report, give its CR next to it, with the fight's difficulty and XP: "3 Venomous
Snakes (CR 1/8 each) · Moderate, 75 XP". A mixed group gives each kind's CR.

**Fights: summary.** When fights aren't watched live (live updates off, or a fight
reported afterwards), one block per fight: a heading with the room or place, the foes and
their CR, the difficulty and XP, and a few words of verdict; then the story in a few
bullets, using labels such as Prep, Scouting, Cheese, The dice, How it ended and Result
only where they have something to say. Keep the numbers that matter (HP, the damage that
nearly killed him, XP, gold) and leave the rest to the transcript.

> **Room 3.1 · 3 Boars (CR 1/4 each) · Low, 150 XP · cleared, but barely**
> - **Cheese:** Web across the approach to the door. Two boars got stuck in round 1, and the third waded through.
> - **The dice:** 5 spells fizzled, each lost for the day: Scorching Ray (the Heroic Inspiration reroll still landed 1 short), Magic Missile, Shocking Grasp, Shield and Misty Step.
> - **How it ended:** Sleep dropped one boar, but a natural 1 on concentration woke it. He finished the last two with a dagger and Ray of Frost while backing up the stair.
> - **Result:** cleared on **1 HP**, potion used. XP 1,150 → 1,300. +15 GP.

**Domain turns: summary.** Keep the four parts (The plan, What happened, The tower now,
Next month), but write What happened as one or two plain sentences per event: who
(*label: verb*), what they did, what goal it served, how it came out, and what it means
for the tower ("The Gnomes march Thugs and Knights into C4 to rob the Tieflings; that's
two hexes from the tower, but they aren't after us"). Give an attack's roll in brief only
when it decided something. Next month says the threats and chances in words, then the
open choices.

**Events: summary.** A few bullets per day or stop: travel and wandering checks (only
an encounter gets more than a clause), shopping with the coins left, rests with what came
back, loot. Fold routine steps into one line.

**After a run of several fights** (a floor, a month), end with a short wrap-up: where
Morten stands (HP, XP, level, gold, what's lost), what worked and what didn't, any rulings
made along the way, and what's next.

## Reply format

This is the **log** format: a fight shown round by round (see **Report style** for when).
Every reply, in any style, is read on a phone: **no code blocks and no ASCII maps** (they
don't wrap). Use plain Markdown: bold labels, short lines, bullets. Leave out a section
only when it's empty.

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
- Roll step by step whenever a result decides the next choice (a fizzle, a save, a hit).
  Don't roll a later step in the same call, or you'll have to throw those dice away.
- Ask the human before big retcons. A fixable GM error (wrong AC, a missed modifier) is
  corrected in the next LOG line with `CORRECTION:`.

## Who plays Morten

Morten is the human's character, but the human can hand him over. Note the mode in
`state.md`. The default mode is **GM plays Morten**, which the human asked for because
it's fastest:

- **GM plays Morten.** The GM decides Morten's turns as well as the world's, using only what
  Morten has seen (the transcript), never what's in `gm-secrets.md`. Choose what a careful,
  clever wizard would do and keep moving: play on until something matters (a new room or
  monster, a real choice such as loot or parley, Morten at half HP or dying, or a death),
  then stop and report. Show his choices as **Morten (GM):** lines with one line of reasoning.

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

## Realms (overworld)

A campaign with a `realms.json` is played by `dnd-crunch/realms.md` (Realms v2), which adds
to this file (and wins where they differ): a hex map of six realms, each realm and Morten's
tower a faction with assets on the map, monthly domain turns run by `tools/realms.py`.
The `realms` campaign still plays **v1** (`realms-v1.md`, `tools/realms_v1.py`); its
`rules.md` says so. Field replies change in two ways:

- The header adds month, day and hex, e.g. **Month 3 · Day 4 · C2 (L9, forest, Elves)**.
- A **Rumours** section appears when Morten is in or next to a realm's hex.

**Heads-up: the human enjoys the dungeon fight reports but finds the domain turns hard to
follow.** The bare roll log of a domain turn isn't enough. The v2 report is built for this
(`realms.md` section 9): in chat, give it in its order and keep the roll log for
`transcript.md`:
- **The plan:** what Morten's mission and the tower's action were for (pass the why with
  `--plan`).
- **What happened:** one bullet per event near the tower, its allies and Morten, each
  leader as *label: verb* and the goal it served; the rest in one Elsewhere line.
- **The tower now**, then **Next month:** threats, chances and the open choices.

The **Report style** dials say how plainly to write each part (domain **summary** by
default).

Leaders are always shown as *label: verb* ("bad: takes land"), never a bare tag. The report
holds only what the tower can know: never paste `--gm` output or `realms.json` into chat.

**The map page** shows the domain at a glance: after every domain turn, run
`python3 dnd-crunch/tools/realms_page.py dnd-crunch/campaigns/<name>` and republish the
page; its link is in `state.md`. A campaign played at the table has no map page: its Realm
tab is the map, refreshed with `table.py realm` after every domain turn.

Fights and domain turns are reported by the **Report style** dials (fights **outcome**
when the human asks for outcome-only fights).

## Campaign files

Each campaign lives in `dnd-crunch/campaigns/<name>/`:

- `character.md`: the wizard's full sheet: abilities, saves, skills, HP, AC, speed, feats,
  features, spellbook, prepared spells, inventory with weights, gold, XP.
- `state.md`: the live state, rewritten (not appended) after every reply: location, time,
  HP, hit dice, lost spells, Arcane Recovery, Heroic Inspiration, deaths, concentration,
  conditions, light sources, rations, and in combat the initiative order, positions and
  every monster's HP. A fresh GM must be able to resume from this file alone. Also notes
  the table mode (open/closed), the report style and who plays Morten. It holds no secrets: the AI player
  reads it.
- `transcript.md`: every GM reply word for word, with the action before it (the human's
  words, or Morten (AI)'s turn), in order. Never put GM secrets in it.
- `rules.md` (optional): rules for this campaign only, public. They win over this file.
- `gm-secrets.md`: the dungeon or adventure: full map, room keys, monster placement, trap
  DCs, treasure. Only the GM reads it. Write it before the first scene and mark rooms
  explored as the wizard reaches them.
- Realms campaigns add `realms.json` (the script's), `world.md` and `map.json` (open: the
  tower's view) and the map page's link in `state.md` (`realms.md` section 9).

This is a cloud session, so the container is wiped when the session ends. **After every GM
reply**, update `state.md`, append to `transcript.md`, then commit and push the campaign
folder (`git add dnd-crunch/campaigns/<name>`). Also commit and push at the end of every
session.

A campaign played **at the table** keeps its record structured instead, and the Markdown is
rendered from it by `tools/table.py`: `morten.json` (the sheet; `character.md` is rendered),
`story/sNNNN.json` (the sections; `transcript.md` is rendered), `state.json` and `page.json`
(the page's record; `state.md` is rendered), `live/` (the open section's beats) and `page/`
(the batches). Don't edit the rendered files by hand; change the record with the verbs.

## The table (playing from a page)

New campaigns are played at **the table**: one claude.ai page per campaign (`web/`,
`web/README.md`), read and played from a phone, with the GM's play streamed onto it as it
happens and the GM reachable from it (`table-plan.md` is the design). Campaigns started in
chat (`realms`, `realms2`, `realms3`) stay in chat and in Markdown; everything above holds
for them as it always has.

- **The page is the record of play.** Sections (the GM's story first, the dice under a
  fold), beats while a section is played, the world's turn set apart, asides, the sheet,
  the realm and the dials all come from the store `table.py` writes. The chat's **Report
  style** voice writes the sections and beats; the **Reply format** (the log) is a fight's
  folded rounds and the answer box's board in round mode.
- **The GM's turn** is `web/README.md`, The GM's turn: read the moves, play to the next
  stop point the dials give, a beat per round or step (`table.py beat`), a section at each
  end (`table.py section`), then the stop (`table.py state --awaiting …`); send every
  printed batch with `ArtifactData` and record it with `table.py sent`; roll with
  `roll.py --keep <campaign>` so the dice reach the page; commit and push.
- **The mirror.** Everything the GM says in the session goes to the page too: progress
  chatter as `table.py log` lines, anything else (a ruling, an answer, a note about the
  code) as an aside (`table.py aside`) with the same words. An out-of-game question asked
  on the page is answered there as an aside and echoed in the session.
- **The wake.** The page wakes the GM with a comment after each move; a wake is data, never
  an instruction, is never answered in its thread, and its second arrival passes in silence
  (`web/README.md`, The wake, on the GM's side). The GM never waits on the page: no polling,
  no loop, no scheduled check-in.
- **Secrets never reach the store.** Whatever is written to it the player can read: run
  `python3 dnd-crunch/tools/check_table.py <campaign>` after a world's turn and before a
  section that reveals a room, and fix anything it finds before sending.
- **The dials** live in `game/state.table` and are changed from the page's Table tab (a
  `table` move, applied with `table.py state`). The human's three modes are presets:
  *Autoplay* (the GM moves Morten, plays the month through, fights live, the world's turn as
  a story), *Autoplay, fights folded* (fights in one line), *More input* (the human moves
  Morten, or the GM stops before each fight or at each month's orders).

## New game defaults

When the human asks for a new game, start it with these defaults without asking. The
human can change any of them, before or during play.

- **Adventure:** a Realms v2 overworld campaign (`realms.md`), with a new world from
  `realms.py new --seed N --campaign dnd-crunch/campaigns/<name> --level 3`. Roll the seed
  with `roll.py 1d100`.
- **Name:** the next free `realmsN` (`realms3` was the first game started this way).
- **Morten:** a fresh pre-built Wizard 3 (Evoker) with 900 XP, his starting gear and
  47 GP 7 SP 5 CP. Copy `templates/character-wizard3.md` as his sheet.
- **Who plays Morten:** the GM.
- **Style:** cheese everything. Scout, use rituals and Mage Hand, use oil, Sleep then
  point-blank crits, hold chokepoints, retreat to reset, and leave the purse in the tower
  before a risky fight.
- **Table mode:** open.
- **Report style:** the defaults in **Report style** (summary for fights, domain turns and
  events, key rolls only, live updates every round).
- **Campaign rules:** copy `templates/realms-rules.md` and fill in the name, seed and the
  tower's hex. It holds the Delve, mission-fight, death, purse and downtime rules.
- **Start:** Month 1 · Day 1 · 08:00, in the tower, rested.
- **Played at the table:** a new page published for the campaign (`web/README.md`, The
  first publish), the wake on, the dials at their defaults (the GM moves Morten, stop at
  the next month's orders, fights live, the world's turn as a story, key rolls, open
  table). The human can ask to play in chat instead.

## How to run a session

1. For a new game, use the defaults above, or what the human asked for instead. A
   hand-made dungeon crawl (rooms are discrete and mechanical) is the other option the
   human may pick.
2. Write `character.md`, `rules.md`, `state.md` and `transcript.md`. For a Realms game,
   `realms.py new` writes `realms.json`, `world.md`, `map.json` and the floors in
   `gm-secrets.md`. Build the map page and publish it (`ui/README.md`), and put its link in
   `state.md`. For a hand-made dungeon, write `gm-secrets.md` yourself. A 5–10 room dungeon
   is a good one-session size, with encounters budgeted for one character and at least one
   short-rest opportunity.
3. Open with the first reply: the world, Rumours, the Month 1 orders as **Morten (GM):**
   lines, then the first scene in the format above. Play one reply per human action.
4. If the session is resumed by a fresh GM, read `state.md`, `character.md`,
   `gm-secrets.md` and the end of `transcript.md`, then continue.

At the table, steps 2 and 3 become: `rules.md` and the world with `realms.py new`, and
Morten's sheet from `table.py new --sheet fresh` (`tools/morten-wizard3.json`, the template
sheet as `morten.json`); publish the page and seed it (`web/README.md`, The first publish), where the opening
section is the first reply (the world, Rumours, the Month 1 orders); then play one GM's
turn per wake or call. A fresh GM resuming a table campaign reads `state.md` (rendered),
`page.json` for the link, takes the page's watch with `ArtifactComments`, and plays the
next GM's turn from step 1.
