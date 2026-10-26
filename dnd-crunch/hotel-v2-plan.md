# Hotel v2: two in one body, and the luggage (a plan)

**Status: proposed, not built.** Two additions to the Hotel (`hotel.md`): a class system
where the guest is **two party members in one body** (any SRD class plus a roll-to-cast
wizard's spellbook, both levelling together), and **magic items**, rolled from guests'
luggage at roughly the 2024 DMG's rate but more generous and random. Everything here is a
proposal for the human to pick from; section 7 lists the choices that are theirs, and
section 8 what gets built once they have chosen. The rules text in sections 2 and 4 is
written to be pasted into `hotel.md` as sections 11 and 12.

## 1. The class question, answered

The ask: the guest is always at least part wizard with roll to cast, but can be another
class too. The version the human really wants: **start as a non-wizard and get two levels
at every level, one in the class and one in wizard, automatically**; the wizard half gives
only the spells (roll to cast), never the wizard's class features; and a wizard can take
the wizard half twice, getting spell slots on top of the roll.

**Yes, it makes sense, and it has a name.** It is the *gestalt character* from D&D 3.5's
*Unearthed Arcana*: at every level the character takes a level in two classes at once,
keeps the better Hit Die and saves, and gets both classes' features. It was written for
small parties, which is exactly the Hotel's problem: a party of one. It works in 5e for a
reason worth saying out loud: **a gestalt body still gets one turn a round.** What kills a
solo character is action economy (the crunch rules say so in *Encounters for a party of
one*), and two classes in one body don't fix that. They add hit points, armour, options and
a second resource pool, which is the right kind of help: Morten dies less, but the fights
are still his to lose. Floor N stays built for a level N character and "deadlier floors are
the only gate" stays true; if the Hotel turns out too soft, floors can be generated one
level up (section 7).

The wizard half stripped to its spells is also self-balancing, because **the casting
check runs on Intelligence**. A Fighter with INT 13 casts at +3 at level 3 (65 % for a
level 1 spell, 60 % for level 2) where Morten casts at +5 (75 % and 70 %). The fighter
pays for every spell with a worse die, no Arcane Recovery, and a standard array that had
to find 13 for INT after 15 for STR. The wizard pays with d6 hit points and no armour. The
*Headband of Intellect* (Uncommon, INT 19) becomes the funniest item in the building.

**Why gestalt and not SRD multiclassing.** The simple version (one level track split
between Wizard and another class by `Multiclassing.md`, the wizard side rolling to cast)
works and needs no new rules, but it makes a weaker character than today's Morten, not a
stronger one: a Fighter 2 / Wizard 1 at level 3 has one level 1 spell list and no
subclass. Since the Hotel's one-body party is already the hardest mode of D&D, a rule that
adds rather than splits is the better fit, and it's the one the human described. The
multiclass version stays available as a campaign's `rules.md` choice for a grittier game.

## 2. The rules: the Class and the Book (draft for `hotel.md` section 11)

Every guest-hero in the Hotel is **two party members in one body**: the **Class**, any of
the twelve SRD classes played by its own rules, and the **Book**, a wizard's spellbook
cast from by the roll-to-cast house rule. One body, one set of ability scores, one XP
total, one turn a round.

- **Levels.** XP and character level are one track (`Level Advancement.md`). Every level
  is a level in the Class **and** a level in the Book, so a level 3 character is
  Fighter 3 + Book 3. Proficiency bonus is by character level. Level 20 is Class 20 +
  Book 20.
- **Prerequisites.** 13 in the Class's primary ability and 13 in Intelligence, as for
  multiclassing. The standard array (15/14/13/12/10/8) always allows it.
- **The body is the Class's.** Hit Dice, hit points, saving throws, skills, weapons,
  armour training, starting equipment and every class and subclass feature, including
  Ability Score Improvements and feats, come from the Class. The Book adds none of these.
- **The Book is the Wizard's Spellcasting feature and nothing else:** cantrips and
  prepared spells by the Wizard table at Book level (3 cantrips and 6 prepared at Book 3),
  a spellbook that starts with six level 1 wizard spells and gains two per level, the
  highest spell level the Wizard table's slots would give (level 2 at Book 3, 3 at 5, 4
  at 7, 5 at 9, 6 at 11, 7 at 13, 8 at 15, 9 at 17), Intelligence as the spellcasting
  ability, an Arcane Focus or the spellbook as focus, copying found spells and scrolls at
  the Wizard's cost. **No** Arcane Recovery, Ritual Adept, Scholar, subclass, Memorize
  Spell, Spell Mastery or Signature Spells. A prepared Ritual spell can still be cast as a
  Ritual (`Spells.md: Rituals`), without a check.
