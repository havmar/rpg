# The Hotel

The Hotel for 13th Age: a megadungeon that is a hotel, searched room by room by one
character who is also a guest. These add to `13th-age/CLAUDE.md` (the table, the house
rules, the report style, the GM) and win where they differ. Everything here is public:
Morten may know all of it. The design is this page; there is no map and no engine. The
dice are `tools/roll.py`, the rooms come from `tools/gen_hotel.py`, the magic items from
`tools/loot.py`.

## 1. The premise

The Hotel was built from the ruins of a civilisation nobody remembers, and its
**Cornerstone** was broken into bricks and mortared into the rooms. Morten is the only
guest who can hear a brick in a wall, and the only one who can pull it out: that is his
One Unique Thing. He is here to reassemble the Cornerstone, which means **searching every
room in the Hotel**. What a finished Cornerstone does is the GM's secret, written in
`gm-secrets.md` before play.

The vibe is surreal and matter-of-fact. Every guest is a 13th Age monster, chosen at random
and never explained. A Wererat with a suitcase and pyjamas has room 112 and sees nothing odd
about it. The Staff speak of the Hotel's rules as policy. Nobody is surprised by anything
except Morten turning their room over. The narration stays minimal: one terse line per
room, one line of speech when it carries information, and every guest named with its
level and role.

Morten is a registered guest. He has a room on floor 1, a key, and a bill.

## 2. The building

- **Ten floors**, one per character level: floor N is built for a level N Morten, and
  its 12 rooms are about one level's worth of battles. Floors 1 to 4 are **adventurer** tier,
  5 to 7 **champion**, 8 to 10 **epic**: the tier sets the skill DCs, the potions and the
  items found there. Room 3.1 is **room 301**, up to 312; the rooms open off one corridor
  in number order, with a stair at each end. Nothing is locked but doors. Higher floors
  are deadlier, which is the only gate.
- **Each room** holds 1 to 4 guests of one random kind, or a mob of 3 to 8 mooks, worth
  0.7, 1 or 1.5 standard monsters for one character, with one piece of **furniture** that
  matters in a fight (wardrobes to get behind, a mezzanine far away up a ladder, a narrow
  hallway where only one can engage, a hole into the room below, a chandelier, steam in
  which nothing is far away). The generator rolls all of it.
- **The lobby** is the ground floor: the **desk** (the bill, the register, lost and
  found), the **gift shop** (gear at the SRD's prices, `Equipment-Price-Guide.md`; one-use
  items and a window, section 12), the **bar** (a truce by policy: no violence; one true
  rumour per drink, 1 gp), and the **lift**, which stops at every floor Morten has stood on.
- **Morten's room** is **100**, at the stair end of floor 1: not one of the rooms to search, and
  a safe bed while the Staff are not Hostile.
- **The Manager** has never been seen. The Staff speak of them in the present tense.

## 3. The search (the loop)

Every room is handled the same way, door to door.

1. **Listen** (1 turn, a Wisdom skill check, or just knock).
2. **The door.** The guest answers. Roll the **reaction** (section 4). Morten says what he
   wants: to search the room. Most guests find that repugnant. With an offer (a gift, a
   favour, a good story) he rolls a **skill check**: d20 + CHA (or the ability the
   approach uses) + level + a background, against the floor's tier DC, **hard** for a
   guest that talks but is unwilling, **normal** once it is Friendly. It needs a guest that
   understands him; a beast is coaxed with an animal background and WIS instead. A failure
   falls forward: the guest names a price, or lets him in to watch him closely, or slams
   the door with a clue on the way. A **gift** (coins or a knick-knack worth 5 gp × floor)
   moves the reaction one row up, once per door.
3. **Or not the door.** He can wait until the room is empty (the register, an event, a
   stakeout), sneak in, lure the guest out, or fight. A guest that is out, asleep, fled or
   dead doesn't object.
4. **The search** takes **1 hour** (6 turns) and is **loud**: furniture over, walls
   tapped, the brick's name shouted. Once during the hour roll the **noise check**, 1d6:
   - **1:** a guest from a random occupied room on the floor comes to look. Reaction roll
     at −2.
   - **2:** housekeeping arrives. Staff standing −1, unless he pays the **damages**
     (10 gp × floor) on the spot.
   - **3 to 6:** nothing yet.
