# Threats

The opponents `tools/threat.py` rolls from. The GM never chooses who the pair fights; when a
scene calls for opponents, roll them (see `CLAUDE.md`, Opponents). The tool reads the table
below, so keep its columns as they are when adding rows.

**Colour** is the rulebook's threat level (`rulebook/18/05-npc-and-threat-rules.md`): yellow
are thugs, one hit drops them; orange are about one player character each; red can take on
the whole pair; ultraviolet is a boss, run or plan. The book's colours and group sizes assume
four player characters; the tool halves the group size for our two, and a red or
ultraviolet threat always comes alone. `rolled` means the tool
rolls a colour.

**Places** where a threat belongs:

- `civilised`: cities and big stations (Mars, the Moon, Venus, the large habitats)
- `fringe`: remote stations, small outposts, ships, open space
- `ruins`: Earth, the quarantine zones, derelict stations, TITAN sites
- `exoplanet`: other star systems, reached through the wormhole gates
- `mesh`: online, the network and virtual worlds

**Stats** is where the stat block is. Entries marked *house* have no book stats: build them
at the rolled colour from the benchmarks in `18/05` (skills, Durability, armour, Threat
pool), in bodies from `rulebook/04/21-morphs.md` onwards and with gear from `rulebook/12/`
and `rulebook/16/`. Rows added by us are marked *house* in Stats.

