# RPG table

This repo is for trying out tabletop RPGs. Each game is a **self-contained folder** (e.g.
`godbound/`) holding everything it needs: its rulebook, its own `CLAUDE.md` with all the rules
for running it (who is GM, dice, campaign files, conventions), and any agent prompts, tools and
campaigns.

- When the human picks a game, read `<game>/CLAUDE.md` and follow only that. Don't read or
  apply other games' folders; their rules don't carry over.
- To try a new game, create a new top-level folder with its own `CLAUDE.md`. If you want
  something from another game (a dice roller, a play setup), copy it into the new folder and
  adapt it, rather than pointing at the other game's files.
- Don't put game-specific rules in this file.

Games so far: `godbound/` (Godbound), `dnd-crunch/` (D&D 2024, mechanics-only, solo wizard), `bestiary/` (D&D 2024 West Marches sandbox: Claude the DM, a subagent the player, a random monster themes each adventure), `chronicle/` (solo D&D 2024, Claude as player and DM, first-person chronicle), `13th-age/` (13th Age 1e, the Hotel megadungeon for one character, no grid, its own SRD in `13th-age/srd/`), `breach/` (D&D 2024: a county's Company of twenty dungeoneer-and-automaton pairs against monthly breaches of intruding realities; the human plays a role on the ladder, death passes it to a recruit, fights autoplayed by the GM), `breach2/` (Breach moved to an industrial megacity: a Division of ten pairs under a ward mast, breaches rolled every dawn instead of monthly, a gizmo carried by the automaton that sends denizens and breaches home, relics that pass down the seat), `breach3/` (Breach again, without the dungeons: a precinct station of four pairs, breach dice at 6 am and 6 pm, single monsters stranded in the streets and read by CR, the lowest pair that can handle one sent out with a needle to kill it or bring it in; `shift.py` runs the whole day so a small model can GM), `crb/` (Celestial Robot Butler, D&D 2024: a 4 × 4 hex island of sixteen biomes, each with a settlement and a leader; a heavenly robot butler and the human's character, his master, depose the tyrants), `eclipse-phase/` (Eclipse Phase 2e, transhuman horror; rulebook as Markdown in `eclipse-phase/rulebook/`, play setup not yet decided).

Rulebooks are large. Never read one whole; use the game's own index and `grep -n`.

## Shared reference

`reference/` holds sources that belong to no game. A game uses one only when its own
`CLAUDE.md` says so, and can point at it there rather than copying it.

- `reference/srd/` is the D&D SRD 5.2.1 (the 2024 rules) as markdown, one file per entry:
  monsters, spells, magic items, equipment, the rules glossary and the GM's toolbox. Its
  README says where things are and how to refresh it; find an entry by its file name
  (`Monsters/Wolf.md`) and grep for the rest. `Monsters by CR.md` is the table for picking
  a fight's monsters.

This is a cloud session and the container is wiped when it ends, so commit and push work as
you go.

**Heads-up: PRs are squash-merged.** A merged PR lands on `main` as one new commit titled
after the PR (often its first commit), so the session branch's own commits never show up
in `main`'s history. To check whether work reached `main`, compare content
(`git diff origin/main <branch>`, empty means it's all there), not commit hashes or
`git log main..<branch>`. Fetch `origin/main` first; the local `main` can be stale.
