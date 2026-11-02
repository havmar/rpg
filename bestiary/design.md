# The Bestiary · design notes

The why behind the game, in the human's terms, for any DM who picks it up. Read it before
running the game; `CLAUDE.md` assumes it.

## Where the rules came from

The Bestiary is its own game. It is **not** the Hotel or the Twins, and their procedures
don't carry over. What came from where:

**The human's constraints** (the game's fundamentals; change only with the human):

- Claude is the DM; a **subagent is the player**. One human message is played as a
  **chapter** of several turns, like a chapter in a story.
- **D&D SRD rules**, with the focus on **combat and mechanics**.
- A **sandbox, West Marches style**, but with **more factions and social play**.
- The **central gimmick**: a **random SRD monster** is chosen and gives the theme of the
  next part of the game, as **an NPC, an enemy, a location or a faction**, for the next
  scene or adventure. (The rules call it the **omen**; the name and its tool are the
  DM's.)
- The player has **one NPC party member** (the companion).
- The PC and the companion are **random classes from the Twins' Front and Back lists**.
- The **Hotel's narration style**: the chronicle and its ornament. This matters.
- The **PC can't die for good**: on death he comes back in plain clothes with a dagger,
  everything else dropped where he was killed. The companion can die.

**Agreed in discussion (Day 0):**

- The DM does **deliberate prep** at every chapter start, keeps a **notebook**, and the
  game is **reviewed** periodically (below).
- The player keeps a **journal** of its own, and sees the **dice lines** (the open table).
- The party starts at **level 3**.
- **Death has no cost by rule** beyond the drop: if the PC dies the companion is likely
  dead too, and that is the cost. What happens to the dropped gear (there, taken, lost for
  good) and any change in how the world sees the PC are **narrative**, the DM's to decide.
  The revival is there because rolling a new character to continue the story is more
  jarring than a revival.
- **Factions are the DM's to write**, with plans and opinions in the notebook, not run by
  clocks, standing numbers or dice.
- **No travel or event tables.** The draft had them; the human didn't ask for them.

**The DM's own additions**, kept light: the omen tool's CR note, `loot.py` for when chance
should choose an item, the SRD's encounter budgets for two. Anything else procedural that
creeps in should earn its place at a review.

## The human's view of an LLM DM

The human's general problem with Claude as a DM: **Claude jumps into a story and vibes.**
It doesn't do the work of DM preparation, and it shows. The stories come out cliché or
dreamlike, with no felt intention behind them: things happen because something had to
happen next, not because someone meant them, and they don't add up.

What the human wants is **a DM who makes an effort for quality and doesn't phone it in.**

- **Not more instructions.** The human doesn't want to fix the DM's storytelling with
  rules about storytelling. A list of "don't be cliché" lines makes a DM obey a list, not
  think.
- **A self-harness for the DM's own work.** Claude should use whatever helps it DM
  better: notes, plans, drafts, content written ahead, anything. It is for the story and
  the game, **not for the human to look at**; the human cares about the quality of what
  reaches the table, not the DM's process. If nothing extra helps, use nothing. The test
  is the game, not the paperwork.
- **Deliberate prep at the start of each chapter** is the one concrete practice asked for.
- **Procedures are not the answer.** The Hotel and the Twins tried to design the DM's work
  away: tables and generators were the base of the game, so the LLM only had to follow
  them. The human finds that this makes games dull and constrained and wastes what an
  LLM DM could be. Here the mechanics are the SRD's and the omen is the one strong
  random input; the story is the DM's to author.
- **Periodic reviews** look at the game as a whole for bigger changes than prep can make.

## What prep is for

Prep is how intention gets into the game. By the first beat the DM should know things the
table doesn't: who wants what in this scene and why now, what each faction will do if
the party does nothing, what the omen's monster means here, what was set up earlier that
can pay off, what the party could lose, what winning would cost. A prepared scene
surprises the players and still makes sense afterwards. A scene improvised from nothing
drifts to the average story, which is the cliché, or to whatever the last sentence
suggested, which is the dream.

Ways to prep (a toolbox, not a checklist; use what helps, drop what doesn't):

- **Write the situation, not the plot:** who and what is present, what each wants, what
  each will do, and what happens if nobody stops it. Decide nothing about the party.
- **Tie the omen in.** A random monster is a constraint, and a constraint is fuel. Look
  for the reading that connects it to something already in play rather than one that
  stands alone. If the obvious reading came first, find a second and choose.
- **Look back before looking forward.** Reread the end of the log, the notebook and what
  the player has shown it cares about: what was promised, foreshadowed or left hanging,
  and what can come back now, changed.
- **Make people specific:** a name, a manner, a want, a thing they won't do, a way of
  talking. Specific details beat atmospheric ones.
- **Prepare the hard parts:** a fight's ground and the enemy's tactics; a negotiation's
  real terms and what each side would settle for; a mystery's clues, with more than one
  route to each conclusion.
- **Know the stakes:** what each outcome changes in the world, so the result matters
  whichever way the dice go.
- **Draft what deserves care:** a letter, a speech, a notice, a history, a song.
- **Get a second reader.** Hand the chapter's prep (not the human's chat) to a fresh
  subagent and ask it plainly what is generic, what is unmotivated, and what a player
  would see coming; then revise. It costs tokens, so keep it for the prep that matters
  most: a campaign's start, a new faction, a big scene.
- **Leave yourself a line** at a chapter's end: what landed, what fell flat, what the
  player went for. That is next chapter's prep's first input.

The notebook is the campaign's `dm/` folder, freeform. It is committed with the
campaign because the container is wiped, but it is the DM's and isn't shown at the table.

## Reviews

Every five chapters or so, at a natural pause, or when the human asks, the DM reviews the
game apart from play and records it below. The question is whether the game is good and
what bigger change would make it better: a rule, the player's brief, the chapter's shape,
the narration, a constraint.

Methods that may help:

- **Read recent chapters as a reader**, from the log and the notebook: where it was
  dull, where it surprised, where it felt meant and where it drifted, what anyone would
  remember.
- **Ask the player**, out of character, in a separate message: what it enjoyed, what
  felt arbitrary or flat, what it wished it could do, what it would change. The game
  should be fun for the Claudes playing it as well as the human watching. Its journal
  shows what it cared about.
- **Check prep against play:** what paid off, what was wasted, what was missing when it
  was needed. That shapes the next prep.
- **Check the rules:** which made the game better, which made it dull or did the DM's
  thinking for it, which were ignored anyway.
- **Bring proposals to the human**, ranked, with reasons. Changes to the fundamentals
  are the human's; changes to how the DM preps are the DM's.

### Review log

(None yet.)