5. **The brick.** Roll 1d6: on a **1 or 2** a brick comes out of the wall. The **last
   unsearched room in the Hotel always holds the last brick**; the Hotel knows. Bricks go
   in his bag and are never lost on death.
6. **The battle and the luggage.** A searched room is **one battle** on the heal-up clock
   (`CLAUDE.md`, House rules), weighted by its difficulty (Easy 0.7, Normal 1, Hard 1.5)
   and earned **once, when its search completes**, however he got in. Every guest has luggage: the generator's coins in a suitcase, plus one
   **knick-knack** the GM names in a few words (a snow globe of the Hotel, a monogrammed
   toothbrush, a brass key to nothing) worth 1d6 × floor gp at the gift shop or to a
   Friendly guest, and sometimes a **magic item** (section 12). Taking luggage while the
   guest lives is robbery: the reaction drops to 2.

**Word travels.** Reaction rolls on a floor take **−1 for every room Morten has searched
there**, to a maximum of −3. New guests who check in later don't know him yet.

**Corridors.** Walking a corridor is a turn; every 3 turns roll 1d6, and on a 1 a
**wanderer** comes: a guest from a random occupied room on that floor, on its way to the
bar or the bathroom, with a reaction roll. A fight with a wanderer is a battle, weighted as one guest of its room.

## 4. Reaction roll

On first contact with any guest, **2d6 + Morten's CHA modifier**, plus the standing of
the guest's faction if it has one, plus the floor's word-travels penalty, +2 at the bar,
+2 with the housekeeping cart (section 5).

| 2d6 | Guest that talks | Guest that doesn't (beasts, oozes, mindless things) |
|---|---|---|
| 2 or less | Attacks | Attacks |
| 3 to 5 | Slams the door, threatens, refuses; a forced entry is a fight | Attacks if approached, else holds its ground |
| 6 to 8 | Talks. Lets him search for a price, an ask, or a hard skill check | Wary: can be coaxed or walked around |
| 9 to 11 | Friendly: lets him search for a small price or a chat (a normal check, or none) | Ignores him; the room can be searched around it |
| 12 or more | Helpful: lets him search, and tells him a true thing about a neighbour | Follows him about |

Whether a guest talks is the GM's call from its type and stat block. A guest that fled is
back in its room, at full HP, 8 hours later.

## 5. Factions (the Hotel's icons)

Three to start. Each is a card: who, wants, offers, fears, and three deeds. They give asks,
prices and consequences, and they never take a turn of their own. **The Hotel moves when
Morten moves it.** They are also his **icons**: 13th Age's relationship dice, rolled at
each full heal-up.

**Standing** with each is a number from −3 to +3, changed by deeds. Morten's 3 icon
relationship points set where he starts (the default is Staff +1, Residents +1, Ark −1),
and he gains one more point to place at levels 5 and 8 (`Icon-Relationships.md`). Members
use their faction's standing on the reaction roll. **Friendly** is +2 or +3, **Hostile**
−2 or −3; the perks unlock at Friendly, the Hostile line fires at Hostile and stays until
standing recovers.

**Icon dice.** At each full heal-up, roll **1d6 per point of standing** with each faction
(+2 or −2 rolls two dice; 0 rolls none). A **6** means the faction gives him an advantage
before the next heal-up, a **5** the same with a complication (an obligation from a
friend, unwanted attention from a foe). A positive standing helps outright (a key, a tip,
the register, a guest who owes them); a negative one gives inside knowledge, or help from
the faction's rivals. The GM names each result in one line when it comes up, and it is
spent when used.

### The Staff

- **Who:** the desk, the gift shop, housekeeping (random guests in uniform pushing carts),
  and the unseen Manager.
- **Wants:** rooms intact, bills paid, no bodies in the corridors.
- **Offers:** the gift shop; the **register** (which rooms are occupied and when a guest
  is usually out) for a tip of 10 gp × floor; **jobs** (deliver towels to 4xx, fetch a
  cart from 7xx) that are an excuse to enter a room with the guest's consent.
