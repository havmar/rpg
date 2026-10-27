# Hotel 3 · GM secrets

Only the GM reads this. Seed 45: `gen_dungeon.py --seed 45`, all 20 floors below. Hotel room
number = floor × 100 + room (room 1.1 is 101, 17.3 is 1703).

## The marks (these win over the rows below)

- **101 (row 1.1) is Morten's room, empty.** The two Mules in the generator's row checked
  out before he came down (the register says 101 is his). No guests, no XP. He can still
  search it: the walls are the Hotel's walls.
- **407 (row 4.7) is the Ark's suite (A).** Rolled with `roll.py 1d33` over the 33 rooms of
  floors 1 to 4 other than 101 (24th room). The generator's two Apes are replaced by **two
  Sahuagin Warriors** (CR 1/2 each, 100 XP each, 200 XP: the same budget; Fiends in the 2024
  SRD). They speak Sahuagin. Rolled with `roll.py 1d5` from the Fiends that fit 200 XP
  (1 four Dretches, 2 an Imp, 3 a Quasit, 4 two Gnoll Warriors, 5 two Sahuagin Warriors):
  5. The suite's feature stays: pillars (full cover). The Hotel's other Fiends (the Imp in
  304, the Quasit in 404, the Imps in 715, the Incubus in 707 and others above) are the
  Ark's members and use its standing.
- **Residents (R):** one per band of four floors, the floor rolled on 1d4 and the room on
  the floor's count: **403** (4.3, a Goblin Boss), **701** (7.1, a Red Dragon Wyrmling),
  **901** (9.1, a Gladiator), **1501** (15.1, two Young Brass Dragons, one Resident couple),
  **2003** (20.3, three Air Elementals, one Resident family). Names when Morten meets them.
- **Rumoured bricks.** A rumour that names a brick fixes it: that room's search finds a
  brick with no roll. 201 (Day 1).
- **Luggage** (`hotel.md` section 12) is rolled when a room's guests are first met and
  written in the room's row below. The five R suites and 407 always hold an item:
  `loot.py --floor N --sure --band-up`.

## The Cornerstone's secret

Put back together, the Cornerstone is **the Manager**. Not a person who works upstairs: a
stone figure the size of a door, the Hotel's founder, who was broken into bricks and
mortared into the rooms by the first guests, because the Manager's one rule was that every
stay ends. That is why the Staff fear the inspection, and why nobody has ever checked out.
When the last brick goes in, the Manager stands up in the lobby, straightens its tie and
holds the inspection at once: every bill in the Hotel comes due, every guest checks out
in the same minute, and twenty floors of SRD monsters in pyjamas queue at the desk with
their luggage. Then the Manager turns to Morten, the only guest who paid attention, and
offers him the job. Taking it makes him the Manager (a new campaign from the Staff's side
of the desk, standing with the Staff +3 for good, the Hotel restocking around him).
Refusing it, the Manager thanks him, hands him his bill (cancelled), and breaks itself
into bricks again, to be mortared into the next Hotel; Morten walks out of the front door
into daylight. The Hotel may have an opinion.

## Room states

Written as searched: `unsearched` · `searched, brick` · `searched, no brick` · `empty`.
Luggage: `—` until rolled, then the item or `nothing magic`. Updated after every room.

