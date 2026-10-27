# The Hotel

The Hotel rules for D&D Crunch: a megadungeon that is a hotel, searched room by room by one
character who is also a guest. These add to `dnd-crunch/CLAUDE.md` (the crunch, the house
rules, the report style, the GM) and win where they differ. Everything here is public:
Morten may know all of it. The design is this page; there is no engine, no page and no
map. The dice are `tools/roll.py`, the rooms come from `tools/gen_dungeon.py`, the magic
items from `tools/loot.py`.

Morten is **two party members in one body**: a class of his own and a wizard's spellbook
cast by the roll, levelling together (section 11). Guests' luggage holds **magic items**
(section 12). `hotel1` predates both: its `rules.md` says what it plays instead.

## 1. The premise

The Hotel was built from the ruins of a civilisation nobody remembers, and its
**Cornerstone** was broken into bricks and mortared into the rooms. Morten is the only
guest who can hear a brick in a wall, and the only one who can pull it out. He is here to
reassemble the Cornerstone, which means **searching every room in the Hotel**. What a
finished Cornerstone does is the GM's secret, written in `gm-secrets.md` before play.

The vibe is Troika: surreal and matter-of-fact. Every guest is an SRD monster, chosen at
random and never explained. A Camel with a suitcase and pyjamas has room 304 and sees
nothing odd about it. The Staff speak of the Hotel's rules as policy. Nobody is surprised
by anything except Morten turning their room over. The narration stays minimal as in the
crunch rules: one terse line per room, one line of speech when it carries information,
and every guest named with its CR.

Morten is a registered guest. He has a room on floor 1, a key, and a bill.

## 2. The building

- **Floors.** Floor N is built for a level N character, exactly as the demo dungeon:
  its rooms add up to at least the XP from level N to N+1, each room holds 1 to 4 guests
  of one random SRD kind, with a random size and one feature, all from
  `python3 dnd-crunch/tools/gen_dungeon.py --seed S`. Floor 20 is the top. Room 3.1 is
  **room 301**; the floor's rooms open off one corridor in number order, with a stair at
  each end going up and down. Nothing is locked but doors. Higher floors are deadlier,
  which is the only gate.
- **Features read as furniture.** Pillars are wardrobes, statues are mannequins, rubble is
  overturned furniture, knee-deep water is a flooded bathroom, the ledge is a mezzanine
  bed, the chasm is a hole into the room below, chains hang from the ceiling because they
  do. Sizes stay as generated; the Hotel is bigger inside.
- **The lobby** is the ground floor: the **desk** (the bill, the register, lost and
  found), the **gift shop** (anything in `reference/srd/Equipment/` at list price, Potions
  of Healing 50 GP, buys gear at half, gems at full, and a shelf and a window of magic
  items, section 12), the **bar** (a truce by policy: no
  violence; one true rumour per drink, 1 GP), and the **lift**, which stops at every floor
  Morten has already stood on. Nobody sleeps in the lobby.
- **Morten's room** is 101, a safe Long Rest while the Staff are not Hostile.
- **The Manager** has never been seen. The Staff speak of them in the present tense.

## 3. The search (the loop)

Every room is handled the same way, door to door.

1. **Listen** (1 turn, Perception, or just knock). Occupied rooms have guests in them
   unless an event or the register says otherwise.
2. **The door.** The guest answers. Roll the **reaction** (section 4). Morten says what he
   wants: to search the room. Most guests find that repugnant, so by the SRD's Influence
   rules they are *unwilling* until he offers something; then they are *hesitant* and he
   rolls the Influence check, DC 15 or the guest's Intelligence if higher
   (`Glossary/Influence.md`). Deception and Persuasion need a guest that understands him
   (a language on his sheet, or *Comprehend Languages*); Intimidation and Performance
   work on anyone with a language; Animal Handling coaxes a Beast or Monstrosity. A
   **gift** (coins or a knick-knack worth 5 GP × floor) moves the reaction one row up,
   once per door.
3. **Or not the door.** He can wait until the room is empty (the register, an event, a
   stakeout), sneak in, lure the guest out, or fight. A guest that is out, asleep, fled or
   dead doesn't object.
