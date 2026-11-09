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
