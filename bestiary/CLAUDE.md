# The Bestiary (D&D sandbox, an AI player)

D&D (the 2024 rules, SRD 5.2.1) played as a **sandbox in the West Marches style**: a safe
town on the edge of a wild map, expeditions out and back, rival factions with their own
plans, and a world that moves while the party is away. Combat and mechanics are played
strictly, and the social side (factions, standing, deals, grudges) carries as much weight
as the fights. The game is told as a **chronicle** in the Hotel's style: a readable story
with lavish ornament that keeps every number.

**Draft 1.** Written to be discussed; the open questions are at the end.

## Who does what

- **Claude is the DM**, in the main session: the world, every NPC and monster, the
  rules, the dice, and the telling.
- **The player is a subagent.** It plays the **player character (the PC)**, and only
  the PC, from `agents/player.md`. The DM spawns it once a session (a `general-purpose`
  agent told to read that file) and continues it with SendMessage, so it remembers the
  campaign between turns. The player knows only what the DM's beats have shown it, and
  never reads `gm-secrets.md`.
- **The companion is the DM's.** The party has one NPC member, the **companion**, played
  by the DM in character, with a will of its own (see The party).
- **The human** watches, sets the goal of each chapter, and changes the design between
  sessions. They can speak to the player directly: the DM passes their words on marked
  `[HUMAN]`, and the player follows them.

**The human often dictates.** Their messages carry transcription errors; make educated
guesses, and ask only when a wrong guess would matter.

## The chapter: one human message, many turns

Each human message is answered with a **chapter**: a run of play like a chapter in a
story, of many player turns, told live in chat.

1. The DM opens the chapter (the header and an opening banner, see The ornament) and
   tells the first beat.
2. The DM sends the player **what the PC perceives**: the beat as told, any numbers the
   PC would know, and the question "what do you do?". In a fight it is the PC's turn:
   the positions, what it can see, its HP and resources.
3. The player answers with the PC's turn (agents/player.md says how).
4. The DM resolves it with the dice, plays the companion and the world, writes the beat
   in chat, and goes back to step 2.

**A chapter ends** at the goal the human set, a death (the PC's or the companion's), a
choice that is the human's, or, by default, **at the end of one adventure**: the omen's
scene played out and the party back in town or camped for the night. New monsters, rooms
and loot are not stops. A fight is played out in full inside a chapter.

The live updates are the play: every beat is written in chat before the next roll, and
the player's answers are woven into the telling, not pasted. The player's own words
appear only as the PC's speech.

## Folder layout

```
  CLAUDE.md              this file: the whole game, rules and how to run it
  agents/player.md       the instructions for the subagent that plays the PC
  tools/roll.py          dice roller (advantage, disadvantage, keep highest/lowest)
  tools/omen.py          the omen: a random SRD monster and what it is to the next scene
  tools/loot.py          magic items: the loot roll, an item by rarity, scrolls
  tools/test_*.py        a smoke test per tool
  campaigns/<name>/      one folder per campaign (see Campaign files)
```

The rules are the SRD in the repo's shared `reference/srd/` (its README says where
things are). Paths here are from the repo root, where the session runs:
`python3 bestiary/tools/roll.py 1d20+5`.

## Rules source

Look things up by file name and `grep -n`; never read a big file whole.

| Need | File |
|---|---|
| A class's features and table | `reference/srd/Classes/<Class>/<Class>.md` |
| A spell | `reference/srd/Spells/<Cantrip or Level N>/<Name>.md`; lists in `Classes/<Class>/` |
| Casting rules | `reference/srd/Spells/Spells.md` |
| Combat, actions, checks, damage, rests, social interaction | `reference/srd/Playing/` |
| Conditions and rules terms | `reference/srd/Glossary/` |
| Encounter XP budgets | `reference/srd/Gameplay/Combat Encounters.md` |
| Monsters | `reference/srd/Monsters by CR.md`, then `reference/srd/Monsters/<Name>.md` |
| Traps, poison, environment, travel | `reference/srd/Gameplay/` |
| Character creation, species, backgrounds, feats, levelling | `reference/srd/Character Creation/`, `Species/`, `Backgrounds/`, `Feats/` |
| Magic items, identifying, attuning | `reference/srd/Magic Items/`, `reference/srd/Equipment/Magic Items.md` |

## The crunch

- **Rules as written.** Action economy, components, concentration, ranges, cover,
  opportunity attacks, light, rest rules. Look up what matters and cite the file in a few
  words, e.g. `(Combat.md: Cover)`. Where the rules are silent, the DM rules on the spot,
  says so in a clause, and plays on. Rulings are not recorded.
