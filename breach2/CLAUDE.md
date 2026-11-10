# Breach 2

An endless industrial city where pieces of other worlds lodge inside buildings, with whoever
was standing on them. The Board of Wards' **Division** in one district keeps ten dungeoneers, each paired with
an automaton, and never has enough. Every dawn the dice say which breaches opened; the one
of your grade is yours. The human plays **one seat** in that Division: not a person but a
call sign, held by whoever is alive to hold it. When the holder dies, the human plays the
replacement. The story is the Division's.

Rules: D&D 2024 (SRD 5.2.1, `reference/srd/`), rules as written, with the house rules below.
Claude is the GM, and **plays every fight for both bodies**; the human plays the dungeoneer
everywhere else. Paths are relative to the repo root, where the session runs. The city, the
Board, the masts and the automatons are in `breach2/setting.md`; read it whole before the
first game.

**Keep it lean.** These rules are the constraints; the rest is the GM's judgement. Don't add
a procedure in play where a ruling will do.

## Folder layout

```
breach2/
  CLAUDE.md            this file: how to run the game
  setting.md           the city, breaches, masts, the Board, automatons (with the species block)
  tools/roll.py        dice roller (advantage, disadvantage, keep highest/lowest)
  tools/day.py         the Division's day: seats, ledger, spills, deaths, arrivals, review
  tools/gen_breach.py  one breach as a dungeon for a pair, with each group's rolled disposition
  campaigns/<name>/    one folder per campaign (see Campaign files)
```

## Rules source

| Need | File |
|---|---|
| A class, its features and subclass | `reference/srd/Classes/<Class>/<Class>.md` |
| A spell | `reference/srd/Spells/<Cantrip or Level N>/<Name>.md`; lists in `Classes/<Class>/` |
| Species (Elf, Gnome, Human, Orc, Tiefling) | `reference/srd/Species/<Name>.md`; the Automaton is in `breach2/setting.md` |
| Backgrounds (Acolyte, Criminal, Sage, Soldier) | `reference/srd/Backgrounds/Character Origins.md` |
| Creating and levelling a character | `reference/srd/Character Creation/` |
| Combat, actions, cover, grid | `reference/srd/Playing/Combat.md`, `Actions.md` |
| Checks, saves, advantage; damage, dying, rests | `reference/srd/Playing/D20 Tests.md`, `Damage and Healing.md` |
| Conditions and rules terms | `reference/srd/Glossary/` |
| Encounter budgets | `reference/srd/Gameplay/Combat Encounters.md` |
| A monster | `reference/srd/Monsters/<Name>.md`; `reference/srd/Monsters by CR.md` |
| Equipment and prices | `reference/srd/Equipment/` |
| Magic items (relics) | `reference/srd/Magic Items/<Rarity>/<Name>.md` |

Never read a big file whole; find the file by name and `grep -n`.

## The loop

A day is one turn. **Dawn**: `day.py dawn` rolls the day; at the station the ledger is read
out. **Out**: the legs to the precinct, an encounter die each. **The breach**: room by room
until it's closed, left, or the dungeoneer is dead. **Report**: back at the station, or by a
call. Then a Long Rest ends the day, and the next dawn is rolled.

There is no fixed month. Time is the resource: every dawn can put a new breach on the pair's
desk, and every dawn an open one can spill.

## House rules

These replace the SRD where they differ.

### The day

- **Every dawn, `day.py dawn` rolls a d20 for each grade, 1 to 10. On a 1, a breach of that
  grade opens** (about one and a half a month per grade). It lands in the band its grade
  belongs to: the Core (1 to 3), the Fringe (4 to 7), the Static (8 to 10).
- A breach is **assigned** to the seat of its grade if that officer is alive and free. If
  not, it waits on the ledger with no one, and spills.
- **Spill.** Every dawn, each open breach rolls a d6; on a 1 its strongest remaining group
  walks out and is **loose** in the precinct. For the human's breach the GM picks the group
  and marks its room empty. This is the price of a Long Rest with a breach half done.
