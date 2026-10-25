# The table's page (`web/`)

The page that plays a Realms campaign: [../table-plan.md](../table-plan.md) is the design,
this file is how it is built and the exact data it reads and writes. Where the two differ,
this file wins (the plan says so in its notes).

## Departures from the plan

- **Vanilla JS, not Angular.** The plan copied Dream's Angular app for its bridge and
  harness; Dream's code is not reachable from this repo, so the bridge, the parsers and the
  dev harness are written here from the platform's own type definitions. With nothing to
  copy, a framework buys nothing: the page is plain HTML/CSS/JS like `ui/realms-map.html`
  and `ui/table-mockup.html`, split into source files and joined by `build.py`. No npm, no
  install, no network.
- **One build output**: `web/dist/table.html`, committed, published with the Artifact
  tool as it is. Like the map page it has no doctype, `<html>`, `<head>` or `<body>`
  (the artifact host adds the skeleton).

## Layout

```
web/
  README.md            this file
  build.py             joins src/ into dist/table.html; --check verifies dist is current
  src/page.html        the shell: <title>, the CSS slot, the SVG sprite, the markup, the JS slot
  src/css/NN-name.css  joined in file-name order into one <style>
  src/js/NN-name.js    joined in file-name order into one <script>; each file is an IIFE
  dist/table.html      the build (committed)
  dev/serve.mjs        the local table: dist over a fake store, live over server-sent events
  dev/fake-claude.js   window.claude for the dev page: use("db"), use("comments"), use("user")
  dev/db.mjs           CLI: apply an ArtifactData-shaped batch to the dev store, dump it, seed it
  dev/fixture/         a realms3-like campaign projected by tools/table.py (the store's docs)
  e2e.mjs              Playwright at 412 px: seed, load, play a move, a beat, a section
```

### JS conventions

- One global namespace, `window.T`, made in `src/js/00-core.js`. Every other file is
  `(() => { 'use strict'; const T = window.T; ... })();` and hangs its exports on `T`:
  `T.store`, `T.model`, `T.ui`, `T.icons`, `T.panels.<name>`.
- A panel is `T.panels.<name> = { mount(el), render(view) }`. `render` is called with the
  parsed view model (below) after every store change, at most once per animation frame.
  Panels re-render their own element only; they keep their own UI state (open folds,
  picked hex) in closures, and survive re-renders (no lost scroll, no lost input).
- Escape every string from the store with `T.ui.esc` before it goes into HTML, or set
  `textContent`. Store content is untrusted.
- No `localStorage` outside `T.ui.local` (try/catch wrapped; per-viewer conveniences only:
  theme, first-visit notes dismissed, reading position, unread marks, the wake thread id).
- Numbers carry their unit. Icons from the sprite: `T.ui.icon('heart')` returns
  `<svg class="ic"><use href="#i-heart"/></svg>`. The sprite and the tokens are the
  mockup's (`ui/table-mockup.html`), light and dark on `:root`.

### File ownership (so parallel work does not collide)