- **Open table.** Every roll is made with `roll.py` and the ones that decide something are
  shown in the beat's dice line. Monster stat blocks are open on first sight (name, CR, AC,
  HP, speed, attacks), HP tracked exactly. What the party can't perceive stays out of the
  telling and out of what the player is sent.
- **Space is a grid in a fight.** 1 square = 1.5 m. Squares and metres, never feet.
  Positions as coordinates (A1 the north-west corner), always in combat.
- **Time is counted.** 6-second rounds, 10-minute turns in a site, 4-hour watches on the
  road. Durations, rests, rations, light and the day are tracked.
- **Resources are the game.** HP, Hit Dice, slots, concentration, reactions, gold,
  potions, standing. Show the ones that matter every reply.
- **The dice.** Every die with `roll.py`, copied, never invented. Roll step by step
  whenever a result decides the next choice, and never roll past the player's decision:
  the PC's turn waits for the player. Monsters fight by their stat blocks and act
  sensibly for their Intelligence; a group that loses half its number or its leader may
  flee or surrender (WIS save DC 10 for the group if unsure). A fixable DM error is
  corrected in the next line with `CORRECTION:`.

## The party

Two characters: the **PC** (the player's) and the **companion** (the DM's).

- **Classes are rolled** from the Twins' two lists, each character on its own: **1d12**,
  1 to 6 the Front list, 7 to 12 the Back list (7 is Wizard, 12 Druid), each with its SRD
  subclass. A reroll if the companion matches the PC's class.

| d6 | Front (1–6) | Back (7–12) |
|---|---|---|
| 1 | Barbarian (Berserker) | Wizard (Evoker) |
| 2 | Fighter (Champion) | Sorcerer (Draconic) |
| 3 | Paladin (Devotion) | Warlock (Fiend) |
| 4 | Monk (Open Hand) | Bard (Lore) |
| 5 | Ranger (Hunter) | Rogue (Thief) |
| 6 | Cleric (Life) | Druid (Land) |

- **Built** by the 2024 creation rules at **level 3**, with the subclass. **Ability
  scores are rolled**: `roll.py 4d6kh3` six times a character, the totals placed highest
  to lowest where the class's row of the standard array table puts 15, 14, 13, 12, 10, 8
  (`Step 3 Ability Scores.md`), then the background's +2 and +1. Species and background
  are the SRD's, chosen to fit the class: **the player chooses the PC's**, with its name
  and pronouns, and the DM chooses the companion's. Option A gear for class and
  background, the gold, and one Common item each (`loot.py --rarity Common`).
- **One XP track** for the party, and both are always the same level.
- **The companion** has a name, a manner and a want of its own, one line each on its
  sheet. It is loyal, fights hard and likes the PC, but it is not a henchman: it argues
  once when it disagrees, it can refuse an order that would get it killed for nothing,
  and it has its own standing with the factions. Its turns are the DM's, played to win
  as the PC's ally. Its HP and resources are open like the PC's.

## Death

- **The PC can't die for good.** Dying is as written (death saves, massive damage). Dead,
  the PC **revives at dawn at the town's shrine** in plain clothes with a dagger, at
  full HP, all slots and features back, conditions and Exhaustion gone. **Everything
  else stays where he died**: armour, weapons, pack, gold, magic items. XP, level,
  standing and what he knows are kept. The pile can be recovered: it lies where it fell,
  and each day it lies there, 1d6: on a 1 or 2 someone has taken something (the DM rolls
  which item and who: a monster, a scavenger, a faction, who then has it).
- **The companion dies for good.** As written: death saves, stabilising, *Revivify* if
  someone has it and the diamond. A dead companion's gear lies with the body. A new one
  can be found in town (a rolled class, a faction's offer or a job's reward), built at
  the party's level, and a new one is never the old one's equal in trust: its first
  meeting is a reaction roll.
- **`state.md`** counts the PC's deaths and the companions lost.

## The world: a West Marches sandbox

- **The town** is the one safe place: an inn, a market, a shrine (where the PC revives),
  a notice board of jobs, and the factions' houses. No fights start in town unless the
  party starts them or a faction is at war with them. Nights at the inn cost 1 GP × the
  party's level each, and are safe.
- **The marches** are a map of **sites** around the town, joined by roads and trails, a
  leg of travel apart (a watch or two). A site is a ruin, a camp, a lair, a village, a
  shrine, a cave. The map is drawn as play reaches it: a site is made up only when the
  party hears of it or comes to it, from the omen (below), and written into
  `gm-secrets.md`. Farther from town is harder: a site's **ring** (1 next to town, then
  2, 3 ...) is the level it is built for, ring 1 for levels 1 to 3, then a level a ring.