4. **The search** takes **1 hour** (6 turns) and is **loud**: furniture over, walls
   tapped, the brick's name shouted. It is heard across the floor. Once during the hour
   roll the **noise check**, 1d6:
   - **1:** a guest from a random occupied room on the floor comes to look. Reaction roll
     at −2.
   - **2:** housekeeping arrives. Staff standing −1, unless he pays the **damages**
     (10 GP × floor) on the spot.
   - **3 to 6:** nothing yet.
5. **The brick.** Roll 1d6: on a **1 or 2** a brick comes out of the wall. The **last
   unsearched room in the Hotel always holds the last brick**; the Hotel knows. Bricks go
   in his bag, count toward the Cornerstone, and are never lost on death.
6. **XP and luggage.** A room's XP is earned **once, when its search completes**, however
   he got in: talk, stealth or violence all pay the same. Wanderers and guests fought in
   corridors give their XP as normal. Every guest has luggage: the generator's coins (a
   tenth of the XP) in a suitcase, plus one **knick-knack** the GM names in a few words (a
   snow globe of the Hotel, a monogrammed toothbrush, a brass key to nothing) worth
   1d6 × floor GP at the gift shop or to a Friendly guest, and sometimes a **magic item**
   (section 12). Taking luggage while the guest lives is robbery: the reaction drops to 2.

**Word travels.** Reaction rolls on a floor take **−1 for every room Morten has searched
there**, to a maximum of −3. The talky rooms are easiest first; by the end of a floor the
Hotel is as antagonistic as he has made it. New guests who check in later don't know him
yet: no penalty for them.

**Corridors.** Walking a corridor is exploration: a wandering check every 3 turns as in
the crunch rules. A wanderer is a guest from a random occupied room on that floor, on
their way to the bar or the bathroom, with a reaction roll.

## 4. Reaction roll

On first contact with any guest, **2d6 + Morten's CHA mod** (+0), plus the standing of
the guest's faction if it has one, plus the floor's word-travels penalty, +2 at the bar,
+2 with the housekeeping cart (section 5).

| 2d6 | Guest with a language | Guest with none (Beasts, oozes, swarms) |
|---|---|---|
| 2 or less | Attacks | Attacks |
| 3 to 5 | Slams the door, threatens, refuses; a forced entry is a fight | Attacks if approached, else holds its ground |
| 6 to 8 | Talks. Lets him search for a price, an ask, or a successful Influence check | Wary: can be coaxed (Animal Handling) or walked around |
| 9 to 11 | Friendly: lets him search for a small price or a chat; trades knick-knacks | Ignores him; the room can be searched around it |
| 12 or more | Helpful: lets him search, and tells him a true thing about a neighbour | Follows him about |

The roll sets the starting attitude for the Influence rules: 2 to 5 Hostile, 6 to 8
Indifferent, 9 or more Friendly (`Glossary/Attitude.md`). Morale is as in the crunch
rules. A guest that fled is back in its room, at full HP, 8 hours later.

## 5. Factions

Three to start. Each is a card: who, wants, offers, fears, and three deeds. The factions
are a side show: they give asks, prices and consequences, and they never take a turn of
their own. **The Hotel moves when Morten moves it.**

**Standing** with each is a number from −3 to +3, starting at 0, changed only by deeds.
It maps to the SRD attitude: **−3 or −2 Hostile**, **−1 to +1 Indifferent**, **+2 or +3
Friendly**. Members use their faction's standing on the reaction roll. Perks unlock at
Friendly; the Hostile line fires at Hostile and stays until standing recovers.

### The Staff

- **Who:** the desk, the gift shop, housekeeping (random SRD guests in uniform pushing
  carts), and the unseen Manager.
- **Wants:** rooms intact, bills paid, no bodies in the corridors.
- **Offers:** the gift shop; the **register** (which rooms are occupied and when a guest
  is usually out) for a tip of 10 GP × floor; **jobs** (deliver towels to 4xx, fetch a
  cart from 7xx) that are an excuse to enter a room with the guest's consent.
