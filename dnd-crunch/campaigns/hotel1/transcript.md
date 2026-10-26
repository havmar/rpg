# Hotel 1 · transcript

## Human

> dnd crunch, please start a new game - hotel - search 10 rooms, Claude the dm controlling Morten.

## GM

**Day 1 · 10:30 · Room 103 (floor 1) · Bricks 1 · Staff 0 · Residents 0 · Ark 0**

**Stopped at half HP.** Morten is at 4/20 HP in a fight with a Dretch, so the sweep stops here, as the house rule says. Two of the ten rooms are searched and the third is in progress.

The premise: Morten is a registered guest with a key, a room (101) and a bill at zero. The Hotel's Cornerstone was broken into bricks and mortared into the walls, so he searches room by room. Every guest is an SRD monster in pyjamas, and nobody thinks it's odd.

### Room 101 · his own room · searched, no brick
- The three Guards in the generator's row for 101 had checked out before he came down. No guests, no XP.
- Search 08:00–09:00: noise 6 (nothing), brick 6 (none).
- At 09:00 a Mastiff from 102 walked past his open door on its way to the bathroom (CR 1/8, AC 12, HP 5, speed 8 sq (12 m), bite 1d6+1). Reaction 6, wary. Morten let it go.

### Room 102 · 2 Mastiffs (CR 1/8 each) · searched, brick · 50 XP
- Knock: reaction 11. They ignore him, so he searched around the one still inside.
- Search 09:10–10:10: noise 1, brick 1. **A brick came out. Bricks 1.**
- Noise 1: a Blood Hawk from 104 came to look (CR 1/8, AC 12, HP 7, fly 12 sq (18 m), beak +4 for 1d4+2 piercing). Reaction 4: it held the corridor and didn't attack.
- Morten (GM): stayed in the doorway and Fire Bolted it rather than walk up to a hawk that attacks when approached. Cast 21 vs DC 10, hit vs AC 12, 7 fire dmg. **Dead.** 25 XP.
- He dragged the body into 102; the Staff fine a body left in a corridor.
- The Mastiffs' suitcases (5 GP, two knick-knacks) stayed where they are. Taking them while the guests live is robbery.
- The room's 50 XP came with the search.

### Room 103 · 1 Dretch (CR 1/4, Moderate, 50 XP) · in progress
- Dretch: CR 1/4, AC 11, HP 18, speed 4 sq (6 m), Rend +3 for 1d6+1 slashing, Fetid Cloud (1/day, CON DC 11, Poisoned). Speaks Abyssal.
- Knock: reaction 4 (after −2 for word travels). It slams the door. A forced entry is a fight.
- **Round 1:** Morten opened the door and cast Sleep: cast 11 vs DC 11. The Dretch's WIS save was a natural 1 (0 vs DC 13), so it's Incapacitated.
- **Round 2:** At the end of its turn it repeats the save: 11 vs DC 13, fail, so it's Unconscious. Morten closed in and daggered it with Advantage: natural 20, crit, 4 dmg → 14/18 HP. The damage woke it, because Sleep ends when the target takes damage.
- **CORRECTION:** My off-hand dagger swing was rolled as if the Dretch were still unconscious. Re-rolled as an ordinary attack: 6 vs AC 11, miss.
- **Round 3:** Fetid Cloud. Morten's CON save 8 vs DC 11, fail: Poisoned until the end of his turn, which gives Disadvantage on his casting check. He used Disengage and backed out into the corridor, so the Dretch could only reach the doorway.
- **Round 4** (no longer poisoned): Magic Missile, cast 13 vs DC 11, darts 2 + 2 + 4 = 8 → Dretch 6/18 HP.
- **Round 5:** the Dretch moved in and Rend hit 16 vs AC 12, 4 dmg → Morten 16/20. Then Morten's Magic Missile: natural 1, fizzle. **Mishap** (1d12 = 2, Wild target): the spell goes at a random creature in range, and the roll (1d4 = 2) picked Morten. Darts 4 + 5 + 3 = 12 → **Morten 4/20 HP.** Magic Missile is lost until Long Rest.
- **Morten (GM):** Magic Missile without Disadvantage was the sure kill: any cast that lands does 6+ against the Dretch's 6 HP. Then the wild target went to Morten.

