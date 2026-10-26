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