- **Fears:** the Manager's inspection. The Staff never say why.
- **Deeds:** +1 pay a damage bill or finish a job · −1 caught searching without paying
  (the noise check), a body left in a corridor or the lobby, searching a Staff room.
- **Friendly:** the **housekeeping cart and uniform**: +2 on reaction rolls at doors
  ("Housekeeping!"), and the register for free.
- **Hostile:** Morten is **checked out**: room 101 is gone, the shop and the bar refuse
  him, and housekeeping attacks him on sight in corridors (as a wanderer of the floor's
  CR). He squats in searched rooms (section 7). Paying every outstanding bill at the desk
  restores standing to −1 and checks him back in.

### The Residents

- **Who:** five permanent guests with names, chosen by the GM at random from the
  generator's rooms (one every 4 floors or so) and marked **R** in `gm-secrets.md`. They
  have the best pyjamas and opinions about everyone.
- **Wants:** peace, a nicer wing (higher up), and their neighbours gone.
- **Offers:** they **hear the walls hum**: a Friendly Resident names one unsearched room
  on their floor that holds a brick, or says their floor is empty of them; a **bed** (a
  Long Rest in their suite with no noise check), knick-knack trade, gossip about the Ark.
- **Fears:** being moved out.
- **Deeds:** +1 finish an ask (clear a neighbouring room, bring an item, carry a message
  to another Resident) · −1 search a Resident's suite (they never consent) · −2 kill a
  Resident.
- **Friendly:** the hum, on every floor with a Resident, each time he asks.
- **Hostile:** the Residents warn their floors: the word-travels penalty on every floor
  with a Resident is −3 at once, and their asks go to other guests, against him.

### The Ark

- **Who:** the Fiends among the guests (devils, demons, imps and the like), who meet in
  one suite the GM marks **A**. Their ritual is a reverse Noah's Ark: **one of each kind
  of guest in the Hotel must die**.
- **Wants:** a first kill of every kind. They keep a list; the generator's monster list is
  the list.
- **Offers:** a **bounty** for the first kill of each kind, **25 GP × CR** (minimum
  10 GP), double for a Resident, paid on proof (the guest's key tag); potions and poisons
  from `Equipment/` at list price; asks for specific kills at a specific bounty.
- **Fears:** the Staff. A word at the desk ends the Ark's stay.
- **Deeds:** +1 finish an ask · −1 refuse an ask or warn a guest they named · −3 tell the
  Staff (and the Staff +1).
- **Friendly:** a **devil's deal**: once per floor, one fiend joins one fight on Morten's
  side, and remembers it.
- **Hostile:** the Ark hunts him: a fiend wanders every floor the Ark has a room on, and
  the bounties go on him instead.

The three pull against each other: the Staff hate bodies, the Ark wants bodies, the
Residents want their neighbours gone but not themselves. Morten is in the middle, and
every room he searches touches at least one of them. If the side show wants more
later, a kind's guests can be a fourth card on the same pattern (the dragons, the
goblinoids, the zoo); not before.

## 6. Housekeeping (restocking)

After every Long Rest Morten takes, housekeeping turns over the Hotel. Each room he has
searched whose guests are gone or dead has a **1 in 6** chance of a **new guest**: one
random group for that floor (`gen_dungeon.py --floors N --seed <roll d100>`, take the
first row). New guests have luggage and don't know him. **The room stays searched**: no
second brick. Guests who fled are back in their rooms at full HP after 8 hours, as in the
crunch rules. Dead guests stay dead.

## 7. Rest, death and the bill

- **Long Rest in room 101:** safe while the Staff are not Hostile.
- **Long Rest in a searched room** (squatting): once, at the midpoint, roll the **noise
  check** of section 3: on a **1** a new guest's key turns in the lock (reaction roll at
  −2; it's their room now), on a **2** housekeeping finds him (Staff −1 unless Friendly).