**Where it stands**
- Morten: **4/20 HP** (half, the stop), AC 12, speed 6 sq (9 m). Action spent this turn; bonus action and movement unused. Potion of Healing in his pack (bonus action, 2d4+2). Lost: Magic Missile.
- Dretch: **6/18 HP** (Bloodied), AC 11, Fetid Cloud spent. Adjacent to Morten.
- Positions: the door of 103 is at C1. Morten C-2 (corridor, 3 sq north of the door). Dretch C-1, next to him.

**Stakes and open choices**
- He carries 47 GP 7 SP 5 CP and would lose it on death. The brick is safe.
- The open choices are his: the Potion (bonus action), a move (6 sq), a Fire Bolt or dagger on the Dretch (action), or one of the other spells.

**Tally**
- XP 975 (900 + 25 hawk + 50 room 102). Level 4 needs 2,700, so 1,725 to go.
- Rooms searched: 101, 102 (2 of 10). Word travels: −2 on floor 1.
- Rations 4, torches 7, oil 10 (lamp unlit). Day 1; no Long Rest yet.

Say what Morten does and I'll resume.

## Roll log (roll.py, in order)

- Seed: 1d100 = 10.
- Residents' floors (1d4 × 5, one per band): 3, 1, 3, 4, 1 → floors 3, 5, 11, 16, 17. Ark floor (1d20): 2.
- Rooms within floors: 1d5 = 2 (Ark suite 202); 1d8 = 4 (304); 1d14 = 4 (504); 1d8 = 4 (1104); 1d8 = 4 (1604); 1d7 = 3 (1703).
- 101 search: noise 1d6 = 6; brick 1d6 = 6 (none); wandering 1d6 = 3, then 1 (encounter).
- Wanderer: 1d4 = 1 (room 102); reaction 2d6 = 6 + 1 = 7, −1 = 6 (wary).
- 102 door: reaction 2d6 = 6 + 6 = 12, −1 = 11 (ignores).
- 102 search: noise 1d6 = 1; brick 1d6 = 1 (brick); wandering 1d6 = 2, 5.
- Noise guest: 1d4 = 3 (room 104); reaction 2d6 = 3 + 5 = 8, −4 = 4 (holds ground).
- Fire Bolt: cast 1d20+5 = 16 + 5 = 21 (DC 10, hit AC 12); damage 1d10 = 7 (hawk dead).
- 103 door: reaction 2d6 = 3 + 3 = 6, −2 = 4 (slams the door).
- Initiative: Morten 1d20+4 = 8 + 4 = 12; Dretch 1d20+0 = 14.
- Sleep: cast 1d20+5 = 6 + 5 = 11 (DC 11, success). A 5d8 = 31 HP pool was rolled in error: the 2024 Sleep (SRD 5.2.1) has no HP pool, so it's void.
- Dretch WIS save 1d20−1 = 1 − 1 = 0 (natural 1, fail): Incapacitated.
- Dretch second save at the end of its turn: 1d20−1 = 12 − 1 = 11 (fail): Unconscious.
- Dagger (Advantage) 1d20+4 = [20, 4] keep 20 + 4 = 24 (natural 20, crit); damage 2d4+2 = 1 + 1 + 2 = 4 → Dretch 14/18.
- Off-hand dagger, first roll (void: the Dretch had woken): 1d20+4 with Advantage = [8, 15] keep 15 + 4 = 19; 2d4 = 4 + 3 = 7 (crit dice, not valid). Then 1d4 = 3 for damage, also void.
- CORRECTION, off-hand dagger as an ordinary attack: 1d20+4 = 2 + 4 = 6 (miss).
- Fetid Cloud, Morten's CON save 1d20+2 = 6 + 2 = 8 (vs DC 11, fail): Poisoned until the end of his turn.
- Magic Missile (round 4): cast 1d20+5 = 8 + 5 = 13 (DC 11, success); darts 1d4+1 = 2, 1d4+1 = 2, 1d4+1 = 4 → 8 → Dretch 6/18.
- Dretch Rend vs AC 12: 1d20+3 = 13 + 3 = 16 (hit); damage 1d6+1 = 3 + 1 = 4 → Morten 16/20.
- Magic Missile (round 5): cast 1d20+5 = 1 + 5 = 6 (natural 1, fizzle). Mishap 1d12 = 2 (Wild target). Target 1d4 = 2 (Morten). Darts 1d4+1 = 4, 1d4+1 = 5, 1d4+1 = 3 → 12 → Morten 4/20.
- Wandering check at the 103 door: 1d6 = 2 (no encounter).

