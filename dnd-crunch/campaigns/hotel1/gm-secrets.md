# Hotel 1 · GM secrets

Only the GM reads this. Seed 10: `gen_dungeon.py --seed 10`, all 20 floors below. Hotel room
number = floor × 100 + room (room 1.1 is 101, 17.3 is 1703).

## The marks (these win over the rows below)

- **101 (row 1.1) is Morten's room, empty.** The three Guards in the generator's row checked
  out before he came down (the register says 101 is his). No guests, no XP. He can still
  search it: the walls are the Hotel's walls.
- **202 (row 2.2) is the Ark's suite (A).** The generator's two Giant Seahorses are replaced by
  **four Dretches** (CR 1/4 each, 50 XP each, 200 XP: the same budget). Dretches speak Abyssal
  and telepathy 60 ft, but only with creatures that understand Abyssal.
- **Residents (R):** 304 (3.4), 504 (5.4), 1104 (11.4), 1604 (16.4), 1703 (17.3). Names when
  Morten meets them. Each is a guest from the row shown.

## The Cornerstone's secret

Put back together, the Cornerstone is a key. It opens the one door the Staff never mention:
the Manager's suite, past the stair at the top of floor 20. Behind it is a guest who checked
in before the Hotel was built and has never checked out: the Manager, in pyjamas, with the
bill. The Manager offers to check Morten out. Accepting ends the stay: the luggage comes back,
the bill is cancelled, and the Hotel goes quiet. Refusing keeps the Cornerstone in his bag,
and in the morning the doors are open again and the lift has a new floor. The Hotel may have
an opinion.

## Room states

Written as searched: `unsearched` · `searched, brick` · `searched, no brick` · `empty`.
Updated after every room.

| Room | Guests (generator row) | State |
|---|---|---|
| 101 | none (row 1.1 checked out) | searched, no brick |
| 102 | 2× Mastiff (1.2) | searched, brick. One Mastiff went past 101 (wary); the other ignored him. Dead Blood Hawk (from 104) in the room. Luggage left: two suitcases |
| 103 | 1× Dretch (1.3) | in progress: Dretch 6/18 HP, out in the corridor, awake |
| 104 | 3× Blood Hawk (1.4) | unsearched; one hawk dead (in 102), two left |
| 105 | 2× Blink Dog (1.5) | unsearched |
| 201 | 3× Giant Wolf Spider (2.1) | unsearched |
| 202 | 4× Dretch, the Ark (2.2, A) | unsearched |
| 203 | 4× Guard (2.3) | unsearched |
| 204 | 1× Warhorse (2.4) | unsearched |
| 205 | 3× Axe Beak (2.5) | unsearched |

## The floors (the generator's output, seed 10)

## Floor 1 (for level 1)

XP needed for level 2: 300 · floor total: 350 · 5 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 1.1 | 3× Guard | 1/8 | 75 | Moderate | 6×12 sq (9×18 m) | a high ceiling (9 m) with hanging chains | 7 GP |
| 1.2 | 2× Mastiff | 1/8 | 50 | Low | 6×12 sq (9×18 m) | magical darkness in half the room | 5 GP |
| 1.3 | 1× Dretch | 1/4 | 50 | Moderate | 6×6 sq (9×9 m) | an open, empty floor | 5 GP |
| 1.4 | 3× Blood Hawk | 1/8 | 75 | Moderate | 8×10 sq (12×15 m) | thick fog (heavily obscured beyond 3 m) | 7 GP |
| 1.5 | 2× Blink Dog | 1/4 | 100 | High | 12×12 sq (18×18 m) | knee-deep water (difficult terrain) | 10 GP |

## Floor 2 (for level 2)

