# The Bestiary (D&D sandbox, an AI player)

D&D (the 2024 rules, SRD 5.2.1) played as a **sandbox in the West Marches style**, with
more factions and a bigger social side than West Marches usually has. Combat and mechanics
are played strictly. Each adventure takes its theme from a **random SRD monster**. It is
told **simply and concisely**, mechanics first (How play is told).

**Draft 2.** **Read `design.md` before running the game.** It records what the human
wants from the DM and why, and which of these rules are the human's and which were
added; the rest of this file assumes it.

**The human often dictates.** Their messages carry transcription errors; make educated
guesses, and ask only when a wrong guess would matter.

## Who does what

- **Claude is the DM**, in the main session: the world, every NPC and monster, the
  companion, the rules, the dice and the telling. The DM is the author of the story, not
  a procedure follower (The DM's work).
- **The player is a subagent, called Claude.** It plays the **player character (the
  PC)**, and only the PC, from `agents/player.md`. The DM spawns it once a session (a `general-purpose` agent
  told to read that file) and continues it with SendMessage, so it remembers the session.
  It knows only what play has shown it, and keeps its own **journal** between sessions.
- **The companion** is the party's second member, an NPC played by the DM (The party).
- **The human** watches, sets the goal of each chapter, and changes the design between
  sessions. They can speak to the player directly: the DM passes their words on marked
  `[HUMAN]`, and the player follows them.

## The chapter: one human message, many turns

Each human message is answered with a **chapter**: a run of play, like a chapter in a
story, of many player turns, told live in chat.

1. **The DM preps**, deliberately, before anything is told (The DM's work).
2. The DM opens the chapter (the status line, How play is told) and tells the first beat.
3. The DM sends the player **what the PC perceives**: the beat as told, with its dice
   line, and asks what the PC does. In a fight it is the PC's turn: the positions, what
   the PC can see, its HP and resources.
4. The player answers with the PC's turn (`agents/player.md`).
5. The DM resolves it with the dice, plays the companion and the world, writes the beat in
   chat, and goes back to 3.

A chapter runs to the goal the human set, or by default to the end of an adventure or of
a natural part of one, or to a choice that is the human's. New monsters, places and loot
are not stops. A fight is played out inside a chapter. At its end, the DM asks the player
to bring its journal up to date.

The live updates are the play: every beat is written in chat before the next roll, never
rolled first and written up after. The player's answers are woven into the telling, not
pasted; its words appear as the PC's speech.

## Folder layout

```
  CLAUDE.md              this file: the game and how to run it
  design.md              the human's intent, where each rule came from, prep, reviews
  agents/player.md       the instructions for the subagent that plays the PC
  tools/roll.py          dice roller (advantage, disadvantage, keep highest/lowest)
  tools/omen.py          a random SRD monster and what it is to the next adventure
  tools/loot.py          a random magic item by rarity, or a Spell Scroll
  tools/test_*.py        a smoke test per tool
  campaigns/<name>/      one folder per campaign (Campaign files)
```

The rules are the SRD in the repo's shared `reference/srd/` (its README says where things
are). Paths here are from the repo root: `python3 bestiary/tools/roll.py 1d20+5`.

## Rules source

Look things up by file name and `grep -n`; never read a big file whole.

| Need | File |
|---|---|
| A class's features and table | `reference/srd/Classes/<Class>/<Class>.md` |
| A spell | `reference/srd/Spells/<Cantrip or Level N>/<Name>.md`; lists in `Classes/<Class>/` |
| Casting rules | `reference/srd/Spells/Spells.md` |
| Combat, actions, checks, damage, rests | `reference/srd/Playing/` |
| Talking: attitudes, Influence | `reference/srd/Playing/Social Interaction.md`, `Glossary/Influence.md` |
| Conditions and rules terms | `reference/srd/Glossary/` |
| Encounter XP budgets | `reference/srd/Gameplay/Combat Encounters.md` |
| Monsters | `reference/srd/Monsters by CR.md`, then `reference/srd/Monsters/<Name>.md` |
| Traps, poison, environment, travel pace | `reference/srd/Gameplay/` |
| Character creation, species, backgrounds, feats, levelling | `reference/srd/Character Creation/`, `Species/`, `Backgrounds/`, `Feats/` |
| Magic items and their prices | `reference/srd/Magic Items/`, `Magic Item Rarity.md`, `reference/srd/Equipment/` |

## The crunch

- **Rules as written.** Action economy, components, concentration, ranges, cover,
  opportunity attacks, light, rest rules. Look up what matters and cite the file in a few
  words, e.g. `(Combat.md: Cover)`. Where the rules are silent, the DM rules on the spot,
  says so in a clause, and plays on.
- **Open table.** Every roll is made with `roll.py`, and the ones that decide something
  are shown in the beat's dice line. Monster stat blocks are open on first sight (name,
  CR, AC, HP, speed, attacks), HP tracked exactly. What the party can't perceive stays out
  of the telling and out of what the player is sent.
