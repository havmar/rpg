#!/usr/bin/env bash
# Rebuild the fixture campaign by playing realms3's month 2 through tools/table.py, as a GM
# would (every batch "sent" at once), then export the store's view for the dev page:
#   web/dev/fixture/       the end of month 2: the world's turn done, awaiting month 3's orders
#   web/dev/fixture-live/  the same play stopped in room 2.5, a fight open with 2 beats
# Run from anywhere:  bash dnd-crunch/web/dev/fixture-campaign/play.sh
# Inputs are play/ (sections as Markdown, morten-start.json, foes.json, moves) and realms3's
# map.json, realms.json, gm-secrets.md, rules.md, world.md (copied; realms3 is not touched).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"
D=dnd-crunch/web/dev/fixture-campaign
P=$D/play
SRC=dnd-crunch/campaigns/realms3
export TABLE_NOW=2026-10-25T09:00:00Z
t() {  # quiet unless it fails
  local err; err=$(python3 dnd-crunch/tools/table.py "$@" 2>&1 >/dev/null) || { echo "table.py $1: $err" >&2; return 1; }
}
sent() { python3 dnd-crunch/tools/table.py sent "$D" 2>/dev/null; }
play() { t "$@"; sent; }       # one verb, and its batch sent
foes() { python3 -c "import json,sys; print(json.dumps(json.load(open('$P/foes.json'))[sys.argv[1]]))" "$1"; }
explore() {  # mark a room of floor 2 explored in gm-secrets.md: explore 2.1 ["note"]
  python3 - "$D/gm-secrets.md" "$1" "${2:-}" <<'EOF'
import sys
p, n, note = sys.argv[1:]
s = open(p).read()
s = s.replace(f"| {n} |", f"| {n} ✓{' (' + note + ')' if note else ''} |", 1)
open(p, "w").write(s)
EOF
}

# ---- the record, from realms3 ----
rm -rf "$D"/story "$D"/live "$D"/page "$D"/page.json "$D"/state.json "$D"/morten.json \
       "$D"/character.md "$D"/state.md "$D"/transcript.md
for f in map.json realms.json gm-secrets.md rules.md world.md; do cp "$SRC/$f" "$D/$f"; done
cp "$P/morten-start.json" "$D/morten.json"
# floor 2 as it was at the start of month 2: nothing explored
sed -i -E 's/^\| (2\.[0-9]+) ✓( \([^)]*\))? \|/| \1 |/; s/^(## Floor 2 · A5 \(savanna, Humans\)) · CLEARED.*/\1/' "$D/gm-secrets.md"

# ---- Month 2 · Day 1: the page opens; the player's question and "play a month" ----
play new $D --campaign realms3 --file $P/s01-opening.md --month 2 --day 1 --clock 08:00 --hex B5 --where "the tower (B5)"
play wake $D
python3 dnd-crunch/tools/table.py moves $D --file $P/moves-1.json >/dev/null
play aside $D --file $P/a01-cr.md --ooc --answers m0001
play log $D "Month 2: the orders"
play section $D --file $P/s02-orders.md --status playing --doing "playing month 2"

# ---- Day 2: the road and the lizards ----
play morten $D --item "Rations -1" --armor on --free-armor off
play log $D "Day 2: on the road to A5"
play section $D --file $P/s03-travel.md --die 1d6:1
play morten $D --hp 17 --lose "Magic Missile" --inspiration off --xp +150 --coins "+15 GP"
play section $D --file $P/s04-lizards.md \
  --die 1d20+4:20 --die 1d20+1:15 \
  --die "1d20+5:20:DC 11:cast" \
  --die "1d20:8:DC 13:fail" --die "1d20:17:DC 13:save" --die "1d20:19:DC 13:save" --die "1d20:3:DC 13:fail" \
  --die "1d20+5:13:DC 11:cast" --die "1d20+1:17:DC 13:save" --die "1d20+1:8:DC 13:fail" --die 2d8:6,4 \
  --die "1d20+4:9:AC 15:miss" --die "1d20+4:3:AC 15:miss" \
  --die "1d20+5:5:DC 11:fizzle" --die "1d20+5:8:DC 11:cast" --die "1d20+1:14:DC 13:save" --die "1d20+1:12:DC 13:save" --die 2d8:4,3 \
  --die "1d20+4:15:AC 15:hit" --die "1d20+5:10:DC 11:cast" \
  --die "1d20+5:18:DC 11:cast" --die 3d4+3:3,4,4 \
  --die "1d20+5:2:DC 11:fizzle" \
  --die "1d20+4:18:AC 15:hit" --die 1d8+2:1 \
  --die "1d20+2:20:DC 10:save" \
  --die "1d20+5:8:DC 11:cast" --die "1d20+1:8:DC 13:fail" --die 2d8:4,7 \
  --die "1d20+5 adv:14,15:AC 12:hit" --die 4d6:5,1,3,4 \
  --die "1d20+5:13:AC 12:hit" --die 2d6:1,5