| # | Name | Kind | Colour | Number | Places | Stats | What it is |
|---|---|---|---|---|---|---|---|
| 1 | Creeper | exsurgent | ultraviolet | 1 | ruins | 18/14-exsurgent-types.md:26 | A cloud of machines far smaller than ours; cunning, sets traps, adapts |
| 2 | Fractal Troll | exsurgent | red | 1-3 | ruins | 18/14-exsurgent-types.md:86 | Pale, clawed, 2-metre humanoid servants of the TITANs |
| 3 | Jelly | exsurgent | orange | 1-12 | ruins | 18/14-exsurgent-types.md:138 | Huge slimy bubble that oozes through cracks |
| 4 | Mimic Jelly | exsurgent | red | 1-5 | ruins | 18/14-exsurgent-types.md:196 | A jelly that swallows a creature and copies its form, gear and all |
| 5 | Shifter | exsurgent | red | 1-4 | ruins | 18/14-exsurgent-types.md:238 | A robot body turned to reshaping liquid metal |
| 6 | Skrik | exsurgent | yellow | 1-8 | ruins | 18/14-exsurgent-types.md:294 | Tiny screaming copies of their host, coughed out of infected people |
| 7 | Snapper | exsurgent | red | 1-3 | ruins | 18/14-exsurgent-types.md:350 | Robots and vehicles fused into a centipede-like monster |
| 8 | Wastewalker | exsurgent | orange | 4-8 | ruins | 18/14-exsurgent-types.md:406 | Masked cyborg soldiers, the TITANs' elite infantry in the war |
| 9 | Whipper | exsurgent | yellow | 4-24 | ruins | 18/14-exsurgent-types.md:462 | Barrel body on spider legs, with 3-metre whip tentacles |
| 10 | Worm | exsurgent | orange | 1-4 | ruins, civilised | 18/14-exsurgent-types.md:517 | Looks and talks like a person; infected mind, spreads the virus |
| 11 | Exsurgent Virus AI | exsurgent | red | 1 | mesh | 18/09-the-exsurgent-virus.md:41 | The virus as a program, met online or in a hijacked machine |
| 12 | Fetch | TITAN | ultraviolet | 1 | ruins | 18/22-titan-machines-and-minions.md:26 | A cut-down copy of a TITAN mind, riding networks and bodies |
| 13 | Fractal | TITAN | ultraviolet | 1-2 | ruins | 18/22-titan-machines-and-minions.md:81 | Branching "bush robot" that splits into ever smaller pieces |
| 14 | Headhunter | TITAN | orange | 6-12 | ruins | 18/22-titan-machines-and-minions.md:140 | Flying insect drones that take heads to steal the minds inside |
| 15 | Puppet | TITAN | yellow | 1-8 | ruins, civilised | 18/22-titan-machines-and-minions.md:196 | A person whose mind the TITANs took over, still at the controls |
| 16 | Self-Replicating Nanoswarm | TITAN | ultraviolet | 1 | ruins | 18/22-titan-machines-and-minions.md:254 | Thinking, self-copying nanomachines |
| 17 | Warbot | TITAN | red | 1-4 | ruins | 18/22-titan-machines-and-minions.md:312 | A four-armed armoured war machine the size of a tank |
| 18 | Limbwalker | exhuman | yellow | 1-12 | fringe, exoplanet | 18/08-exhumans.md:30 | A creature bred in exhuman experiments, kept as a fighter |
| 19 | Neurode | exhuman | ultraviolet | 1-4 | fringe, exoplanet | 18/08-exhumans.md:79 | Someone who remade themselves into a huge mobile brain |
| 20 | Predator | exhuman | red | 1-6 | fringe, exoplanet | 18/08-exhumans.md:131 | Someone who remade themselves into the perfect hunter |
| 21 | Factor Ambassador | alien | yellow | 1-4 | civilised | 18/15-factors.md:77 | Envoy of the only living alien species in contact; a colony organism |
| 22 | Factor Guardian | alien | orange | 2-8 | civilised | 18/15-factors.md:136 | An ambassador's alien bodyguard |
| 23 | Iktomi Kumobot | machine | red | 1-8 | exoplanet | 18/07-the-iktomi.md:32 | Six-legged guardian robot of a dead alien civilisation |
| 24 | Embedded Ozma Agent | people | red | 1-8 | civilised, exoplanet | 18/18-project-ozma.md:54 | Undercover operative of a secret government black-ops group |
| 25 | Guard Dog | animal | orange | 1-4 | civilised, fringe | 16/14-creatures.md:103 | Smart, trained security dog |
| 26 | Police Baboon | animal | orange | 1-4 | civilised | 16/14-creatures.md:114 | Smart baboon used by Martian police |
| 27 | Rust Hound | animal | orange | 1-4 | civilised, fringe | 16/14-creatures.md:126 | Engineered hound bred for the Martian surface |
| 28 | Lockbot | machine | orange | 1-2 | civilised, fringe | 18/03-security-systems.md:44 | Robot guard bolted beside a door it protects |
| 29 | Street Gang | people | rolled | rolled | civilised, fringe | house | Local toughs defending turf, a racket or a debt |
| 30 | Corporate Security | people | rolled | rolled | civilised | house | Guards, investigators or a response team of a hypercorporation |
| 31 | Mercenaries | people | rolled | rolled | civilised, fringe, ruins, exoplanet | house | Hired guns, often in combat bodies |
| 32 | Crime Syndicate | people | rolled | rolled | civilised, fringe | house | Enforcers of an organised crime family: triads, cartels, mind traffickers |
| 33 | Zealots | people | rolled | rolled | civilised, fringe | house | Believers: anti-technology militants, cults, AI-haters, transformation worshippers |
| 34 | Scavengers | people | rolled | rolled | ruins, fringe, exoplanet | house | Salvagers looting ruins and wrecks, who don't share |
| 35 | Pirates | people | rolled | rolled | fringe | house | Raiders and outlaws between stations |
| 36 | Rival Agents | people | rolled | rolled | civilised, fringe, ruins, exoplanet | house | Spies of a government, corporation or secret group with other aims |
| 37 | Hackers | people | rolled | rolled | mesh, civilised | house | Intruders in the network, or the people behind a hijacked machine |
| 38 | Rogue AI | machine | rolled | 1 | mesh, civilised, fringe | house | A free machine mind with its own agenda, in a robot body or online |
