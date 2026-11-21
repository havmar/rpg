# Eclipse Phase Second Edition: rulebook text

The English text of the Eclipse Phase 2e core rulebook (errata 1.4) and three supplements, as
Markdown, one file per section.

## Source and licence

- **Game:** Eclipse Phase, created by Rob Boyle and Brian Cross, published by Posthuman Studios,
  who release it under **CC BY-NC-SA 4.0** (Attribution-NonCommercial-ShareAlike).
- **Markdown edition:** Luiz Borges Gomide, https://github.com/eclipsephase/eclipsephase.github.io
  (`src/`), read online at https://eclipsephase.github.io/en/. Copied from commit
  `1be72468599dab5c442758923dcb2b92ed8a530e` (2025-11-12).
- `LICENSE` is the full licence text; `license.md` holds the book's own credits. Anything
  derived from these files is under the same licence and must stay non-commercial and
  credited.

Left out: the art and morph pictures (`.png`), the sample character and character sheet PDFs
(links to them in `05/00-sample-characters.md` and `19/07-character-sheet.md` are broken), the
Portuguese translation and the "buy the book" page. Buy the book: https://eclipsephase.com.

## Where things are

`SUMMARY.md` is the table of contents (every file, in order). By chapter folder:

| Folder | Chapter |
|---|---|
| `01` | Infamy (opening fiction) |
| `02` | Starting Out: what the game is, themes, campaigns, setting overview |
| `03` | Game Mechanics: tests, actions and time, initiative, pools |
| `04` | Making Characters: stats, the 13 creation steps, skills, morphs, traits |
| `05` | Sample Characters (list only; the sheets were PDFs) |
| `06`–`11` | Setting: history, technology, culture, economy, factions, the system gazetteer |
| `12` | Action & Combat: weapons, armour, health, mental health, social actions, movement |
| `13` | The Mesh: hacking, AIs and muses, infomorphs, VR |
| `14` | Psi |
| `15` | Transhuman Tech: ware, nanotech, vehicles, bots |
| `16` | Gear |
| `17` | Running the Game: GM advice, scenarios, campaigns |
| `18` | Threats & X-Risks: NPC rules, the Exsurgent virus, TITAN machines, Firewall |
| `19` | Appendices: glossary, complete mesh-action and morph lists, **rules primer** |
| `SUPP/01-MS` | Multiplicity & Synthesis (forking, group minds) |
| `SUPP/02-CO` | Character Options: life path creation, morph recognition guide, new ware and traits |
| `SUPP/03-FC` | Flexbot Confidential |

The fastest way into the rules is `19/06-rules-primmer.md` (sic). Files hold some HTML (`<blockquote class="table">` and the like) from the
web edition; tables read fine as Markdown. Links between files are relative and work.

## Refreshing

```bash
git clone --depth 1 https://github.com/eclipsephase/eclipsephase.github.io /tmp/ep
cd /tmp/ep/src && find . -name '*.md' ! -name buy-the-book.md -print0 | xargs -0 -I{} cp --parents {} <repo>/eclipse-phase/rulebook/
```

Then drop the `buy-the-book.md` line from `SUMMARY.md` and update the commit above.
