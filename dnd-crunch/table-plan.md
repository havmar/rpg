# The table: D&D Crunch played from a page (a plan)

**Status: built** (`web/`; how it is built, its exact data contract and the GM's turn are
in [web/README.md](web/README.md), which wins over this plan where they differ). Where the
build departs from the plan:

- **Plain JS, not Angular.** Dream's bridge, harness and lessons were ported by reading
  Dream's code (`store.ts`, `publish.py`, the dev store, the e2e), not by copying its
  Angular app: the page is source files joined by `web/build.py` into one committed
  `web/dist/table.html`, with no npm and no install. Section 8's file list is therefore
  `web/src/js/NN-*.js` and `web/src/css/NN-*.css` per panel, not `panels/*.ts`.
- **One wake thread per move**, resolved by the page at once (Dream's way), rather than a
  standing thread.
- **The player's words sit above** the section that answers them (question, then answer,
  as Dream shows them), not under it.
- **Two fixtures**: `web/dev/fixture/` (a month played, awaiting orders) and
  `web/dev/fixture-live/` (a fight open), both projected by `table.py` from a replay of
  `realms3`'s month 2 (`web/dev/fixture-campaign/`).
- **More verbs**: `table.py open` (a section opens so beats can stream into it), `resend`,
  `render`, `export`, and `sent --drop` / `--landed` / `--from` for a send that went wrong.
- **The theme switch** belongs to the shell; the Table tab calls it.

This is the design for the page that replaces chat as the
way a Realms campaign is played: the whole game on one claude.ai artifact, read and played
from a phone, with the GM's play streamed onto it as it happens and the GM reachable from
it. It takes Dream's page (`havmar/dream`, `web/` and `publish.py`) as the proven transport
and rebuilds the content for this game. The look is sketched in
[ui/table-mockup.html](ui/table-mockup.html), a clickable phone-first mockup filled with
the `realms3` campaign's second month; its published copy is linked at the end (section
11). When the build departs from this plan, the build wins and a note here says where.

## 1. The brief

What the human asked for, in their words and what each means for the design:

- **A standalone game interface.** "Claude Code chat not needed to play." Everything the
  chat does today (the orders, the fight log, the report, the sheet, out-of-game talk)
  has a place on the page, and the page can reach the GM on its own (section 7).
- **Game modes.** Three, as given:
  1. *Autoplay:* the GM is the DM and moves Morten too, plays the fights and reports them
     as they go.
  2. *Autoplay, fights folded:* the same, but a fight is a brief summary and the attention
     is on the factions' moves.
  3. *More player input:* per round, per fight, or per month, with the reporting detail of
     either of the above.

  These are not three modes but **three dials** (section 5): *who moves Morten*, *when the
  game stops for the player's word* (never in a month, at each month's orders, before each
  fight, each round) and *how much is told* (fights live, folded or one line; the faction
  turn as story or as the full report). Any setting of each works with any of the others.
- **Streamed, not turn-based.** "The structure is not clear-cut player message, DM
  message, more like the DM actions getting streamed as they happen. The more often the UI
  updates, the better. At the same time, reading only after the DM actions are finished
  should also be comfortable." So the page shows two renderings of the same play: a **live
  card** that grows a line at a time while the GM plays, and a **settled section** that
  replaces it when the GM has written the piece up, with the story first and the trace
  folded under it (section 4.2).
- **Everything the GM says in chat goes to the page too.** An out-of-game or developer
  question is answered in chat and the answer is sent to the page as well, so an aside the
  GM has while playing, which today would go only into chat, is on the page (section 4.2,
  asides).
- **Structure the narration:** per-fight sections, the monthly faction turn visually set
  apart. **Both the printed trace and the GM-written story are needed.**
- **Evaluate every element** of the old page and the planned one for whether it is
  presented in a friendly, pleasant way; hex codes aren't useful, the green lines aren't
  known to be HP, the realm breakdown is padded, "assets" means nothing to a new player;
  display efficiently and nicely, with icons where they help (section 3).

## 2. What exists

### 2.1 This game today

Play is in chat, by `CLAUDE.md`: the GM rolls with `tools/roll.py`, writes replies in the
**Report style** dials (fights summary · domain summary · events summary · dice: key
rolls · live updates every round) and keeps `state.md` (rewritten), `transcript.md`
(appended), `character.md` and the engine's `realms.json`. The one page is **Morten's War
Table** (`ui/realms-map.html`, built by `tools/realms_page.py` from `map.json`, published
as an artifact and republished after each domain turn): three views, Map, Realms, Month,
from one static JSON inlined into the file. It is read-only, knows no rules (every string
comes worded in the data), and is a good map; it holds nothing of Morten, the fights, the
days or the dice, and nothing moves on it until the GM republishes.

What the chat does that the page cannot yet: the fight log in rounds with every die; the
**State** block (HP, AC, lost spells, concentration, reaction, light, coins); the orders
and the **Rumours**; the domain report in Claude's words (the plan, what happened, the
tower now, next month); the trader and downtime; death and the altar; the out-of-game
talk and the rulings.

### 2.2 Dream's page: what carries over, copied

