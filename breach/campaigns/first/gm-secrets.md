# GM secrets: the 11th Company

Not for the human. Don't paste into chat.

## Why the breaches open

The breaches are drawn by absorbed breach-magic. Every dungeoneer who has taken a kill is a
lodestone; a breach opens tuned to the nearest one, which is why the world "offers a fair
fight". The Order was not founded to answer the breaches; the breaches answer the Order.
Counties with a Company have more breaches, not fewer, and the Crown knows it.

The Crown pays for it because of what happens at the Capital. A Lord Marshal who graduates
carries twenty levels of absorbed magic. At the Capital the college renders them into a
**ward stone**: the body is laid into the stone and the stone is set in a new settlement or
under a failing one. That is where veterans go and why they do not write. Wards are made of
dungeoneers; the ladder is a crop. Kill-heavy dungeoneers make strong stones; the college
prefers them, which is why the ladder rewards the kill and the doctrine the deportation.

Automaton cores are chips of spent ward stones: the remains of older graduates. That is the
design the college does not share, why a core can't absorb anything (it is full), and why some
automatons, rarely, remember things from before their first partner.

Clues, to lay as play goes:
- Barrowden's ward stone sits in an empty tower; the tower's door is carved with the Order's
  gate and twenty animals. The stone is warm.
- Breaches cluster around wherever the Company's high ranks are posted that month.
- Teg Harrow deserted at rank 6 and there have been noticeably fewer breaches near the
  stables since. (Not true; it's that Teg stopped killing. Their pull faded.)
- The Crown's liaison receives a letter each month naming the top three roles by kills.
- Lampwick, asked the right question, will recall a garden that it has never seen.

## Current breach: month 2, the Bull

`gen_breach.py --seed 255881 --level 2 --reported 2` · near Goose Green, 3 days · true level 2.
Principal kind Giant Goat; the surface is high upland pasture and scree where there was
lowland, thin cold air, bells somewhere. 600 XP in the breach; 450 is level 3 (needs 150 more).

| Room | Denizens | CR | XP | Difficulty | Disposition | Size | Feature | Coins | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4× Grimlock (stowaways) | 1/4 | 200 | Low | Hostile: fights | 15×15 m | a 3 m ledge along one wall (elevation) | 20 GP | cleared: all 4 killed on the scree, 200 XP; coins taken |
| 2 | 4× Giant Goat | 1/2 | 400 | High | Wild: Animal Handling DC 15 or fight | 9×12 m | the rift, 3 m tear at the far end | 40 GP | deported: all 4 herded through the rift. **Breach closed** day 4. |

Notes: Grimlocks are blind (blindsight), so darkness and stealth by sight don't fool them;
noise does. Giant goats are Beasts (Animal Friendship works, one per slot). Thing left behind
on closing: a goat bell, cracked, or a grimlock's bone flute.

## Month 1 breach (closed)

Giant Hyena by Hadley, seed 152302, level 1: 4 flying snakes and a giant hyena, all killed,
closed day 4. Thing left: a hyena's tooth on plaited grass cord. (Secret: the cord was plaited
by Lampwick's core-memory, not by anyone in the breach: Lampwick did it in the night without
knowing, as the previous owner of its core's stone used to. It doesn't know this.)

## Month-end foreknowledge (month 1, now resolved)

`month.py end` is seeded by campaign seed and month, so its result is fixed in advance (checked
on a scratch copy, month 1). Month 1's end: the Hare (Rowena Lowry) dies in the Giant Shark
breach by Kingsmere, the Bear (Aelar Vance) in the Wyvern breach by Hollins; both automatons
come home. The Raven graduates. Loose next month: Air Elementals near Kingsmere (level 15),
Wraiths near Goose Green (11), Fire Giants near Barrowden (10), Polar Bears near Barrowden (3),
Dretches near Barrowden (1). The Bull's month 2 breach: Giant Goat near Goose Green, level 2.
Play nothing in downtime that contradicts this (the Hare and the Bear are out on their breaches
until month's end; the Hound lives).

## Month-end foreknowledge (month 2)

Checked on a scratch copy: at month 2's end **the Heron, Carlin Lowry, dies in the Killer Whale
breach near Goose Green**; Tamsin comes home; the new Heron is Loopmottin Quayle (she/her,
Gnome Fighter) with Tamsin. The Boar (Rieta Rooke) graduates; new Boar Shanairra of the Fen
(they/them, Elf Wizard). Loose next: Chimeras (15) near Hollins, Adult Brass Dragons (14) near
Hadley, Unicorns (11) near Fenwick, Ogres (3) near Barrowden, Goblin Warriors (1) near Goose
Green. Settled: the Giant Sharks near Kingsmere and the Wraiths near Goose Green (GM says
what became of them). The Bull's month 3 breach: Imp, level 3, near Fenwick, 2 days.

If the Bull closes the unassigned **Goblin Warrior** breach near Goose Green (level 1, seed
101120, `gen_breach.py --seed 101120 --level 1`) before month's end, strike the goblins from
`loose` in campaign.json by hand after `month.py end`, and give the XP.

Don't let the Heron's death be prevented by anything but the human's own choices; if the
human goes with the Heron, the GM plays it and settles the roster by hand.

## Side breach: month 2, Copse Wood (unassigned; the Bull went of its own accord)

`gen_breach.py --seed 101120 --level 1` · Copse Wood, 3 km north of Goose Green · true level 1.
Principal kind Goblin Warrior; the surface is a wood that wasn't there, flowers out of season,
moonlight at noon. 400 XP in the breach. Caelynn at 500 XP gains no level from it (1,350 next).

| Room | Denizens | CR | XP | Difficulty | Disposition | Size | Feature | Coins | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1× Giant Octopus (stowaway) | 1 | 200 | Moderate | Wild: Animal Handling DC 15 or fight | 15×18 m | flooded: water 3 m deep, a 1.5 m ledge round the edge | 20 GP (on the cistern floor) | scouted day 5 (Stealth 12 vs PP 14, then Hide 19). Charmed (Animal Friendship, save nat 1), calmed (Animal Handling 24 adv), led through the rift (Animal Handling 15 adv vs DC 15). Deported. Coins fetched by Lampwick off the bottom. |
| 2 | 4× Goblin Warrior | 1/4 | 200 | High | Wary: Persuasion/Intimidation DC 15 to go; refused, bargains or fights | 15×18 m | the rift, 3 m tear at the far end | 20 GP | talked home by Lampwick (Persuasion 16 vs DC 15); all 4 deported, coins left for the pair. **Breach closed** day 5, early afternoon. Left behind: a pressed primrose. |

Notes: the octopus is a Beast (Animal Friendship works; WIS +0). On land it has Speed 3 m, so
Longbow Slow stops it dead; it holds its breath an hour. It is under 3 m of water: arrows into
the water from above at disadvantage (GM ruling, by analogy with underwater combat). Ink Cloud
1/day when damaged underwater. The goblins are Fey, speak Common, and are frightened, not
cruel: they will bargain to be shown home (they want the octopus gone first; it ate one of
them). Thing left on closing: a goblin's brass thimble, or a pressed out-of-season flower.

After `month.py end` for month 2: strike the Goblin Warriors near Goose Green from `loose` in campaign.json by hand (closed by the Bull). No XP (all deported).
