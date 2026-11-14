# D&D SRD 5.2.1 (reference)

The System Reference Document 5.2.1 (the 2024 rules) as markdown, one file per entry, for
the GM to consult. It is reference only and belongs to no game: a game uses it when its own
`CLAUDE.md` says so, and that game's rules win where they differ.

- Source: https://github.com/your5e/5e-srd-markdown, the `dnd/521/markdown/` folder at
  commit `f1f5060fd975aa2ffc3e4b336560ded479934d80`, unchanged. `LEGAL.md` is the SRD's
  own legal page, from that repo's whole-document file.
- License: CC-BY-4.0. This work includes material from the System Reference Document
  5.2.1 ("SRD 5.2.1") by Wizards of the Coast LLC, available at
  https://www.dndbeyond.com/srd. The SRD 5.2.1 is licensed under the Creative Commons
  Attribution 4.0 International License, available at
  https://creativecommons.org/licenses/by/4.0/legalcode.

## Finding things

Every entry is its own file, named for its title, so find it by name first
(`Monsters/Goblin Warrior.md`, `Spells/Level 1/Magic Missile.md`), and Grep across a
folder for anything else (`Grapple`, `Darkvision`, `Poisoned`).

| Folder | Contents |
| --- | --- |
| `Monsters/` | 330 stat blocks, animals included. [Monsters by CR](Monsters%20by%20CR.md) lists them by challenge rating, with type, AC and HP; [Monsters by Setting](Monsters%20by%20Setting.md) sorts them into 20 settings whose monsters can share a place (hand-made, not rewritten by a refresh) |
| `Gameplay/` | The GM's toolbox: combat encounters, traps, poison, curses, environment, fear, travel pace, monster rules |
| `Glossary/` | The rules glossary: conditions, actions, and every rules term |
| `Playing/` | Playing the game: D20 tests, actions, combat, damage and healing, exploration, social interaction |
| `Spells/` | Spells, by level (`Cantrip`, `Level 1` to `Level 9`); `Spells.md` is the rules for casting them |
| `Magic Items/` | Magic items, by rarity |
| `Equipment/` | Weapons, armour, gear, tools, mounts and vehicles |
| `Services/` | Lifestyle, food, lodging, hirelings, spellcasting services |
| `Classes/`, `Species/`, `Backgrounds/`, `Feats/`, `Character Creation/` | Character options |

Distances are in feet, as printed.

## Refreshing

Clone that repo with `--depth 1`, replace these folders with its `dnd/521/markdown/`
ones (keeping this README and `LEGAL.md`), then run `python3 reference/index_srd.py` to
rewrite the CR table.