Dream (`havmar/dream`) plays its game through an Angular page on a claude.ai artifact with
the `db` capability (the store) and `comments` (the wake). The parts that are the
transport, not the game, carry over by copying them into this folder (the repo's rule:
copy and adapt, never point at another game's files):

| From Dream | What it is | Here |
|---|---|---|
| `web/app/src/app/store.ts` | the db bridge: subscribe once, one write at a time, the seq handshake, the wake through `comments.sendToClaude` | `dnd-crunch/web/app/src/app/store.ts`, the same code with this game's paths |
| `web/app/src/app/model.ts` (its pattern) | defensive parsers: read every field with a fallback, never cast | rewritten for this game's documents (section 6) |
| `publish.py` (the record, the pinned batch, `--sent`, `--log`, `--wake`) | how the GM writes the store without a server: a JSON file per document, one `ArtifactData` batch, every `game/` write pinned by the version kept in `page.json` | `tools/table.py` (section 7) |
| `web/dev/serve.mjs`, `web/dev/fake-db.js`, `web/dev/db.mjs` | a local table: the built page over a fake store, live over server-sent events, with the comments shim | `dnd-crunch/web/dev/` |
| `web/e2e.mjs`, `web/build-artifact.mjs`, `tests/test_web_dist.py` | the smoke test on a phone, the page assembled from `page.html` and the bundles, the committed build's stamp | `dnd-crunch/web/e2e.mjs`, `build-artifact.mjs`, `tools/check_web_dist.py` |
| the look's tokens, light and dark on `:root` | one token set, both themes | kept, but this page keeps its own war-table palette (section 4.7) |
| the keeper's turn and the wake (`web/README.md`) | read moves, play, publish, send, `--sent`, commit; the page wakes the keeper with a comment; two arrivals of each wake | section 7, with this game's loop |

What does not carry over: Dream's panels (a party of four, a hexroll realm, dungeons by
area), its chronicle-per-turn shape (this page streams within a turn), and its rule that
the DM's text never goes into the session (here the opposite: chat and page say the same).

### 2.3 What the platform gives the page

The capabilities the page declares (`artifact-capabilities`, contract 0.2.90):

- **`db`**: a document store per artifact, live through `onSnapshot`, written by the GM
  session with the `ArtifactData` tool and by the page for its moves. One document at most
  256 KiB; 25,000 documents an artifact; 64 subscriptions a view. Owner and editors write;
  the player is the owner.
- **`comments`**: `sendToClaude` from the page posts a comment and wakes the Claude
  session watching the artifact. That is the standalone loop: a move lands, the page
  wakes the GM, the GM plays and writes, the page shows it. Proven in Dream.
- Not used: `room` (its events are not stored, and the publishing session reaches it only
  where a flag admits it, so an agent "narrates through db" anyway), `sample` (the page
  asking Claude on its own would be a second GM with none of the files), `artifact`
  (republishing the page as state: the store is the state).

## 3. The evaluation, element by element

Each row: what the element shows today, what is wrong with it for a reader who does not
know the rules, and what the new page does instead. The old page's three screens were
read at phone width (412 px) and on a desktop.

### 3.1 The header and the tower strip (Map, Realms and Month alike)

| Element | Today | Problem | The table |
|---|---|---|---|
| Eyebrow "The six realms · realms3", title "Month 3", sub "The map after month 2's domain turn · 8 moves the tower saw" | three lines of heading on every view | a sentence to say what the page is; "moves the tower saw" is an aside about visibility | one **now line** on every tab, sticky: the month, the day and the clock, where Morten is in words ("Floor 2, room 2.4 · under A5 · Day 4 · 09:40"), and what the GM is doing ("rolling the Darkmantle's crush") |
| "Tower ▬▬▬ 7/7" | a chip with an unlabelled green bar | nothing says the bar is the regime's HP, or what HP of a tower means | the tower card on the Realm tab says **Regime 7/7 ♥** with a heart glyph and, on first visit, one line: "the tower's health as a power; at 0 it is sacked" |
| "F 1 C 1 W 1 · 89 GP · +60/mo" | abbreviations and numbers | F, C, W mean nothing unsaid | three glyphs with names on first read: ⚔ Force 1 · ◎ Cunning 1 · ¤ Wealth 1 (drawn as SVG, not emoji), then **89 GP, +60 a month** in words |
| "Morten B5 · L3" | a brass chip | "L3" is his level, but reads like a hex | Morten lives on the now line and the Morten tab: "Morten · wizard 3 · 20/20 HP"; his hex shows on the map as a pin, named in words ("at home, B5") |
| "Allies Goblinkind Humans" / "X hostile · 3 mo" | chips | fine, but far from the realms they name | kept, on the tower card, each name a link to the realm's row |

### 3.2 The map

| Element | Today | Problem | The table |
|---|---|---|---|
| Hex id "A1" at the top of each hex | a small mono label | the human's own verdict: "the hex codes aren't useful"; they are the engine's addresses, not what a player thinks in | **demoted**: tiny, in the hex's corner, shown only when "Codes" is switched on in the map's bar; the entry's title names a hex by whose it is, its land and its level ("The Tieflings' savanna, level 18"), with the code after in grey. The codes stay in the data and in the orders form, where the engine needs them |
| The big level number | the hex's ley, 1–20 | the most prominent thing on the map, unexplained: it is the floor under the hex, the wandering monsters' level and the income | kept as the big number, because it is what matters, and explained once: the entry says "Level 18: floor 18 lies under it, its wanderers are level-18 trouble, and it pays 180 GP a month"; a first-visit note on the map says the same in one line |
| Biome as an italic word | "mountains", "swamp" | a word per hex adds clutter; the biome is flavour | a small land glyph (peaks, pine, reeds, dune) under the number, the word in the entry |
| Seat as a flag | a small pennant in the hex's corner | a flag reads as "a place", not "the ruler sits here" | a **crown** glyph, and the ruler's name in the entry ("the seat of Exarch Iados") |
| Asset chips "F•", "W••" with a 2 px HP strip | letter, tier dots, a strip | letter and dots are a code; the strip is invisible; "asset" is a word from the book | **pieces** as tokens: a round token in the owner's colour with a glyph for its kind (⚔ soldiers, ◎ spies, ¤ income), tier as 1–3 pips, and an HP ring around the token; a hostile owner's token has a red ring and a skull. The word on the page is **piece** ("a piece is something a realm has put on the map: soldiers, spies or income"), and each piece's entry says what it is in words ("Knights: mounted soldiers, tier 3, 12/12 HP, upkeep 100 a month") |
| Dashed red edge for a hostile owner | on the chip | too small to notice | the hostile ring and skull on the token, and the realm's row says "hostile to the tower, 2 months left" |
| Morten's hex: a brass dashed ring and an "M" pin | | fine | a brass pin with a wizard glyph; the ring stays |
| Last month's moves: numbered arrows and badges, a toggle | | the numbers refer to the Month tab's list, two taps away; in-place badges stack | kept, numbered as the **world's turn** section's events (section 4.2), and tapping a badge opens that event's sentence under the map |
| Realm borders, rivers, lakes | | good | kept; a river's +1 is said in the entry ("a river edge against B3: defenders +1 from there") |
| The Key, a collapsed details | eight icons explained | a key nobody opens | a **first-visit note** per tab (dismissed once, kept in the browser) and a "?" in the map's bar that overlays the key on the map itself |
| Tap target: the whole hex | | good (44 px and more) | kept |
| Distance | none | the player cannot tell how far a hex is without counting | the entry says **days from Morten** and the way ("3 days: B5 → B4 → C4 → D3"), counted on the page from the neighbours |

