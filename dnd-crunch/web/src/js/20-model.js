// T.model: the defensive parsers. T.model.view(raw) turns the store's raw bodies into the
// view model the panels render (README: The page's view model). Every field is read with
// a fallback of the right type; a wrong type falls back, nothing is cast. Parsed docs are
// cached by body identity (delivered bodies are frozen and reused when unchanged).
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;
  const isObj = U.isObj;

  // ---------- readers ----------
  const P = {
    str: (v, d = '') => (typeof v === 'string' ? v : d),
    strOrNull: (v) => (typeof v === 'string' && v !== '' ? v : null),
    /** A display value that may come as a string or a number ("1/2", 2, "+5"). */
    text: (v, d = '') => (typeof v === 'string' ? v : typeof v === 'number' && Number.isFinite(v) ? String(v) : d),
    num: (v, d = null) => (typeof v === 'number' && Number.isFinite(v) ? v : d),
    int: (v, d = null) => (Number.isInteger(v) ? v : d),
    bool: (v, d = false) => (typeof v === 'boolean' ? v : d),
    boolOrNull: (v) => (typeof v === 'boolean' ? v : null),
    arr: (v) => (Array.isArray(v) ? v : []),
    obj: (v) => (isObj(v) ? v : null),
    oneOf: (v, list, d) => (list.includes(v) ? v : d),
    strs: (v) => (Array.isArray(v) ? v.filter((x) => typeof x === 'string') : typeof v === 'string' && v ? [v] : []),
    nums: (v) => (Array.isArray(v) ? v.filter((x) => typeof x === 'number' && Number.isFinite(x)) : []),
    /** Map an array through fn, dropping what fn returns null for. */
    list: (v, fn) => (Array.isArray(v) ? v.map((x, i) => fn(x, i)).filter((x) => x !== null && x !== undefined) : []),
    /** An object of key -> fn(value), dropping nulls. */
    map: (v, fn) => {
      const out = {};
      if (!isObj(v)) return out;
      for (const k of Object.keys(v)) {
        const x = fn(v[k], k);
        if (x !== null && x !== undefined) out[k] = x;
      }
      return out;
    },
    seqFromId: (id) => {
      const m = typeof id === 'string' ? /(\d+)$/.exec(id) : null;
      return m ? parseInt(m[1], 10) : 0;
    },
  };
  const { str, strOrNull, text, num, int, bool, boolOrNull, obj, oneOf, strs, nums, list, map } = P;

  // ---------- enums (README: The data contract) ----------
  const E = {
    status: ['awaiting', 'playing', 'ended'],
    who: ['dm', 'you'],
    stop: ['month', 'orders', 'fight', 'round', 'matters'],
    fights: ['live', 'turning', 'summary', 'line'],
    world: ['story', 'report'],
    dice: ['key', 'all', 'none'],
    mode: ['open', 'closed'],
    awaiting: ['orders', 'fight', 'turn', 'word', 'none'],
    sectionKinds: ['orders', 'travel', 'fight', 'rest', 'shop', 'delve', 'domain', 'death', 'wrap', 'aside', 'opening'],
    lineWho: ['morten', 'foe', 'gm', 'world'],
    lineKind: ['roll', 'cast', 'attack', 'save', 'damage', 'note', 'move'],
    dieResult: ['hit', 'miss', 'cast', 'fizzle', 'save', 'fail'],
    outcome: ['cleared', 'died', 'fled', 'bypassed', 'going'],
    foeState: ['healthy', 'bloodied', 'near death'],
    moveKinds: ['say', 'play', 'orders', 'fight', 'turn', 'table', 'take'],
    playScope: ['month', 'matters', 'fight', 'round', 'stop'],
    fightChoice: ['fight', 'avoid', 'plan'],
  };

  // ---------- shared shapes ----------
  function die(d) {
    if (!isObj(d)) return null;
    const faces = nums(d.faces);
    const kept = Array.isArray(d.kept) ? nums(d.kept) : faces;
    return {
      expr: str(d.expr),
      faces,
      kept,
      mod: num(d.mod, 0),
      total: num(d.total, null),
      vs: str(d.vs),
      result: oneOf(d.result, E.dieResult, null),
      nat: d.nat === 20 || d.nat === 1 ? d.nat : null,
    };
  }

  function line(l) {
    if (typeof l === 'string') return { text: l, who: 'gm', kind: 'note', round: null, dice: [] };
    if (!isObj(l)) return null;
    return {
      text: str(l.text),
      who: oneOf(l.who, E.lineWho, 'gm'),
      kind: oneOf(l.kind, E.lineKind, 'note'),
      round: int(l.round, null),
      dice: list(l.dice, die),
    };
  }

  function foe(f) {
    if (!isObj(f)) return null;
    return {
      name: str(f.name, 'unknown foe'),
      cr: text(f.cr),
      ac: num(f.ac, null),
      hp: num(f.hp, null),
      maxHp: num(f.maxHp, null),
      speed: str(f.speed),
      attacks: strs(f.attacks),
      notes: str(f.notes),
      count: int(f.count, 1),
      state: oneOf(f.state, E.foeState, null),
    };
  }

  function table(t) {
    const o = isObj(t) ? t : {};
    return {
      who: oneOf(o.who, E.who, 'dm'),
      stop: oneOf(o.stop, E.stop, 'month'),
      fights: oneOf(o.fights, E.fights, 'live'),
      world: oneOf(o.world, E.world, 'story'),
      dice: oneOf(o.dice, E.dice, 'key'),
      mode: oneOf(o.mode, E.mode, 'open'),
      habits: strs(o.habits),
    };
  }

  // ---------- game/state ----------
  function hud(h) {
    const o = isObj(h) ? h : {};
    return {
      known: isObj(h),
      hp: num(o.hp, null),
      maxHp: num(o.maxHp, null),
      ac: num(o.ac, null),
      acArmor: num(o.acArmor, null),
      armorOn: boolOrNull(o.armorOn),
      light: str(o.light),
      conc: strOrNull(o.conc),
      conditions: strs(o.conditions),
      exhaustion: int(o.exhaustion, 0),
      reaction: boolOrNull(o.reaction),
      inspiration: boolOrNull(o.inspiration),
      freeArmor: boolOrNull(o.freeArmor),
      coins: str(o.coins),
      lost: strs(o.lost),
    };
  }

  function orders(o) {
    if (!isObj(o)) return null;
    return {
      hexes: list(o.hexes, (h) => (isObj(h) && typeof h.id === 'string' ? { id: h.id, name: str(h.name, h.id), days: num(h.days, null) } : null)),
      missions: list(o.missions, (m) => (isObj(m) ? { type: str(m.type), target: str(m.target), label: str(m.label, str(m.type)), hex: str(m.hex), days: num(m.days, null) } : null)),
      actions: list(o.actions, (a) => (isObj(a) ? { action: str(a.action), label: str(a.label, str(a.action)), cost: num(a.cost, null), affordable: boolOrNull(a.affordable) } : null)),
      realms: strs(o.realms),
    };
  }

  function awaiting(a) {
    const o = isObj(a) ? a : {};
    const f = obj(o.fight);
    const t = obj(o.turn);
    return {
      kind: oneOf(o.kind, E.awaiting, 'none'),
      prompt: str(o.prompt),
      orders: orders(o.orders),
      fight: f ? { title: str(f.title), foes: list(f.foes, foe), difficulty: str(f.difficulty), xp: num(f.xp, null) } : null,
      turn: t ? { board: Array.isArray(t.board) ? strs(t.board).join('\n') : str(t.board), lines: strs(t.lines), options: strs(t.options) } : null,
    };
  }

  function liveHead(l) {
    if (!isObj(l)) return null;
    return { kind: str(l.kind), title: str(l.title), month: int(l.month, null), day: int(l.day, null), openedAt: str(l.openedAt) };
  }

  function state(d) {
    if (!isObj(d)) return null;
    return {
      v: num(d.v, 1),
      campaign: str(d.campaign),
      status: oneOf(d.status, E.status, 'awaiting'),
      lastSeq: int(d.lastSeq, 0),
      lastMove: int(d.lastMove, 0),
      month: int(d.month, null),
      day: int(d.day, null),
      clock: str(d.clock),
      hex: str(d.hex),
      where: str(d.where),
      level: int(d.level, null),
      xp: num(d.xp, null),
      deaths: int(d.deaths, 0),
      hud: hud(d.hud),
      table: table(d.table),
      awaiting: awaiting(d.awaiting),
      live: liveHead(d.live),
      latest: strOrNull(d.latest),
      lastFight: strOrNull(d.lastFight),
      doing: str(d.doing),
      checkIn: typeof d.checkIn === 'string' || isObj(d.checkIn) ? d.checkIn : null,
      wake: { on: isObj(d.wake) && d.wake.on === true },
      url: str(d.url),
    };
  }

  // ---------- game/morten ----------
  function morten(d) {
    if (!isObj(d)) return null;
    const coins = isObj(d.coins) ? { on: str(d.coins.on), purse: str(d.coins.purse) } : { on: str(d.coins), purse: '' };
    const load = obj(d.load);
    return {
      v: num(d.v, 1),
      name: str(d.name, 'Morten'),
      class: str(d.class),
      species: str(d.species),
      background: str(d.background),
      hp: num(d.hp, null),
      maxHp: num(d.maxHp, null),
      hitDice: str(d.hitDice),
      ac: num(d.ac, null),
      acArmor: num(d.acArmor, null),
      armorOn: boolOrNull(d.armorOn),
      speed: text(d.speed),
      initiative: text(d.initiative),
      passivePerception: num(d.passivePerception, null),
      prof: num(d.prof, null),
      spellAttack: num(d.spellAttack, null),
      saveDc: num(d.saveDc, null),
      abilities: list(d.abilities, (a) => (isObj(a) && typeof a.key === 'string' ? { key: a.key, score: num(a.score, null), mod: num(a.mod, null), save: num(a.save, null), saveProf: bool(a.saveProf) } : null)),
      skills: list(d.skills, (s) => (isObj(s) && typeof s.name === 'string' ? { name: s.name, mod: num(s.mod, null) } : null)),
      attacks: list(d.attacks, (a) => (isObj(a) && typeof a.name === 'string' ? { name: a.name, hit: text(a.hit), damage: str(a.damage), range: str(a.range) } : null)),
      spells: list(d.spells, (s) => (isObj(s) && typeof s.name === 'string'
        ? { name: s.name, level: int(s.level, 0), dc: num(s.dc, null), lost: bool(s.lost), conc: bool(s.conc), ritual: bool(s.ritual), line: str(s.line), prepared: bool(s.prepared, true), time: str(s.time), range: str(s.range), note: str(s.note) }
        : null)),
      features: list(d.features, (f) => (isObj(f) && typeof f.name === 'string' ? { name: f.name, state: str(f.state), line: str(f.line) } : null)),
      light: str(d.light),
      conc: strOrNull(d.conc),
      conditions: strs(d.conditions),
      exhaustion: int(d.exhaustion, 0),
      inspiration: boolOrNull(d.inspiration),
      freeArmor: boolOrNull(d.freeArmor),
      reaction: boolOrNull(d.reaction),
      gear: list(d.gear, (g) => (isObj(g) && typeof g.name === 'string' ? { name: g.name, count: num(g.count, null), kg: num(g.kg, null), note: str(g.note) } : null)),
      load: load ? { kg: num(load.kg, null), max: num(load.max, null) } : null,
      coins,
      xp: num(d.xp, null),
      nextXp: num(d.nextXp, null),
      level: int(d.level, null),
      deaths: int(d.deaths, 0),
      familiar: str(d.familiar),
      habits: strs(d.habits),
      trader: list(d.trader, (t) => (isObj(t) && typeof t.name === 'string' ? { name: t.name, price: text(t.price) } : null)),
    };
  }

  // ---------- game/realm (map.json, snake_case, plus the page's camelCase keys) ----------
  function asset(a) {
    if (!isObj(a)) return null;
    return {
      id: str(a.id),
      owner: str(a.owner),
      name: str(a.name),
      type: str(a.type),
      tier: int(a.tier, 1),
      hp: num(a.hp, null),
      max_hp: num(a.max_hp, null),
      leader: strOrNull(a.leader),
      attack: str(a.attack),
      counter: str(a.counter),
      special: str(a.special),
    };
  }

  function hex(h) {
    if (!isObj(h) || typeof h.id !== 'string' || !h.id) return null;
    const m = /^([A-Z])(\d+)$/.exec(h.id);
    return {
      id: h.id,
      col: int(h.col, m ? m[1].charCodeAt(0) - 65 : 0),
      row: int(h.row, m ? parseInt(m[2], 10) - 1 : 0),
      level: int(h.level, null),
      biome: str(h.biome),
      people: str(h.people),
      holder: strOrNull(h.holder),
      lake: bool(h.lake),
      seat_of: strOrNull(h.seat_of),
      income: num(h.income, null),
      neighbours: strs(h.neighbours),
      assets: list(h.assets, asset),
    };
  }

  function faction(f) {
    if (!isObj(f) || typeof f.name !== 'string') return null;
    const l = isObj(f.leader) ? f.leader : {};
    return {
      name: f.name,
      tower: bool(f.tower),
      leader: { name: str(l.name), title: str(l.title), label: str(l.label), tag: str(l.tag), verb: str(l.verb) },
      income: num(f.income, null),
      goal: str(f.goal),
      hp: num(f.hp, null),
      max_hp: num(f.max_hp, null),
      force: num(f.force, null),
      cunning: num(f.cunning, null),
      wealth: num(f.wealth, null),
      treasury: num(f.treasury, null),
      seat: strOrNull(f.seat),
      hexes: strs(f.hexes),
      hostile: int(f.hostile, 0),
      ally: bool(f.ally),
      disorder: int(f.disorder, 0),
    };
  }

  function realm(d) {
    if (!isObj(d)) return null;
    const lay = isObj(d.layout) ? d.layout : {};
    const rep = isObj(d.report) ? d.report : {};
    const mo = obj(d.morten);
    return {
      v: num(d.v, 1),
      campaign: str(d.campaign),
      month: int(d.month, null),
      layout: { cols: int(lay.cols, 4), rows: int(lay.rows, 5), orientation: str(lay.orientation, 'flat-top'), shift: str(lay.shift, 'odd') },
      hexes: list(d.hexes, hex),
      rivers: P.arr(d.rivers).filter((p) => Array.isArray(p) && p.length === 2 && typeof p[0] === 'string' && typeof p[1] === 'string'),
      factions: list(d.factions, faction),
      morten: mo ? { hex: str(mo.hex), level: int(mo.level, null) } : null,
      events: list(d.events, (e) => (isObj(e)
        ? { month: int(e.month, null), actor: str(e.actor), action: str(e.action), from_hex: strOrNull(e.from_hex), to_hex: strOrNull(e.to_hex), target: str(e.target), result: str(e.result) }
        : null)),
      report: { plan: strs(rep.plan), happened: strs(rep.happened), tower: strs(rep.tower), next: strs(rep.next) },
      words: map(d.words, (v) => (typeof v === 'string' ? v : null)),
      kinds: map(d.kinds, (k) => (isObj(k)
        ? { glyph: str(k.glyph), type: str(k.type), tier: int(k.tier, 1), what: str(k.what), cost: num(k.cost, null), hp: num(k.hp, null), hits: str(k.hits), counter: str(k.counter), upkeep: num(k.upkeep, null), special: str(k.special), needs: str(k.needs), income: num(k.income, null), moves: num(k.moves, null), fight: str(k.fight) }
        : null)),
      rumours: map(d.rumours, (v) => strs(v)),
      floors: map(d.floors, (f) => (isObj(f)
        ? { floor: int(f.floor, null), rooms: list(f.rooms, (r) => (isObj(r) ? { n: text(r.n), monster: strOrNull(r.monster), cr: strOrNull(text(r.cr)), state: str(r.state, 'unknown'), xp: strOrNull(text(r.xp)), difficulty: str(r.difficulty), note: str(r.note) } : null)), cleared: bool(f.cleared) }
        : null)),
      days: map(d.days, (v) => num(v, null)),
      eventsWords: list(d.eventsWords, (e) => (isObj(e) ? { n: int(e.n, null), who: str(e.who), from: str(e.from), to: str(e.to), action: str(e.action), text: str(e.text) } : null)),
      hexNames: map(d.hexNames, (v) => (typeof v === 'string' ? v : null)),
      nextWords: strs(d.nextWords),
      dissidents: list(d.dissidents, (x) => (isObj(x) && x.name ? { realm: str(x.realm), name: str(x.name), hex: strOrNull(x.hex) } : null)),
    };
  }

  // ---------- game/rules ----------
  function rules(d) {
    if (!isObj(d)) return null;
    return {
      v: num(d.v, 1),
      sections: list(d.sections, (s, i) => (isObj(s) ? { id: str(s.id, `rule-${i + 1}`), title: str(s.title), md: str(s.md) } : null)),
    };
  }

  // ---------- story/sNNNN ----------
  function fight(f) {
    if (!isObj(f)) return null;
    return {
      foes: list(f.foes, foe),
      difficulty: str(f.difficulty),
      budget: num(f.budget, null),
      xp: num(f.xp, null),
      initiative: strs(f.initiative),
      rounds: int(f.rounds, null),
      outcome: oneOf(f.outcome, E.outcome, 'going'),
      verdict: str(f.verdict),
      hpTrack: list(f.hpTrack, (t) => (isObj(t) ? { name: str(t.name), max: num(t.max, null), hp: P.arr(t.hp).map((v) => num(v, null)) } : null)),
      loot: str(f.loot),
      lost: strs(f.lost),
      potion: bool(f.potion),
      xpBefore: num(f.xpBefore, null),
      xpAfter: num(f.xpAfter, null),
    };
  }

  function domain(d) {
    if (!isObj(d)) return null;
    const nx = isObj(d.next) ? d.next : {};
    return {
      plan: strs(d.plan),
      happened: list(d.happened, (h) => (isObj(h)
        ? { n: int(h.n, null), who: str(h.who), label: str(h.label), verb: str(h.verb), text: str(h.text), from: str(h.from), to: str(h.to) }
        : null)),
      elsewhere: str(d.elsewhere),
      tower: list(d.tower, (t) => (isObj(t) ? { what: str(t.what), before: text(t.before), after: text(t.after) } : null)),
      next: { threats: strs(nx.threats), chances: strs(nx.chances), open: strs(nx.open) },
      income: strs(d.income),
      log: strs(d.log),
    };
  }

  function section(id, d) {
    if (!isObj(d)) return null;
    const after = obj(d.after);
    return {
      id,
      seq: num(d.seq, P.seqFromId(id)),
      kind: typeof d.kind === 'string' && d.kind ? d.kind : 'aside',
      month: int(d.month, null),
      day: int(d.day, null),
      clock: str(d.clock),
      hex: str(d.hex),
      where: str(d.where),
      title: str(d.title),
      headline: str(d.headline),
      prose: strs(d.prose),
      bullets: list(d.bullets, (b) => (typeof b === 'string' ? { label: '', text: b } : isObj(b) ? { label: str(b.label), text: str(b.text) } : null)),
      trace: list(d.trace, line),
      answered: strs(d.answered),
      after: after ? { hp: num(after.hp, null), maxHp: num(after.maxHp, null), xp: num(after.xp, null), coins: str(after.coins), lost: strs(after.lost) } : null,
      fight: fight(d.fight),
      domain: domain(d.domain),
      words: list(d.words, (w) => (isObj(w) && typeof w.text === 'string' ? { move: str(w.move), text: w.text } : null)),
      ooc: bool(d.ooc),
    };
  }

  // ---------- live/bNNNN, log/lNNNN, moves/mNNNN ----------
  function beat(id, d) {
    if (!isObj(d)) return null;
    const s = obj(d.section);
    const st = isObj(d.state) ? d.state : {};
    const m = obj(st.morten);
    return {
      id,
      seq: num(d.seq, P.seqFromId(id)),
      section: s ? { kind: str(s.kind), title: str(s.title), month: int(s.month, null), day: int(s.day, null), where: str(s.where), foes: list(s.foes, foe) } : null,
      round: int(d.round, null),
      text: str(d.text),
      lines: list(d.lines, line),
      state: {
        morten: m ? { hp: num(m.hp, null), maxHp: num(m.maxHp, null) } : null,
        foes: list(st.foes, (f) => (isObj(f) ? { name: str(f.name), hp: num(f.hp, null), maxHp: num(f.maxHp, null), state: oneOf(f.state, E.foeState, null) } : null)),
      },
      at: str(d.at),
    };
  }

  function log(id, d) {
    if (!isObj(d)) return null;
    return { id, seq: num(d.seq, P.seqFromId(id)), text: str(d.text), at: str(d.at) };
  }

  function move(id, d) {
    if (!isObj(d)) return null;
    const mi = obj(d.mission);
    const gv = obj(d.give);
    return {
      id,
      seq: num(d.seq, P.seqFromId(id)),
      at: str(d.at),
      kind: oneOf(d.kind, E.moveKinds, 'say'),
      text: str(d.text),
      ooc: bool(d.ooc),
      scope: oneOf(d.scope, E.playScope, null),
      travel: strOrNull(d.travel),
      mission: mi ? { type: str(mi.type), target: str(mi.target) } : null,
      action: strOrNull(d.action),
      give: gv ? { realm: str(gv.realm), gp: num(gv.gp, 0) } : null,
      plan: str(d.plan),
      choice: oneOf(d.choice, E.fightChoice, null),
      table: isObj(d.table) ? table(d.table) : null,
      who: oneOf(d.who, E.who, null),
    };
  }

  // ---------- the view ----------
  const caches = {};
  function cached(kind, body, fn) {
    if (!isObj(body)) return fn(body);
    const cache = caches[kind] || (caches[kind] = new WeakMap());
    let hit = cache.get(body);
    if (hit === undefined) {
      hit = U.safe(() => fn(body), 'parse') || null;
      try { cache.set(body, hit); } catch (_) { /* not cacheable */ }
    }
    return hit;
  }
  const bySeq = (a, b) => a.seq - b.seq || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  // cached by id too: a body is parsed under the id it came with
  const parseCol = (kind, rows, fn) => (Array.isArray(rows) ? rows : [])
    .map((r) => (r && typeof r.id === 'string' ? cached(`${kind}/${r.id}`, r.data, (d) => fn(r.id, d)) : null))
    .filter(Boolean)
    .sort(bySeq);

  function view(raw) {
    const r = isObj(raw) ? raw : {};
    const docs = isObj(r.docs) ? r.docs : {};
    const cols = isObj(r.cols) ? r.cols : {};
    const loaded = isObj(r.loaded) ? r.loaded : {};
    const sent = new Set(P.arr(r.sentIds));

    const sections = parseCol('story', cols.story, section);
    const beats = parseCol('live', cols.live, beat);
    const logs = parseCol('log', cols.log, log);
    // our own write the store has not confirmed yet (hasPendingWrites) is still pending, not sent
    const confirmed = P.arr(cols.moves).filter((row) => !(isObj(row) && row.pending === true));
    const moves = parseCol('moves', confirmed, move).map((m) => (sent.has(m.id) ? Object.assign({}, m, { mine: true }) : Object.assign({}, m, { mine: false })));
    const inMoves = new Set(moves.map((m) => m.id));
    const pending = P.arr(r.pending)
      .filter((p) => isObj(p) && !inMoves.has(p.id))
      .map((p) => ({ id: p.id, seq: p.seq, kind: p.kind, at: p.at, status: p.status === 'failed' ? 'failed' : 'sending', error: str(p.error), move: move(p.id, p.body) }));

    const st = cached('state', docs.state, state);
    let lastBeatAt = null;
    for (const x of beats.concat(logs)) {
      const t = U.ms(x.at);
      if (t !== null && (lastBeatAt === null || t > lastBeatAt)) lastBeatAt = t;
    }
    const newestLog = logs.length ? logs[logs.length - 1].text : '';
    const w = isObj(r.wake) ? r.wake : {};
    const user = isObj(r.user) ? r.user : {};

    return {
      ready: loaded.state === true,
      db: r.db === 'none' || r.db === 'error' ? r.db : 'ok',
      dbError: str(r.dbError),
      opening: r.db === 'pending' || (r.db === 'ok' && loaded.state !== true),
      loaded: {
        state: !!loaded.state, morten: !!loaded.morten, realm: !!loaded.realm, rules: !!loaded.rules,
        story: !!loaded.story, live: !!loaded.live, log: !!loaded.log, moves: !!loaded.moves,
      },
      state: st,
      morten: cached('morten', docs.morten, morten),
      realm: cached('realm', docs.realm, realm),
      rules: cached('rules', docs.rules, rules),
      sections,
      beats,
      logs,
      moves,
      pending,
      sending: num(r.sending, 0) > 0,
      wake: {
        state: oneOf(w.state, ['idle', 'off', 'calling', 'called', 'unavailable', 'failed'], 'idle'),
        reason: str(w.reason),
        move: strOrNull(w.move),
        at: num(w.at, null),
        // canSendToClaude's last answer: available · writers_only · no_session · off · none; null until asked
        reach: oneOf(w.reach, ['available', 'writers_only', 'no_session', 'off', 'none'], null),
        again: w.again === true, // a "Call the GM again" can help (false after a permanent refusal)
        code: str(w.code), // the refusal's code, '' when none
      },
      comments: oneOf(r.comments, ['pending', 'ok', 'none'], 'pending'),
      canWrite: isObj(user) && user.canWrite === false ? false : r.db !== 'none' && r.db !== 'error',
      activity: (st && st.doing) || newestLog,
      lastBeatAt,
      now: Date.now(),
      rev: num(r.rev, 0),
    };
  }

  T.model = {
    view,
    P,
    E,
    parse: { state, morten, realm, rules, section, beat, log, move, line, die, foe, fight, domain, table, hud, awaiting },
  };
})();
