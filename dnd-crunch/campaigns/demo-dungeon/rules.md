# Demo dungeon: campaign rules

A 20-floor dungeon for seeing what SRD monsters can do. Public: Morten may know all of this.
These add to `dnd-crunch/CLAUDE.md` and win where they differ.

- **Floor N is built for a level N character.** Its rooms add up to at least the XP needed
  to go from level N to N+1, using the 2024 XP budgets for one character. Floor 20 is the
  finale.
- **One monster type per room**, 1 to 4 of them, picked at random from all of
  `reference/srd/Monsters/`. No themes: a camel can follow a mephit.
  Each room has a random size and one terrain feature.
- **Layout:** each floor is a chain. Camp → room 1 → room 2 → … → stair down → next floor's
  camp. He can't skip a room without getting through it (fighting, sneaking or
  teleporting past all count; bypassed monsters still give their XP).
- **Camps (checkpoints).** Every floor starts with a camp on the stair landing: a safe Long
  Rest, no wandering monsters, and a trader with the same stock as before. He can walk back
  to any camp he's reached; each room crossed costs 1 exploration turn.
- **Death:** he revives at the camp of the floor he died on, as in the house rule (full
  HP, all spells, 8 hours pass, all coins and gems carried are lost).
  Dead monsters stay dead. Survivors are back at full HP in their room after any 8 hours
  he spends away, whether he died or rested.
- **No wandering monsters** anywhere in the demo dungeon.
- **Loot:** each room's monsters drop coins worth a tenth of their XP. No magic items unless
  the GM adds them.
- **Generator:** the floors come from `python3 dnd-crunch/tools/gen_dungeon.py --seed 20`
  (the GM copies them into `gm-secrets.md`, so the room list stays a surprise).
- **Start:** Morten enters at **floor 3** as a level 3 wizard with his gear from the Sunken
  Vault. Floors 1 and 2 exist but are below him.
