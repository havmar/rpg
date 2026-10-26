// T.panels.story: the Story (table-plan.md 4.2). The stream of sections, oldest at the top,
// under month headers (orders in one line, the sum once the month is over; months before
// the newest fold, "Older months" opens them) and day rows. Each section is the GM's story
// first and its trace folded under it; the world's turn is set apart; asides have a dashed
// rule; fights use T.panels.fightCard when it is there. At the bottom the live card (the
// section being played, from live/* beats) and the activity line, the player's moves not
// yet answered, a "live" button, and the answer box keyed on game/state.awaiting.
//
// The stream is keyed: one wrapper element per item (data-key), reused across renders, so
// open folds and the reader's place survive. The reader's place is kept as an item and its
// offset (T.ui.local 'story.reading'); before each render the first item on screen is
// measured and after it the page is scrolled back by however much that item moved, so a
// section landing (or the live card settling into its section) never moves the reader.
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;
  const ui = T.ui;
  const { esc, icon, fmt } = ui;

  // ---------- words ----------
  const GLYPH = {
    orders: 'flag', travel: 'boots', fight: 'fight', rest: 'bed', shop: 'cart', delve: 'door',
    domain: 'globe', death: 'skull', wrap: 'book', aside: 'speech', opening: 'tower',
  };
  const KIND_WORD = {
    orders: 'The orders', travel: 'The road', fight: 'A fight', rest: 'A rest', shop: 'Shopping',
    delve: 'The delve', domain: "The world's turn", death: 'A death', wrap: 'The wrap-up',
    aside: 'An aside', opening: 'The opening',
  };
  const STOP_WORD = {
    month: "stops at the next month's orders", orders: "stops at each month's orders",
    fight: 'stops before each fight', round: 'stops each round', matters: 'stops when something matters',
  };
  const FIGHTS_WORD = { live: 'fights live, every round', turning: 'fights at the turning points', summary: 'fights as a summary after', line: 'fights in one line' };
  const SCOPES = [
    ['month', 'a month', 'Play the month through'],
    ['matters', 'until something matters', 'Play until something matters'],
    ['fight', 'this fight', 'Play this fight'],
    ['round', 'a round', 'Play one round'],
  ];
  const SCOPE_WORD = { month: 'a month', matters: 'until something matters', fight: 'this fight', round: 'one round', stop: 'stop' };
  const CHOICES = [['fight', 'Fight it', 'fight'], ['avoid', 'Avoid it', 'boots'], ['plan', 'Plan…', 'spark']];
  const CHOICE_WORD = { fight: 'Fight it', avoid: 'Avoid it', plan: 'Plan' };
  const OUTCOME = { cleared: 'good', died: 'bad', fled: 'warn', bypassed: 'muted', going: 'brass' };
  const MISSION_ICON = { delve: 'door', strike: 'sword', rob: 'coins', contact: 'speech', aid: 'hand' };
  const NEAR_HEXES = 6;
  const NEAR_GOALS = 5;   // v3: the tower's goal choices shown before "all N goals"

  // ---------- the panel's own state (survives re-renders) ----------
  let root = null;
  let stream = null;
  let jumpEl = null;
  const A = {}; // the answer box's parts
  let last = null; // the last view rendered
  const folds = new Map(); // details[data-fold] key -> open
  const openMonths = new Set(); // months the viewer opened
  const closedMonths = new Set(); // months the viewer folded
  let olderOpen = false;
  let prevNewest = null;
  let restored = false;
  let following = false;
  let reading = null;
  let saveTimer = 0;
  let scrollFrame = 0;
  let prevKeys = new Set();
  let draft = '';
  let ooc = false;
  let picks = null;
  let picksSig = '';
  let allHexes = false;
  let allGoals = false;
  let lastMode = '';
  let revise = ''; // the id of the sent move the player chose to change (the form shows again)
  // the box's answer to the question showing now: {sig, kind, id} (id null while the write is
  // in flight); kept per viewer so a reload still says the move is with the GM
  let sentFor = (() => { const v = ui.local.get('story.sent', null); return v && typeof v === 'object' && typeof v.sig === 'string' ? v : null; })();

  const saved = ui.local.get('story.reading', null);
  if (U.isObj(saved)) {
    if (Array.isArray(saved.open)) for (const m of saved.open) if (Number.isInteger(m)) openMonths.add(m);
    if (Array.isArray(saved.closed)) for (const m of saved.closed) if (Number.isInteger(m)) closedMonths.add(m);
    olderOpen = saved.older === true;
  }
  {
    const d = ui.local.get('story.draft', '');
    draft = typeof d === 'string' ? d : '';
  }

  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);

  // ---------- the trace ----------
  function lineHtml(l) {
    const who = l.who === 'morten' ? 'morten' : l.who === 'foe' ? 'foe' : 'gm';
    const cls = who === 'foe' ? 'ln them' : who === 'morten' ? 'ln me' : 'ln gm';
    const mk = who === 'morten' ? '✦' : who === 'foe' ? '›' : '·';
    const vh = who === 'morten' ? 'Morten: ' : who === 'foe' ? 'Foe: ' : '';
    const dice = l.dice && l.dice.length ? ` <span class="dice">${ui.dice(l.dice)}</span>` : '';
    return `<div class="${cls}" data-who="${who}"><span class="mk" aria-hidden="true">${mk}</span><span class="tx">${vh ? `<span class="vh">${vh}</span>` : ''}${esc(l.text)}${dice}</span></div>`;
  }

  /** Lines grouped by round (a "Round N" heading where the round changes). */
  function linesHtml(lines) {
    let out = '';
    let round;
    let open = false;
    for (const l of lines) {
      if (l.round !== null && l.round !== round) {
        if (open) out += '</div>';
        round = l.round;
        out += `<div class="round"><h5>Round ${esc(round)}</h5>`;
        open = true;
      }
      out += lineHtml(l);
    }
    if (open) out += '</div>';
    return out;
  }

  function foldHtml(key, summary, body, dflt = false) {
    const st = folds.get(key);
    const open = st === undefined ? dflt : st;
    return `<details class="trace" data-fold="${esc(key)}"${open ? ' open' : ''}><summary>${icon('chev')}${esc(summary)}</summary>${body}</details>`;
  }

  function traceHtml(s) {
    if (!s.trace.length) return '';
    const rounds = new Set(s.trace.map((l) => l.round).filter((r) => r !== null));
    const dice = s.trace.reduce((n, l) => n + l.dice.length, 0);
    const what = rounds.size
      ? `The rounds and the dice (${fmt.plural(rounds.size, 'round')})`
      : `The trace (${fmt.plural(s.trace.length, 'line')}${dice ? `, ${fmt.plural(dice, 'die', 'dice')}` : ''})`;
    return foldHtml(`${s.id}-trace`, what, `<div class="lines">${linesHtml(s.trace)}</div>`);
  }

  // ---------- the GM's story ----------
  function storyHtml(s) {
    const parts = [];
    if (s.headline) parts.push(`<p class="head">${esc(s.headline)}</p>`);
    for (const p of s.prose) parts.push(`<p>${esc(p)}</p>`);
    if (s.bullets.length) {
      parts.push(`<ul class="bullets">${s.bullets.map((b) => `<li>${b.label ? `<b>${esc(b.label)}</b>` : ''}${esc(b.text)}</li>`).join('')}</ul>`);
    }
    return parts.length ? `<div class="story">${parts.join('')}</div>` : '';
  }

  function metaHtml(s, extra = []) {
    const bits = [];
    if (s.clock) bits.push(`<span class="num">${esc(s.clock)}</span>`);
    if (s.where) bits.push(`<span>${esc(s.where)}</span>`);
    for (const x of extra) if (x) bits.push(x);
    return bits.length ? `<p class="meta">${bits.join('<span aria-hidden="true">·</span>')}</p>` : '';
  }

  function glyphFor(s) {
    if (s.kind === 'fight' || s.kind === 'delve') return /room|floor/i.test(s.where || s.title) ? 'door' : GLYPH[s.kind];
    return GLYPH[s.kind] || 'story';
  }

  function resultHtml(s) {
    const a = s.after;
    if (!a) return '';
    const bits = [];
    if (isNum(a.hp)) bits.push(`<span>${icon('heart')}<b>${esc(fmt.hp(a.hp, a.maxHp))}</b></span>`);
    if (isNum(a.xp)) bits.push(`<span>${icon('spark')}<b>${esc(fmt.xp(a.xp))}</b></span>`);
    if (a.coins) bits.push(/^(none|0( GP)?)$/i.test(a.coins) ? '<span>no coins on him</span>' : `<span>${icon('coins')}<b>${esc(a.coins)}</b> on him</span>`);
    if (a.lost.length) bits.push(`<span>lost <b>${esc(a.lost.join(', '))}</b></span>`);
    return bits.length ? `<p class="result">${bits.join('')}</p>` : '';
  }

  function plainSection(s, cls) {
    const label = `${KIND_WORD[s.kind] || 'A section'}: ${s.title || s.headline || ''}`;
    return `<article class="sec ${cls}" data-sec="${esc(s.id)}" data-kind="${esc(s.kind)}" aria-label="${esc(label)}">`
      + `<div class="sec-head">${icon(glyphFor(s))}<div><h3>${esc(s.title || KIND_WORD[s.kind] || 'The story')}</h3>${metaHtml(s)}</div></div>`
      + storyHtml(s)
      + (s.kind === 'death' ? resultHtml(s) : '')
      + traceHtml(s)
      + '</article>';
  }

  function asideHtml(s) {
    const title = s.ooc ? 'The GM, out of game' : s.title && !/^aside$/i.test(s.title) ? s.title : 'The GM, aside';
    const body = [s.headline, ...s.prose].filter(Boolean).map((p) => `<p>${esc(p)}</p>`).join('');
    return `<aside class="sec aside${s.ooc ? ' ooc' : ''}" data-sec="${esc(s.id)}" data-kind="aside" aria-label="${esc(title)}">`
      + `<div class="sec-head">${icon('speech')}<div><h3>${esc(title)}${s.clock ? ` <small>${esc(s.clock)}</small>` : ''}</h3>${body}</div></div>`
      + (s.bullets.length ? `<ul class="bullets">${s.bullets.map((b) => `<li>${b.label ? `<b>${esc(b.label)}</b>` : ''}${esc(b.text)}</li>`).join('')}</ul>` : '')
      + traceHtml(s)
      + '</aside>';
  }

  // ---------- a fight (the fight card when it is there) ----------
  function foeRow(f, closed) {
    const n = f.count > 1 ? ` ×${f.count}` : '';
    const stats = [f.ac !== null ? `AC ${f.ac}` : '', f.speed, ...f.attacks, f.notes].filter(Boolean).join(' · ');
    const hp = closed || f.hp === null
      ? (f.state ? `<span class="hp">${esc(f.state)}</span>` : '')
      : `<span class="hp">${icon('heart', 'bad')}${esc(fmt.hp(f.hp, f.maxHp))}${f.count > 1 ? ' each' : ''}</span>`;
    return `<div class="foe"><b>${esc(f.name)}${esc(n)} <small class="cr">CR ${esc(f.cr || '?')}</small></b>${hp}${stats ? `<span class="stats">${esc(stats)}</span>` : ''}</div>`;
  }

  function hpRow(name, hp, max, word) {
    const v = hp === null && word ? esc(word) : esc(fmt.hp(hp, max).replace(' HP', ''));
    return `<div class="hp"><span class="nm">${esc(name)}</span>${hp === null && word ? `<span class="bar ${word === 'healthy' ? '' : word === 'bloodied' ? 'mid' : 'low'}"><i style="width:${word === 'healthy' ? 100 : word === 'bloodied' ? 50 : 15}%"></i></span>` : ui.bar(hp, max)}<b>${v}</b></div>`;
  }

  function fightFallback(s) {
    const f = s.fight;
    const closed = last && last.state && last.state.table.mode === 'closed';
    const extra = [];
    if (f) {
      extra.push(`<span class="out ${OUTCOME[f.outcome] || ''}">${esc(f.outcome === 'going' ? 'going on' : f.outcome)}</span>`);
      if (f.rounds) extra.push(`<span>${esc(fmt.plural(f.rounds, 'round'))}</span>`);
      if (f.verdict) extra.push(`<span>${esc(f.verdict)}</span>`);
    }
    let body = '';
    if (f && f.foes.length) body += `<div class="foes">${f.foes.map((x) => foeRow(x, closed)).join('')}</div>`;
    if (f && f.hpTrack.length) {
      body += `<div class="hprow" aria-label="HP at the end">${f.hpTrack.map((t) => {
        const hps = t.hp.filter(isNum);
        return hpRow(t.name, hps.length ? hps[hps.length - 1] : null, t.max);
      }).join('')}</div>`;
    }
    body += storyHtml(s);
    body += traceHtml(s);
    if (f) {
      const r = [];
      if (isNum(f.xp)) r.push(`<span>+${esc(fmt.xp(f.xp))}${isNum(f.xpAfter) ? ` → <b>${esc(fmt.n(f.xpAfter))}</b>` : ''}</span>`);
      if (f.loot) r.push(`<span>${esc(f.loot)}</span>`);
      if (s.after && isNum(s.after.hp)) r.push(`<span>HP <b>${esc(fmt.hp(s.after.hp, s.after.maxHp))}</b></span>`);
      r.push(`<span>${f.lost.length ? `lost <b>${esc(f.lost.join(', '))}</b>` : 'nothing lost'}</span>`);
      if (f.potion) r.push('<span>a potion used</span>');
      body += `<p class="result">${r.join('')}</p>`;
    } else body += resultHtml(s);
    return `<article class="sec fight" data-sec="${esc(s.id)}" data-kind="fight" aria-label="${esc(`A fight: ${s.title}`)}">`
      + `<div class="sec-head">${icon(glyphFor(s))}<div><h3>${esc(s.title || 'A fight')}</h3>${metaHtml(s, extra)}</div></div>`
      + body + '</article>';
  }

  function fightCard() {
    const fc = T.panels.fightCard;
    return fc && typeof fc.html === 'function' ? fc : null;
  }

  function fightHtml(s) {
    const fc = fightCard();
    if (fc) {
      const h = U.safe(() => fc.html(s, { live: false }), 'fight card');
      if (typeof h === 'string' && h) return { html: h, bind: typeof fc.bind === 'function' ? (el) => U.safe(() => fc.bind(el), 'fight card bind') : null };
    }
    return { html: fightFallback(s), bind: null };
  }

  // ---------- the world's turn ----------
  function whoInText(text, who) {
    const t = esc(text);
    if (!who) return t;
    const w = esc(who);
    const re = new RegExp(`(the |our ally |our )?${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i');
    const m = re.exec(t);
    const name = who.toLowerCase() === 'tower' ? 'The tower' : who;
    if (!m) return `<span class="who">${esc(name)}</span> · ${t}`;
    return `${t.slice(0, m.index)}<span class="who">${m[0]}</span>${t.slice(m.index + m[0].length)}`;
  }

  function domainHtml(s) {
    const d = s.domain || { plan: [], happened: [], elsewhere: '', tower: [], next: { threats: [], chances: [], open: [] }, income: [], log: [] };
    const report = !!(last && last.state && last.state.table.world === 'report');
    const parts = [];
    if (s.headline || s.prose.length || s.bullets.length) parts.push(storyHtml(s));
    if (d.plan.length) parts.push(`<div class="part"><h4>The plan</h4>${d.plan.map((p) => `<p>${esc(p)}</p>`).join('')}</div>`);
    if (d.happened.length || d.elsewhere) {
      const items = d.happened.map((h) => `<li class="${ui.fac(h.who)}" data-event="${esc(h.n)}"${h.n !== null && s.month !== null ? ` id="ev-${esc(s.month)}-${esc(h.n)}"` : ''}>`
        + `<span class="n" aria-label="${esc(`event ${h.n}`)}">${esc(h.n !== null ? h.n : '·')}</span>`
        + `<span>${h.text ? whoInText(h.text, h.who) : `<span class="who">${esc(h.who)}</span> (${esc(h.label)}: ${esc(h.verb)})`}${(h.from || h.to) ? ` <small class="hexes">${esc([h.from, h.to].filter(Boolean).filter((x, i, a) => a.indexOf(x) === i).join(' → '))}</small>` : ''}</span></li>`);
      if (d.elsewhere) items.push(`<li class="else"><span class="n" aria-hidden="true">·</span><span class="muted"><b>Elsewhere:</b> ${esc(d.elsewhere)}</span></li>`);
      parts.push(`<div class="part"><h4>What happened</h4><ol class="events">${items.join('')}</ol></div>`);
    }
    if (d.tower.length) {
      parts.push(`<div class="part"><h4>The tower now</h4><ul class="delta-rows">${d.tower.map((t) => {
        const same = t.before === t.after;
        return `<li${same ? ' class="same"' : ''}><span class="what">${esc(t.what)}</span><span class="ba num">${same ? `<b>${esc(t.after)}</b> <span class="muted">unchanged</span>` : `${esc(t.before)} <span class="arr" aria-label="to">→</span> <b>${esc(t.after)}</b>`}</span></li>`;
      }).join('')}</ul></div>`);
    }
    const nx = d.next;
    if (nx.threats.length || nx.chances.length || nx.open.length) {
      parts.push(`<div class="part"><h4>Next month</h4><div class="chips">${[
        ...nx.threats.map((x) => ui.chip(x, { kind: 'threat' })),
        ...nx.chances.map((x) => ui.chip(x, { kind: 'chance' })),
        ...nx.open.map((x) => ui.chip(x, { kind: 'open' })),
      ].join('')}</div></div>`);
    }
    if (d.income.length || d.log.length) {
      const body = `<div class="trace-lines">${d.income.length ? `<span class="label">Income</span>${d.income.map((x) => `<span>${esc(x)}</span>`).join('')}` : ''}`
        + `${d.log.length ? `<span class="label">The log</span>${d.log.map((x) => `<span>${esc(x)}</span>`).join('')}` : ''}</div>`;
      parts.push(foldHtml(`${s.id}-log`, "The script's income and log, as it printed them", body, report));
    }
    parts.push(traceHtml(s));
    const extra = [d.happened.length ? `<span>${esc(fmt.plural(d.happened.length, 'event'))} the tower saw</span>` : ''];
    const sm = s.month !== null ? ` <small>end of month ${esc(s.month)}</small>` : '';
    return `<article class="sec world${report ? ' report' : ''}" data-sec="${esc(s.id)}" data-kind="domain" aria-label="${esc(`The world's turn${s.month !== null ? `, month ${s.month}` : ''}`)}">`
      + `<div class="sec-head">${icon('globe')}<div><h3>The world's turn${sm}</h3>${metaHtml({ clock: '', where: '' }, extra)}</div></div>`
      + parts.join('') + '</article>';
  }

  function sectionItem(s) {
    if (s.kind === 'fight') return fightHtml(s);
    if (s.kind === 'domain') return { html: domainHtml(s), bind: null };
    if (s.kind === 'aside') return { html: asideHtml(s), bind: null };
    const cls = s.kind === 'rest' ? 'plain' : s.kind === 'death' ? 'death' : s.kind;
    return { html: plainSection(s, cls), bind: null };
  }

  // ---------- the player's words ----------
  function hexName(view, id) {
    if (!id) return '';
    const st = view.state;
    const h = st && st.awaiting.orders ? st.awaiting.orders.hexes.find((x) => x.id === id) : null;
    if (h) return `${h.name} (${id})`;
    const n = view.realm && view.realm.hexNames[id];
    return n ? `${n} (${id})` : id;
  }

  function moveWords(view, m) {
    if (!m) return '';
    switch (m.kind) {
      case 'say': return m.text;
      case 'play': return m.scope === 'stop' ? `Stop after this${m.text ? `: ${m.text}` : ''}` : `Play ${SCOPE_WORD[m.scope] || ''}${m.text ? `: ${m.text}` : ''}`;
      case 'orders': {
        const bits = [];
        if (m.travel) bits.push(`to ${hexName(view, m.travel)}`);
        const form = view.state && view.state.awaiting.orders;
        const mi = m.mission && form ? form.missions.find((x) => x.type === m.mission.type && x.target === m.mission.target) : null;
        const ac = m.action && form ? form.actions.find((x) => x.action === m.action) : null;
        if (m.mission) bits.push(mi ? mi.label : `${m.mission.type} ${m.mission.target}`);
        if (m.actions !== null) {  // Realms v3: the goal and the purse's options
          if (m.goal) {
            const g = form ? form.goals.find((x) => x.goal === m.goal) : null;
            bits.push(`the goal: ${g ? g.label : m.goal.replace(':', ' ')}`);
          }
          bits.push(m.actions.length ? `the purse: ${m.actions.map((a) => { const f = form ? form.actions.find((x) => x.action === a) : null; return f ? f.label : a.replace(/^--/, ''); }).join(', ')}` : 'the purse saves');
        } else bits.push(m.action ? `the tower: ${ac ? ac.label : m.action.replace(/^(\w+):([^@]*)(?:@(.+))?$/, (x, v, k, h) => `${v} ${k}${h ? ` in ${h}` : ''}`)}` : 'the tower saves');
        if (m.give) bits.push(`give ${fmt.gp(m.give.gp)} to the ${m.give.realm}`);
        return `Orders: ${bits.join(' · ')}${m.plan ? `. ${m.plan}` : ''}`;
      }
      case 'fight': return `${CHOICE_WORD[m.choice] || 'Fight'}${m.text ? `: ${m.text}` : ''}`;
      case 'turn': return m.text;
      case 'table': return 'New table settings';
      case 'take': return m.who === 'you' ? 'I take over Morten.' : 'The GM plays Morten again.';
      default: return m.text;
    }
  }

  function wordsHtml(s) {
    if (!s.words.length) return '';
    return s.words.map((w) => `<div class="you" data-move="${esc(w.move)}"><span class="label">You${s.kind === 'aside' && s.ooc ? ', out of game' : ''}</span><p>${esc(w.text)}</p></div>`).join('');
  }

  function pendingItems(view) {
    const out = [];
    const answered = new Set();
    for (const s of view.sections) for (const id of s.answered) answered.add(id);
    for (const m of view.moves) {
      if (answered.has(m.id)) continue;
      out.push({
        key: `p-${m.id}`,
        html: `<div class="you sent${m.ooc ? ' ooc' : ''}" data-move="${esc(m.id)}"><span class="label">You${m.ooc ? ', out of game' : ''}</span><p>${esc(moveWords(view, m))}</p>`
          + `<span class="st">sent${m.at ? ` ${esc(ui.ago(m.at, view.now))}` : ''} · the GM has it</span></div>`,
      });
    }
    for (const p of view.pending) {
      const failed = p.status === 'failed';
      out.push({
        key: `p-${p.id}`,
        html: `<div class="you ${failed ? 'failed' : 'sending'}${p.move && p.move.ooc ? ' ooc' : ''}" data-move="${esc(p.id)}"><span class="label">You</span><p>${esc(moveWords(view, p.move))}</p>`
          + (failed
            ? `<span class="st bad">not sent: ${esc(p.error)}</span><span class="acts"><button type="button" data-act="retry" data-id="${esc(p.id)}">Send again</button><button type="button" data-act="dismiss" data-id="${esc(p.id)}">Forget it</button></span>`
            : '<span class="st">sending…</span>')
          + '</div>',
      });
    }
    return out;
  }

  // ---------- months and days ----------
  function groupMonths(sections) {
    const map = new Map();
    let cur = null;
    for (const s of sections) {
      const m = s.month !== null ? s.month : cur;
      cur = m;
      if (!map.has(m)) map.set(m, []);
      map.get(m).push(s);
    }
    return Array.from(map.entries())
      .sort((a, b) => (a[0] === null ? -1 : b[0] === null ? 1 : a[0] - b[0]))
      .map(([month, list]) => ({ month, sections: list }));
  }

  function monthSum(view, g, prev) {
    const st = view.state;
    const over = g.sections.some((s) => s.kind === 'domain') || (st && st.month !== null && g.month !== null && g.month < st.month);
    if (!over) return 'in play';
    const afterXp = (list) => {
      for (let i = list.length - 1; i >= 0; i--) if (list[i].after && isNum(list[i].after.xp)) return list[i].after.xp;
      return null;
    };
    const firstXp = (list) => {
      for (const s of list) if (s.after && isNum(s.after.xp)) return s.after.xp;
      return null;
    };
    const bits = [];
    const start = prev ? afterXp(prev.sections) : firstXp(g.sections);
    const end = afterXp(g.sections);
    if (start !== null && end !== null) bits.push(`${fmt.signed(end - start)} XP`);
    const fights = g.sections.filter((s) => s.kind === 'fight').length;
    if (fights) bits.push(fmt.plural(fights, 'fight'));
    const deaths = g.sections.filter((s) => s.kind === 'death').length;
    bits.push(deaths ? fmt.plural(deaths, 'death') : 'no deaths');
    const dom = g.sections.find((s) => s.kind === 'domain' && s.domain);
    const gold = dom ? dom.domain.tower.find((t) => /gold|treasury/i.test(t.what)) : null;
    if (gold && gold.before !== gold.after) bits.push(`tower ${gold.before} → ${gold.after}`);
    return bits.join(' · ');
  }

  function monthHeader(view, g, prev, open, live) {
    const orders = g.sections.find((s) => s.kind === 'orders');
    const line = orders ? orders.headline || orders.title : '';
    const name = g.month === null ? 'Before the months' : `Month ${g.month}`;
    const sum = live ? 'in play' : monthSum(view, g, prev);
    return `<div class="month${open ? '' : ' folded'}" data-act="month" data-m="${esc(g.month === null ? '' : g.month)}" role="button" tabindex="0" aria-expanded="${open}" aria-label="${esc(`${name}${open ? ', open' : ', folded'}`)}">`
      + `<h2>${esc(name)}</h2>${line ? `<span class="orders">${esc(line)}</span>` : ''}<span class="sum">${esc(sum)}</span>`
      + `<span class="fold" aria-hidden="true">${icon('chev')}</span></div>`;
  }

  function dayRow(month, day, first, list) {
    const domain = first && first.kind === 'domain';
    const where = (list.find((s) => s.kind !== 'aside' && s.where) || first || {}).where || '';
    const g = domain ? 'globe' : first && first.kind === 'travel' ? 'boots' : /room|floor/i.test(where) ? 'door' : 'pin';
    const fights = list.filter((s) => s.kind === 'fight').length;
    const rests = list.filter((s) => s.kind === 'rest').length;
    const counts = [fights ? fmt.plural(fights, 'fight') : '', rests ? fmt.plural(rests, 'rest') : ''].filter(Boolean).join(', ');
    const label = domain ? "<b>The month's end</b>" : `<b>Day ${esc(day)}</b>`;
    return { key: `d-${month}-${day}`, html: `<div class="day">${icon(g)}<span>${label}${where && !domain ? ` · ${esc(where)}` : ''}${counts ? ` <span class="muted">· ${esc(counts)}</span>` : ''}</span></div>` };
  }

  // ---------- the live card ----------
  function liveBeats(view) {
    const settled = (b) => view.sections.some((s) => s.seq > b.seq && s.kind !== 'aside' && (!b.section || !b.section.kind || s.kind === b.section.kind));
    const open = view.beats.filter((b) => !settled(b));
    if (!open.length) return [];
    const lb = open[open.length - 1];
    const title = lb.section ? lb.section.title : '';
    return open.filter((b) => !title || !b.section || !b.section.title || b.section.title === title);
  }

  function liveHead(view, beats) {
    const lb = beats[beats.length - 1];
    const sl = view.state && view.state.live;
    const s = (beats.slice().reverse().find((b) => b.section) || {}).section || null;
    return {
      kind: (s && s.kind) || (sl && sl.kind) || 'fight',
      title: (s && s.title) || (sl && sl.title) || 'In progress',
      month: s && s.month !== null ? s.month : sl ? sl.month : null,
      day: s && s.day !== null ? s.day : sl ? sl.day : null,
      where: (s && s.where) || '',
      foes: (s && s.foes) || [],
      round: lb.round,
    };
  }

  function liveHtml(view, beats, h) {
    const fc = fightCard();
    if (fc && h.kind === 'fight') {
      const sec = { id: 'live', kind: 'fight', title: h.title, month: h.month, day: h.day, where: h.where, foes: h.foes };
      const html = U.safe(() => fc.html(sec, { live: true, beats }), 'live fight card');
      if (typeof html === 'string' && html) return { html: `<div class="live-wrap" data-live>${html}</div>`, bind: typeof fc.bind === 'function' ? (el) => U.safe(() => fc.bind(el), 'fight card bind') : null };
    }
    return { html: ownLiveHtml(view, beats, h), bind: null };
  }

  function ownLiveHtml(view, beats, h) {
    const playing = view.state && view.state.status === 'playing';
    const closed = view.state && view.state.table.mode === 'closed';
    const tag = playing
      ? `<span class="live-tag"><i class="pulse" aria-hidden="true"></i>in progress${h.round !== null ? ` · round ${esc(h.round)}` : ''}</span>`
      : `<span class="live-tag paused">paused${h.round !== null ? ` · round ${esc(h.round)}` : ''}</span>`;
    let body = '';
    if (h.kind === 'fight') {
      if (h.foes.length) body += `<div class="foes">${h.foes.map((f) => foeRow(f, closed)).join('')}</div>`;
      const withMorten = beats.slice().reverse().find((b) => b.state.morten);
      const withFoes = beats.slice().reverse().find((b) => b.state.foes.length);
      const hud = view.state && view.state.hud;
      const rows = [];
      if (withMorten) rows.push(hpRow('Morten', withMorten.state.morten.hp, withMorten.state.morten.maxHp));
      else if (hud && hud.hp !== null) rows.push(hpRow('Morten', hud.hp, hud.maxHp));
      if (withFoes) for (const f of withFoes.state.foes) rows.push(hpRow(f.name, closed ? null : f.hp, f.maxHp, f.state));
      if (rows.length) body += `<div class="hprow" aria-label="HP now">${rows.join('')}</div>`;
    }
    let round;
    let open = false;
    let lines = '';
    for (const b of beats) {
      if (b.round !== null && b.round !== round) {
        if (open) lines += '</div>';
        round = b.round;
        lines += `<div class="round"><h5>Round ${esc(round)}</h5>`;
        open = true;
      }
      lines += `<div class="beat" data-beat="${esc(b.id)}">${b.text ? `<p class="bt">${esc(b.text)}</p>` : ''}${b.lines.map(lineHtml).join('')}</div>`;
    }
    if (open) lines += '</div>';
    body += lines ? `<div class="lines">${lines}</div>` : '<p class="muted waiting">The first lines are being rolled.</p>';
    const g = h.kind === 'fight' ? (/room|floor/i.test(h.where || h.title) ? 'door' : 'fight') : GLYPH[h.kind] || 'story';
    return `<article class="sec live ${esc(h.kind)}" data-live aria-label="${esc(`In progress: ${h.title}`)}" aria-live="polite">`
      + `<div class="sec-head">${icon(g)}<div><h3>${esc(h.title)}</h3><p class="meta">${h.where ? `<span>${esc(h.where)}</span><span aria-hidden="true">·</span>` : ''}${tag}</p></div></div>`
      + body + '</article>';
  }

  function activityHtml(view) {
    const st = view.state;
    const since = view.lastBeatAt ? ui.ago(view.lastBeatAt, view.now) : '';
    const items = [`<li>the GM: ${esc(view.activity || (st && st.status === 'playing' ? 'playing' : 'waiting'))}</li>`];
    if (since) items.push(`<li>last line ${esc(since)}</li>`);
    return `<ol class="activity" aria-label="What the GM is doing">${items.join('')}</ol>`;
  }

  // ---------- the stream ----------
  function newestMonth(view, liveH) {
    let m = null;
    for (const s of view.sections) if (s.month !== null && (m === null || s.month > m)) m = s.month;
    if (liveH && liveH.month !== null && (m === null || liveH.month > m)) m = liveH.month;
    return m;
  }

  function isOpen(m, newest) {
    if (m === null || m === newest) return !closedMonths.has(m);
    if (closedMonths.has(m)) return false;
    return olderOpen || openMonths.has(m);
  }

  function buildItems(view) {
    const items = [];
    const beats = liveBeats(view);
    const sl = view.state && view.state.status === 'playing' ? view.state.live : null;
    // a section opened (game/state.live) with no beat yet: its card, waiting for the first line
    const lh = beats.length ? liveHead(view, beats)
      : sl ? { kind: sl.kind || 'fight', title: sl.title || 'In progress', month: sl.month, day: sl.day, where: '', foes: [], round: null } : null;
    const newest = newestMonth(view, lh);
    if (prevNewest !== null && newest !== null && newest > prevNewest) openMonths.add(prevNewest);
    prevNewest = newest;

    const note = ui.note('story', 'The story runs top to bottom: a thick rule starts a month, a thin one a day, each card one thing that happened. The GM\'s words come first; the dice are folded under them. The card with the pulse is being played now.');
    if (note && (view.sections.length || beats.length)) items.push({ key: 'note', html: note });

    const groups = groupMonths(view.sections);
    const folded = groups.filter((g) => !isOpen(g.month, newest)).length;
    if (folded && !olderOpen && groups.some((g) => g.month !== newest && !isOpen(g.month, newest))) {
      items.push({ key: 'older', html: `<button type="button" class="older" data-act="older">Older months <span class="num">(${esc(folded)})</span></button>` });
    }
    let lastDay = null;
    let lastMonth;
    groups.forEach((g, gi) => {
      const open = isOpen(g.month, newest);
      items.push({ key: `m-${g.month}`, html: monthHeader(view, g, gi ? groups[gi - 1] : null, open, false) });
      lastMonth = g.month;
      lastDay = null;
      if (!open) return;
      let day;
      g.sections.forEach((s, i) => {
        if (s.day !== null && s.day !== day && !(s.kind === 'aside' && day !== undefined)) {
          day = s.day;
          const sameDay = [];
          for (let j = i; j < g.sections.length && (g.sections[j].day === day || g.sections[j].day === null); j++) sameDay.push(g.sections[j]);
          items.push(dayRow(g.month, day, s, sameDay));
          lastDay = day;
        }
        // the player's words first, then the section that answered them (as in Dream)
        const w = wordsHtml(s);
        if (w) items.push({ key: `w-${s.id}`, html: w });
        const it = sectionItem(s);
        items.push({ key: s.id, html: it.html, bind: it.bind, sec: s });
      });
    });

    if (lh) {
      if (lh.month !== lastMonth && lh.month !== null) {
        items.push({ key: `m-${lh.month}`, html: monthHeader(view, { month: lh.month, sections: [] }, null, true, true) });
        lastDay = null;
      }
      if (lh.day !== null && lh.day !== lastDay) items.push(dayRow(lh.month, lh.day, { kind: lh.kind, where: lh.where }, [{ kind: lh.kind, where: lh.where }]));
      const li = liveHtml(view, beats, lh);
      items.push({ key: 'live', html: li.html, bind: li.bind });
    }
    if (lh || (view.state && view.state.status === 'playing')) items.push({ key: 'activity', html: activityHtml(view) });

    if (!view.sections.length && !lh) {
      const why = view.db === 'none' ? 'Nothing to show: there is no table store in this view.'
        : view.opening ? 'Opening the table…'
          : 'The GM has not written the first section yet. It appears here as soon as it is written, without a reload.';
      items.push({ key: 'empty', html: `<p class="empty">${esc(why)}</p>` });
    }
    for (const p of pendingItems(view)) items.push(p);
    return items;
  }

  function restoreFolds(el) {
    for (const d of el.querySelectorAll('details[data-fold]')) {
      const st = folds.get(d.dataset.fold);
      if (st !== undefined && d.open !== st) d.open = st;
    }
  }

  function reconcile(items) {
    const have = new Map();
    for (const el of Array.from(stream.children)) if (el.dataset && el.dataset.key) have.set(el.dataset.key, el);
    const added = [];
    let prev = null;
    for (const it of items) {
      let el = have.get(it.key);
      if (el) have.delete(it.key);
      else {
        el = document.createElement('div');
        el.className = 'it';
        el.dataset.key = it.key;
        added.push(it.key);
      }
      if (ui.put(el, it.html)) {
        restoreFolds(el);
        if (it.bind) it.bind(el);
      }
      const next = prev ? prev.nextSibling : stream.firstChild;
      if (next !== el) stream.insertBefore(el, next);
      prev = el;
    }
    for (const el of have.values()) el.remove();
    return added;
  }

  // ---------- the reader's place ----------
  const visible = () => !!root && root.getClientRects().length > 0 && getComputedStyle(root).display !== 'none';
  function topInset() {
    const n = document.getElementById('now');
    return n ? Math.max(0, n.getBoundingClientRect().bottom) : 0;
  }
  function bottomInset() {
    const t = document.getElementById('tabs');
    return t && t.getClientRects().length && getComputedStyle(t).display !== 'none' ? t.getBoundingClientRect().height : 0;
  }

  function anchorNow() {
    if (!stream) return null;
    const inset = topInset();
    for (const el of stream.children) {
      const r = el.getBoundingClientRect();
      if (r.height && r.bottom > inset + 1) return { el, key: el.dataset.key, top: r.top };
    }
    return null;
  }

  function remember() {
    if (!restored || !visible()) return;
    const a = anchorNow();
    if (!a) return;
    reading = { key: a.key, top: Math.round(a.top), y: Math.round(window.scrollY), open: Array.from(openMonths), closed: Array.from(closedMonths), older: olderOpen };
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      saveTimer = 0;
      ui.local.set('story.reading', reading);
    }, 300);
  }

  function keyEl(key) {
    return stream ? Array.from(stream.children).find((e) => e.dataset.key === key) || null : null;
  }

  function scrollToEl(el, top) {
    const want = top === undefined ? topInset() + 8 : top;
    window.scrollBy(0, el.getBoundingClientRect().top - want);
  }

  function firstPlace() {
    const sv = U.isObj(saved) ? saved : null;
    const el = sv && typeof sv.key === 'string' ? keyEl(sv.key) : null;
    if (el && isNum(sv.top)) scrollToEl(el, sv.top);
    else {
      const target = keyEl('live') || (() => {
        const secs = Array.from(stream.children).filter((e) => /^s/.test(e.dataset.key));
        return secs[secs.length - 1] || null;
      })();
      if (target) scrollToEl(target);
    }
    restored = true;
    remember();
  }

  function follow() {
    const el = keyEl('live');
    if (!el) {
      following = false;
      return;
    }
    const act = keyEl('activity');
    const r = (act || el).getBoundingClientRect();
    const want = window.innerHeight - bottomInset() - 16;
    if (r.bottom > want || r.bottom < topInset()) window.scrollBy(0, r.bottom - want);
  }

  function stopFollowing() {
    following = false;
  }

  function updateJump() {
    if (!jumpEl) return;
    let show = '';
    if (visible()) {
      const live = keyEl('live');
      const vh = window.innerHeight - bottomInset();
      if (live) {
        const r = live.getBoundingClientRect();
        if (!following && (r.top > vh - 40 || r.bottom < topInset())) show = 'live';
      } else {
        const secs = Array.from(stream.children).filter((e) => /^s/.test(e.dataset.key));
        const lastSec = secs[secs.length - 1];
        if (lastSec && lastSec.getBoundingClientRect().top > vh + 40) show = 'newest';
      }
    }
    const html = show === 'live' ? `<i class="pulse" aria-hidden="true"></i>live${icon('chev', 'down')}` : show === 'newest' ? `newest${icon('chev', 'down')}` : '';
    jumpEl.hidden = !show;
    jumpEl.dataset.mode = show;
    ui.put(jumpEl, html);
  }

  function onScroll() {
    if (scrollFrame) return;
    scrollFrame = requestAnimationFrame(() => {
      scrollFrame = 0;
      remember();
      updateJump();
    });
  }

  // ---------- the answer box ----------
  /** The box's face: the GM's question, or 'sent' while the player's answer to it is with
   * the GM (unless they chose to change it). */
  /** What the GM is asking now, as a key: a new question (or the same asked again later in
   * the month) gets a fresh form. */
  function sigOf(view, mode) {
    const st = view.state;
    const a = st ? st.awaiting : null;
    return [mode, a && a.kind, a && a.prompt, st && st.month, st && st.day, a && a.fight && a.fight.title].join('|');
  }

  /** The player's answer to the question showing now while it waits for the GM (in moves,
   * or being written), else null. */
  function withGm(view, mode = modeOf(view)) {
    if (!sentFor || mode === 'closed' || mode === 'playing' || sentFor.sig !== sigOf(view, mode)) return null;
    if (!sentFor.id) {
      const p = view.pending.filter((x) => x.status === 'sending' && x.move && x.move.kind === sentFor.kind).pop();
      return p ? p.move : null;
    }
    const m = view.moves.find((x) => x.id === sentFor.id);
    if (m) return m;
    const p = view.pending.find((x) => x.id === sentFor.id && x.status === 'sending');
    return p ? p.move : null;
  }

  function faceOf(view, mode) {
    const w = withGm(view, mode);
    if (!w || revise === w.id) return mode;
    return 'sent';
  }

  /** A send from the box that answers the question showing now. */
  function sendAnswer(view, mode, kind, fields) {
    const sig = sigOf(view, mode);
    sentFor = { sig, kind, id: null };
    revise = '';
    const p = sendMove(kind, fields);
    p.then((res) => {
      if (sentFor && sentFor.sig === sig && !sentFor.id) {
        sentFor = { sig, kind, id: res.id };
        ui.local.set('story.sent', sentFor);
      }
      T.app.render();
    }, () => {
      if (sentFor && sentFor.sig === sig) sentFor = null;
      T.app.render();
    });
    return p;
  }

  const CHANGE_WORD = { orders: 'Change the orders', fight: 'Change your call', turn: 'Change the turn', word: 'Something else' };

  function sentForm(view, mode) {
    const w = withGm(view, mode);
    return `<div class="row sent-row" data-row="sent"><span class="label">${icon('hand')}With the GM</span>`
      + `<p class="sent-words">${esc(w.kind === 'orders' ? 'Your orders are sent (above): the GM plays the month from them.' : w.kind === 'fight' ? 'Your call is sent (above): the GM plays the fight from it.' : w.kind === 'turn' ? "Morten's turn is sent (above): the GM resolves it." : 'Your word is sent (above): the GM plays on from it.')}</p>`
      + `<div class="seg"><button type="button" data-act="revise" data-id="${esc(w.id)}">${esc(CHANGE_WORD[mode] || 'Something else')}</button></div></div>`;
  }

  function modeOf(view) {
    const st = view.state;
    if (view.db !== 'ok' || !view.canWrite || !st || st.status === 'ended') return 'closed';
    if (st.status === 'playing') return 'playing';
    const a = st.awaiting;
    if (a.kind === 'orders' && a.orders) return 'orders';
    if (a.kind === 'fight') return 'fight';
    if (a.kind === 'turn') return 'turn';
    return 'word';
  }

  function closedWhy(view) {
    if (view.db === 'none') return 'No table store in this view: nothing written here would reach the GM.';
    if (view.db === 'error') return 'The table stopped updating. Reload the page to reconnect.';
    if (view.opening) return 'Opening the table…';
    if (!view.canWrite) return 'You are watching this table: playing needs edit access.';
    if (!view.state) return 'The answer box opens when the GM sets the table.';
    if (view.state.status === 'ended') return 'The campaign has ended.';
    return '';
  }

  function ensurePicks(view, mode) {
    const st = view.state;
    const a = st ? st.awaiting : null;
    const sig = [mode, a && a.prompt, st && st.month, a && a.fight && a.fight.title].join('|');
    if (picks && sig === picksSig) return;
    picksSig = sig;
    allHexes = false;
    allGoals = false;
    const hexes = a && a.orders ? a.orders.hexes : [];
    const here = st && hexes.find((h) => h.id === st.hex);
    picks = { travel: here ? here.id : hexes.length ? hexes[0].id : null, mission: null, action: null, actions: [], goal: null, give: null, gp: '', choice: 'fight' };
  }

  function holderOf(view, id) {
    const h = view.realm ? view.realm.hexes.find((x) => x.id === id) : null;
    return h ? h.holder : null;
  }

  function treasury(view) {
    const t = view.realm ? view.realm.factions.find((f) => f.tower) : null;
    return t ? t.treasury : null;
  }

  function kindGlyph(view, label) {
    const kinds = view.realm ? view.realm.kinds : {};
    for (const k of Object.keys(kinds)) if (label.toLowerCase().includes(k.toLowerCase()) && kinds[k].glyph) return kinds[k].glyph;
    return /raise/i.test(label) ? 'spark' : /repair|mend/i.test(label) ? 'heart' : /^back/i.test(label) ? 'hand' : /^hinder/i.test(label) ? 'off' : /^set/i.test(label) ? 'flag' : '';
  }
  const GOAL_ICON = { take: 'hex', ally: 'hand', topple: 'crown', drop: 'off' };

  function missionsFor(o, hex) {
    const anyHex = o.missions.some((m) => m.hex);
    return anyHex ? o.missions.filter((m) => m.hex === hex) : o.missions;
  }

  const pressed = (b) => ` aria-pressed="${b ? 'true' : 'false'}"`;

  function ordersForm(view) {
    const o = view.state.awaiting.orders;
    const rows = [];
    // travel
    const hexes = o.hexes.slice().sort((a, b) => (a.days ?? 99) - (b.days ?? 99));
    const shown = allHexes ? hexes : hexes.filter((h, i) => i < NEAR_HEXES || h.id === picks.travel);
    const hexBtn = (h) => {
      const holder = holderOf(view, h.id);
      const sw = holder ? `<span class="sw ${ui.fac(holder)}" aria-hidden="true"></span>` : icon('hex');
      return `<button type="button" data-act="pick" data-f="travel" data-v="${esc(h.id)}"${pressed(picks.travel === h.id)}>${sw}<span>${esc(h.name)} <small>${esc(h.id)}${h.days !== null ? ` · ${esc(fmt.plural(h.days, 'day'))}` : ''}</small></span></button>`;
    };
    rows.push(`<div class="row" data-row="travel"><span class="label">Travel: end the month in</span><div class="pick">${shown.map(hexBtn).join('')}`
      + (hexes.length > shown.length ? `<button type="button" data-act="all-hexes">${icon('hex')}<span>all ${esc(hexes.length)} hexes <small>farther away</small></span></button>` : '')
      + '</div></div>');
    // mission
    const ms = missionsFor(o, picks.travel);
    rows.push(`<div class="row" data-row="mission"><span class="label">Mission there</span><div class="pick">`
      + `<button type="button" data-act="pick" data-f="mission" data-v=""${pressed(picks.mission === null)}>none</button>`
      + ms.map((m) => {
        const i = o.missions.indexOf(m);
        return `<button type="button" data-act="pick" data-f="mission" data-v="${i}"${pressed(picks.mission === i)}>${MISSION_ICON[m.type] ? icon(MISSION_ICON[m.type]) : ''}<span>${esc(m.label)}</span></button>`;
      }).join('')
      + (ms.length ? '' : '<span class="muted small">nothing to do there but travel</span>')
      + '</div></div>');
    const v3 = o.version === 3;
    // v3: the tower's goal (kept, a new one, or dropped)
    if (v3) {
      const near = o.goals.filter((g, i) => i < NEAR_GOALS || g.goal === picks.goal || g.kind === 'drop');
      const shownGoals = allGoals ? o.goals : near;
      const keep = o.goal
        ? `keep <i>${esc(o.goal.text)}</i> <small>${esc(`${o.goal.marks} of ${o.goal.size !== null ? o.goal.size : '?'} marks`)}</small>`
        : 'none <small>no goal yet</small>';
      rows.push(`<div class="row" data-row="goal"><span class="label">The tower's goal</span><div class="pick">`
        + `<button type="button" data-act="pick" data-f="goal" data-v=""${pressed(picks.goal === null)}>${icon('flag')}<span>${keep}</span></button>`
        + shownGoals.map((g) => `<button type="button" data-act="pick" data-f="goal" data-v="${esc(g.goal)}"${pressed(picks.goal === g.goal)}>${icon(GOAL_ICON[g.kind] || 'flag')}<span>${esc(g.label)}</span></button>`).join('')
        + (o.goals.length > shownGoals.length ? `<button type="button" data-act="all-goals">${icon('more')}<span>all ${esc(o.goals.length)} goals <small>every hex, ally and topple</small></span></button>` : '')
        + '</div>'
        + (o.goal ? '<p class="muted small">A new goal drops the old one and loses its marks.</p>' : '')
        + '</div>');
    }
    // the tower's action (v3: the purse, several at once)
    const gold = o.funds && o.funds.treasury !== null ? o.funds.treasury : treasury(view);
    const isPicked = (i) => (v3 ? picks.actions.includes(i) : picks.action === i);
    const actBtn = (a, i, ok) => {
      const g = kindGlyph(view, a.label);
      return `<button type="button" data-act="pick" data-f="action" data-v="${i}"${pressed(isPicked(i))}${ok ? '' : ' disabled title="the tower cannot afford it"'}>${g ? icon(g) : ''}<span>${esc(a.label)}${a.cost !== null && a.cost > 0 ? ` <small>${esc(fmt.gp(a.cost))}</small>` : ''}</span></button>`;
    };
    const can = [];
    const cannot = [];
    o.actions.forEach((a, i) => {
      const ok = a.affordable !== null ? a.affordable : gold !== null && a.cost !== null ? a.cost <= gold : true;
      (ok ? can : cannot).push(actBtn(a, i, ok));
    });
    const least = o.actions.filter((a, i) => a.cost !== null).reduce((m, a) => (m === null || a.cost < m ? a.cost : m), null);
    const spent = v3 ? picks.actions.reduce((s, i) => s + ((o.actions[i] && o.actions[i].cost) || 0), 0) : 0;
    rows.push(`<div class="row" data-row="action"><span class="label">${v3 ? 'The purse' : "The tower's action"}${gold !== null ? ` <small class="muted">· ${esc(fmt.gp(gold))} in the treasury${spent ? `, ${esc(fmt.gp(spent))} picked` : ''}</small>` : ''}</span><div class="pick">`
      + `<button type="button" data-act="pick" data-f="action" data-v=""${pressed(v3 ? !picks.actions.length : picks.action === null)}>save <small>no action</small></button>`
      + can.join('')
      + '</div>'
      + (cannot.length ? foldHtml('orders-cannot', `${fmt.plural(cannot.length, 'action')} the tower cannot afford yet${least !== null ? ` (from ${fmt.gp(least)})` : ''}`, `<div class="pick">${cannot.join('')}</div>`) : '')
      + '</div>');
    // give
    rows.push(`<div class="row" data-row="give"><span class="label">Give</span><div class="pick">`
      + `<button type="button" data-act="pick" data-f="give" data-v=""${pressed(picks.give === null)}>nothing</button>`
      + o.realms.map((r) => `<button type="button" data-act="pick" data-f="give" data-v="${esc(r)}"${pressed(picks.give === r)}><span class="sw ${ui.fac(r)}" aria-hidden="true"></span>${esc(r)}</button>`).join('')
      + '</div>'
      + (picks.give ? `<label class="gp"><span>to the ${esc(picks.give)}:</span><input type="number" inputmode="numeric" min="1" step="1" data-a="gp" aria-label="${esc(`GP to give the ${picks.give}`)}"><span>GP</span></label>` : '')
      + '</div>');
    return rows.join('');
  }

  function playRow(label) {
    return `<div class="row" data-row="play"><span class="label">${esc(label)}</span><div class="seg">${SCOPES.map(([scope, word, title]) => `<button type="button" data-act="play" data-scope="${scope}" title="${esc(title)}">${icon('play')}${esc(word)}</button>`).join('')}</div></div>`;
  }

  function fightForm(view) {
    const f = view.state.awaiting.fight;
    const closed = view.state.table.mode === 'closed';
    let out = '';
    if (f) {
      out += `<div class="row"><span class="label">${esc(f.title || 'Before the fight')}${f.difficulty ? ` · ${esc(f.difficulty)}` : ''}${isNum(f.xp) ? `, ${esc(fmt.xp(f.xp))}` : ''}</span>`;
      if (f.foes.length) out += `<div class="foes">${f.foes.map((x) => foeRow(x, closed)).join('')}</div>`;
      out += '</div>';
    }
    out += `<div class="row" data-row="choice"><span class="label">Your call</span><div class="seg">${CHOICES.map(([c, w, g]) => `<button type="button" data-act="choice" data-v="${c}"${pressed(picks.choice === c)}>${icon(g)}${esc(w)}</button>`).join('')}</div></div>`;
    return out;
  }

  function turnForm(view) {
    const t = view.state.awaiting.turn || { board: '', lines: [], options: [] };
    let out = '';
    const board = t.board ? t.board.split('\n').filter((x) => x.trim()) : [];
    if (board.length || t.lines.length) {
      out += `<div class="row"><span class="label">The board</span><div class="board">${board.map((x) => `<p>${esc(x)}</p>`).join('')}${t.lines.map((x) => `<p class="muted">${esc(x)}</p>`).join('')}</div></div>`;
    }
    let opts = t.options.slice();
    const mo = view.morten;
    if (!opts.length && mo) {
      opts = mo.spells.filter((s) => !s.lost && s.prepared).map((s) => s.name).concat(mo.attacks.map((a) => a.name).filter((n) => !mo.spells.some((s) => s.name === n)));
    }
    const lost = new Set(mo ? mo.spells.filter((s) => s.lost).map((s) => s.name) : []);
    if (opts.length) {
      out += `<div class="row"><span class="label">Drop a spell or an attack in</span><div class="pick">${opts.map((x) => {
        const sp = mo ? mo.spells.find((s) => s.name === x) : null;
        return `<button type="button" class="spell" data-act="insert" data-v="${esc(x)}"${lost.has(x) ? ' disabled title="lost until a Long Rest"' : ''}>${esc(x)}${sp && sp.dc !== null ? ` <small>DC ${esc(sp.dc)}</small>` : ''}</button>`;
      }).join('')}</div></div>`;
    }
    return out;
  }

  function playingForm(view) {
    const st = view.state;
    const fight = (st.live && st.live.kind === 'fight') || liveBeats(view).some((b) => b.section && b.section.kind === 'fight');
    const take = st.table.who === 'you'
      ? `<button type="button" data-act="take" data-who="dm">${icon('hand')}Hand Morten back</button>`
      : `<button type="button" data-act="take" data-who="you">${icon('hand')}Take over Morten</button>`;
    const isStop = (m) => !!m && m.kind === 'play' && m.scope === 'stop';
    const asked = view.moves.some(isStop) || view.pending.some((x) => x.status === 'sending' && isStop(x.move));
    const stop = asked
      ? `<button type="button" class="stop" data-act="stop" aria-pressed="true" disabled title="the GM reads it at the next stop point">${icon('stop')}${fight ? 'Stopping after this fight' : 'Stopping at the next stop'}</button>`
      : `<button type="button" class="stop" data-act="stop">${icon('stop')}${fight ? 'Stop after this fight' : 'Stop at the next stop'}</button>`;
    return `<div class="row" data-row="playing"><span class="label">A word now</span><div class="seg">${stop}${take}</div></div>`;
  }

  function formHtml(view, mode, face) {
    if (face === 'sent') return sentForm(view, mode);
    if (mode === 'orders') return ordersForm(view);
    if (mode === 'fight') return fightForm(view) + playRow('Or let the GM play');
    if (mode === 'turn') return turnForm(view);
    if (mode === 'playing') return playingForm(view);
    if (mode === 'word') return playRow('Play');
    return '';
  }

  const PLACEHOLDER = {
    orders: 'Why, in a line (it goes in The plan).',
    fight: "A plan, with Plan…: 'Web the doorway first, then Sleep whatever is stuck.'",
    turn: "Morten's turn: tap a spell above, then say at whom and where he moves.",
    playing: "A steer for the GM ('leave the sleeping boar, go round'), read at the next stop point.",
    word: "Morten's words, or a question for the GM.",
    sent: 'More words for the GM, read with your move.',
    closed: '',
  };
  const HINT = {
    orders: 'checked by the engine before anything moves',
    fight: 'the GM plays the fight from your call',
    turn: 'an illegal move comes back with why',
    playing: 'read at the next fight, day or world\'s turn',
    word: "sent as Morten's words",
    sent: 'read with your move',
  };

  function sendHtml(view, mode) {
    const busy = view.sending || !view.canWrite;
    const text = draft.trim();
    const hint = ooc ? 'out of game: answered here as an aside' : HINT[mode] || '';
    let primary;
    let second = '';
    if (ooc) primary = `<button type="button" class="primary" data-act="say"${busy || !text ? ' disabled' : ''}>Ask the GM</button>`;
    else if (mode === 'orders') primary = `<button type="button" class="primary" data-act="send"${busy || !picks.travel ? ' disabled' : ''}>Send the orders</button>`;
    else if (mode === 'fight') {
      const w = picks.choice === 'plan' ? 'Send the plan' : `Send: ${CHOICE_WORD[picks.choice]}`;
      primary = `<button type="button" class="primary" data-act="send"${busy || (picks.choice === 'plan' && !text) ? ' disabled' : ''}>${esc(w)}</button>`;
    } else if (mode === 'turn') primary = `<button type="button" class="primary" data-act="send"${busy || !text ? ' disabled' : ''}>Send the turn</button>`;
    else primary = `<button type="button" class="primary" data-act="say"${busy || !text ? ' disabled' : ''}>Send</button>`;
    if (!ooc && ['orders', 'fight', 'turn'].includes(mode)) second = `<button type="button" class="second" data-act="say"${busy || !text ? ' disabled' : ''} title="send the text alone, as Morten's words">Say it</button>`;
    return `<button type="button" class="toggle ooc" data-act="ooc"${pressed(ooc)} title="a question for the GM, not Morten's words">out of game</button>`
      + `<span class="hint">${esc(hint)}</span><span class="btns">${second}${primary}</span>`;
  }

  function myOpenMove(view) {
    const w = view.wake;
    if (!w.move) return null;
    const m = view.moves.find((x) => x.id === w.move);
    const p = view.pending.find((x) => x.id === w.move);
    return m || p ? { id: w.move, at: (m && m.at) || (p && p.at) || '' } : null;
  }

  function statusHtml(view) {
    const st = view.state;
    const parts = [];
    const sep = '<span class="sep" aria-hidden="true">·</span>';
    if (!st) parts.push(`<span>${esc(closedWhy(view) || 'The answer box opens when the table does.')}</span>`);
    else if (st.status === 'ended') parts.push('<span>The campaign has ended</span>');
    else if (st.status === 'playing') {
      parts.push(`<span class="who-move gm"><i class="pulse" aria-hidden="true"></i>${st.table.who === 'you' ? 'The GM is playing; Morten is yours' : 'The GM is playing Morten'}</span>`);
      parts.push(`<span>${esc(STOP_WORD[st.table.stop] || '')}</span>`);
      parts.push(`<span>${esc(FIGHTS_WORD[st.table.fights] || '')}</span>`);
    } else if (withGm(view) && revise !== withGm(view).id) {
      parts.push(`<span class="who-move gm"><i class="pulse" aria-hidden="true"></i>The GM's move</span>`);
      parts.push(`<span>${esc(withGm(view).kind === 'orders' ? 'your orders are with the GM' : 'your word is with the GM')}</span>`);
    } else {
      parts.push(`<span class="who-move mine">${icon('hand')}Your move</span>`);
      if (st.awaiting.prompt) parts.push(`<span>${esc(st.awaiting.prompt)}</span>`);
    }
    const failed = view.pending.find((p) => p.status === 'failed');
    const sending = view.pending.find((p) => p.status === 'sending');
    const open = myOpenMove(view);
    const w = view.wake;
    if (failed) parts.push(`<span class="bad">${esc(failed.id)} was not sent: ${esc(failed.error)}</span><button type="button" data-act="retry" data-id="${esc(failed.id)}">Send again</button>`);
    else if (sending) parts.push(`<span>sending ${esc(sending.id)}…</span>`);
    else if (open) {
      const since = open.at ? ui.ago(open.at, view.now) : '';
      parts.push(`<span title="${esc(open.id)}">your move was sent${since ? ` ${esc(since)}` : ''}</span>`);
      if (w.state === 'calling') parts.push('<span>calling the GM…</span>');
      else if (w.state === 'called') parts.push('<span class="good">the GM has been called</span>');
      else if (w.state === 'off') parts.push('<span>the GM reads it when it is next called</span>');
      else if (w.state === 'unavailable' || w.state === 'failed') parts.push(`<span class="warn">${esc(w.reason)}</span><button type="button" data-act="wake-again">Call the GM again</button>`);
    }
    return parts.join(sep);
  }

  function renderAnswer(view) {
    if (!A.box) return;
    const mode = modeOf(view);
    if (mode !== 'closed') ensurePicks(view, mode);
    if (revise && !(withGm(view, mode) && withGm(view, mode).id === revise)) revise = '';
    const face = faceOf(view, mode);
    ui.put(A.status, statusHtml(view));
    const open = myOpenMove(view);
    const waitKey = open && !view.pending.some((p) => p.status === 'failed') ? open.id : '';
    if (A.wait.dataset.k !== waitKey) {
      A.wait.dataset.k = waitKey;
      A.wait.innerHTML = waitKey ? '<i></i>' : '';
      A.wait.hidden = !waitKey;
    }
    const why = mode === 'closed' ? closedWhy(view) : '';
    A.closed.hidden = !why;
    ui.put(A.closed, why ? esc(why) : '');
    A.box.hidden = mode === 'closed';
    if (mode === 'closed') return;
    if (ui.put(A.form, formHtml(view, mode, face))) {
      restoreFolds(A.form);
      const gp = A.form.querySelector('[data-a="gp"]');
      if (gp) gp.value = picks.gp;
    }
    A.form.hidden = !A.form.innerHTML;
    const ph = ooc ? 'A question for the GM, out of game.' : PLACEHOLDER[face];
    if (A.text.placeholder !== ph) A.text.placeholder = ph;
    if (lastMode !== face) {
      lastMode = face;
      A.text.setAttribute('aria-label', face === 'orders' ? 'Why, for the orders' : face === 'turn' ? "Morten's turn" : 'Your words to the GM');
    }
    if (A.text.value !== draft && document.activeElement !== A.text) A.text.value = draft;
    ui.put(A.send, sendHtml(view, face));
  }

  function setDraft(v) {
    draft = v;
    ui.local.set('story.draft', v);
  }

  function clearText() {
    setDraft('');
    if (A.text) A.text.value = '';
  }

  /** Every send goes straight from the click (the wake needs the viewer's gesture). */
  function sendMove(kind, fields, clear = true) {
    const p = T.store.send(kind, fields);
    if (clear) {
      const sent = draft;
      p.then(() => {
        if (draft === sent) clearText();
        if (kind === 'say' && ooc) ooc = false;
        T.app.render();
      }, () => T.app.render());
    } else p.catch(() => {});
    T.app.render();
    return p;
  }

  function sendPrimary(view) {
    const base = modeOf(view);
    const mode = faceOf(view, base);
    const text = draft.trim();
    if (mode === 'orders') {
      const o = view.state.awaiting.orders;
      const m = picks.mission !== null ? o.missions[picks.mission] : null;
      const a = picks.action !== null ? o.actions[picks.action] : null;
      const gp = parseInt(picks.gp, 10);
      const give = picks.give && Number.isFinite(gp) && gp > 0 ? { realm: picks.give, gp } : null;
      if (o.version === 3) {
        sendAnswer(view, base, 'orders', {
          travel: picks.travel,
          mission: m ? { type: m.type, target: m.target } : null,
          goal: picks.goal,
          actions: picks.actions.map((i) => o.actions[i]).filter(Boolean).map((x) => x.action),
          give,
          plan: text,
        });
      } else {
        sendAnswer(view, base, 'orders', {
          travel: picks.travel,
          mission: m ? { type: m.type, target: m.target } : null,
          action: a ? a.action : null,
          give,
          plan: text,
        });
      }
    } else if (mode === 'fight') sendAnswer(view, base, 'fight', { choice: picks.choice, text });
    else if (mode === 'turn') {
      if (text) sendAnswer(view, base, 'turn', { text });
    } else if (text && !ooc && mode === 'word') sendAnswer(view, base, 'say', { text, ooc });
    else if (text) sendMove('say', { text, ooc });
  }

  function insertText(v) {
    const t = A.text;
    if (!t) return;
    const s = t.value;
    const at = typeof t.selectionStart === 'number' && document.activeElement === t ? t.selectionStart : s.length;
    const before = s.slice(0, at);
    const pre = before && !/\s$/.test(before) ? ' ' : '';
    const ins = `${pre}${v} `;
    t.value = before + ins + s.slice(at);
    setDraft(t.value);
    t.focus();
    const pos = before.length + ins.length;
    try { t.setSelectionRange(pos, pos); } catch (_) { /* not a text field */ }
    T.app.render();
  }

  function onClick(ev) {
    const b = ev.target.closest('[data-act]');
    if (!b || !root.contains(b) || b.disabled) return;
    const act = b.dataset.act;
    const view = T.app.view() || last;
    switch (act) {
      case 'older':
        olderOpen = true;
        for (const m of Array.from(closedMonths)) if (m !== prevNewest) closedMonths.delete(m);
        remember();
        T.app.render();
        break;
      case 'month': {
        const m = b.dataset.m === '' ? null : parseInt(b.dataset.m, 10);
        if (b.getAttribute('aria-expanded') === 'true') {
          closedMonths.add(m);
          openMonths.delete(m);
        } else {
          openMonths.add(m);
          closedMonths.delete(m);
        }
        T.app.render();
        setTimeout(remember, 50);
        break;
      }
      case 'jump': {
        const mode = jumpEl.dataset.mode;
        if (mode === 'live') {
          following = true;
          follow();
        } else {
          const secs = Array.from(stream.children).filter((e) => /^s/.test(e.dataset.key));
          if (secs.length) scrollToEl(secs[secs.length - 1]);
        }
        updateJump();
        break;
      }
      case 'pick': {
        const f = b.dataset.f;
        const v = b.dataset.v;
        if (f === 'travel') {
          picks.travel = v;
          if (picks.mission !== null && view && view.state && view.state.awaiting.orders) {
            const m = view.state.awaiting.orders.missions[picks.mission];
            if (m && m.hex && m.hex !== v) picks.mission = null;
          }
        } else if (f === 'action' && view && view.state && view.state.awaiting.orders && view.state.awaiting.orders.version === 3) {
          // v3: the purse takes several options; "save" clears them
          if (v === '') picks.actions = [];
          else {
            const i = parseInt(v, 10);
            picks.actions = picks.actions.includes(i) ? picks.actions.filter((x) => x !== i) : picks.actions.concat(i);
          }
        } else if (f === 'mission' || f === 'action') picks[f] = v === '' ? null : parseInt(v, 10);
        else if (f === 'goal') picks.goal = v || null;
        else if (f === 'give') picks.give = v || null;
        T.app.render();
        break;
      }
      case 'all-hexes':
        allHexes = true;
        T.app.render();
        break;
      case 'all-goals':
        allGoals = true;
        T.app.render();
        break;
      case 'choice':
        picks.choice = b.dataset.v;
        if (picks.choice === 'plan' && A.text) A.text.focus();
        T.app.render();
        break;
      case 'insert':
        insertText(b.dataset.v);
        break;
      case 'ooc':
        ooc = !ooc;
        T.app.render();
        break;
      case 'send':
        if (view) sendPrimary(view);
        break;
      case 'revise':
        revise = b.dataset.id || '';
        T.app.render();
        break;
      case 'say': {
        const text = draft.trim();
        if (text) sendMove('say', { text, ooc });
        break;
      }
      case 'play':
        if (view && modeOf(view) !== 'playing') sendAnswer(view, modeOf(view), 'play', { scope: b.dataset.scope, text: draft.trim() });
        else sendMove('play', { scope: b.dataset.scope, text: draft.trim() });
        break;
      case 'stop':
        sendMove('play', { scope: 'stop', text: draft.trim() });
        break;
      case 'take':
        sendMove('take', { who: b.dataset.who === 'dm' ? 'dm' : 'you' }, false);
        break;
      case 'wake-again':
        T.store.wakeAgain();
        break;
      case 'retry':
        T.store.retry(b.dataset.id).catch(() => {});
        break;
      case 'dismiss':
        T.store.dismiss(b.dataset.id);
        break;
      default:
    }
  }

  // ---------- mount and render ----------
  function render(view) {
    if (!root) return;
    last = view;
    const shown = visible();
    const before = restored && shown && !following ? anchorNow() : null;
    const items = buildItems(view);
    const added = reconcile(items);
    const keys = new Set(items.map((i) => i.key));
    if (before) {
      let el = before.el.isConnected ? before.el : null;
      if (!el && before.key === 'live') {
        const fresh = added.filter((k) => /^s/.test(k)).map(keyEl).filter(Boolean);
        const settled = fresh.filter((e) => !e.querySelector('[data-kind="aside"]'));
        el = settled[settled.length - 1] || fresh[fresh.length - 1] || null;
      }
      if (el) {
        const d = el.getBoundingClientRect().top - before.top;
        if (Math.abs(d) > 0.5) window.scrollBy(0, d);
      }
    }
    prevKeys = keys;
    renderAnswer(view);
    if (!restored && shown && view.loaded.story && view.ready) firstPlace();
    if (following && shown) follow();
    updateJump();
  }

  T.panels.story = {
    mount(el) {
      root = el;
      el.innerHTML = '<div class="stream" id="stream"></div>'
        + '<section class="answer" data-wake-anchor aria-label="Your word">'
        + '<p class="status" role="status" data-a="status"></p><div class="wait" data-a="wait" aria-hidden="true" hidden></div>'
        + '<p class="note closed-why" data-a="closed" hidden></p>'
        + '<div class="box" data-a="box"><div class="form" data-a="form"></div>'
        + '<textarea id="answer-text" rows="2" aria-label="Your words to the GM"></textarea>'
        + '<div class="send" data-a="send"></div></div></section>'
        + '<button type="button" class="jump" data-act="jump" hidden></button>';
      stream = el.querySelector('#stream');
      jumpEl = el.querySelector('.jump');
      for (const k of ['status', 'wait', 'closed', 'box', 'form', 'send']) A[k] = el.querySelector(`[data-a="${k}"]`);
      A.text = el.querySelector('#answer-text');
      A.text.value = draft;
      A.text.addEventListener('input', () => {
        setDraft(A.text.value);
        if (last) ui.put(A.send, sendHtml(last, modeOf(last)));
      });
      A.text.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter' && (ev.metaKey || ev.ctrlKey)) {
          ev.preventDefault();
          const p = A.send.querySelector('button.primary');
          if (p && !p.disabled) p.click();
        }
      });
      el.addEventListener('input', (ev) => {
        if (ev.target && ev.target.dataset && ev.target.dataset.a === 'gp' && picks) picks.gp = ev.target.value;
      });
      el.addEventListener('click', onClick);
      el.addEventListener('keydown', (ev) => {
        const m = ev.target.closest && ev.target.closest('.month[data-act="month"]');
        if (m && (ev.key === 'Enter' || ev.key === ' ')) {
          ev.preventDefault();
          m.click();
        }
      });
      el.addEventListener('toggle', (ev) => {
        const d = ev.target;
        if (d && d.dataset && d.dataset.fold) folds.set(d.dataset.fold, d.open);
      }, true);
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      for (const e of ['wheel', 'touchmove']) window.addEventListener(e, stopFollowing, { passive: true });
      window.addEventListener('keydown', (ev) => { if (['ArrowUp', 'PageUp', 'Home'].includes(ev.key)) stopFollowing(); });
      window.addEventListener('pagehide', () => { if (reading) ui.local.set('story.reading', reading); });
      // More → Months asks for a month (80-more.js): open it here and bring its header up
      document.addEventListener('table:goto', (ev) => {
        const m = ev.detail ? ev.detail.month : undefined;
        if (!(Number.isInteger(m) || m === null)) return;
        ev.preventDefault();
        T.panels.story.showMonth(m);
      });
    },
    render,
    tick(view) {
      render(view);
    },
    /** Open a month in the stream and bring its header to the top (for the Months tab). */
    showMonth(month) {
      const m = Number.isInteger(month) ? month : null;
      openMonths.add(m);
      closedMonths.delete(m);
      T.app.go('story');
      if (last) render(last);
      const el = keyEl(`m-${m}`);
      if (el) scrollToEl(el);
      remember();
    },
    /** Bring a section (story/sNNNN id) to the top, opening its month (for the Fights tab, the map's badges). */
    goTo(id) {
      const s = last ? last.sections.find((x) => x.id === id) : null;
      if (s) {
        openMonths.add(s.month);
        closedMonths.delete(s.month);
      }
      T.app.go('story');
      if (last) render(last);
      const el = keyEl(id);
      if (el) scrollToEl(el);
      remember();
    },
    /** The player's answer to the GM's question now, while it waits for the GM (the now line). */
    withGm(view) {
      return view ? withGm(view) : null;
    },
    /** Pick a hex as the orders' travel (for the Realm tab's map). */
    pickHex(id) {
      const view = T.app.view() || last;
      if (!view || modeOf(view) !== 'orders') return false;
      ensurePicks(view, 'orders');
      const o = view.state.awaiting.orders;
      if (!o.hexes.some((h) => h.id === id)) return false;
      picks.travel = id;
      if (picks.mission !== null) {
        const mi = o.missions[picks.mission];
        if (mi && mi.hex && mi.hex !== id) picks.mission = null;
      }
      const near = o.hexes.slice().sort((a, b) => (a.days ?? 99) - (b.days ?? 99)).slice(0, NEAR_HEXES);
      allHexes = allHexes || !near.some((h) => h.id === id);
      const w = withGm(view, 'orders');
      if (w) revise = w.id; // changing the orders sent
      T.app.render();
      // once the Story shows, bring the form's travel row into view
      setTimeout(() => {
        const row = A.form && A.form.querySelector('[data-row="travel"]');
        if (row && visible()) row.scrollIntoView({ block: 'center' });
      }, 60);
      return true;
    },
  };
})();
