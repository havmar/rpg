# Realms 3 campaign: campaign rules

Public: Morten may know all of this. These add to `dnd-crunch/CLAUDE.md` and
`dnd-crunch/realms.md` (Realms v2), and win where they differ.

- **The world** comes from `python3 dnd-crunch/tools/realms.py new --seed 53 --campaign
  dnd-crunch/campaigns/realms3 --level 3`. `world.md` is the open map, `map.json` feeds the
  map page, `realms.json` is the script's state.
- **Morten** starts fresh: the pre-built Wizard 3 (Evoker), 900 XP, his starting gear and
  47 GP 7 SP 5 CP. He starts in his tower (B5) on Month 1 · Day 1 at 08:00, rested. The
  tower starts at Force 1, Cunning 1, Wealth 1, HP 7, 100 GP, no assets.
- **Dungeon floors (Delve).** Each hex holds the floor of its level (`gm-secrets.md`). A
  floor works like the demo dungeon's: a chain of rooms (entrance → room 1 → room 2 → … →
  the end), one monster type per room, each room with a size and one terrain feature. He
  can't skip a room without getting through it (fighting, sneaking or teleporting past all
  count; bypassed monsters still give their XP).
  - **No camps and no stairs between floors.** The entrance is in the hex; leaving the
    floor ends the Delve.
  - **No wandering monsters** inside a floor.
  - **Loot:** each room's monsters drop coins worth a tenth of their XP, once.
  - Dead monsters stay dead. Survivors are back at full HP in their room after any 8 hours
    he spends away.
- **Mission fights** (Strike, Rob, a Contact that turns into a fight) are built by
  `realms.py encounter --asset ID` from the asset's Fight column, at the tier's budget for
  his level. Their coins are a tenth of their XP, as in a floor.
- **Death** sends him back to the tower (realms.md), not to a camp.
- **The purse.** Coins he leaves in the tower are safe from death but are not the tower's
  treasury until he deposits them at the domain turn (`--deposit`).
- **Downtime.** After the month's mission the rest of the month passes: Morten finishes a
  Long Rest where he is (full HP, spells, Heroic Inspiration and the free Mage Armor back)
  and lives off his own land. Rations count only on travel and mission days.
