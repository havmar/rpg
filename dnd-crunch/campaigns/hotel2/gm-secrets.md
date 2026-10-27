# Hotel 2 · GM secrets

Only the GM reads this. Seed 52: `gen_dungeon.py --seed 52`, all 20 floors below. Hotel room
number = floor × 100 + room (room 1.1 is 101, 17.3 is 1703).

## The marks (these win over the rows below)

- **101 (row 1.1) is Morten's room, empty.** The four Blood Hawks in the generator's row
  checked out before he came down (the register says 101 is his). No guests, no XP. He can
  still search it: the walls are the Hotel's walls.
- **201 (row 2.1) is the Ark's suite (A).** The generator's four Pseudodragons are replaced
  by **two Sahuagin Warriors** (CR 1/2 each, 100 XP each, 200 XP: the same budget; Fiends in
  the 2024 SRD). They speak Sahuagin. Rolled with `roll.py 1d5` from the Fiends that fit
  200 XP (4 Dretches, an Imp, a Quasit, 2 Gnoll Warriors, 2 Sahuagin Warriors). The suite's
  feature stays: pillars (full cover).
- **Residents (R):** 204 (2.4, a Magma Mephit), 510 (5.10, a Green Hag), 1106 (11.6, a
  Tough Boss), 1602 (16.2, a Stone Golem, who answers in notes), 2007 (20.7, three Rocs,
  one Resident family). Names when Morten meets them.
- **Luggage** (`hotel.md` section 12) is rolled when a room's guests are first met and
  written in the room's row below. The five R suites and 201 always hold an item:
  `loot.py --floor N --sure --band-up`.

## The Cornerstone's secret

Put back together, the Cornerstone is the Hotel's own room key. The Hotel is a guest too,
staying in a much larger hotel, and it has never been able to leave because its key was
broken into the walls. When the last brick goes in, the corridors fold up like a map and
Morten stands at the desk of the larger hotel with the Hotel in his luggage: a doll's house
of twenty floors, every guest asleep in it, in pyjamas. The clerk asks whether he is
checking in or checking out. Checking out sends him home with the doll's house; the stay
is over and the bill is cancelled. Checking in gives him a room on floor 1 of the larger
hotel, his level, items and bricks kept, and a new register to read: a new campaign. The
Hotel may have an opinion.

## Room states

Written as searched: `unsearched` · `searched, brick` · `searched, no brick` · `empty`.
Luggage: `—` until rolled, then the item or `nothing magic`. Updated after every room.

| Room | Guests (generator row) | Luggage | State |
|---|---|---|---|
| 101 | none (row 1.1 checked out) | — | unsearched |
| 102 | 4× Noble (1.2) | — | unsearched |
| 103 | 2× Giant Bat (1.3) | — | unsearched |
| 201 | 2× Sahuagin Warrior, the Ark (2.1, A) | — (sure, band up) | unsearched |
| 202 | 3× Grimlock (2.2) | — | unsearched |
| 203 | 2× Giant Centipede (2.3) | — | unsearched |
| 204 | 1× Magma Mephit, Resident (2.4, R) | — (sure, band up) | unsearched |
| 205 | 1× Black Bear (2.5) | — | unsearched |

Floors 3 and up: add rows as Morten reaches them.

## The floors (the generator's output, seed 52)

## Floor 1 (for level 1)

XP needed for level 2: 300 · floor total: 300 · 3 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 1.1 | 4× Blood Hawk | 1/8 | 100 | High | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 10 GP |
| 1.2 | 4× Noble | 1/8 | 100 | High | 12×12 sq (18×18 m) | pillars (full cover) | 10 GP |
| 1.3 | 2× Giant Bat | 1/4 | 100 | High | 12×12 sq (18×18 m) | knee-deep water (difficult terrain) | 10 GP |

## Floor 2 (for level 2)