- **Long Rest in a Resident's suite:** needs a Friendly Resident; no check.
- **Short Rests** take the wandering check of the crunch rules.
- **Death** works as the crunch house rule. Housekeeping finds him; he wakes in room 101
  (in the lobby's luggage room if checked out) 8 hours later at full HP with all spells.
  **Coins and gems are gone: the bill.** Bricks, gear, spellbook and XP are kept; the Hotel
  returns luggage.

## 8. Events

After every Long Rest, roll **1d6**. On a **5**, something turns up at lost and found
(section 12). On a **6**, roll 1d12 on the table. One event at a time; it plays out over
the next day. "A visited floor" is a random floor Morten has
stood on.

| d12 | Event |
|---|---|
| 1 | **Convention.** A visited floor fills: every empty room gets guests, all of one kind (roll one monster of the floor's band). They have name badges. |
| 2 | **Inspection.** The Manager walks the floors tomorrow. Every unpaid bill is called in (Staff −1 if any stays unpaid), and corridors are patrolled: a wandering check every turn. |
| 3 | **Fire drill.** For one hour tomorrow at a random time, every guest stands in the corridor in pyjamas. Every room is empty and unlocked; every guest is awake and watching the corridor. |
| 4 | **Checkout day.** On a visited floor, half the occupied rooms (round down) empty out; the guests leave with their luggage. Unsearched rooms keep their bricks. |
| 5 | **Renovation.** The Staff close a corridor on a visited floor. Its stair is reached only through one room (the GM picks which). |
| 6 | **The Ark's night.** A guest of some kind is found dead in its room; the Ark ticks the kind (no bounty for Morten on it). The Staff suspect Morten: −1 unless he spent the night in room 101. |
| 7 | **Power cut.** A visited floor is dark for a day: darkness in corridors and rooms. |
| 8 | **Room service.** A cart outside his door: a Potion of Healing and two days of rations, compliments of a faction (1–2 Staff, 3–4 Residents, 5–6 the Ark), who will mention it. |
| 9 | **A complaint.** A guest he searched or slighted complains at the desk: Staff −1 (Residents −1 if it was a Resident). |
| 10 | **Mislaid luggage.** A suitcase stands in a corridor on a visited floor: one sure item of that floor (`loot.py --floor N --sure`) and a knick-knack. Its owner, a random guest of the floor, is looking for it. Bringing it back is +2 on that guest's reaction roll; keeping it, if they find out, is robbery. |
| 11 | **The walls hum.** A Resident, or a dream if none is Friendly, names one unsearched room that holds a brick. |
| 12 | **New resident.** A random guest on a visited floor checks in permanently: a name, pyjamas, an ask. The Residents are now six. |

## 9. Running it

- **Files.** `gm-secrets.md` is the generator's output with the GM's marks: **R** and
  **A** rooms, each room's state (unsearched · searched, brick · searched, empty ·
  restocked by …), and the Cornerstone's secret. `state.md` adds one line each for
  **bricks**, **rooms searched per floor** (the word-travels penalty), **standing** with
  the three factions, **checked in or out**, **unpaid bills**, and the **magic items**
  carried, with the attuned ones marked (three at most) and what the shop window and lost
  and found hold. `rules.md` names the
  Hotel, the seed and anything this campaign does differently. `transcript.md` as always.
  Whether a room holds a brick is rolled when it is searched, so it is never a secret in
  advance.
- **Header.** Every reply opens **Day 3 · 14:20 · Room 412 (floor 4) · Bricks 7 ·
  Staff 0 · Residents +1 · Ark −1**.
- **Rumours.** At the bar, one true line per drink: a room's guest, a faction's current
  ask, or on a 1 on 1d6 a brick's hum.
- **Report style.** The crunch rules' dials apply. A search is an **event**: a few
  bullets (the door and its roll, the price or the fight, the noise check, the brick, the
  luggage). A fight is a fight. There are no domain turns to report; the factions appear
  only as what guests say and do.
- **New game.** Roll Morten's class (`roll.py 1d12`, section 11) and build his sheet.
  Roll the seed (`roll.py 1d100`), generate all 20 floors into
  `gm-secrets.md`, mark five **R** rooms and one **A** suite at random (the Ark's suite
  holds Fiends: reroll the suite's guests from the SRD's Fiends if the generator put a
  Camel there), write the Cornerstone's secret, and open with Morten in room 101 on
  **Day 1 · 08:00**, with his bill at zero. Floors 1 and 2 are for levels 1 and 2 and a
  level 3 Morten walks through them quickly; they are the Hotel teaching him the loop.
- **The end.** When the last room is searched, the last brick comes out, the Cornerstone
  is whole, and the GM opens the secret. The Hotel may have an opinion.

## 10. What is deliberately not here

No overworld, no hexes, no map, no page, no world turn, no clocks, no ownership ladder, no
crafting of magic items beyond the SRD's scrolls and potions, no item economy beyond list
prices.
Factions never act unprompted; the only things that move on their own are housekeeping
(section 6) and the d6 after a Long Rest (section 8). If the game needs more world than
that, add one card or one table row, not a system.

## 11. The Class and the Book (two in one body)

Morten is **two party members in one body**: the **Class**, any of the twelve SRD classes
played by its own rules, and the **Book**, a wizard's spellbook cast from by the crunch
rules' *Roll to cast*. One body, one set of ability scores, one XP total, one turn a
round. This is D&D 3.5's *gestalt* character, made for parties too small to survive; the
body still gets one turn a round, so the action economy that kills a party of one is
untouched. The design record is `hotel-v2-plan.md`.

- **The class is rolled** at a new game, 1d12, each with the SRD's one subclass:
  1 Barbarian (Berserker), 2 Bard (Lore), 3 Cleric (Life), 4 Druid (Land), 5 Fighter
  (Champion), 6 Monk (Open Hand), 7 Paladin (Devotion), 8 Ranger (Hunter), 9 Rogue
  (Thief), 10 Sorcerer (Draconic), 11 Warlock (Fiend), 12 Wizard (Evoker). A 12 makes the
  **double wizard** below.
- **Levels.** Every level is a level in the Class **and** in the Book: at 900 XP he is,
  say, Sorcerer 3 + Book 3. XP, character level and proficiency bonus are one track
  (`Level Advancement.md`). Level 20 is Class 20 + Book 20.
- **Building him.** The 2024 character creation rules with the standard array
  (15/14/13/12/10/8): 13 or more in the Class's primary ability and in Intelligence, as
  for multiclassing. He starts at level 3 with 900 XP, the Class's and the background's
  starting equipment, the Book's spellbook and a wand (an Arcane Focus, 10 GP), and one
  Common magic item (`Starting at Higher Levels.md`; `loot.py --rarity Common`).
- **The body is the Class's.** Hit Dice, hit points, saving throws, skills, weapons,
  armour training and every class and subclass feature, Ability Score Improvements and
  feats included, come from the Class. The Book adds none of these.
- **The Book is the Wizard's Spellcasting feature and nothing else:** cantrips and
  prepared spells by the Wizard table at his level (3 cantrips and 6 prepared at level 3),
  a spellbook of six level 1 wizard spells plus two per level after 1 (ten at level 3),
  spells up to the highest level the Wizard table's slots would give (level 2 at 3, 3 at
  5, 4 at 7, 5 at 9, 6 at 11, 7 at 13, 8 at 15, 9 at 17), Intelligence as its ability
  (save DC 8 + INT + PB, attack INT + PB), an Arcane Focus or the spellbook as its focus,
  and copying found spells at 2 hours and 50 GP a level. **Not** Arcane Recovery, Ritual
  Adept, Scholar, a subclass, Memorize Spell, Spell Mastery or Signature Spells. A Ritual
  spell he has prepared can still be cast as a Ritual, with no check (`Spells.md`).