- **A grade is two levels**: grade N is levels 2N−1 and 2N. The Reader gives only the grade,
  so "a grade 3" is level 5 or 6, and one reading in six is a whole grade too low.
- **The ledger is known only at the station or by a call.** A call from the field costs
  10 GP × the pair's grade and tells the pair the ledger as it stands. Without one, the
  pair learns the morning's news when it walks in. The GM runs `dawn` every day regardless
  and keeps what the pair hasn't heard to itself; `day.py report` rewrites `division.md`
  when they do hear.
- **Assigned work comes first.** The pair is expected to report after a breach, not wander.
  Closing a breach that isn't theirs is misappropriation (`setting.md`): the GM plays the
  consequences, there is no rule for them. The Director may also send the pair to any
  breach, over or under grade (`day.py take`).

### The ladder

- Ten **seats**, one per grade, each with an animal call sign. **Every 60 days is review
  day: every seat moves up a grade.** The grade-10 holder is called to Head Office and that
  seat gets a level 1 Probationer.
- The other nine are at one of their grade's two levels. **The human's holder is at the
  level their XP gives** (the halved table below).
- **The quota.** The Board does not order anyone killed. It expects growth: by each review
  an officer should have reached the first level of the grade they are moving into, two
  levels in sixty days. One who hasn't is **behind**: the auditor writes it down, the
  Director hears about it, and the seat moves up and is sent to its new grade's breaches
  all the same. What follows from being behind is the GM's to play, not a rule.
- A dead officer's seat is **empty for 2d6 days**, then filled by a transfer at the seat's
  grade. Breaches of that grade pile up meanwhile. This, and pairs that withdraw, is what
  keeps the Division undermanned.

### XP: absorbed, not awarded

- XP is the magic a breach denizen leaks when it dies, absorbed by the dungeoneer who is
  there. **Only a kill gives XP.** Sending a denizen home gives none. Traps, talk and bypasses give
  none.
- The automaton absorbs nothing. It is **bound** and gains a level whenever its partner does.
- **Levels come twice as fast as the SRD:** the thresholds are halved.

| Level | XP | Level | XP | Level | XP | Level | XP |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 6 | 7,000 | 11 | 42,500 | 16 | 97,500 |
| 2 | 150 | 7 | 11,500 | 12 | 50,000 | 17 | 112,500 |
| 3 | 450 | 8 | 17,000 | 13 | 60,000 | 18 | 132,500 |
| 4 | 1,350 | 9 | 24,000 | 14 | 70,000 | 19 | 152,500 |
| 5 | 3,250 | 10 | 32,000 | 15 | 82,500 | 20 | 177,500 |

- A breach holds a full SRD level's worth of denizens, so **killing about half** of one is a
  level, and about half its groups will fight whatever is said to them. A grade is two
  levels and brings about three breaches before the next review, some reviews only one.

### The breach

- **Few rooms, each a real fight.** `gen_breach.py` builds three to six rooms, nearly every
  group Moderate or High for two characters, the anchor always High. No filler fights.
- **Any SRD monster can turn up.** A group is as many of its kind as fill the room's budget,
  up to ten: often one or two strong creatures, sometimes a crowd of weak ones. Run a crowd
  briskly: one initiative, attacks rolled together.
- Every group has a **disposition**, rolled by the generator. Evil kinds are Hostile; every
  other group rolls a d6: 1 or 2 Hostile, 3 to 5 Neutral, 6 Willing.
  - **Hostile:** fights, and will not be talked round.
  - **Neutral:** has no quarrel yet, and no wish to go anywhere. From inside, this is its
    home and the pair are armed strangers. Whether it can be convinced, and by what, is the
    **GM's discretion**, played from what the creature is and how clever: a scene, not one
    roll, and not a quest or a price by default. A beast or a mindless thing isn't argued
    with; it is calmed, penned, lured or left alone.
  - **Willing:** knows it is lost, wants to go home, may help.