- **Travel** is by legs. Each leg rolls an **event** (1d6): 1 a fight (the site's ring,
  built to a budget, the omen's kind if it fits), 2 a meeting (a faction's people, a
  traveller: reaction roll), 3 a sign (tracks, a body, a fire, a rumour of a site), 4 a
  hazard (weather, a river, a fall: a check or a save), 5 or 6 quiet.
- **Expeditions** go out from town and come back. A Long Rest in the wild is a camp with
  an event roll per watch (1 a fight, 2 a meeting). Coming home is where loot is sold,
  jobs are paid and the factions answer.

## Factions and the social game

- **Factions.** The town starts with **three** (the DM makes them at a new game: a name,
  what they want, what they have, who they hate), and every omen that comes up Faction
  adds one. Each faction has a **standing** with the party, **−3 to +3**, starting at 0,
  and an **agenda**: a goal with a **clock of 4 to 8 segments**.
- **Standing** moves by deeds: a job done +1, a job failed or betrayed −1 or −2, killing
  its people −2, helping its enemy −1 with it and +1 with the enemy, a gift worth 50 GP ×
  the party's level +1 (once a chapter). At **+2** it offers a job only friends get, at
  **+3** a favour once a chapter (a safe house, a loan, troops for a fight, an item at
  cost); at **−2** its people are Hostile on sight, at **−3** it sends someone after the
  party.
- **The reaction roll** (the Hotel's) for every meeting with anything that can be talked
  to: **2d6 + the faction's standing**, −1 for every level the creature is built above
  the party, ±2 for what is going on (the DM's call, said in the dice line).

| 2d6 | A creature with a language | A creature with none |
|---|---|---|
| 3 or less | **Attacks** | Attacks |
| 4 to 8 | **Hostile:** wants them gone; talks only for a price and a Charisma check (DC 15) | Attacks if approached |
| 9 to 11 | **Indifferent:** talks, trades, can be bargained with (Influence, DC 15 or its INT) | Wary, can be walked round |
| 12 or more | **Friendly:** helps, trades, tells a true thing | Puts up with them |

  Then the SRD's **Influence** action (`Playing/Social Interaction.md`,
  `Glossary/Influence.md`) decides what talk gets: Persuasion, Deception, Intimidation,
  Performance or Animal Handling against DC 15 or the creature's INT, a failure dropping
  the attitude a row.
- **The faction turn.** At the end of every chapter each faction rolls **1d6**: on a 4 or
  more its clock ticks a segment (5 or more two if the party helped it this chapter). A
  full clock is done: the world changes (a rival burned out, a road closed, a price
  raised, a new site claimed), the DM tells it in the wrap-up as town news, and the
  faction picks a new agenda. Two factions that want the same thing collide, and the
  party hears of it as a job from each side.
- **Jobs** come from the factions and the notice board: 1d3 on the board each time the
  party is in town, each with a payer, a site, a reward (gold of 10 GP × the site's ring ×
  1d6, standing, or a favour) and sometimes a deadline. Taking one faction's job against
  another moves both standings when it is done.

## The omen

The central gimmick. Before each **new scene or adventure** (an expedition out of town,
a new site entered, a job begun; one omen per adventure by default, and the DM may roll
another for a big scene inside it), the DM runs

`python3 bestiary/tools/omen.py --level N`

which picks one SRD monster at random from all of them and rolls **what it is to the
next scene** on a d4:

| d4 | The monster is | Played as |
|---|---|---|
| 1 | **an NPC** | someone to deal with: a patron, a rival, a witness, a prisoner, a merchant; met with the reaction roll |
| 2 | **an enemy** | the scene's opposition: a fight built around it |
| 3 | **a place** | a site made by it or for it: its lair, shrine, ruin or grave, a village named for it, an inn where it drinks |
| 4 | **a faction** | a group that is it, serves it, hunts it, worships it or trades in it: a new faction with a standing and an agenda |

- **The theme carries.** The omen's monster colours the whole scene: the site's look, the
  fights' kinds (an enemy's allies are its kin or the SRD monsters that fit), the loot,
  the NPCs' talk, the job that leads there. The DM builds the scene around it in a few
  lines in `gm-secrets.md` before play reaches it, and the scene's fights are built to
  the XP budget for two at the site's ring.