- **Book spells are always cast by the roll:** the casting check, a fizzled spell lost
  until a Long Rest, the mishap on a 1, the double on a 20. The Book has no slots and no
  slot ever casts a Book spell. With no Arcane Recovery, a lost Book spell stays lost
  until the Long Rest. Spells from an origin feat (*Magic Initiate*) are cast by the roll
  too, with the feat's chosen ability; the feat's free casting once per Long Rest needs no
  check, and a Class with slots may cast the feat's level 1 spell from a slot with no
  check, as the feat says.
- **A Class that casts** (Bard, Cleric, Druid, Paladin, Ranger, Sorcerer, Warlock) keeps
  its own Spellcasting or Pact Magic exactly as written: its slots, its list, its
  ability, no check. Its slots never cast Book spells and the Book never casts its
  spells. A spell on both lists is prepared on one of them. Concentration is one spell
  at a time across both.
- **One slot a turn** (`Spells.md: One Spell with a Spell Slot per Turn`) limits only
  slots, so Book spells are never held back by it: a Book spell with the Magic action and
  a Bonus Action Book spell can share a turn, and a Fighter's Action Surge is a second
  Magic action for a second spell.
- **Features that work on "a spell you cast"** work on Book spells too (a Sorcerer's
  Metamagic, an Evoker's Sculpt Spells). **Features that spend a spell slot** (Divine
  Smite, Font of Magic, a *Pearl of Power*) never touch the Book.
