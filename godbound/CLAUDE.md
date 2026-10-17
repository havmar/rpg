# Godbound

*Godbound: A Game of Divine Heroes* (free edition) by Kevin Crawford, Sine Nomine Publishing, 2016.
The PCs are newly awakened demigods who wield Words of Creation in the broken world of Arcem.
Follow the general rules in `../CLAUDE.md` too. This file only covers Godbound.

## The rulebook: `Godbound.md`

This is a pandoc conversion of the EPUB. It has no Markdown headings: section titles appear
right after `{#...idTextAnchorNNN}` tags, and text is wrapped across lines. Image links point
to files that aren't in the repo. Search it with `grep -n`, then read the line range with
`sed -n 'START,ENDp'`. Never load the whole file (about 25,000 lines).

Section index (line numbers in `Godbound.md`; if the file changes, grep the title instead):

| Line | Section | Line | Section |
|---:|---|---:|---|
| 55 | New Gods Awaken (intro, setting pitch) | 7301 | **A Gazetteer of Arcem** |
| 391 | **Character Creation** | 7516 | The Nature of the Universe, Heaven, Hell |
| 480 | Rolling Attributes, saves | 7781 | The Nations (Ancalia 7946 … Vissio 9667) |
| 608 | Determining Facts | 9780 | Ways of the Realm (peoples, tech, religion) |
| 673 | Choosing Words and Gifts | 10443 | A Player's Guide to the Realm |
| 813 | Final Touches (HP, AC, Effort, Influence) | 10566 | **Running the World** |
| 887 | Creating Your Hero (step-by-step summary) | 10660 | Changing the World (Influence, Dominion) |
| 1116 | Wealth and Equipment, Armor 1155, Weapons 1187 | 11630 | Creating Adventures |
| 1414 | **The Rules of the Game** | 12148 | Creating a Court |
| 1512 | Attribute Checks | 12870 | Creating a Ruin |
| 1572 | Advancement | 13971 | Creating Challenges |
| 1710 | Combat | 14774 | Factions, Nations, and Organizations |
| 2034 | Saving Throws | 15841 | **Foes of Heaven** (bestiary) |
| 2123 | **Quick Rule Reference** (best one-page summary) | 15975 | Judging Appropriate Opposition |
| 2260 | **Divine Powers** | 16006 | Reactions, Parleying 16006, Morale 16054 |
| 2526 | Universal Gifts | 16214 | Angels, Eldritch 16446, Made Gods 16584 |
| 2586 | What Can Miracles Do? | 16871 | Mobs (stat blocks 17007–17112) |
| 2875 | The Words: Alacrity … Wealth (to 5808) | 17161 | Mortal Foes, Parasite Gods 17392 |
| 5809 | Magic and Spellcasting (low magic traditions) | 17675 | Relicts, Undead 18515, Uncreated 18385 |
| 6606 | Theurgic Invocations | 18653 | Creating New Foes |
| 19346 | **Treasures Beyond Price** (artifacts 19729) | 24035 | Topic Index, Gift Index 24440 |

Word sections: Alacrity 2875, Apotheosis 2978, Artifice 3114, Beasts 3234, Bow 3356,
Command 3473, Death 3590, Deception 3699, Earth 3808, Endurance 3916, Fertility 4020,
Fire 4139, Health 4245, Journeying 4352, Knowledge 4454, Luck 4558, Might 4659, Night 4769,
Passion 4872, Sea 4996, Sky 5114, Sorcery 5219, Sun 5338, Sword 5447, Time 5556, Wealth 5670.

## Quick character creation (about 10 minutes)

1. **Attributes:** assign 16, 14, 13, 13, 10, 8, or roll `4d6kh3` six times and assign.
   Modifiers: 3 = −3, 4–5 = −2, 6–8 = −1, 9–12 = 0, 13–15 = +1, 16–17 = +2, 18 = +3.
2. **Three Facts:** origin, former profession, and a relationship with a group. A relevant
   Fact gives +4 on attribute checks.
3. **Three Words.** Each grants a free special ability (read the start of the Word's section).
4. **Gifts:** 6 points. Lesser gift = 1, greater gift = 2, binding a 4th Word = 3.
5. **Final numbers:** HP = 8 + Con mod. AC = 9 − Dex mod (lower is better). Effort = 2.
   Influence = 2. Attack bonus = level + Str/Dex mod. Fray die = 1d8. Saves: Hardiness,
   Evasion and Spirit each = 15 − the better of (Str/Con), (Dex/Int), (Wis/Cha) mods, and
   improve by 1 per level after 1st.
6. **A goal**: what the hero wants to change in the world.

For a fast game the GM can offer a pre-built PC: three Words, two or three gifts picked for
fun, and three one-line Facts.

## Core rules cheat sheet

- **Attribute check:** d20 ≥ 21 − attribute. +4 with a relevant Fact, −4 to −8 for extreme
  feats. A failure means a complication, not a flat fail. Tasks within a hero's Words or Facts
  just succeed.
- **Saving throw:** d20 ≥ save score. A failed save can be turned into a success by
  committing 1 Effort for the day.
- **Effort:** commit it to power gifts (for the scene, the day, or as long as it's sustained).
  A **miracle** (any feat within a Word that isn't a known gift) costs 1 Effort for the day.
  All Effort comes back each morning.
- **Combat:** PCs act first unless ambushed. Each turn: move 9 m plus one action.
  To hit: d20 + attack bonus + target AC ≥ 20.
  **Damage chart:** each die read separately (1 or less = 0, 2–5 = 1, 6–9 = 2, 10+ = 4
  damage), modifier on one die. Use `python3 ../tools/roll.py 1d8+2 --gb`.
  NPCs lose hit dice, PCs lose HP. Excess damage from a kill overflows to another foe with the
  same or worse AC.
- **Fray die:** each round, for free, roll 1d8 on the damage chart against one foe with hit
  dice ≤ the PC's level.
- **Mobs** are treated as single creatures (see Mobs, line 16871).

## Running a quick one-shot

- Use Arcem, starting PCs at level 1, and open in the middle of a crisis: the heroes have just
  awakened and something needs a god *now*.
- Godbound PCs are very powerful. Mortal threats should be crowds, dilemmas and consequences
  rather than straight fights. Save real fights for a parasite god, rogue angel, Uncreated
  horror, or rival Godbound (see Judging Appropriate Opposition, line 15975).
- A one-shot is usually three or four scenes: hook, complication, confrontation, and the
  aftermath where the PCs change something with their power.
- Hook ideas: a drowned town's parasite god demands children as tribute. A Patrian legion
  marches on a village the PCs grew up in. A broken celestial engine is turning a valley's
  seasons to permanent winter. An angel claims one PC's soul belongs to Heaven's ledger.

## Campaigns

Campaign folders go in `campaigns/<name>/`, with the files described in `../CLAUDE.md`.