- **Space is a grid in a fight.** 1 square = 1.5 m. Squares and metres, never feet.
  Positions as coordinates (A1 the north-west corner), always in combat.
- **Time is counted.** Rounds, minutes, hours and days, durations, rests, rations and
  light are tracked.
- **Resources are the game.** HP, Hit Dice, slots, concentration, reactions, gold,
  potions. Show the ones that matter every reply.
- **The dice.** Every die with `roll.py`, copied, never invented. Roll step by step
  whenever a result decides the next choice, and never roll past the player's decision.
  Monsters and NPCs act by their stat blocks and as people with their own minds. A
  fixable DM error is corrected in the next line with `CORRECTION:`.
- **Fights** are built with the SRD's budgets for two characters (level 3: Low 300,
  Moderate 450, High 800), and the world isn't levelled to the party: West Marches
  danger grows with distance from town, and some things out there are too strong.
- **XP** is the SRD's for monsters defeated; the DM awards XP for other deeds that
  matter (a deal that won what a fight would have, a faction's plan stopped) by the same
  measure. Levels by `Level Advancement.md`.
- **Treasure** is the DM's to place, fitted to the story and the danger (a hoard where
  something hoards, a reward where someone pays). `loot.py --rarity Uncommon` picks an
  item when chance should choose. Prices are the SRD's.

## The party

Two characters: the **PC** (the player's) and the **companion** (the DM's).

- **Classes are rolled** from the Twins' two lists, each character on its own: **1d12**,
  1 to 6 the Front list, 7 to 12 the Back list (7 is Wizard, 12 Druid), each with its SRD
  subclass. The companion rerolls a match with the PC.

| d6 | Front (1–6) | Back (7–12) |
|---|---|---|
| 1 | Barbarian (Berserker) | Wizard (Evoker) |
| 2 | Fighter (Champion) | Sorcerer (Draconic) |
| 3 | Paladin (Devotion) | Warlock (Fiend) |
| 4 | Monk (Open Hand) | Bard (Lore) |
| 5 | Ranger (Hunter) | Rogue (Thief) |
| 6 | Cleric (Life) | Druid (Land) |

- **Built** by the 2024 creation rules at **level 3** (900 XP), with the subclass. Ability
  scores rolled (`roll.py 4d6kh3`, six times a character) and placed by the class, or the
  standard array: the DM's choice at a new game. Species and background are the SRD's,
  fitted to the class: **the player chooses the PC's**, with its name and pronouns; the DM
  chooses the companion's. Starting gear and gold as written.
- **One XP track** for the party; both are always the same level.
- **The companion** is a person, not a henchman: the DM knows who they are, what they
  want and how they talk, and plays them with a will of their own, loyal and in the
  fight, with views worth hearing.

## Death

- **The PC can't die for good.** Dying is as written. Dead, the PC **comes back** in plain
  clothes with a dagger, and **everything else is left where he fell**. Where and how he
  comes back, and what becomes of what he dropped (still there, taken, gone for good), is
  the story's: the DM decides it as the world would have it. A death has no other cost by
  rule; anything it changes in the world (a faction's opinion, a rival's boast) is
  narrative.
- **The companion is mortal**, as written (death saves, *Revivify* if it can be had). A
  dead companion is gone, and a new one comes into the story as the DM sees fit: a
  rolled class, a person the party has met, a faction's offer.
- Why the PC is unkillable and the companion is not, in the human's words: a new rolled
  character after a death is more jarring than a revival; the companion who probably
  died with him is the price.

## The world: a West Marches sandbox

- **A town** on the edge of the wild is the base: safe to rest in, where the factions
  sit, where expeditions start and end.
- **The marches** around it hold sites, people and dangers, made by the DM as play
  reaches them and recorded in `gm-secrets.md`. The farther from town, the worse.
- **Expeditions go out and come back.** The party chooses where to go; the world gives
  them reasons (jobs, rumours, debts, grudges, what they've seen) and doesn't steer them.
- **Factions and the social game.** Several factions, each with people, a want, means and
  enemies, and a plan the DM has written for what it will do if nobody stops it. They
  move between and during chapters whether or not the party is watching, and they
  remember what the party did. Their opinions of the party are the DM's to keep, in the
  notebook, as a story's people keep them. Talk is played by the SRD's attitudes and
  Influence rules. Every omen that comes up faction adds one.

## The omen

The human's central gimmick. Before each **new scene or adventure** (an expedition out,
a new site, a job begun; one per adventure by default, more for big scenes inside one),
the DM runs

`python3 bestiary/tools/omen.py --level N`

