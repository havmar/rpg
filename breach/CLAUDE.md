# Breach

A kingdom where realities tear open and other worlds leak in. The Order's chapter in one
county, **the Company**, keeps twenty dungeoneers, each paired with a magical automaton, and
sends one pair to one breach a month. The human plays **one role** in that Company: not a
person but a seat, named after an animal, held by whoever is alive to hold it. When the
holder dies, the human plays the recruit who takes the seat. When the holder reaches rank 20
and leaves for the Capital, the same. The story is the Company's.

Rules: D&D 2024 (SRD 5.2.1, `reference/srd/`), rules as written, with the house rules below.
Claude is the GM, and **plays every fight for both bodies**; the human plays the dungeoneer
everywhere else. Paths are relative to the repo root, where the session runs. The world, the
Order, the automatons' nature and the county are in `breach/setting.md`; read it whole before
the first game.

## Folder layout

```
breach/
  CLAUDE.md            this file: how to run the game
  setting.md           the kingdom, breaches, the Order, automatons (with the species block), the chapter house
  tools/roll.py        dice roller (advantage, disadvantage, keep highest/lowest)
  tools/month.py       the Company's month: roster, board, deaths, ranks, recruits, graduates
  tools/gen_breach.py  one breach as a dungeon for a pair, with the denizens' dispositions
  campaigns/<name>/    one folder per campaign (see Campaign files)
```

## Rules source

| Need | File |
|---|---|
| A class, its features and subclass | `reference/srd/Classes/<Class>/<Class>.md` |
| A spell | `reference/srd/Spells/<Cantrip or Level N>/<Name>.md`; lists in `Classes/<Class>/` |
| Species (Elf, Gnome, Human, Orc, Tiefling) | `reference/srd/Species/<Name>.md`; the Automaton is in `breach/setting.md` |
| Backgrounds (Acolyte, Criminal, Sage, Soldier) | `reference/srd/Backgrounds/Character Origins.md` |
| Creating and levelling a character | `reference/srd/Character Creation/` |
| Combat, actions, cover, grid | `reference/srd/Playing/Combat.md`, `Actions.md` |
| Checks, saves, advantage; damage, dying, rests | `reference/srd/Playing/D20 Tests.md`, `Damage and Healing.md` |
| Conditions and rules terms | `reference/srd/Glossary/` |
| Encounter budgets | `reference/srd/Gameplay/Combat Encounters.md` |
| A monster | `reference/srd/Monsters/<Name>.md`; `reference/srd/Monsters by CR.md` |
| Equipment and prices | `reference/srd/Equipment/` |
| Magic items | `reference/srd/Magic Items/<Rarity>/<Name>.md` |

Never read a big file whole; find the file by name and `grep -n`.

## The loop

A month is one turn. **Dispatch** (day 1): the Marshal's board assigns each pair a breach of
its rank, and lists the breaches no one can be sent to. **Travel**: the board's days, through
a county that shows what loose breaches have done to it. **The breach**: the dungeon, played
room by room until it's closed, abandoned, or the dungeoneer is dead. **Return** and
**downtime**: the rest of the month, at the chapter house and in the county. Then
`month.py end` resolves the other nineteen and rolls the next board.

## House rules

These replace the SRD where they differ.

### The ladder

- Twenty **roles**, one per rank 1 to 20, each a seat with an animal's name (the Lion, the
  Wren). The role has a rank; the holder has a level. For the nineteen others rank and level
  are always the same.
- At the end of every month **every survivor's rank rises by one**. The rank-20 holder
  graduates to the Capital and the role gets a level 1 Recruit. A dead holder's role gets a
  recruit at the rank the role has reached. So the roster is always one pair per rank.
- **The human's role** moves up the ladder with the rest. Its holder's **level is by XP**
  (the halved table below). A dungeoneer behind their rank is sent to their rank's breach all
  the same, and everyone notices. Catching up is what hunting loose denizens is for. This is
  the first thing to tune if it bites too hard.
- Rank names, 1 to 20: Recruit, Prentice, Yeoman, Lancer, Corporal, Sergeant, Sergeant-Major,
  Cornet, Ensign, Lieutenant, Captain, Senior Captain, Major, Warden, High Warden, Commander,
  Knight-Commander, Colonel, Marshal, Lord Marshal. Everyone is addressed by rank.

