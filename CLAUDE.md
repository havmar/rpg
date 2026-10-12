# RPG table

This repo holds tabletop RPG rulebooks and the campaigns played with them. Claude usually runs
the game (GM) and can also field AI party members alongside the human player.

## Layout

```
CLAUDE.md                  this file: rules for every game
.claude/agents/            subagents shared by all games (rpg-player)
tools/roll.py              dice roller
<system>/                  one folder per RPG system, e.g. godbound/
  CLAUDE.md                system-specific notes: rulebook index, quick rules, house rules
  <Rulebook>.md            the rulebook converted to Markdown
  campaigns/<name>/        one folder per campaign (see below)
```

Adding a new RPG: create `<system>/`, put the rulebook in it, and write a `<system>/CLAUDE.md`
modelled on `godbound/CLAUDE.md`. Don't put game-specific rules in this file.

Rulebooks are large (Godbound is about 1.3 MB). Never read one whole. Use the section index in
the system's CLAUDE.md, then `grep -n` and read only the line range you need.

## Campaign files

Each campaign lives in `<system>/campaigns/<name>/`:

- `party.md`: character sheets for every PC, human and AI. Mark AI PCs with `(AI)`.
- `log.md`: running session log. Append a short summary when each scene ends.
- `gm-secrets.md`: things only the GM knows (villain plans, hidden twists, unrevealed stats).
  AI players must never read this file, and the GM never pastes it to a player agent.
- `world.md` (optional): established places, NPCs and facts revealed to the players.

This is a cloud session, so the container is wiped when the session ends. Commit and push the
campaign folder at natural breaks and at the end of every session, or the game is lost.

## How to run a session

- **The main Claude session is the GM.** The human talks to it directly.
- **AI party members are `rpg-player` subagents** (`.claude/agents/rpg-player.md`), one per AI
  PC. The GM spawns each one once with the Agent tool (`subagent_type: "rpg-player"`,
  `run_in_background: false`). The first prompt holds the system name, the PC's sheet and
  personality, and the opening scene. After that, continue the same agent with SendMessage so
  it remembers the game, and note the agent ID in `log.md`. If the agent is lost (new session,
  context gone), spawn a fresh one and catch it up from `party.md` and `log.md`.
- Each round: the GM narrates. The human states their action. The GM then sends the AI player
  only what its character can perceive (never GM secrets), plus what the human's character
  just said and did, and asks for its action. The GM resolves everything and narrates the
  result.
- Show the AI player's reply to the human in a quoted block with the character's name, e.g.
  `> **Ilsa (AI):** "Cover me, I'm going for the idol."`
- The GM makes every roll, including the AI players' rolls, with `python3 tools/roll.py` and
  shows the result. Never invent a dice result. The human may roll their own physical dice and
  report the number instead.
- Ask the human before big retcons. Otherwise keep things moving: make reasonable calls
  instead of stopping to look up rules.

## Table conventions

- Use metric units in narration (the books use feet and miles; 30 ft ≈ 9 m, 1 mile ≈ 1.6 km).
  Leave rule text as written when quoting it.
- Keep GM narration fairly short (a paragraph or two) and end on a prompt for action.
- Unless the human asks for strict rules, prefer fun and momentum over rules accuracy.
