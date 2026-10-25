// window.claude for the dev page (serve.mjs), shaped like the platform's contract
// (artifact-capabilities: claude.d.ts, db.d.ts, comments.d.ts, user.d.ts) closely enough
// for the table: use("db") | use("comments") | use("user"), resolving after the page's
// first synchronous run, as the real one does.
//
// Query switches on the page's URL:
//   ?nodb=1             use("db") resolves null (the "no table store" path)
//   ?nocomments=1       use("comments") resolves null
//   ?cansend=no_session canSendToClaude() answers that (writers_only | no_session | off)
//   ?delay=300          every call and first snapshot waits that many ms
//   ?dbfail=revoked     every subscription ends with that DbError after its first snapshot
//   ?noclaude=1         no window.claude at all (a saved copy of the page)
(() => {
  'use strict';
  const q = new URLSearchParams(window.location.search);
  const NODB = q.get('nodb') === '1';
  const NOCOMMENTS = q.get('nocomments') === '1';
  const CANSEND = q.get('cansend') || 'available';
  const DELAY = Math.max(0, parseInt(q.get('delay') || '0', 10) || 0);
  const DBFAIL = q.get('dbfail');
  if (q.get('noclaude') === '1') return;
  const later = (v) => new Promise((r) => setTimeout(() => r(v), DELAY));
  const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
  const fail = (code, message) => Promise.reject(Object.freeze({ code, message }));

  // ?dbfail=CODE: end a listener with that error, once, after its first delivery
  function failLater(stop, error) {
    if (!DBFAIL) return;
    setTimeout(() => {
      stop();
      if (typeof error === 'function') error(Object.freeze({ code: DBFAIL, message: `dev: ${DBFAIL}` }));
    }, 50);
  }

  function deepFreeze(o) {
    if (o && typeof o === 'object' && !Object.isFrozen(o)) {
      Object.freeze(o);
      for (const v of Object.values(o)) deepFreeze(v);
    }
    return o;
  }

  // ---------- the live mirror of the server's store ----------
  let docs = new Map(); // "collection/doc" -> {id, collection, version, data}
  let readyResolve;
  const ready = new Promise((r) => { readyResolve = r; });
  const listeners = new Set();
  const META = Object.freeze({ fromCache: false, hasPendingWrites: false });

  function connect() {
    const es = new EventSource('/events');
    es.addEventListener('snapshot', (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch (_) { return; }
      const next = new Map();
      for (const d of msg.docs || []) {
        const p = `${d.collection}/${d.doc_id}`;
        const old = docs.get(p);
        next.set(p, old && old.version === d.version ? old : { id: d.doc_id, collection: d.collection, version: d.version, data: deepFreeze(d.data) });
      }
      docs = next;
      readyResolve();
      for (const l of Array.from(listeners)) {
        try { l(); } catch (err) { setTimeout(() => { throw err; }); }
      }
    });
  }

  // ---------- refs ----------
  const SEG = /^[A-Za-z0-9_\-.~:@+]{1,200}$/;
  function segments(path, want) {
    if (typeof path !== 'string' || !path) throw new TypeError('a path is a non-empty string');
    const s = path.split('/');
    for (const x of s) if (!SEG.test(x) || x === '.' || x === '..') throw new TypeError(`bad path segment "${x}" in ${path}`);
    if (want === 'doc' && s.length % 2 !== 0) throw new TypeError(`a document path has an even number of segments (${path} has ${s.length})`);
    if (want === 'collection' && s.length % 2 !== 1) throw new TypeError(`a collection path has an odd number of segments (${path} has ${s.length})`);
    if (s.length > 2) throw new TypeError('the dev store holds top-level collections only');
    return s;
  }

  const snapCache = new Map();
  function docSnap(path, id) {
    const d = docs.get(path);
    if (!d) return Object.freeze({ id, exists: false, data: () => undefined, metadata: META });
    const c = snapCache.get(path);
    if (c && c.version === d.version) return c.snap;
    const snap = Object.freeze({ id, exists: true, data: () => d.data, metadata: META });
    snapCache.set(path, { version: d.version, snap });
    return snap;
  }

  async function write(w) {
    await later();
    let res;
    try {
      res = await fetch('/api/write', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(w) });
    } catch (_) {
      return fail('unavailable', 'the dev server is not answering');
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) return fail(body.error || 'unavailable', body.message || `HTTP ${res.status}`);
    return undefined;
  }

  function clone(data) {
    if (!isObj(data)) return null;
    try { return JSON.parse(JSON.stringify(data)); } catch (_) { return null; }
  }

  function docRef(path) {
    const s = segments(path, 'doc');
    const [collection, id] = s;
    return Object.freeze({
      id,
      path,
      get: () => ready.then(later).then(() => docSnap(path, id)),
      set: (data) => (isObj(data) ? write({ op: 'set', collection, doc_id: id, data: clone(data) }) : fail('invalid_argument', 'a body is a plain object')),
      update: (data) => (isObj(data) ? write({ op: 'update', collection, doc_id: id, data: clone(data) }) : fail('invalid_argument', 'a body is a plain object')),
      delete: () => write({ op: 'delete', collection, doc_id: id }),
      acquire: (o) => later({ acquired: true, version: (docs.get(path) || {}).version || 1, expiresAt: new Date(Date.now() + ((o && o.ttlMs) || 30000)).toISOString(), holder: o && o.holder }),
      onSnapshot(next, error) {
        let live = true;
        let last = null;
        const fire = () => {
          if (!live) return;
          const snap = docSnap(path, id);
          if (snap === last) return;
          last = snap;
          next(snap);
          failLater(() => { live = false; listeners.delete(fire); }, error);
        };
        ready.then(later).then(() => { if (live) { listeners.add(fire); fire(); } });
        return () => { live = false; listeners.delete(fire); };
      },
      collection: () => { throw new TypeError('the dev store holds top-level collections only'); },
    });
  }

  const OPS = {
    '==': (a, b) => a === b, '!=': (a, b) => a !== b, '<': (a, b) => a < b, '<=': (a, b) => a <= b,
    '>': (a, b) => a > b, '>=': (a, b) => a >= b, in: (a, b) => Array.isArray(b) && b.includes(a),
    'not-in': (a, b) => Array.isArray(b) && !b.includes(a), 'array-contains': (a, b) => Array.isArray(a) && a.includes(b),
  };

  function query(collection, filters, order, lim) {
    const run = () => {
      let list = [];
      for (const [p, d] of docs) if (d.collection === collection) list.push({ p, d });
      list = list.filter(({ d }) => filters.every(([f, op, v]) => OPS[op](d.data[f], v)));
      if (order) {
        const [f, dir] = order;
        list.sort((a, b) => {
          const x = a.d.data[f];
          const y = b.d.data[f];
          if (x === undefined) return 1;
          if (y === undefined) return -1;
          return (x < y ? -1 : x > y ? 1 : 0) * (dir === 'desc' ? -1 : 1);
        });
      } else list.sort((a, b) => (a.d.id < b.d.id ? -1 : a.d.id > b.d.id ? 1 : 0));
      if (lim) list = list.slice(0, lim);
      return list.map(({ p, d }) => docSnap(p, d.id));
    };
    const qsnap = (list, prev) => {
      const changes = [];
      const prevIds = prev ? prev.map((s) => s.id) : [];
      const ids = list.map((s) => s.id);
      if (prev) prev.forEach((s, i) => { if (!ids.includes(s.id)) changes.push({ type: 'removed', doc: s, oldIndex: i, newIndex: -1 }); });
      list.forEach((s, i) => {
        const j = prevIds.indexOf(s.id);
        if (j < 0) changes.push({ type: 'added', doc: s, oldIndex: -1, newIndex: i });
        else if (prev[j] !== s) changes.push({ type: 'modified', doc: s, oldIndex: j, newIndex: i });
      });
      return Object.freeze({ docs: list, size: list.length, empty: list.length === 0, docChanges: () => changes, metadata: META });
    };
    const q = {
      where: (f, op, v) => {
        if (!OPS[op]) throw new TypeError(`unknown operator ${op}`);
        return query(collection, filters.concat([[f, op, v]]), order, lim);
      },
      orderBy: (f, dir = 'asc') => query(collection, filters, [f, dir], lim),
      limit: (n) => query(collection, filters, order, n),
      get: () => ready.then(later).then(() => qsnap(run(), null)),
      onSnapshot(next, error) {
        let live = true;
        let prev = null;
        const fire = () => {
          if (!live) return;
          const list = run();
          if (prev && prev.length === list.length && prev.every((s, i) => s === list[i])) return;
          const snap = qsnap(list, prev);
          prev = list;
          next(snap);
          failLater(() => { live = false; listeners.delete(fire); }, error);
        };
        ready.then(later).then(() => { if (live) { listeners.add(fire); fire(); } });
        return () => { live = false; listeners.delete(fire); };
      },
    };
    return q;
  }

  function colRef(path) {
    const [collection] = segments(path, 'collection');
    const q = query(collection, [], null, null);
    const doc = (id) => docRef(`${collection}/${id || `auto${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`}`);
    return Object.freeze(Object.assign({}, q, {
      path,
      doc,
      add: (data) => { const r = doc(); return r.set(data).then(() => r); },
    }));
  }

  const db = Object.freeze({ doc: docRef, collection: colRef });

  // ---------- comments ----------
  function cssPath(el) {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 6; e = e.parentElement) {
      parts.unshift(e.id ? `#${e.id}` : e.tagName.toLowerCase());
      if (e.id) break;
    }
    return parts.join(' > ');
  }

  const comments = Object.freeze({
    anchorFor(el) {
      if (!(el instanceof Element) || !el.isConnected) return fail('invalid', 'not an attached element');
      return later({ path: cssPath(el), x: 0.5, y: 0.5 });
    },
    canSendToClaude: () => later(CANSEND),
    async sendToClaude(target) {
      await later();
      if (CANSEND !== 'available') return fail('claude_unavailable', `canSendToClaude is ${CANSEND}`);
      if (!isObj(target) || typeof target.text !== 'string' || !target.text.trim()) return fail('invalid', 'text is required');
      const res = await fetch('/api/wake', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target }) }).catch(() => null);
      if (!res) return fail('upstream_error', 'the dev server is not answering');
      const body = await res.json().catch(() => ({}));
      if (!res.ok) return fail(body.error || 'upstream_error', body.message || `HTTP ${res.status}`);
      return Object.freeze({ threadId: body.threadId, commentId: body.commentId });
    },
    create: () => later(Object.freeze({ threadId: `th_plain_${Date.now()}`, commentId: `c_${Date.now()}` })),
    reply: () => later(Object.freeze({ commentId: `c_${Date.now()}` })),
    openComposer: () => later(Object.freeze({ opened: false })),
    resolve: () => later(undefined),
    delete: () => later(undefined),
  });

  // ---------- user ----------
  const VIEWER = Object.freeze({ id: 'dev-viewer', name: 'Dev viewer', avatarUrl: '', color: '#8a5a10', email: null, isOwner: true, canEdit: true });
  const user = Object.freeze({
    isOwner: () => later(true),
    canEdit: () => later(true),
    can: () => later(true),
    me: () => later(VIEWER),
    id: () => later(VIEWER.id),
    profiles: () => later({}),
    name: () => later(VIEWER.name),
    avatarUrl: () => later(null),
    search: () => later([]),
    email: () => later(null),
  });

  // ---------- use() ----------
  const memo = {};
  function use(name) {
    if (memo[name]) return memo[name];
    let ns = null;
    if (name === 'db' && !NODB) ns = db;
    else if (name === 'comments' && !NOCOMMENTS) ns = comments;
    else if (name === 'user') ns = user;
    const p = new Promise((r) => setTimeout(() => r(ns), DELAY));
    if (ns) memo[name] = p;
    return p;
  }

  if (!NODB) connect();
  window.claude = Object.freeze({ use });
})();