play morten $D --long-rest --armor off
play section $D --file $P/s05-rest.md

# ---- Day 3: floor 2 ----
play morten $D --item "Rations -1" --item "Oil flask -1" --armor on --free-armor off --light "lamp, fresh flask until 12:10"
play section $D --file $P/s06-delve.md
# Room 2.1 · Grimlocks, live: open, two beats, the section
play open $D --kind fight --title "Room 2.1 · 3 Grimlocks (CR 1/4 each)" --where "Floor 2 · room 2.1" --clock 06:20 --foes "$(foes grimlocks)" --doing "fighting the grimlocks in room 2.1"
play beat $D --round 1 --text "Sleep on the two grimlocks that came first: the cast holds (20) and both fail their WIS saves. Morten is on 20/20 HP." \
  --line "gm/roll/3: Grimlock Stealth 11 vs passive Perception 13: seen. Initiative: Grimlocks 21, Morten 15." \
  --line "foe/attack/2: Grimlocks A and B close to D9 and C9 and swing their bone cudgels: both miss." \
  --line "morten/cast/1: Sleep on A and B: the cast holds." \
  --line "foe/save: A and B fail their WIS saves: Incapacitated." \
  --die 1d20+5:6 --die 1d20+1:20 --die 1d20+4:11 \
  --die "1d20+5:5:AC 15:miss" --die "1d20+5:7:AC 15:miss" --die "1d20+5:15:DC 11:cast" \
  --die "1d20-1:4:DC 13:fail" --die "1d20-1:13:DC 13:fail" \
  --hp 20/20
play log $D "rolling round 2"
play beat $D --round 2 --text "Thunderwave fizzled, and the Heroic Inspiration reroll held: 16 thunder dmg kills two grimlocks, and the third ran into his dagger. Morten is untouched." \
  --line "foe/save/2: A and B make their second saves (B with a natural 20) and wake." \
  --line "foe/attack/2: C closes to E9 and hits; Shield holds (24 vs DC 11): AC 20, miss." \
  --line "morten/cast/6: Thunderwave fizzles on 9; the Heroic Inspiration reroll holds (14). A and B fail their CON saves, C saves: 16 thunder dmg. A and B dead, C 11 → 3 HP." \
  --line "foe/save/1: C fails its morale roll and flees." \
  --line "morten/attack/2: Opportunity attack with the dagger: hit, 4 piercing dmg. C dead." \
  --die "1d20-1:14:DC 13:save" --die "1d20-1:20:DC 13:save" \
  --die "1d20+5:13:AC 15:hit" --die "1d20+5:19:DC 11:cast" \
  --die "1d20+5:4:DC 11:fizzle" --die "1d20+5:9:DC 11:cast" --die "1d20+1:11:DC 13:fail" --die "1d20+1:6:DC 13:fail" --die "1d20+1:18:DC 13:save" --die 2d8:8,8 \
  --die "1d20-1:7:DC 10:fail" --die "1d20+4:13:AC 11:hit" --die 1d4+2:2 \
  --foe "Grimlock A=0" --foe "Grimlock B=0" --foe "Grimlock C=0"
play morten $D --inspiration off --xp +150 --coins "+15 GP"
explore 2.1
play section $D --file $P/s07-grimlocks.md
play realm $D

# Room 2.2 · Mastiffs, told after (no beats)
play morten $D --hp 17 --lose "Shocking Grasp" --lose "Magic Missile" --xp +100 --coins "+10 GP"
explore 2.2 "2 Mastiffs fled, morale"
play section $D --file $P/s08-mastiffs.md \
  --die "1d20+5:11:AC 12:hit" --die 1d10:8 --die "1d20+3:17:AC 15:hit" --die 1d6+1:2 \
  --die "1d20+5:3:DC 10:fizzle" --die "1d20+3:15:AC 15:hit" --die "1d20+5:18:DC 11:cast" \
  --die "1d20+5:2:DC 11:fizzle" \
  --die "1d20+5:11:DC 11:cast" --die "1d20+1:2:DC 13:fail" --die 2d8:1,5 \
  --die "1d20+3:6:DC 10:fail"
play morten $D --regain "Shocking Grasp" --regain "Magic Missile" --feature "Arcane Recovery=used" --hp 20 --hit-dice "2/3 d6"
play section $D --file $P/s09-short-rest.md --die 1d6+2:5

