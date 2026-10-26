# Hotel 2 · campaign rules

The Hotel, as `dnd-crunch/hotel.md` describes it, all twelve sections, with the crunch
house rules from `dnd-crunch/CLAUDE.md`. Seed 52 (`gen_dungeon.py --seed 52`); the floors
and the GM's marks are in `gm-secrets.md`.

- **Morten** is two in one body (`hotel.md` section 11): the class roll was 1d12 = 10,
  **Sorcerer 3 (Draconic) + Book 3**, Human Acolyte, 900 XP, starting gear and 36 GP
  (`character.md`, from `templates/character-sorcerer3.md`). His starting Common item
  (`loot.py --rarity Common`) is a Spell Scroll of *Alarm*.
- **Magic items** are in the luggage (`hotel.md` section 12), rolled with
  `tools/loot.py`.
- **Who plays Morten:** the GM. Played in chat, in Markdown.
- **Style:** cheese everything. Table mode open. Report style: the defaults.
- **Room 101 is Morten's own room.** It has no guests and no XP. He searches it like any
  room (one hour, a noise check, a brick check), and it counts toward the rooms he has
  searched on floor 1.
