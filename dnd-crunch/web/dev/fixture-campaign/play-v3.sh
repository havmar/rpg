#!/usr/bin/env bash
# Rebuild the Realms v3 fixture campaign: a fresh world (realms3.py new --seed 7), month 1
# played through tools/table.py as a GM would (every batch "sent" at once: the opening, a
# v3 orders move answered by the orders section, one Delve with a fight told after, the
# world's turn), then the store's view exported for the dev page:
#   web/dev/fixture-campaign-v3/   the campaign (the world, the record)
#   web/dev/fixture-v3/            the end of month 1: awaiting month 2's orders
# Run from anywhere:  bash dnd-crunch/web/dev/fixture-campaign/play-v3.sh
# Inputs are play-v3/ (sections as Markdown, the move, domain.py); play.sh (the v2 fixture)
# is untouched.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"
D=dnd-crunch/web/dev/fixture-campaign-v3
P=dnd-crunch/web/dev/fixture-campaign/play-v3
export TABLE_NOW=2026-10-26T09:00:00Z
t() {  # quiet unless it fails
  local err; err=$(python3 dnd-crunch/tools/table.py "$@" 2>&1 >/dev/null) || { echo "table.py $1: $err" >&2; return 1; }
}
sent() { python3 dnd-crunch/tools/table.py sent "$D" 2>/dev/null; }
play() { t "$@"; sent; }       # one verb, and its batch sent
explore() {  # mark a room of floor 1 explored in gm-secrets.md: explore 1.1 ["note"]
  python3 - "$D/gm-secrets.md" "$1" "${2:-}" <<'PY'
import sys
p, n, note = sys.argv[1:]
s = open(p).read()
s = s.replace(f"| {n} |", f"| {n} ✓{' (' + note + ')' if note else ''} |", 1)
open(p, "w").write(s)
PY
}

# ---- the world, fresh from the engine (deterministic by seed) ----
rm -rf "$D"
python3 dnd-crunch/tools/realms3.py new --seed 7 --campaign "$D" --level 3 >/dev/null
sed -e 's/<Name>/Fixture v3/; s/<N>/7/; s/<name>/fixture-v3/; s/<hex>/B5/' dnd-crunch/templates/realms-rules.md > "$D/rules.md"

# ---- Month 1 · Day 1: the page opens; the player's orders ----
play new $D --campaign fixture-v3 --sheet fresh --file $P/s01-opening.md --month 1 --day 1 --clock 08:00 --hex B5 --where "the tower (B5)"
play wake $D
play state $D --awaiting orders --prompt "Month 1's orders: where Morten goes, his mission, the tower's goal, the purse, a gift"
python3 dnd-crunch/tools/table.py moves $D --file $P/moves-1.json >/dev/null
play log $D "Month 1: the orders"
play section $D --file $P/s02-orders.md --status playing --doing "playing month 1"

# ---- the Delve: floor 1, room 1.1 ----
play morten $D --item "Rations -1" --armor on --free-armor off --light "lamp, lit at 09:00"
play section $D --file $P/s03-delve.md
play morten $D --xp +50 --coins "+5 GP"
explore 1.1
play section $D --file $P/s04-horse.md \
  --die 1d20+2:13 --die 1d20:8 \
  --die "1d20+5:12:AC 10:hit" --die 1d10:7 \
  --die "1d20+6:4:AC 15:miss" \
  --die "1d20+5:9:DC 11:cast" --die 3d4+3:2,3,1
play morten $D --coins "-5 GP" --coins-note "Month 1: room 1.1 +5 GP, deposited." --armor off --light "lamp, about 5 h of oil left"
play section $D --file $P/s05-rest.md

# ---- the world's turn (the engine), then its section ----
python3 dnd-crunch/tools/realms3.py turn --campaign $D --at B5 --delve --deposit 5 \
  --plan "Floor 1 first: safe XP under the wards; the tower keeps its gold and declares no goal yet." >/dev/null
python3 $P/domain.py $D $D/page/domain.md
play section $D --file $D/page/domain.md
rm -f $D/page/domain.md
play realm $D

# ---- awaiting Month 2's orders ----
play state $D --awaiting orders --prompt "Month 2's orders: where Morten goes, his mission, the tower's goal, the purse, a gift" \
  --month 2 --day 1 --clock 08:00 --hex B5 --where "the tower (B5)" --doing ""
python3 dnd-crunch/tools/table.py export $D dnd-crunch/web/dev/fixture-v3 2>/dev/null
python3 dnd-crunch/tools/check_table.py $D --docs dnd-crunch/web/dev/fixture-v3
echo "fixture rebuilt: dnd-crunch/web/dev/fixture-campaign-v3/ and dnd-crunch/web/dev/fixture-v3/"