- **Fears:** the Manager's inspection. The Staff never say why.
- **Deeds:** +1 pay a damage bill or finish a job · −1 caught searching without paying
  (the noise check), a body left in a corridor or the lobby, a campaign loss (the incident
  report).
- **Friendly:** the **housekeeping cart and uniform**: +2 on reaction rolls at doors
  ("Housekeeping!"), and the register for free.
- **Hostile:** Morten is **checked out**: room 100 is gone, the shop and the bar refuse
  him, and housekeeping attacks him on sight in corridors (a wanderer worth 1 standard
  monster of the floor). He squats in searched rooms (section 7). Paying every
  outstanding bill at the desk restores standing to −1 and checks him back in.

### The Residents

- **Who:** five permanent guests with names, chosen by the GM at random from the
  generator's rooms (one every two floors) and marked **R** in `gm-secrets.md`. They have
  the best pyjamas and opinions about everyone.
- **Wants:** peace, a nicer wing (higher up), and their neighbours gone.
- **Offers:** they **hear the walls hum**: a Friendly Resident names one unsearched room
  on their floor that holds a brick, or says their floor holds none; a **bed** (a full
  heal-up in their suite with no noise check), knick-knack trade, gossip about the Ark.
- **Fears:** being moved out.
- **Deeds:** +1 finish an ask (clear a neighbouring room, bring an item, carry a message
  to another Resident) · −1 search a Resident's suite (they never consent) · −2 kill a
  Resident.
- **Friendly:** the hum, on every floor with a Resident, each time he asks.
- **Hostile:** the Residents warn their floors: the word-travels penalty on every floor
  with a Resident is −3 at once, and their asks go to other guests, against him.

### The Ark

- **Who:** the demons and devils among the guests, who meet in one suite the GM marks
  **A**. Their ritual is a reverse Noah's Ark: **one of each kind of guest in the Hotel
  must die**.
- **Wants:** a first kill of every kind. They keep a list; the generator's guests are
  the list.