- **Book spells are always cast by the roll** (the crunch rules' *Roll to cast*): the
  casting check, spells lost until a Long Rest, mishaps on a 1, the double on a 20. No
  spell slot ever casts a Book spell and the Book gives no slots. A lost Book spell stays
  lost until the Long Rest; there is no Arcane Recovery to buy it back.
- **Components are real.** A Somatic component needs a free hand or the hand holding the
  focus (`Spells.md: Components`). A sword-and-shield Fighter can't cast Somatic spells
  without sheathing something; a two-handed weapon frees a hand between attacks; a
  Quarterstaff that is an Arcane Focus does both jobs. Armour you have training in doesn't
  stop casting; armour you don't does.
- **Class features that work on "a spell you cast" work on Book spells:** a Sorcerer's
  Metamagic, a Fighter's Action Surge (two Magic actions in a turn; the one-spell limit
  applies only to Bonus Action spells in the 2024 rules), an Evoker's Sculpt Spells.
  Features that work on spell slots (a Paladin's smite spells, a Pearl of Power) don't
  touch the Book.
- **The double wizard** is Class Wizard + Book: the Wizard class as written, **with spell
  slots**, Arcane Recovery, Ritual Adept, Scholar, a subclass and the rest, plus the Book.
  One spellbook and one list of prepared spells, cast either from a slot (no check, as
  written) or by the roll. A spell lost by a failed roll can still be cast from a slot;
  it is the improvising that misfired. Arcane Recovery restores slots as written, or
  lost spells as the crunch house rule has it, the player's choice each time.
- **Multiple AC calculations and Extra Attack** follow `Multiclassing.md`: one AC
  formula at a time (a Monk/Book picks Unarmored Defense or *Mage Armor*), Extra Attack
  never stacks.
- **Starting kit.** The Class's starting equipment and the background's, plus a
  spellbook with six level 1 wizard spells and a wand (an Arcane Focus, 10 GP).
- **Sheet header:** **Morten · Fighter 3 (Champion) + Book 3 · 900 XP**. The
  campaign's `character.md` keeps the Class and the Book in separate sections.

**Worked example: Fighter 3 (Champion) + Book 3.** Human, Sage. STR 15, CON 14, INT 13,
DEX 12, WIS 10, CHA 8 before the background's +2/+1 (Sage puts +2 INT, +1 CON: INT 15,
CON 15). HP 10 + 2 + 2 × (6 + 2) = 28 (Morten has 20). Chain Mail AC 16, or Mage Armor's
13 + DEX for a quieter night. Greatsword 2d6+3 with the Graze mastery, a Quarterstaff focus
as the backup. Second Wind, Action Surge (a Fire Bolt and a greatsword swing in one turn,
or two spells), Improved Critical. Book: Fire Bolt, Light, Mage Hand; prepared Mage Armor,
Shield, Sleep, Thunderwave, Misty Step, Web; casting check d20 +4 (PB 2, INT 2). He kicks
doors Morten only talked at, and his spells fizzle a little more often.