- **The gizmo.** The automaton carries it: a 25 kg case that folds out, at the **anchor**
  (the deepest room) and nowhere else, into the machine that works the piece loose. Setting
  it up and running it takes **10 minutes in peace**: the automaton does nothing else, and
  if he is hit or leaves it the run starts over. The dungeoneer guards alone. The whole
  breach feels it start, and every Hostile group still alive inside comes to the anchor.
- **Who goes home.** When the run ends the piece goes back, and with it every denizen **of
  that piece** that is **within 6 m of the gizmo and has kept still for the last minute**. So going home is
  something a creature does, not something done to it; one that won't stand still can only
  be sent bound or senseless and laid there, which is allowed and is work.
- **The rest stay.** The breach is **closed** and the building is itself again in a day. Any
  denizen alive in it and not sent is left standing in a cellar or a loft, and is **loose**
  in the precinct. Tell the script (`day.py close ID`, with `--left N` for N groups left
  behind). An officer who closes a breach and leaves half of it on the street has closed
  it; the precinct and the Director will have views.
- A wrecked automaton runs no gizmo: the breach stays open until he is rebuilt.
- **A breach's contents are never settled.** The generator's table is what was there when
  the pair walked in. A lodged piece keeps arriving, and loose things wander in from the
  street; the pair never knows a breach is empty, only that it is quiet.