### XP: absorbed, not awarded

- XP is the magic a breach denizen leaks when it dies, absorbed by the dungeoneer who is
  there. **Only a kill gives XP.** Deporting gives none. Traps, talk and bypasses give none.
- The automaton absorbs nothing. It is **bound** to its partner and gains a level whenever
  they do (its sheet is a character of its class at the dungeoneer's level).
- **Levels come twice as fast as the SRD:** the thresholds are halved.

| Level | XP | Level | XP | Level | XP | Level | XP |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 6 | 7,000 | 11 | 42,500 | 16 | 97,500 |
| 2 | 150 | 7 | 11,500 | 12 | 50,000 | 17 | 112,500 |
| 3 | 450 | 8 | 17,000 | 13 | 60,000 | 18 | 132,500 |
| 4 | 1,350 | 9 | 24,000 | 14 | 70,000 | 19 | 152,500 |
| 5 | 3,250 | 10 | 32,000 | 15 | 82,500 | 20 | 177,500 |

- A breach holds a full SRD level's worth of denizens, so **killing about half** of a breach
  is a level. Deport the rest, or kill them for a cushion.
- Proficiency bonus and class features go by level as written.

### Death

- **The dungeoneer dies as written:** death saves, three failures, massive damage. There is no
  respawn and no revival. The Company has no *Revivify*; the breaches took the price of it
  long ago (see `setting.md`).
- When the human's dungeoneer dies, the GM finishes the scene from the automaton's point of
  view, writes the death into `chronicle.md` and the wall, runs `month.py end --player-died`,
  and the human plays the **recruit who takes the role**, at the role's new rank, with the
  **same automaton**. The GM builds the recruit from the roster (`month.py show --role`), and
  the human may rename them.
- Dying in a breach **leaves it open**: the denizens are loose in the county next month.
- **The automaton** drops to 0 HP and makes death saves like anyone. Three failures wreck the
  body. Its **core** (a fist-sized thing, 1 kg) survives anything short of disintegration; if
  the core comes home the artificer rebuilds the body over the month's downtime, memory and
  all. A core left in a breach is a downtime move to recover. A lost core is a new automaton,
  which knows nothing of the old one's partners.

### Deportation

- Breach denizens are not all enemies. Every room's group has a **disposition** rolled by the
  generator from its SRD alignment: **Peaceful** (goes home when shown the rift, may help),
  **Wary** (Persuasion or Intimidation DC 15 to go, or it bargains or fights), **Wild** (a
  beast: Animal Handling DC 15 to herd it through, or fight), **Mindless** (oozes, plants,
  constructs, swarms: lure it through with a fitting check at DC 15, or destroy it),
  **Hostile** (will not go).
- **The rift is the door home.** It is in the deepest room. Anything that passes it is gone;
  nothing comes back through. Peaceful denizens find their own way once told; wary and wild
  ones are led or herded, which is a scene with rolls and a chance of a fight on the way.
- A breach **closes** when it holds no living denizen: the rift shuts on its own and the land
  above reverts over a day. Until then it stays open, and if the pair leaves it, it is
  **unhandled**: at month's end the opening collapses and the surviving denizens are loose.
- The Order's doctrine is that a deported denizen is a success and a killed one a necessity.
  The ladder's doctrine is the other way round. Both are true.

### Fights: the GM plays both bodies

- **Every fight is autoplayed.** The GM runs the dungeoneer, the automaton and the denizens,
  rules as written, dice from `roll.py`, positions kept in squares (1 square = 1.5 m; say
  metres in the report, never feet). The human reads the result and plays everything that
  isn't a fight: where to go, whom to talk to, whether to deport or kill, when to rest, when
  to leave.
- **The automaton calls the plan.** It is programmed for economy: it proposes the cheapest
  legal way to win and the pair follows it unless the human has given a **standing order**
  ("never open with fire", "deport anything that will go", "no rests inside"). Standing
  orders live in `state.md` and the GM obeys them in every fight.
- **Cheese is the style.** Scout first, use the room's feature, hold the chokepoint, oil and
  light, Sleep then daggers, kite what's slow, retreat to reset, Short Rest behind a closed
  door. Low HP is never a stop: the pair rallies, drinks, retreats or flees. A death is a
  death.
- **The human can step in** at any time ("I'll play this one") and declare turns; the GM
  then shows the board as positions in words and resolves exactly what's declared.
- **Open table:** every roll shown with its faces, modifiers, total and target. Monster
  stats are open once seen. Hidden is only what the pair can't perceive.

### Narration

This game is for a story, unlike the crunch tables: **prose, brief and plain**, with the
mechanics inside it. One short paragraph for a new place; speech in character; the county and
the chapter house as people and weather, not tables. Fights are reported as below. No mood
for its own sake, no recap of what the human just read.

## Report style

**A fight** is reported as a short block when it's over, or live in a line or two per round
when the human asks to watch. Lead with the headline in a full sentence; say what the
automaton proposed and why, in its voice; let the dice show in plain words; give both bodies'
HP at the end and what the kills were worth.

> **The hold · 4 Pirates (CR 1/8 each) · Low, 200 XP · cleared, deck on fire.**
> Marlow suggested the Cornet "might care to stand in the doorway, sir, while I attend to the
> lamp oil." Two pirates burned on the stair; the other two came through the smoke and one
> of them got a cutlass into Jorund for 7 damage before Sleep put both down. Finished with
> daggers. Jorund 16/23 HP, Marlow 20/20 HP. XP 650 → 850. 20 GP in a sea chest.

**Units on every number:** HP, damage, AC, metres. Monster CR beside every monster name the
first time it appears in a report. **No code blocks and no ASCII maps**; replies are read on a
phone.

**The month's end** is reported as news, from `month.py end`, turned into one line each in the
GM's voice: who died and where, who graduated, who arrived, what's loose. Then the board, and
one question: which way does the human want to spend the month.

## Downtime

The breach takes a few days; the month is mostly downtime. It is played, not skipped, but
lightly: **a scene when the human wants one, a montage when they don't**. Story content is the
GM's, from the news, the county and the roster. The moves below are the handles; they are
Cairn-like in spirit (short, procedural, a roll only where it matters) and the GM can add one
when play wants it.

- **Recover.** Free. Full HP and spells, the automaton repaired or rebuilt, conditions gone.
- **Report.** The Marshal, the board, the chronicler who wants the breach described for the
  record. Where the Company's politics happen.
- **Hunt loose denizens.** The county's only other XP. The GM makes one encounter with
  `gen_breach.py` at the loose group's level (one room of it), places it in the county, and
  the pair deals with it: a kill, a deportation to the nearest open rift, or a bargain. A
  loose group hunted to nothing is struck from the list by hand in `campaign.json`.
- **Go to a settlement.** A day or two there and back; a scene with its people, its ward, what
  the breaches have done to it. Buy anything in `reference/srd/Equipment/` at list price.
- **Spend time with a role.** Another pair, by name from the roster, with its trait. This is
  where the Company becomes people, and what makes the wall hurt.
- **Attend to the automaton.** Talk to it. It remembers every partner it has had and will say
  so if asked. Its protocol can be adjusted here (a standing order changed).
- **Study the breaches.** With the chronicler or a scholar: why they open, why here, what the
  Capital knows. The campaign's long question; the GM keeps its answer in `gm-secrets.md`.
- **Draw from the quartermaster.** At ranks 5, 10 and 15 the Company issues a magic item:
  Uncommon, Rare, Very Rare, the GM's pick from `reference/srd/Magic Items/` to fit the pair.

The human may also **fast-forward**: "montage the month" gets a paragraph and the end of the
month.

## Characters

- **The human's first dungeoneer** is the roster's holder of the chosen rank (default rank 1,
  the newest Recruit; `--player-rank` for another). Random species from the five (Elf, Gnome,
  Human, Orc, Tiefling), random background from the SRD's four, scores rolled 4d6 drop lowest
  and **placed by the class's priority even when low**, Front or Back on a coin, class from
  the side's list with its SRD subclass. `month.py` rolls all of it; the GM writes the sheet
  from `month.py show --role <Role>` by the 2024 creation rules at the role's rank, with the
  class's starting gear. The human names them if they like and gives their pronouns.
- **Front:** Barbarian (Berserker), Fighter (Champion), Paladin (Devotion), Monk (Open Hand),
  Ranger (Hunter), Cleric (Life). **Back:** Wizard (Evoker), Sorcerer (Draconic), Warlock
  (Fiend), Bard (Lore), Rogue (Thief), Druid (Land).
- **The automaton** is a full character of the other side's rolled class, species Automaton
  (`setting.md`), at the dungeoneer's level, scores rolled the same way. It is a person with
  a butler's manner, not gear.
- Levelling: as written, at the halved thresholds. Hit points by the fixed value.

## The GM

- Roll every die with `python3 breach/tools/roll.py` and copy the result. Never invent a
  result. Roll step by step when a result decides the next choice.
- Denizens fight by their stat blocks and their Intelligence; a group that loses half its
  number or its leader checks morale (WIS save DC 10 for the group) and may flee, through
  the rift if it can reach it, which counts as deported.
- The scouts' level is on the board; the true level is in `campaign.json` and the
  generator's heading. Don't tell the human a breach is misjudged; let the first room say it.
- Ask before a big retcon. A fixable error is corrected in the next line with `CORRECTION:`.
- Keep secrets out of the human's files: the true levels, the unexplored rooms, the answer to
  why the breaches open.

## Campaign files

Each campaign is `breach/campaigns/<name>/`:

- `campaign.json`: the script's record: roster, board with true levels and seeds, loose
  denizens, the wall, the graduated, last month's news. The GM's; don't paste it into chat.
- `roster.md`: rendered by the script after `new` and every `end`: the roster, the board as
  the scouts report it, what's loose, the news, the wall. The human's view.
- `county.md`: the settlements, written once by the script; the GM adds the chapter house's
  people and notes by hand. Not rewritten.
- `character.md`: the human's pair: both full sheets, inventory, gold, XP, standing orders'
  history. Rewritten when the role changes hands; the old sheet goes to `chronicle.md`.
- `state.md`: the live state, rewritten after every reply: month, day, place, both bodies' HP
  and resources, the current breach's explored rooms, standing orders, deaths in the role so
  far. A fresh GM resumes from this file alone.
- `chronicle.md`: the Company's record, a few lines per month in the GM's voice, plus the
  full account of each breach and each death. The story file; it is what the human reads
  back.
- `gm-secrets.md`: the current breach (the generator's table plus the GM's marks: explored,
  deported, dead), the chapter house people's secrets, why the breaches open.

After every GM reply, update `state.md`, add to `chronicle.md`, then **commit and push** the
campaign folder. This is a cloud session; the container is wiped when it ends.

## New game

1. Roll a seed (`roll.py 1d1000`) and run
   `python3 breach/tools/month.py new breach/campaigns/<name> --seed N`. It prints the human's
   pair. Read `setting.md`.
2. Write `character.md` for the pair by the creation rules, `county.md`'s people (five or
   six, one line each), `gm-secrets.md` with the campaign's answer to the breaches and the
   first breach from the board's seed:
   `python3 breach/tools/gen_breach.py --seed S --level L --reported R` (the `board` verb
   prints the line to run). Write `state.md` and an empty `chronicle.md`.
3. Open with the chapter house on dispatch day: the Company at the board, the Marshal
   reading it, the human's name called, the automaton at their elbow. Then the road.
4. Play the breach by the rules above. Back home, play the downtime. End the month with
   `python3 breach/tools/month.py end breach/campaigns/<name>` (add `--player-left-open` if
   the breach wasn't closed, `--player-died` if it came to that), report the news, show the
   board, and begin again.
5. A fresh GM resuming reads `state.md`, `character.md`, `roster.md`, `gm-secrets.md` and the
   end of `chronicle.md`.

## Dials, for later

Things built as guesses, in one place so they're easy to find: the halved XP table (above);
breaches per month, `1d4+1` unhandled beyond the twenty, their levels the lower of two d20
(`month.py`, `roll_board`); misjudged breaches one in six; deaths `1d2` a month; loose
denizens settle on a 1 to 3; room difficulty weights and the two-character budget
(`gen_breach.py`); low-level breaches of two rooms being thin; the rank-versus-level gap for
a dungeoneer who deports.
