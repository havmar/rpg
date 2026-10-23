# Eberron

*Eberron* is a D&D campaign setting by Keith Baker: magic is industry, lightning rails cross
the continent of Khorvaire, and the Five Nations are four years into an uneasy peace after the
Last War and the Mourning that destroyed Cyre. Pulp adventure and noir intrigue, with
dragonmarked houses, warforged, changelings and airships.
Follow the general rules in `../CLAUDE.md` too. This file only covers Eberron.

## No rulebook in this folder

There is no converted rulebook here. Play uses **Eberron Lite**, the simple house system
below, loosely based on D&D 5e. The GM runs the setting from general knowledge of Eberron
(Sharn, the Five Nations, the dragonmarked houses, the Lord of Blades, the Aurum, the Dreaming
Dark and so on). When unsure of a canon detail, make a reasonable call and keep it consistent
by noting it in the campaign's `world.md`.

## Eberron Lite rules

- **Abilities:** each PC has six modifiers (Str, Dex, Con, Int, Wis, Cha), from −1 to +3.
- **Checks:** d20 + ability mod, +2 if the PC is trained in a relevant skill, against a DC:
  easy 10, moderate 13, hard 16, very hard 19. Failing forward is fine: a miss can mean
  success with a cost.
- **Advantage / disadvantage:** roll 2d20 and keep the higher / lower. Roll both with
  `python3 tools/roll.py 1d20 1d20` and pick.
- **Combat:** roll initiative (d20 + Dex). On a turn: move about 9 m and take one action.
  Attack: d20 + attack bonus ≥ target AC. Damage is the weapon's dice plus the mod.
  A natural 20 doubles the damage dice.
- **Hit points:** at 0 HP a PC is down and dying. Each turn roll d20: 10+ is a success,
  three successes means stable, three failures means dead. Any healing brings them back up.
  Mooks drop at 0; named foes may surrender or flee instead.
- **Action points (Eberron flavour):** each PC starts every session with 2. Spend one after
  seeing a d20 roll to add 1d6 to it, or to stabilise instantly when dying.
- **Spells:** casters list a few spells. Cantrips are free; others use spell slots, which
  come back after a long rest. A short rest (an hour) lets each PC spend one Hit Die
  (1d8 + Con) to heal.
- **Levelling:** after each finished adventure, PCs gain a level: +1d8 + Con HP and one
  new trick (a spell, a feature, or +1 to a mod, maximum +4). Keep it quick.

## Quick character creation

Pick a race (human, dwarf, elf, half-elf, gnome, halfling, orc/half-orc, warforged,
changeling, shifter, kalashtar), a concept, and a background tied to the Last War or a
dragonmarked house. Assign mods +3, +2, +2, +1, +0, −1. Train four skills. HP = 10 + Con.
AC = 10 + Dex + armour (light +1–2, medium +3–4, heavy +6 with no Dex). Attack bonus =
ability mod + 2. Give each PC one or two signature features and a want, a flaw and a tie to
another PC.

## Running a quick one-shot

- Three or four scenes: hook, investigation/complication, confrontation, aftermath.
- Sharn, the City of Towers, is the best default: vertical districts kilometres high, skycoaches,
  the Watch, crime families (Boromar Clan, Daask, the Tarkanan), and the ruins below.
- Hook ideas: a missing House Cannith artificer and a half-built warforged; a stolen
  schema on a lightning rail; a changeling who wears a dead client's face; a Cyran refugee
  with a map into the Mournland; a skycoach crash that wasn't an accident.

## Campaigns

Campaign folders go in `campaigns/<name>/`, with the files described in `../CLAUDE.md`.