- **Components are real** (`Spells.md: Components`). A Somatic component needs a hand to
  gesture with, a Material component a free hand or the focus held in one. A shortsword
  in one hand and a wand in the other casts anything; a sword and a shield cast nothing
  with S or M until one is put away; a two-handed bow holds in one hand between shots.
  Armour he has training in doesn't stop casting; armour he lacks training in does.
- **One AC formula at a time and Extra Attack once,** as `Multiclassing.md` says: *Mage
  Armor*, Draconic Resilience or Unarmored Defense, not two.
- **The double wizard** (a 12 on the class roll) is the Wizard class as written, with
  spell slots, Arcane Recovery, Ritual Adept, Scholar and the Evoker, **plus** the Book.
  One spellbook and **one list of prepared spells** (the Wizard table's number, not
  twice), and every prepared spell can be cast either way: from a slot, with no check, as
  written; or by the roll. A spell lost to a failed roll can still be cast from a slot; it
  was the improvising that misfired. Arcane Recovery restores slots as written, or lost
  spells as the crunch house rule has it, his choice each time.
- **The sheet** keeps the Class and the Book in separate sections, with the header
  **Morten · Sorcerer 3 (Draconic) + Book 3 · 900 XP**.

## 12. Luggage and magic items

Every guest's luggage holds the generator's coins and a knick-knack as before, and
**sometimes a magic item**, at about twice one character's share of what the 2024 DMG
expects, and fully random.

- **The luggage roll.** When a group of guests is first met (at the door, in a corridor,
  at the bar), the GM rolls **1d20** on its floor's row for the room's luggage, and on a
  hit takes a random item of that rarity from `reference/srd/Magic Items/`:
  `python3 dnd-crunch/tools/loot.py --floor N` does both and prints the item, its
  attunement, its price and its file. One roll per room, not per guest. Guests who
  restock a room bring a fresh roll. A **Resident's suite** and the **Ark's suite** always
  hold an item, rolled one band up: `--sure --band-up` (floors 17–20 stay on their row).
  The result is the GM's until Morten sees the item; write it in `gm-secrets.md`.

| Floors | Nothing | Common | Uncommon | Rare | Very Rare | Legendary |
|---|---|---|---|---|---|---|
| 1–4 | 1–10 | 11–16 | 17–19 | 20 | — | — |
| 5–10 | 1–9 | 10–12 | 13–17 | 18–20 | — | — |
| 11–16 | 1–8 | 9 | 10–12 | 13–16 | 17–19 | 20 |
| 17–20 | 1–8 | — | 9 | 10–12 | 13–17 | 18–20 |

- **Common** is a d6: 1–2 *Potion of Healing*, 3 *Potion of Climbing*, 4 *Bead of
  Nourishment*, 5–6 a **Spell Scroll** of a random level 1 wizard spell. Every other
  rarity is any file in its folder, with the *Varies* items spread into their rarities
  (a *+1 Weapon* is Uncommon, *+1 Armor* Rare, the *Ioun Stones*, *Figurines* and
  *Feather Tokens* by their own lines, scrolls by spell level). A magic weapon or armour
  of no fixed kind gets a random base from `Equipment/`. Anything can turn up anywhere:
  a Camel's suitcase can hold a *Trident of Fish Command*.