### 3.3 The hex entry

| Element | Today | Problem | The table |
|---|---|---|---|
| "B5 · Level 1 desert" and chips (Held by, People, Seat, income, lake, river, "Morten is here") | a chip row | fine, but the chips repeat the map and the income is the one number that matters | title in words, then one line: "Held by the Tieflings, their own people · 180 GP a month to them · 2 days from Morten" |
| Assets: a card per asset with a bar, Attack, Counter, Special | | "Attack W vs F, 2d4+2" is the book's notation; the HP bar unlabelled | a **piece row**: token · name and what it is · HP 1/6 ♥ with a small bar · one line in words: "hits with Wealth against Force for 2d4+2; hits back for 1d6; upkeep 100" · what Morten can do to it: "Strike (a Moderate fight) · Rob (up to 200 GP)" |
| Last month here | event cards | duplicates the Month list | the events that touched the hex as sentences, numbered as on the map |
| Next to: hex buttons | | fine | kept, each named in words with its code small |

### 3.4 The Realms view

| Element | Today | Problem | The table |
|---|---|---|---|
| Standings: swatch, name, "bad: robs its neighbours · ally", an HP bar, "F4 C4 W4" | a list | the bar is unlabelled; F C W again | a **realm row**: swatch, name, the leader as *label: verb*, state (ally · hostile 2 mo · in disorder), **Regime 19/22 ♥** as a bar with its number, and the three glyphs with their numbers. Tap to unfold |
| Realm cards: leader line, label pill, goal box, HP bar, five attribute boxes, state chips, seat and hex buttons, asset rows | one tall card per realm, seven of them (about 500 px each on a phone) | "the realm breakdown is very padded": the same facts five times (standings, pill, chips, attributes, rows); treasury and income boxed like attributes | the **unfolded row** is compact: the goal as one sentence ("going to build Walls at its seat, month 3 of it"), treasury and income in one line ("1,200 GP, +310 a month"), the hexes as a row of small hex buttons with the seat crowned, the pieces as piece rows (section 3.3). Nothing is repeated |
| The tower first, as a card like the others | | the tower is the player's, not one realm of seven | the **tower card** stands above the map on the Realm tab: regime HP, the three glyphs, gold and income, its pieces, its hexes, allies and hostiles, and the dissidents found |
| Allies and hostiles as chips on each card | | fine | a state word on the row |

### 3.5 The Month view

| Element | Today | Problem | The table |
|---|---|---|---|
| The report's four parts (The plan, What happened, The tower now, Next month) with Threat/Chance/Open marks | the script's lines as bullets | this is the script's wording ("Tieflings (Exarch Iados, bad: squeezes its own people): Buy Treasury a26 in D5 (it has the gold), −1,200 GP → 300 GP."), not the story the GM writes in chat; the human found domain turns hard to follow from exactly this | the **world's turn** section in the Story (section 4.2): the plan in one or two sentences, what happened as the GM's story (each event a sentence: who, *label: verb*, what, why, how it came out, and what it means for the tower), the Elsewhere line, the tower now as what changed, Next month as threat, chance and open chips; the script's lines are the **trace**, folded under "the script's log", as the human asked: both are needed |
| Every move, in order: numbered event cards | a list after the report | the same events a second time, as cards with an action tag and a hex button | gone as a list; the events are the numbered sentences, and the map's badges point at them |
| "Month 3" as the title while the report is month 2's | | confusing: the page is "Month 3" and the report "Month 2's" | the Story's month groups are the months played; the now line says the month in play |

### 3.6 What the chat shows and the page must take over

| In chat today | Problem on a phone | The table |
|---|---|---|
| The fight log: a heading per round, one line per event with the dice, a State block, "Morten's turn: move 6 sq · action · …" | long, scrolls past; nothing is at a glance | a **fight card** (section 4.5): the foes with CR, AC and HP at the top, HP bars for Morten and each foe that move as the beats land, the rounds as lines with the dice as chips, the GM's summary first once the fight settles, the rounds folded under it |
| The State block in every reply | the same five lines every time | the **now line** and the **Morten tab**: HP, AC, light, concentration, lost spells, coins on him, always visible, never repeated in the story |
| "Morten (GM):" lines with his reasoning | | kept, as the story's own voice inside the section ("Morten holds the doorway so one dog reaches him at a time") |
| The orders as text; "Open:" lines listing every option with its price | the player types what the engine must parse | the **orders form** (section 4.2): travel by tapping a hex, the mission from what is in that hex, the tower's action from what it can afford, Give, a plan note; free text stays beside it |
| Rumours when next to a realm | | on the hex entry and the realm row, as heard |
| Trader, shopping, downtime | | a shop section in the story with the coins left; the trader's list on the Morten tab when he is home |
| Rulings and GM asides ("ruling: the Strength loss lasts until a Long Rest") | lost in chat | **asides** in the story, set apart, and gathered under Table talk |
| Death and the respawn | | a death section with a skull, the coins lost, the walk home; Deaths on the Morten tab |
| "Say go on and I play him" | | the **play controls** (section 4.2): Play a month · until something matters · this fight · one round · Stop |

