# Eclipse Phase

Eclipse Phase Second Edition: transhuman horror and conspiracy, ten years after the Fall.
Minds are software that can be backed up, copied and resleeved into new bodies (morphs);
Earth is lost to the TITANs; the player characters are usually sentinels of Firewall,
quietly fighting the existential risks that could finish transhumanity off.

Rules: Eclipse Phase 2e as written (errata 1.4), from `eclipse-phase/rulebook/`. Paths are
relative to the repo root, where the session runs.

## The table

A party of two. The human plays one character; Claude is the GM and also plays the other
character, keeping the two roles apart: the GM knows what the character doesn't, and the
character acts only on what it knows. The world is a sandbox and is not scaled to the pair:
a place is as dangerous as it is, and they choose where to go.

**Not yet decided:** the campaign premise (the default is a Firewall cell), campaign file
layout and house rules beyond those below. Settle them with the human and write them here.
This is a first try at a foreign game: play loosely, and turn what works into rules here
after a few sessions.

## Folder layout

```
eclipse-phase/
  CLAUDE.md          this file
  rulebook/          the core book and three supplements as Markdown (CC BY-NC-SA 4.0)
  rulebook/README.md source, licence, what is where, how to refresh
  threats.md         the opponent catalogue: book threats with stat locations, plus house-made people
  tools/roll.py      dice roller: d100 tests with 33/66 superiors and criticals, opposed tests, dice sums
  tools/threat.py    rolls a scene's opponents from threats.md
  campaigns/<name>/  one folder per campaign, once there is one
```

## Rules source

The rulebook is large. Never read it whole: find the file in `rulebook/SUMMARY.md` (the table
of contents) or the chapter table in `rulebook/README.md`, then `grep -n`.

| Need | File |
|---|---|
| The whole system on a few pages | `rulebook/19/06-rules-primmer.md` |
| Tests, modifiers, 33/66, criticals | `rulebook/03/01-how-to-play.md`, `03/02-types-of-tests.md` |
| Actions, time, initiative, pools | `rulebook/03/03-actions-and-time.md`, `03/04-initiative-order-of-actions.md`, `03/05-pools.md` |
| Character creation | `rulebook/04/02-character-creation-overview.md`, then the step files `04/04`–`04/16` |
| Skills | `rulebook/04/18-skills.md`, `04/19-active-skill-list.md`, `04/20-know-skills.md` |
| Morphs | `rulebook/04/21-morphs.md` … `04/26-infomorphs.md`, `19/05-complete-list-of-morphs.md` |
| Combat, damage, healing, stress | `rulebook/12/` |
| Hacking and the mesh | `rulebook/13/`, `19/04-complete-list-of-mesh-actions.md` |
| Psi | `rulebook/14/` |
| Ware, nanotech, gear | `rulebook/15/`, `rulebook/16/` |
| Running the game | `rulebook/17/` |
| NPCs, threats, Exsurgents, TITANs | `rulebook/18/` (NPC rules: `18/05-npc-and-threat-rules.md`) |
| Terms | `rulebook/19/01-glossary.md` |
| Setting | `rulebook/06/`–`11/` |

## Dice

`python3 eclipse-phase/tools/roll.py` with no arguments prints its usage. `test TARGET [MOD]`
rolls a skill test and reports success or failure, superior results and criticals;
`--default` drops critical successes when defaulting to an aptitude; `opposed A B` settles an
opposed test; `2d10+3` sums dice. `--seed N` makes a roll repeatable. Roll in the open and
show the output line.

## Opponents

The GM does not choose who the pair fights. When a scene needs opponents, whether a fight
is likely or they are simply there, roll them: `python3 eclipse-phase/tools/threat.py PLACE`,
with PLACE one of `civilised`, `fringe`, `ruins`, `exoplanet`, `mesh` (defined in
`threats.md`). Show the output. Usually the result is native to the place; on a 1 in 4 it is
from anywhere, and the story must explain how it got there. That explanation is often the
adventure: an exsurgent in a city is an outbreak, which is Firewall's business.

- The tool already scales numbers for two characters (halved; red and ultraviolet alone).
  Adjust only as `rulebook/18/05-npc-and-threat-rules.md` allows (Tailoring Challenges:
  behaviour, cover, reinforcements), not by swapping the opponent.
- An opponent need not be met head-on. What the pair does about it, fight, sneak, talk,
  hack or flee, is theirs to choose; the colour says how wise a straight fight would be.
- Book entries: read the stat block at the line given. House entries (people, rogue AI):
  build them at the rolled colour from the 18/05 benchmarks, then note the stats in the
  campaign files so they stay the same if met again.
- Add to `threats.md` when the book or play gives new opponents; keep its columns.

## Licence

The rulebook text is CC BY-NC-SA 4.0 (Posthuman Studios; Markdown edition by Luiz Borges
Gomide). Anything made from it in this folder stays non-commercial, credited and under the
same licence.