- **The encounter die.** Roll a d6: for each leg of travel; for each Short Rest inside a
  breach; the first time in a fight that something is loud (a gunshot, Thunder damage, an
  explosion); and when the gizmo starts. **On a 1, a Hostile encounter**, always possible,
  whatever has been cleared. Inside a breach it is a **new group**: `gen_breach.py --seed S
  --level L --encounter N` (the breach's seed and level, N counting up) gives more of the
  breach's kind or something else. In the street it is the precinct's loose denizens if the
  list has any, at whatever level they are; if not, a stray nobody has counted, at the
  pair's level (`--encounter N --street`, any seed). Its kills give XP like any other.
- **No Long Rest inside a breach.** The pair leaves to sleep, and that is a dawn: the breach
  may spill, the ledger may grow.

### Relics and gear

- **A closed breach leaves one relic**: a magic item from `reference/srd/Magic Items/`, the
  GM's pick, dressed as a thing of that breach's reality. Rarity is capped by the breach's
  grade: Uncommon at grades 1 and 2, Rare at 3 to 5, Very Rare at 6 to 8, Legendary at 9 and
  10. Pick below the cap more often than at it. A breach left open, or closed by someone
  else, leaves the pair nothing.
- A relic **bonds** to whichever of the pair takes it up. It can't be given, sold or bought,
  and it is dead metal when its holder dies; the automaton's relics stay with the automaton.
  Attunement is as written. The GM may also put a consumable in a room where it fits.
- **Shops sell only mundane things:** anything in `reference/srd/Equipment/` at list price.
- **Guns are ordinary.** The Pistol and Musket are in the SRD's weapon table; anyone with
  martial weapon proficiency uses them as written. At creation a character may swap a
  starting Shortbow or Light Crossbow for a Pistol, or a Longbow or Heavy Crossbow for a
  Musket. A gun is loud (the encounter die); a bow is not.

### Death

- **The dungeoneer dies as written:** death saves, three failures, massive damage. No
  respawn, no revival; the Board has no *Revivify*.
- When the human's dungeoneer dies, the GM finishes the scene from the automaton's point of
  view, writes the death into `chronicle.md`, and runs `day.py dawn --player-died`. The seat
  is empty for 2d6 days: the GM runs those dawns as news, briefly, so the human sees what
  the gap cost. Then the human plays the **transfer who takes the seat**, at the seat's
  grade and the level the script gives, with the **same automaton**. Relics bonded to the
  dead are gone. The human may rename the newcomer.
- Dying in a breach leaves it open and unassigned.
- **The automaton** drops to 0 HP and makes death saves like anyone. Three failures wreck the
  body. Its **core** (fist-sized, 1 kg) survives anything short of disintegration; if the
  core comes home the fitter rebuilds the body in 1d6+1 days, memory and all, and the pair
  is off the street meanwhile. A lost core is a new automaton, which knows nothing of the
  old one's partners.

### Fights: the GM plays both bodies

- **Every fight is autoplayed.** The GM runs the dungeoneer, the automaton and the denizens,
  rules as written, dice from `roll.py`, positions kept in squares (1 square = 1.5 m; say
  metres in the report, never feet). The human reads the result and plays everything that
  isn't a fight: where to go, whom to talk to, whether to send home or kill, when to rest, when
  to leave.
- **The automaton calls the plan.** He is programmed for economy: he proposes the cheapest
  legal way to win and the pair follows it unless the human has given a **standing order**
  ("never open with fire", "send home anything that will go", "no guns indoors"). Standing
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

This game is for a story: **prose, brief and plain**, with the mechanics inside it. One
short paragraph for a new place; speech in character; the district and the station as people,
soot and weather, not tables. No mood for its own sake, no recap of what the human just read.

## Report style

**A fight** is reported as a short block when it's over, or live in a line or two per round
when the human asks to watch. Lead with the headline in a full sentence; say what the
automaton proposed and why, in his voice; let the dice show in plain words; give both bodies'
HP at the end and what the kills were worth.

> **The hold · 4 Pirates (CR 1 each) · High, 800 XP · cleared, deck on fire.**
> Marlow suggested the Constable "might care to stand in the doorway, sir, while I attend to
> the lamp oil." Two pirates burned on the stair; the other two came through the smoke and
> one of them got a cutlass into Arthur for 7 damage before Sleep put both down. Finished
> with daggers. Arthur 16/23 HP, Marlow 20/20 HP. XP 650 → 1,450. 80 GP in a sea chest.

**Units on every number:** HP, damage, AC, metres. Monster CR beside every monster name the
first time it appears in a report. **No code blocks and no ASCII maps**; replies are read on a
phone.

**The dawn** is reported as news, from `day.py dawn`, a line each in the GM's voice, and only
what the pair is in a position to know.

## Between breaches

Most days the ledger has nothing for the pair. Such a day is a scene if the human wants one
and a line if not; **"skip to the next breach"** runs the dawns as a paragraph of news. A day
spent on one of these is still a day, and its dawn is still rolled.

- **Hunt loose denizens.** One encounter: a room of `gen_breach.py` at the loose group's
  level, in its precinct. A kill or a bargain. A denizen goes home only with its own
  piece: a group spilled from a breach that is still open can be walked back to its anchor,
  and one whose breach is closed is here for good. Dealt with, it comes off the list (`day.py clear N`).
- **Walk a precinct.** Its people, what the breaches have done to it, who is asking why
  the breach on their street has no one.
- **Spend time with a seat**, by name from the roster, with its trait.
- **Attend to the automaton.** He remembers every partner. A standing order changes here.
- **Study the breaches**, with the Reader: the campaign's long question.

## Characters

- **The human's first dungeoneer** is the holder of the chosen grade (default grade 1, the
  Probationer; `--player-grade` for another). `day.py` rolls species, background, scores
  (4d6 drop lowest, **placed by the class's priority even when low**), Front or Back, and
  class. The GM writes the sheet from `day.py show --role <Seat>` by the 2024 creation
  rules, with the class's starting gear. The dungeoneer is a man or a woman, as rolled (never
  "they"); the human may rename them.
- **Front:** Barbarian (Berserker), Fighter (Champion), Paladin (Devotion), Monk (Open Hand),
  Ranger (Hunter), Cleric (Life). **Back:** Wizard (Evoker), Sorcerer (Draconic), Warlock
  (Fiend), Bard (Lore), Rogue (Thief), Druid (Land).
- **The automaton** is a full character of the other side's rolled class, species Automaton
  (`setting.md`), at the dungeoneer's level. He carries the call box. He is a person with a
  butler's manner, not gear, and always "he".
- Levelling: as written, at the halved thresholds. Hit points by the fixed value.
- **Names are plain English names** (`setting.md`), for everyone the GM invents too.

## The GM

- Roll every die with `python3 breach2/tools/roll.py` and copy the result. Never invent a
  result. Roll step by step when a result decides the next choice.
