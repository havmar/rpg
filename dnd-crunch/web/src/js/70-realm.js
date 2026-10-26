// The Realm tab (table-plan.md 3.1-3.4, 4.4): the tower card, the map, the hex entry and
// the realm rows, from game/realm (map.json as the engine writes it, plus the page's
// camelCase words, kinds, rumours, floors, days, eventsWords, hexNames) and game/state.
// UI state (the picked hex, the open rows, the map's toggles, the event shown) lives in
// this closure and survives re-renders; Codes and Moves are remembered per viewer.
(() => {
  'use strict';
  const T = window.T;
  const { esc, fmt, put, icon, bar, band, fac, note, local } = T.ui;

  // ---------- words ----------
  const ATTR = { F: ['sword', 'Force'], C: ['mask', 'Cunning'], W: ['coins', 'Wealth'] };
  const typeOf = (a, k) => {
    const t = (k && k.type) || (a && a.type) || '';
    const c = t.charAt(0).toUpperCase();
    return ATTR[c] ? c : 'F';
  };
  const DIFF = ['Low', 'Moderate', 'High'];
  // Realms v3 (game/realm.version 3): sites instead of pieces, goals as clocks, standing, the ladder
  const V3 = (r) => r.version === 3;
  const SITE_GLYPH = { seat: 'crown', garrison: 'shield', works: 'globe', walls: 'door' };
  const STANDING_CLS = { ally: 'good', friendly: 'good', neutral: '', wary: 'warn', enemy: 'bad' };
  /** What a Strike or an Aid moves: 2 marks, 3 once the tower is A power in the land. */
  const markStep = (m) => (m.tower && m.tower.tier !== null && m.tower.tier >= 3 ? 3 : 2);
  /** A goal's clock: its marks as boxes, and the count in words. */
  function clockHtml(c, cls = '') {
    if (!c || c.size === null) return '';
    const n = Math.max(0, Math.min(c.size, c.marks));
    const boxes = Array.from({ length: c.size }, (_, i) => `<i${i < n ? ' class="on"' : ''}></i>`).join('');
    const waits = c.waits ? `<small>done, waits for ${esc(fmt.gp(c.waits))}</small>` : '';
    return `<span class="clock${cls ? ` ${cls}` : ''}" role="img" aria-label="${esc(`${n} of ${c.size} marks`)}"><span class="boxes">${boxes}</span><b>${esc(`${n} of ${c.size}`)}</b>${waits}</span>`;
  }
  /** The tower's Hold boxes. */
  function holdHtml(hold, max) {
    const h = hold === null ? 0 : hold;
    const mx = max === null ? 3 : max;
    return `<span class="hold" role="img" aria-label="${esc(`Hold ${h} of ${mx}`)}"><span class="boxes">${Array.from({ length: mx }, (_, i) => `<i${i < h ? ' class="on"' : ''}></i>`).join('')}</span><b>Hold ${esc(h)} of ${esc(mx)}</b></span>`;
  }
  /** The hex a v3 realm's goal is aimed at (its seat for goals with no hex; the target's seat for a goal at a realm). */
  function aimHex(m, f) {
    const c = f.clock;
    if (!c) return f.seat;
    if (c.hex) return c.hex;
    if (c.target && isTower(c.target)) return m.tower ? m.tower.seat : null;
    if (c.target) { const o = m.facs.get(c.target); return o ? o.seat : f.seat; }
    return f.seat;
  }
  const isTower = (n) => n === 'tower' || n === 'the tower';
  const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : '');
  /** "the Orcs" / "the tower" */
  const the = (n) => (isTower(n) ? 'the tower' : n ? `the ${n}` : 'nobody');
  /** "the Orcs'" / "the Goblinkind's" / "the tower's" */
  const poss = (n) => (isTower(n) ? "the tower's" : !n ? "nobody's" : /s$/.test(n) ? `the ${n}'` : `the ${n}'s`);
  const plural = (n, one, many) => `${fmt.n(n)} ${n === 1 ? one : many || `${one}s`}`;
  const days = (d) => plural(d, 'day');
  /** The engine's asset ids ("Caravans a8") are not for the reader. */
  const noIds = (s) => String(s || '').replace(/\s+a\d+\b/g, '');
  const L = { F: 'Force', C: 'Cunning', W: 'Wealth' };
  /** "F vs F, 1d6" -> "hits with Force against Force for 1d6" (when kinds lacks the words). */
  function attackWords(att) {
    const m = /^\s*([FCW])\s*vs\s*([FCW])\s*,\s*(.+)$/i.exec(att || '');
    if (!m) return att ? `attacks: ${att}` : "doesn't attack";
    return `hits with ${L[m[1].toUpperCase()]} against ${L[m[2].toUpperCase()]} for ${m[3]}`;
  }

  // ---------- geometry (flat-top hexes, the mockup's) ----------
  const S = 58;
  const HH = (Math.sqrt(3) / 2) * S;
  const PAD = 10;
  const f1 = (n) => (Math.round(n * 10) / 10).toString();
  const corners = (x, y, s = S) => [0, 1, 2, 3, 4, 5].map((i) => [x + s * Math.cos((Math.PI / 3) * i), y + s * Math.sin((Math.PI / 3) * i)]);
  const pts = (x, y, s = S) => corners(x, y, s).map((p) => `${f1(p[0])},${f1(p[1])}`).join(' ');

  // ---------- the model: what every part reads, built once per realm doc and origin ----------
  let memo = { realm: null, origin: null, state: null, m: null };
  function model(realm, state) {
    const origin = (state && state.hex) || (realm.morten && realm.morten.hex) || '';
    if (memo.realm === realm && memo.origin === origin && memo.state === state) return memo.m;
    const byId = new Map(realm.hexes.map((h) => [h.id, h]));
    const facs = new Map(realm.factions.map((f) => [f.name, f]));
    const lay = realm.layout || {};
    const shifted = (c) => (lay.shift === 'even' ? c % 2 === 0 : c % 2 !== 0);
    const centre = new Map();
    for (const h of realm.hexes) centre.set(h.id, [h.col * 1.5 * S, h.row * 2 * HH + (shifted(h.col) ? HH : 0)]);
    const xs = [...centre.values()].map((p) => p[0]);
    const ys = [...centre.values()].map((p) => p[1]);
    const box = { x: Math.min(...xs) - S - PAD, y: Math.min(...ys) - HH - PAD };
    box.w = Math.max(...xs) + S + PAD - box.x;
    box.h = Math.max(...ys) + HH + PAD - box.y;
    const edgeOf = (a, b) => {
      const ca = centre.get(a);
      const cb = centre.get(b);
      if (!ca || !cb) return null;
      const pa = corners(ca[0], ca[1]);
      const pb = corners(cb[0], cb[1]);
      const same = pa.filter((p) => pb.some((q) => Math.hypot(p[0] - q[0], p[1] - q[1]) < 0.5));
      return same.length === 2 ? same : null;
    };
    // neighbours: the engine's, else the geometry's
    const nbrs = new Map();
    for (const h of realm.hexes) {
      const given = h.neighbours.filter((n) => byId.has(n));
      nbrs.set(h.id, given.length ? given : realm.hexes.filter((o) => o.id !== h.id && edgeOf(h.id, o.id)).map((o) => o.id));
    }
    // days from Morten and the way: breadth first from his hex
    const hops = new Map();
    const way = new Map();
    if (byId.has(origin)) {
      hops.set(origin, 0);
      way.set(origin, [origin]);
      const q = [origin];
      while (q.length) {
        const id = q.shift();
        for (const n of nbrs.get(id) || []) {
          if (hops.has(n)) continue;
          hops.set(n, hops.get(id) + 1);
          way.set(n, [...way.get(id), n]);
          q.push(n);
        }
      }
    }
    const useDays = realm.morten && realm.morten.hex === origin;
    const dayOf = (id) => (useDays && typeof realm.days[id] === 'number' ? realm.days[id] : hops.has(id) ? hops.get(id) : null);
    // v2: hostile realms (a timer); v3: enemies (standing −2)
    const hostile = new Set(realm.factions.filter((f) => !f.tower && (V3(realm) ? f.standing !== null && f.standing <= -2 : f.hostile > 0)).map((f) => f.name));
    const piecesOf = new Map();
    for (const h of realm.hexes) for (const a of h.assets) {
      if (!piecesOf.has(a.owner)) piecesOf.set(a.owner, []);
      piecesOf.get(a.owner).push({ a, h });
    }
    const evAt = new Map();
    for (const e of realm.eventsWords) for (const id of new Set([e.from, e.to])) {
      if (!id || !byId.has(id)) continue;
      if (!evAt.has(id)) evAt.set(id, []);
      evAt.get(id).push(e);
    }
    const riversAt = new Map();
    for (const [a, b] of realm.rivers) {
      if (!riversAt.has(a)) riversAt.set(a, []);
      if (!riversAt.has(b)) riversAt.set(b, []);
      riversAt.get(a).push(b);
      riversAt.get(b).push(a);
    }
    const tower = realm.factions.find((f) => f.tower) || null;
    const m = { realm, state, origin, byId, facs, centre, box, edgeOf, nbrs, dayOf, way, hostile, piecesOf, evAt, riversAt, tower };
    memo = { realm, origin, state, m };
    return m;
  }

  const nameOf = (m, id) => {
    const given = m.realm.hexNames[id];
    if (given) return given;
    const h = m.byId.get(id);
    return h ? `${poss(h.holder)} ${h.biome || 'land'}${h.lake ? ' with its lake' : ''}` : id;
  };
  const leaderOf = (f) => (f && f.leader && f.leader.name ? `${f.leader.title ? `${f.leader.title} ` : ''}${f.leader.name}` : '');

  // ---------- small parts ----------
  function hexBtn(m, id) {
    const h = m.byId.get(id);
    if (!h) return '';
    const d = m.dayOf(id);
    const seat = h.seat_of && !isTower(h.seat_of) ? icon('crown') : isTower(h.seat_of) ? icon('tower') : '';
    const bits = [h.level !== null ? `level ${h.level}` : '', d === 0 ? 'Morten is here' : d !== null ? days(d) : '', id].filter(Boolean);
    return `<button type="button" class="hexbtn ${fac(h.holder)}" data-hex="${esc(id)}"><span class="sw"></span>${seat}<span class="hn"><span>${esc(cap(nameOf(m, id)))}</span><small>${esc(bits.join(' · '))}</small></span></button>`;
  }

  const pips = (n, max = 3) => `<span class="pips" aria-label="tier ${n}">${Array.from({ length: max }, (_, i) => `<i${i < n ? '' : ' class="off"'}></i>`).join('')}</span>`;

  /** What a piece does, in words, from kinds (else the engine's notation, translated). */
  function pieceWords(a, k) {
    const parts = [];
    if (k) {
      if (k.hits) parts.push(k.hits);
      if (k.counter) parts.push(k.counter);
      if (k.upkeep) parts.push(`upkeep ${fmt.gp(k.upkeep)} a month`);
      if (k.income) parts.push(`+${fmt.gp(k.income)} a month to its owner`);
      for (const s of (k.special || '').split(/;\s*/)) if (s && !/^(income|upkeep)\b/.test(s)) parts.push(s);
    } else {
      parts.push(attackWords(a.attack));
      if (a.counter) parts.push(`hits back ${a.counter}`);
      if (a.special) parts.push(a.special);
    }
    return cap(parts.join('; '));
  }

  /** Strike / Rob, per realms.md's missions; nothing for the tower's own pieces. */
  function missions(m, a, k) {
    if (isTower(a.owner)) return '';
    const tier = a.tier || (k && k.tier) || 1;
    const fight = (k && k.fight) || `${DIFF[Math.min(3, Math.max(1, tier)) - 1]} fight`;
    const out = [`<span>Strike: a ${esc(fight)}, 2d6 to it</span>`];
    if (typeOf(a, k) === 'W') {
      const f = m.facs.get(a.owner);
      let gp = tier * 100 * (a.name === 'Treasury' ? 2 : 1);
      if (f && typeof f.treasury === 'number') gp = Math.min(gp, f.treasury);
      out.push(`<span>${gp > 0 ? `Rob: up to ${esc(fmt.gp(gp))}` : 'Rob: their coffers are empty'}</span>`);
    }
    return `<div class="do">${out.join('')}</div>`;
  }

  /** v3: a site's row (a seat, a garrison, works or walls): its fight tier, its effect, Strike / Rob. */
  function siteRow(m, a, h, opts = {}) {
    const k = m.realm.kinds[a.name] || null;
    const glyph = (k && k.glyph) || SITE_GLYPH[a.type] || 'hex';
    const tier = Math.max(1, Math.min(3, a.tier || 1));
    const enemy = m.hostile.has(a.owner);
    const what = k && k.what ? k.what : a.type || 'a site';
    const where = opts.where && h ? (() => {
      const d = m.dayOf(h.id);
      return `<small class="at">in ${esc(nameOf(m, h.id))} · ${esc(d === 0 ? 'where Morten is' : d !== null ? `${days(d)} from Morten` : h.id)}</small>`;
    })() : '';
    const f = m.facs.get(a.owner);
    const step = markStep(m);
    let dos = '';
    if (!isTower(a.owner) && opts.missions !== false) {
      const out = [`<span>Strike: a ${esc(DIFF[tier - 1])} fight, ${esc(step)} marks off their goal</span>`];
      if (a.type === 'works') {
        let gp = 100 * (f && f.force !== null ? f.force : 1);
        if (f && typeof f.treasury === 'number') gp = Math.min(gp, f.treasury);
        out.push(`<span>${gp > 0 ? `Rob: a ${esc(DIFF[tier - 1])} fight, up to ${esc(fmt.gp(gp))}` : 'Rob: their coffers are empty'}</span>`);
      }
      dos = `<div class="do">${out.join('')}</div>`;
    }
    return `<div class="piece site ${fac(a.owner)}${enemy ? ' hostile' : ''}" data-piece="${esc(a.id)}">`
      + `<span class="tok-big site" title="${esc(cap(a.type || 'site'))}">${icon(glyph)}</span>`
      + '<div class="body">'
      + `<div class="pn"><b>${esc(a.name || 'A site')}</b>${opts.owner === false ? '' : `<span>${esc(poss(a.owner))}</span>`}<small>${esc(what)}</small>${enemy ? `<span class="hos">${icon('skull')}enemy</span>` : ''}</div>`
      + `<div class="hp">${pips(tier)}<span>tier ${esc(tier)} · a ${esc(DIFF[tier - 1])} fight</span></div>`
      + (k && k.effect ? `<p class="what">${esc(k.effect)}</p>` : '')
      + where
      + dos
      + '</div></div>';
  }

  /** A piece (v2) or a site (v3), one row. */
  const assetRow = (m, a, h, opts) => (V3(m.realm) ? siteRow(m, a, h, opts) : pieceRow(m, a, h, opts));

  function pieceRow(m, a, h, opts = {}) {
    const k = m.realm.kinds[a.name] || null;
    const t = typeOf(a, k);
    const tier = a.tier || (k && k.tier) || 1;
    const hostile = m.hostile.has(a.owner);
    const what = k && k.what ? k.what : `${L[t]} piece`;
    const where = opts.where && h ? (() => {
      const d = m.dayOf(h.id);
      return `<small class="at">in ${esc(nameOf(m, h.id))} · ${esc(d === 0 ? 'where Morten is' : d !== null ? `${days(d)} from Morten` : h.id)}</small>`;
    })() : '';
    return `<div class="piece ${fac(a.owner)}${hostile ? ' hostile' : ''}" data-piece="${esc(a.id)}">`
      + `<span class="tok-big ${band(a.hp, a.max_hp)}" title="${esc(L[t])}">${icon(ATTR[t][0])}</span>`
      + '<div class="body">'
      + `<div class="pn"><b>${esc(a.name || 'A piece')}</b>${opts.owner === false ? '' : `<span>${esc(poss(a.owner))}</span>`}<small>tier ${esc(tier)} · ${esc(what)}</small>${hostile ? `<span class="hos">${icon('skull')}hostile</span>` : ''}</div>`
      + `<div class="hp">${icon('heart')}${bar(a.hp, a.max_hp)}<span>${esc(fmt.hp(a.hp, a.max_hp))}</span>${pips(tier)}</div>`
      + `<p class="what">${esc(pieceWords(a, k))}</p>`
      + where
      + (opts.missions === false ? '' : missions(m, a, k))
      + '</div></div>';
  }

  // ---------- the tower card ----------
  function nextChips(lines) {
    return lines.map((s) => {
      const mm = /^\s*(threat|chance|open)\s*:\s*(.*)$/i.exec(s);
      return mm ? T.ui.chip(mm[2], { kind: mm[1].toLowerCase() }) : T.ui.chip(s);
    }).join('');
  }

  function realmLink(f) {
    const st = f.hostile > 0 ? ` <small>${esc(plural(f.hostile, 'month'))} left</small>` : '';
    return `<button type="button" class="rlink ${fac(f.name)}" data-goto-realm="${esc(f.name)}"><span class="sw"></span>${esc(f.name)}${st}</button>`;
  }

  /** v3: tier and Renown, Hold, gold, the goal as a clock, sites, land, allies and enemies. */
  function towerCard3(m) {
    const t = m.tower;
    const r = m.realm;
    const allies = r.factions.filter((f) => !f.tower && f.ally);
    const enemies = r.factions.filter((f) => !f.tower && f.standing !== null && f.standing <= -2);
    const own = (m.piecesOf.get(t.name) || []).concat(t.name !== 'tower' ? (m.piecesOf.get('tower') || []) : []);
    const tier = `<div class="tierline" title="${esc(r.words.tier || '')}">${icon('crown')}<b>${esc(t.tierName || 'Hermit')}</b><small>tier ${esc(t.tier !== null ? t.tier : 0)} · Renown ${esc(t.renown !== null ? t.renown : 0)}</small></div>`;
    const hold = `<div class="holdline" title="${esc(r.words.hold || '')}">${icon('shield')}${holdHtml(t.hold, t.maxHold)}</div>`;
    const gold = `<p class="gold"><b>${esc(fmt.gp(t.treasury) || '? GP')}</b> in the coffers, <b>${esc(t.income !== null ? `${fmt.signed(t.income)} GP` : '? GP')}</b> a month</p>`;
    const c = t.clock;
    const goal = c
      ? `<div class="sub"><span class="label">The tower's goal</span><p class="goal">${icon('flag')}<span><b>${esc(cap(c.text))}</b> ${clockHtml(c)}${c.kind && r.goalWords[c.kind] ? `<small class="muted">When full: ${esc(r.goalWords[c.kind])}.</small>` : ''}</span></p></div>`
      : '<p class="muted small">No goal yet: declare one with the month\'s orders (take a hex, win an ally or topple a ruler). Its marks come from Morten\'s deeds and from allies, never from dice.</p>';
    const lines = r.nextWords.length ? r.nextWords : r.report.next;
    const next = lines.length
      ? `<div class="nextm"><span class="label">What month ${esc(r.month !== null ? r.month : (r.report.month || 0) + 1)} can bring</span><div class="chips">${nextChips(lines)}</div></div>`
      : '';
    const found = r.dissidents.length
      ? `<div class="sub"><span class="label">Dissidents found</span><ul class="heard">${r.dissidents.map((d) => `<li class="${fac(d.realm)}">${icon('speech')}<span><b>${esc(d.name)}</b>, of ${esc(the(d.realm))}${d.hex ? ` in ${esc(cap(nameOf(m, d.hex)))}` : ''}: the tower can declare a topple there</span></li>`).join('')}</ul></div>`
      : '';
    const won = t.won !== null ? `<p class="brass"><b>The world is his</b> (since month ${esc(t.won)}).</p>` : '';
    return '<div class="card tower v3">'
      + `<h3>${icon('tower')}The tower<small>yours</small></h3>`
      + tier
      + note('realm-ladder', '<b>Renown</b> is hexes held beyond the tower\'s own, plus allies, plus 2 for each ruler toppled; it climbs a ladder of five tiers, each with a power. <b>Hold</b> is three boxes: a realm\'s <i>break the tower</i> goal that fires takes one, and half the gold.')
      + hold
      + gold
      + won
      + goal
      + (own.length ? `<div class="sub"><span class="label">Its sites · ${esc(own.length)}</span><div class="pieces">${own.map(({ a, h }) => siteRow(m, a, h, { owner: false, missions: false, where: true })).join('')}</div></div>` : '<p class="muted small">No sites yet: works for income, and from Lord of the hex a garrison and walls for its hexes.</p>')
      + (t.hexes.length ? `<div class="sub"><span class="label">Its land</span><div class="hexbtns">${t.hexes.map((id) => hexBtn(m, id)).join('')}</div></div>` : '')
      + `<div class="rel"><span class="label">Allies</span><span class="links">${allies.length ? allies.map(realmLink).join('') : '<span class="muted">none</span>'}</span>`
      + `<span class="label">Enemies</span><span class="links">${enemies.length ? enemies.map(realmLink).join('') : '<span class="muted">nobody</span>'}</span></div>`
      + found
      + next
      + '</div>';
  }

  function towerCard(m) {
    const t = m.tower;
    const r = m.realm;
    if (!t) return '';
    if (V3(r)) return towerCard3(m);
    const allies = r.factions.filter((f) => !f.tower && f.ally);
    const hostile = r.factions.filter((f) => !f.tower && f.hostile > 0);
    const own = (m.piecesOf.get(t.name) || []).concat(t.name !== 'tower' ? (m.piecesOf.get('tower') || []) : []);
    const attrs = ['force', 'cunning', 'wealth'].map((k, i) => {
      const c = 'FCW'[i];
      return `<span title="${esc(r.words[k] || '')}">${icon(ATTR[c][0])}${ATTR[c][1]} <b>${esc(fmt.n(t[k]))}</b></span>`;
    }).join('<span class="dot" aria-hidden="true">·</span>');
    // a hex of the tower's with another realm's soldiers in it pays it nothing: say so
    const held = t.hexes.map((id) => m.byId.get(id)).filter(Boolean)
      .map((h) => ({ h, by: h.assets.filter((a) => a.owner !== h.holder && typeOf(a, r.kinds[a.name]) === 'F').map((a) => a.owner) }))
      .filter((x) => x.by.length);
    const why = held.length ? ` <small class="warn">(${esc(held.map((x) => `${poss(x.by[0])} soldiers hold ${x.h.id}`).join('; '))}: no income from it)</small>` : '';
    const gold = `<p class="gold"><b>${esc(fmt.gp(t.treasury) || '? GP')}</b> in the coffers, <b>${esc(t.income !== null ? `${fmt.signed(t.income)} GP` : '? GP')}</b> a month${why}</p>`;
    const lines = r.nextWords.length ? r.nextWords : r.report.next;
    const next = lines.length
      ? `<div class="nextm"><span class="label">What month ${esc(r.month !== null ? r.month : (r.report.month || 0) + 1)} can bring</span><div class="chips">${nextChips(lines)}</div></div>`
      : '';
    const found = r.dissidents.length
      ? `<div class="sub"><span class="label">Dissidents found</span><ul class="heard">${r.dissidents.map((d) => `<li class="${fac(d.realm)}">${icon('speech')}<span><b>${esc(d.name)}</b>, of ${esc(the(d.realm))}${d.hex ? ` in ${esc(cap(nameOf(m, d.hex)))}` : ''}: the tower can buy Seditionists there</span></li>`).join('')}</ul></div>`
      : '';
    return '<div class="card tower">'
      + `<h3>${icon('tower')}The tower<small>yours</small></h3>`
      + `<div class="hpbig">${icon('heart')}${bar(t.hp, t.max_hp)}<b>Regime ${esc(fmt.n(t.hp))}/${esc(fmt.n(t.max_hp))}</b></div>`
      + note('realm-regime', '<b>Regime</b> is the tower\'s health as a power. At 0 it is sacked: whoever brought it down carries off half its gold, and the wards still hold the hex.')
      + `<div class="attrs">${attrs}</div>`
      + gold
      + (own.length ? `<div class="sub"><span class="label">Its pieces · ${esc(own.length)}</span><div class="pieces">${own.map(({ a, h }) => pieceRow(m, a, h, { owner: false, missions: false, where: true })).join('')}</div></div>` : '<p class="muted small">No pieces yet: soldiers, spies or income the tower puts on the map.</p>')
      + (t.hexes.length ? `<div class="sub"><span class="label">Its land</span><div class="hexbtns">${t.hexes.map((id) => hexBtn(m, id)).join('')}</div></div>` : '')
      + `<div class="rel"><span class="label">Allies</span><span class="links">${allies.length ? allies.map(realmLink).join('') : '<span class="muted">none</span>'}</span>`
      + `<span class="label">Hostile</span><span class="links">${hostile.length ? hostile.map(realmLink).join('') : '<span class="muted">nobody</span>'}</span></div>`
      + found
      + next
      + '</div>';
  }

  // ---------- the map ----------
  const LAND = {
    mountains: 'M-10 6l6-10 4 6 3-4 7 8',
    hills: 'M-10 5q5-8 10-2q4-5 10 2',
    forest: 'M0 7v-4M0 3a5 5 0 1 1 .1 0M-4.6-.5h9.2',
    taiga: 'M0-8l4 5h-2l3 4h-2l3 4h-12l3-4h-2l3-4h-2zM0 5v3',
    tundra: 'M0-7v14M-6-3.5l12 7M-6 3.5l12-7M-2-6l2 2 2-2M-2 6l2-2 2 2',
    plains: 'M-8 6l-1-6M-8 6l2-5M0 6v-8M0 6l-3-5M0 6l3-5M8 6l1-6M8 6l-2-5',
    savanna: 'M-9 6h18M0 6v-6M0 0l-6-3M0 0l6-3M-7-3.5h14',
    swamp: 'M-9 4q3-4 6 0t6 0t6 0M-4 3v-7M0 2v-8M4 3v-6M0-6l-1.5 2',
    desert: 'M-10 6q5-7 10-2q4-5 10 2M4-6a2.5 2.5 0 1 0 .1 0',
    jungle: 'M0 7q1-6 0-11M0-4q-5-3-9 0M0-4q5-3 9 0M0-4q-3-4-7-6M0-4q3-4 7-6',
  };
  const landGlyph = (b) => LAND[b] || 'M-1 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0';

  function tokens(m, h, x, y) {
    const list = h.assets;
    if (!list.length) return '';
    const more = list.length > 6 ? list.length - 5 : 0;
    const shown = more ? list.slice(0, 5) : list;
    const n = shown.length + (more ? 1 : 0);
    const two = n > 3;
    const r = two ? 6.6 : 8.2;
    const ringR = r + 2.2;
    const step = 2 * ringR + 2.4;
    let out = '';
    const place = (i) => {
      const inRow = !two ? n : i < 3 ? 3 : n - 3;
      const k = !two || i < 3 ? i : i - 3;
      const cy = !two ? y + 16 : y + (i < 3 ? 8 : 31);
      return [x - ((inRow - 1) * step) / 2 + k * step, cy];
    };
    const v3 = V3(m.realm);
    shown.forEach((a, i) => {
      const [cx, cy] = place(i);
      const k = m.realm.kinds[a.name] || null;
      const t = typeOf(a, k);
      const tier = Math.max(1, Math.min(3, a.tier || (k && k.tier) || 1));
      const ok = typeof a.hp === 'number' && typeof a.max_hp === 'number' && a.max_hp > 0;
      const rt = ok ? Math.max(0, Math.min(1, a.hp / a.max_hp)) : 1;
      const circ = 2 * Math.PI * ringR;
      const g = r * 1.3;
      const hostile = m.hostile.has(a.owner);
      // v3: a site has no health; its token carries the site's glyph and a plain ring
      const glyph = v3 ? (k && k.glyph) || SITE_GLYPH[a.type] || 'hex' : ATTR[t][0];
      out += `<g class="tokn ${fac(a.owner)}${hostile ? ' hos' : ''}${v3 ? ' site' : ''}" data-piece="${esc(a.id)}">`
        + `<circle class="ring" cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(ringR)}"/>`
        + (v3 ? '' : `<circle class="ring on ${band(a.hp, a.max_hp)}" cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(ringR)}" stroke-dasharray="${f1(circ * rt)} ${f1(circ)}" transform="rotate(-90 ${f1(cx)} ${f1(cy)})"/>`)
        + `<circle class="tok" cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(r)}"/>`
        + `<use class="tok-g" href="#i-${glyph}" x="${f1(cx - g / 2)}" y="${f1(cy - g / 2)}" width="${f1(g)}" height="${f1(g)}"/>`
        + (hostile ? `<circle class="hostile" cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(ringR + 2.2)}"/><circle class="skull-b" cx="${f1(cx + r * 0.95)}" cy="${f1(cy - r * 0.95)}" r="4.6"/><use class="skull-g" href="#i-skull" x="${f1(cx + r * 0.95 - 3.6)}" y="${f1(cy - r * 0.95 - 3.6)}" width="7.2" height="7.2"/>` : '');
      for (let p = 0; p < tier; p++) out += `<circle class="pip" cx="${f1(cx - (tier - 1) * 1.8 + p * 3.6)}" cy="${f1(cy + ringR + 2.9)}" r="1.25"/>`;
      out += '</g>';
    });
    if (more) {
      const [cx, cy] = place(5);
      out += `<g class="tokn more"><circle class="tok" cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(r)}"/><text class="more-t" x="${f1(cx)}" y="${f1(cy + 3)}" text-anchor="middle">+${more}</text></g>`;
    }
    return out;
  }

  const crownAt = (owner, x, y) => `<g class="${fac(owner)}" transform="translate(${f1(x)} ${f1(y)})"><path class="crown" d="M-7 5h14M-7 5l-1-9 4.5 3.5L0-6l3.5 5.5L8-4l-1 9z"/></g>`;
  const towerAt = (x, y) => `<g class="fac-tower" transform="translate(${f1(x)} ${f1(y)})"><path class="tower-g" d="M-6 7V-4h2.4v-3h2.2v3h2.8v-3h2.2v3H6V7zM-1.6 7V3h3.2v4"/></g>`;

  function arrows(m) {
    let out = '';
    const self = new Map();
    for (const e of m.realm.eventsWords) {
      if (e.n === null) continue;
      const a = m.centre.get(e.from);
      const b = m.centre.get(e.to);
      const cls = fac(e.who);
      const on = evShown === e.n ? ' on' : '';
      if (a && b && e.from !== e.to) {
        const [x1, y1] = a;
        const [x2, y2] = b;
        const dx = x2 - x1;
        const dy = y2 - y1;
        const len = Math.hypot(dx, dy) || 1;
        const ux = dx / len;
        const uy = dy / len;
        const sx = x1 + ux * 18;
        const sy = y1 + uy * 18;
        const ex = x2 - ux * 30;
        const ey = y2 - uy * 30;
        const bend = 0.22 * len * (e.n % 2 ? 1 : -1);
        const cx = (sx + ex) / 2 - uy * bend;
        const cy = (sy + ey) / 2 + ux * bend;
        const tx = ex - cx;
        const ty = ey - cy;
        const tl = Math.hypot(tx, ty) || 1;
        const hx = tx / tl;
        const hy = ty / tl;
        const head = `${f1(ex + hx * 6)},${f1(ey + hy * 6)} ${f1(ex - hx * 6 - hy * 6)},${f1(ey - hy * 6 + hx * 6)} ${f1(ex - hx * 6 + hy * 6)},${f1(ey - hy * 6 - hx * 6)}`;
        const mx = 0.25 * sx + 0.5 * cx + 0.25 * ex;
        const my = 0.25 * sy + 0.5 * cy + 0.25 * ey;
        const d = `M${f1(sx)} ${f1(sy)}Q${f1(cx)} ${f1(cy)} ${f1(ex)} ${f1(ey)}`;
        out += `<g class="mv ${cls}${on}"><path class="arrow-halo" d="${d}"/><path class="arrow" d="${d}"/><polygon class="head-a" points="${head}"/>${badge(e, mx, my)}</g>`;
      } else {
        const id = a ? e.from : b ? e.to : null;
        if (!id) continue;
        const k = self.get(id) || 0;
        self.set(id, k + 1);
        const [x, y] = m.centre.get(id);
        out += `<g class="mv ${cls}${on}">${badge(e, x - 41, y - 13 + k * 19)}</g>`;
      }
    }
    return out;
  }
  const badge = (e, x, y) => `<circle class="badge" cx="${f1(x)}" cy="${f1(y)}" r="8.5"/><text class="badge-t" x="${f1(x)}" y="${f1(y + 3.5)}" text-anchor="middle">${esc(e.n)}</text>`
    + `<circle class="evhit" data-ev="${esc(e.n)}" cx="${f1(x)}" cy="${f1(y)}" r="15" role="button" tabindex="0" aria-label="Move ${esc(e.n)}: ${esc(e.text)}"/>`;

  function mapSvg(m) {
    const land = [];
    const marks = [];
    const hits = [];
    const borders = [];
    const rivers = [];
    for (const h of m.realm.hexes) {
      const [x, y] = m.centre.get(h.id);
      land.push(`<polygon class="land ${fac(h.holder)}" points="${pts(x, y)}"/>`);
      if (h.lake) marks.push(`<ellipse class="lake" cx="${f1(x - 1)}" cy="${f1(y - 39)}" rx="9" ry="4.5"/>`);
      marks.push(`<text class="hid" x="${f1(x + S - 15)}" y="${f1(y + 4)}" text-anchor="middle">${esc(h.id)}</text>`);
      if (h.level !== null) marks.push(`<text class="lvl" x="${f1(x)}" y="${f1(y - 5)}" text-anchor="middle">${esc(h.level)}</text>`);
      marks.push(`<path class="glyph" transform="translate(${f1(x + 25)} ${f1(y - 13)})" d="${landGlyph(h.biome)}"/>`);
      if (h.seat_of) marks.push(isTower(h.seat_of) ? towerAt(x - 24, y - 35) : crownAt(h.seat_of, x - 24, y - 34));
      marks.push(tokens(m, h, x, y));
      const d = m.dayOf(h.id);
      const label = `${cap(nameOf(m, h.id))}, level ${h.level}${d === 0 ? ', Morten is here' : d !== null ? `, ${days(d)} from Morten` : ''} (${h.id})`;
      hits.push(`<polygon class="hit" data-hex="${esc(h.id)}" points="${pts(x, y)}" tabindex="0" role="button" aria-label="${esc(label)}"/>`);
    }
    const seen = new Set();
    for (const h of m.realm.hexes) for (const nid of m.nbrs.get(h.id) || []) {
      const key = [h.id, nid].sort().join('|');
      if (seen.has(key)) continue;
      seen.add(key);
      const n = m.byId.get(nid);
      if (!n || (h.holder || '') === (n.holder || '')) continue;
      const e = m.edgeOf(h.id, nid);
      if (e) borders.push(`M${f1(e[0][0])} ${f1(e[0][1])}L${f1(e[1][0])} ${f1(e[1][1])}`);
    }
    for (const [a, b] of m.realm.rivers) {
      const e = m.edgeOf(a, b);
      if (e) rivers.push(`M${f1(e[0][0])} ${f1(e[0][1])}L${f1(e[1][0])} ${f1(e[1][1])}`);
    }
    let mort = '';
    const mc = m.centre.get(m.origin);
    if (mc) {
      const [mx, my] = mc;
      mort = `<polygon class="morten-ring" points="${pts(mx, my, S - 6)}"/><g class="morten" transform="translate(${f1(mx + 22)} ${f1(my - 35)})"><circle class="morten-pin" r="9.5"/><path class="morten-g" d="M0-6l3.6 7.5H-3.6zM-4.5 3h9l.8 2.2h-10.6z"/></g>`;
    }
    const pc = m.centre.get(picked);
    const pick = pc ? `<polygon class="picked" points="${pts(pc[0], pc[1], S - 2)}"/>` : '';
    const b = m.box;
    return `<svg class="map${codes ? '' : ' nocodes'}" viewBox="${f1(b.x)} ${f1(b.y)} ${f1(b.w)} ${f1(b.h)}" role="group" aria-label="The realms' map: tap a hex for its entry">`
      + `<g>${land.join('')}</g><path class="border" d="${borders.join('')}"/><path class="river" d="${rivers.join('')}"/>`
      + `<g pointer-events="none">${marks.join('')}</g><g pointer-events="none">${mort}</g><g pointer-events="none">${pick}</g>`
      + `<g>${hits.join('')}</g>`
      + (moves ? `<g class="moves">${arrows(m)}</g>` : '')
      + '</svg>';
  }

  function keyOver3() {
    const tok = (g, c = 'fac-humans') => `<span class="ktok site ${c}">${icon(g)}</span>`;
    return `<div class="keyover" role="dialog" aria-label="The map's key"><ul>`
      + `<li><b class="klvl">18</b><span>The big number is a hex's <b>level</b>: the floor under it, how bad its wanderers are, and its income (level × 10 GP a month).</span></li>`
      + `<li>${tok('crown')}<span>A <b>seat</b>: the ruler's court, the realm's hardest fight. A Strike there costs 2 standing.</span></li>`
      + `<li>${tok('shield')}<span>A <b>garrison</b>: −1 to goal rolls aimed at its hex.</span></li>`
      + `<li>${tok('globe')}<span><b>Works</b> (farms, a mine, caravans): +50 GP a month to its owner; what a Rob takes from.</span></li>`
      + `<li>${tok('door')}<span><b>Walls</b>: −1 more to goal rolls at the hex; a take against it needs 6 marks.</span></li>`
      + `<li><span class="kpips">${pips(2)}</span><span>The pips under a token: the site's fight tier, 1 to 3 (a Low, Moderate or High fight for Morten).</span></li>`
      + `<li><span class="kic bad">${icon('skull')}</span><span>A red ring and a skull: the owner is an enemy of the tower (standing −2).</span></li>`
      + `<li><span class="kic">${icon('tower')}</span><span>The tower: your seat, warded.</span></li>`
      + `<li><span class="kic">${icon('pin')}</span><span>Morten, and the dashed brass ring round his hex.</span></li>`
      + `<li><span class="kn">3</span><span>Last month's moves, numbered as in the story's world's turn; tap a number for its sentence.</span></li>`
      + `<li><span class="kriv"></span><span>A river. The lines between colours are borders.</span></li>`
      + `</ul><button type="button" class="toggle" data-t="key" aria-pressed="true">Close the key</button></div>`;
  }

  function keyOver() {
    if (last && last.realm && V3(last.realm)) return keyOver3();
    const tok = (g, c = 'fac-humans') => `<span class="ktok ${c}">${icon(g)}</span>`;
    return `<div class="keyover" role="dialog" aria-label="The map's key"><ul>`
      + `<li><b class="klvl">18</b><span>The big number is a hex's <b>level</b>: the floor under it, how bad its wanderers are, and its income (level × 10 GP a month).</span></li>`
      + `<li>${tok('sword')}<span>Soldiers (Force): they take land and break pieces.</span></li>`
      + `<li>${tok('mask')}<span>Spies (Cunning): they see, sabotage and chip at a regime.</span></li>`
      + `<li>${tok('coins')}<span>Income (Wealth): farms, caravans, mines, a treasury.</span></li>`
      + `<li><span class="kpips">${pips(2)}</span><span>The pips under a token: its tier, 1 to 3. The ring round it: its health.</span></li>`
      + `<li><span class="kic bad">${icon('skull')}</span><span>A red ring and a skull: the owner is hostile to the tower.</span></li>`
      + `<li><span class="kic">${icon('crown')}</span><span>A ruler's seat, in the realm's colour.</span></li>`
      + `<li><span class="kic">${icon('tower')}</span><span>The tower: your seat.</span></li>`
      + `<li><span class="kic">${icon('pin')}</span><span>Morten, and the dashed brass ring round his hex.</span></li>`
      + `<li><span class="kn">3</span><span>Last month's moves, numbered as in the story's world's turn; tap a number for its sentence.</span></li>`
      + `<li><span class="kriv"></span><span>A river: a defender is +1 against attacks over it. The lines between colours are borders.</span></li>`
      + `</ul><button type="button" class="toggle" data-t="key" aria-pressed="true">Close the key</button></div>`;
  }

  function mapBar() {
    const t = (k, label, on) => `<button type="button" class="toggle" data-t="${k}" aria-pressed="${on}">${label}</button>`;
    return t('codes', 'Codes', codes) + t('moves', 'Moves', moves) + t('key', `${icon('q')}<span class="vh">The key</span>`, keyOn)
      + '<span class="hint">Tap a hex for its entry</span>';
  }

  function evLine(m) {
    if (evShown === null) return '';
    const e = m.realm.eventsWords.find((x) => x.n === evShown);
    if (!e) return '';
    return `<ol class="events evline"><li class="${fac(e.who)}"><span class="n">${esc(e.n)}</span><span>${esc(e.text)}</span><button type="button" class="x" data-ev-close aria-label="Close">×</button></li></ol>`;
  }

  // ---------- the hex entry ----------
  function roomsStrip(m, h) {
    const fl = m.realm.floors[h.id];
    const n = fl && fl.floor !== null ? fl.floor : h.level;
    const st = m.state;
    const nowRoom = st && st.hex === h.id ? (/room\s+(\d+\.\d+)/i.exec(st.where || '') || [])[1] : null;
    const rooms = fl ? fl.rooms : [];
    const cells = rooms.map((r) => {
      const known = r.state !== 'unknown' && r.monster;
      const done = r.state === 'cleared';
      const now = r.n === nowRoom || r.state === 'fighting';
      const cls = ['room', done ? 'done' : '', now ? 'now' : ''].filter(Boolean).join(' ');
      const sub = known ? `${r.monster}${r.cr ? ` (CR ${r.cr})` : ''}` : '?';
      const tip = [known ? sub : 'not yet explored', r.state !== 'unknown' ? r.state : '', r.note].filter(Boolean).join(' · ');
      return `<span class="${cls}" title="${esc(tip)}"><b>${esc(r.n)}${done ? ' <i class="ok" aria-label="cleared">✓</i>' : ''}</b><small>${esc(sub)}</small>${r.note ? `<small class="nt">${esc(r.note)}</small>` : ''}</span>`;
    });
    if (!rooms.length) cells.push(`<span class="room"><b>?</b><small>not entered</small></span>`);
    else if (!(fl && fl.cleared) && !rooms.some((r) => r.state === 'unknown')) cells.push('<span class="room"><b>?</b><small>more?</small></span>');
    const head = `The floor under it · floor ${n !== null ? esc(n) : '?'}${fl && fl.cleared ? ' · cleared' : ''}`;
    return `<span class="label">${head}</span><div class="rooms">${cells.join('')}</div>`;
  }

  function entry(m, id) {
    const h = m.byId.get(id);
    if (!h) return '';
    const r = m.realm;
    const v3 = V3(r);
    const home = isTower(h.holder);
    const lv = h.level;
    const d = m.dayOf(id);
    const holder = m.facs.get(h.holder);
    const held = home
      ? (h.warded || !v3 ? `Yours, warded: it can never be ${v3 ? 'taken' : 'seized'}` : 'Yours')
      : h.holder ? `Held by ${esc(the(h.holder))}${h.people === h.holder ? ', their own people' : h.people ? `, ${esc(poss(h.people))} land` : ''}` : 'Held by nobody';
    const occupiers = v3 ? [] : h.assets.filter((a) => a.owner !== h.holder && typeOf(a, r.kinds[a.name]) === 'F').map((a) => a.owner);
    const inc = typeof h.income === 'number' ? h.income : lv !== null ? lv * 10 : null;
    const income = inc === 0 && occupiers.length
      ? `pays ${home ? 'the tower' : 'them'} nothing while ${esc(poss(occupiers[0]))} soldiers stand in it`
      : inc !== null ? `${esc(fmt.gp(inc))} a month to ${home ? 'the tower' : 'them'}` : '';
    const way = m.way.get(id);
    const dist = d === 0 ? '<b class="brass">Morten is here</b>'
      : d !== null ? `<b>${esc(days(d))} from Morten</b>${way && way.length > 1 ? ` <span class="way">(${esc(way.join(' → '))})</span>` : ''}`
        : 'no way there from Morten';
    const riv = m.riversAt.get(id) || [];
    const river = riv.length ? ` · a river edge against ${riv.map((x) => esc(cap(nameOf(m, x)).replace(/^The /, 'the ')) + ` <small class="code">${esc(x)}</small>`).join(', ')}: a defender here is +1 against attacks from there` : '';
    let seat = '';
    if (h.seat_of) seat = isTower(h.seat_of) ? ' The tower stands here.' : ` The seat of ${esc(leaderOf(m.facs.get(h.seat_of)) || 'the ruler')} of ${esc(the(h.seat_of))}.`;

    // missions beyond the pieces: Strike an unguarded seat (v2), Aid (v3), Contact, Delve
    const more = [];
    const om = m.state && m.state.awaiting && m.state.awaiting.orders ? m.state.awaiting.orders.missions : [];
    if (!v3 && h.seat_of && !isTower(h.seat_of) && !h.assets.some((a) => a.owner === h.seat_of && typeOf(a, r.kinds[a.name]) === 'F')) {
      more.push(`<span>Strike the seat: a High fight, 2d6 to ${esc(poss(h.seat_of))} regime</span>`);
    }
    const clocksHere = [];
    if (v3) {
      const step = markStep(m);
      for (const f of r.factions) {
        if (f.tower || !f.clock) continue;
        if (f.clock.hex === id) clocksHere.push(f);
        if (aimHex(m, f) !== id || (f.clock.target && isTower(f.clock.target)) || f.clock.waits) continue;
        const given = om.find((x) => x.type === 'aid' && x.target === f.name && x.hex === id);
        const fight = given && /\((Low|Moderate|High)[^)]*\)/.exec(given.label) ? ` ${/\((Low|Moderate|High)[^)]*\)/.exec(given.label)[1]} fight,` : '';
        more.push(`<span>Aid ${esc(the(f.name))} with ${esc(f.goal)}:${esc(fight)} ${esc(step)} marks on their clock</span>`);
      }
    }
    if (!home && holder) {
      const given = om.find((x) => x.type === 'contact' && (v3 ? x.hex === id : x.target === id));
      const given2 = given && /DC\s*(\d+)/.exec(given.label) ? /DC\s*(\d+)/.exec(given.label)[1] : null;
      if (v3) {
        const enemy = holder.standing !== null && holder.standing <= -2;
        const dc = given2 !== null ? given2 : holder.standing !== null ? 12 + (holder.leader.label === 'bad' ? 3 : 0) - 2 * holder.standing + (holder.squeezed ? 4 : 0) : null;
        more.push(enemy ? `<span>Contact ${esc(the(h.holder))}: refused, they are enemies</span>` : `<span>Contact ${esc(the(h.holder))}: Persuasion${dc !== null ? ` DC ${esc(dc)}` : ''}, standing +1</span>`);
      } else {
        const dc = given2 !== null ? given2 : typeof holder.cunning === 'number' ? 10 + holder.cunning - (holder.leader.tag === 'Tyrant' ? 4 : 0) : null;
        more.push(`<span>Contact the people: Persuasion${dc !== null ? ` DC ${esc(dc)}` : ''}</span>`);
      }
    }
    const pieces = h.assets.length
      ? `<div class="pieces">${h.assets.map((a) => assetRow(m, a, h)).join('')}</div>`
        + (h.assets.some((a) => !isTower(a.owner)) ? `<p class="muted small">${v3 ? 'A Strike or a Rob is a fight for Morten. A won Strike takes marks off the owner\'s goal and costs 1 standing (2 at a seat); a Rob costs 1.' : 'A Strike or a Rob is a fight for Morten, and turns the owner hostile to the tower for 3 months (6 at a seat).'}</p>` : '')
      : '<p class="muted small">Nothing the tower can see stands here.</p>';
    const aimed = clocksHere.length
      ? `<span class="label">Clocks aimed here</span><ul class="heard aimed">${clocksHere.map((f) => `<li class="${fac(f.name)}">${icon('flag')}<span>${esc(the(f.name))}: <b>${esc(f.goal)}</b> ${clockHtml(f.clock)}</span></li>`).join('')}</ul>`
      : '';
    // the orders form is open: send Morten here from the map (the Story's form takes it)
    const aw = m.state && m.state.status === 'awaiting' && m.state.awaiting && m.state.awaiting.kind === 'orders' ? m.state.awaiting.orders : null;
    const oh = aw ? aw.hexes.find((x) => x.id === id) : null;
    const travel = oh
      ? `<div class="travel-here"><button type="button" class="primary" data-travel-here="${esc(id)}">${icon('boots')}Travel here<small>${esc(oh.days === 0 ? 'stay: 0 days' : days(oh.days))}</small></button><span class="muted small">for this month's orders, in the Story</span></div>`
      : '';
    const evs = m.evAt.get(id) || [];
    const heard = r.rumours[id] || [];
    const nb = m.nbrs.get(id) || [];
    return `<h3>${esc(cap(nameOf(m, id)))}${lv !== null ? `, level ${esc(lv)}` : ''}${home ? ' · home' : ''}<span class="code">${esc(id)}</span></h3>`
      + `<p class="line">${[held, income, dist].filter(Boolean).join(' · ')}${river}.</p>`
      + travel
      + (lv !== null ? `<p class="line lvl-line">Level ${esc(lv)}: floor ${esc(lv)} lies under it, and its wanderers are level-${esc(lv)} trouble.${seat}</p>` : seat ? `<p class="line">${seat.trim()}</p>` : '')
      + `<span class="label">${v3 ? 'Sites' : 'Pieces'} here · ${esc(h.assets.length)}</span>${pieces}`
      + (more.length ? `<span class="label">Morten's missions here</span><div class="do">${more.join('')}</div>` : '')
      + aimed
      + roomsStrip(m, h)
      + (evs.length ? `<span class="label">Last month here</span><ol class="events">${evs.map((e) => `<li class="${fac(e.who)}"><span class="n">${esc(e.n)}</span><span>${esc(e.text)}</span></li>`).join('')}</ol>` : '')
      + (heard.length ? `<span class="label">Heard here</span><ul class="heard">${heard.map((s) => `<li>${icon('speech')}<span>${esc(noIds(s))}</span></li>`).join('')}</ul>` : '')
      + (nb.length ? `<span class="label">Next to</span><div class="hexbtns">${nb.map((x) => hexBtn(m, x)).join('')}</div>` : '');
  }

  // ---------- the realm rows ----------
  function stateWords(f) {
    const out = [];
    if (f.ally) out.push('<span class="st good">ally</span>');
    if (f.hostile > 0) out.push(`<span class="st bad">${icon('skull')}hostile · ${esc(plural(f.hostile, 'month'))} left</span>`);
    if (f.disorder > 0) out.push(`<span class="st warn">in disorder · ${esc(plural(f.disorder, 'month'))}</span>`);
    if (typeof f.hp === 'number' && f.hp <= 0) out.push('<span class="st bad">fallen</span>');
    return out.join('');
  }

  /** v3: the standing word, ally or enemy, landless. */
  function stateWords3(f) {
    const out = [];
    const w = f.standingWord || (f.standing !== null ? ['enemy', 'wary', 'neutral', 'friendly', 'ally'][f.standing + 2] : '');
    if (w) out.push(`<span class="st ${STANDING_CLS[w] || ''}" title="standing ${f.standing !== null ? fmt.signed(f.standing) : '?'} with the tower">${w === 'enemy' ? icon('skull') : ''}${esc(w)}</span>`);
    if (!f.hexes.length) out.push('<span class="st bad">landless</span>');
    if (f.squeezed) out.push('<span class="st warn">squeezed</span>');
    return out.join('');
  }

  /** v3: ruler (label: verb), Force and tier, the goal as a clock; open: gold, land, sites, the dissident. */
  function realmRow3(m, f) {
    const isOpen = open.has(f.name);
    const r = m.realm;
    const lab = f.leader.label ? `${f.leader.label}${f.leader.verb ? `: ${f.leader.verb}` : ''}` : f.leader.verb;
    const tier = f.tier !== null ? f.tier : f.force !== null ? (f.force <= 2 ? 1 : f.force <= 4 ? 2 : 3) : 1;
    const nums = `<span title="${esc(r.words.force || 'Force')}">${icon('sword')}Force ${esc(f.force !== null ? fmt.n(f.force) : '?')}</span>`
      + `<span title="${esc(`tier ${tier}: its fights are ${DIFF[tier - 1]} for Morten`)}">${pips(tier)}<span class="vh">tier ${esc(tier)}</span></span>`
      + `<span title="treasury">${icon('coins')}${esc(fmt.gp(f.treasury) || '? GP')}</span>`;
    const goal = `<span class="goalline">${icon('flag')}<span>${f.goal ? esc(f.goal) : 'no goal'}</span>${f.clock ? clockHtml(f.clock) : ''}</span>`;
    const pcs = m.piecesOf.get(f.name) || [];
    const when = f.clock && f.clock.kind && r.goalWords[f.clock.kind] ? `<p class="muted small">When the clock fills: ${esc(r.goalWords[f.clock.kind])}. Each month a d6: a 1 loses a mark, 3 to 5 add one, a 6 adds two.</p>` : '';
    const body = isOpen ? `<div class="more">`
      + when
      + `<p class="gold"><b>${esc(fmt.gp(f.treasury) || '? GP')}</b> in the coffers, <b>${esc(f.income !== null ? `${fmt.signed(f.income)} GP` : '? GP')}</b> a month</p>`
      + `<p class="standing"><b>Standing ${esc(f.standing !== null ? fmt.signed(f.standing) : '?')}</b>, ${esc(f.standingWord || '')}: ${esc(r.words.standing || '')}</p>`
      + (f.dissident ? `<p class="dis">${icon('speech')}<span><b>${esc(f.dissident.name)}</b> is the dissident${f.dissident.hex ? `, in ${esc(cap(nameOf(m, f.dissident.hex)))}` : ''}: the tower can declare a topple.</span></p>` : '')
      + (f.hexes.length ? `<span class="label">Its land · ${esc(plural(f.hexes.length, 'hex', 'hexes'))}</span><div class="hexbtns">${[...f.hexes].sort((a, b) => (b === f.seat) - (a === f.seat)).map((id) => hexBtn(m, id)).join('')}</div>` : '<p class="muted small">It holds no land: its only goal is to take a hex back.</p>')
      + `<span class="label">Its sites · ${esc(pcs.length)}</span>`
      + (pcs.length ? `<div class="pieces">${pcs.map(({ a, h }) => siteRow(m, a, h, { owner: false, where: true })).join('')}</div>` : '<p class="muted small">None.</p>')
      + '</div>' : '';
    return `<div class="rrow v3 ${fac(f.name)}" data-realm="${esc(f.name)}" data-open="${isOpen}">`
      + `<button type="button" class="rhead" data-realm-toggle="${esc(f.name)}" aria-expanded="${isOpen}">`
      + '<span class="sw"></span>'
      + `<span class="top"><b>${esc(f.name)}</b><span class="sts">${stateWords3(f)}</span><span class="lv">${esc(leaderOf(f))}${lab ? ` · <i>${esc(lab)}</i>` : ''}</span></span>`
      + `<span class="nums">${nums}</span>`
      + `<span class="goalrow">${goal}</span>`
      + `${icon('chev', 'chev')}</button>${body}</div>`;
  }

  function realmRow(m, f) {
    if (V3(m.realm)) return realmRow3(m, f);
    const isOpen = open.has(f.name);
    const lab = f.leader.label ? `${f.leader.label}${f.leader.verb ? `: ${f.leader.verb}` : ''}` : f.leader.verb;
    const glyphs = ['force', 'cunning', 'wealth'].map((k, i) => `<span title="${ATTR['FCW'[i]][1]}">${icon(ATTR['FCW'[i]][0])}<span class="vh">${ATTR['FCW'[i]][1]} </span>${esc(fmt.n(f[k]))}</span>`).join('');
    const pcs = m.piecesOf.get(f.name) || [];
    const body = isOpen ? `<div class="more">`
      + `<p class="goal">${icon('flag')}<span>${f.goal ? `Going to ${esc(noIds(f.goal))}.` : 'No goal yet.'}</span></p>`
      + `<p class="gold"><b>${esc(fmt.gp(f.treasury) || '? GP')}</b> in the coffers, <b>${esc(f.income !== null ? `${fmt.signed(f.income)} GP` : '? GP')}</b> a month</p>`
      + (f.hexes.length ? `<span class="label">Its land · ${esc(plural(f.hexes.length, 'hex', 'hexes'))}</span><div class="hexbtns">${[...f.hexes].sort((a, b) => (b === f.seat) - (a === f.seat)).map((id) => hexBtn(m, id)).join('')}</div>` : '<p class="muted small">It holds no land.</p>')
      + `<span class="label">Pieces the tower can see · ${esc(pcs.length)}</span>`
      + (pcs.length ? `<div class="pieces">${pcs.map(({ a, h }) => pieceRow(m, a, h, { owner: false, where: true })).join('')}</div>` : '<p class="muted small">None seen.</p>')
      + '</div>' : '';
    return `<div class="rrow ${fac(f.name)}" data-realm="${esc(f.name)}" data-open="${isOpen}">`
      + `<button type="button" class="rhead" data-realm-toggle="${esc(f.name)}" aria-expanded="${isOpen}">`
      + '<span class="sw"></span>'
      + `<span class="top"><b>${esc(f.name)}</b><span class="sts">${stateWords(f)}</span><span class="lv">${esc(leaderOf(f))}${lab ? ` · <i>${esc(lab)}</i>` : ''}</span></span>`
      + `<span class="nums"><span class="reg">${icon('heart')}${bar(f.hp, f.max_hp)}<span>Regime ${esc(fmt.n(f.hp))}/${esc(fmt.n(f.max_hp))}</span></span>${glyphs}</span>`
      + `${icon('chev', 'chev')}</button>${body}</div>`;
  }

  function realmRows(m) {
    const list = m.realm.factions.filter((f) => !f.tower);
    if (!list.length) return '';
    const v3 = V3(m.realm);
    const rank = (f) => (f.ally ? 0 : (v3 ? f.standing !== null && f.standing <= -2 : f.hostile > 0) ? 1 : 2);
    const sorted = list.map((f, i) => ({ f, i })).sort((a, b) => rank(a.f) - rank(b.f) || a.i - b.i).map((x) => x.f);
    return `<h3>${icon('crown')}The realms<small>allies first, then the ${v3 ? 'enemies' : 'hostile'}</small></h3><div class="rrows">${sorted.map((f) => realmRow(m, f)).join('')}</div>`;
  }

  // ---------- state, painting, events ----------
  let box = null;
  let parts = null;
  let last = null;
  let picked = null;
  let evShown = null;
  let keyOn = false;
  let codes = !!local.get('realm.codes', false);
  let moves = local.get('realm.moves', true) !== false;
  const open = new Set();

  function skeleton() {
    box.innerHTML = '<div data-part="tower"></div><div data-part="note"></div><div class="mapbar" data-part="bar"></div>'
      + '<div class="frame" data-part="frame"><div data-part="svg"></div><div data-part="key"></div></div>'
      + '<div data-part="ev"></div><article class="card entry" data-part="entry" aria-live="polite"></article>'
      + '<div class="card realms" data-part="realms"></div>';
    box.__tableHtml = null;
    parts = {};
    for (const el of box.querySelectorAll('[data-part]')) parts[el.dataset.part] = el;
  }

  function paint() {
    if (!box || !last) return;
    const r = last.realm;
    if (!r || !r.hexes.length) {
      parts = null;
      const msg = !last.loaded || last.loaded.realm || last.db !== 'ok'
        ? (last.db === 'ok' ? 'No map yet: the GM draws it with the campaign\'s first world\'s turn.' : 'No map in this view.')
        : 'Opening the map…';
      put(box, `<div class="card"><h3>${icon('hex')}The realm</h3><p class="muted">${esc(msg)}</p></div>`);
      return;
    }
    if (!parts) skeleton();
    const m = model(r, last.state);
    if (!picked || !m.byId.has(picked)) picked = m.byId.has(m.origin) ? m.origin : r.hexes[0].id;
    put(parts.tower, towerCard(m));
    put(parts.note, V3(r)
      ? note('realm-map3', 'Colours are realms. The big number is a hex\'s <b>level</b>: the floor under it, how bad its wanderers are, and its income (level × 10 GP a month). The round tokens are <b>sites</b>: a crown the ruler\'s seat, a shield a garrison, a globe, gear or cart its works, a door its walls; the pips under one are its fight tier. Tap a hex.')
      : note('realm-map', 'Colours are realms. The big number is a hex\'s <b>level</b>: the floor under it, how bad its wanderers are, and its income (level × 10 GP a month). The round tokens are <b>pieces</b> a realm put there: a sword is soldiers, a mask spies, coins income; the ring round a token is its health. A crown is a ruler\'s seat. Tap a hex.'));
    put(parts.bar, mapBar());
    put(parts.svg, mapSvg(m));
    put(parts.key, keyOn ? keyOver() : '');
    put(parts.ev, evLine(m));
    parts.entry.dataset.hex = picked;
    put(parts.entry, entry(m, picked));
    put(parts.realms, realmRows(m));
  }

  function revealEntry() {
    const el = parts && parts.entry;
    if (!el) return;
    const top = el.getBoundingClientRect().top;
    if (top > window.innerHeight - 140 || top < 0) el.scrollIntoView({ block: 'start', behavior: 'smooth' });
  }

  function pick(id, reveal) {
    picked = id;
    paint();
    if (reveal) revealEntry();
  }

  function onClick(ev) {
    const t = ev.target;
    if (!t || !t.closest) return;
    const tg = t.closest('[data-t]');
    if (tg) {
      const k = tg.dataset.t;
      if (k === 'codes') { codes = !codes; local.set('realm.codes', codes); }
      if (k === 'moves') { moves = !moves; local.set('realm.moves', moves); if (!moves) evShown = null; }
      if (k === 'key') keyOn = !keyOn;
      paint();
      return;
    }
    const evb = t.closest('[data-ev]');
    if (evb) {
      const n = parseInt(evb.getAttribute('data-ev'), 10);
      evShown = evShown === n ? null : n;
      paint();
      return;
    }
    if (t.closest('[data-ev-close]')) { evShown = null; paint(); return; }
    const th = t.closest('[data-travel-here]');
    if (th) {
      const sp = T.panels.story;
      if (sp && typeof sp.pickHex === 'function' && sp.pickHex(th.getAttribute('data-travel-here'))) T.app.go('story');
      return;
    }
    const hx = t.closest('[data-hex]');
    if (hx) {
      pick(hx.getAttribute('data-hex'), true);
      return;
    }
    const rt = t.closest('[data-realm-toggle]');
    if (rt) {
      const n = rt.getAttribute('data-realm-toggle');
      if (open.has(n)) open.delete(n); else open.add(n);
      paint();
      return;
    }
    const go = t.closest('[data-goto-realm]');
    if (go) {
      const n = go.getAttribute('data-goto-realm');
      open.add(n);
      paint();
      const row = Array.from(box.querySelectorAll('.rrow')).find((x) => x.dataset.realm === n);
      if (row) row.scrollIntoView({ block: 'start', behavior: 'smooth' });
    }
  }

  function onKey(ev) {
    if (ev.key !== 'Enter' && ev.key !== ' ') return;
    const t = ev.target;
    if (!t || !t.matches || !t.matches('.hit[data-hex], .evhit[data-ev]')) return;
    ev.preventDefault();
    onClick(ev);
  }

  T.panels.realm = {
    mount(el) {
      box = el;
      box.addEventListener('click', onClick);
      box.addEventListener('keydown', onKey);
    },
    render(view) {
      last = view;
      paint();
    },
    /** Open the Realm on a hex (for the other panels: an orders hex, a world's-turn event). */
    show(id) {
      if (T.app && T.app.go) T.app.go('realm');
      if (typeof id === 'string' && id) pick(id, true);
    },
  };
})();
