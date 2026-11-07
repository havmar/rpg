# 13th Age SRD (rules for this game)

The 13th Age System Reference Document (the Archmage Engine: the core book, the *13th Age
Bestiary* and *13 True Ways*) as markdown, one file per entry, for the GM to consult. This
is first-edition 13th Age.

- Source: https://github.com/Obsidian-TTRPG-Community/13th-Age-SRD-Markdown, its
  `Compendium/13A/` folder at commit `f52570de87ebe9ba52f23e68c5112b00f3db38d1`
  (2023-08-27), shallow-cloned. The markdown is unchanged. Images were left out (icon
  portraits, the Dragon Empire map, the monster key picture), and so were the Obsidian
  vault settings.
- License: `LICENSE.md` is the repo's own: the OGL 1.0a and Pelgrane Press's Archmage
  Engine terms for the rules text; proper names (the icons, places, characters) are
  Product Identity. Fine for play here; mind it before publishing anything.

## Finding things

Files are named for their entry in Kebab-Case, so find one by name first
(`Bestiary/Humanoid/Goblin/Goblin-Grunt.md`, `Classes/Wizard.md`) and grep for the rest
(`grep -rn "Disengag" 13th-age/srd/Combat-Rules`). Never read a big file whole: a class file
is 300 to 2,500 lines, so grep its headings (`grep -n '^#' 13th-age/srd/Classes/Wizard.md`).

| Folder | Contents |
| --- | --- |
| `Combat-Rules/` | The fight: sequence, initiative, the escalation die, actions, position (engaged, nearby, far away), attacks, crits, damage, recoveries, rests, death, conditions |
| `Character-Rules/` | Abilities, backgrounds and skill checks, icon relationships, One Unique Thing, combat stats, feats, gear and prices |
| `Classes/` | 15 classes, each one file with its features, talents, powers or spells and feats |
| `Spells/` | A few shared spells (racial and multiclass); class spells are in the class files |
| `Races/` | 13 races and racial feats |
| `Multiclassing/` | Multiclass rules and feats |
| `Bestiary/` | About 630 monster stat blocks, sorted by type, then by family |
| `Monsters/` | Monster rules (mooks, large and huge, abilities), the monster creation tables, `Monster-List.md` |
| `Running-the-Game/` | Building battles (monster equivalents), environment DCs, levelling up, loot, rituals |
| `Magic-Items/` | True magic items by chakra (`Magic-Item-Descriptions/`), quirks, one-use items (potions, oils, runes), cursed items |
| `Icons/` | The 13 icons of the Dragon Empire (setting material; the Hotel has its own) |

## Format notes

- **Monsters** are YAML stat blocks inside a ```` ```statblock ```` code block: `level`,
  `role` (troop, wrecker, mook, ...), `size` (normal, large, huge, double-strength, ...),
  `initiative`, `actions` (attack lines with hit and miss damage and triggers), `traits`,
  `nastier_traits`, then `ac`, `pd`, `md`, `hp`. Read it as text; no plugin needed.
- `dice: 1d8` inside backticks is just the dice expression `1d8`.
- `[[Compendium/13A/X/Y|text]]` links point to `13th-age/srd/X/Y.md`.
- Distances: 13th Age uses no measurements in combat (engaged, nearby, far away), so
  there is nothing to convert.

## Refreshing

`git clone --depth 1` the source repo, replace everything here except this README with its
`Compendium/13A/` markdown (`find . -name '*.md'`), copy its `LICENSE.md`, and update the
commit above. `13th-age/tools/gen_hotel.py` and `loot.py` read the files directly, so run
them once afterwards to check they still parse.
