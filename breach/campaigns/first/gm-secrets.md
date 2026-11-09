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

## Current breach: month 1, the Bull

`gen_breach.py --seed 152302 --level 1 --reported 1` · near Hadley, 3 days · true level 1.
Principal kind Giant Hyena; the surface is dry grassland and thorn scrub where there was
pasture, warm wind, a smell of dust. 300 XP in the breach; 150 is level 2.

| Room | Denizens | CR | XP | Difficulty | Disposition | Size | Feature | Coins | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4× Flying Snake (stowaways, Monstrosity) | 1/8 | 100 | Low | Wild: Animal Handling DC 15 or fight | 12×12 m | 1.5 m entrance (chokepoint) | 10 GP | cleared: all 4 killed (fire at the gap), 100 XP; coins taken |
| 2 | 1× Giant Hyena | 1 | 200 | High | Wild: Animal Handling DC 15 or fight | 9×18 m | the rift, 3 m tear at the far end | 20 GP | killed at the thorn gap, 200 XP; coins taken. **Breach closed** day 4. |

Notes: Flying Snakes are Monstrosities, so *Animal Friendship* won't take them. The hyena is
a Beast (WIS +1). Thing left behind on closing: a hyena's tooth threaded on grass cord, or
a brass bell from whatever the snakes stowed away in.

## Month-end foreknowledge

`month.py end` is seeded by campaign seed and month, so its result is fixed in advance (checked
on a scratch copy, month 1). Month 1's end: the Hare (Rowena Lowry) dies in the Giant Shark
breach by Kingsmere, the Bear (Aelar Vance) in the Wyvern breach by Hollins; both automatons
come home. The Raven graduates. Loose next month: Air Elementals near Kingsmere (level 15),
Wraiths near Goose Green (11), Fire Giants near Barrowden (10), Polar Bears near Barrowden (3),
Dretches near Barrowden (1). The Bull's month 2 breach: Giant Goat near Goose Green, level 2.
Play nothing in downtime that contradicts this (the Hare and the Bear are out on their breaches
until month's end; the Hound lives).