**Worked example: the double wizard.** Today's Morten with the Wizard 3 column of the
Wizard table added: four level 1 slots and two level 2 slots a day that never fizzle, on
top of everything he does now. That is a buff, and the obvious conversion for `hotel1` if
the human wants it (section 7).

**The loop opens up.** The Hotel's three ways into a room (section 3 of `hotel.md`) now
have a class each: a Bard or Paladin talks (Persuasion, Intimidation), a Rogue or Ranger
stakes out and sneaks, a Fighter or Barbarian fights. The Book is the fourth way for all
of them: Sleep, Web, *Comprehend Languages* for the Camel.

## 3. The item question, answered

The ask: magic items at roughly the DMG's recommended amount and rarity, but more
generous and random; a loot roll whenever Morten has access to a room's luggage (the guest
dead or robbed); rare chances to buy from the shop or friendly guests; and whatever other
obvious channels there are.

**The DMG's rate.** The 2024 DMG's *Magic Items Awarded by Level* table says a party
should receive about 6 Common, 4 Uncommon and 1 Rare item over levels 1–4, consumables
counted ([confirmed from a secondary source](https://rpgbot.net/openvideo/v/2024-dnd-expects-more-magic-items-than-2014);
the table is not in the SRD). The rest of the table, as I remember it and as *Xanathar's
Guide*'s minor-items table had it: levels 5–10: 10 C, 17 U, 6 R, 1 VR; levels 11–16: 3 C,
7 U, 11 R, 7 VR, 2 L; levels 17–20: 5 R, 11 VR, 9 L. About 100 items over a campaign
**for a party of four**, so about 25 per character. The proportions matter more than the
totals; the human should check the totals against the book if they have it.

**The Hotel's rate.** A seed-10 Hotel has 175 rooms: 31 on floors 1–4, 73 on 5–10, 46 on
11–16, 25 on 17–20. Morten gets at a room's luggage when the guest is dead, out, fled or
robbed, so perhaps 60 % of rooms. The table in section 4 gives a magic item on about half
of those, which comes to roughly **60 items over the Hotel**: a bit over twice one
character's DMG share, well under a whole party's. The six marked suites always hold one.
Add the shop window and lost and found and he sees perhaps 70. That is generous; the real
cap on power is the one the DMG relies on too, **three attuned items** (`Glossary/Attunement.md`).
The die size is the generosity dial (section 7).

**Random, really.** The item is a random file from `reference/srd/Magic Items/<Rarity>/`
(73 Uncommon, 82 Rare, 56 Very Rare, 32 Legendary), with the *Varies* folder's entries
spread into their rarities (+1 weapons and shields Uncommon, +1 armour Rare, the potions
and figurines by their tables, Spell Scrolls by spell level). A Camel's suitcase can hold a
*Trident of Fish Command*. That is the Hotel.

## 4. The rules: luggage and magic items (draft for `hotel.md` section 12)

Every guest's luggage holds the generator's coins and a knick-knack as before, and
**sometimes a magic item**.

- **The luggage roll.** When a guest is first met (the door, the corridor, the bar), the
  GM rolls **1d20** on the floor's row and, on a hit, picks the item at random from the
  SRD's folder for that rarity (`tools/loot.py --floor N` does both). A room restocked by
  housekeeping gets a fresh roll with its new guests. Residents' suites and the Ark's suite
  always hold an item: reroll a miss, and roll on the next floor band's row (floors 17–20
  stay on their own).

| Floors | Miss | Common | Uncommon | Rare | Very Rare | Legendary |
|---|---|---|---|---|---|---|
| 1–4 | 1–10 | 11–16 | 17–19 | 20 | — | — |
| 5–10 | 1–9 | 10–12 | 13–17 | 18–20 | — | — |
| 11–16 | 1–8 | 9 | 10–12 | 13–16 | 17–19 | 20 |
| 17–20 | 1–8 | — | 9 | 10–12 | 13–17 | 18–20 |