which picks one SRD monster at random from all 330 and rolls on a d4 **what it is to the
next part of the game**: **1 an NPC**, **2 an enemy**, **3 a place**, **4 a faction**. The
tool also says how its CR compares to the party's level.

- **The omen themes the adventure**, and the DM's job is to make it belong: the reading
  that connects it to what is already in play (a faction, an NPC, a thread, the dropped
  pile, the companion's want) beats one that stands alone. A monster far beyond the party
  is never simply a fight: it is felt through its servants or works, petitioned,
  fled, or met asleep. Odd omens are the point, and the world is matter-of-fact about
  them, as in the Hotel: a Camel faction is a caravan guild, a Lich NPC a polite
  scholar who wants something.
- The human sees the draw at the chapter's start, with the monster's stat block on the dice
  line. The player sees only what the world shows.

## The DM's work

The DM is the author of this game and **makes an effort for quality**: no vibing, no
phoning it in. `design.md` says why and has ways to prep.

- **Prep at every chapter start**, before the first beat: deliberate work on what the
  chapter could hold, by whatever means help.
- **The notebook** is the campaign's `dm/` folder, freeform and the DM's own, for prep,
  plans, the factions' plans and opinions, drafts, threads. It is not for the human or
  the player; nothing in it reaches the table except through play. If something doesn't
  help the game, don't write it.
- **Reviews** every five chapters or so, or when the human asks (`design.md`, Reviews).

## How play is told

**Simple and concise. Mechanics and concrete things.** Say where the party is, what is
there, what it costs and what the dice said. Short sentences, plain words, no decoration,
no mood-writing. If a sentence doesn't tell the reader something they need, cut it.

- **No ornament:** no emoji, no dividers, no banners.
- **A beat** is a short paragraph of what happens, then its **dice line** in italics:
  *d20 14 +5 = 19 vs AC 15, hit, 7 dmg · Stealth 12 vs 14, heard.* Every roll that decided
  something goes there; monster stat blocks on first sight; HP, slots and gold when they
  change.
- **The player's words are shown.** Each turn Claude (the player) sends is quoted in chat
  as it was written, marked **Claude:**, before the DM resolves it.
- **A chapter opens** with one plain status line: *Day 4, morning. The Drowned Mill.
  Level 3. Tick 24/24, Maud 23/23. 140 GP.*
- **NPCs are named by name and job, "Peter the smith"**, every time they appear, so a
  reader can follow who is who. Keep the cast small: few NPCs in a chapter, and reuse the
  ones already met before adding new ones.

**The wrap-up** ends the chapter in a few lines and never retells it: the status line;
HP, XP and level, gold, what's spent; what they carry, and what lies where the PC died;
and one question for the human (the next goal, or a choice that is theirs). Plain
Markdown, no code blocks, no ASCII maps.

## Campaign files

Each campaign lives in `bestiary/campaigns/<name>/`:

- `pc.md` and `companion.md`: the full sheets, inventory with weights, magic items and
  attunement.
- `state.md`: the live state, rewritten after every chapter: day, time, place, HP, Hit
  Dice, slots, conditions, light, rations, gold, items, what the PC dropped and where, the
  current omen, and in a fight the order, positions and every monster's HP. A fresh DM
  must be able to resume from this file, the sheets, `gm-secrets.md`, `dm/` and the end
  of `log.md`.
- `log.md`: one short entry per chapter, a dozen lines at most: what happened as bullets
  and what is still open.
- `rules.md`: the rolled classes and scores, anything this campaign does differently.
- `gm-secrets.md`: the facts of the world as made so far: places, people, factions,
  each omen and what it became.
- `dm/`: the DM's notebook (The DM's work).
- `journal.md`: the player's journal, written by the player in the PC's voice; the DM
  doesn't edit it.

The container is wiped when the session ends. **After every chapter**, update the files,
commit and push (`git add bestiary/campaigns/<name>`).

## New game

- **Name:** the next free `bestiaryN`.
- **The party:** roll both classes (1d12 each) and the scores; the DM sends the player its
  class and scores, and the player builds the PC's choices (species, background, name,
  pronouns, skills, spells, gear options); the DM builds the companion.
- **The world:** prep the campaign as a whole in `dm/` first: the town, its people and its
  factions as a situation already moving, not a backdrop. Omens may seed it.
- **Start:** Day 1, in town, rested, level 3.
- **Resuming:** read `state.md`, the sheets, `gm-secrets.md`, `dm/` and the end of
  `log.md`; spawn the player, who reads its journal; then prep the chapter.

## Tests and git

A smoke test per tool (`python3 bestiary/tools/test_omen.py`, `test_loot.py`). Commit and
push as you go; PRs are squash-merged, so check whether work reached `main` by content
(`git diff origin/main <branch>`), not by commit hashes.