- **The guest uses what it can.** A permanent item the guest could wear or wield (armour
  or a weapon it would use, boots, a cloak, a ring, a wand if it casts spells) is in use
  when the door opens, and in its open-table stat line once it can be seen. A guest with
  Intelligence 6 or more drinks its potion when Bloodied. Everything else is in the
  suitcase.
- **Spellbooks.** A guest whose stat block casts wizard spells (a Mage, an Archmage)
  keeps a spellbook in its luggage with those spells, besides the roll.
- **Getting at it** is as before: the guest dead, out, fled, asleep or robbed. A theft
  under its nose is a **Sleight of Hand check against the guest's passive Perception**
  while it is busy (a chat at the door, a Helpful guest's tour of the room), or *Mage
  Hand* (4.5 kg: the item, not the suitcase). Noticed, it is robbery: the reaction drops
  to 2.
- **Knowing what it does** (`Equipment/Magic Items.md`): *Identify* reveals it, so does
  an item held through a Short Rest, and a sip names a potion. Curses are never revealed
  that way (`Cursed Items.md`). Attunement takes another Short Rest, **three items at
  most**, and ends on death: after a respawn he re-attunes, one Short Rest an item.
- **Scrolls** are the Book's best friend: cast with no check if the spell is on his list
  and of a level he can cast (the crunch house rule), or with the SRD's INT check if it is
  higher; or copied into the spellbook (an Arcana check, DC 10 + the spell's level; the
  scroll is used up either way, `Varies/Spell Scroll.md`). A Class caster reads scrolls
  of its own list too.
- **Prices** are the SRD's rarity values (`Magic Item Rarity.md`): Common 100 GP,
  Uncommon 400, Rare 4,000, Very Rare 40,000, Legendary 200,000. A consumable is half
  (a *Potion of Healing* stays 50 GP); a Spell Scroll is twice its scribing cost (a
  level 1 scroll 50 GP, level 2 200, level 3 300); a magic weapon or armour adds its base
  item's price. The gift shop buys at half, Staff Friendly or not.
- **The gift shop's shelf** holds Potions of Healing (50 GP) and three Spell Scrolls,
  `loot.py --scroll 1 --count 3`, restocked every 7 days. Its **window** holds one magic
  item at list price, `loot.py --rarity Uncommon`, rerolled every 7 days or when sold.
  From the day Morten first stands on floor 5, roll 1d6 at each reroll: on a 6 the window
  holds a Rare instead. Staff Friendly: a quarter off the window. Staff Hostile: no shop.
- **Lost and found** at the desk: on a 5 on the d6 after a Long Rest (section 8), an item
  turns up, `loot.py --floor N --sure` for a random visited floor. The Staff sell it at
  list price to the first guest who asks, half price at Staff Friendly. Claiming it
  ("that's mine") is Deception, DC 15: it's his for nothing, or Staff −1 on a failure.
  One item waits at a time; an unclaimed one is sold to a guest after 7 days.
- **Guests sell.** A Friendly guest (9 or more on the reaction) sells an item from its
  luggage at list price, or trades it for a knick-knack and the difference in coins. A
  Helpful guest's true thing about a neighbour can be an item ("the Harpy in 305 keeps a
  wand"), and so can a rumour at the bar.
- **The factions pay in items.** A **Resident's** finished ask pays one item of their
  floor's band (`--floor N --sure`) instead of a knick-knack. **The Ark** pays its bounties
  in coins or in potions, poisons and scrolls at list value, and puts an item on the kills
  it asks for: an Uncommon below floor 11, a Rare from 11 up (`--rarity`). A **Staff job**
  finished pays a Common item (`--rarity Common`) from floor 5 up.
- **Crafting** in the quiet hours is the SRD's: scribing a Spell Scroll
  (`Equipment/Scribing Spell Scrolls.md`: a level 1 scroll is 1 day and 25 GP, needs
  Arcana or Calligrapher's Supplies and the spell prepared) and brewing Potions of Healing
  (Herbalism Kit). A day of work is 8 hours in room 101 or a searched room.
- **Death** keeps items, as before: the Hotel returns luggage. Attunement ends, as above.