# Room 2.3 · Shadows, told after
play morten $D --hp 11 --ability STR=3 --xp +200 --coins "+20 GP"
explore 2.3
play section $D --file $P/s10-shadows.md \
  --die "1d20+5:8:DC 11:cast" --die 3d4+3:2,2,3 \
  --die "1d20+5:12:DC 11:cast" --die 3d4+3:1,4,4 \
  --die "1d20+4:17:AC 15:hit" --die 1d6+2:3 --die 1d4:3 \
  --die "1d20+5:20:DC 11:cast" --die 3d4+3:2,2,3 --die 3d4+3:4,3,4 \
  --die "1d20+4:14:AC 15:hit" --die "1d20+5:14:DC 11:cast" \
  --die "1d20+5:19:DC 11:cast" --die 3d4+3:1,4,4 \
  --die "1d20+4:17:AC 15:hit" --die 1d6+2:2 --die 1d4:2 \
  --die "1d20+5:14:DC 11:cast" --die 3d4+3:3,4,3
play morten $D --long-rest --ability STR=8 --item "Rations -1" --armor on --free-armor off
play section $D --file $P/s11-rest.md

# Room 2.4 · Darkmantle, live
play open $D --kind fight --title "Room 2.4 · Darkmantle (CR 1/2)" --where "Floor 2 · room 2.4" --clock 06:20 --foes "$(foes darkmantle)" --doing "fighting the Darkmantle in room 2.4"
play beat $D --round 1 --text "The Darkmantle dropped from the ceiling and missed; Magic Missile hits it for 9 force dmg. It is on 13/22 HP, Morten on 20/20." \
  --line "gm/roll/3: Darkmantle Stealth 12 vs passive Perception 13: seen on the ceiling at E8. Initiative: Darkmantle 21, Morten 17." \
  --line "foe/attack/1: Crush: miss." \
  --line "morten/cast/2: Magic Missile holds: 3 darts, 9 force dmg. Darkmantle 22 → 13 HP." \
  --die 1d20+3:9 --die 1d20+3:18 --die 1d20+4:13 \
  --die "1d20+5:2:AC 15:miss" --die "1d20+5:10:DC 11:cast" --die 3d4+3:1,3,2 \
  --foe "Darkmantle=13/22"
play beat $D --round 2 --text "A natural 20 on its Crush: 10 dmg, and it's stuck to his head. Thunderwave blows it off and kills it. Morten is on 10/20 HP." \
  --line "foe/attack/2: Crush, a natural 20: a crit, 10 bludgeoning dmg, attached (not covering: no Advantage). Morten 20 → 10 HP." \
  --line "morten/cast/3: Thunderwave holds; it fails its CON save: 13 thunder dmg, pushed off. Dead." \
  --die "1d20+5:20:AC 15:hit" --die 2d6+3:3,4 \
  --die "1d20+5:15:DC 11:cast" --die "1d20+1:8:DC 13:fail" --die 2d8:7,6 \
  --hp 10/20 --foe "Darkmantle=0"
play morten $D --xp +100 --coins "+10 GP"
explore 2.4
play section $D --file $P/s12-darkmantle.md
play morten $D --hp 20 --hit-dice "1/3 d6"
play section $D --file $P/s13-short-rest.md --die 1d6+2:3 --die 1d6+2:4

# Room 2.5 · Giant Wolf Spiders, live
play open $D --kind fight --title "Room 2.5 · 3 Giant Wolf Spiders (CR 1/4 each)" --where "Floor 2 · room 2.5" --clock 07:50 --foes "$(foes spiders)" --doing "fighting the wolf spiders in room 2.5"
play beat $D --round 1 --text "One spider rushed the door and missed; Sleep held but it saved. Morten is on 20/20 HP, all three spiders on 11/11." \
  --line "gm/roll/3: Spider Stealth 10 vs passive Perception 13: seen at F3, A1 and D7. Initiative: Spiders 19, Morten 13." \
  --line "foe/attack/1: Spider A runs from D7 to C12 and bites: miss." \
  --line "morten/cast/2: Sleep on C12 holds; Spider A saves (13 vs DC 13)." \
  --die 1d20+7:3 --die 1d20+3:16 --die 1d20+4:9 \
  --die "1d20+5:8:AC 15:miss" --die "1d20+5:18:DC 11:cast" --die "1d20+1:12:DC 13:save" \
  --hp 20/20
play beat $D --round 2 --text "Sleep again, and a natural 20 doubles its radius: the spider in the doorway fails. Morten is on 20/20 HP." \
  --line "foe/attack/1: Spider A bites: miss." \
  --line "morten/cast/3: Sleep, a natural 20: 3 m radius over C12 and E11. A fails (Incapacitated), C saves." \
  --die "1d20+5:3:AC 15:miss" --die "1d20+5:20:DC 11:cast" --die "1d20+1:6:DC 13:fail" --die "1d20+1:17:DC 13:save"