## Human

> let's continue the game. is there a rule to stop at half hp ? should not be a rule. Claude plays on even at low hp. cheeses (as seen in old first commits of dnd crunch)

## GM

(The half-HP stop is gone from `dnd-crunch/CLAUDE.md`: low HP is never a stop, and with a goal set the GM plays on to the goal or a death.)

**Day 1 · 10:30 → Day 2 · 01:31 · Bricks 4 · Staff −1 · Residents 0 · Ark 0**

**Morten searched four more rooms (6 of 10), pulled two more bricks, and died in room 204 to a Dretch from the Ark.**

### Room 103 · Dretch (CR 1/4) · finished on 8/20 HP
- **Round 5 (cont.):** the potion rolled its minimum, 2d4+2 = 4 → Morten 8/20 HP. He stayed put rather than give the Dretch an opportunity attack. The Dretch's Rend missed (9 vs AC 12).
- **Round 6:** Morten (GM): fire, cold and lightning are halved on a Dretch and Thunderwave risks a spell, so it's daggers. Dagger 19 vs AC 11, hit, 1d4+2 = 6 dmg. **Dead.**
- He dragged the body into 103 (no body in the corridor). Short Rest 10:31–11:31: wandering 2; 2 Hit Dice 2d6+4 = 11 → **19/20 HP**; Arcane Recovery brought Magic Missile back. Free **Mage Armor** (AC 15 until 19:31).
- Search 11:31–12:31: noise 4, **brick 1: Bricks 2.** Luggage: 5 GP and a jar of pickled eyes with an Abyssal label (4 GP). XP 975 → 1,025.