- **Offers:** a **bounty** for the first kill of each kind, **10 gp × the guest's level**
  (minimum 10 gp), double for a Resident, paid on proof (the guest's key tag); potions and
  oils at list price; asks for specific kills at a specific bounty.
- **Fears:** the Staff. A word at the desk ends the Ark's stay.
- **Deeds:** +1 finish an ask · −1 refuse an ask or warn a guest they named · −3 tell the
  Staff (and the Staff +1).
- **Friendly:** a **devil's deal**: once per floor, one fiend joins one fight on Morten's
  side (it takes its own turns), and remembers it.
- **Hostile:** the Ark hunts him: a fiend wanders every floor the Ark has a room on, and
  the bounties go on him instead.

The three pull against each other: the Staff hate bodies, the Ark wants bodies, the
Residents want their neighbours gone but not themselves. Every room he searches touches at
least one of them.

## 6. Housekeeping (restocking)

After every full heal-up, housekeeping turns over the Hotel. Each room he has searched
whose guests are gone or dead has a **1 in 6** chance of a **new guest**: one random group
for that floor (`gen_hotel.py --floors N --seed <roll d100> --rooms 1`). New guests have
luggage and don't know him. **The room stays searched**: no second brick, and no battle for
searching it again (a fight with them is still a battle). Dead guests stay dead.

## 7. Rest, death and the bill

- **A full heal-up** is 8 hours' sleep in a bed: in **room 100** while the Staff are not
  Hostile; in a **Resident's suite** with a Friendly Resident, no check; or **squatting** in
  a searched room, with one noise check at the midpoint: on a **1** a new guest's key turns
  in the lock (reaction roll at −2; it's their room now), on a **2** housekeeping finds
  him (Staff −1 unless Friendly). With Battles under 4, it is also a
  campaign loss (`CLAUDE.md`). Then the icon dice (section 5), housekeeping (section 6)
  and the event roll (section 8), in that order.
- **Quick rests** after each battle take a turn, as the SRD's.
- **Death** works as the house rule. Housekeeping finds him; he wakes in room 100 (in the
  lobby's luggage room if checked out) 8 hours later with a full heal-up. **Coins and gems
  are gone: the bill.** Bricks, gear, magic items, levels and advances are kept; the Hotel
  returns luggage.

## 8. Events

After every full heal-up, roll **1d6**. On a **5**, something turns up at lost and found
(section 12). On a **6**, roll 1d12 on the table. One event at a time; it plays out over
the next day. "A visited floor" is a random floor Morten has stood on.

| d12 | Event |
|---|---|
| 1 | **Convention.** A visited floor fills: every empty room gets guests, all of one kind (one group from the generator for that floor). They have name badges. |
| 2 | **Inspection.** The Manager walks the floors tomorrow. Every unpaid bill is called in (Staff −1 if any stays unpaid), and corridors are patrolled: a wandering check every turn. |
| 3 | **Fire drill.** For one hour tomorrow at a random time, every guest stands in the corridor in pyjamas. Every room is empty and unlocked; every guest is awake and watching the corridor. |
| 4 | **Checkout day.** On a visited floor, half the occupied rooms (round down) empty out; the guests leave with their luggage. Unsearched rooms keep their bricks. |
| 5 | **Renovation.** The Staff close a corridor on a visited floor. Its stair is reached only through one room (the GM picks which). |
| 6 | **The Ark's night.** A guest of some kind is found dead in its room; the Ark ticks the kind (no bounty for Morten on it). The Staff suspect Morten: −1 unless he spent the night in room 100. |
| 7 | **Power cut.** A visited floor is dark for a day, corridors and rooms. |
| 8 | **Room service.** A cart outside his door: a healing potion of his tier, compliments of a faction (1–2 Staff, 3–4 Residents, 5–6 the Ark), who will mention it. |
| 9 | **A complaint.** A guest he searched or slighted complains at the desk: Staff −1 (Residents −1 if it was a Resident). |
| 10 | **Mislaid luggage.** A suitcase stands in a corridor on a visited floor: one sure item of that floor (`loot.py --floor N --sure`) and a knick-knack. Its owner, a random guest of the floor, is looking for it. Bringing it back is +2 on that guest's reaction roll; keeping it, if they find out, is robbery. |
| 11 | **The walls hum.** A Resident, or a dream if none is Friendly, names one unsearched room that holds a brick. |
| 12 | **New resident.** A random guest on a visited floor checks in permanently: a name, pyjamas, an ask. The Residents are now six. |

## 9. Running it

- **Files.** `gm-secrets.md` is the generator's output with the GM's marks: **R** and
  **A** rooms, each room's state (unsearched · searched, brick · searched, empty ·
  restocked by …), the luggage rolled, and the Cornerstone's secret. `state.md` adds one
  line each for **bricks**, **rooms searched per floor** (the word-travels penalty),
  **standing** with the three factions and any unspent icon results, **checked in or
  out**, **unpaid bills**, and the **magic items** carried (chakra, quirk), with what the
  shop window and lost and found hold. Whether a room holds a brick is rolled when it is
  searched, so it is never a secret in advance.
- **Header.** Every reply opens **Day 3 · 14:20 · Room 412 (floor 4) · Bricks 7 ·
  Staff +1 · Residents +1 · Ark −1 · Battles 2.7/4 · Progress 6.2/12**.
- **Rumours.** At the bar, one true line per drink: a room's guest, a faction's current
  ask, or on a 1 on 1d6 a brick's hum.
- **Report style.** The table's dials apply. A search is an **event**: a few bullets (the
  door and its roll, the price or the fight, the noise check, the brick, the luggage). A
  fight is a fight.
- **New game.** Build Morten (`CLAUDE.md`, New game defaults). Roll the seed
  (`roll.py 1d100`) and generate all ten floors into `gm-secrets.md`. Mark five **R** rooms
  (one on every second floor, guests that talk) and one **A** suite (its guests rerolled as
  demons or devils of the floor's band if the generator put something else there). Write
  the Cornerstone's secret, and open with Morten in room 100 on **Day 1 ·
  08:00**, with his bill at zero.
- **The end.** When the last room is searched, the last brick comes out, the Cornerstone
  is whole, and the GM opens the secret. The Hotel may have an opinion.

## 10. What is deliberately not here

No overworld, no map, no grid, no clocks beyond the heal-up count, no crafting, no item
economy beyond the prices below. Factions never act unprompted; the only things that move
on their own are housekeeping (section 6), the icon dice and the d6 after a full heal-up
(sections 5 and 8). If the game needs more world than that, add one card or one table row,
not a system.

## 11. Magic items, the 13th Age way

- **Chakras.** A true magic item sits in a chakra (armour, belt, boots, cloak, gloves,
  helmet, necklace, two rings, shield, a wand, staff or symbol, a melee and a ranged
  weapon, ammunition, a book, and any number of wondrous items) and only one per chakra
  works (`Chakras.md`). Each has a **default bonus** by tier and usually a power with a
  recharge (once a day sure, then 6+, 11+ or 16+ after the battle it was used in).
- **An item found on a higher floor is that floor's tier**: items listed as adventurer
  scale up with their "(champion: …; epic: …)" numbers.
- **Quirks and the limit.** Every true item has a personality and a **quirk**. Morten can
  wield **as many as his level** (an item a tier above counts as two) and the quirks only
  tug at him; over the limit, the items run him (`True-Magic-Items.md`). The GM plays the
  quirks, briefly, when they matter.
- **Knowing what it does:** an item tells him when he takes it into its chakra, which takes
  a quick rest. Cursed items lie (`Cursed-Magic-Items.md`).

## 12. Luggage and the shop

- **The luggage roll.** When a room's guests are first met (at the door, in a corridor, at
  the bar), the GM rolls once for the room with `python3 13th-age/tools/loot.py --floor N`:
  1d20, **1–9** nothing magic, **10–16** a **one-use item** of the floor's tier (a healing
  potion on 1–3 of a d6, a resistance potion on 4, an oil on 5, a rune on 6), **17–20** a
  **true magic item** of the floor's tier (one in ten cursed). About two true items a
  floor, twice what a 13th Age character gets in a level, with the wielding limit as the
  brake. A **Resident's suite** and the **Ark's suite** always hold a true item
  (`loot.py --true <tier>`). The result is the GM's until Morten sees it; write it
  in `gm-secrets.md`.