- **No roll without a consequence.** Call for a check only when failing it would change
  something: a cost, a danger, a door that stays shut, a different scene. If a failure
  would leave things as they were, or the pair could simply try again, don't roll: say what
  happens. The same goes for knowledge: if the story needs the pair to know it, they know it.
- Denizens fight by their stat blocks and their Intelligence; a group that loses half its
  number or its leader checks morale (WIS save DC 10 for the group) and may flee, deeper in
  or out to the street (loose).
- The Reader's grade is on the ledger; the true level is in `campaign.json` and the
  generator's heading. Don't tell the human a breach is misread; let the first room say it.
- The Director's choices are the GM's: who is sent over their grade, which precinct waits.
  Make them defensible and sometimes wrong.
- Ask before a big retcon. A fixable error is corrected in the next line with `CORRECTION:`.
- Keep secrets out of the human's files: true levels, unexplored rooms, unheard news, the
  answer to why the breaches open.

## Campaign files

Each campaign is `breach2/campaigns/<name>/`:

- `campaign.json`: the script's record: seats, ledger with true levels and seeds, loose
  denizens, the wall. The GM's; don't paste it into chat.
- `division.md`: rendered by `day.py report`: the seats, the ledger, what's loose, the news,
  the wall, as of the pair's last report. The human's view.
- `district.md`: the nine precincts, written once by the script; the GM adds the station's
  people and notes by hand.
- `character.md`: the human's pair: both full sheets, relics and who they're bonded to,
  inventory, gold, XP. Rewritten when the seat changes hands; the old sheet goes to
  `chronicle.md`.
- `state.md`: the live state, rewritten after every reply: day, place, both bodies' HP and
  resources, the current breach's explored rooms, standing orders, what the pair hasn't
  heard yet. A fresh GM resumes from this file alone.
- `chronicle.md`: the Division's record in the GM's voice: each breach, each death, a line
  for the days between. The story file.
- `gm-secrets.md`: the current breach (the generator's table plus the GM's marks: explored,
  convinced, sent home, dead, spilled, left behind), the station people's secrets, why the breaches open.

After every GM reply, update `state.md`, add to `chronicle.md`, then **commit and push** the
campaign folder. This is a cloud session; the container is wiped when it ends.

## New game

1. Roll a seed (`roll.py 1d1000`) and run
   `python3 breach2/tools/day.py new breach2/campaigns/<name> --seed N`. It prints the
   human's pair and their first breach. Read `setting.md`.
2. Write `character.md`, `district.md`'s people (five or six, one line each),
   `gm-secrets.md` with the campaign's answer to the breaches and the first breach (`day.py
   ledger` prints the `gen_breach.py` line), `state.md` and an empty `chronicle.md`.
3. Open at the station at dawn: the ledger read out, the human's seat called, the automaton
   at their elbow with the call box. Then the street.
4. Play by the rules above. `day.py close ID` when a breach closes, `day.py dawn` after each
   Long Rest, `day.py report` when the pair hears the ledger.
5. A fresh GM resuming reads `state.md`, `character.md`, `division.md`, `gm-secrets.md` and
   the end of `chronicle.md`.

## Dials

Guesses, in one place. The script's are constants at the top of `day.py`: the breach die
(d20), the spill die (d6) and three spills to empty an unattended breach, the misread (one
in six), review every 60 days, the other pairs' death (1 in 20) and withdrawal (3 in 20) per
breach, the 2d6-day vacancy. In `gen_breach.py`: three rooms minimum, Moderate and High,
groups of up to ten, crowds made rarer, and `HOSTILE_ON` (a group that isn't Evil is Hostile
on a d6 of 1 or 2: about 45% of groups fight at level 1, 60% from level 5; set it to 1 for
30% and 50%). Here: the halved XP table, the call's price, the relic rarity caps, the encounter
die and the even odds of what it brings, the gizmo's 10 minutes and 6 m. If the pair outruns its grade, un-halve the XP table first; if the Division isn't
stretched enough, shorten the breach die.
