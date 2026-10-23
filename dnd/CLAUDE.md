# Dungeons & Dragons (5e)

Fifth-edition D&D, played with the core rules (the 5e SRD 5.1 rules, CC-BY 4.0).
Follow the general rules in `../CLAUDE.md` too. This file only covers D&D.

## The rulebook

No rulebook is in this folder. The quick reference below is the whole rules source for now.
If a full rulebook is added later (e.g. `SRD.md`), add a section index here like Godbound's,
and read only the line ranges you need.

## Quick rules

- **Ability modifier:** (score − 10) ÷ 2, rounded down. Scores 8 = −1, 10 = 0, 12 = +1, 14 = +2,
  16 = +3, 18 = +4.
- **Proficiency bonus:** +2 at levels 1–4, +3 at 5–8.
- **Ability check / skill check:** d20 + modifier (+ proficiency if proficient) ≥ DC.
  Easy DC 10, medium 15, hard 20.
- **Advantage / disadvantage:** roll 2d20 and keep the higher (`2d20kh1`) or lower (`2d20kl1`).
- **Attack roll:** d20 + attack bonus ≥ target AC. Natural 20 always hits and doubles the
  damage dice. Natural 1 always misses.
- **Attack bonus:** proficiency + Str (melee) or Dex (finesse or ranged).
- **Saving throw:** d20 + ability modifier (+ proficiency if proficient) ≥ DC.
- **Spell save DC:** 8 + proficiency + spellcasting modifier. **Spell attack:** proficiency +
  spellcasting modifier.
- **Initiative:** d20 + Dex. Highest goes first.
- **Turn:** move (about 9 m / 30 ft), one action, one bonus action (if you have one), and a
  reaction (once per round, on someone else's turn).
- **Common actions:** Attack, Cast a Spell, Dash (extra movement), Dodge (attacks against you
  have disadvantage), Help, Hide, Ready, Search, Use an Object.
- **Damage:** roll the weapon or spell dice, add the modifier. Resistance halves it, vulnerability doubles it.
- **Dying:** at 0 HP you fall unconscious. At the start of each turn roll a death save (d20,
  10+ succeeds, 9 or less fails; natural 20 gets you back to 1 HP; natural 1 counts as two
  failures). Three successes stabilize you; three failures kill you. Damage at 0 HP is a failure.
- **Short rest** (1 hour): spend Hit Dice (roll the die, add Con, regain HP).
- **Long rest** (8 hours, at least 6 of them sleep): regain all HP, half your spent Hit Dice
  (minimum 1), and all spell slots. Only one long rest per 24 hours.
- **Cover:** half cover +2 AC, three-quarters cover +5 AC.

## Monsters used so far

| Monster | AC | HP | Attack |
|---|---:|---:|---|
| Goblin | 15 | 7 (2d6) | Scimitar +4, 1d6+2 slashing. Shortbow +4, 1d6+2 piercing (range 24 m / 80 ft) |
| Goblin boss (Snik Ratchet) | 17 | 21 (6d6) | Two scimitar attacks +4, 1d6+2 slashing each |
| Wolf | 13 | 11 (2d8+2) | Bite +4, 2d4+2 piercing. On a hit, Str DC 11 or knocked prone |

Use the sheet's numbers. Monsters with multiple attacks each roll for their attacks.

## Creating a PC (for this table)

1. **Abilities:** standard array (15, 14, 13, 12, 10, 8), then the racial bonuses.
2. **Race and class:** keep it to the core races and the classes in the sheets below.
3. **HP at level 1:** the class's hit die maximum + Con mod.
4. **AC, attack and spells:** from the armor, weapon and prepared spells on the sheet.
5. **Two skills** from the class list, plus background skills. Note the passive Perception
   (10 + Wis mod, + 2 if proficient).

## Campaigns

Campaign folders go in `campaigns/<name>/`, with the files described in `../CLAUDE.md`.
The campaign's `party.md` holds the PC sheets and the table's setup.

## Table setup for this system

- **Two-person party.** The human only prompts each turn. They don't play a PC.
- **Setup 2 variant:** the main session is the DM. It also plays one PC. The AI player is an
  `rpg-player` subagent with its own PC.
- The DM's own PC knows only what the DM's PC has seen. It does not use `gm-secrets.md` for
  decisions. Treat the DM's knowledge as the DM's, and let the PC act on what it has seen.
- **Narration:** short. One or two paragraphs. End on a prompt for action. Use metric units
  (9 m for 30 ft, 1.5 m for 5 ft, 18 m for 60 ft, 1.6 km for a mile). Quote rule text as written.
- **Dice:** `python3 ../tools/roll.py` (run from the repo root as `python3 tools/roll.py`).
  Advantage is `2d20kh1+mod`, disadvantage is `2d20kl1+mod`. Show results inline.
