# Eclipse Phase

Eclipse Phase Second Edition: transhuman horror and conspiracy, ten years after the Fall.
Minds are software that can be backed up, copied and resleeved into new bodies (morphs);
Earth is lost to the TITANs; the player characters are usually sentinels of Firewall,
quietly fighting the existential risks that could finish transhumanity off.

Rules: Eclipse Phase 2e as written (errata 1.4), from `eclipse-phase/rulebook/`. Paths are
relative to the repo root, where the session runs.

**Not yet decided:** who is GM and who plays, the campaign premise, campaign file layout and
house rules. Settle these with the human before the first session and write them here.

## Folder layout

```
eclipse-phase/
  CLAUDE.md          this file
  rulebook/          the core book and three supplements as Markdown (CC BY-NC-SA 4.0)
  rulebook/README.md source, licence, what is where, how to refresh
  tools/roll.py      dice roller: d100 tests with 33/66 superiors and criticals, opposed tests, dice sums
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

## Licence

The rulebook text is CC BY-NC-SA 4.0 (Posthuman Studios; Markdown edition by Luiz Borges
Gomide). Anything made from it in this folder stays non-commercial, credited and under the
same licence.