| Files | Owner |
|---|---|
| `src/page.html`, `src/css/00-tokens.css` `10-shell.css`, `src/js/00-core.js` … `40-app.js` | the shell |
| `src/css/50-story.css`, `src/js/50-story.js` (sections, months, days, live card, world's turn, aside, answer box, orders form, turn form) | Story |
| `src/css/60-fight.css`, `src/js/60-fight.js` (`T.panels.fightCard`, the Fights tab), `src/css/62-morten.css`, `src/js/62-morten.js` | Fights & Morten |
| `src/css/70-realm.css`, `src/js/70-realm.js` (tower card, map, hex entry, realm rows) | Realm |
| `src/css/80-more.css`, `src/js/80-more.js` (Months, Rules, Talk, Table, notes, theme) | More |

## The page's view model

`T.store` subscribes once to `game/state`, `game/morten`, `game/realm`, `game/rules`
(docs) and `story`, `live`, `log`, `moves` (collections), and `T.model.view(raw)` parses
them into one object. Every field is read with a fallback; nothing is cast.

```js
view = {
  ready: bool,            // false until the first snapshot of game/state (or no db: a notice)
  db: 'ok' | 'none' | 'error',
  state, morten, realm, rules,   // parsed singletons, null when missing
  sections: [...],        // story/*, sorted by seq ascending
  beats: [...],           // live/*, sorted by seq
  logs: [...],            // log/*, sorted by seq
  moves: [...],           // moves/*, sorted by seq (the player's, not yet answered)
  pending: [...],         // moves this view sent that have not landed yet
}
```

`T.store.send(kind, fields)` writes one move (below), then wakes the GM. Writes go one at
a time; a second send waits for the first.

## The data contract

Paths are the db's: collection `game`, doc ids `state`, `morten`, `realm`, `rules`;
collections `story`, `live`, `log`, `moves` with doc ids `s0001`, `b0001`, `l0001`,
`m0001` (zero-padded to 4, so ids sort in order). Every document has `v: 1`. Keys are
camelCase. A `seq` is one counter shared by the GM's sections, beats and logs (the GM's
`lastSeq`); moves have their own counter (the page's, `moves.seq`).

### `game/state`

```json
{
  "v": 1, "campaign": "realms4", "status": "awaiting",
  "lastSeq": 42, "lastMove": 7,
  "month": 3, "day": 4, "clock": "09:40", "hex": "A5",
  "where": "Floor 2, room 2.4 · under the Humans' A5",
  "level": 3, "xp": 2125, "deaths": 0,
  "hud": {"hp": 11, "maxHp": 20, "ac": 12, "acArmor": 15, "light": "lamp, until 10:40",
          "conc": "Sleep", "conditions": [], "exhaustion": 0, "reaction": true,
          "inspiration": true, "freeArmor": false, "coins": "7 SP 5 CP", "lost": ["Shield"]},
  "table": {"who": "dm", "stop": "month", "fights": "live", "world": "story",
            "dice": "key", "mode": "open",
            "habits": ["Shield: when a hit would become a miss at AC 20 and deals 4+ damage."]},
  "awaiting": {"kind": "orders", "prompt": "Month 3's orders",
               "orders": {"hexes": [{"id": "A5", "name": "the Humans' savanna", "days": 1}],
                          "missions": [{"type": "delve", "target": "floor 2", "label": "Delve floor 2 (level 2)"}],
                          "actions": [{"action": "buy Thugs in B5", "label": "Buy Thugs in B5", "cost": 50}],
                          "realms": ["Humans", "Goblinkind"]},
               "fight": null, "turn": null},
  "live": {"kind": "fight", "title": "Room 2.4 · Darkmantle (CR 1/2)", "month": 3, "day": 4,
           "openedAt": "2026-10-25T09:12:00Z"},
  "latest": "s0041", "lastFight": "s0039",
  "doing": "rolling the Darkmantle's crush",
  "checkIn": null,
  "wake": {"on": true},
  "url": "https://claude.ai/artifact/…"
}
```

- `status`: `awaiting` (the GM waits for the player) · `playing` (a run is going on) ·
  `ended`.
- `table.who`: `dm` · `you`. `table.stop`: `month` · `orders` · `fight` · `round` ·
  `matters`. `table.fights`: `live` · `turning` · `summary` · `line`. `table.world`:
  `story` · `report`. `table.dice`: `key` · `all` · `none`. `table.mode`: `open` · `closed`.
- `awaiting.kind`: `orders` · `fight` · `turn` · `word` · `none`. With `fight`,
  `awaiting.fight` is `{"title", "foes": [Foe], "difficulty", "xp"}`. With `turn`,
  `awaiting.turn` is `{"board": "<the log format's Area/Positions/State as text lines>",
  "lines": ["…"], "options": ["Fire Bolt", "Shocking Grasp", "Dagger", "Dash", …]}`.
- `live` is null when no section is open.

### `game/morten`

```json
{
  "v": 1, "name": "Morten", "class": "Wizard 3 (Evoker)", "species": "Human",
  "background": "Sage",
  "hp": 20, "maxHp": 20, "hitDice": "3/3 d6", "ac": 12, "acArmor": 15, "speed": "6 sq (9 m)",
  "initiative": "+2", "passivePerception": 11, "prof": 2, "spellAttack": 5, "saveDc": 13,
  "abilities": [{"key": "INT", "score": 15, "mod": 2, "save": 4}],
  "skills": [{"name": "Arcana", "mod": 6}],
  "attacks": [{"name": "Fire Bolt", "hit": "+5", "damage": "1d10 fire", "range": "24 sq (36 m)"}],
  "spells": [{"name": "Shield", "level": 1, "dc": 11, "lost": false, "conc": false,
              "ritual": false, "line": "Reaction: +5 AC until your next turn; no Magic Missile.",
              "prepared": true}],
  "features": [{"name": "Arcane Recovery", "state": "ready", "line": "…"}],
  "light": "lamp, about 1 h of oil left", "conc": null, "conditions": [], "exhaustion": 0,
  "inspiration": true, "freeArmor": true,
  "gear": [{"name": "Oil flask", "count": 8, "kg": 0.5, "note": ""}],
  "load": {"kg": 31, "max": 54},
  "coins": {"on": "7 SP 5 CP", "purse": "none"},
  "xp": 2125, "nextXp": 2700, "level": 3, "deaths": 0, "familiar": "owl (Fey)",
  "habits": ["…"], "trader": [{"name": "Potion of Healing", "price": "50 GP"}]
}
```

`trader` is present only while he is home (or at a camp with a trader).

### `game/realm`

`map.json` as `realms.py` writes it (`hexes`, `rivers`, `factions`, `morten`, `events`,
`report`, `layout`, `month`, `campaign`; see `ui/README.md`: The data), kept snake_case
as the engine writes it, plus these camelCase keys the page needs to know no rules:

```json
{
  "v": 1,
  "words": {"force": "Force: soldiers, and the strength to take and hold land.",
            "cunning": "…", "wealth": "…", "piece": "A piece is something a realm has put on the map: soldiers, spies or income.",
            "regime": "The realm's health as a power; at 0 it falls.",
            "level": "Level N: floor N lies under it, its wanderers are level-N trouble, and it pays N×10 GP a month."},
  "kinds": {"Knights": {"glyph": "sword", "type": "F", "tier": 3, "what": "mounted soldiers",
                        "cost": 300, "hp": 12, "hits": "hits with Force against Force for 1d8",
                        "counter": "hits back 1d8", "upkeep": 100, "special": ""}},
  "rumours": {"A5": ["The Humans' reeve pays 50 GP for each wolf pelt."]},
  "floors": {"A5": {"floor": 2, "rooms": [{"n": "2.1", "monster": "3 Wolves", "cr": "1/4", "state": "cleared"},
                                          {"n": "2.4", "monster": null, "cr": null, "state": "unknown"}]}},
  "days": {"A5": 1, "B5": 0},
  "eventsWords": [{"n": 1, "who": "Gnomes", "from": "D3", "to": "C4", "text": "The Gnomes marched Thugs and Knights into C4."}],
  "hexNames": {"A5": "the Humans' savanna"}
}
```

Only what the tower can know is in it: `map.json` is already the tower's view; a floor's
rooms past the explored mark are `"state": "unknown"` with no monster.

### `game/rules`

```json
{"v": 1, "sections": [{"id": "cast", "title": "Roll to cast", "md": "…markdown…"}]}
```

The page renders `md` with `T.ui.md` (a small, safe Markdown subset: paragraphs, `**bold**`,
`*italic*`, `` `code` ``, bullets, tables, headings `###`; everything escaped first).

### `story/sNNNN` (written once, never changed)

```json
{
  "v": 1, "seq": 41, "kind": "fight",
  "month": 3, "day": 4, "clock": "09:52", "hex": "A5", "where": "Floor 2 · room 2.4",
  "title": "Room 2.4 · Darkmantle (CR 1/2) · Low, 100 XP · cleared",
  "headline": "Morten pried the Darkmantle off his head and burned it.",
  "prose": ["paragraph", "paragraph"],
  "bullets": [{"label": "Cheese", "text": "…"}],
  "trace": [Line],
  "answered": ["m0007"],
  "after": {"hp": 11, "maxHp": 20, "xp": 2225, "coins": "7 SP 5 CP", "lost": ["Shield"]},
  "fight": Fight | null,
  "domain": Domain | null,
  "words": [{"move": "m0007", "text": "the player's words, as sent"}]
}
```

- `kind`: `orders` · `travel` · `fight` · `rest` · `shop` · `delve` · `domain` · `death` ·
  `wrap` · `aside` · `opening`. An aside has `prose` only (the GM's words) and `ooc: true`
  when it answers an out-of-game question.
- `Line`: `{"text": "Morten casts Fire Bolt at the Darkmantle.", "who": "morten" | "foe" |
  "gm" | "world", "kind": "roll" | "cast" | "attack" | "save" | "damage" | "note" | "move",
  "round": 2, "dice": [Die]}`. `round` is present in fights only.
- `Die`: `{"expr": "1d20+5", "faces": [14], "kept": [14], "mod": 5, "total": 19,
  "vs": "AC 15", "result": "hit" | "miss" | "cast" | "fizzle" | "save" | "fail" | null,
  "nat": 20 | 1 | null}`.
- `Fight`: `{"foes": [Foe], "difficulty": "Low", "budget": 150, "xp": 100,
  "initiative": ["Morten 18", "Darkmantle 7"], "rounds": 3, "outcome": "cleared" | "died" |
  "fled" | "bypassed" | "going", "verdict": "the one that hurt",
  "hpTrack": [{"name": "Morten", "max": 20, "hp": [20, 14, 11, 11]}, {"name": "Darkmantle", "max": 22, "hp": [22, 13, 0]}],
  "loot": "+15 GP", "lost": ["Shield"], "potion": false, "xpBefore": 2125, "xpAfter": 2225}`.
  `hp[i]` is the HP after round `i` (index 0: before round 1).
- `Foe`: `{"name": "Darkmantle", "cr": "1/2", "ac": 11, "hp": 22, "maxHp": 22,
  "speed": "2 sq (3 m), fly 6 sq (9 m)", "attacks": ["Crush +5, 1d6+3 bludgeoning"],
  "notes": "Darkness Aura (1/day)", "count": 1}`. On a closed table the GM writes `hp` as
  null and `state` as `healthy` · `bloodied` · `near death`.
- `Domain`: `{"plan": ["…"], "happened": [{"n": 1, "who": "Gnomes", "label": "bad",
  "verb": "robs its neighbours", "text": "The sentence the GM wrote.", "from": "D3", "to":
  "C4"}], "elsewhere": "…", "tower": [{"what": "Gold", "before": "89 GP", "after": "149 GP"}],
  "next": {"threats": ["…"], "chances": ["…"], "open": ["…"]}, "income": ["…"],
  "log": ["the script's lines verbatim"]}`. `happened[].n` matches the map's badges
  (`game/realm.eventsWords[].n`).

### `live/bNNNN` (written once, deleted when its section settles)

```json
{"v": 1, "seq": 39, "section": {"kind": "fight", "title": "Room 2.4 · Darkmantle (CR 1/2)",
 "month": 3, "day": 4, "where": "Floor 2 · room 2.4", "foes": [Foe]},
 "round": 2, "text": "Fire Bolt hits for 8 dmg; the Darkmantle is on 13/22 HP.",
 "lines": [Line], "state": {"morten": {"hp": 14, "maxHp": 20}, "foes": [{"name": "Darkmantle", "hp": 13, "maxHp": 22}]},
 "at": "2026-10-25T09:14:00Z"}
```

### `log/lNNNN` (written once, deleted at the next section)

`{"v": 1, "seq": 40, "text": "rolling round 3", "at": "…"}`

### `moves/mNNNN` (the page writes; the GM deletes each when it answers it)

`{"v": 1, "seq": 7, "at": "<ISO time>", "kind": …, …fields}` with:

| `kind` | Fields |
|---|---|
| `say` | `text`, `ooc` (bool) |
| `play` | `scope`: `month` · `matters` · `fight` · `round` · `stop`; `text` (optional steer) |
| `orders` | `travel` (hex id), `mission` `{type, target}` or null, `action` (string, the engine's `--action`) or null, `give` `{realm, gp}` or null, `plan` (text) |
| `fight` | `choice`: `fight` · `avoid` · `plan`; `text` |
| `turn` | `text` (free text, with spell chips dropped in) |
| `table` | `table` (the whole dials object as in `game/state.table`) |
| `take` | `who`: `you` · `dm` |

The page's move seq is `max(game/state.lastMove, every moves/* seq, its own last) + 1`.
It writes `moves/m` + the seq zero-padded to 4. A move shows as pending until it appears
in `moves` (then as sent) and is gone from `moves` once the GM has answered it (shown under
the section whose `answered` names it, from `story/*.words`).

### The wake

After a move lands, when `game/state.wake.on` is true, the page calls
`comments.sendToClaude`: the first time with `{anchor: await comments.anchorFor(<the answer
box>), text}`, after that `{threadId, text}` with the thread id it got back (kept in
`T.ui.local`). `text` is one line: `Table move m0007 (say).` Before that it checks
`canSendToClaude()` and shows the reason in the status line when it is not `available`
("the GM is not watching; it will read your move next time"). A wake is never retried
in a loop; the status line offers one "Call the GM again" button.

## The GM's side

`tools/table.py` (see the plan, section 7.2) keeps the campaign's record and writes the
store. It never talks to the network: each verb writes the documents it changes as JSON
files under `<campaign>/page/out/` and prints the `ArtifactData` batch to send as JSON
(`{"writes": [{"op", "collection", "doc_id", "file_path", "if_version"}]}`), which the GM
passes to the `ArtifactData` tool's `batch` action. `table.py sent` records the versions
(assumed 1 for a created doc and +1 for a rewritten one; `--version path=N` overrides from
the batch's result). A pinned write with a wrong version is refused by the store and
writes nothing, so a wrong guess is safe: re-read and redo.

`web/dev/db.mjs apply <batch.json>` applies the same batch to the dev store, with the same
version rules, so the whole loop runs locally.

## Running it

```sh
python3 dnd-crunch/web/build.py                  # build dist/table.html
python3 dnd-crunch/web/build.py --check          # dist is current
node dnd-crunch/web/dev/serve.mjs --seed dnd-crunch/web/dev/fixture   # http://localhost:8787
node dnd-crunch/web/dev/db.mjs apply batch.json  # play the GM's side locally
node dnd-crunch/web/e2e.mjs                      # the smoke test at 412 px
```