- **Common** is a d6: 1–2 *Potion of Healing*, 3 *Potion of Climbing*, 4 *Bead of
  Nourishment*, 5–6 a **Spell Scroll** of a random level 1 wizard spell. Scrolls are the
  Book's lifeblood: cast with no check, or copied into the spellbook (DC 10 + level
  Arcana check, the scroll is used up either way, `Varies/Spell Scroll.md`).
- **The guest uses what it can.** A permanent item the guest could wear or wield (a
  weapon it is proficient with, armour, boots, a wand if it casts spells) is in use when
  the door opens, and is in its open-table stat line if it can be seen. A guest with
  Intelligence 6 or more drinks its potion when Bloodied. Everything else is in the
  suitcase.
- **Spellbooks.** A guest whose stat block casts wizard spells (a Mage, an Archmage) has
  its spells in a spellbook in its luggage. Copying costs the usual 2 hours and 50 GP per
  spell level.
- **Getting at it** is as before: the guest dead, out, fled, asleep or robbed. Robbery is
  a Sleight of Hand check against the guest's passive Perception while it is distracted
  (a chat at the door, a Helpful tour of the room), or *Mage Hand* through a window
  (4.5 kg: the item, not the suitcase). Noticed, the reaction drops to 2, as before.
- **Knowing what it does.** *Identify* (a level 1 Ritual; the Book needs it prepared, the
  double wizard casts it from the book) or an hour's handling during a Short Rest tells
  him what an item does and how to use it; a potion is known by a sip. Curses are never
  revealed that way (`Cursed Items.md`); the *Sword of Vengeance* and the *Berserker Axe*
  are in the folders like everything else, and lost and found is where they end up.
- **Prices.** The SRD's rarity values: Common 100 GP, Uncommon 400, Rare 4,000, Very
  Rare 40,000, Legendary 200,000; consumables half (a *Potion of Healing* stays 50 GP);
  a Spell Scroll twice its scribing cost (level 1: 50 GP, level 2: 200, level 3: 300). A
  magic weapon or armour adds the base item's price. The gift shop buys at half.
- **The gift shop** stocks *Potions of Healing* and three random level 1 scrolls
  (restocked every 7 days) and has a **window**: one random Uncommon item at list price,
  rerolled every 7 days or when sold. From the day Morten first stands on floor 5, the
  reroll shows a Rare instead on a 6 on 1d6. Staff Friendly: a quarter off the window;
  Staff Hostile: no shop.
- **Lost and found** (the desk) replaces event 10's one-off: after every Long Rest, on a
  6 on 1d6 a random item of a visited floor's band turns up (reroll a miss). The Staff
  sell it at list price to the first guest who asks, half at Staff Friendly; a Deception
  check DC 15 ("that's mine") takes it for nothing, and a failure is Staff −1.
- **Friendly guests** (9 or more on the reaction roll) sell an item from their luggage at
  list price or trade it for a knick-knack and coins; Helpful ones name a neighbour's item
  as their true thing. **Residents** pay a finished ask with an item of their floor's
  band (a sure roll) instead of a knick-knack. **The Ark** pays bounties in potions,
  poisons and scrolls of any rarity at list value, and offers an Uncommon (a Rare from
  floor 11) as the bounty for a kill it asks for. **Jobs** for the Staff pay a Common item
  from floor 5 up. **The bar**'s rumour can be an item: "the Harpy in 303 keeps a wand".
- **Death.** Items are kept, as before; the Hotel returns luggage.

## 5. Other ways to offer items (asked for; take or leave)

Each is one line or one table row, in the spirit of `hotel.md` section 10. The ones in
section 4 are the ones I'd take; these are the rest.

- **Crafting in the quiet hours.** `Equipment/Scribing Spell Scrolls.md` (a level 1 scroll
  is 1 day and 25 GP) and *Brewing Potions of Healing* already exist and suit the double
  wizard with Calligrapher's Supplies: a day in room 101 turns gold into a no-check cast.