### 3.7 Across the page

- **Numbers carry their unit.** "20/20 HP", "AC 15", "6 sq (9 m)", "180 GP a month": the
  chat rule holds on the page, and the mono face keeps them aligned.
- **Icons are a drawn set**, not emoji, so they render alike on every phone: heart (HP),
  shield (AC), sword (Force, soldiers), mask (Cunning, spies), coins (Wealth, income),
  crown (a seat), tower, skull (hostile, a death), d20 (a roll), spark (a spell), pin
  (Morten), boots (travel), door (a room), bed (a rest), lantern (light), bag (gear),
  globe (the world's turn), speech (an aside), gear (settings), flag (the goal).
- **Colour means one thing each**: a realm's pigment is its own everywhere (the map, its
  row, its pieces, its sentences' who); brass is Morten and the tower; green, amber and
  red are good, warn and bad, used only for states (HP bands, won/lost, ally/hostile).
- **One thing is said once.** Where the old page repeated a fact in a chip, a box and a
  row, the new one has one place for it and links to it.
- **Every tap target is 44 px** or more, every tab works at 412 px with no sideways
  scroll, and the page is designed at that width first.

## 4. The design

### 4.1 The shape

One page, one campaign. On a phone, one view at a time and a **bottom bar** of five:
**Story · Morten · Realm · Fights · More** (More opens Months, Rules, Talk, Table, and
the light/dark switch as chips). Above every view the **now line**. On a screen wider
than 900 px, two zones: the Story on the left with its answer box, and a drawer on the
right with tabs Morten · Realm · Fights · Months · Rules · Talk · Table, the Realm tab
first because the map wants the width.

### 4.2 The Story

The story is a stream of **sections**, oldest at the top, grouped under **month
headers** and, inside a month, **day rows**. A section is one thing that happened, written
once when it is done: the month's orders, a day's travel, a fight, a rest, a shop, a
delve's floor opened or left, the world's turn, a death, a wrap-up, or an aside. Each
section is the GM's story first (its headline and a few sentences or labelled bullets, in
the chat's voice) and its **trace** under a fold: the lines as they were played, each with
its dice as chips. The report dials (section 5) decide how much story a section gets; the
trace is always whole.

- **The month header** is a thick rule with the month, its orders in one line ("Delve
  floor 2 under A5 · tower saves · no gifts") and, once the month is over, its sum ("+700
  XP, +70 GP, no deaths, floor 2 cleared"). Months before the newest fold to their header;
  "Older months" opens them.
- **A day row** is a thin rule: "Day 3 · floor 2 under the Humans' A5" with a boots or
  door glyph; sections hang under it.
- **A fight section** is a card (section 4.5).
- **The world's turn** is the month's last section and is set apart: a globe glyph, a
  tinted background that no other section has, and its four parts in order. The plan.
  What happened, as numbered sentences; each sentence's who is in the realm's colour and
  its number matches the badge on the map; "Elsewhere" closes it. The tower now, as what
  changed (gold, pieces, hexes, allies, hostile), each with an arrow from before. Next
  month, as chips: red for a threat, green for a chance, brass for an open choice, each
  chip one sentence. Under the fold: the script's income lines and its log, verbatim.
- **An aside** is the GM's out-of-game voice: a speech glyph, a dashed left rule, the
  text as written. Every message the GM writes in the session goes to the page as one,
  and every out-of-game answer to the player goes to both (section 7). Asides sit in the
  stream where they were said and are gathered under More → Talk.
- **The live card** is the section being played: it sits at the bottom of the stream, in
  its day, with a pulsing mark and "in progress", and grows a line at a time as the GM's
  beats land (section 6). For a fight it shows the foes and the HP bars moving; for a
  road, the days and the wandering checks; for the world's turn, the events as they are
  rolled. When the section's document lands the live card becomes the settled section in
  the same place, so the page never jumps. Under it, the **activity line** says what the
  GM is doing now ("rolling round 3", "writing the fight up"), from the GM's log lines,
  and the time since the last beat.
- **The player's words** show in the stream as their own bubbles, each under the section
  that answered it, as in Dream.
- **The answer box** is at the bottom of the Story and knows what the GM is waiting for
  (`game/state.awaiting`): it shows the matching control and, always, a text box.
  - *Waiting for the month's orders:* the **orders form**. Travel: the hex to end the
    month in, picked on a small map or from a list that says the days. Mission: what is
    possible there (Delve floor N; Strike or Rob each piece in the hex, with the fight's
    difficulty; Contact, with its DC; none). The tower's action: the affordable ones with
    their prices (buy a piece in a hex, raise an attribute, repair, move, attack, seize;
    none). Give: a realm and a sum. A line of why. Send sends it as one `orders` move.
  - *Waiting before a fight:* the foes as the card shows them, and chips: **Fight it**,
    **Avoid it**, **Plan…** (the text box, for "Web the doorway first").
  - *Waiting for Morten's turn (round mode):* the board as the log format gives it, and
    chips to drop a spell or an attack from the sheet into the text ("Fire Bolt at Goblin
    A"), then Send as a `turn` move. Illegal moves come back as an aside with why.
  - *While the GM plays:* **Stop after this fight**, **Take over Morten**, and the text
    box for a steer ("leave the sleeping boar, go round"). A steer lands as a move; the GM
    reads moves at every stop point and obeys it from there (section 5).
  - *Any time:* the text box, for Morten's words or a question to the GM, as one `say`
    move; and **Play** with its scope (a month · until something matters · this fight · a
    round) as a `play` move.

  The status line above the box says whose move it is, that the GM has been called (or
  why it could not be), and the time since the move was sent, with Dream's waiting bar.
- **Reading position** is kept as Dream keeps it: by section and offset, per viewer, so
  the page opens where the player left off and a new section lands without moving them;
  a **"live" button** at the bottom jumps to the live card and follows it.

### 4.3 Morten

The sheet, built for the phone from `game/morten`:

- **The HUD** (also the now line's second row on every tab): HP as a labelled bar with its
  numbers, AC (and "with Mage Armor 15" while it holds), the light he carries and when it
  runs out, concentration, conditions and exhaustion, reaction used or free in a fight,
  Heroic Inspiration and the free Mage Armor as glyphs lit or spent, coins on him.
- **Spells**: a grid of cantrips and prepared spells, each a chip with its name, level
  and DC; a lost spell is struck through with "back after a Long Rest"; concentration
  marked; tap for the spell's one line (range, effect) as the sheet has it. Arcane
  Recovery as a button-like chip the GM lights.
- **Fighting**: the attacks table (to hit, damage, range), saves, skills, speed and
  initiative, passive Perception.
- **Gear**: the inventory with kilograms and the load ("31 of 54 kg"), counts (oil, torches,
  rations, potions) as pips, coins on him and the purse in the tower, and the trader's
  list when he is home.
- **Progress**: XP as a bar to the next level with the number ("2,125 of 2,700"), level,
  deaths, the familiar.
- **Habits**: the standing orders from `state.md` (Shield at which hits, when to reroll,
  the purse drop), as the player set them, editable in words from the Table tab.

### 4.4 The Realm

- **The tower card** first (section 3.4), with a line of what the next month can bring
  from the engine's next-month lines, as chips.
- **The map**, full-bleed, redrawn as section 3.2 says: colour by holder, the big level,
  a land glyph, a crown for a seat, the tower, Morten's pin, pieces as tokens with HP
  rings, the world's-turn badges, rivers and lakes, borders. A bar over it: **Codes**
  (show the hex codes), **Moves** (last month's arrows), **?** (the key over the map).
  Tap a hex for its entry.
- **The hex entry** (section 3.3): the title in words, the one line, the pieces as rows
  with what Morten can do to each, last month here, rumours heard here, the floor under
  it as a strip of rooms (the explored rooms with their monster and whether cleared, the
  rest as "?"), the neighbours.
- **The realms** as rows that unfold (section 3.4), the allies first, then the hostile,
  then the rest; each with its goal, regime HP, the three attributes, gold and income,
  hexes and pieces.

### 4.5 Fights

A fight is a section in the Story and the same card on the **Fights** tab, which lists
every fight as a row (month and day, place, the foes with CR, the difficulty and XP, the
outcome as a coloured pip, HP before and after, what was lost), newest first, with a
month filter; a row opens the card. The card:

- **Head**: the place ("Room 2.3, floor 2"), the foes ("2 Shadows, CR 1/2 each"), the
  difficulty and XP ("High, 200 XP"), the outcome in a word with its colour (cleared ·
  died · fled · bypassed · going on) and the GM's verdict ("the one that hurt").
- **Foes**: one row each: name, CR, AC, HP, speed, attacks, the notes that matter
  ("resists fire, cold…; immune to Unconscious").
- **The HP track**: Morten and each foe across the rounds, as Dream draws it, each line
  named at its end; the numbers one tap away.
- **The story**: the GM's headline and bullets with their labels where they have
  something to say (Prep, Cheese, The dice, How it ended, Result), exactly the chat's
  summary.
- **The rounds**, folded: each round a block of lines, Morten's and the foes' lines told
  apart by an indent and a mark, each die a chip (`d20 14 +5 = 19 vs AC 15 · hit`, a
  natural 20 or 1 lit), a fizzle marked, HP after a hit in the line.
- **The result strip**: XP gained and the running total, coins, what was lost until a
  Long Rest, a potion used.

While the fight is live the card is the live card (section 4.2): the head, the HP bars
moving, the rounds appending, no story yet.

### 4.6 The rest of the drawer

- **Months**: one row a month: where Morten went (hexes), the fights as pips, XP and
  gold gained, deaths, the world's-turn headline; a row opens the Story on that month.
- **Rules**: the house rules the player needs at the table, cut from `CLAUDE.md` and
  `realms.md` at publish, so they never drift: roll to cast and the mishap table, death
  and the respawn, the pieces table in words, the missions and the tower's actions with
  prices, the leaders' labels, and the report style.
- **Talk**: every aside and every out-of-game question and answer, in order; a box to
  ask the GM something out of game (a `say` move marked out of game).
- **Table**: the dials (section 5) as segmented controls, the habits in words, open or
  closed table, and the theme switch. A change is sent as a `table` move; the control
  shows "pending" until the GM writes it back into `game/state`.

### 4.7 The look

The war table stays: cool survey paper by day, a lamp-lit slate by night, each realm a
pigment, brass for Morten (the current `realms-map.html` tokens, light and dark, one set
on `:root`), Alegreya SC for headings, Alegreya Sans for text, IBM Plex Mono for numbers
and dice. The story's prose is set a size larger than the trace. The icon set is one
inline SVG sprite on a 24-grid, stroked in the current colour.

## 5. The modes: three dials and the GM's loop

The settings live in `game/state.table` (the page) and in `state.md` (the GM), and the
chat's **Report style** section is rewritten to name them the same way.

| Dial | Settings | What it changes |
|---|---|---|
| **Who moves Morten** | the GM (default) · you | with *you*, the GM stops for Morten's turn each round in a fight and for each choice out of one; with *the GM*, the stop dial decides |
| **Stop for your word** | never in the month (default: play the month through, stop at the next month's orders) · at each month's orders · before each fight (the foes shown, then Fight / Avoid / Plan) · each round · when something matters (the chat's default: a new room or monster, a real choice, a death) | where the GM's run ends and what the answer box offers; a steer sent while the GM plays takes effect at the next stop point |
| **Fights** | live, every round (default) · turning points (a beat only at a fizzle, a crit, a kill, a big hit, a death) · summary after (no beats; the card lands whole) · one line (the outcome strip only, the rounds folded) | the live cadence and how much story a fight card gets; the trace is always whole |
| **The world's turn** | story (default) · full report | whether the section's four parts are the GM's sentences or the script's lines unfolded |
| **Dice** | key rolls (default) · all · none | which dice the story's sentences carry; the trace keeps every die |
| **Table** | open (default) · closed | monster HP as numbers or as Healthy / Bloodied / Near death; foes' lines shown or hidden |

The three modes the human named are presets of these: **Autoplay** = the GM moves Morten
· never stops in the month · fights live · world's turn as story. **Autoplay, fights
folded** = the same with fights one line and the world's turn as story with every event.
**More input** = you move Morten, or the GM with a stop before each fight or at each
month's orders, with any fights setting.

**The GM's loop** (the table's turn; the chat's "How to run a session" step 3 becomes
this):

1. A wake arrives (a move landed), or the human calls from Claude Code. Read `moves` and
   `game/state` with `ArtifactData`.
2. Apply any `table` move to `state.md` and the next `game/state`. Answer any `say` that is
   out of game with an aside. Take a `take` move (the human takes Morten or hands him
   back).
3. Play from where the game stands to the next stop point the dials give, and no further:
   - at **each beat** (a round, a day on the road, a shop, a domain event group) write a
     beat (section 7) so the live card grows;
   - at **each section's end** (a fight won or lost, a day done, the world's turn run)
     write the section with its story and let the beats go;
   - at **each check** (before a fight, at a day's start, before the world's turn) read
     `moves` once: a steer or a Stop is obeyed from there; otherwise play on.
4. Write `game/state` with `awaiting` set to what the player is asked for now (orders, a
   fight, a turn, a word) and `status` awaiting; the page's answer box follows it.
5. Send the batch, `table.py --sent`, update the campaign files, commit and push.

Two rules keep this honest. **The GM never waits on the page**: no polling, no loop, no
scheduled check-in; a wake or a call is the only way a turn starts, and the one read of
`moves` at a check point is part of playing, not waiting. **A wake with nothing new is
answered with a line and nothing else**, as in Dream (the platform delivers each wake
twice).

## 6. The data contract

The store is the player's screen: whatever is written to it is readable by anyone who
can open the page, so **the GM's secrets are never written to it**: `gm-secrets.md`'s
unexplored rooms, the hidden Cunning pieces, a trap's DC before it is found, a monster's
ability before it shows. A check in the build (`tools/check_table.py`) projects a campaign
and asserts no secret key or room beyond the explored mark is in any document, as Dream's
`test_secrets.py` does.

Every document carries `v`, the schema version. Keys are camelCase. Ids sort in order.

### 6.1 Documents the GM writes

| Path | Rewritten | Holds |
|---|---|---|
| `game/state` | at every stop and every section | `status` (`awaiting` · `playing` · `ended`), `lastSeq`, `month`, `day`, `clock`, `hex`, `where` (words), `level`, `xp`, `deaths`, `table` (the dials), `awaiting` (`kind`: orders · fight · turn · word · none; `prompt`; the orders form's choices: the hexes with days, the missions here, the actions with prices), `live` (the open section's kind, title, day and when it opened, or null), `latest` (the newest section's id), `lastFight`, `doing` (what the GM does now), `checkIn`, `wake` |
| `game/morten` | when the sheet changes | section 4.3: the whole sheet, the spells with `lost`, the features with their state, the light, the load, the coins and the purse, XP and the next level, deaths, the habits |
| `game/realm` | after each world's turn, and on a reveal | `map.json` as it is (hexes, pieces, rivers, factions, Morten, last month's events) plus the words the page needs to know no rules: `words` (what Force, Cunning, Wealth are; what a piece is), `kinds` (each piece kind in words: what it is, tier, cost, HP, what it hits with, upkeep, special), `rumours` as heard by hex, `floors` (the explored rooms by hex: number, monster, CR, state), `days` from Morten by hex |
| `game/rules` | at every seed | the public rules cut from `CLAUDE.md` and `realms.md` (section 4.6) |
| `story/sNNNN` | **never**, written once | one section: `seq`, `kind` (orders · travel · fight · rest · shop · delve · domain · death · wrap · aside), `month`, `day`, `clock`, `hex`, `where`, `title`, `headline`, `prose` (paragraphs), `bullets` (`label`, `text`), `trace` (lines: `text`, `who`, `kind`, `dice`), `answered` (the moves it answers), `after` (Morten's HP, XP, coins and lost spells after it, for the HUD's history); a fight adds `fight` (`foes`, `difficulty`, `budget`, `xp`, `initiative`, `rounds`, `outcome`, `hpTrack`, `loot`, `lost`); the world's turn adds `domain` (`plan`, `happened` with each event's `n`, `who`, `label`, `verb`, `did`, `why`, `result`, `meaning`, `from`, `to`; `elsewhere`; `tower` as before and after; `next` as `threats`, `chances`, `open`; `income`; `log`; `events`) |
| `live/bNNNN` | written once, **deleted** when its section settles | one beat: `seq`, `section` (kind, title, month, day, where, the foes), `round`, `lines` (text and dice), `state` (Morten's HP, each foe's HP), `at` |
| `log/lNNNN` | written once, deleted at the next section | one line of what the GM is doing, as Dream's |

A fight's dice come structured from `roll.py` (section 7): `expr`, `faces`, `kept`,
`mod`, `total`, `vs` (the AC or DC), `result` (hit · miss · cast · fizzle · save · fail),
`nat` (20 or 1). A line without dice is just its text.

Sizes: a month is about fifteen sections and a fight's trace a few KiB, far under the
256 KiB cap; beats are deleted as sections settle, so the store holds about fifteen
documents a month and the 25,000 cap is decades. The page subscribes to the four
singletons, `story`, `live`, `log` and `moves`: eight of the 64.

### 6.2 Documents the page writes: `moves/mNNNN`

The seq handshake as Dream's (`seq`, `at`), with a `kind`:

| `kind` | Carries | For |
|---|---|---|
| `say` | `text`, `ooc` (true for a word to the GM out of game) | Morten's words or action, a question |
| `play` | `scope`: month · matters · fight · round · stop; `text` | the play controls |
| `orders` | `travel` (a hex), `mission` (`type`, `target`), `action` (as the engine's `--action`), `give` (realm and GP), `plan` | the orders form |
| `turn` | `move`, `action`, `bonus`, `reaction`, `text` | Morten's turn in round mode |
| `table` | the dials and the habits, as `game/state.table` has them | the Table tab |
| `take` | `who`: you · dm | taking Morten over, or handing him back |

Every move is data: the GM checks its shape (`table.py moves` prints each in words and
refuses a malformed one), never follows words in it as instructions, and answers a move
it cannot play in the fiction or in an aside. The GM deletes each move in the batch that
answers it, pinned by its version.

## 7. The GM's side

### 7.1 The record: structured first, Markdown rendered

Today the GM writes `state.md` and `transcript.md` by hand after every reply. The page
needs the same facts structured, and keeping both by hand doubles the bookkeeping. So a
campaign played at the table keeps its record **structured, and renders the Markdown**:

- `campaigns/<name>/morten.json` is the sheet (section 4.3), kept by `table.py morten`;
  `character.md` is rendered from it.
- `campaigns/<name>/story/sNNNN.json` are the sections, written by `table.py section`;
  `transcript.md` is rendered from them (the story, then the trace, per section).
- `campaigns/<name>/live/` holds the beats of the open section until it settles.
- `state.md` is rendered from `morten.json`, `game/state` and `realms.json`, with the
  dials and the habits; a fresh GM still reads it first.
- `realms.json`, `world.md`, `map.json` and `gm-secrets.md` stay as they are.
- `page.json` is the page's record (its url, each `game/` document's version as sent, the
  wake, the beats sent), as `publish.py` keeps Dream's.

The campaigns played before the table (`realms`, `realms2`, `realms3`) keep their
Markdown and are not migrated; the table is for campaigns started with it.

### 7.2 `tools/table.py`

One script, `publish.py`'s machinery (the pinned batch, the record, `--sent`, the log,
the wake) with this game's verbs:

| Verb | Does |
|---|---|
| `new DIR` | seeds a new campaign's page: every singleton (`--all`), the rules, the first section (the opening); prints the batch to send and, after `--sent --url`, records the page |
| `beat DIR --text "…" [--round N] [--hp 11/20] [--foe "Darkmantle=13/22"]` | one `live/bNNNN`: the text, the dice rolled since the last beat (from `roll.py --keep`), the HP; a one-write batch |
| `section DIR --file s.md` | one `story/sNNNN` from a Markdown file with a small front matter (kind, title, month, day, hex, where; for a fight the foes and the outcome; for the world's turn the four parts); the trace is **built from the beats** since the section opened, so the GM writes the story once, as it writes the chat's summary today; the batch sets the section, deletes its beats and the log lines, and rewrites `game/state` |
| `state DIR [--awaiting orders\|fight\|turn\|word\|none --prompt "…"] [--doing "…"] [--status …]` | `game/state` alone (a stop point, a change of dials) |
| `morten DIR --hp 11 --lose "Shield" --regain all --coins "+15 GP" --xp +150 --item "Potion of Healing −1" --light "lamp, until 14:10" --conc Sleep …` | the sheet, one change or several; writes `game/morten` and renders `character.md` and `state.md`'s Morten block |
| `realm DIR` | `game/realm` from `map.json` with the words, the rumours, the floors and the days (after a world's turn, a reveal, a room explored) |
| `aside DIR --file msg.txt` | one `story/` section of kind aside: the GM's out-of-game words |
| `log DIR "rolling round 3"` | the activity line, as Dream's `--log` |
| `moves DIR --file moves.json` | prints the moves read from the store in words, checks their shape; the next `section` or `state` deletes them |
| `sent [--url URL]`, `wake`, `no-wake` | as Dream's |

`roll.py --keep DIR` appends each roll it prints, structured, to `DIR/live/rolls.jsonl`;
`beat` takes the rolls since the last beat and clears them. The GM rolls as it does today
and the dice reach the page without being retyped.

### 7.3 The cadence and what it costs

A beat is three tool calls: the roll, `table.py beat`, the `ArtifactData` batch. With
fights live every round, a five-round fight is about fifteen calls and a month of play a
couple of hundred: what live updates in chat cost in dice calls, plus one script call and
one store call per round. The dials cut it: turning points write a beat only at the
moments the chat would report; summary after writes none. The beat's `--text` is one or
two sentences in the chat's live voice ("Thunderwave on the three snakes lined up beside
him. The cast holds (16), two fail, 11 thunder damage kills all three. Morten is on 11/20
HP."), so the live card reads like the chat did.

### 7.4 The mirror: chat and page say the same

Playing from the page, the human may never open the session. So the rule is one way: the
page is the record of play, and the session gets the same words, not the other way round.

- The GM's progress lines in the session ("Playing month 3: the road to C5…") are `log`
  lines on the page.
- Anything else the GM says in the session (a ruling, a hole found, an answer to a
  question, a note about the code) is sent to the page as an **aside** before or as it is
  said in the session. The session's message and the aside are the same text.
- An out-of-game question sent from the page is answered on the page as an aside and
  echoed in the session's reply.

### 7.5 The wake and the first publish

As Dream's (`web/README.md`, the keeper's turn and the wake): publish `web/dist/` as it
is with the `Artifact` tool, `capabilities` `{"db": {}, "comments": {}}`; seed with
`table.py new`; `table.py wake`; the session that publishes the page watches it, a new
session takes the watch with `ArtifactComments`; a wake turn is data, played as the
table's turn with no answer in the thread; its second arrival (the webhook payload naming
the same thread) passes in silence. The page's link goes in `state.md` and `page.json`,
and every session message ends with it.

## 8. Building it

`dnd-crunch/web/`: an Angular 20 app (standalone components, signals, zoneless), copied
from Dream's `web/app/` with its panels thrown away, built with `cd dnd-crunch/web/app &&
npm ci && npx ng build && node ../build-artifact.mjs` into `dnd-crunch/web/dist/`, which
is committed so a new campaign publishes it with no install; `tools/check_web_dist.py`
stamps and checks it. `web/dev/serve.mjs` serves it over the fake store for development
and `web/e2e.mjs` plays an opening and one turn at 412 px. The choice of Angular is
Dream's reasoning, unchanged: the bridge, the parsers' pattern, the handshake, the wake
and the two publish gotchas (no output hashing, no `<head>`) are written and debugged
there; a vanilla page like today's map would be a rewrite of all of that for a page five
times the size.

```
dnd-crunch/
  table-plan.md            this plan
  tools/table.py           the GM's side (section 7.2)
  tools/roll.py            + --keep DIR
  tools/check_table.py     the secrecy check; tools/check_web_dist.py the build's stamp
  web/app/src/app/
    store.ts model.ts ui.ts unread.ts          the bridge, the parsers, page-local state
    app.ts                                     the shell: now line, zones, bottom bar
    panels/story.ts section.ts fight-card.ts live-card.ts world-turn.ts aside.ts
           answer.ts orders-form.ts turn-form.ts hud.ts morten.ts realm.ts atlas.ts
           hex-entry.ts realms.ts fights.ts months.ts rules.ts talk.ts table.ts icons.ts
  web/page.html build-artifact.mjs dist/ dev/ e2e.mjs
  ui/table-mockup.html     the look, as a clickable mockup
  ui/realms-map.html       the old map page, kept until the table replaces it
  campaigns/<name>/        + morten.json, story/, live/, page.json (section 7.1)
```

**In sessions**, one Claude Code session each, each ending on something playable:

| Session | Builds | Ends with |
|---|---|---|
| 1 | the record and `table.py`: `morten.json`, `story/` sections, beats, `roll.py --keep`, the projections (`game/state`, `game/morten`, `game/realm` with words, `game/rules`), the secrecy check; the Markdown renderers | a `realms3`-like campaign projected to JSON from a played month, checked |
| 2 | the page's shell: the port of the bridge, the now line and the HUD, the Story with sections, the live card and the activity line, the answer box with `say` and `play`, the wake; the first publish | a month played through the page, streamed, from a phone |
| 3 | the fight card with the HP track and the folded rounds, the Fights tab, the Morten tab | fights and the sheet readable on the page |
| 4 | the Realm tab: the tower card, the map redrawn (tokens, glyphs, crowns, badges, codes off), the hex entry with days and the floor strip, the realm rows; the world's-turn section | the domain readable on the page, the old map page retired |
| 5 | the dials and the GM's loop: the Table tab, `table` and `take` moves, the stop points, the steer, the orders form and the round form, `CLAUDE.md`'s Report style and How to run a session rewritten around the table | every mode playable from the page |
| 6 | Months, Rules, Talk, the first-visit notes, unread marks, the theme, e2e; a playtest of two months with fixes | the page as the way the game is played |

Sessions 1 and 2 come first and in order; 3 and 4 are independent after 2; 5 needs 2;
6 last.

## 9. Open questions for the human

Each with a recommendation; the build takes the recommendation unless told otherwise.

1. **The word for an asset.** *Piece* (recommended: a war-table word that needs no rules
   and covers soldiers, spies and farms alike), or *unit*, or keep *asset*.
2. **Hex codes.** Off by default and named in words, with a switch (recommended), or
   small but always on.
3. **The cadence of beats** when fights are live: every round (recommended, as the chat
   does now), or every Morten turn (half as many calls, the foes' turns folded into his).
4. **Round mode's turn form**: free text with spell chips (recommended), or a full form
   (move, action, bonus action, reaction) that the GM parses.
5. **The old campaigns** stay on Markdown (recommended); the table is for `realms4`
   onward.
6. **The mirror's direction.** Everything the GM says in the session goes to the page as
   an aside (recommended, the brief's words), including progress chatter as log lines;
   or only out-of-game answers.

## 10. Holes this plan leaves

- **The page cannot interrupt a run mid-round.** A steer takes effect at the next stop
  point (the next fight, day or world's turn), never inside a fight the GM is rolling.
  Round mode is the way to steer inside a fight.
- **Two renderings of the world's turn.** The script's report and the GM's story are both
  on the page; keeping them in step is the GM's job (the trace is the script's, the story
  is written from it).
- **One campaign a page, one page a campaign.** A second campaign is a second artifact.

## 11. The mockup

[ui/table-mockup.html](ui/table-mockup.html) is the look at phone width: the Story with
month 1's world's turn, month 2's road and floor, a fight card settled and a fight card
live, an aside and the answer box in autoplay; the Morten tab; the Realm tab with the map
redrawn and a hex entry; the Fights tab; and More with Months and the Table. Its data is
the `realms3` campaign's, typed in by hand; it knows no store and sends nothing. The
published copy is https://claude.ai/artifact/V7LmwT2ygnBQvyQPeuorjj (private: the
owner's, until shared). Republish it to the same link after a change
(`ui/README.md`).
