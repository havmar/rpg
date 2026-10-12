# RPG table

This repo holds tabletop RPG rulebooks and the campaigns played with them. Claude runs the game
(GM) and plays AI party members alongside the human player.

## Layout

```
CLAUDE.md                  this file: rules for every game
.claude/agents/            subagents shared by all games (rpg-gm, rpg-player)
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
  Only the GM reads this file. AI players, and the main session when it is a player, never
  open it, not even to check it before committing.
- `world.md` (optional): established places, NPCs and facts revealed to the players.
- `transcript.md`: everything said at the table, in order: GM replies word for word, plus each
  round's player actions. Written by the main session. Never put GM secrets in it.

This is a cloud session, so the container is wiped when the session ends. **After every GM
reply**, append it (and the player actions that led to it) to `transcript.md`, then commit and
push the campaign folder, so nothing is ever lost. Also commit and push at the end of every
session.

## How to run a session

There are two setups. Use the subagent GM unless the human asks for the other one, and note
the setup at the top of the campaign's `log.md`.

### Setup 1 (default): subagent GM, main session is the AI party member

- The **GM is an `rpg-gm` subagent** (`.claude/agents/rpg-gm.md`). It owns the plot, secrets,
  NPCs and all dice rolls, and writes `gm-secrets.md`, `log.md` and `party.md`.
- The **main session plays one AI PC** and is the human's only contact with the GM. It is a
  player: it knows only what the GM has narrated, and never reads `gm-secrets.md`.
- Start: agree on the system and campaign name with the human, create the campaign folder,
  and make the PCs together (the human's PC and the main session's PC) in `party.md`. Then
  spawn the GM once with the Agent tool (`subagent_type: "rpg-gm"`, `run_in_background: false`),
  telling it the system, campaign folder, tone and length the human wants, and to prepare the
  adventure and narrate the opening scene. Keep the agent ID it returns, and continue that same
  agent with SendMessage every round.
- Each round:
  1. The human states their action (or asks something out of character).
  2. The main session sends the GM one message with the human's words copied exactly, then
     its own PC's action:
     `[HUMAN] <exact words>` and `[AI PC: <name>] <action>`. Never reword, shorten or "fix"
     the human's message.
  3. Append the round's actions and the GM's reply to `transcript.md`, then commit and push
     the campaign folder (`git add <system>/campaigns/<name>`).
  4. Show the GM's reply to the human word for word, under a `**GM:**` label. Then show your
     own PC's in-character reaction, if any, as a quoted block, e.g.
     `> **Ilsa (AI):** "Cover me, I'm going for the idol."`
- Play your PC as a good party member: give it wants and flaws, back up the human, leave them
  the spotlight, and keep your turns short. Don't narrate outcomes or roll dice; the GM does.
- If the human addresses the GM out of character, relay that as `[HUMAN]` too.
- Ending: send `[TABLE] session ending, save your notes`, wait for "notes saved", then commit
  and push the campaign folder (`git add <system>/campaigns/<name>`) without opening
  `gm-secrets.md`. Don't run `git diff` or `git show` on it either, since that prints it.
- If the GM agent is lost (new session, context gone), spawn a fresh `rpg-gm` and tell it to
  take over the existing campaign from its files.

### Setup 2: main session is the GM, AI party members are subagents

- The **main session is the GM** and the human talks to it directly.
- **AI party members are `rpg-player` subagents** (`.claude/agents/rpg-player.md`), one per AI
  PC. Spawn each once with the Agent tool (`subagent_type: "rpg-player"`,
  `run_in_background: false`). The first prompt holds the system name, the PC's sheet and
  personality, and the opening scene. After that, continue the same agent with SendMessage so
  it remembers the game, and note the agent ID in `log.md`. If the agent is lost, spawn a fresh
  one and catch it up from `party.md` and `log.md`.
- Each round: the GM narrates. The human states their action. The GM then sends the AI player
  only what its character can perceive (never GM secrets), plus what the human's character
  just said and did, and asks for its action. The GM resolves everything and narrates the
  result. Show the AI player's reply as a quoted block with the character's name.
- The GM writes all campaign files, appends each narration to `transcript.md`, and commits and
  pushes after every narration.

### Both setups

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