### Room 104 · 2 Blood Hawks (CR 1/8 each) · 50 XP · cleared on 16/20 HP
- Knock: reaction 2d6 −3 = 2, attacks. Thick fog inside, so Morten opened the door and backed 4 sq (6 m) down the corridor. Initiative: Morten 7 › Hawks 5.
- **Round 1:** Morten Readied Sleep (cast 16 vs DC 11). Hawk A hit 23 (too high for Shield to matter) for 3 → 16/20 HP; concentration natural 20. Hawk B landed beside it and Sleep went off: WIS saves 3 and 12 vs DC 13, both Incapacitated before B could bite.
- **Round 2:** Dodge, no damage, so Sleep holds. Second saves 11 and 7: both **Unconscious**.
- **Rounds 3–4:** point-blank daggers with Advantage, both crits: 2d4+2 = 7 and 7 dmg. Both dead.
- Bodies dragged into 104. Search 12:33–13:33: noise 5, brick 4 (none). Wandering: a Mastiff from 102 passed, reaction 4 (holds its ground); Morten stayed in 104 and let it go.
- Luggage: 7 GP and a hawk-sized silk sleeping mask (5 GP). XP 1,025 → 1,075 (the room's 75 less the 25 for the hawk killed on Day 1).

### Room 105 · 2 Blink Dogs (CR 1/4 each) · High, 100 XP · talked in
- Knock: reaction 2d6 −3 = 3, slammed the door. Morten (GM): they understand Elvish. The silk mask as a gift moved them up a row to **6, Talks**; they asked 10 GP and he paid.
- Search 13:40–14:40: noise **2: housekeeping**; he paid the 10 GP damages on the spot (Staff stays 0). **Brick 1: Bricks 3.** XP 1,075 → 1,175.
- Lobby: sold the Sage book (12 GP 5 SP) and the jar (4 GP), bought a **Potion of Healing** (50 GP). Coins 6 GP 2 SP 5 CP.

### Floor 2 · listening at the doors, 15:00–15:50
- 201 legs skittering (Perception 13 vs Stealth 12) · 202 Abyssal voices, the Dretch reek · 203 voices in Common, armour · 204 one heavy animal stamping · 205 big birds clacking. Wandering 2, 5.

### Room 203 · 4 Guards (CR 1/8 each) · Low, 100 XP · Helpful
- Knock: reaction **12, Helpful.** They let him search and told him: "Don't knock at 202. That's the Ark, demons who keep a list. They pay a bounty for the first of each kind of guest killed, if you bring the key tag."
- Search 15:55–16:55, knee-deep water: **brick 1: Bricks 4.** Noise **1**: 204's Warhorse came to look, reaction 2d6 −2 = 1, **attacks**.

### Wanderer · Warhorse (CR 1/2) · 100 XP · killed on 1 HP
- Warhorse: AC 11, HP 19, speed 12 sq (18 m), Hooves +6 for 2d4+4, +2d4 and Prone after a 4 sq straight charge. Initiative: Morten 20 › Warhorse 2 (natural 1).
- **Round 1:** Sleep (cast 12): WIS save 12 vs DC 13, Incapacitated. Second save 14: it shook it off.
- **Round 2:** Scorching Ray, **natural 20**: ray 1 a crit, 4d6 = 12 fire → 7/19 HP. Rays 2 and 3 missed (10, natural 1). The Warhorse charged 5 sq through the water: 23 vs AC 15 (Shield wouldn't do), 2d4+4 = 7 plus 2d4 = 8: **15 dmg, Prone → Morten 1/20 HP.**
- **Round 3:** potion first (2d4+2 = 5 → 6/20 HP), then Magic Missile (cast 16): darts 3d4+3 = 7, exactly enough. **Dead.**
- XP 1,175 + 100 (horse) + 100 (room 203) = **1,375**. He took the horse's key tag.

### Room 204 · empty · Morten died
- 204's only guest was the horse, so he searched it at 17:05 on 6/20 HP (no Long Rest before 00:00). Noise **1**: a Dretch from 202, reaction 2d6 −3 = 2, **attacks.**
- Dretch: CR 1/4, AC 11, HP 18, Rend +3 for 1d6+1. Initiative: Morten 15 › Dretch 1.
- **Round 1:** Sleep (cast 21); the Dretch saved, 14 vs DC 13. It waded in: Rend 20 (meets AC 20 even with Shield), 1d6+1 = **7 dmg → 0 HP.**
- **Round 2:** death save 13 (success). The Dretch clawed again with Advantage, 22, a crit on an unconscious target: two failures. Death save 8: **third failure. Morten is dead** at 17:31.

### Respawn
- He wakes in room 101 at **Day 2 · 01:31**, full HP and spells, counted as a Long Rest. **Lost: 6 GP 2 SP 5 CP.** Kept: 4 bricks, gear, spellbook, XP 1,375, the Warhorse's key tag. Deaths: 1.
- The 204 search didn't finish: still unsearched, the brick roll void.
- Housekeeping: 103 (6) and 104 (5), no new guests. Event 1d6 = 6 → 1d12 = 9, **a complaint**: the Blink Dogs of 105 at the desk. **Staff −1.**

**Where it stands**
- Morten 20/20 HP, nothing lost, Arcane Recovery and free Mage Armor fresh, Heroic Inspiration 1, no potion, **0 coins**. He may re-prepare spells now.
- Rooms searched: 101–105, 203 (**6 of 10**). Left on floor 2: 204 (empty, 10 GP luggage), 201 (skittering), 205 (big birds), 202 (the Ark).
- The Ark would pay 12 GP 5 SP for the Warhorse's tag.

**Stakes and open choices:** nothing to lose but time; the next four rooms are 204, 201, 205 and the Ark's 202 (or a floor 3 room in its place).

## Roll log, Day 1 10:30 → Day 2 01:31 (roll.py, in order)

- Potion 2d4+2 = 1+1+2 = 4 (Morten 8/20). Dretch Rend 1d20+3 = 6+3 = 9 (miss).
- Dagger 1d20+4 = 15+4 = 19 (hit); 1d4+2 = 4+2 = 6 (Dretch dead).
- Short Rest wandering 1d6 = 2. Hit Dice 2d6+4 = 5+2+4 = 11 (19/20).
- 103 search: noise 1d6 = 4; brick 1d6 = 1 (brick); wandering 4, 4.
- Knick-knack 1d6 = 4 (jar). 104 reaction 2d6−3 = 3+2−3 = 2. Wandering 1d6 = 2.
- Initiative: Morten 1d20+4 = 3+4 = 7; Hawks 1d20+2 = 3+2 = 5.
- Sleep (readied) cast 1d20+5 = 11+5 = 16. Hawk A beak 1d20+4 = 19+4 = 23 (hit); 1d4+2 = 1+2 = 3 (16/20). Concentration 1d20+2 = 20+2 = 22 (natural 20).
- Hawk WIS saves 1d20+2: 1+2 = 3 (natural 1), 10+2 = 12: both fail. Second saves: 9+2 = 11, 5+2 = 7: both Unconscious.
- Dagger (adv) [17, 18] 18+4 = 22, crit 2d4+2 = 4+1+2 = 7 (Hawk A dead). Dagger (adv) [7, 16] 16+4 = 20, crit 2d4+2 = 4+1+2 = 7 (Hawk B dead).
- 104 search: noise 5; brick 4; wandering 2, 1 (encounter). Knick-knack 1d6 = 5 (mask). Wanderer 1d2 = 1 (102, Mastiff); reaction 2d6−3 = 3+4−3 = 4.
- 105 reaction 2d6−3 = 3+3−3 = 3; gift → 6.
- 105 search: noise 2 (housekeeping, paid 10 GP); brick 1 (brick); wandering 3, 4.
- Floor 2 listening: Perception 1d20+3 = 10+3 = 13 vs spiders' Stealth 1d20+7 = 5+7 = 12. Wandering 2, 5.
- 203 reaction 2d6 = 6+6 = 12.
- 203 search: noise 1; brick 1 (brick); wandering 6, 2. Noise guest 1d4 = 3 (204, Warhorse); reaction 2d6−2 = 1+2−2 = 1.
- Initiative: Morten 1d20+4 = 16+4 = 20; Warhorse 1d20+1 = 1+1 = 2.
- Sleep cast 1d20+5 = 7+5 = 12. Warhorse WIS 1d20+3 = 9+3 = 12 (fail); second save 11+3 = 14 (success).
- Scorching Ray cast 1d20+5 = 20+5 = 25 (natural 20, crit) 4d6 = 3+1+6+2 = 12. Rays 2, 3: 5+5 = 10 (miss), 1+5 = 6 (miss).
- Warhorse Hooves 1d20+6 = 17+6 = 23 (hit); 2d4+4 = 2+1+4 = 7; charge 2d4 = 4+4 = 8 (Morten 1/20, Prone).
- Potion 2d4+2 = 2+1+2 = 5 (6/20). Magic Missile cast 1d20+5 = 11+5 = 16; darts 3d4+3 = 1+1+2+3 = 7 (Warhorse dead).
- 204 search: noise 1; brick 3 (void, the search didn't finish); wandering 3, 6; knick-knack 1d6 = 1 (2 GP). Noise guest 1d4 = 2 (202, Dretch); reaction 2d6−3 = 3+2−3 = 2.
- Initiative: Morten 1d20+4 = 11+4 = 15; Dretch 1d20 = 1.
- Sleep cast 1d20+5 = 16+5 = 21. Dretch WIS 1d20−1 = 15−1 = 14 (save).
- Dretch Rend 1d20+3 = 17+3 = 20 (hit); 1d6+1 = 6+1 = 7 (Morten 0 HP).
- Death save 1d20 = 13 (success). Dretch Rend (adv) [18, 19] 19+3 = 22, crit (two failures). Death save 1d20 = 8 (third failure, dead).
- Housekeeping: 103 1d6 = 6, 104 1d6 = 5 (no restock). Event 1d6 = 6 → 1d12 = 9 (a complaint).
