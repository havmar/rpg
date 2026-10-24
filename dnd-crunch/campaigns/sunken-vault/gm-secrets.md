# GM secrets: The Sunken Vault

GM only. Budget for one level 3 character: Low 150 · Moderate 225 · High 400 XP.
All rooms are dark unless noted. Squares are 1.5 m. On the maps, `#` wall, `.` floor,
`+` door, `~` difficult terrain, `=` stair, `o` pillar (blocks, gives cover).
Map rows run north (top) to south (bottom); columns are numbered from the west.

## Premise (one line, reveal only if asked)

Ister Vael, a dead evoker, sealed his workroom under his tower. His apprentice's ghost
(the Specter) still guards it. Kobolds and vermin moved into the upper rooms.

## Layout

```
                 [R8 Vault]
                     | bronze door (arcane-locked; bronze key in R7)
  [R7 Crypt] ---- [R6 Hall of Arms]
                     | stair down 6 m
  [R5 Kobold Den]--[R4 Grotto]
                     | R3 dart corridor (north–south)
  [R2 Library]-+--[R1 Gatehouse]
                     | stair up 9 m
                  Camp (surface)
```

## Camp: Stair-Head (surface, safe)

- Revival point. Long Rests here have no wandering checks.
- **Trader Hesk** sells anything in `reference/srd/Equipment/` at list price, Potions of
  Healing (50 GP, 3 in stock), incense for Find Familiar (10 GP). Buys gear at half price,
  gems and art at full value. Speaks Common only. Knows: "Kobolds below. Something cold at
  the bottom. Nobody's come back up with the old man's books."

## R1 Gatehouse — 6×4 sq interior (9×6 m)

```
   1 2 3 4 5 6 7 8
1  # # # . . # # #     N arch (cols 4–5) → R3
2  # . . . . . T #     T = overturned table: half cover (+2 AC) from the west
3  + . . . r . . #     W door (wood, unlocked, bar on the R2 side) → R2
4  # . . c r . . #     c = dead adventurer
5  # . . r . . . #
6  # # # = = # # #     S stair up → camp
```

- **3 Giant Rats** (75 XP, Low): AC 13, HP 7, speed 9 m + climb, bite +5 1d4+3, Pack
  Tactics, darkvision 18 m, passive 12. At (5,3), (5,4), (4,5), feeding on the corpse.
  They notice light coming down the stair (no surprise unless he comes down unlit and
  Stealth beats 12). They swarm the nearest target; flee at 1 rat left.
- Corpse: 6 GP, 2 torches, a shield (useless to him), a scrap note: "door in the dart
  hall... no, the PLATE. Step over the fifth flagstone."

## R2 Collapsed Library — 8×6 sq interior (12×9 m)

```
   1 2 3 4 5 6 7 8 9 10
1  # # # # # # # # # #
2  # S . . . . ~ ~ ~ #     S = skeleton
3  # . . . L . ~ ~ ~ #     L = lectern; ~ = rubble (difficult terrain, half cover)
4  # . . . . . ~ ~ ~ +     E door → R1
5  # S . . . . ~ ~ ~ #
6  # . . . . . . ~ ~ #
7  # # # # # # # # # #
```

- **2 Skeletons** (100 XP, Low): AC 14, HP 13, shortsword +5 1d6+3 / shortbow +5 1d6+3
  range 24/96 m, vulnerable bludgeoning, immune poison and Exhaustion (Sleep fails), passive
  9. Inert against the west wall until a creature comes within 3 squares of the lectern,
  then roll initiative. They shoot first, then close in.
- Lectern drawer: 24 GP and a **Spell Scroll of Ice Knife** (L1, conjuration; can be
  cast once from the scroll with no casting check, or copied: 2 h, 50 GP).
  Investigation DC 12 on the drawer finds a false bottom: **garnet** (gem, 50 GP).
- Best rest spot in the dungeon: bar the E door from inside. Short Rest still makes its
  wandering check.

## R3 Dart Corridor — 2 sq wide × 10 sq long (3×15 m), runs north from R1 to R4

- **Poisoned Darts** (SRD Traps.md): the pressure plate is the full-width 5th row of
  flagstones from the south (1 square deep). Trigger: entering it. DEX save DC 13 or
  1d3 darts × 1d6 poison. Resets each turn, up to 3 activations.
- Detect: Search action, Perception DC 15 (plate or holes). Investigation DC 15 also
  finds the plate (he has Expertise: +7). The R1 corpse's note gives it away.
