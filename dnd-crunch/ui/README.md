# The Realms map page

`realms-map.html` is the page the human reads a Realms v2 campaign by: one vanilla
HTML/CSS/JS file with no build step, no library and no external script. It's designed for
a phone first (412 px, a bottom bar, every tap target 44 px or more) and works side by side on a
desktop. It knows no rules: every string it shows comes worded in the data.

## What it shows

- **Header and tower strip:** the month about to be played, how many moves the tower saw
  last month, and the tower at a glance: HP, Force/Cunning/Wealth, gold, Morten's hex
  and level, who is hostile (and for how long), and the allies.
- **Map:** the 4 × 5 flat-topped hexes, tinted by holder, with realm borders. Each hex
  shows its id, level, biome, any lake, the rivers on its edges, a ruler's seat (a flag)
  or the tower, and the assets seen there as chips in the owner's colour: type letter
  (F/C/W), tier as dots and an HP strip under each. A dashed red edge means the owner is
  hostile to the tower. Morten's hex has a brass ring and an M. Last month's events are
  numbered arrows (a badge in place when an event stays in one hex), with a toggle to hide
  them. Tap a hex to open its entry: level, biome, people, holder, income, river, the
  assets with HP bars, attack, counter, special and leader, the events that touched it,
  and its neighbours as buttons.
- **Realms:** a standings list (HP, attributes, label and state), then one card per
  faction, the tower first: leader, the *label: verb* pill, the goal line, HP,
  attributes, treasury, state chips (hostile months, ally, disorder), seat and hexes, and
  the assets the tower can see. Every hex and asset row opens that hex on the map.
- **Month:** the report in its four parts (The plan, What happened, The tower now, Next
  month, with Threat/Chance/Open lines marked), then every event in order, numbered as
  on the map.

`#map`, `#realms` or `#month` on the link opens that view.

## Building it

```sh
python3 dnd-crunch/tools/realms_page.py dnd-crunch/campaigns/<name>          # writes <name>/page.html
python3 dnd-crunch/tools/realms_page.py dnd-crunch/campaigns/<name> --out FILE
```

The script reads `<campaign>/map.json`, which `realms.py` writes after `new` and after
every real (not dry-run) turn. It inlines the JSON into the template's one placeholder
(`__MAP_JSON__`) with `<`, `>` and `&` escaped, so no string in the data can close the
script element. `sample-map.json` is a realistic sample (the v1 campaign's map with
invented v2 factions, assets and nine events) to build and try the page against:

```sh
mkdir -p /tmp/rm && cp dnd-crunch/ui/sample-map.json /tmp/rm/map.json
python3 dnd-crunch/tools/realms_page.py /tmp/rm
```

## Publishing

The GM publishes `page.html` as a claude.ai artifact (private until the human shares it),
and after every domain turn rebuilds it and republishes it to **the same URL**, so the
human's link never changes. Keep the link in the campaign's `state.md`. The file has no
doctype, `<html>`, `<head>` or `<body>` because the artifact host adds that skeleton.

## The data

`map.json` is documented in `dnd-crunch/realms.md` (Realms v2). It is the tower's view:
only what Morten and the tower can know. In short:

- `month` (the month about to be played), `campaign`, and
  `layout` `{cols, rows, orientation: "flat-top", shift: "odd"}`.
- `hexes[]`: `id`, `col`/`row` (0-based), `level`, `biome`, `people`, `holder` (a
  faction name, `"tower"` or null), `lake`, `seat_of`, `income`, `neighbours`, and
  `assets[]` with `id`, `owner`, `name`, `type`, `tier`, `hp`, `max_hp`, `leader`,
  `attack`, `counter` and `special`.
- `rivers`: pairs of hex ids that share a river edge.
- `factions[]`: `name`, `tower`, `leader` `{name, title, label, tag, verb}`, `goal`,
  `hp`, `max_hp`, `force`, `cunning`, `wealth`, `treasury`, `seat`, `hexes`, `hostile`
  (months left), `ally` and `disorder` (months left).
- `morten` `{hex, level}`.
- `events[]` (last month, in order): `month`, `actor`, `action`, `from_hex`, `to_hex`
  (either may be null), `target` and `result`.
- `report` `{plan, happened, tower, next}`, each a list of plain lines. A `next` line that
  starts with `Threat:`, `Chance:` or `Open:` is marked as one.

The page is defensive: a missing field is left out, `col`/`row` fall back to the id, and
a page with no data shows how to build it.

## The table's mockup

`table-mockup.html` is the look of the page that is to replace this one: the whole game
played from a page, as [../table-plan.md](../table-plan.md) plans it. One vanilla file in
the same artifact format as the map page, filled by hand with the `realms3` campaign's
second month (the Story with a live fight, the world's turn, an aside and the answer box
in its four states; Morten; the Realm with the map redrawn; Fights; More with the months
and the table's dials). It reads no store and sends nothing: every control is a mock.
Published at https://claude.ai/artifact/V7LmwT2ygnBQvyQPeuorjj; after a change,
republish the same file to that link (the Artifact tool with `url` set to it).