| Room | Guests (generator row) | Luggage | State |
|---|---|---|---|
| 101 | none (row 1.1 checked out) | — | searched, no brick (Day 1, 10:50) |
| 102 | 1× Axe Beak (1.2), alive | Eyes of Charming: **stolen by Mage Hand, unnoticed** · left: 5 GP and a knick-knack (a feather duster, 5 GP) | searched, no brick (Day 1 12:10; a 5 GP gift) |
| 103 | 1× Giant Lizard (1.3), dead | Spell Scroll of Charm Person (taken) · 5 GP · a tin of scale polish (taken) | searched, no brick (Day 1 13:20) · **restocked Day 2 ~18:00: 1× Boar** (CR 1/4, `gen_dungeon.py --floors 1 --seed 90` row 1; braziers come with it, the room stays 6×8 sq) · luggage — · doesn't know Morten |
| 104 | 1× Black Bear (1.4), dead | nothing magic · 10 GP · a rubber duck with a monocle (taken) | searched, brick (Day 1 14:40) |
| 105 | 1× Violet Fungus (1.5), dead | nothing magic · 5 GP · a violet pressed-flower bookmark (taken) | searched, no brick (Day 1 16:50) |
| 201 | 1× Pirate (2.1), alive | Spell Scroll of False Life (**stolen** by hand, unnoticed) · 20 GP and a knick-knack left | searched, brick (the rumour's) Day 2 08:30. Charmed (Eyes of Charming) 07:30–08:30; the charm ended and **he knows Morten charmed him: Hostile to Morten**, reaction capped at 5 |
| 202 | 3× Skeleton (2.2), alive | nothing magic · 15 GP and a knick-knack left | searched, no brick (Day 2 09:40). One skeleton met as a wanderer, reaction 9, Friendly; it let him in |
| 203 | 2× Giant Wolf Spider (2.3), alive | Potion of Growth (Uncommon, 200 GP; in the suitcase, unseen) · 10 GP | unsearched. Met Day 2 09:50, reaction 5; they killed Morten in the corridor. 8 hours later (GM's call): both back in 203 at full HP, 11/11 |
| 204 | 1× Copper Dragon Wyrmling (2.4) | — | unsearched |
| 403 | 1× Goblin Boss, Resident (4.3, R) | — (sure, band up) | unsearched |
| 407 | 2× Sahuagin Warrior, the Ark (4.7, A) | — (sure, band up) | unsearched |

**Lost and found** (Day 2 respawn, event d6 5, floor 1 rolled): a Bead of Nourishment (Common,
50 GP). Floors 3 and up (other than the marked suites): add rows as Morten reaches them.

## The floors (the generator's output, seed 45)

## Floor 1 (for level 1)

XP needed for level 2: 300 · floor total: 300 · 5 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 1.1 | 2× Mule | 1/8 | 50 | Low | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 5 GP |
| 1.2 | 1× Axe Beak | 1/4 | 50 | Moderate | 6×8 sq (9×12 m) | a narrow 1.5 m entrance (chokepoint) | 5 GP |
| 1.3 | 1× Giant Lizard | 1/4 | 50 | Low | 6×8 sq (9×12 m) | magical darkness in half the room | 5 GP |
| 1.4 | 1× Black Bear | 1/2 | 100 | High | 6×8 sq (9×12 m) | knee-deep water (difficult terrain) | 10 GP |
| 1.5 | 1× Violet Fungus | 1/4 | 50 | Low | 8×8 sq (12×12 m) | a 3 m ledge along one wall (elevation) | 5 GP |

## Floor 2 (for level 2)

XP needed for level 3: 600 · floor total: 650 · 4 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 2.1 | 1× Pirate | 1 | 200 | High | 6×8 sq (9×12 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 2.2 | 3× Skeleton | 1/4 | 150 | Moderate | 6×6 sq (9×9 m) | pillars (full cover) | 15 GP |
| 2.3 | 2× Giant Wolf Spider | 1/4 | 100 | Low | 10×12 sq (15×18 m) | thick fog (heavily obscured beyond 3 m) | 10 GP |
| 2.4 | 1× Copper Dragon Wyrmling | 1 | 200 | High | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 20 GP |

## Floor 3 (for level 3)

XP needed for level 4: 1,800 · floor total: 1,850 · 9 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 3.1 | 1× Giant Seahorse | 1/2 | 100 | Low | 10×12 sq (15×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 10 GP |
| 3.2 | 2× Sphinx of Wonder | 1 | 400 | High | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 40 GP |
| 3.3 | 2× Satyr | 1/2 | 200 | Moderate | 10×10 sq (15×15 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 3.4 | 1× Imp | 1 | 200 | Moderate | 10×12 sq (15×18 m) | a 3 m ledge along one wall (elevation) | 20 GP |
| 3.5 | 2× Satyr | 1/2 | 200 | Moderate | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 20 GP |
| 3.6 | 2× Sahuagin Warrior | 1/2 | 200 | Moderate | 12×12 sq (18×18 m) | magical darkness in half the room | 20 GP |
| 3.7 | 3× Giant Wolf Spider | 1/4 | 150 | Low | 12×12 sq (18×18 m) | knee-deep water (difficult terrain) | 15 GP |
| 3.8 | 1× Pirate | 1 | 200 | Moderate | 6×8 sq (9×12 m) | an open, empty floor | 20 GP |
| 3.9 | 1× Lion | 1 | 200 | Moderate | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 20 GP |

## Floor 4 (for level 4)

XP needed for level 5: 3,800 · floor total: 3,800 · 16 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 4.1 | 1× Wererat | 2 | 450 | High | 10×10 sq (15×15 m) | a chasm crossed by a 1.5 m-wide bridge | 45 GP |
| 4.2 | 1× Dire Wolf | 1 | 200 | Moderate | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 4.3 | 1× Goblin Boss | 1 | 200 | Low | 6×8 sq (9×12 m) | pillars (full cover) | 20 GP |
| 4.4 | 1× Quasit | 1 | 200 | Moderate | 10×12 sq (15×18 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 4.5 | 1× Hippogriff | 1 | 200 | Low | 8×10 sq (12×15 m) | a chasm crossed by a 1.5 m-wide bridge | 20 GP |
| 4.6 | 1× Giant Eagle | 1 | 200 | Low | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 20 GP |
| 4.7 | 2× Ape | 1/2 | 200 | Low | 8×8 sq (12×12 m) | pillars (full cover) | 20 GP |
| 4.8 | 3× Giant Goat | 1/2 | 300 | Moderate | 6×12 sq (9×18 m) | rubble (difficult terrain, half cover) | 30 GP |
| 4.9 | 2× Dust Mephit | 1/2 | 200 | Low | 6×8 sq (9×12 m) | rubble (difficult terrain, half cover) | 20 GP |
| 4.10 | 2× Crocodile | 1/2 | 200 | Low | 12×12 sq (18×18 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 4.11 | 2× Shadow | 1/2 | 200 | Low | 6×12 sq (9×18 m) | statues (half cover) | 20 GP |
| 4.12 | 1× Giant Hyena | 1 | 200 | Moderate | 12×12 sq (18×18 m) | statues (half cover) | 20 GP |
| 4.13 | 1× Ettercap | 2 | 450 | High | 4×12 sq (6×18 m) | pillars (full cover) | 45 GP |
| 4.14 | 2× Reef Shark | 1/2 | 200 | Low | 12×12 sq (18×18 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 20 GP |
| 4.15 | 2× Giant Wasp | 1/2 | 200 | Low | 6×12 sq (9×18 m) | a high ceiling (9 m) with hanging chains | 20 GP |
| 4.16 | 1× Goblin Boss | 1 | 200 | Low | 4×12 sq (6×18 m) | an open, empty floor | 20 GP |

## Floor 5 (for level 5)

XP needed for level 6: 7,500 · floor total: 7,600 · 11 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 5.1 | 1× Warrior Veteran | 3 | 700 | Moderate | 12×12 sq (18×18 m) | a high ceiling (9 m) with hanging chains | 70 GP |
| 5.2 | 1× Silver Dragon Wyrmling | 2 | 450 | Low | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 45 GP |
| 5.3 | 2× Giant Boar | 2 | 900 | High | 8×10 sq (12×15 m) | pillars (full cover) | 90 GP |
| 5.4 | 1× Ochre Jelly | 2 | 450 | Low | 10×10 sq (15×15 m) | a chasm crossed by a 1.5 m-wide bridge | 45 GP |
| 5.5 | 2× Sea Hag | 2 | 900 | High | 12×12 sq (18×18 m) | a high ceiling (9 m) with hanging chains | 90 GP |
| 5.6 | 2× Pirate | 1 | 400 | Low | 6×12 sq (9×18 m) | thick fog (heavily obscured beyond 3 m) | 40 GP |
| 5.7 | 1× Tough Boss | 4 | 1,100 | High | 6×6 sq (9×9 m) | statues (half cover) | 110 GP |
| 5.8 | 1× Ogre Zombie | 2 | 450 | Low | 6×6 sq (9×9 m) | rubble (difficult terrain, half cover) | 45 GP |
| 5.9 | 1× Werewolf | 3 | 700 | Moderate | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 70 GP |
| 5.10 | 1× Couatl | 4 | 1,100 | High | 12×12 sq (18×18 m) | a chasm crossed by a 1.5 m-wide bridge | 110 GP |
| 5.11 | 1× Plesiosaurus | 2 | 450 | Low | 10×12 sq (15×18 m) | thick fog (heavily obscured beyond 3 m) | 45 GP |

## Floor 6 (for level 6)

XP needed for level 7: 9,000 · floor total: 10,300 · 14 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 6.1 | 1× Black Dragon Wyrmling | 2 | 450 | Low | 12×12 sq (18×18 m) | a high ceiling (9 m) with hanging chains | 45 GP |
| 6.2 | 2× Bronze Dragon Wyrmling | 2 | 900 | Moderate | 4×12 sq (6×18 m) | burning braziers (bright light, fire) | 90 GP |
| 6.3 | 3× Giant Spider | 1 | 600 | Low | 6×8 sq (9×12 m) | thick fog (heavily obscured beyond 3 m) | 60 GP |
| 6.4 | 3× Death Dog | 1 | 600 | Low | 10×10 sq (15×15 m) | magical darkness in half the room | 60 GP |
| 6.5 | 2× Ettercap | 2 | 900 | Moderate | 10×12 sq (15×18 m) | statues (half cover) | 90 GP |
| 6.6 | 1× Hobgoblin Captain | 3 | 700 | Moderate | 12×12 sq (18×18 m) | a 3 m ledge along one wall (elevation) | 70 GP |
| 6.7 | 1× Cultist Fanatic | 2 | 450 | Low | 6×8 sq (9×12 m) | an open, empty floor | 45 GP |
| 6.8 | 3× Spy | 1 | 600 | Low | 6×6 sq (9×9 m) | a high ceiling (9 m) with hanging chains | 60 GP |
| 6.9 | 1× Nightmare | 3 | 700 | Moderate | 10×12 sq (15×18 m) | a narrow 1.5 m entrance (chokepoint) | 70 GP |
| 6.10 | 1× Red Dragon Wyrmling | 4 | 1,100 | High | 10×10 sq (15×15 m) | magical darkness in half the room | 110 GP |
| 6.11 | 3× Animated Armor | 1 | 600 | Low | 12×12 sq (18×18 m) | a chasm crossed by a 1.5 m-wide bridge | 60 GP |
| 6.12 | 1× Will-o'-Wisp | 2 | 450 | Low | 10×10 sq (15×15 m) | a 3 m ledge along one wall (elevation) | 45 GP |
| 6.13 | 2× Ghast | 2 | 900 | Moderate | 6×12 sq (9×18 m) | an open, empty floor | 90 GP |
| 6.14 | 3× Pegasus | 2 | 1,350 | High | 6×8 sq (9×12 m) | rubble (difficult terrain, half cover) | 135 GP |

## Floor 7 (for level 7)

XP needed for level 8: 11,000 · floor total: 11,350 · 15 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 7.1 | 1× Red Dragon Wyrmling | 4 | 1,100 | High | 12×12 sq (18×18 m) | a chasm crossed by a 1.5 m-wide bridge | 110 GP |
| 7.2 | 1× Ogre | 2 | 450 | Low | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 45 GP |
| 7.3 | 2× Saber-Toothed Tiger | 2 | 900 | Moderate | 6×12 sq (9×18 m) | burning braziers (bright light, fire) | 90 GP |
| 7.4 | 1× Hunter Shark | 2 | 450 | Low | 8×10 sq (12×15 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 45 GP |
| 7.5 | 1× Giant Scorpion | 3 | 700 | Moderate | 6×6 sq (9×9 m) | a chasm crossed by a 1.5 m-wide bridge | 70 GP |
| 7.6 | 3× Ghoul | 1 | 600 | Low | 6×12 sq (9×18 m) | an open, empty floor | 60 GP |
| 7.7 | 1× Incubus | 4 | 1,100 | Moderate | 8×8 sq (12×12 m) | a chasm crossed by a 1.5 m-wide bridge | 110 GP |
| 7.8 | 1× Will-o'-Wisp | 2 | 450 | Low | 10×10 sq (15×15 m) | a high ceiling (9 m) with hanging chains | 45 GP |
| 7.9 | 2× Doppelganger | 3 | 1,400 | High | 4×12 sq (6×18 m) | magical darkness in half the room | 140 GP |
| 7.10 | 1× Minotaur Skeleton | 2 | 450 | Low | 4×12 sq (6×18 m) | an open, empty floor | 45 GP |
| 7.11 | 1× Weretiger | 4 | 1,100 | High | 8×8 sq (12×12 m) | a chasm crossed by a 1.5 m-wide bridge | 110 GP |
| 7.12 | 1× Green Hag | 3 | 700 | Moderate | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 70 GP |
| 7.13 | 1× Cultist Fanatic | 2 | 450 | Low | 6×8 sq (9×12 m) | burning braziers (bright light, fire) | 45 GP |
| 7.14 | 2× Green Dragon Wyrmling | 2 | 900 | Moderate | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 90 GP |
| 7.15 | 3× Imp | 1 | 600 | Low | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 60 GP |

## Floor 8 (for level 8)

XP needed for level 9: 14,000 · floor total: 15,950 · 12 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 8.1 | 1× Water Elemental | 5 | 1,800 | High | 6×12 sq (9×18 m) | statues (half cover) | 180 GP |
| 8.2 | 2× Manticore | 3 | 1,400 | Moderate | 8×8 sq (12×12 m) | a narrow 1.5 m entrance (chokepoint) | 140 GP |
| 8.3 | 2× Cultist Fanatic | 2 | 900 | Low | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 90 GP |
| 8.4 | 2× Berserker | 2 | 900 | Low | 8×8 sq (12×12 m) | pillars (full cover) | 90 GP |
| 8.5 | 3× Gold Dragon Wyrmling | 3 | 2,100 | High | 10×10 sq (15×15 m) | pillars (full cover) | 210 GP |
| 8.6 | 1× Chuul | 4 | 1,100 | High | 6×6 sq (9×9 m) | statues (half cover) | 110 GP |
| 8.7 | 1× Swarm of Crawling Claws | 3 | 700 | Low | 12×12 sq (18×18 m) | knee-deep water (difficult terrain) | 70 GP |
| 8.8 | 1× Wraith | 5 | 1,800 | High | 4×12 sq (6×18 m) | a high ceiling (9 m) with hanging chains | 180 GP |
| 8.9 | 2× White Dragon Wyrmling | 2 | 900 | Low | 6×6 sq (9×9 m) | magical darkness in half the room | 90 GP |
| 8.10 | 2× Rhinoceros | 2 | 900 | Low | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 90 GP |
| 8.11 | 3× Bronze Dragon Wyrmling | 2 | 1,350 | Moderate | 8×8 sq (12×12 m) | a narrow 1.5 m entrance (chokepoint) | 135 GP |
| 8.12 | 3× Phase Spider | 3 | 2,100 | High | 10×12 sq (15×18 m) | thick fog (heavily obscured beyond 3 m) | 210 GP |

## Floor 9 (for level 9)

XP needed for level 10: 16,000 · floor total: 16,100 · 10 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 9.1 | 1× Gladiator | 5 | 1,800 | High | 10×12 sq (15×18 m) | statues (half cover) | 180 GP |
| 9.2 | 2× Manticore | 3 | 1,400 | Moderate | 8×10 sq (12×15 m) | knee-deep water (difficult terrain) | 140 GP |
| 9.3 | 1× Fire Elemental | 5 | 1,800 | Moderate | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 180 GP |
| 9.4 | 2× Knight | 3 | 1,400 | Moderate | 6×12 sq (9×18 m) | burning braziers (bright light, fire) | 140 GP |
| 9.5 | 1× Roper | 5 | 1,800 | Moderate | 10×10 sq (15×15 m) | rubble (difficult terrain, half cover) | 180 GP |
| 9.6 | 2× Ghast | 2 | 900 | Low | 10×12 sq (15×18 m) | a chasm crossed by a 1.5 m-wide bridge | 90 GP |
| 9.7 | 1× Water Elemental | 5 | 1,800 | Moderate | 10×10 sq (15×15 m) | a 3 m ledge along one wall (elevation) | 180 GP |
| 9.8 | 1× Tough Boss | 4 | 1,100 | Low | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 110 GP |
| 9.9 | 1× Gorgon | 5 | 1,800 | Moderate | 8×8 sq (12×12 m) | thick fog (heavily obscured beyond 3 m) | 180 GP |
| 9.10 | 1× Mage | 6 | 2,300 | High | 10×10 sq (15×15 m) | burning braziers (bright light, fire) | 230 GP |

## Floor 10 (for level 10)

XP needed for level 11: 21,000 · floor total: 21,500 · 12 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 10.1 | 1× Lamia | 4 | 1,100 | Low | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 110 GP |
| 10.2 | 2× Archelon | 4 | 2,200 | Moderate | 8×8 sq (12×12 m) | burning braziers (bright light, fire) | 220 GP |
| 10.3 | 1× Barbed Devil | 5 | 1,800 | Moderate | 10×12 sq (15×18 m) | a 3 m ledge along one wall (elevation) | 180 GP |
| 10.4 | 1× Werebear | 5 | 1,800 | High | 10×12 sq (15×18 m) | an open, empty floor | 180 GP |
| 10.5 | 3× Black Dragon Wyrmling | 2 | 1,350 | Low | 8×10 sq (12×15 m) | a narrow 1.5 m entrance (chokepoint) | 135 GP |
| 10.6 | 1× Tough Boss | 4 | 1,100 | Low | 6×12 sq (9×18 m) | a 3 m ledge along one wall (elevation) | 110 GP |
| 10.7 | 2× Lamia | 4 | 2,200 | Moderate | 4×12 sq (6×18 m) | thick fog (heavily obscured beyond 3 m) | 220 GP |
| 10.8 | 2× Warrior Veteran | 3 | 1,400 | Low | 8×8 sq (12×12 m) | a high ceiling (9 m) with hanging chains | 140 GP |
| 10.9 | 3× Will-o'-Wisp | 2 | 1,350 | Low | 8×8 sq (12×12 m) | a 3 m ledge along one wall (elevation) | 135 GP |
| 10.10 | 1× Shield Guardian | 7 | 2,900 | High | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 290 GP |
| 10.11 | 3× Owlbear | 3 | 2,100 | Moderate | 10×10 sq (15×15 m) | an open, empty floor | 210 GP |
| 10.12 | 2× Succubus | 4 | 2,200 | Moderate | 8×10 sq (12×15 m) | statues (half cover) | 220 GP |

## Floor 11 (for level 11)

XP needed for level 12: 15,000 · floor total: 17,100 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 11.1 | 2× Warrior Veteran | 3 | 1,400 | Low | 4×12 sq (6×18 m) | an open, empty floor | 140 GP |
| 11.2 | 2× Succubus | 4 | 2,200 | Moderate | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 220 GP |
| 11.3 | 2× Winter Wolf | 3 | 1,400 | Low | 12×12 sq (18×18 m) | burning braziers (bright light, fire) | 140 GP |
| 11.4 | 1× Shield Guardian | 7 | 2,900 | High | 12×12 sq (18×18 m) | a chasm crossed by a 1.5 m-wide bridge | 290 GP |
| 11.5 | 2× Barbed Devil | 5 | 3,600 | High | 12×12 sq (18×18 m) | a 3 m ledge along one wall (elevation) | 360 GP |
| 11.6 | 1× Pirate Captain | 6 | 2,300 | Moderate | 6×6 sq (9×9 m) | thick fog (heavily obscured beyond 3 m) | 230 GP |
| 11.7 | 3× Guard Captain | 4 | 3,300 | High | 10×10 sq (15×15 m) | burning braziers (bright light, fire) | 330 GP |

## Floor 12 (for level 12)

XP needed for level 13: 20,000 · floor total: 21,400 · 8 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 12.1 | 2× Hill Giant | 5 | 3,600 | Moderate | 6×12 sq (9×18 m) | a 3 m ledge along one wall (elevation) | 360 GP |
| 12.2 | 1× Hezrou | 8 | 3,900 | High | 4×12 sq (6×18 m) | an open, empty floor | 390 GP |
| 12.3 | 2× Giant Shark | 5 | 3,600 | Moderate | 8×10 sq (12×15 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 360 GP |
| 12.4 | 2× Red Dragon Wyrmling | 4 | 2,200 | Low | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 220 GP |
| 12.5 | 1× Otyugh | 5 | 1,800 | Low | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 180 GP |
| 12.6 | 1× Medusa | 6 | 2,300 | Moderate | 10×10 sq (15×15 m) | knee-deep water (difficult terrain) | 230 GP |
| 12.7 | 1× Werebear | 5 | 1,800 | Low | 6×12 sq (9×18 m) | thick fog (heavily obscured beyond 3 m) | 180 GP |
| 12.8 | 2× Hippopotamus | 4 | 2,200 | Low | 6×6 sq (9×9 m) | burning braziers (bright light, fire) | 220 GP |

## Floor 13 (for level 13)

XP needed for level 14: 20,000 · floor total: 23,900 · 6 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 13.1 | 2× Vrock | 6 | 4,600 | High | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 460 GP |
| 13.2 | 3× Phase Spider | 3 | 2,100 | Low | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 210 GP |
| 13.3 | 2× Troll | 5 | 3,600 | Moderate | 4×12 sq (6×18 m) | rubble (difficult terrain, half cover) | 360 GP |
| 13.4 | 2× Gladiator | 5 | 3,600 | Moderate | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 360 GP |
| 13.5 | 3× Triceratops | 5 | 5,400 | High | 6×12 sq (9×18 m) | a chasm crossed by a 1.5 m-wide bridge | 540 GP |
| 13.6 | 2× Wyvern | 6 | 4,600 | High | 4×12 sq (6×18 m) | a chasm crossed by a 1.5 m-wide bridge | 460 GP |

## Floor 14 (for level 14)

XP needed for level 15: 25,000 · floor total: 25,400 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 14.1 | 2× Medusa | 6 | 4,600 | Moderate | 8×8 sq (12×12 m) | a chasm crossed by a 1.5 m-wide bridge | 460 GP |
| 14.2 | 1× Giant Shark | 5 | 1,800 | Low | 6×6 sq (9×9 m) | flooded: water 3 m deep, a 1.5 m ledge around the edge | 180 GP |
| 14.3 | 1× Young Silver Dragon | 9 | 5,000 | High | 6×6 sq (9×9 m) | a narrow 1.5 m entrance (chokepoint) | 500 GP |
| 14.4 | 2× Wraith | 5 | 3,600 | Moderate | 8×8 sq (12×12 m) | an open, empty floor | 360 GP |
| 14.5 | 1× Stone Giant | 7 | 2,900 | Moderate | 10×10 sq (15×15 m) | a 3 m ledge along one wall (elevation) | 290 GP |
| 14.6 | 1× Spirit Naga | 8 | 3,900 | High | 8×10 sq (12×15 m) | pillars (full cover) | 390 GP |
| 14.7 | 2× Bulette | 5 | 3,600 | Moderate | 6×12 sq (9×18 m) | a chasm crossed by a 1.5 m-wide bridge | 360 GP |

## Floor 15 (for level 15)

XP needed for level 16: 30,000 · floor total: 32,900 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 15.1 | 2× Young Brass Dragon | 6 | 4,600 | Moderate | 6×8 sq (9×12 m) | magical darkness in half the room | 460 GP |
| 15.2 | 1× Half-Dragon | 5 | 1,800 | Low | 10×12 sq (15×18 m) | a high ceiling (9 m) with hanging chains | 180 GP |
| 15.3 | 1× Young Blue Dragon | 9 | 5,000 | Moderate | 12×12 sq (18×18 m) | a 3 m ledge along one wall (elevation) | 500 GP |
| 15.4 | 3× Young White Dragon | 6 | 6,900 | High | 6×12 sq (9×18 m) | pillars (full cover) | 690 GP |
| 15.5 | 1× Fire Giant | 9 | 5,000 | High | 10×12 sq (15×18 m) | pillars (full cover) | 500 GP |
| 15.6 | 2× Chimera | 6 | 4,600 | Moderate | 8×10 sq (12×15 m) | a high ceiling (9 m) with hanging chains | 460 GP |
| 15.7 | 1× Young Blue Dragon | 9 | 5,000 | High | 6×6 sq (9×9 m) | knee-deep water (difficult terrain) | 500 GP |

## Floor 16 (for level 16)

XP needed for level 17: 30,000 · floor total: 37,000 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 16.1 | 3× Flesh Golem | 5 | 5,400 | Moderate | 10×12 sq (15×18 m) | statues (half cover) | 540 GP |
| 16.2 | 1× Cloud Giant | 9 | 5,000 | Moderate | 8×8 sq (12×12 m) | thick fog (heavily obscured beyond 3 m) | 500 GP |
| 16.3 | 3× Hippopotamus | 4 | 3,300 | Low | 10×12 sq (15×18 m) | an open, empty floor | 330 GP |
| 16.4 | 3× Red Dragon Wyrmling | 4 | 3,300 | Low | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 330 GP |
| 16.5 | 3× Gladiator | 5 | 5,400 | Moderate | 6×12 sq (9×18 m) | a 3 m ledge along one wall (elevation) | 540 GP |
| 16.6 | 1× Deva | 10 | 5,900 | High | 8×10 sq (12×15 m) | an open, empty floor | 590 GP |
| 16.7 | 3× Oni | 7 | 8,700 | High | 4×12 sq (6×18 m) | statues (half cover) | 870 GP |

## Floor 17 (for level 17)

XP needed for level 18: 40,000 · floor total: 41,600 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 17.1 | 1× Frost Giant | 8 | 3,900 | Moderate | 10×10 sq (15×15 m) | burning braziers (bright light, fire) | 390 GP |
| 17.2 | 4× Fire Elemental | 5 | 7,200 | Moderate | 6×12 sq (9×18 m) | a narrow 1.5 m entrance (chokepoint) | 720 GP |
| 17.3 | 1× Roc | 11 | 7,200 | High | 8×8 sq (12×12 m) | burning braziers (bright light, fire) | 720 GP |
| 17.4 | 1× Horned Devil | 11 | 7,200 | Moderate | 10×10 sq (15×15 m) | thick fog (heavily obscured beyond 3 m) | 720 GP |
| 17.5 | 1× Hydra | 8 | 3,900 | Moderate | 8×8 sq (12×12 m) | rubble (difficult terrain, half cover) | 390 GP |
| 17.6 | 4× Earth Elemental | 5 | 7,200 | Moderate | 6×12 sq (9×18 m) | pillars (full cover) | 720 GP |
| 17.7 | 1× Bone Devil | 9 | 5,000 | Moderate | 6×8 sq (9×12 m) | pillars (full cover) | 500 GP |

## Floor 18 (for level 18)

XP needed for level 19: 40,000 · floor total: 40,700 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 18.1 | 1× Archmage | 12 | 8,000 | Moderate | 6×6 sq (9×9 m) | a 3 m ledge along one wall (elevation) | 800 GP |
| 18.2 | 1× Purple Worm | 15 | 13,000 | High | 4×12 sq (6×18 m) | a high ceiling (9 m) with hanging chains | 1,300 GP |
| 18.3 | 1× Shield Guardian | 7 | 2,900 | Low | 8×10 sq (12×15 m) | a 3 m ledge along one wall (elevation) | 290 GP |
| 18.4 | 2× Half-Dragon | 5 | 3,600 | Low | 10×10 sq (15×15 m) | pillars (full cover) | 360 GP |
| 18.5 | 2× Giant Crocodile | 5 | 3,600 | Low | 12×12 sq (18×18 m) | knee-deep water (difficult terrain) | 360 GP |
| 18.6 | 2× Wyvern | 6 | 4,600 | Low | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 460 GP |
| 18.7 | 1× Treant | 9 | 5,000 | Moderate | 8×8 sq (12×12 m) | a 3 m ledge along one wall (elevation) | 500 GP |

## Floor 19 (for level 19)

XP needed for level 20: 50,000 · floor total: 50,300 · 7 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 19.1 | 3× Otyugh | 5 | 5,400 | Low | 10×12 sq (15×18 m) | a high ceiling (9 m) with hanging chains | 540 GP |
| 19.2 | 1× Adult Bronze Dragon | 15 | 13,000 | High | 6×12 sq (9×18 m) | burning braziers (bright light, fire) | 1,300 GP |
| 19.3 | 1× Giant Ape | 7 | 2,900 | Low | 8×8 sq (12×12 m) | a 3 m ledge along one wall (elevation) | 290 GP |
| 19.4 | 2× Invisible Stalker | 6 | 4,600 | Low | 6×8 sq (9×12 m) | magical darkness in half the room | 460 GP |
| 19.5 | 1× Adult White Dragon | 13 | 10,000 | Moderate | 8×10 sq (12×15 m) | a narrow 1.5 m entrance (chokepoint) | 1,000 GP |
| 19.6 | 1× Efreeti | 11 | 7,200 | Moderate | 12×12 sq (18×18 m) | burning braziers (bright light, fire) | 720 GP |
| 19.7 | 1× Remorhaz | 11 | 7,200 | Moderate | 4×12 sq (6×18 m) | a narrow 1.5 m entrance (chokepoint) | 720 GP |

## Floor 20 (for level 20)

Final floor, XP target: 50,000 · floor total: 56,500 · 6 encounters

| Room | Encounter | CR | XP | Difficulty | Room size | Feature | Coins |
|---|---|---|---|---|---|---|---|
| 20.1 | 1× Deva | 10 | 5,900 | Low | 8×8 sq (12×12 m) | an open, empty floor | 590 GP |
| 20.2 | 2× Deva | 10 | 11,800 | Moderate | 12×12 sq (18×18 m) | rubble (difficult terrain, half cover) | 1,180 GP |
| 20.3 | 3× Air Elemental | 5 | 5,400 | Low | 10×12 sq (15×18 m) | knee-deep water (difficult terrain) | 540 GP |
| 20.4 | 3× Otyugh | 5 | 5,400 | Low | 8×10 sq (12×15 m) | rubble (difficult terrain, half cover) | 540 GP |
| 20.5 | 1× Adult Bronze Dragon | 15 | 13,000 | Moderate | 6×6 sq (9×9 m) | magical darkness in half the room | 1,300 GP |
| 20.6 | 1× Adult Silver Dragon | 16 | 15,000 | High | 6×8 sq (9×12 m) | knee-deep water (difficult terrain) | 1,500 GP |