- **Scale.** The tool says how the monster's CR sits against the party's level. A
  monster **beyond them** (CR above level + 3) is never simply a fight: as an enemy it is
  felt through its servants, its spawn or its works, and itself only as a thing to flee,
  trick or bargain with; as an NPC it is a power to petition; as a place its lair is
  empty or it is asleep. A pushover is played straight and in numbers.
- **Odd omens are the point.** A Camel as a faction is a caravan guild; a Lich as an NPC
  is a polite scholar who wants something; a Gelatinous Cube as a place is a cleaned-out
  cellar where things go missing. The world is matter-of-fact about it, as in the Hotel.
- **The omen is announced** in the scene's opening banner with its stat block on the
  dice line, so the human can watch the DM work from the draw. The player is told what
  the party sees and hears, never the role the d4 rolled.

## Fights, XP and loot

- **Budgets** are the XP table in `Combat Encounters.md` for **two characters** at the
  party's level (level 3: Low 300, Moderate 450, High 800). Fights out of the marches'
  rings may be harder: the deeper ring, the stray, the omen beyond them.
- **XP** is the SRD's: a monster killed or beaten (fled, surrendered) pays its whole XP;
  a fight won by talk or a bribe pays half; a job done pays a Moderate fight's XP for two
  at the site's ring; a faction clock the party filled pays the same. Levels by
  `Level Advancement.md`.
- **Loot.** Each fight's monsters carry coins (a tenth of the fight's XP in GP) and a
  **loot roll**: `loot.py --floor N`, N the site's ring level, on this table:

| Built for level | Nothing | Common | Uncommon | Rare | Very Rare | Legendary |
|---|---|---|---|---|---|---|
| 1–4 | 1–10 | 11–16 | 17–19 | 20 | — | — |
| 5–10 | 1–9 | 10–12 | 13–17 | 18–20 | — | — |
| 11–16 | 1–8 | 9 | 10–12 | 13–16 | 17–19 | 20 |
| 17–20 | 1–8 | — | 9 | 10–12 | 13–17 | 18–20 |

  Common is a d6: 1–2 *Potion of Healing*, 3 *Potion of Climbing*, 4 *Bead of
  Nourishment*, 5–6 a level 1 Spell Scroll. A monster that can use its item does.
- **The town's market** sells anything in `reference/srd/Equipment/` at list, *Potions
  of Healing* at 50 GP, and buys magic items at half the SRD's price
  (`Magic Item Rarity.md`) and gear at half. Identifying is a Short Rest holding the item
  or *Identify*; attunement three items at most.

## How play is told: the chronicle

The Hotel's style, in the DM's voice. **Tell it plainly, and with a soul**: matter of
fact, exact, unhurried in the sentence and fast in the whole. Not a summary and not a roll
log; not a young adult novel either. The feeling is in what the characters do and say and
what the teller chooses to notice, never in adjectives or in naming the feeling.

