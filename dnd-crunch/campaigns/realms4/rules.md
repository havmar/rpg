# Realms4 campaign: campaign rules

Public: Morten may know all of this. These add to `dnd-crunch/CLAUDE.md` and
`dnd-crunch/realms-v3.md` (Realms v3), and win where they differ.

- **The world** comes from `python3 dnd-crunch/tools/realms3.py new --seed 83 --campaign
  dnd-crunch/campaigns/realms4 --level 3`. `world.md` is the open map, `map.json` feeds the
  table's Realm tab, `realms.json` is the script's state. Nothing in the world is hidden
  from the tower but the dungeon floors.
- **Morten** starts fresh: the pre-built Wizard 3 (Evoker), 900 XP, his starting gear and
  47 GP 7 SP 5 CP. He starts in his tower (C5) on Month 1 · Day 1 at 08:00, rested. The
  tower starts as **Hermit** (Renown 0), Hold 3 of 3, 100 GP, no sites, no goal, holding
  only its warded hex.
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
- **Missions:** one a month, in the hex he is in: **Strike** a site, **Rob** a realm's
  works, **Aid** a realm's goal, **Contact** a realm (a Persuasion check), or **Delve**
  (`realms-v3.md` section 9).
- **Mission fights** (Strike, Rob, Aid) are built by `realms3.py encounter --site ID` (a
  Strike or Rob on that site) or `encounter --aid REALM` (an Aid), from the site's fight
  list at its tier, at the tier's budget for his level (tier 1 Low, 2 Moderate, 3 High).
  Their coins are a tenth of their XP, as in a floor. `encounter --contact REALM` gives
  the Contact DC.
- **Death** sends him back to the tower (`realms-v3.md` section 9), not to a camp: the
  month's mission fails, he loses the coins and gems he carried, the purse actions stand.
- **The purse.** Coins he leaves in the tower are safe from death but are not the tower's
  treasury until he deposits them at the world's turn (`--deposit`).
- **Downtime.** After the month's mission the rest of the month passes: Morten finishes a
  Long Rest where he is (full HP, spells, Heroic Inspiration and the free Mage Armor back)
  and lives off his own land. Rations count only on travel and mission days.