XP needed for level 3: 600 · floor total: 650 · 5 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 2.1 | 4× Pseudodragon | 1/4 | 200 | High | 6×6 sq (9×9 m) | pillars (full cover) | 20 GP |
| 2.2 | 3× Grimlock | 1/4 | 150 | Moderate | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 15 GP |
| 2.3 | 2× Giant Centipede | 1/4 | 100 | Low | 6×12 sq (9×18 m) | a 3 m ledge along one wall (elevation) | 10 GP |
| 2.4 | 1× Magma Mephit | 1/2 | 100 | Moderate | 6×12 sq (9×18 m) | statues (half cover) | 10 GP |
| 2.5 | 1× Black Bear | 1/2 | 100 | Low | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 10 GP |

## Floor 3 (for level 3)

XP needed for level 4: 1,800 · floor total: 1,800 · 11 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 3.1 | 2× Shadow | 1/2 | 200 | Moderate | 10×12 sq (15×18 m) | an open, empty floor | 20 GP |
| 3.2 | 1× Gnoll Warrior | 1/2 | 100 | Low | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 10 GP |
| 3.3 | 1× Dire Wolf | 1 | 200 | Moderate | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 20 GP |
| 3.4 | 2× Troll Limb | 1/2 | 200 | Moderate | 12×12 sq (18×18 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 3.5 | 1× Harpy | 1 | 200 | Moderate | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 20 GP |
| 3.6 | 1× Satyr | 1/2 | 100 | Low | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 10 GP |
| 3.7 | 1× Death Dog | 1 | 200 | Moderate | 6×8 sq (9×12 m) | knee-deep water (difficult terrain) | 20 GP |
| 3.8 | 1× Sahuagin Warrior | 1/2 | 100 | Low | 8×10 sq (12×15 m) | magical darkness in half the room | 10 GP |
| 3.9 | 3× Pteranodon | 1/4 | 150 | Low | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 15 GP |
| 3.10 | 1× Swarm of Piranhas | 1 | 200 | Moderate | 8×10 sq (12×15 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 20 GP |
| 3.11 | 3× Violet Fungus | 1/4 | 150 | Low | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 15 GP |

## Floor 4 (for level 4)

XP needed for level 5: 3,800 · floor total: 4,050 · 14 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 4.1 | 3× Darkmantle | 1/2 | 300 | Moderate | 8×10 sq (12×15 m) | an open, empty floor | 30 GP |
| 4.2 | 1× Specter | 1 | 200 | Moderate | 12×12 sq (18×18 m) | an open, empty floor | 20 GP |
| 4.3 | 1× Giant Boar | 2 | 450 | High | 6×8 sq (9×12 m) | burning braziers (bright light, fire) | 45 GP |
| 4.4 | 3× Darkmantle | 1/2 | 300 | Moderate | 6×6 sq (9×9 m) | thick fog (heavily obscured beyond 3 m) | 30 GP |
| 4.5 | 1× Animated Armor | 1 | 200 | Moderate | 10×12 sq (15×18 m) | magical darkness in half the room | 20 GP |
| 4.6 | 2× Black Bear | 1/2 | 200 | Low | 8×8 sq (12×12 m) | an open, empty floor | 20 GP |
| 4.7 | 1× Centaur Trooper | 2 | 450 | High | 12×12 sq (18×18 m) | an open, empty floor | 45 GP |
| 4.8 | 1× Allosaurus | 2 | 450 | High | 8×8 sq (12×12 m) | magical darkness in half the room | 45 GP |
| 4.9 | 3× Black Bear | 1/2 | 300 | Moderate | 8×8 sq (12×12 m) | an open, empty floor | 30 GP |
| 4.10 | 2× Darkmantle | 1/2 | 200 | Low | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 20 GP |
| 4.11 | 1× Giant Eagle | 1 | 200 | Moderate | 10×12 sq (15×18 m) | burning braziers (bright light, fire) | 20 GP |
| 4.12 | 2× Giant Goat | 1/2 | 200 | Low | 8×10 sq (12×15 m) | knee-deep water (difficult terrain) | 20 GP |
| 4.13 | 2× Tough | 1/2 | 200 | Low | 10×10 sq (15×15 m) | pillars (full cover) | 20 GP |
| 4.14 | 2× Ghoul | 1 | 400 | High | 8×10 sq (12×15 m) | an open, empty floor | 40 GP |

## Floor 5 (for level 5)

XP needed for level 6: 7,500 · floor total: 7,800 · 13 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 5.1 | 1× Grick | 2 | 450 | Moderate | 10×12 sq (15×18 m) | magical darkness in half the room | 45 GP |
| 5.2 | 2× Pirate | 1 | 400 | Low | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 40 GP |
| 5.3 | 1× Werewolf | 3 | 700 | Moderate | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 70 GP |
| 5.4 | 1× Wight | 3 | 700 | Moderate | 10×10 sq (15×15 m) | magical darkness in half the room | 70 GP |
| 5.5 | 1× Knight | 3 | 700 | Moderate | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 70 GP |
| 5.6 | 3× Quasit | 1 | 600 | Moderate | 6×12 sq (9×18 m) | magical darkness in half the room | 60 GP |
| 5.7 | 2× Bronze Dragon Wyrmling | 2 | 900 | High | 4×12 sq (6×18 m) | pillars (full cover) | 90 GP |
| 5.8 | 2× Bronze Dragon Wyrmling | 2 | 900 | High | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 90 GP |
| 5.9 | 1× Black Dragon Wyrmling | 2 | 450 | Low | 10×10 sq (15×15 m) | a high ceiling (9 m) with hanging chains | 45 GP |
| 5.10 | 1× Green Hag | 3 | 700 | High | 10×10 sq (15×15 m) | an open, empty floor | 70 GP |
| 5.11 | 1× Animated Rug of Smothering | 2 | 450 | Low | 10×12 sq (15×18 m) | an open, empty floor | 45 GP |
| 5.12 | 2× Copper Dragon Wyrmling | 1 | 400 | Low | 10×12 sq (15×18 m) | a narrow 1.5 m entrance (chokepoint) | 40 GP |
| 5.13 | 1× Mimic | 2 | 450 | Low | 8×8 sq (12×12 m) | pillars (full cover) | 45 GP |

## Floor 6 (for level 6)

XP needed for level 7: 9,000 · floor total: 9,000 · 14 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 6.1 | 3× Dire Wolf | 1 | 600 | Low | 4×12 sq (6×18 m) | a 3 m ledge along one wall (elevation) | 60 GP |
| 6.2 | 1× White Dragon Wyrmling | 2 | 450 | Low | 10×10 sq (15×15 m) | an open, empty floor | 45 GP |
| 6.3 | 1× Priest | 2 | 450 | Low | 6×8 sq (9×12 m) | a narrow 1.5 m entrance (chokepoint) | 45 GP |
| 6.4 | 1× Ankheg | 2 | 450 | Low | 10×12 sq (15×18 m) | a high ceiling (9 m) with hanging chains | 45 GP |
| 6.5 | 1× Ettin | 4 | 1,100 | High | 10×10 sq (15×15 m) | a chasm crossed by a 1.5 m-wide bridge | 110 GP |
| 6.6 | 1× Giant Constrictor Snake | 2 | 450 | Low | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 45 GP |
| 6.7 | 3× Specter | 1 | 600 | Low | 12×12 sq (18×18 m) | thick fog (heavily obscured beyond 3 m) | 60 GP |
| 6.8 | 1× Priest | 2 | 450 | Low | 10×12 sq (15×18 m) | a 3 m ledge along one wall (elevation) | 45 GP |
| 6.9 | 1× Plesiosaurus | 2 | 450 | Low | 4×12 sq (6×18 m) | statues (half cover) | 45 GP |
| 6.10 | 2× Silver Dragon Wyrmling | 2 | 900 | Moderate | 6×8 sq (9×12 m) | thick fog (heavily obscured beyond 3 m) | 90 GP |
| 6.11 | 1× Werewolf | 3 | 700 | Moderate | 12×12 sq (18×18 m) | a 3 m ledge along one wall (elevation) | 70 GP |
| 6.12 | 2× Centaur Trooper | 2 | 900 | Moderate | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 90 GP |
| 6.13 | 2× Mimic | 2 | 900 | Moderate | 4×12 sq (6×18 m) | an open, empty floor | 90 GP |
| 6.14 | 3× Imp | 1 | 600 | Low | 12×12 sq (18×18 m) | burning braziers (bright light, fire) | 60 GP |

## Floor 7 (for level 7)

XP needed for level 8: 11,000 · floor total: 11,550 · 15 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 7.1 | 1× Doppelganger | 3 | 700 | Moderate | 4×12 sq (6×18 m) | an open, empty floor | 70 GP |
| 7.2 | 3× Green Dragon Wyrmling | 2 | 1,350 | High | 6×6 sq (9×9 m) | thick fog (heavily obscured beyond 3 m) | 135 GP |
| 7.3 | 2× Polar Bear | 2 | 900 | Moderate | 6×12 sq (9×18 m) | knee-deep water (difficult terrain) | 90 GP |
| 7.4 | 2× Merrow | 2 | 900 | Moderate | 6×12 sq (9×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 90 GP |
| 7.5 | 1× Gold Dragon Wyrmling | 3 | 700 | Moderate | 6×12 sq (9×18 m) | rubble (difficult terrain, half cover) | 70 GP |
| 7.6 | 3× Goblin Boss | 1 | 600 | Low | 12×12 sq (18×18 m) | statues (half cover) | 60 GP |
| 7.7 | 1× Ghast | 2 | 450 | Low | 12×12 sq (18×18 m) | magical darkness in half the room | 45 GP |
| 7.8 | 3× Lion | 1 | 600 | Low | 8×8 sq (12×12 m) | a high ceiling (9 m) with hanging chains | 60 GP |
| 7.9 | 1× Bronze Dragon Wyrmling | 2 | 450 | Low | 10×10 sq (15×15 m) | statues (half cover) | 45 GP |
| 7.10 | 1× Black Dragon Wyrmling | 2 | 450 | Low | 6×8 sq (9×12 m) | a 3 m ledge along one wall (elevation) | 45 GP |
| 7.11 | 1× Ettercap | 2 | 450 | Low | 4×12 sq (6×18 m) | pillars (full cover) | 45 GP |
| 7.12 | 2× Gelatinous Cube | 2 | 900 | Moderate | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 90 GP |
| 7.13 | 1× Wereboar | 4 | 1,100 | High | 6×8 sq (9×12 m) | a high ceiling (9 m) with hanging chains | 110 GP |
| 7.14 | 2× Azer Sentinel | 2 | 900 | Moderate | 8×8 sq (12×12 m) | statues (half cover) | 90 GP |
| 7.15 | 1× Red Dragon Wyrmling | 4 | 1,100 | Moderate | 12×12 sq (18×18 m) | thick fog (heavily obscured beyond 3 m) | 110 GP |

## Floor 8 (for level 8)

XP needed for level 9: 14,000 · floor total: 14,700 · 12 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 8.1 | 3× Cultist Fanatic | 2 | 1,350 | Moderate | 12×12 sq (18×18 m) | magical darkness in half the room | 135 GP |
| 8.2 | 2× Bugbear Stalker | 3 | 1,400 | Moderate | 10×12 sq (15×18 m) | burning braziers (bright light, fire) | 140 GP |
| 8.3 | 1× Hippopotamus | 4 | 1,100 | Moderate | 12×12 sq (18×18 m) | burning braziers (bright light, fire) | 110 GP |
| 8.4 | 1× Black Pudding | 4 | 1,100 | High | 8×10 sq (12×15 m) | magical darkness in half the room | 110 GP |
| 8.5 | 1× Succubus | 4 | 1,100 | Moderate | 6×6 sq (9×9 m) | pillars (full cover) | 110 GP |
| 8.6 | 3× Swarm of Venomous Snakes | 2 | 1,350 | Moderate | 4×12 sq (6×18 m) | rubble (difficult terrain, half cover) | 135 GP |
| 8.7 | 3× Grick | 2 | 1,350 | Moderate | 10×10 sq (15×15 m) | statues (half cover) | 135 GP |
| 8.8 | 2× Manticore | 3 | 1,400 | Moderate | 6×6 sq (9×9 m) | an open, empty floor | 140 GP |
| 8.9 | 2× Minotaur Skeleton | 2 | 900 | Low | 8×8 sq (12×12 m) | burning braziers (bright light, fire) | 90 GP |
| 8.10 | 2× Manticore | 3 | 1,400 | Moderate | 4×12 sq (6×18 m) | pillars (full cover) | 140 GP |
| 8.11 | 2× Awakened Tree | 2 | 900 | Low | 12×12 sq (18×18 m) | statues (half cover) | 90 GP |
| 8.12 | 3× Merrow | 2 | 1,350 | Moderate | 4×12 sq (6×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 135 GP |

## Floor 9 (for level 9)

XP needed for level 10: 16,000 · floor total: 16,100 · 13 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 9.1 | 1× Elephant | 4 | 1,100 | Low | 8×8 sq (12×12 m) | knee-deep water (difficult terrain) | 110 GP |
| 9.2 | 2× Awakened Tree | 2 | 900 | Low | 12×12 sq (18×18 m) | a narrow 1.5 m entrance (chokepoint) | 90 GP |
| 9.3 | 1× Gladiator | 5 | 1,800 | High | 6×12 sq (9×18 m) | a chasm crossed by a 1.5 m-wide bridge | 180 GP |
| 9.4 | 2× Phase Spider | 3 | 1,400 | Moderate | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 140 GP |
| 9.5 | 2× Ochre Jelly | 2 | 900 | Low | 6×6 sq (9×9 m) | pillars (full cover) | 90 GP |
| 9.6 | 2× Basilisk | 3 | 1,400 | Moderate | 6×6 sq (9×9 m) | magical darkness in half the room | 140 GP |
| 9.7 | 1× Bugbear Stalker | 3 | 700 | Low | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 70 GP |
| 9.8 | 1× Roper | 5 | 1,800 | High | 6×12 sq (9×18 m) | a 3 m ledge along one wall (elevation) | 180 GP |
| 9.9 | 2× Giant Constrictor Snake | 2 | 900 | Low | 6×8 sq (9×12 m) | thick fog (heavily obscured beyond 3 m) | 90 GP |
| 9.10 | 2× Ogre Zombie | 2 | 900 | Low | 10×12 sq (15×18 m) | an open, empty floor | 90 GP |
| 9.11 | 1× Elephant | 4 | 1,100 | Moderate | 12×12 sq (18×18 m) | an open, empty floor | 110 GP |
| 9.12 | 3× Manticore | 3 | 2,100 | High | 8×8 sq (12×12 m) | a chasm crossed by a 1.5 m-wide bridge | 210 GP |
| 9.13 | 1× Incubus | 4 | 1,100 | Moderate | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 110 GP |

## Floor 10 (for level 10)

XP needed for level 11: 21,000 · floor total: 22,250 · 13 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 10.1 | 2× Doppelganger | 3 | 1,400 | Low | 6×12 sq (9×18 m) | a chasm crossed by a 1.5 m-wide bridge | 140 GP |
| 10.2 | 1× Young Brass Dragon | 6 | 2,300 | Moderate | 10×12 sq (15×18 m) | a 3 m ledge along one wall (elevation) | 230 GP |
| 10.3 | 1× Giant Crocodile | 5 | 1,800 | Moderate | 8×10 sq (12×15 m) | statues (half cover) | 180 GP |
| 10.4 | 1× Fire Elemental | 5 | 1,800 | Moderate | 6×6 sq (9×9 m) | thick fog (heavily obscured beyond 3 m) | 180 GP |
| 10.5 | 1× Ghost | 4 | 1,100 | Low | 6×8 sq (9×12 m) | a narrow 1.5 m entrance (chokepoint) | 110 GP |
| 10.6 | 2× Ghost | 4 | 2,200 | Moderate | 4×12 sq (6×18 m) | magical darkness in half the room | 220 GP |
| 10.7 | 2× Basilisk | 3 | 1,400 | Low | 8×10 sq (12×15 m) | a 3 m ledge along one wall (elevation) | 140 GP |
| 10.8 | 3× Swarm of Crawling Claws | 3 | 2,100 | Moderate | 8×8 sq (12×12 m) | an open, empty floor | 210 GP |
| 10.9 | 1× Vampire Spawn | 5 | 1,800 | Moderate | 4×12 sq (6×18 m) | thick fog (heavily obscured beyond 3 m) | 180 GP |
| 10.10 | 2× Owlbear | 3 | 1,400 | Low | 6×8 sq (9×12 m) | an open, empty floor | 140 GP |
| 10.11 | 3× Saber-Toothed Tiger | 2 | 1,350 | Low | 10×10 sq (15×15 m) | a narrow 1.5 m entrance (chokepoint) | 135 GP |
| 10.12 | 1× Vampire Spawn | 5 | 1,800 | Moderate | 12×12 sq (18×18 m) | a narrow 1.5 m entrance (chokepoint) | 180 GP |
| 10.13 | 1× Giant Shark | 5 | 1,800 | High | 10×10 sq (15×15 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 180 GP |

## Floor 11 (for level 11)

XP needed for level 12: 15,000 · floor total: 16,400 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 11.1 | 1× Medusa | 6 | 2,300 | Moderate | 8×10 sq (12×15 m) | a narrow 1.5 m entrance (chokepoint) | 230 GP |
| 11.2 | 1× Giant Crocodile | 5 | 1,800 | Moderate | 8×8 sq (12×12 m) | statues (half cover) | 180 GP |
| 11.3 | 1× Wraith | 5 | 1,800 | Moderate | 12×12 sq (18×18 m) | thick fog (heavily obscured beyond 3 m) | 180 GP |
| 11.4 | 1× Fire Elemental | 5 | 1,800 | Moderate | 6×8 sq (9×12 m) | a narrow 1.5 m entrance (chokepoint) | 180 GP |
| 11.5 | 2× Incubus | 4 | 2,200 | Moderate | 6×6 sq (9×9 m) | rubble (difficult terrain, half cover) | 220 GP |
| 11.6 | 1× Tough Boss | 4 | 1,100 | Low | 6×8 sq (9×12 m) | burning braziers (bright light, fire) | 110 GP |
| 11.7 | 2× Bulette | 5 | 3,600 | High | 8×10 sq (12×15 m) | an open, empty floor | 360 GP |
| 11.8 | 1× Xorn | 5 | 1,800 | Moderate | 8×8 sq (12×12 m) | knee-deep water (difficult terrain) | 180 GP |

## Floor 12 (for level 12)

XP needed for level 13: 20,000 · floor total: 23,100 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 12.1 | 3× Hippopotamus | 4 | 3,300 | Moderate | 10×12 sq (15×18 m) | burning braziers (bright light, fire) | 330 GP |
| 12.2 | 2× Salamander | 5 | 3,600 | Moderate | 6×12 sq (9×18 m) | a chasm crossed by a 1.5 m-wide bridge | 360 GP |
| 12.3 | 1× Hill Giant | 5 | 1,800 | Low | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 180 GP |
| 12.4 | 1× Wyvern | 6 | 2,300 | Moderate | 8×8 sq (12×12 m) | a 3 m ledge along one wall (elevation) | 230 GP |
| 12.5 | 2× Vrock | 6 | 4,600 | High | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 460 GP |
| 12.6 | 1× Giant Ape | 7 | 2,900 | High | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 290 GP |
| 12.7 | 2× Medusa | 6 | 4,600 | High | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 460 GP |

## Floor 13 (for level 13)

XP needed for level 14: 20,000 · floor total: 20,900 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 13.1 | 1× Drider | 6 | 2,300 | Moderate | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 230 GP |
| 13.2 | 2× Earth Elemental | 5 | 3,600 | Moderate | 10×12 sq (15×18 m) | thick fog (heavily obscured beyond 3 m) | 360 GP |
| 13.3 | 1× Vrock | 6 | 2,300 | Moderate | 6×8 sq (9×12 m) | pillars (full cover) | 230 GP |
| 13.4 | 1× Mammoth | 6 | 2,300 | Moderate | 8×10 sq (12×15 m) | burning braziers (bright light, fire) | 230 GP |
| 13.5 | 2× Shambling Mound | 5 | 3,600 | Moderate | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 360 GP |
| 13.6 | 2× Elephant | 4 | 2,200 | Low | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 220 GP |
| 13.7 | 2× Young White Dragon | 6 | 4,600 | High | 6×12 sq (9×18 m) | a high ceiling (9 m) with hanging chains | 460 GP |

## Floor 14 (for level 14)

XP needed for level 15: 25,000 · floor total: 26,200 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 14.1 | 1× Young Black Dragon | 7 | 2,900 | Moderate | 6×8 sq (9×12 m) | a narrow 1.5 m entrance (chokepoint) | 290 GP |
| 14.2 | 2× Roper | 5 | 3,600 | Moderate | 12×12 sq (18×18 m) | statues (half cover) | 360 GP |
| 14.3 | 2× Young White Dragon | 6 | 4,600 | Moderate | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 460 GP |
| 14.4 | 2× Bulette | 5 | 3,600 | Moderate | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 360 GP |
| 14.5 | 2× Air Elemental | 5 | 3,600 | Moderate | 6×8 sq (9×12 m) | statues (half cover) | 360 GP |
| 14.6 | 1× Young Copper Dragon | 7 | 2,900 | Low | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 290 GP |
| 14.7 | 1× Clay Golem | 9 | 5,000 | High | 8×8 sq (12×12 m) | a chasm crossed by a 1.5 m-wide bridge | 500 GP |

## Floor 15 (for level 15)

XP needed for level 16: 30,000 · floor total: 31,700 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 15.1 | 1× Mage | 6 | 2,300 | Low | 12×12 sq (18×18 m) | pillars (full cover) | 230 GP |
| 15.2 | 1× Djinni | 11 | 7,200 | High | 12×12 sq (18×18 m) | an open, empty floor | 720 GP |
| 15.3 | 3× Vampire Spawn | 5 | 5,400 | Moderate | 4×12 sq (6×18 m) | pillars (full cover) | 540 GP |
| 15.4 | 1× Unicorn | 5 | 1,800 | Low | 6×8 sq (9×12 m) | burning braziers (bright light, fire) | 180 GP |
| 15.5 | 3× Pirate Captain | 6 | 6,900 | High | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 690 GP |
| 15.6 | 1× Pirate Captain | 6 | 2,300 | Low | 6×12 sq (9×18 m) | a 3 m ledge along one wall (elevation) | 230 GP |
| 15.7 | 2× Oni | 7 | 5,800 | High | 6×8 sq (9×12 m) | rubble (difficult terrain, half cover) | 580 GP |

## Floor 16 (for level 16)

XP needed for level 17: 30,000 · floor total: 31,800 · 5 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 16.1 | 1× Sphinx of Lore | 11 | 7,200 | High | 10×10 sq (15×15 m) | magical darkness in half the room | 720 GP |
| 16.2 | 1× Stone Golem | 10 | 5,900 | Moderate | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 590 GP |
| 16.3 | 1× Deva | 10 | 5,900 | Moderate | 6×8 sq (9×12 m) | a narrow 1.5 m entrance (chokepoint) | 590 GP |
| 16.4 | 1× Young Silver Dragon | 9 | 5,000 | Moderate | 8×10 sq (12×15 m) | a chasm crossed by a 1.5 m-wide bridge | 500 GP |
| 16.5 | 2× Tyrannosaurus Rex | 8 | 7,800 | High | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 780 GP |

## Floor 17 (for level 17)

XP needed for level 18: 40,000 · floor total: 40,400 · 6 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 17.1 | 1× Young Gold Dragon | 10 | 5,900 | High | 10×12 sq (15×18 m) | a narrow 1.5 m entrance (chokepoint) | 590 GP |
| 17.2 | 2× Troll | 5 | 3,600 | Low | 10×10 sq (15×15 m) | statues (half cover) | 360 GP |
| 17.3 | 3× Chain Devil | 8 | 11,700 | High | 8×10 sq (12×15 m) | statues (half cover) | 1,170 GP |
| 17.4 | 3× Hydra | 8 | 11,700 | High | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 1,170 GP |
| 17.5 | 1× Hydra | 8 | 3,900 | Moderate | 6×8 sq (9×12 m) | burning braziers (bright light, fire) | 390 GP |
| 17.6 | 2× Fire Elemental | 5 | 3,600 | Low | 10×12 sq (15×18 m) | a chasm crossed by a 1.5 m-wide bridge | 360 GP |

## Floor 18 (for level 18)

XP needed for level 19: 40,000 · floor total: 44,500 · 6 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 18.1 | 1× Purple Worm | 15 | 13,000 | High | 4×12 sq (6×18 m) | a 3 m ledge along one wall (elevation) | 1,300 GP |
| 18.2 | 3× Shield Guardian | 7 | 8,700 | Moderate | 4×12 sq (6×18 m) | pillars (full cover) | 870 GP |
| 18.3 | 2× Shambling Mound | 5 | 3,600 | Low | 6×12 sq (9×18 m) | a chasm crossed by a 1.5 m-wide bridge | 360 GP |
| 18.4 | 2× Hydra | 8 | 7,800 | Moderate | 10×10 sq (15×15 m) | a 3 m ledge along one wall (elevation) | 780 GP |
| 18.5 | 2× Fire Elemental | 5 | 3,600 | Low | 6×12 sq (9×18 m) | a high ceiling (9 m) with hanging chains | 360 GP |
| 18.6 | 2× Assassin | 8 | 7,800 | Moderate | 10×10 sq (15×15 m) | thick fog (heavily obscured beyond 3 m) | 780 GP |

## Floor 19 (for level 19)

XP needed for level 20: 50,000 · floor total: 50,100 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 19.1 | 1× Roc | 11 | 7,200 | Moderate | 10×12 sq (15×18 m) | magical darkness in half the room | 720 GP |
| 19.2 | 3× Giant Shark | 5 | 5,400 | Low | 6×6 sq (9×9 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 540 GP |
| 19.3 | 1× Clay Golem | 9 | 5,000 | Low | 12×12 sq (18×18 m) | pillars (full cover) | 500 GP |
| 19.4 | 3× Triceratops | 5 | 5,400 | Low | 12×12 sq (18×18 m) | magical darkness in half the room | 540 GP |
| 19.5 | 1× Hezrou | 8 | 3,900 | Low | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 390 GP |
| 19.6 | 2× Tyrannosaurus Rex | 8 | 7,800 | Moderate | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 780 GP |
| 19.7 | 3× Night Hag | 5 | 5,400 | Low | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 540 GP |
| 19.8 | 2× Glabrezu | 9 | 10,000 | Moderate | 8×10 sq (12×15 m) | a chasm crossed by a 1.5 m-wide bridge | 1,000 GP |

## Floor 20 (for level 20)

Final floor, XP target: 50,000 · floor total: 63,200 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 20.1 | 1× Djinni | 11 | 7,200 | Moderate | 8×10 sq (12×15 m) | thick fog (heavily obscured beyond 3 m) | 720 GP |
| 20.2 | 2× Drider | 6 | 4,600 | Low | 6×6 sq (9×9 m) | thick fog (heavily obscured beyond 3 m) | 460 GP |
| 20.3 | 1× Efreeti | 11 | 7,200 | Moderate | 8×8 sq (12×12 m) | statues (half cover) | 720 GP |
| 20.4 | 1× Djinni | 11 | 7,200 | Moderate | 12×12 sq (18×18 m) | statues (half cover) | 720 GP |
| 20.5 | 2× Young Blue Dragon | 9 | 10,000 | Moderate | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 1,000 GP |
| 20.6 | 3× Roper | 5 | 5,400 | Low | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 540 GP |
| 20.7 | 3× Roc | 11 | 21,600 | High | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 2,160 GP |