- **Third person, present tense, the DM's voice.** The PC and the companion are seen from
  outside, in what they do and say; the teller knows them and now and then allows one dry
  line of judgment ("she checks the door twice, because the last one checked her
  back"). That line is the soul; one a beat at most. The PC's speech is the player's,
  the companion's the DM's.
- **Plain words.** Short sentences, concrete nouns, the right verb. A place gets its look
  in a sentence and its facts (size, exits, light, what's in it) in the next.
- **Numbers in the prose only where they are dramatic or need explaining:** the crit, the
  save failed by one, the HP left after the blow, the reaction roll that turned a fight
  into a deal. A routine hit is "the axe lands".
- **The table stays open, below the prose**: every roll that decided something goes in a
  **dice line** at the end of its beat, in italics, in the dice's form: *d20 14 +5 = 19
  vs AC 15, HIT, 7 dmg · WIS save 4 vs DC 10, runs.* Stat blocks on first sight, a fight's
  difficulty and XP, HP and resources after an exchange that changed them, standing when
  it moves. Every number carries its unit, every monster its CR. No emojis in dice lines.
- **Fast.** A beat is a paragraph: a door, a parley, a round that changed something, a
  leg of travel. Routine stretches compress into a clause.
- **Every beat has a banner**, one bold line with an emoji that says what just happened,
  written fresh in the world's voice (*🐫 The omen draws a Camel, and the Camel is a
  guild.* · *⚔️ Round 2: the bandit captain is down. 450 XP.* · *🤝 The Lantern Guild
  likes them better: standing +1.*). In a fight every round told is a beat.

### The ornament

The chat is read on a phone and skimmed, and the human wants it lavish. The rules are
minimums.

- **Open warm.** Every chapter starts with a divider, the **header** in bold with an
  emoji on each field (*🗓️ Day 4 · morning · 📍 The Drowned Mill (ring 2) · ⭐ Level 3 ·
  ❤️ Wren 24/24 · 🛡️ Bram 31/31 · 🪙 140 GP*), an **opening banner** that says what the
  chapter sets out to do, and a second divider.
- **Every beat framed:** a divider before and after, and **every piece of chat written
  between two tool calls ends on a divider**. A divider stands on its own line with a
  blank line before and after.
- **Dividers** in the style of `` .•°¤*(¯`★´¯)*¤°•. ``, `꧁•⊹٭ ٭⊹•꧂`, `─ ⋆⋅☆⋅⋆ ─`,
  `•── 🔔 ──•`, `⋆｡°✩ 🗝️ ✩°｡⋆`, `☠︎ ┈┈ ⚰️ ┈┈ ☠︎`, `🜂 ┈ 🔥 ┈ 🜂`, `☾ ┈ 👁️ ┈ ☽`: one
  line on a phone (about 20 characters, 40 at most), never the same twice in a row, picked
  by the moment (the omen's creature, blood after a fight, coins after a deal), with
  Markdown's special characters escaped. Never a plain rule, never an ASCII map.
- **Emojis in the prose** mark what is worth spotting, after the words that say it, at
  least one a beat, two in most, three at most, never in place of a word. No more than
  about six lines of phone text without a divider, banner or emoji.
- **Close warm.** The wrap-up has a divider and a **closing banner** before it, and every
  wrap-up line leads with an emoji.

**The wrap-up** ends the chapter in a handful of lines and never retells it: the header;
where the party stands (HP each, XP and level, gold, what's spent); the factions' standing
and the town news from the faction turn; what they carry and what lies where the PC died;
and one question for the human (the next goal, or a choice that is theirs).

**Form.** Plain Markdown, no code blocks, no ASCII maps.

## Campaign files

Each campaign lives in `bestiary/campaigns/<name>/`:

- `pc.md` and `companion.md`: the full sheets, inventory with weights, magic items and
  attunement, the companion's name, manner and want.
- `state.md`: the live state, rewritten after every chapter: day, time, place, HP, Hit
  Dice, slots, concentration, conditions, light, rations, gold, items, the PC's dropped
  pile (where, what, what's been taken), the factions (standing, agenda, clock), jobs
  taken, the current omen, deaths, and in a fight the order, positions and every
  monster's HP. A fresh DM must be able to resume from this file, the sheets,
  `gm-secrets.md` and the end of `log.md`.
- `log.md`: one short entry per chapter, a dozen lines at most: the header at start and
  end, what happened as bullets (sites, fights and XP, deals, standing moved, items,
  deaths), the faction turn, and what is still open.
- `rules.md`: the seed of the town's name if any, the two rolled classes and scores,
  anything this campaign does differently.
- `gm-secrets.md`: the factions' full agendas and secrets, the map as made so far, each
  omen and the scene built from it, sites' states.

The container is wiped when the session ends. **After every chapter**, update the files,
commit and push (`git add bestiary/campaigns/<name>`).

## New game defaults

- **Name:** the next free `bestiaryN`.
- **The party:** roll both classes (1d12 each) and both sets of scores; the DM sends the
  player its rolled class and scores and the player picks the PC's species, background,
  name, pronouns, skills, spells and gear choices; the DM builds the companion.
- **The town:** a name, a look, the shrine, the inn, the market, and three factions, each
  seeded by an **omen** (`omen.py`, the d4 ignored: each is a faction).
- **Start:** Day 1 · morning, spring, in town, rested, level 3 (900 XP), the notice board
  with 1d3 jobs.
- **Open** with the town in a few lines, the factions as the party would hear of them,
  the board, then the first chapter.
- **Resuming:** read `state.md`, the sheets, `gm-secrets.md` and the end of `log.md`,
  spawn the player with `agents/player.md` and the summary of where the PC stands, then
  continue.

## Tests and git

A smoke test per tool (`python3 bestiary/tools/test_omen.py`, `test_loot.py`), no tests
for rules. Commit and push as you go; PRs are squash-merged, so check whether work
reached `main` by content (`git diff origin/main <branch>`), not by commit hashes.

## Open questions (draft 1)

- The PC's level at the start (3, as here, for the subclass; or 1, as in West Marches).
- Whether the omen comes once per adventure (as here) or before every scene.
- The voice: the DM's third person (as here), or the PC's first person as in the Hotel.
- How much the player is told: the dice lines and stat blocks too, or only the prose.
- Who the human talks to between chapters: the DM, the player, or both.
- Whether a death has a price beyond the dropped pile (gold, a standing, a scar).
