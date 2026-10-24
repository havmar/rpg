# Realms campaign: campaign rules

Public: Morten may know all of this. These add to `dnd-crunch/CLAUDE.md` and
`dnd-crunch/realms-v1.md` (this campaign plays Realms v1), and win where they differ.

- **The world** comes from `python3 dnd-crunch/tools/realms_v1.py new --seed 101`. `world.md`
  is the open map; `realms.json` is the script's state.
- **Morten** starts as he left the demo dungeon: Wizard 4, 2,700 XP, his gear, spellbook
  and 116 GP 5 SP. He starts in his tower (C5) on Month 1 · Day 1, rested.
- **Dungeon floors (Delve).** Each hex holds the floor of its level. A floor works like
  the demo dungeon's: a chain of rooms (entrance → room 1 → room 2 → … → the end), one
  monster type per room, each room with a size and one terrain feature. He can't skip a
  room without getting through it (fighting, sneaking or teleporting past all count;
  bypassed monsters still give their XP).
  - **No camps and no stairs between floors.** The entrance is in the hex; leaving the
    floor ends the Delve.
  - **No wandering monsters** inside a floor.
  - **Loot:** each room's monsters drop coins worth a tenth of their XP, once.
  - Dead monsters stay dead. Survivors are back at full HP in their room after any 8 hours
    he spends away.
- **Death** sends him back to the tower (realms-v1.md), not to a camp.
- **Downtime (GM ruling, Month 1).** After the month's mission the rest of the month
  passes: Morten finishes a Long Rest where he is (full HP, spells, Heroic Inspiration and
  the free Mage Armor back) and lives off his own land. Rations count only on travel and
  mission days.