play log $D "rolling round 3"
python3 dnd-crunch/tools/table.py export $D dnd-crunch/web/dev/fixture-live 2>/dev/null
play beat $D --round 3 --text "The spider in the doorway falls unconscious; Scorching Ray burns the one on the ledge for 17 fire dmg. Two left." \
  --line "foe/save/1: Spider A's second save fails: Unconscious, plugging the door." \
  --line "morten/attack/5: Scorching Ray at C on the ledge (half cover, AC 15): rays 1 and 3 hit for 7 and 10 fire dmg, ray 2 misses. C dead." \
  --line "foe/save/1: Spider B's morale holds; it backs out of sight of the door." \
  --die "1d20+1:5:DC 13:fail" \
  --die "1d20+5:16:AC 15:hit" --die 2d6:4,3 --die "1d20+5:5:AC 15:miss" --die "1d20+5:12:AC 15:hit" --die 2d6:5,5 \
  --die "1d20+1:15:DC 10:save" \
  --foe "Giant Wolf Spider C=0"
play beat $D --round 4 --text "Scorching Ray auto-crits the sleeper for 18 fire dmg, but the third spider comes back unseen and bites for 10. Morten is on 10/20 HP." \
  --line "morten/attack/2: Scorching Ray on the sleeper with Advantage: hit, auto-crit, 18 fire dmg. A dead; rays 2 and 3 have no target in sight." \
  --line "foe/attack/3: Spider B, unseen, to C12, bites with Advantage: hit, 5 piercing + 5 poison dmg. Morten 20 → 10 HP." \
  --die "1d20+5 adv:7,10:AC 13:hit" --die 4d6:5,5,4,4 \
  --die "1d20+5 adv:8,17:AC 15:hit" --die 1d4+3:2 --die 2d4:3,2 \
  --hp 10/20 --foe "Giant Wolf Spider A=0"
play beat $D --round 5 --text "Magic Missile for 8 force dmg; the spider's bite misses. It is on 3/11 HP." \
  --line "morten/cast/2: Magic Missile holds: 8 force dmg. Spider B 11 → 3 HP." \
  --line "foe/attack/1: Spider B bites: miss." \
  --die "1d20+5:15:DC 11:cast" --die 3d4+3:2,1,2 --die "1d20+5:7:AC 15:miss" \
  --foe "Giant Wolf Spider B=3"
play beat $D --round 6 --text "Magic Missile scrapes the DC (11) and kills the last spider. Floor 2 is cleared; Morten is on 10/20 HP." \
  --line "morten/cast/2: Magic Missile holds on exactly 11: 11 force dmg. Spider B dead." \
  --die "1d20+5:6:DC 11:cast" --die 3d4+3:3,1,4 \
  --foe "Giant Wolf Spider B=0"
play morten $D --xp +150 --coins "+15 GP"
explore 2.5
sed -i -E 's/^(## Floor 2 · A5 \(savanna, Humans\))$/\1 · CLEARED Month 2 Day 4/' "$D/gm-secrets.md"
play section $D --file $P/s14-spiders.md
play realm $D

# ---- Day 5: home, the trader, downtime ----
play morten $D --item "Rations -1"
play section $D --file $P/s15-travel.md
play morten $D --coins "-62 GP 5 SP" --item "Potion of Healing +1 0.2 kg (Bonus action: regain 2d4+2 HP)" \
  --item "Rations +5" --long-rest --familiar "owl (Fey), summoned Month 2 downtime; scout and Help only" \
  --armor off --light "lamp, about 1 h of oil left in its flask"
play section $D --file $P/s16-shop.md

# ---- the world's turn (realms3's month 2, as map.json reports it) ----
play morten $D --coins "-22 GP" \
  --coins-note "Month 2: lizards +15 GP, floor 2 +70 GP; bought a Potion of Healing (50 GP), incense (10 GP) and 5 rations (2 GP 5 SP); deposited 22 GP. Month 1: started with 47 GP 7 SP 5 CP; sold the Book (+12 GP 5 SP); floor 1 loot +37 GP; deposited 97 GP."
play section $D --file $P/s17-domain.md
play aside $D --file $P/a02-correction.md

# ---- awaiting Month 3's orders ----
play state $D --awaiting orders --prompt "Month 3's orders: where Morten goes, his mission, the tower's action, a gift" \
  --month 3 --day 1 --clock 08:00 --hex B5 --where "the tower (B5)" --doing ""
python3 dnd-crunch/tools/table.py export $D dnd-crunch/web/dev/fixture 2>/dev/null
python3 dnd-crunch/tools/check_table.py $D --docs dnd-crunch/web/dev/fixture --docs dnd-crunch/web/dev/fixture-live
echo "fixture rebuilt: dnd-crunch/web/dev/fixture/ and dnd-crunch/web/dev/fixture-live/"