XP needed for level 3: 600 · floor total: 700 · 5 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 2.1 | 3× Giant Wolf Spider | 1/4 | 150 | Moderate | 12×12 sq (18×18 m) | magical darkness in half the room | 15 GP |
| 2.2 | 2× Giant Seahorse | 1/2 | 200 | High | 6×12 sq (9×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 20 GP |
| 2.3 | 4× Guard | 1/8 | 100 | Low | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 10 GP |
| 2.4 | 1× Warhorse | 1/2 | 100 | Moderate | 8×10 sq (12×15 m) | a narrow 1.5 m entrance (chokepoint) | 10 GP |
| 2.5 | 3× Axe Beak | 1/4 | 150 | Moderate | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 15 GP |

## Floor 3 (for level 3)

XP needed for level 4: 1,800 · floor total: 1,900 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 3.1 | 3× Zombie | 1/4 | 150 | Low | 10×10 sq (15×15 m) | an open, empty floor | 15 GP |
| 3.2 | 1× Giant Eagle | 1 | 200 | Moderate | 10×12 sq (15×18 m) | burning braziers (bright light, fire) | 20 GP |
| 3.3 | 1× Harpy | 1 | 200 | Moderate | 6×12 sq (9×18 m) | rubble (difficult terrain, half cover) | 20 GP |
| 3.4 | 1× Giant Spider | 1 | 200 | Moderate | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 20 GP |
| 3.5 | 4× Gray Ooze | 1/2 | 400 | High | 8×10 sq (12×15 m) | pillars (full cover) | 40 GP |
| 3.6 | 3× Giant Lizard | 1/4 | 150 | Low | 6×8 sq (9×12 m) | an open, empty floor | 15 GP |
| 3.7 | 2× Bugbear Warrior | 1 | 400 | High | 8×8 sq (12×12 m) | statues (half cover) | 40 GP |
| 3.8 | 2× Giant Wasp | 1/2 | 200 | Moderate | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 20 GP |

## Floor 4 (for level 4)

XP needed for level 5: 3,800 · floor total: 3,800 · 13 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 4.1 | 2× Bugbear Warrior | 1 | 400 | High | 6×12 sq (9×18 m) | knee-deep water (difficult terrain) | 40 GP |
| 4.2 | 2× Ghoul | 1 | 400 | High | 10×12 sq (15×18 m) | statues (half cover) | 40 GP |
| 4.3 | 1× Saber-Toothed Tiger | 2 | 450 | High | 8×10 sq (12×15 m) | burning braziers (bright light, fire) | 45 GP |
| 4.4 | 2× Sahuagin Warrior | 1/2 | 200 | Low | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 20 GP |
| 4.5 | 1× Gibbering Mouther | 2 | 450 | High | 6×12 sq (9×18 m) | magical darkness in half the room | 45 GP |
| 4.6 | 2× Scout | 1/2 | 200 | Low | 8×8 sq (12×12 m) | knee-deep water (difficult terrain) | 20 GP |
| 4.7 | 1× Giant Vulture | 1 | 200 | Moderate | 10×12 sq (15×18 m) | statues (half cover) | 20 GP |
| 4.8 | 2× Magmin | 1/2 | 200 | Low | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 20 GP |
| 4.9 | 2× Giant Spider | 1 | 400 | High | 6×8 sq (9×12 m) | magical darkness in half the room | 40 GP |
| 4.10 | 3× Reef Shark | 1/2 | 300 | Moderate | 8×8 sq (12×12 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 30 GP |
| 4.11 | 1× Imp | 1 | 200 | Moderate | 8×10 sq (12×15 m) | thick fog (heavily obscured beyond 3 m) | 20 GP |
| 4.12 | 1× Giant Hyena | 1 | 200 | Moderate | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 20 GP |
| 4.13 | 1× Brown Bear | 1 | 200 | Moderate | 8×8 sq (12×12 m) | a narrow 1.5 m entrance (chokepoint) | 20 GP |

## Floor 5 (for level 5)

XP needed for level 6: 7,500 · floor total: 7,650 · 14 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 5.1 | 1× Hobgoblin Captain | 3 | 700 | Moderate | 8×8 sq (12×12 m) | statues (half cover) | 70 GP |
| 5.2 | 1× Green Dragon Wyrmling | 2 | 450 | Moderate | 4×12 sq (6×18 m) | statues (half cover) | 45 GP |
| 5.3 | 3× Death Dog | 1 | 600 | Moderate | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 60 GP |
| 5.4 | 1× Polar Bear | 2 | 450 | Low | 6×6 sq (9×9 m) | pillars (full cover) | 45 GP |
| 5.5 | 1× Basilisk | 3 | 700 | Moderate | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 70 GP |
| 5.6 | 1× Centaur Trooper | 2 | 450 | Low | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 45 GP |
| 5.7 | 2× Quasit | 1 | 400 | Low | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 40 GP |
| 5.8 | 3× Giant Eagle | 1 | 600 | Moderate | 6×12 sq (9×18 m) | statues (half cover) | 60 GP |
| 5.9 | 1× Ogre | 2 | 450 | Moderate | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 45 GP |
| 5.10 | 1× Gibbering Mouther | 2 | 450 | Moderate | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 45 GP |
| 5.11 | 2× Sphinx of Wonder | 1 | 400 | Low | 6×6 sq (9×9 m) | rubble (difficult terrain, half cover) | 40 GP |
| 5.12 | 2× Ochre Jelly | 2 | 900 | High | 8×10 sq (12×15 m) | thick fog (heavily obscured beyond 3 m) | 90 GP |
| 5.13 | 2× Brown Bear | 1 | 400 | Low | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 40 GP |
| 5.14 | 1× Blue Dragon Wyrmling | 3 | 700 | High | 10×10 sq (15×15 m) | knee-deep water (difficult terrain) | 70 GP |

## Floor 6 (for level 6)

XP needed for level 7: 9,000 · floor total: 9,350 · 10 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 6.1 | 2× Ettercap | 2 | 900 | Moderate | 10×12 sq (15×18 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 6.2 | 2× Giant Elk | 2 | 900 | Moderate | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 90 GP |
| 6.3 | 3× Ghoul | 1 | 600 | Low | 12×12 sq (18×18 m) | a 3 m ledge along one wall (elevation) | 60 GP |
| 6.4 | 1× Guard Captain | 4 | 1,100 | High | 6×12 sq (9×18 m) | thick fog (heavily obscured beyond 3 m) | 110 GP |
| 6.5 | 3× Saber-Toothed Tiger | 2 | 1,350 | High | 12×12 sq (18×18 m) | a narrow 1.5 m entrance (chokepoint) | 135 GP |
| 6.6 | 2× Gibbering Mouther | 2 | 900 | Moderate | 10×10 sq (15×15 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 6.7 | 2× Allosaurus | 2 | 900 | Moderate | 8×10 sq (12×15 m) | statues (half cover) | 90 GP |
| 6.8 | 2× Pegasus | 2 | 900 | Moderate | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 90 GP |
| 6.9 | 3× Black Dragon Wyrmling | 2 | 1,350 | High | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 135 GP |
| 6.10 | 1× Sea Hag | 2 | 450 | Low | 12×12 sq (18×18 m) | a 3 m ledge along one wall (elevation) | 45 GP |

## Floor 7 (for level 7)

XP needed for level 8: 11,000 · floor total: 11,600 · 13 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 7.1 | 1× Green Hag | 3 | 700 | Moderate | 6×12 sq (9×18 m) | thick fog (heavily obscured beyond 3 m) | 70 GP |
| 7.2 | 1× Nightmare | 3 | 700 | Low | 4×12 sq (6×18 m) | magical darkness in half the room | 70 GP |
| 7.3 | 2× Will-o'-Wisp | 2 | 900 | Moderate | 10×12 sq (15×18 m) | a chasm crossed by a 1.5 m-wide bridge | 90 GP |
| 7.4 | 2× Plesiosaurus | 2 | 900 | Moderate | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 90 GP |
| 7.5 | 2× Berserker | 2 | 900 | Moderate | 4×12 sq (6×18 m) | thick fog (heavily obscured beyond 3 m) | 90 GP |
| 7.6 | 2× Minotaur Skeleton | 2 | 900 | Moderate | 8×8 sq (12×12 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 7.7 | 1× Tough Boss | 4 | 1,100 | High | 6×8 sq (9×12 m) | a high ceiling (9 m) with hanging chains | 110 GP |
| 7.8 | 1× Guard Captain | 4 | 1,100 | High | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 110 GP |
| 7.9 | 1× Hippopotamus | 4 | 1,100 | Moderate | 6×8 sq (9×12 m) | thick fog (heavily obscured beyond 3 m) | 110 GP |
| 7.10 | 1× Lamia | 4 | 1,100 | Moderate | 10×10 sq (15×15 m) | a high ceiling (9 m) with hanging chains | 110 GP |
| 7.11 | 3× Death Dog | 1 | 600 | Low | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 60 GP |
| 7.12 | 2× Azer Sentinel | 2 | 900 | Moderate | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 7.13 | 1× Mummy | 3 | 700 | Moderate | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 70 GP |

## Floor 8 (for level 8)

XP needed for level 9: 14,000 · floor total: 15,850 · 12 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 8.1 | 3× Ogre Zombie | 2 | 1,350 | Moderate | 6×6 sq (9×9 m) | statues (half cover) | 135 GP |
| 8.2 | 2× Giant Elk | 2 | 900 | Low | 4×12 sq (6×18 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 8.3 | 1× Otyugh | 5 | 1,800 | High | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 180 GP |
| 8.4 | 3× Azer Sentinel | 2 | 1,350 | Moderate | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 135 GP |
| 8.5 | 3× Mimic | 2 | 1,350 | Moderate | 10×12 sq (15×18 m) | a high ceiling (9 m) with hanging chains | 135 GP |
| 8.6 | 2× Doppelganger | 3 | 1,400 | Moderate | 6×8 sq (9×12 m) | a high ceiling (9 m) with hanging chains | 140 GP |
| 8.7 | 1× Red Dragon Wyrmling | 4 | 1,100 | High | 8×8 sq (12×12 m) | pillars (full cover) | 110 GP |
| 8.8 | 3× Silver Dragon Wyrmling | 2 | 1,350 | Moderate | 4×12 sq (6×18 m) | a chasm crossed by a 1.5 m-wide bridge | 135 GP |
| 8.9 | 2× Silver Dragon Wyrmling | 2 | 900 | Low | 10×12 sq (15×18 m) | pillars (full cover) | 90 GP |
| 8.10 | 2× Silver Dragon Wyrmling | 2 | 900 | Low | 6×12 sq (9×18 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 8.11 | 3× Ogre Zombie | 2 | 1,350 | Moderate | 8×8 sq (12×12 m) | a chasm crossed by a 1.5 m-wide bridge | 135 GP |
| 8.12 | 3× Phase Spider | 3 | 2,100 | High | 4×12 sq (6×18 m) | an open, empty floor | 210 GP |

## Floor 9 (for level 9)

XP needed for level 10: 16,000 · floor total: 17,000 · 12 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 9.1 | 1× Gorgon | 5 | 1,800 | Moderate | 6×8 sq (9×12 m) | statues (half cover) | 180 GP |
| 9.2 | 2× Bearded Devil | 3 | 1,400 | Moderate | 8×8 sq (12×12 m) | burning braziers (bright light, fire) | 140 GP |
| 9.3 | 2× Vampire Familiar | 3 | 1,400 | Moderate | 10×12 sq (15×18 m) | an open, empty floor | 140 GP |
| 9.4 | 1× Black Pudding | 4 | 1,100 | Moderate | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 110 GP |
| 9.5 | 2× Hell Hound | 3 | 1,400 | Moderate | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 140 GP |
| 9.6 | 2× Will-o'-Wisp | 2 | 900 | Low | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 90 GP |
| 9.7 | 2× Bearded Devil | 3 | 1,400 | Moderate | 12×12 sq (18×18 m) | a high ceiling (9 m) with hanging chains | 140 GP |
| 9.8 | 1× Bulette | 5 | 1,800 | High | 10×12 sq (15×18 m) | a 3 m ledge along one wall (elevation) | 180 GP |
| 9.9 | 1× Giant Shark | 5 | 1,800 | Moderate | 12×12 sq (18×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 180 GP |
| 9.10 | 1× Troll | 5 | 1,800 | High | 10×12 sq (15×18 m) | pillars (full cover) | 180 GP |
| 9.11 | 1× Elephant | 4 | 1,100 | Low | 12×12 sq (18×18 m) | knee-deep water (difficult terrain) | 110 GP |
| 9.12 | 1× Tough Boss | 4 | 1,100 | Moderate | 6×8 sq (9×12 m) | statues (half cover) | 110 GP |

## Floor 10 (for level 10)

XP needed for level 11: 21,000 · floor total: 22,400 · 12 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 10.1 | 2× Couatl | 4 | 2,200 | High | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 220 GP |
| 10.2 | 1× Mage | 6 | 2,300 | Moderate | 10×10 sq (15×15 m) | an open, empty floor | 230 GP |
| 10.3 | 2× Couatl | 4 | 2,200 | Moderate | 10×12 sq (15×18 m) | an open, empty floor | 220 GP |
| 10.4 | 1× Hill Giant | 5 | 1,800 | Moderate | 4×12 sq (6×18 m) | magical darkness in half the room | 180 GP |
| 10.5 | 2× Doppelganger | 3 | 1,400 | Low | 12×12 sq (18×18 m) | thick fog (heavily obscured beyond 3 m) | 140 GP |
| 10.6 | 3× Rhinoceros | 2 | 1,350 | Low | 6×12 sq (9×18 m) | rubble (difficult terrain, half cover) | 135 GP |
| 10.7 | 2× Red Dragon Wyrmling | 4 | 2,200 | Moderate | 8×10 sq (12×15 m) | magical darkness in half the room | 220 GP |
| 10.8 | 1× Gladiator | 5 | 1,800 | Moderate | 4×12 sq (6×18 m) | an open, empty floor | 180 GP |
| 10.9 | 3× Minotaur Skeleton | 2 | 1,350 | Low | 6×6 sq (9×9 m) | pillars (full cover) | 135 GP |
| 10.10 | 2× Succubus | 4 | 2,200 | Moderate | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 220 GP |
| 10.11 | 1× Night Hag | 5 | 1,800 | Moderate | 10×12 sq (15×18 m) | burning braziers (bright light, fire) | 180 GP |
| 10.12 | 1× Giant Crocodile | 5 | 1,800 | Moderate | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 180 GP |

## Floor 11 (for level 11)

XP needed for level 12: 15,000 · floor total: 15,500 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 11.1 | 2× Green Hag | 3 | 1,400 | Low | 8×10 sq (12×15 m) | a 3 m ledge along one wall (elevation) | 140 GP |
| 11.2 | 2× Red Dragon Wyrmling | 4 | 2,200 | Moderate | 12×12 sq (18×18 m) | an open, empty floor | 220 GP |
| 11.3 | 2× Flesh Golem | 5 | 3,600 | High | 6×6 sq (9×9 m) | rubble (difficult terrain, half cover) | 360 GP |
| 11.4 | 2× Blue Dragon Wyrmling | 3 | 1,400 | Low | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 140 GP |
| 11.5 | 1× Bulette | 5 | 1,800 | Moderate | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 180 GP |
| 11.6 | 1× Triceratops | 5 | 1,800 | Moderate | 8×8 sq (12×12 m) | a high ceiling (9 m) with hanging chains | 180 GP |
| 11.7 | 2× Black Pudding | 4 | 2,200 | Moderate | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 220 GP |
| 11.8 | 1× Succubus | 4 | 1,100 | Low | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 110 GP |

## Floor 12 (for level 12)

XP needed for level 13: 20,000 · floor total: 23,400 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 12.1 | 2× Barbed Devil | 5 | 3,600 | Moderate | 12×12 sq (18×18 m) | burning braziers (bright light, fire) | 360 GP |
| 12.2 | 2× Vampire Spawn | 5 | 3,600 | Moderate | 10×12 sq (15×18 m) | burning braziers (bright light, fire) | 360 GP |
| 12.3 | 3× Killer Whale | 3 | 2,100 | Low | 10×10 sq (15×15 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 210 GP |
| 12.4 | 1× Werebear | 5 | 1,800 | Low | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 180 GP |
| 12.5 | 1× Night Hag | 5 | 1,800 | Low | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 180 GP |
| 12.6 | 2× Gladiator | 5 | 3,600 | Moderate | 10×12 sq (15×18 m) | pillars (full cover) | 360 GP |
| 12.7 | 3× Succubus | 4 | 3,300 | Moderate | 4×12 sq (6×18 m) | statues (half cover) | 330 GP |
| 12.8 | 2× Fire Elemental | 5 | 3,600 | High | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 360 GP |

## Floor 13 (for level 13)

XP needed for level 14: 20,000 · floor total: 21,600 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 13.1 | 3× Blue Dragon Wyrmling | 3 | 2,100 | Low | 8×10 sq (12×15 m) | an open, empty floor | 210 GP |
| 13.2 | 1× Fire Elemental | 5 | 1,800 | Low | 10×10 sq (15×15 m) | thick fog (heavily obscured beyond 3 m) | 180 GP |
| 13.3 | 1× Cloud Giant | 9 | 5,000 | High | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 500 GP |
| 13.4 | 3× Ettin | 4 | 3,300 | Moderate | 6×12 sq (9×18 m) | magical darkness in half the room | 330 GP |
| 13.5 | 2× Wraith | 5 | 3,600 | Moderate | 8×8 sq (12×12 m) | burning braziers (bright light, fire) | 360 GP |
| 13.6 | 2× Red Dragon Wyrmling | 4 | 2,200 | Low | 8×8 sq (12×12 m) | a narrow 1.5 m entrance (chokepoint) | 220 GP |
| 13.7 | 2× Gladiator | 5 | 3,600 | Moderate | 10×12 sq (15×18 m) | an open, empty floor | 360 GP |

## Floor 14 (for level 14)

XP needed for level 15: 25,000 · floor total: 28,500 · 9 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 14.1 | 2× Fire Elemental | 5 | 3,600 | Moderate | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 360 GP |
| 14.2 | 2× Flesh Golem | 5 | 3,600 | Moderate | 6×12 sq (9×18 m) | thick fog (heavily obscured beyond 3 m) | 360 GP |
| 14.3 | 1× Flesh Golem | 5 | 1,800 | Low | 6×12 sq (9×18 m) | an open, empty floor | 180 GP |
| 14.4 | 2× Troll | 5 | 3,600 | Moderate | 4×12 sq (6×18 m) | statues (half cover) | 360 GP |
| 14.5 | 2× Tough Boss | 4 | 2,200 | Low | 10×12 sq (15×18 m) | thick fog (heavily obscured beyond 3 m) | 220 GP |
| 14.6 | 3× Flesh Golem | 5 | 5,400 | High | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 540 GP |
| 14.7 | 1× Half-Dragon | 5 | 1,800 | Low | 4×12 sq (6×18 m) | an open, empty floor | 180 GP |
| 14.8 | 1× Stone Giant | 7 | 2,900 | Low | 6×8 sq (9×12 m) | thick fog (heavily obscured beyond 3 m) | 290 GP |
| 14.9 | 2× Earth Elemental | 5 | 3,600 | Moderate | 6×6 sq (9×9 m) | pillars (full cover) | 360 GP |

## Floor 15 (for level 15)

XP needed for level 16: 30,000 · floor total: 32,100 · 6 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 15.1 | 1× Remorhaz | 11 | 7,200 | High | 8×10 sq (12×15 m) | burning braziers (bright light, fire) | 720 GP |
| 15.2 | 3× Shambling Mound | 5 | 5,400 | Moderate | 6×8 sq (9×12 m) | rubble (difficult terrain, half cover) | 540 GP |
| 15.3 | 3× Hippopotamus | 4 | 3,300 | Low | 6×12 sq (9×18 m) | statues (half cover) | 330 GP |
| 15.4 | 3× Water Elemental | 5 | 5,400 | Moderate | 8×8 sq (12×12 m) | burning braziers (bright light, fire) | 540 GP |
| 15.5 | 3× Unicorn | 5 | 5,400 | Moderate | 4×12 sq (6×18 m) | a 3 m ledge along one wall (elevation) | 540 GP |
| 15.6 | 3× Water Elemental | 5 | 5,400 | Moderate | 8×10 sq (12×15 m) | thick fog (heavily obscured beyond 3 m) | 540 GP |

## Floor 16 (for level 16)

XP needed for level 17: 30,000 · floor total: 34,700 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 16.1 | 3× Incubus | 4 | 3,300 | Low | 8×10 sq (12×15 m) | an open, empty floor | 330 GP |
| 16.2 | 3× Vampire Spawn | 5 | 5,400 | Moderate | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 540 GP |
| 16.3 | 3× Giant Crocodile | 5 | 5,400 | Moderate | 4×12 sq (6×18 m) | knee-deep water (difficult terrain) | 540 GP |
| 16.4 | 1× Invisible Stalker | 6 | 2,300 | Low | 6×12 sq (9×18 m) | rubble (difficult terrain, half cover) | 230 GP |
| 16.5 | 1× Fire Giant | 9 | 5,000 | High | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 500 GP |
| 16.6 | 3× Elephant | 4 | 3,300 | Low | 10×12 sq (15×18 m) | statues (half cover) | 330 GP |
| 16.7 | 2× Mammoth | 6 | 4,600 | Moderate | 10×12 sq (15×18 m) | magical darkness in half the room | 460 GP |
| 16.8 | 3× Giant Crocodile | 5 | 5,400 | Moderate | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 540 GP |

## Floor 17 (for level 17)

XP needed for level 18: 40,000 · floor total: 48,900 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 17.1 | 4× Roper | 5 | 7,200 | Moderate | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 720 GP |
| 17.2 | 1× Young Blue Dragon | 9 | 5,000 | Moderate | 6×6 sq (9×9 m) | statues (half cover) | 500 GP |
| 17.3 | 4× Water Elemental | 5 | 7,200 | Moderate | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 720 GP |
| 17.4 | 1× Rakshasa | 13 | 10,000 | High | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 1,000 GP |
| 17.5 | 2× Flesh Golem | 5 | 3,600 | Low | 6×8 sq (9×12 m) | statues (half cover) | 360 GP |
| 17.6 | 1× Aboleth | 10 | 5,900 | Moderate | 4×12 sq (6×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 590 GP |
| 17.7 | 1× Vampire | 13 | 10,000 | High | 10×10 sq (15×15 m) | a high ceiling (9 m) with hanging chains | 1,000 GP |

## Floor 18 (for level 18)

XP needed for level 19: 40,000 · floor total: 41,500 · 5 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 18.1 | 2× Chain Devil | 8 | 7,800 | Moderate | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 780 GP |
| 18.2 | 1× Rakshasa | 13 | 10,000 | High | 8×10 sq (12×15 m) | statues (half cover) | 1,000 GP |
| 18.3 | 1× Nalfeshnee | 13 | 10,000 | High | 6×12 sq (9×18 m) | burning braziers (bright light, fire) | 1,000 GP |
| 18.4 | 3× Shield Guardian | 7 | 8,700 | Moderate | 12×12 sq (18×18 m) | magical darkness in half the room | 870 GP |
| 18.5 | 1× Cloud Giant | 9 | 5,000 | Moderate | 6×12 sq (9×18 m) | knee-deep water (difficult terrain) | 500 GP |

## Floor 19 (for level 19)

XP needed for level 20: 50,000 · floor total: 62,700 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 19.1 | 1× Oni | 7 | 2,900 | Low | 6×12 sq (9×18 m) | statues (half cover) | 290 GP |
| 19.2 | 2× Tyrannosaurus Rex | 8 | 7,800 | Moderate | 6×12 sq (9×18 m) | a high ceiling (9 m) with hanging chains | 780 GP |
| 19.3 | 2× Sphinx of Lore | 11 | 14,400 | High | 4×12 sq (6×18 m) | a chasm crossed by a 1.5 m-wide bridge | 1,440 GP |
| 19.4 | 1× Sphinx of Lore | 11 | 7,200 | Moderate | 10×10 sq (15×15 m) | knee-deep water (difficult terrain) | 720 GP |
| 19.5 | 1× Hezrou | 8 | 3,900 | Low | 8×8 sq (12×12 m) | an open, empty floor | 390 GP |
| 19.6 | 1× Adult Black Dragon | 14 | 11,500 | High | 4×12 sq (6×18 m) | a high ceiling (9 m) with hanging chains | 1,150 GP |
| 19.7 | 1× Adult Blue Dragon | 16 | 15,000 | High | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 1,500 GP |

## Floor 20 (for level 20)

Final floor, XP target: 50,000 · floor total: 53,200 · 6 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 20.1 | 2× Fire Giant | 9 | 10,000 | Moderate | 8×8 sq (12×12 m) | a 3 m ledge along one wall (elevation) | 1,000 GP |
| 20.2 | 1× Young Bronze Dragon | 8 | 3,900 | Low | 10×12 sq (15×18 m) | pillars (full cover) | 390 GP |
| 20.3 | 1× Adult Brass Dragon | 13 | 10,000 | Moderate | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 1,000 GP |
| 20.4 | 1× Purple Worm | 15 | 13,000 | Moderate | 10×12 sq (15×18 m) | pillars (full cover) | 1,300 GP |
| 20.5 | 3× Young Green Dragon | 8 | 11,700 | Moderate | 10×12 sq (15×18 m) | magical darkness in half the room | 1,170 GP |
| 20.6 | 2× Medusa | 6 | 4,600 | Low | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 460 GP |