- Bypass: step over (a 1.5 m long jump is fine for STR 8), wedge it (a dagger works and is
  stuck there), or plug the holes (1 exploration turn).

## R4 Glow-Moss Grotto — 8×8 sq natural cave (12×12 m), dim light (moss)

```
   1 2 3 4 5 6 7 8
1  # # # = = # # #     N stair down 6 m → R6
2  # . . . . . . #
3  . . . v . . . #     W tunnel (1 sq wide) → R5
4  . . . . . v . #     v = violet fungus (looks like a big mushroom)
5  # . . . . . . #
6  # . ~ ~ . . . #     ~ = slick moss (difficult terrain)
7  # . ~ ~ . . . #
8  # # # . . # # #     S → R3
```

- **2 Violet Fungi** (100 XP, Low): AC 5, HP 18, speed 1.5 m, 2× rotting touch +2, reach
  3 m, 1d8 necrotic, blindsight 9 m. Look like large mushrooms; Nature DC 12 or passive
  Perception 14+ spots them. They attack anything within 3 m.
- The glow-moss is the material component for *Light* (he can harvest it).
- The kobolds won't pass this room while the fungi live.

## R5 Kobold Den — 7×7 sq (10.5×10.5 m), dim light (firepit)

```
   1 2 3 4 5 6 7
1  # # # # # # #
2  # k . . . k #     k = kobold
3  # . . F . . #     F = firepit (entering or ending a turn in it: 1d4 fire)
4  # . . . . . X     X = east entrance from R4, junk barricade at col 6 (half cover)
5  # k . . . k #
6  # . . . . . #     chest under furs at (2,6)
7  # # # # # # #
```

- **4 Kobold Warriors** (100 XP, Low): AC 14, HP 7, dagger +4 1d4+2 (melee or 6/18 m),
  Pack Tactics, darkvision 18 m, passive 8. Leader is Snik (same stats, 10 HP).
- **Talkable.** They speak Draconic and Common; Morten speaks Draconic. Snik opens
  hostile but bargains. Wants: the fungi in R4 dead (their way out), or food (2 rations).
  Gives in exchange: "the bronze key is round the neck of the hungry one in the wet
  tomb" (R7), and that "the metal man won't leave its hall" (R6). If befriended they're
  neutral and the kobold patrol on the wandering table becomes friendly.
- Morale: flee or surrender when Snik dies or 2 are down (WIS save DC 10 for the group).
- Chest (unlocked): 31 GP, 40 SP, 1 Potion of Healing.

## R6 Hall of Arms — 6×12 sq (9×18 m)

```
   1 2 3 4 5 6
1  # # B B # #     B = bronze door → R8 (arcane-locked)
2  # . . A . #     A = Animated Armor at its post
3  # o . . o #
4  . . . . . .     W door → R7 (col 1), E: blank wall (col 6 is a niche, armour stand)
5  # . . . . #
6  # o . . o #     o = pillars (full cover behind)
7  # s . . s #     s = empty armour stands
8  # . . . . #
9  # o . . o #
10 # . . . . #
11 # . . . . #
12 # # = = # #     S stair up 6 m → R4
```

- **Animated Armor** (200 XP, Moderate): AC 18, HP 33, speed 7.5 m, 2× slam +4 1d6+2,
  blindsight 18 m, immune poison, psychic, Charmed, Paralyzed, Exhaustion (Sleep fails).
  Shatter: it has Disadvantage on the save. It activates when a creature comes within 4
  squares of the bronze door or touches it. **It never leaves R6**, and returns to its
  post if no target is in the hall for a round.
