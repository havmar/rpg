# Hotel 3 · campaign rules

The Hotel, as `dnd-crunch/hotel.md` describes it, all twelve sections, with the crunch
house rules from `dnd-crunch/CLAUDE.md`. Seed 45 (`gen_dungeon.py --seed 45`); the floors
and the GM's marks are in `gm-secrets.md`.

- **Morten** is two in one body (`hotel.md` section 11): the class roll was 1d12 = 10,
  **Sorcerer 3 (Draconic) + Book 3**, Human Acolyte, 900 XP, starting gear and 36 GP
  (`character.md`, from `templates/character-sorcerer3.md`). His starting Common item
  (`loot.py --rarity Common`) is a Potion of Healing.
- **Magic items** are in the luggage (`hotel.md` section 12), rolled with
  `tools/loot.py`.
- **Who plays Morten:** the GM. Played in chat, in Markdown.
- **Style:** cheese everything. Table mode open. Report style: the defaults.
- **Room 101 is Morten's own room.** It has no guests and no XP. He searches it like any
  room (one hour, a noise check, a brick check), and it counts toward the rooms he has
  searched on floor 1.
- **Find Familiar's component** is 10 GP of incense, sold by the gift shop.

## Rulings made in play

- **Paying the damages on the spot** at a noise check (10 GP × floor) only avoids the Staff
  −1. It is not the "+1 pay a damage bill" deed, which is for a bill left unpaid and settled
  later at the desk; otherwise every search would buy standing. (Day 1, room 102.)
- **Doors of guests that can't work a lock** (no hands, Intelligence 2 or less) are left on
  the latch by housekeeping: they open. (Day 1, room 105.)
- **Mage Hand theft** still needs the Sleight of Hand check against the guest's passive
  Perception: the hand is visible. It lets him reach into an open suitcase from up to 9 m.
- **A Friendly wanderer** can walk Morten back to its own room and answer the door itself:
  its reaction stands for that door. (Day 2, a Skeleton from 202.)
- **A guest that knows it was charmed** (Charm Person ends, `Spells/Level 1/Charm Person.md`)
  is Hostile to Morten afterwards: its reaction to him is 5 at best. (Day 2, the Pirate in 201.)
- **Housekeeping takes knick-knacks** at their gift-shop value toward the damages: they are
  Staff, like the shop. (Day 2, room 203.)
- **16 hours between Long Rests** (`Glossary/Long Rest.md`): the respawn counts as one, so
  after a death the next Long Rest can start 16 hours after he wakes.
- **Forcing a locked door** is DC 20 (`Equipment/Carpenter's Tools.md`, Smith's Tools), a
  crowbar giving Advantage; a slammed door is otherwise opened by Knock, a key, or the guest.