- **The guest uses what it can**: a potion when staggered, an oil before the fight, a
  weapon or armour it would wield (in its stat line once seen, the default bonus added).
- **Getting at it** is as before: the guest dead, out, fled, asleep or robbed. A theft
  under its nose is a DEX skill check against the tier's **hard** DC; noticed, it is
  robbery.
- **Prices.** One-use items at the SRD's prices (`One-Use-Items.md`: healing potions 50 /
  100 / 200 gp by tier, resistance potions and oils 100 / 200 / 400, runes 150 / 300 /
  600). True magic items have no SRD price, so the Hotel sets one: **300 gp adventurer,
  1,000 gp champion, 2,500 gp epic**. The gift shop buys anything at half.
- **The gift shop's shelf** holds healing potions of every tier Morten has reached, and
  three one-use items (`loot.py --one-use <tier> --count 3`), restocked every 7 days. Its
  **window** holds one true magic item of his tier (`loot.py --true <tier>`), rerolled
  every 7 days or when sold. Staff Friendly: a quarter off the window. Staff Hostile: no
  shop.
- **Lost and found** at the desk: on a 5 on the d6 after a full heal-up (section 8), an
  item turns up, `loot.py --floor N --sure` for a random visited floor. The Staff sell it
  at list price to the first guest who asks, half price at Staff Friendly. Claiming it
  ("that's mine") is a CHA skill check at the tier's hard DC: it's his for nothing, or
  Staff −1 on a failure. One item waits at a time; an unclaimed one is sold after 7 days.
- **Guests sell.** A Friendly guest sells an item from its luggage at list price or trades
  it for a knick-knack and the difference. A Helpful guest's true thing about a neighbour
  can be an item, and so can a rumour at the bar.
- **The factions pay in items.** A **Resident's** finished ask pays one item of their
  floor (`--floor N --sure`) instead of a knick-knack. **The Ark** pays bounties in coins
  or potions and oils at list value, and puts a true item on the kills it asks for
  (`--true <tier>`). A **Staff job** finished pays a one-use item of the floor's tier.
- **Death** keeps items, as before: the Hotel returns luggage.
