# GM secrets · hotel1 (Hotel Meridian, seed 64)

Only the GM reads this file. Never show it to the AI player.

## The Cornerstone's secret

The Hotel is the civilisation nobody remembers. It was a city that built one hotel and then
kept building it, street by street, until every house was a room and every citizen a guest;
the guests are what is left of them, given new shapes and no memory. The **Manager** is the
city's last mayor, who broke themself into the Cornerstone's bricks and mortared them into
the rooms to stop the Hotel growing. That is why the Staff fear "the inspection": the
Manager coming back together. Morten hears the bricks because he is the mayor's
grandchild, born in the last house before it became room 100.

When the last brick goes in, the Manager stands up out of the Cornerstone in the lobby,
politely, and offers Morten one of two things:
- **Take the keys.** Morten becomes the Manager. The Hotel stops growing for as long as he
  stays, and he can never leave it.
- **Let me check out.** The Manager leaves, the Hotel stands still, and for the first time in
  centuries the front doors open on a street. Every guest may walk out in their pyjamas, and
  most of them will remember who they were. The Ark will not like this; the Residents will
  be furious and then grateful.

The Hotel's opinion: it would rather he took the keys.

## Marks

- **R (Residents)**, rolled 1d12 per odd floor (7, 2, 4, 2, 3):
  - **107** · 3 Kobold Grand-Wizards · spokes-kobold **Grand-Wizard Pim** (with Nib and Tallow). Floor 1's gossip.
  - **302** · Ghoul · **Mr Ossery**, a retired undertaker.
  - **504** · 2 Derro Maniacs · **the Hask twins**.
  - **702** · 3 Beast Gauntlet's Mascots · **Bramble, Thorn and Fig**.
  - **903** · Plant Briar Elf Sorcerer · **Lady Wend**.
