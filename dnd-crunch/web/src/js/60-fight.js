// The fight card and the Fights tab (README: File ownership; table-plan.md 4.5).
//
// T.panels.fightCard is the card the Story and the Fights tab share:
//   html(section, {live, beats}) -> an HTML string
//     section: a parsed story section (kind fight, with .fight), or, live, the beats'
//              section head ({kind, title, month, day, where, foes}) or game/state.live.
//     live:    true while the fight is played: the head, HP bars moving from the newest
//              beat's state, the rounds appending from the beats' lines, no story yet.
//     beats:   the live/* beats of this fight (parsed, oldest first).
//   bind(rootEl) wires the folds and taps inside every card under rootEl (idempotent;
//   safe to call after every render). Folds stay open across re-renders.
//
// T.panels.fights is the Fights tab (#fights): every fight as a row, newest first, a
// month filter, and a row that opens its card inline.
(() => {
  'use strict';
  const T = window.T;
  const { esc, icon, put, fmt, bar, dice } = T.ui;
  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
  const arr = (v) => (Array.isArray(v) ? v : []);
  const str = (v) => (typeof v === 'string' ? v : '');

  /** Open folds, by key (`<scope><section id>:rounds`, `…:hp`), kept across re-renders. */
  const opened = new Set();

  // ---------- words ----------
  const OUTCOME = {
    cleared: { word: 'cleared', cls: 'good' },
    died: { word: 'died', cls: 'bad' },
    fled: { word: 'fled', cls: 'warn' },
    bypassed: { word: 'bypassed', cls: 'muted' },
    going: { word: 'going on', cls: 'brass' },
  };
  const STATE_CLS = { healthy: 'good', bloodied: 'warn', 'near death': 'bad' };
  const STATE_PCT = { healthy: 100, bloodied: 50, 'near death': 15 };
  const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);

  /** The title's parts: place, the foes phrase and its CR, from "Room 2.3 · 2 Shadows (CR 1/2 each) · High, 200 XP · cleared". */
  function head(sec, foes) {
    const parts = str(sec.title).split(' · ').map((s) => s.trim()).filter(Boolean);
    const at = parts.findIndex((p) => /\(CR [^)]*\)/.test(p));
    let place = '';
    let foesWords = '';
    let cr = '';
    if (at >= 0) {
      place = parts.slice(0, at).join(' · ');
      const m = /^(.*?)\s*\((CR [^)]*)\)\s*$/.exec(parts[at]);
      foesWords = m ? m[1] : parts[at];
      cr = m ? m[2] : '';
    } else if (parts.length > 1) {
      place = parts[0];
      foesWords = parts[1];
    } else {
      place = parts[0] || '';
    }
    if (!place) place = str(sec.where);
    if (!foesWords && foes.length) foesWords = foes.map((f) => (f.count > 1 ? `${f.count} × ${f.name}` : f.name)).join(', ');
    if (!cr && foes.length) {
      const crs = foes.filter((f) => f.cr).map((f) => `CR ${f.cr}${f.count > 1 ? ' each' : ''}`);
      cr = foes.length === 1 ? crs[0] || '' : foes.map((f) => (f.cr ? `${f.name} CR ${f.cr}` : '')).filter(Boolean).join(', ');
    }
    return { place, foes: foesWords, cr };
  }

  const isMorten = (name) => /^morten\b/i.test(str(name));

  /** Morten's HP track row, or null. */
  function mortenTrack(f) {
    if (!f) return null;
    return f.hpTrack.find((t) => isMorten(t.name)) || null;
  }

  /** HP before and after for Morten: {before, after, max, low} from the track, else the section's after. */
  function mortenHp(sec) {
    const t = mortenTrack(sec.fight);
    const hp = t ? t.hp.filter(isNum) : [];
    const after = sec.after && isNum(sec.after.hp) ? sec.after.hp : hp.length ? hp[hp.length - 1] : null;
    const max = t && isNum(t.max) ? t.max : sec.after && isNum(sec.after.maxHp) ? sec.after.maxHp : null;
    return { before: hp.length ? hp[0] : null, after, max, low: hp.length ? Math.min(...hp) : after };
  }

  /** The outcome's word and colour; a clear that took Morten to half HP or less shows amber. */
  function outcomeOf(sec, live) {
    if (live) return OUTCOME.going;
    const f = sec.fight;
    const o = OUTCOME[f ? f.outcome : 'going'] || OUTCOME.going;
    if (o === OUTCOME.cleared) {
      const h = mortenHp(sec);
      if (isNum(h.low) && isNum(h.max) && h.max > 0 && h.low <= h.max / 2) return { word: o.word, cls: 'warn' };
    }
    return o;
  }

  const lostOf = (sec) => {
    const f = sec.fight;
    const a = f && f.lost.length ? f.lost : sec.after ? sec.after.lost : [];
    return arr(a);
  };

  /** "3 Giant Lizards" → the phrase; the place's icon. */
  const placeIcon = (place) => (/room|floor|hall|door/i.test(place) ? 'door' : /road|wander|travel|camp/i.test(place) ? 'boots' : 'fight');

  // ---------- the parts of a card ----------
  function foeRows(foes, live) {
    if (!foes.length) return '';
    return `<div class="foes" aria-label="The foes">${foes.map((f) => {
      const name = `${esc(f.name)}${f.count > 1 ? ` <span class="ct">×${esc(f.count)}</span>` : ''}`;
      let hp;
      if (!isNum(f.hp) && !isNum(f.maxHp) && f.state) hp = `<span class="${STATE_CLS[f.state] || ''}">${esc(cap(f.state))}</span>`;
      else if (live || !isNum(f.hp) || f.hp === f.maxHp || !isNum(f.maxHp)) {
        const v = isNum(f.maxHp) ? f.maxHp : f.hp;
        hp = isNum(v) ? `${esc(fmt.n(v))} HP${f.count > 1 ? ' each' : ''}` : '';
      } else hp = esc(fmt.hp(f.hp, f.maxHp));
      const stats = [f.cr ? `CR ${f.cr}` : '', fmt.ac(f.ac), f.speed, ...f.attacks, f.notes].filter(Boolean);
      return `<div class="foe"><b>${name}</b>${hp ? `<span class="hp">${icon('heart', 'bad')}${hp}</span>` : ''}${stats.length ? `<span class="stats">${stats.map(esc).join(' · ')}</span>` : ''}</div>`;
    }).join('')}</div>`;
  }

  /** The live HP bars: Morten and each foe from the newest beat's state. */
  function hpBars(state) {
    if (!state) return '';
    const rows = [];
    const m = state.morten;
    if (m && (isNum(m.hp) || isNum(m.maxHp))) rows.push({ name: 'Morten', hp: m.hp, max: m.maxHp, me: true });
    for (const f of arr(state.foes)) rows.push({ name: f.name, hp: f.hp, max: f.maxHp, state: f.state });
    if (!rows.length) return '';
    return `<div class="hprow" aria-label="HP now">${rows.map((r) => {
      if (!isNum(r.hp) && r.state) {
        return `<div class="hp${r.me ? ' me' : ''}"><span class="nm">${esc(r.name)}</span><span class="bar ${r.state === 'healthy' ? '' : r.state === 'bloodied' ? 'mid' : 'low'}" role="img" aria-label="${esc(r.state)}"><i style="width:${STATE_PCT[r.state] || 0}%"></i></span><b class="${STATE_CLS[r.state] || ''}">${esc(cap(r.state))}</b></div>`;
      }
      const down = isNum(r.hp) && r.hp <= 0;
      return `<div class="hp${r.me ? ' me' : ''}${down ? ' down' : ''}"><span class="nm">${esc(r.name)}</span>${bar(r.hp, r.max)}<b>${down && !r.me ? 'down' : esc(isNum(r.max) ? `${fmt.n(r.hp)}/${fmt.n(r.max)} HP` : fmt.hp(r.hp, r.max))}</b></div>`;
    }).join('')}</div>`;
  }

  /** A short name for a line's end label: "Giant Wolf Spider A" -> "Spider A". */
  function shortName(name) {
    const s = str(name);
    if (s.length <= 11) return s;
    const w = s.split(/\s+/);
    const last = w[w.length - 1];
    if (w.length > 1 && /^[A-Z0-9]$/.test(last)) {
      const pre = w[w.length - 2];
      return `${pre.length > 9 ? `${pre.slice(0, 8)}.` : pre} ${last}`;
    }
    return last.length <= 11 ? last : `${last.slice(0, 10)}.`;
  }

  const DASH = ['5 3', '2 3', '8 3 2 3', '1 3', '10 4', '4 2 1 2'];
  /**
   * The HP track (as Dream's panels/hp-track.ts): Morten and each foe from the start through
   * each round, an inline SVG line chart, each line named at its end, the numbers one tap
   * away. Morten is the brass line; foes are ink lines told apart by their dash and their
   * names. A foe's line ends where it went down (a red dot).
   */
  function hpTrack(f, key) {
    const list = f ? f.hpTrack.filter((t) => t.hp.some(isNum)) : [];
    if (!list.length) return '';
    const series = list.filter((t) => isMorten(t.name)).concat(list.filter((t) => !isMorten(t.name)));
    const W = 360; const H = 140; const L = 28; const R = 84; const TOP = 10; const B = 22;
    const n = Math.max(1, ...series.map((t) => t.hp.length)) - 1;
    const top = Math.max(1, ...series.map((t) => (isNum(t.max) ? t.max : 0)), ...series.flatMap((t) => t.hp.filter(isNum)));
    const x = (i) => (n === 0 ? L + (W - L - R) / 2 : L + (i / n) * (W - L - R));
    const y = (v) => TOP + (1 - v / top) * (H - TOP - B);
    const f1 = (v) => v.toFixed(1);
    let foeI = 0;
    const out = series.map((t) => {
      const me = isMorten(t.name);
      let hp = t.hp.slice();
      if (!me) {
        const z = hp.findIndex((v) => isNum(v) && v <= 0);
        if (z >= 0) hp = hp.slice(0, z + 1);
      }
      const pts = hp.map((v, i) => (isNum(v) ? { x: x(i), y: y(Math.max(0, v)), hp: v, i } : null));
      let d = '';
      let pen = false;
      for (const p of pts) {
        if (!p) { pen = false; continue; }
        d += `${pen ? 'L' : 'M'}${f1(p.x)},${f1(p.y)} `;
        pen = true;
      }
      const real = pts.filter(Boolean);
      const last = real[real.length - 1];
      const dead = !me && last.hp <= 0;
      const cls = me ? 'm' : `f f${foeI % 4}`;
      const dash = me ? '' : DASH[foeI % DASH.length];
      if (!me) foeI += 1;
      // a foe that went down: its line stops there (a red dot), a faint rule runs on at 0
      const gone = dead && last.i < n ? `M${f1(last.x)},${f1(last.y)} L${f1(x(n))},${f1(last.y)}` : '';
      return { t, me, cls, dash, pts: real, d: d.trim(), gone, last, dead, label: { x: x(n) + 6, y: last.y, text: `${shortName(t.name)} ${dead ? '✝' : last.hp <= 0 ? '0' : fmt.n(last.hp)}` } };
    });
    // end labels, all in the right gutter: pushed apart where two end close together,
    // then back up off the round ticks when several end low (as Dream's hp-track does)
    const labs = out.map((s) => s.label).sort((a, b) => a.y - b.y);
    for (let i = 1; i < labs.length; i++) if (labs[i].y - labs[i - 1].y < 11) labs[i].y = labs[i - 1].y + 11;
    const floor = H - B;
    for (let i = labs.length - 1; i >= 0; i--) {
      const below = i === labs.length - 1 ? floor : labs[i + 1].y - 11;
      labs[i].y = Math.min(labs[i].y, below);
    }
    const half = Math.round(top / 2);
    const grid = [0, half, top].filter((v, i, a) => a.indexOf(v) === i);
    const every = n <= 10 ? 1 : Math.ceil(n / 8);
    const ticks = [{ i: 0, t: 'start' }];
    for (let i = every; i <= n; i += every) ticks.push({ i, t: `R${i}` });
    const when = (i) => (i === 0 ? 'at the start' : `after round ${i}`);
    const aria = `HP at the start and after each round: ${out.map((s) => `${s.t.name} ${s.pts.map((p) => p.hp).join(', ')}`).join('; ')}`;
    const svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(aria)}" data-hp-tap="${esc(key)}">`
      + grid.map((v) => `<line class="grid" x1="${L}" x2="${W - R}" y1="${f1(y(v))}" y2="${f1(y(v))}"/><text class="tick" x="${L - 5}" y="${f1(y(v) + 3)}" text-anchor="end">${v}</text>`).join('')
      + ticks.map((k) => `<text class="tick" x="${f1(x(k.i))}" y="${H - 6}" text-anchor="middle">${k.t}</text>`).join('')
      + out.map((s) => (s.gone ? `<path class="gone" d="${s.gone}"/>` : '')).join('')
      + out.map((s) => `<path class="ln ${s.cls}" d="${s.d}"${s.dash ? ` stroke-dasharray="${s.dash}"` : ''}/>`).join('')
      + out.map((s) => s.pts.map((p) => `<circle class="dot ${s.cls}${!s.me && p.hp <= 0 ? ' dead' : ''}" cx="${f1(p.x)}" cy="${f1(p.y)}" r="${!s.me && p.hp <= 0 ? 3.6 : n > 12 ? 1.8 : 2.6}"><title>${esc(s.t.name)}, ${when(p.i)}: ${esc(isNum(s.t.max) ? `${p.hp}/${s.t.max} HP` : `${p.hp} HP`)}</title></circle>`).join('')
        + `<text class="end ${s.cls}" x="${f1(s.label.x)}" y="${f1(s.label.y)}">${esc(s.label.text)}</text>`).join('')
      + '</svg>';
    const legend = out.length > 1
      ? `<span class="legend">${out.map((s) => `<span><svg viewBox="0 0 18 6" aria-hidden="true"><line class="ln ${s.cls}" x1="1" x2="17" y1="3" y2="3"${s.dash ? ` stroke-dasharray="${s.dash}"` : ''}/></svg>${esc(s.t.name)}</span>`).join('')}</span>`
      : '';
    const cols = Array.from({ length: n + 1 }, (_, i) => (i === 0 ? 'start' : `R${i}`));
    const fold = `${key}:hp`;
    const table = `<details class="numbers" data-fold="${esc(fold)}"${opened.has(fold) ? ' open' : ''}><summary>${icon('chev')}The HP as numbers</summary>`
      + `<div class="scroll"><table><thead><tr><th scope="col"><span class="vh">who</span></th>${cols.map((c) => `<th scope="col">${c}</th>`).join('')}</tr></thead><tbody>`
      + out.map((s) => `<tr><th scope="row" title="${esc(s.t.name)}">${esc(shortName(s.t.name))}${isNum(s.t.max) ? ` <small>of ${esc(s.t.max)}</small>` : ''}</th>${cols.map((_, i) => {
        const v = s.t.hp[i];
        return `<td class="${isNum(v) && v <= 0 ? 'zero' : ''}">${isNum(v) ? esc(v) : '·'}</td>`;
      }).join('')}</tr>`).join('')
      + '</tbody></table></div></details>';
    return `<figure class="track" aria-label="HP across the fight"><figcaption><span class="label">HP across the fight</span>${legend}</figcaption>${svg}${table}</figure>`;
  }

  /** Bold the HP a line reports after a hit ("Morten 20 → 15 HP", "A 27 → 17 HP") and a kill. */
  function lineText(text) {
    return esc(text)
      .replace(/((?:\b[A-Z][\w'’]*(?: [A-Z]\b)? )?\d+ → \d+ HP)/g, '<b>$1</b>')
      .replace(/\b(dead|down|killed)\b/g, '<b>$1</b>');
  }

  const MARK = { morten: '✦', foe: '›', gm: '·', world: '·' };
  function lineHtml(l) {
    const cls = l.who === 'foe' ? ' them' : l.who === 'morten' ? ' me' : ' gm';
    const fizz = arr(l.dice).some((d) => d && d.result === 'fizzle');
    const ds = dice(l.dice);
    return `<div class="ln${cls}${fizz ? ' fizzled' : ''}"><span class="mk" aria-hidden="true">${MARK[l.who] || '·'}</span><span class="tx">${lineText(l.text)}${fizz ? ' <span class="tag-fizz">fizzle</span>' : ''}${ds ? ` <span class="dice">${ds}</span>` : ''}</span></div>`;
  }

  /** Lines grouped into rounds; lines with no round join the round before (or "Before the fight"). */
  function group(lines) {
    const out = [];
    let cur = null;
    for (const l of lines) {
      const r = isNum(l.round) ? l.round : null;
      if (!cur || (r !== null && r !== cur.n)) {
        cur = { n: r, lines: [], texts: [] };
        out.push(cur);
      }
      cur.lines.push(l);
    }
    return out;
  }

  function roundsHtml(blocks, initiative) {
    return blocks.map((b) => {
      const init = b.n === 1 && initiative.length ? ` · init ${initiative.map(esc).join(' › ')}` : '';
      const h = b.n === null ? 'Before the fight' : `Round ${b.n}${init}`;
      return `<div class="round"><h5>${h}</h5>${b.texts.map((t) => `<p class="beat-tx">${esc(t)}</p>`).join('')}${b.lines.map(lineHtml).join('')}</div>`;
    }).join('');
  }

  function storyHtml(sec) {
    const parts = [];
    if (sec.headline) parts.push(`<p class="head">${esc(sec.headline)}</p>`);
    for (const p of arr(sec.prose)) parts.push(`<p>${esc(p)}</p>`);
    const bl = arr(sec.bullets).filter((b) => b && b.text);
    if (bl.length) parts.push(`<ul class="bullets">${bl.map((b) => `<li>${b.label ? `<b>${esc(b.label)}</b>` : ''}${esc(b.text)}</li>`).join('')}</ul>`);
    return parts.length ? `<div class="story">${parts.join('')}</div>` : '';
  }

  function resultHtml(sec) {
    const f = sec.fight;
    const bits = [];
    const xpAfter = f && isNum(f.xpAfter) ? f.xpAfter : sec.after ? sec.after.xp : null;
    const gained = f && isNum(f.xp) ? f.xp : f && isNum(f.xpBefore) && isNum(xpAfter) ? xpAfter - f.xpBefore : null;
    if (isNum(gained) || isNum(xpAfter)) bits.push(`<span>${icon('spark')}${isNum(gained) ? `+${esc(fmt.xp(gained))}` : 'XP'}${isNum(xpAfter) ? ` → <b>${esc(fmt.xp(xpAfter))}</b>` : ''}</span>`);
    if (f && f.loot) bits.push(`<span>${icon('coins')}${esc(f.loot)}</span>`);
    const h = mortenHp(sec);
    if (isNum(h.after)) bits.push(`<span>${icon('heart')}<b>${esc(isNum(h.max) ? `${fmt.n(h.after)}/${fmt.n(h.max)} HP` : fmt.hp(h.after))}</b></span>`);
    const lost = lostOf(sec);
    bits.push(lost.length ? `<span class="lost">lost <b>${esc(lost.join(', '))}</b> until a Long Rest</span>` : '<span>nothing lost</span>');
    if (f && f.potion) bits.push('<span class="warn">a potion used</span>');
    return `<p class="result">${bits.join('')}</p>`;
  }

  // ---------- the card ----------
  function html(section, opts = {}) {
    const o = opts || {};
    const sec = section && typeof section === 'object' ? section : {};
    const beats = arr(o.beats).filter((b) => b && typeof b === 'object');
    const live = !!o.live;
    const scope = str(o.scope);
    const id = str(sec.id) || (beats.length ? `live-${str(sec.title) || 'fight'}` : 'fight');
    const key = `${scope}${id}`;
    const f = sec.fight && typeof sec.fight === 'object' ? sec.fight : null;
    // the foes: the fight's, else the section head's, else the beats' head
    let foes = f ? arr(f.foes) : arr(sec.foes);
    if (!foes.length) for (const b of beats) if (b.section && arr(b.section.foes).length) foes = b.section.foes;
    const hd = head(sec.title || !beats.length ? sec : Object.assign({}, sec, { title: beats[beats.length - 1].section ? beats[beats.length - 1].section.title : '' }), foes);
    const out = outcomeOf(sec, live);
    const lastBeat = beats[beats.length - 1] || null;
    const round = live ? (lastBeat && isNum(lastBeat.round) ? lastBeat.round : null) : f && isNum(f.rounds) ? f.rounds : null;

    const meta = [];
    if (f && (f.difficulty || isNum(f.xp))) meta.push(`<span>${esc([f.difficulty, fmt.xp(f.xp)].filter(Boolean).join(', '))}</span>`);
    if (live) meta.push(`<span class="live-tag"><i class="pulse" aria-hidden="true"></i>in progress${isNum(round) ? ` · round ${esc(round)}` : ''}</span>`);
    else {
      meta.push(`<span class="out ${out.cls}">${esc(out.word)}</span>`);
      if (isNum(round)) meta.push(`<span>${esc(fmt.plural(round, 'round'))}</span>`);
      if (f && f.verdict && f.verdict !== out.word) meta.push(`<span class="verdict">${esc(f.verdict)}</span>`);
    }
    const when = !live && (isNum(sec.month) || isNum(sec.day)) ? fmt.when({ month: sec.month, day: sec.day, clock: sec.clock }) : '';
    const title = `${esc(hd.place)}${hd.place && hd.foes ? ' · ' : ''}${esc(hd.foes)}${hd.cr ? ` <small>${esc(hd.cr)}</small>` : ''}`;

    const parts = [];
    parts.push(`<div class="sec-head">${icon(placeIcon(hd.place))}<div><h3>${title || 'A fight'}</h3><p class="meta">${meta.join('')}</p>${when ? `<p class="meta when">${esc(when)}${sec.where && sec.where !== hd.place ? ` · ${esc(sec.where)}` : ''}</p>` : ''}</div></div>`);
    parts.push(foeRows(foes, live));

    if (live) {
      parts.push(hpBars(lastBeat ? lastBeat.state : null));
      const lines = [];
      const texts = new Map();
      for (const b of beats) {
        for (const l of arr(b.lines)) lines.push(isNum(l.round) || !isNum(b.round) ? l : Object.assign({}, l, { round: b.round }));
        if (b.text) {
          const r = isNum(b.round) ? b.round : null;
          if (!texts.has(r)) texts.set(r, []);
          texts.get(r).push(b.text);
        }
      }
      const blocks = group(lines);
      for (const [r, t] of texts) {
        let blk = blocks.find((b) => b.n === r);
        if (!blk) { blk = { n: r, lines: [], texts: [] }; blocks.push(blk); }
        blk.texts.push(...t);
      }
      blocks.sort((a, b) => (a.n === null ? -1 : b.n === null ? 1 : a.n - b.n));
      parts.push(blocks.length ? `<div class="rounds">${roundsHtml(blocks, f ? f.initiative : [])}</div>` : '<p class="muted waiting">The first round is being rolled.</p>');
    } else {
      parts.push(hpTrack(f, key));
      parts.push(storyHtml(sec));
      const blocks = group(arr(sec.trace));
      if (blocks.length) {
        const fold = `${key}:rounds`;
        const nRounds = blocks.filter((b) => b.n !== null).length;
        parts.push(`<details class="trace" data-fold="${esc(fold)}"${opened.has(fold) ? ' open' : ''}><summary>${icon('chev')}The rounds and the dice${nRounds ? ` (${esc(fmt.plural(nRounds, 'round'))})` : ''}</summary>${roundsHtml(blocks, f ? f.initiative : [])}</details>`);
      }
      parts.push(resultHtml(sec));
    }
    const label = `${live ? 'A fight going on' : 'A fight'}: ${hd.foes || hd.place}`;
    return `<article class="sec fight fcard${live ? ' live' : ''}" data-fight="${esc(key)}" aria-label="${esc(label)}">${parts.filter(Boolean).join('')}</article>`;
  }

  function bind(root) {
    if (!root || root.__fightBound) return;
    root.__fightBound = true;
    root.addEventListener('toggle', (ev) => {
      const d = ev.target;
      if (!d || !d.matches || !d.matches('details[data-fold]')) return;
      const k = d.getAttribute('data-fold');
      if (d.open) opened.add(k); else opened.delete(k);
    }, true);
    root.addEventListener('click', (ev) => {
      const s = ev.target && ev.target.closest ? ev.target.closest('svg[data-hp-tap]') : null;
      if (!s || !root.contains(s)) return;
      const fig = s.closest('figure');
      const d = fig && fig.querySelector('details.numbers');
      if (d) d.open = !d.open;
    });
  }

  T.panels.fightCard = { html, bind };

  // ---------- the Fights tab ----------
  let box = null;
  let month = 'all';
  const rowsOpen = new Set();

  /** The live fight, when one is going on: {section, beats}. */
  function liveFight(view) {
    const beats = view.beats.filter((b) => b.section && b.section.kind === 'fight');
    const head = view.state && view.state.live && view.state.live.kind === 'fight' ? view.state.live : null;
    if (!beats.length && !head) return null;
    const last = beats[beats.length - 1];
    const sec = Object.assign({ id: 'live' }, head || {}, last && last.section ? last.section : {});
    if (!isNum(sec.month) && head) sec.month = head.month;
    return { section: Object.assign({}, sec, { id: 'live', seq: last ? last.seq : Infinity }), beats };
  }

  function rowHtml(sec, live) {
    const f = sec.fight;
    const foes = f ? f.foes : arr(sec.foes);
    const hd = head(sec, foes);
    const out = outcomeOf(sec, live);
    let pip = out.cls === 'good' ? '' : out.cls === 'warn' ? 'hurt' : out.cls === 'bad' ? 'dead' : out.cls === 'brass' ? 'going' : 'off';
    if (live) pip = 'going';
    let hpWords = '';
    if (live) {
      const st = live.beats.length ? live.beats[live.beats.length - 1].state : null;
      const m = st && st.morten;
      if (m && isNum(m.hp)) hpWords = `${fmt.n(m.hp)}/${fmt.n(m.maxHp)} HP now`;
    } else {
      const h = mortenHp(sec);
      if (isNum(h.before) && isNum(h.after)) hpWords = h.before === h.after && h.low === h.before && (!isNum(h.max) || h.before === h.max) ? 'untouched' : `HP ${fmt.n(h.before)} → ${fmt.n(h.after)}`;
      else if (isNum(h.after)) hpWords = `HP ${fmt.hp(h.after, h.max)}`;
    }
    const m = [];
    const when = fmt.when({ month: sec.month, day: sec.day });
    if (when) m.push(when);
    if (f && (f.difficulty || isNum(f.xp))) m.push([f.difficulty, fmt.xp(f.xp)].filter(Boolean).join(', '));
    const lost = live ? [] : lostOf(sec);
    if (lost.length) m.push(`lost ${lost.join(', ')}`);
    if (f && f.potion) m.push('potion used');
    if (f && f.verdict && f.verdict !== out.word) m.push(f.verdict);
    const id = live ? 'live' : sec.id;
    const isOpen = rowsOpen.has(id);
    const title = `${esc(hd.place)}${hd.place && hd.foes ? ' · ' : ''}${esc(hd.foes)}${hd.cr ? ` <small class="muted">${esc(hd.cr)}</small>` : ''}`;
    const row = `<button type="button" class="frow" data-frow="${esc(id)}" aria-expanded="${isOpen}"><i class="pip ${pip}" aria-hidden="true"></i><span class="t">${title || 'A fight'}</span><span class="r"><span class="${out.cls}">${esc(out.word)}</span><br>${esc(hpWords)}</span><span class="m">${esc(m.join(' · '))}</span></button>`;
    const card = isOpen ? T.panels.fightCard.html(sec, { live: !!live, beats: live ? live.beats : [], scope: 'fights:' }) : '';
    return `<div class="fitem${isOpen ? ' open' : ''}">${row}${card}</div>`;
  }

  function render(view) {
    if (!box) return;
    const settled = view.sections.filter((s) => s.kind === 'fight' || s.fight).slice().sort((a, b) => b.seq - a.seq);
    const lf = liveFight(view);
    const all = (lf ? [{ sec: lf.section, live: lf }] : []).concat(settled.map((s) => ({ sec: s, live: null })));
    const months = [...new Set(all.map((x) => x.sec.month).filter(isNum))].sort((a, b) => b - a);
    if (month !== 'all' && !months.includes(month)) month = 'all';
    const shown = all.filter((x) => month === 'all' || x.sec.month === month);
    let body;
    if (!view.loaded.story && !all.length) body = '<p class="muted">Opening the story…</p>';
    else if (!all.length) body = '<p class="muted empty">No fight yet. Each fight lands here as a row: where it was, the foes with their CR, how hard it was, how it ended and what it cost; a row opens the fight\'s card.</p>';
    else {
      const filter = months.length > 1
        ? `<div class="subtabs" role="group" aria-label="Which month">${['all', ...months].map((mo) => `<button type="button" data-fmonth="${mo}" aria-pressed="${month === mo}">${mo === 'all' ? 'all' : `month ${mo}`}</button>`).join('')}</div>`
        : '';
      body = `${filter}<div class="frows">${shown.map((x) => rowHtml(x.sec, x.live)).join('')}</div><p class="muted hint">A row opens the fight's card as the story shows it: the foes, the HP track, the GM's summary and the rounds with their dice.</p>`;
    }
    const count = all.length;
    const sub = count ? `${esc(fmt.plural(count, 'fight'))} · newest first` : '';
    put(box, `<div class="card fights">${'<h3>'}${icon('fight')}Every fight${sub ? ` <small>${sub}</small>` : ''}</h3>${body}</div>`);
    T.panels.fightCard.bind(box);
  }

  T.panels.fights = {
    mount(el) {
      box = el;
      el.addEventListener('click', (ev) => {
        const t = ev.target && ev.target.closest ? ev.target : null;
        if (!t) return;
        const mb = t.closest('[data-fmonth]');
        if (mb) {
          const v = mb.getAttribute('data-fmonth');
          month = v === 'all' ? 'all' : parseInt(v, 10);
          if (T.app && T.app.render) T.app.render();
          return;
        }
        const rb = t.closest('[data-frow]');
        if (rb) {
          const id = rb.getAttribute('data-frow');
          if (rowsOpen.has(id)) rowsOpen.delete(id); else rowsOpen.add(id);
          if (T.app && T.app.render) T.app.render();
        }
      });
    },
    render,
  };
})();