- Niche armour stand at (6,4): helm holds a rolled **map of R7 and R8** (shows the
  crypt's dais and "the guardian of the work"), Investigation DC 14.
- **Bronze door:** opens with the bronze key (R7). Otherwise STR DC 25 (crowbar gives
  Advantage). Detect Magic shows abjuration.

## R7 Flooded Crypt — 8×10 sq (12×15 m)

```
   1 2 3 4 5 6 7 8
1  # # # # # # # #
2  # ~ ~ ~ ~ D D #     ~ = knee-deep water (difficult terrain)
3  # ~ z ~ ~ D G #     D = raised dais (dry); G = ghoul by the sarcophagus
4  # ~ ~ ~ ~ D S #     S = sarcophagus
5  # ~ ~ ~ ~ D D #     z = zombie, submerged
6  # ~ ~ ~ z ~ ~ #
7  # ~ ~ ~ ~ ~ ~ #
8  # ~ ~ ~ ~ ~ ~ #
9  # ~ ~ ~ ~ ~ ~ #
10 # # # # # # # +     E door (col 8) → R6 west door via a 6 m passage
```

- **Ghoul** (200 XP) + **2 Zombies** (100 XP) = 300, Moderate-to-High.
  - Ghoul: AC 12, HP 22, 2× bite +4 1d6+2 piercing + 1d6 necrotic, or claw +4 1d4+2 and
    CON save DC 10 or Paralyzed until end of its next turn (paralyzed: melee hits within
    1.5 m are critical). Immune Charmed, Exhaustion. It uses claw first, then bites.
  - Zombies: AC 8, HP 15, speed 6 m, slam +3 1d8+1, Undead Fortitude (CON DC 5 + damage
    to drop to 1 HP instead, not vs radiant or crits). Submerged: Stealth d20−2 vs his
    passive Perception 13; they rise when he's 3 squares in.
- The ghoul wears the **bronze key** on a chain.
- Sarcophagus: STR DC 12 to slide the lid (crowbar Advantage). Inside: 60 GP and a
  **moonstone** (gem, 50 GP).

## R8 Vault of Ister Vael — 8×8 sq (12×12 m), dim cold blue light

```
   1 2 3 4 5 6 7 8
1  # # # # # # # #
2  # B . . . . T #     B = bookstand (spellbook), T = treasure chest
3  # . . . . . . #
4  # . . P . . . #     P = Specter's start (in the floor, rises)
5  # . f . . f . #     f = flying swords, on wall hooks until activated
6  # . . . . . . #
7  # . . . . . . #
8  # # # B B # # #     S bronze door → R6
```

- **Specter** (200 XP) + **2 Animated Flying Swords** (100 XP) = 300, Moderate-to-High.
  - Specter: AC 12, HP 22, fly 15 m (hover), life drain +4 2d6 necrotic and HP max
    reduced by that much (until Long Rest; at revival it's restored). Resists acid,
    bludgeoning, cold, fire, lightning, piercing, slashing, thunder. Immune necrotic,
    poison, most conditions incl. Unconscious. Incorporeal Movement. **Force (Magic
    Missile) is not resisted.**
  - Swords: AC 17, HP 14, fly 15 m, slash +4 1d8+2, blindsight 18 m, immune Exhaustion.
  All three activate when the bronze door opens. The specter targets him directly; the
  swords flank him.
- Bookstand: **Ister's spellbook**: Chromatic Orb (1), Fog Cloud (1), Ice Knife (1),
  Mirror Image (2), Invisibility (2), Knock (2), Fireball (3), Counterspell (3). Copy any of
  level ≤ 2 now (50 GP and 2 h per level); level 3 once he reaches Wizard 5.
- Chest (locked, Investigation DC 15 to find the catch, or STR DC 15): 220 GP,
  3 bloodstones (gems, 50 GP each), **Pearl of Power** (uncommon, attunement by a
  spellcaster; house rule: as a Magic action, regain one lost spell of level ≤ 3, once per
  dawn).

## Wandering monsters

Roll `1d6` every 3 exploration turns and once per Short Rest in the dungeon; 1 = encounter.
Then `1d4`:

| d4 | Encounter | XP |
|---|---|---|
| 1 | 2 Giant Rats | 50 |
| 2 | Swarm of Rats | 50 |
| 3 | 3 Stirges | 75 |
| 4 | Kobold patrol: 2 Kobold Warriors (friendly if R5 was befriended) | 50 |

## Dungeon status

Update as rooms are entered, cleared or reset. After a death, note what moved.

| Room | Status |
|---|---|
| R1 | Day 1: 2 rats killed; rat 3 (7/7) fled to R4. Corpse looted (6 GP, torches, note taken; shield left). 12:01: 3 stirges (wandering) killed Morten here; 1 stirge dead. The 2 survivors (3/5 and 5/5 HP), sated, roost in the R3 corridor ceiling until they're hungry again: back on the wandering table from Day 2 06:00. W door still closed. |
| R2 | Day 1 21:42–21:52: lectern looted by Mage Hand (24 GP, Ice Knife scroll, garnet). Both skeletons destroyed. Cleared. E door open. |
| R3 | unexplored |
| R4 | unexplored |
| R5 | unexplored |
| R6 | unexplored |
| R7 | unexplored |
| R8 | unexplored |
