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

Games so far: `godbound/` (Godbound).

Rulebooks are large. Never read one whole; use the game's own index and `grep -n`.

This is a cloud session and the container is wiped when it ends, so commit and push work as
you go.