- **A (the Ark's suite)**: **105** · Skin Devil · **Mr Vellum**, who keeps the list. (Already a devil; no reroll.)
- A Resident's suite and the Ark's suite always hold a true item (`loot.py --true <tier>`), rolled at first meeting.

## Room state

All 120 rooms unsearched. Updated as play goes: unsearched · searched, brick · searched, empty · restocked by …

## Luggage rolled

(none yet: rolled when a room's guests are first met)

## The shop (public, also in state.md)

- Shelf: healing potions (adventurer, 50 gp) always in stock; the three rolled one-use items (restock Day 8) also came up healing potions (adventurer).
- Window (reroll Day 8 or when sold): Adroit Avoidance (cloak, adventurer, recharge 6+): when ongoing damage a save ends hits him, an immediate save. Quirk: doesn't notice social slights or insults. 300 gp.

## The generator's floors

# The Hotel · seed 64

Worth: what the room's guests count as for one character (1 = one standard monster, Building-Battles.md). Mooks fight as one mob sharing its HP.

## Floor 1 · level 1 · adventurer tier (same level = monster level 1)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 3 × Meteorite Xombie | 1 | mook · mook | 17/11/15 | 7 (mob 21) | +8 | 1.00 | Normal | a fireplace, lit (fire to grab, push into, or put out) | 15 |
| 102 | 3 × Bone Imp Mage-Eater | 2 | mook · mook | 18/12/16 | 4 (mob 12) | +10 | 1.50 | Hard | wardrobes (something can hide behind one; reaching it from the door is a move) | 15 |
| 103 | 1 × Wererat | 2 | troop · normal | 15/14/18 | 34 | +11 | 1.50 | Hard | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 25 |
| 104 | 1 × Giant Scorpion | 1 | wrecker · normal | 16/15/10 | 22 | +6 | 1.00 | Normal | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 15 |
| 105 | 1 × Skin Devil | 2 | troop · weakling | 17/16/16 | 28 | +6 | 0.75 | Easy | wardrobes (something can hide behind one; reaching it from the door is a move) | 30 |
| 106 | 3 × Dire Rat | 1 | mook · mook | 15/15/10 | 6 (mob 18) | +2 | 1.00 | Normal | overturned furniture (moving through the room's middle is a dicey move) | 15 |
| 107 | 3 × Kobold Grand-Wizard | 0 | mook · mook | 15/13/9 | 5 (mob 15) | +8 | 0.75 | Easy | wardrobes (something can hide behind one; reaching it from the door is a move) | 20 |
| 108 | 1 × Fungaloid Creeper | 1 | troop · normal | 16/15/10 | 30 | +3 | 1.00 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 25 |
| 109 | 3 × Meteorite Xombie | 1 | mook · mook | 17/11/15 | 7 (mob 21) | +8 | 1.00 | Normal | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 20 |
| 110 | 1 × Fast Xombie | 0 | spoiler · normal | 16/10/14 | 20 | +8 | 0.70 | Easy | a balcony over the street, three floors up or more | 30 |
| 111 | 1 × Skin Devil | 2 | troop · weakling | 17/16/16 | 28 | +6 | 0.75 | Easy | the lights out (darkness: bring a light, or fight blind) | 30 |
| 112 | 3 × Meteorite Xombie | 1 | mook · mook | 17/11/15 | 7 (mob 21) | +8 | 1.00 | Normal | the lights out (darkness: bring a light, or fight blind) | 25 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Fast-Xombie.md` · `13th-age/srd/Bestiary/Aberration/Star-Masks/Meteorite-Xombie.md` · `13th-age/srd/Bestiary/Beast/Animal-Critter/Dire-Rat.md` · `13th-age/srd/Bestiary/Beast/Animal-Critter/Giant-Scorpion.md` · `13th-age/srd/Bestiary/Beast/Werebeasts/Wererat.md` · `13th-age/srd/Bestiary/Demon/Bone-Imp/Bone-Imp-Mage-Eater.md` · `13th-age/srd/Bestiary/Devil/Skin-Devil.md` · `13th-age/srd/Bestiary/Humanoid/Kobolds/Kobold-Grand-Wizard.md` · `13th-age/srd/Bestiary/Plant/Fungaloid/Fungaloid-Creeper.md`

## Floor 2 · level 2 · adventurer tier (same level = monster level 2)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 201 | 3 × Dainty Lizard | 1 | mook · mook | 16/14/12 | 9 (mob 27) | +5 | 0.75 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 20 |
| 202 | 3 × Demonic-Icon-Fanatic | 2 | mook · mook | 17/16/13 | 10 (mob 30) | +4 | 1.00 | Normal | a hole in the floor into the room below (a dicey move next to it can drop someone) | 35 |
| 203 | 1 × Kobold Hero | 2 | leader · normal | 18/16/12 | 34 | +3 | 1.00 | Normal | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 40 |
| 204 | 1 × Orcish Archer | 2 | archer · normal | 18/17/11 | 32 | +5 | 1.00 | Normal | a balcony over the street, three floors up or more | 40 |
| 205 | 3 × Ettercap Acolyte | 1 | mook · mook | 16/13/15 | 7 (mob 21) | +2 | 0.75 | Easy | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 15 |
| 206 | 3 × Newly Risen Ghoul | 2 | mook · mook | 17/15/11 | 9 (mob 27) | +5 | 1.00 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 35 |
| 207 | 1 × Intellect Devourer | 3 | spoiler · normal | 19/15/19 | 56 | +5 | 1.50 | Hard | a balcony over the street, three floors up or more | 25 |
| 208 | 1 × Kobold Warrior | 1 | troop · normal | 18/15/12 | 22 | +4 | 0.70 | Easy | a hole in the floor into the room below (a dicey move next to it can drop someone) | 15 |
| 209 | 1 × Kobold Warrior | 1 | troop · normal | 18/15/12 | 22 | +4 | 0.70 | Easy | a fireplace, lit (fire to grab, push into, or put out) | 40 |
| 210 | 1 × Orc Shaman | 2 | leader · normal | 18/12/16 | 36 | +5 | 1.00 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 25 |
| 211 | 1 × Splotchcap | 2 | archer · normal | 16/17/14 | 32 | +8 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 40 |
| 212 | 3 × Jackal Gravewrecker | 2 | mook · mook | 17/15/12 | 9 (mob 27) | +4 (+2 when physically carrying a corpse) | 1.00 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 20 |

Files: `13th-age/srd/Bestiary/Aberration/Intellect-Devourers/Intellect-Devourer.md` · `13th-age/srd/Bestiary/Beast/Thunder-Lizard/Dainty-Lizard.md` · `13th-age/srd/Bestiary/Humanoid/Demonic-Icon-Cult/Demonic-Icon-Fanatic.md` · `13th-age/srd/Bestiary/Humanoid/Ettercap/Ettercap-Acolyte.md` · `13th-age/srd/Bestiary/Humanoid/Fallen-Icon-of-Undead/Jackal-Gravewrecker.md` · `13th-age/srd/Bestiary/Humanoid/Kobolds/Kobold-Hero.md` · `13th-age/srd/Bestiary/Humanoid/Kobolds/Kobold-Warrior.md` · `13th-age/srd/Bestiary/Humanoid/Orcs/Orc-Shaman.md` · `13th-age/srd/Bestiary/Humanoid/Orcs/Orcish-Archer.md` · `13th-age/srd/Bestiary/Humanoid/Redcaps/Splotchcap.md` · `13th-age/srd/Bestiary/Undead/Ghouls/Newly-Risen-Ghoul.md`

## Floor 3 · level 3 · adventurer tier (same level = monster level 3)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 301 | 1 × Frogspawn Monk | 3 | spoiler · normal | 18/18/14 | 45 | +8 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 25 |
| 302 | 1 × Ghoul | 3 | spoiler · normal | 18/16/12 | 36 | +8 | 1.00 | Normal | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 60 |
| 303 | 1 × Sporrior | 2 | wrecker · normal | 18/16/12 | 36 | +10 | 0.70 | Easy | a hole in the floor into the room below (a dicey move next to it can drop someone) | 65 |
| 304 | 2 × Skeleton Warrior | 2 | troop · normal | 16/14/11 | 26 | +8 | 1.40 | Hard | wardrobes (something can hide behind one; reaching it from the door is a move) | 35 |
| 305 | 4 × Frogspawn Grunt | 2 | mook · mook | 16/15/11 | 7 (mob 28) | +6 | 0.75 | Easy | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 50 |
| 306 | 1 × Lethal Lothario | 4 | leader · normal | 20/18/17 | 50 | +7 | 1.50 | Hard | the lights out (darkness: bring a light, or fight blind) | 60 |
| 307 | 6 × Zombie Shuffler | 1 | mook · mook | 14/12/8 | 10 (mob 60) | +0 | 0.75 | Easy | a hole in the floor into the room below (a dicey move next to it can drop someone) | 25 |
| 308 | 4 × Newly Risen Ghoul | 2 | mook · mook | 17/15/11 | 9 (mob 36) | +5 | 0.75 | Easy | a hole in the floor into the room below (a dicey move next to it can drop someone) | 50 |
| 309 | 6 × Meteorite Xombie | 1 | mook · mook | 17/11/15 | 7 (mob 42) | +8 | 0.75 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 35 |
| 310 | 1 × Ghoul | 3 | spoiler · normal | 18/16/12 | 36 | +8 | 1.00 | Normal | wardrobes (something can hide behind one; reaching it from the door is a move) | 60 |
| 311 | 1 × Bugbear | 3 | troop · normal | 19/17/12 | 55 | +6 | 1.00 | Normal | wardrobes (something can hide behind one; reaching it from the door is a move) | 55 |
| 312 | 8 × Zombie Shuffler | 1 | mook · mook | 14/12/8 | 10 (mob 80) | +0 | 1.00 | Normal | a fireplace, lit (fire to grab, push into, or put out) | 40 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Meteorite-Xombie.md` · `13th-age/srd/Bestiary/Humanoid/Frogfolk/Frogspawn-Grunt.md` · `13th-age/srd/Bestiary/Humanoid/Frogfolk/Frogspawn-Monk.md` · `13th-age/srd/Bestiary/Humanoid/Goblin/Bugbear.md` · `13th-age/srd/Bestiary/Humanoid/Jorogumo/Lethal-Lothario.md` · `13th-age/srd/Bestiary/Plant/Fungaloid/Sporrior.md` · `13th-age/srd/Bestiary/Undead/Ghouls/Ghoul.md` · `13th-age/srd/Bestiary/Undead/Ghouls/Newly-Risen-Ghoul.md` · `13th-age/srd/Bestiary/Undead/Skeletons/Skeleton-Warrior.md` · `13th-age/srd/Bestiary/Undead/Zombies/Zombie-Shuffler.md`

## Floor 4 · level 4 · adventurer tier (same level = monster level 4)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 401 | 6 × Razor Shark | 2 | mook · mook | 17/14/11 | 10 (mob 60) | +6 | 0.75 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 30 |
| 402 | 1 × Snowy Owlbear | 3 | spoiler · large | 19/17/14 | 94 | +8 | 1.50 | Hard | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 55 |
| 403 | 1 × Trog Chanter | 3 | leader · normal | 19/16/18 | 44 | +5 | 0.70 | Easy | a bare, empty room | 40 |
| 404 | 1 × Giant Web Spider | 2 | blocker · large | 17/16/12 | 68 | +4 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 55 |
| 405 | 2 × Kobold Hero | 2 | leader · normal | 18/16/12 | 34 | +3 | 1.00 | Normal | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 60 |
| 406 | 8 × Bloody Shade | 2 | mook · mook | 18/16/12 | 18 (mob 144) | +4 | 1.00 | Normal | a fireplace, lit (fire to grab, push into, or put out) | 35 |
| 407 | 1 × Whitescale Rime Walker | 5 | troop · normal | 20/18/13 | 65 | +7 | 1.50 | Hard | a balcony over the street, three floors up or more | 50 |
| 408 | 1 × Kobold Engineer | 3 | leader · normal | 19/17/13 | 45 | +8 | 0.70 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 75 |
| 409 | 8 × Frogspawn Grunt | 2 | mook · mook | 16/15/11 | 7 (mob 56) | +6 | 1.00 | Normal | overturned furniture (moving through the room's middle is a dicey move) | 45 |
| 410 | 1 × Sprite | 4 | caster · normal | 21/15/17 | 46 | +11 | 1.00 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 30 |
| 411 | 1 × Medium Copper Dragon | 4 | spoiler · normal | 19/14/18 | 44 | +9 | 1.00 | Normal | wardrobes (something can hide behind one; reaching it from the door is a move) | 70 |
| 412 | 2 × Orc Battle Screamer | 3 | leader · normal | 22/15/15 | 33 | +8 | 1.40 | Hard | overturned furniture (moving through the room's middle is a dicey move) | 60 |

Files: `13th-age/srd/Bestiary/Beast/Animal-Critter/Giant-Web-Spider.md` · `13th-age/srd/Bestiary/Beast/Owlbear/Snowy-Owlbear.md` · `13th-age/srd/Bestiary/Beast/Sahuagin-Beasts/Razor-Shark.md` · `13th-age/srd/Bestiary/Dragon/Metallic-Dragon/Copper-Dragons/Medium-Copper-Dragon.md` · `13th-age/srd/Bestiary/Humanoid/Fey/Sprite.md` · `13th-age/srd/Bestiary/Humanoid/Frogfolk/Frogspawn-Grunt.md` · `13th-age/srd/Bestiary/Humanoid/Kobolds/Kobold-Engineer.md` · `13th-age/srd/Bestiary/Humanoid/Kobolds/Kobold-Hero.md` · `13th-age/srd/Bestiary/Humanoid/Kroma-Dragonic/Whitescale-Rime-Walker.md` · `13th-age/srd/Bestiary/Humanoid/Orcs/Orc-Battle-Screamer.md` · `13th-age/srd/Bestiary/Humanoid/Troglodytes/Trog-Chanter.md` · `13th-age/srd/Bestiary/Undead/Battle-Shade/Bloody-Shade.md`

## Floor 5 · level 5 · champion tier (same level = monster level 6)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 501 | 1 × Faun Keeper | 5 | blocker · normal | 22/15 or 18/18 or 15 | 70 | +6 | 0.70 | Easy | a bare, empty room | 65 |
| 502 | 5 × Summoned Ghoul | 7 | mook · mook | 24/20/16 | 25 (mob 125) | +14 (or immediately after summoner if summoned during a battle) | 1.50 | Hard | a fireplace, lit (fire to grab, push into, or put out) | 40 |
| 503 | 3 × Death Marker | 6 | mook · mook | 22/16/20 | 25 (mob 75) | +9 | 0.60 | Easy | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 65 |
| 504 | 2 × Derro Maniac | 4 | troop · normal | 19/16/18 | 52 | +8 | 1.00 | Normal | a hole in the floor into the room below (a dicey move next to it can drop someone) | 65 |
| 505 | 1 × Sahuagin Glow Priest | 5 | caster · normal | 21/16/19 | 70 | +10 | 0.70 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 70 |
| 506 | 1 × Wild Naiad | 5 | spoiler · large | 20/20/16 | 130 | +11 | 1.50 | Hard | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 90 |
| 507 | 8 × Kobold Shadow-Warrior | 4 | mook · mook | 20/13/17 | 14 (mob 112) | +9 | 0.80 | Normal | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 55 |
| 508 | 3 × Major Haunting | 6 | mook · mook | 21/19/16 | 18 (mob 54) | +9 | 0.60 | Easy | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 65 |
| 509 | 1 × Swarm Prince | 5 | spoiler · normal | 19/18/16 | 80 | +9 | 0.70 | Easy | the lights out (darkness: bring a light, or fight blind) | 55 |
| 510 | 1 × Brain-Absorber Xombie | 4 | caster · large | 20/16/20 | 90 | +10 | 1.00 | Normal | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 80 |
| 511 | 8 × Ravenous Cannibal | 4 | mook · mook | 18/15/11 | 13 (mob 104) | +9 | 0.80 | Normal | the lights out (darkness: bring a light, or fight blind) | 40 |
| 512 | 2 × Ghoul Licklash | 4 | blocker · normal | 21/17/13 | 48 | +8 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 90 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Brain-Absorber-Xombie.md` · `13th-age/srd/Bestiary/Elemental/Nymph/Wild-Naiad.md` · `13th-age/srd/Bestiary/Humanoid/Derro/Derro-Maniac.md` · `13th-age/srd/Bestiary/Humanoid/Fauns/Faun-Keeper.md` · `13th-age/srd/Bestiary/Humanoid/Jorogumo/Swarm-Prince.md` · `13th-age/srd/Bestiary/Humanoid/Kobolds/Kobold-Shadow-Warrior.md` · `13th-age/srd/Bestiary/Humanoid/Ravenous-Cannibal.md` · `13th-age/srd/Bestiary/Humanoid/Sahuagins/Sahuagin-Glow-Priest.md` · `13th-age/srd/Bestiary/Undead/Fallen-Icon-Undead/Summoned-Ghoul.md` · `13th-age/srd/Bestiary/Undead/Ghosts/Major-Haunting.md` · `13th-age/srd/Bestiary/Undead/Ghouls/Ghoul-Licklash.md` · `13th-age/srd/Bestiary/Undead/Reavers/Death-Marker.md`

## Floor 6 · level 6 · champion tier (same level = monster level 7)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 601 | 1 × Sahuagin Mutant | 6 | wrecker · large | 22/20/15 | 200 | +12 | 1.50 | Hard | a flooded bathroom (ankle-deep water; a prone creature is half under) | 95 |
| 602 | 3 × Star-Mask Floating Brain | 10 | mook · mook | 25/20/24 | 50 (mob 150) | +14 | 1.80 | Hard | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 65 |
| 603 | 1 × Big Fire Elemental | 7 | wrecker · normal | 23/22/19 | 92 | +13 | 1.00 | Normal | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 110 |
| 604 | 1 × Specter | 6 | wrecker · large | 19/15/19 | 160 | +9 | 1.50 | Hard | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 70 |
| 605 | 3 × Star-Mask Floating Brain | 10 | mook · mook | 25/20/24 | 50 (mob 150) | +14 | 1.80 | Hard | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 100 |
| 606 | 5 × Summoned Ghoul | 7 | mook · mook | 24/20/16 | 25 (mob 125) | +14 (or immediately after summoner if summoned during a battle) | 1.00 | Normal | a balcony over the street, three floors up or more | 45 |
| 607 | 1 × Ebon Gauntlet Adjudicator | 5 | wrecker · large | 21/18/18 | 130 | +8 | 1.00 | Normal | overturned furniture (moving through the room's middle is a dicey move) | 50 |
| 608 | 1 × Shadow Mongoose Subverter of Fate | 6 | spoiler · normal | 19/16/20 | 116 | +13 | 0.70 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 95 |
| 609 | 7 × Frogspawn Thug | 6 | mook · mook | 21/19/16 | 50 (mob 350) | +9 | 1.05 | Normal | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 110 |
| 610 | 1 × Shadow Mongoose Thief of Fate | 8 | spoiler · normal | 21/18/22 | 188 | +15 | 1.50 | Hard | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 65 |
| 611 | 2 × Faun Keeper | 5 | blocker · normal | 22/15 or 18/18 or 15 | 70 | +6 | 1.00 | Normal | a bare, empty room | 100 |
| 612 | 1 × Star-Mask Brainbuster | 7 | spoiler · normal | 17/21/24 | 100 | +12 | 1.00 | Normal | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 50 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Star-Mask-Brainbuster.md` · `13th-age/srd/Bestiary/Aberration/Star-Masks/Star-Mask-Floating-Brain.md` · `13th-age/srd/Bestiary/Elemental/Big-Fire-Elemental.md` · `13th-age/srd/Bestiary/Humanoid/Fauns/Faun-Keeper.md` · `13th-age/srd/Bestiary/Humanoid/Frogfolk/Frogspawn-Thug.md` · `13th-age/srd/Bestiary/Humanoid/Sahuagins/Sahuagin-Mutant.md` · `13th-age/srd/Bestiary/Humanoid/The-Ebon-Gauntlet/Ebon-Gauntlet-Adjudicator.md` · `13th-age/srd/Bestiary/Spirit/Shadow-Mongoose/Shadow-Mongoose-Subverter-of-Fate.md` · `13th-age/srd/Bestiary/Spirit/Shadow-Mongoose/Shadow-Mongoose-Thief-of-Fate.md` · `13th-age/srd/Bestiary/Undead/Fallen-Icon-Undead/Summoned-Ghoul.md` · `13th-age/srd/Bestiary/Undead/Specters/Specter.md`

## Floor 7 · level 7 · champion tier (same level = monster level 8)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 701 | 7 × Lokkris | 6 | mook · mook | 22/21/14 | 23 (mob 161) | +16 | 0.70 | Easy | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 130 |
| 702 | 3 × Beast Gauntlet's Mascot | 6 | blocker · normal | 24/18/22 | 70 | +9 | 1.50 | Hard | wardrobes (something can hide behind one; reaching it from the door is a move) | 105 |
| 703 | 1 × Koruku Symbiont | 7 | spoiler · normal | 23/19/21 | 94 | +10 | 0.70 | Easy | a flooded bathroom (ankle-deep water; a prone creature is half under) | 65 |
| 704 | 1 × Frogspawn Old-One | 7 | leader · elite | 23/21/24 | 160 | +10 | 1.05 | Normal | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 150 |
| 705 | 1 × Shadow Mongoose Thief of Fate | 8 | spoiler · normal | 21/18/22 | 188 | +15 | 1.00 | Normal | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 80 |
| 706 | 2 × Cackling Demon | 6 | leader · normal | 22/16/20 | 90 | +10 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 145 |
| 707 | 8 × Jotun Auroch | 6 | mook · mook | 20/18/13 | 70 (mob 560) | +7 | 0.80 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 110 |
| 708 | 3 × Koruku Servitor | 8 | mook · mook | 24/19/23 | 40 (mob 120) | +16 | 0.60 | Easy | a fireplace, lit (fire to grab, push into, or put out) | 105 |
| 709 | 2 × Star-Mask Cult Puppet | 6 | troop · normal | 21/16/21 | 80 | +10 | 1.00 | Normal | a balcony over the street, three floors up or more | 65 |
| 710 | 1 × Tempter | 7 | blocker · large | 23/21/21 | 204 | +14 | 1.50 | Hard | the lights out (darkness: bring a light, or fight blind) | 95 |
| 711 | 1 × Redscale Fiery Vanquisher | 7 | wrecker · normal | 23/21/15 | 110 | +9 | 0.70 | Easy | wardrobes (something can hide behind one; reaching it from the door is a move) | 85 |
| 712 | 2 × Koruku Symbiont | 7 | spoiler · normal | 23/19/21 | 94 | +10 | 1.40 | Hard | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 85 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Star-Mask-Cult-Puppet.md` · `13th-age/srd/Bestiary/Beast/Beast-Gauntlets-Mascot.md` · `13th-age/srd/Bestiary/Beast/Drow/Lokkris.md` · `13th-age/srd/Bestiary/Demon/Laughing-Demons/Cackling-Demon.md` · `13th-age/srd/Bestiary/Giant/Jotun-Auroch.md` · `13th-age/srd/Bestiary/Humanoid/Frogfolk/Frogspawn-Old-One.md` · `13th-age/srd/Bestiary/Humanoid/Koruku-Symbiont.md` · `13th-age/srd/Bestiary/Humanoid/Kroma-Dragonic/Redscale-Fiery-Vanquisher.md` · `13th-age/srd/Bestiary/Spirit/Koruku-Servitor.md` · `13th-age/srd/Bestiary/Spirit/Shadow-Mongoose/Shadow-Mongoose-Thief-of-Fate.md` · `13th-age/srd/Bestiary/Undead/Undead-Icon-Cult/Tempter.md`

## Floor 8 · level 8 · epic tier (same level = monster level 10)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 801 | 5 × Epic Haunting | 9 | mook · mook | 24/22/19 | 36 (mob 180) | +12 | 0.75 | Easy | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 125 |
| 802 | 2 × Whitescale Blighter | 8 | leader · normal | 24/22/19 | 140 | +13 | 1.00 | Normal | a bare, empty room | 145 |
| 803 | 5 × Greater Summoned Ghoul | 10 | mook · mook | 27/23/19 | 50 (mob 250) | +18 (or immediately after summoner if summoned during a battle) | 1.00 | Normal | a fireplace, lit (fire to grab, push into, or put out) | 80 |
| 804 | 3 × Great Fang Cadre | 10 | mook · mook | 27/25/21 | 50 (mob 150) | +13 | 0.60 | Easy | wardrobes (something can hide behind one; reaching it from the door is a move) | 75 |
| 805 | 1 × Great Xorn | 8 | troop · elite | 23/21/22 | 200 | +14 | 0.75 | Easy | overturned furniture (moving through the room's middle is a dicey move) | 180 |
| 806 | 1 × Fire Giant Priest-General | 8 | leader · large | 24/21/22 | 360 | +14 | 1.00 | Normal | a hole in the floor into the room below (a dicey move next to it can drop someone) | 155 |
| 807 | 1 × Giant Vrock (Vulture Demon) | 9 | spoiler · large | 24/21/21 | 333 | +12 | 1.50 | Hard | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 100 |
| 808 | 1 × Koruku Landkiller | 8 | leader · huge | 24/22/19 | 432 | +17 | 1.50 | Hard | overturned furniture (moving through the room's middle is a dicey move) | 70 |
| 809 | 5 × Star-Mask Floating Brain | 10 | mook · mook | 25/20/24 | 50 (mob 250) | +14 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 145 |
| 810 | 1 × Vampire | 10 | spoiler · normal | 26/20/26 | 220 | +15 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 175 |
| 811 | 1 × Fire Giant Warlord | 9 | leader · large | 26/22/18 | 355 | +14 | 1.50 | Hard | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 80 |
| 812 | 7 × Great Fang Cadre | 10 | mook · mook | 27/25/21 | 50 (mob 350) | +13 | 1.40 | Hard | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 135 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Star-Mask-Floating-Brain.md` · `13th-age/srd/Bestiary/Beast/Koruku-Beast/Koruku-Landkiller.md` · `13th-age/srd/Bestiary/Demon/Giant-Vrock.md` · `13th-age/srd/Bestiary/Elemental/Xorn/Great-Xorn.md` · `13th-age/srd/Bestiary/Giant/Fire-Giant-Warlord.md` · `13th-age/srd/Bestiary/Giant/Fire-Giants/Fire-Giant-Priest-General.md` · `13th-age/srd/Bestiary/Humanoid/Kroma-Dragonic/Whitescale-Blighter.md` · `13th-age/srd/Bestiary/Humanoid/Orcs/Great-Fang-Cadre.md` · `13th-age/srd/Bestiary/Undead/Fallen-Icon-Undead/Greater-Summoned-Ghoul.md` · `13th-age/srd/Bestiary/Undead/Ghosts/Epic-Haunting.md` · `13th-age/srd/Bestiary/Undead/Vampires/Vampire.md`

## Floor 9 · level 9 · epic tier (same level = monster level 11)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 901 | 2 × Epic Air Elemental | 9 | wrecker · normal | 24/23/19 | 140 | +16 | 1.00 | Normal | a flooded bathroom (ankle-deep water; a prone creature is half under) | 100 |
| 902 | 1 × Elder Manafang Naga | 10 | leader · normal | 26/20/24 | 210 | +18 | 0.70 | Easy | the lights out (darkness: bring a light, or fight blind) | 175 |
| 903 | 1 × Plant Briar Elf Sorcerer | 10 | caster · normal | 26/24/22 | 220 | +18 | 0.70 | Easy | a hole in the floor into the room below (a dicey move next to it can drop someone) | 200 |
| 904 | 7 × Great Fang Cadre | 10 | mook · mook | 27/25/21 | 50 (mob 350) | +13 | 1.05 | Normal | a bare, empty room | 235 |
| 905 | 1 × Empyrean Dragon (Black) | 9 | spoiler · huge | 25/23/21 | 510 | +17 | 1.50 | Hard | a bare, empty room | 175 |
| 906 | 3 × Epic Water Elemental | 9 | blocker · normal | 24/22/18 | 170 | +14 | 1.50 | Hard | a narrow hallway inside the door (only one creature can be engaged in it at a time) | 125 |
| 907 | 2 × Blackscale Light-Killer | 10 | archer · normal | 25/25/19 | 206 | +15 | 1.40 | Hard | a bare, empty room | 135 |
| 908 | 5 × Star-Mask Floating Brain | 10 | mook · mook | 25/20/24 | 50 (mob 250) | +14 | 0.75 | Easy | a fireplace, lit (fire to grab, push into, or put out) | 130 |
| 909 | 8 × Giant Zombie | 9 | mook · mook | 23/21/17 | 100 (mob 800) | +8 | 0.80 | Normal | a bare, empty room | 210 |
| 910 | 1 × Djinn | 9 | spoiler · large | 25/22/21 | 350 | +15 | 1.00 | Normal | wardrobes (something can hide behind one; reaching it from the door is a move) | 150 |
| 911 | 2 × Elder Sparkscale Naga | 9 | leader · normal | 24/23/19 | 190 | +15 | 1.00 | Normal | overturned furniture (moving through the room's middle is a dicey move) | 220 |
| 912 | 5 × Loyal Gatherer | 10 | mook · mook | 25/24/21 | 45 (mob 225) | +15 | 0.75 | Easy | a flooded bathroom (ankle-deep water; a prone creature is half under) | 190 |

Files: `13th-age/srd/Bestiary/Aberration/Star-Masks/Star-Mask-Floating-Brain.md` · `13th-age/srd/Bestiary/Beast/Nagas/Elder-Manafang-Naga.md` · `13th-age/srd/Bestiary/Beast/Nagas/Elder-Sparkscale-Naga.md` · `13th-age/srd/Bestiary/Dragon/Chromatic-Dragon/Black-Dragons/Empyrean-Dragon.md` · `13th-age/srd/Bestiary/Elemental/Epic-Air-Elemental.md` · `13th-age/srd/Bestiary/Elemental/Epic-Water-Elemental.md` · `13th-age/srd/Bestiary/Giant/Genie/Djinn.md` · `13th-age/srd/Bestiary/Humanoid/Kroma-Dragonic/Blackscale-Light-Killer.md` · `13th-age/srd/Bestiary/Humanoid/Orcs/Great-Fang-Cadre.md` · `13th-age/srd/Bestiary/Plant/Briar-Elves/Plant-Briar-Elf-Sorcerer.md` · `13th-age/srd/Bestiary/Undead/Fallen-Icon-of-Underground/Loyal-Gatherer.md` · `13th-age/srd/Bestiary/Undead/Zombies/Giant-Zombie.md`

## Floor 10 · level 10 · epic tier (same level = monster level 12)

| Room | Guests | Lvl | Role · size | AC/PD/MD | HP each | Init | Worth | Fight | Furniture | GP |
|---|---|---|---|---|---|---|---|---|---|---|
| 1001 | 1 × Hellwarped Brute | 10 | wrecker · huge | 25/24/19 | 650 | +10 + 1d4 | 1.50 | Hard | a mezzanine bed up a ladder (far away from the door; up the ladder is a move) | 110 |
| 1002 | 1 × Jackal High Priest | 10 | leader · large | 26/22/24 | 332 | +17 | 1.00 | Normal | wardrobes (something can hide behind one; reaching it from the door is a move) | 240 |
| 1003 | 8 × Star-Mask Floating Brain | 10 | mook · mook | 25/20/24 | 50 (mob 400) | +14 | 0.80 | Normal | overturned furniture (moving through the room's middle is a dicey move) | 190 |
| 1004 | 2 × Barbed Devil (Hamatula) | 10 | caster · normal | 24/24/24 | 175 | +16 | 1.00 | Normal | the lights out (darkness: bring a light, or fight blind) | 150 |
| 1005 | 3 × Elder Manafang Naga | 10 | leader · normal | 26/20/24 | 210 | +18 | 1.50 | Hard | overturned furniture (moving through the room's middle is a dicey move) | 265 |
| 1006 | 1 × Massive Mutant Chuul | 10 | wrecker · huge | 27/25/22 | 450 | +15 | 1.50 | Hard | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 110 |
| 1007 | 7 × Fanatical Druid Circle | 11 | mook · mook | 26/20/24 | 70 (mob 490) | +16 | 1.05 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 130 |
| 1008 | 5 × Treant Avenger | 12 | mook · mook | 30/28/22 | 76 (mob 380) | +15 | 1.00 | Normal | the lights out (darkness: bring a light, or fight blind) | 185 |
| 1009 | 1 × Massive Mutant Chuul | 10 | wrecker · huge | 27/25/22 | 450 | +15 | 1.50 | Hard | the lights out (darkness: bring a light, or fight blind) | 295 |
| 1010 | 5 × Treant Avenger | 12 | mook · mook | 30/28/22 | 76 (mob 380) | +15 | 1.00 | Normal | a chandelier (a ranged attack on its chain drops it on whoever is under it) | 115 |
| 1011 | 1 × Storm Giant | 10 | archer · huge | 26/24/22 | 650 | +16 | 1.50 | Hard | steam from a bath (nobody can see far away; everyone is nearby or engaged) | 300 |
| 1012 | 1 × Briar Elf Assassin | 11 | archer · normal | 27/24/23 | 280 | +16 | 0.70 | Easy | a bare, empty room | 315 |

Files: `13th-age/srd/Bestiary/Aberration/Chuuls/Massive-Mutant-Chuul.md` · `13th-age/srd/Bestiary/Aberration/Hellwarped-Beast/Hellwarped-Brute.md` · `13th-age/srd/Bestiary/Aberration/Star-Masks/Star-Mask-Floating-Brain.md` · `13th-age/srd/Bestiary/Beast/Nagas/Elder-Manafang-Naga.md` · `13th-age/srd/Bestiary/Devil/Barbed-Devil.md` · `13th-age/srd/Bestiary/Giant/Storm-Giant.md` · `13th-age/srd/Bestiary/Humanoid/Briar-Elves/Briar-Elf-Assassin.md` · `13th-age/srd/Bestiary/Humanoid/Fallen-Icon-of-Nature/Fanatical-Druid-Circle.md` · `13th-age/srd/Bestiary/Humanoid/Fallen-Icon-of-Undead/Jackal-High-Priest.md` · `13th-age/srd/Bestiary/Plant/Treant-Avenger.md`

