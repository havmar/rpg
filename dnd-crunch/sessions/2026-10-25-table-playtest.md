# Session notes: 25 October 2026, the table's playtest

The last build session of the table (`web/`, [../table-plan.md](../table-plan.md) section 8,
session 6): two months of a fresh Realms v2 campaign played through the page, as the player
would on a phone, with the GM's side run exactly as `web/README.md`'s GM's turn says. Then
everything the playtest found was fixed.

## What was played

A scratch campaign, `realms-t` (seed 99, rolled with `roll.py 1d100`), started by New game
defaults: `realms.py new --seed 99 --level 3`, the template rules, a fresh Morten. The page
ran on the dev server (`serve.mjs`) and was played in Chromium at 412 px; every GM batch went
in with `db.mjs apply` and was recorded with `table.py sent`; moves were read back with
`db.mjs moves --out` and `table.py moves`. Every die came from `roll.py --keep`.

- **Month 1, floor 1 under the tower (A2).** The orders were sent from the orders form
  (stay home, Delve, the tower saves). Room 1.1's three Flying Snakes (CR 1/8 each) were
  streamed live, a beat a round. Mid-fight the player typed a steer ("Fire Bolt the snakes,
  save Scorching Ray") and tapped **Stop after this fight**: the GM took it at the next
  round; Fire Bolt fizzled, Sleep's concentration broke, and Morten died to the poison
  (every bite that landed rolled 20 or more, past even Shield). He woke in the tower, broke.
  The player asked out of game from Talk why Shield didn't help and whether he should have
  left his coins home; the answer came back as an aside (and a new purse habit). Then the
  **Fights dial went to one line** on the Table tab, and the rest of the month was told
  after: the last snake (a natural 20), 2 Warrior Infantry (6 HP left), a short rest, a
  Panther in one Thunderwave. The world's turn: the Elves marched Knights and Mercenaries
  into the tower's own hex.
- **Month 2, under "fights: one line".** A Rob on the Elves' Mercenaries in A2 (2 Toughs,
  CR 1/2 each, won on 5 HP with Sleep and a point-blank Scorching Ray). The world's turn
  was streamed live as three beats: the Rob paid 200 GP, then the Elves' Knights broke the
  tower's regime to 0 and sacked it for 173 GP. Month 3's orders went in from the map's
  new **Travel here** (a Contact in the Elves' A1).

Screenshots were taken at each step and looked at as the player would; they are not kept in the repo.

## What worked

- The live card feels live: a round lands as a paragraph with its dice as chips, the HP
  bars move, "down" shows for a dead snake, and the activity line says what the GM is doing
  and how long ago the last line came. The world's turn streamed the same way reads well.
- The fight card's HP chart, the folded rounds and the result strip; the world's turn
  section with its numbered events, the tower's arrows and the Next month chips.
- The steer and Stop reached the GM at the next stop point, as the plan says; the dial
  change went through as a `table` move, showed "pending" and landed.
- Talk: the question, the GM's aside under it, gathered with the rest of the table talk.
- The GM's side held up for two months: no version conflict, no lost move, `check_table`
  clean.

## What the playtest found, and what was fixed

The page (`web/src/`):

- After **Send the orders** the box still said "Your move" and offered the whole form again.
  Now the box says the move is with the GM ("The GM's move"), folds the form behind
  **Change the orders** (or **Change your call**…), and the now line says "the GM has your
  orders"; kept per viewer across a reload. **Stop after this fight** shows as asked.
- The HUD lagged the live card (20/20 HP on the HUD, 5/20 in the round): a beat whose
  `--hp` moves Morten's HP now rewrites `game/morten` and `game/state` in its batch.
- The tower card quoted the engine ("Strike a6 (Knights, T3)", "(L1, taiga, tower)",
  "d6 … (1 = encounter)", bare prices): `game/realm.nextWords` says it in words; "+0 GP a
  month" now says why (the Elves' soldiers hold A2).
- A pending orders bubble showed the engine's action string (`buy:farms@A2`); it names the
  form's label now. The answered words read "stop: …" and dropped the orders: they are
  plain sentences now ("Orders: to … · Rob the Elves' Mercenaries … · the tower saves. …").
- A death section's strip read "HP 20/20 HP · on him none"; a fight line bolded "down" in
  "fly down"; Talk's hint stayed on "the GM has been called" after the answer; the now line
  grew to five rows with a long prompt (one line now on a phone).
- The Rules tab showed the GM's file names and commands (`state.md`, `game/state.table`,
  `python3 … realms.py new …`): `game/rules` is unwrapped and cleaned for the player.
- Known gaps closed: a fight told after gets its HP chart (from the trace's HP lines, else
  start and end); `game/realm.dissidents` on the tower card; **Travel here** in the hex
  entry; a Rules filter box; the shell's own Story dot is gone (More's wins anyway).
- The flaky checks read the page before the next frame re-rendered it: "before a fight… :
  a plan needs words" (about 1 run in 6) now waits for the render; "the Table tab switches
  the theme" (seen once in eight runs) was the Table tab showing the new look only a frame
  later, so its buttons now press at once.

The GM's side (`tools/`):

- A new game had no `morten.json`: `table.py new --sheet fresh` writes the New game
  defaults' Morten (`tools/morten-wizard3.json`).
- `roll.py --keep DIR --label fizzle` labels a kept roll once its result is known (a
  fizzle is known only after the roll).
- `morten --condition -Unconscious` was refused by argparse; condition and habit changes
  now print; `section --answers none`; `realm` no longer rewrites an unchanged `game/realm`;
  a trace line with no /N that swallows the dice is named in the error; hexes of a people
  named in the singular read "Goblinkind's savanna", not "the Goblinkind's".
- `check_table` read the hard-wrapped rules, so an example monster in CLAUDE.md ("3
  Venomous Snakes") looked secret once the page's rules were unwrapped; it unwraps them too.

New checks: `web/e2e-loop.mjs` plays the GM's loop with the real `table.py` (seed, orders
from the page, moves read, a beat, a section, the box back to orders) in about 10 s;
`e2e/` gained Travel here, the Rules filter and the box after a send; `test_table.py` a
Playtest class.

## What's still rough

- The GM's bookkeeping is heavy: a five-round fight is twenty-odd tool calls, and labelling
  rolls after the fact is still by hand (now one `--label` call, not an edited file).
- Under "fights: one line" the page shows whatever the GM wrote; the dial only tells the
  GM to write less. A fight section could fold its story by the dial.
- The HUD on a phone is three rows (the light's words are long); the rules are still the
  GM's text, cleaned, not written for the player.
- `table.py` gives no warning when the GM writes a section that contradicts the sheet
  (the playtest's short rest said 12 HP, the dice said 14: fixed by a correction line).
- The death rules in CLAUDE.md still say "revives at the dungeon's entrance camp" while the
  Realms rules send him to the tower; the page shows both.