- **Events.** A *Trade fair* row (a visited floor fills with merchant guests who sell
  Uncommon items for one day), a *Mislaid luggage* row (a suitcase in the corridor: one
  sure roll, and a guest looking for it), an *Auction at the bar* row (the Ark sells the
  dead's effects to the highest bidder).
- **The bricks.** Carrying N bricks could be a property (a +1 to something per three
  bricks, or a daily charge of *Stone Shape*). That belongs with the Cornerstone's secret in
  `gm-secrets.md`, not in the open rules.
- **Minibar and safe.** A safe in each room (Thieves' Tools DC 15, or 10 + floor) holding
  the luggage roll instead of a suitcase would make Rogues happier and add a lock to every
  search. It also adds a step to every room; I'd leave it out.
- **Wanderers.** They carry their key; their luggage is in their room, which the key now
  opens. Killing a wanderer is a free door.

## 6. What changes where

- `hotel.md`: sections 11 (the Class and the Book) and 12 (luggage and magic items) from
  the drafts above; section 2's gift shop line points at 12; event 10 becomes the standing
  lost and found; section 3.6's luggage line points at 12.
- `CLAUDE.md`: *Roll to cast* reworded from "Morten the wizard" to "the Book" (the double
  wizard's slot line and Arcane Recovery choice added); *The wizard* becomes *The guest*
  with the class choice; *New game defaults* adds the class (section 7); the folder layout
  gains `loot.py` and the templates.
- `tools/loot.py`: `--floor N [--sure] [--band-up]` rolls the d20 on the floor's row and
  prints the item's name, rarity, the attunement line and its file path, expanding the
  *Varies* folder's tables; `--rarity Uncommon` picks one for the shop window or lost and
  found. Tests in `tools/test_loot.py` cover the *Varies* expansion and the row sums.
- `templates/`: one sheet per class that gets picked, written at campaign start from the
  SRD by the GM; `character-wizard3.md` stays as the double wizard's base.
- `agents/player.md`: "a level 3 human wizard" becomes "the character in `character.md`".
- `gen_dungeon.py`: unchanged. If the gestalt makes the Hotel soft, add `--level-offset`
  so floor N is built for level N+1 (section 7).

## 7. The human's choices

1. **Gestalt (section 2) or SRD multiclassing** for the class rule. I recommend gestalt.
2. **The double wizard's prepared list:** one list cast either way (my draft), or two
   lists (one for slots, one for the roll, 12 prepared at level 3). Two lists are closer
   to "two party members" and make the double wizard the strongest build by a margin.
3. **Does the Book get Arcane Recovery?** The draft says no, as asked ("only the spells").
   Giving it back makes the non-wizard a much safer caster.
4. **Generosity:** the d20 rows as drafted (about 60 items), or a d12 with the same
   proportions (about 90), or a d20 hitting on 15+ (about 35).
5. **Floor difficulty:** floors as generated, or one level up for a gestalt body.
6. **`hotel1`:** convert Morten to the double wizard where he stands (Day 2, room 101,
   1,425 XP), or start `hotel2` with a new class; and whether the luggage rules apply to
   `hotel1`'s unsearched rooms from now on (I'd say yes; searched rooms stay as they are).
7. **The default class for a new game:** the human picks, or a d12 (Barbarian Berserker,
   Bard Lore, Cleric Life, Druid Land, Fighter Champion, Monk Open Hand, Paladin Devotion,
   Ranger Hunter, Rogue Thief, Sorcerer Draconic, Warlock Fiend, Wizard Evoker: the SRD's
   one subclass each). Rolling fits the Hotel.

## 8. Build order

1. `hotel.md` sections 11 and 12 and the `CLAUDE.md` rewording, with the choices above
   filled in.
2. `tools/loot.py` and its tests.
3. The chosen class's level 3 sheet in `templates/`, and `agents/player.md`.
4. Convert or start the campaign; commit and push as always.
