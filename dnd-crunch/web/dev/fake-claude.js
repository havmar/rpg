// window.claude for the dev page (serve.mjs), shaped like the platform's contract
// (artifact-capabilities 0.2.90: claude.d.ts, db.d.ts, comments.d.ts, user.d.ts) closely
// enough for the table: use("db") | use("comments") | use("user"), resolving after the
// page's first synchronous run, as the real one does.
//
// Like the real store: delivered snapshots and bodies are frozen and reused while
// unchanged; the page's own write shows at once with metadata.hasPendingWrites true and
// is replaced by the confirmed document (or rolled back on a refusal); a query's limit is
// 1-1000; a terminal subscription error reaches the error callback once and the listener
// is dead. sendToClaude checks its target as the runtime does (exactly one of anchor or
// threadId, text non-empty, at most 4 KiB, no control characters but newlines and tabs).
//
// Query switches on the page's URL:
//   ?nodb=1             use("db") resolves null (the "no table store" path)
//   ?nocomments=1       use("comments") resolves null
//   ?noclaude=1         no window.claude at all (a saved copy of the page)
//   ?cansend=no_session canSendToClaude() answers that (writers_only | no_session | off)
//   ?wakefail=CODE      every sendToClaude rejects with CODE (forbidden, rate_limited, …)
//   ?wakedelay=MS       every sendToClaude takes that long
//   ?readonly=1         every write rejects invalid_argument; user.can("data.write") is false
//   ?readonly=quiet     the same, but can("data.write") resolves null (the platform says nothing)
//   ?delay=300          every call and first snapshot waits that many ms
//   ?cache=MS           each listener first gets an empty snapshot marked fromCache, the
//                       server's answer MS later (as on a slow first load)
//   ?dbfail=revoked     every subscription ends with that DbError after its first snapshot
//   ?dbfailonce=unavailable  only the first listener of each path ends so (a dead bridge
//                       the page recovers from with a fresh onSnapshot)
(() => {
  'use strict';
  const q = new URLSearchParams(window.location.search);
  const NODB = q.get('nodb') === '1';
  const NOCOMMENTS = q.get('nocomments') === '1';
  const CANSEND = q.get('cansend') || 'available';
  const WAKEFAIL = q.get('wakefail');
  const WAKEDELAY = Math.max(0, parseInt(q.get('wakedelay') || '0', 10) || 0);
  const READONLY = q.get('readonly');
  const DELAY = Math.max(0, parseInt(q.get('delay') || '0', 10) || 0);
  const CACHE = Math.max(0, parseInt(q.get('cache') || '0', 10) || 0);
  const DBFAIL = q.get('dbfail');
  const DBFAILONCE = q.get('dbfailonce');
  if (q.get('noclaude') === '1') return;
  const later = (v) => new Promise((r) => setTimeout(() => r(v), DELAY));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
  const fail = (code, message) => Promise.reject(Object.freeze({ code, message }));

  // ?dbfail=CODE / ?dbfailonce=CODE: end a listener with that error, once, after its first delivery
  const failedOnce = new Set();
  function failLater(key, stop, error) {
    let code = DBFAIL;
    if (!code && DBFAILONCE && !failedOnce.has(key)) {
      failedOnce.add(key);
      code = DBFAILONCE;
    }
    if (!code) return;
    setTimeout(() => {
      stop();
      if (typeof error === 'function') error(Object.freeze({ code, message: `dev: ${code}` }));
    }, 50);
  }

  function deepFreeze(o) {
    if (o && typeof o === 'object' && !Object.isFrozen(o)) {
      Object.freeze(o);
      for (const v of Object.values(o)) deepFreeze(v);
    }
    return o;
  }

  // ---------- the live mirror of the server's store, and this page's unconfirmed writes ----------
  let docs = new Map(); // "collection/doc" -> {id, collection, version, data}
  // "collection/doc" -> {id, collection, version: 'pN', data, deleted, confirmed: version|null}
  const overlay = new Map();
  let overlayN = 0;
  let readyResolve;
  const ready = new Promise((r) => { readyResolve = r; });
  const listeners = new Set();
  const META = Object.freeze({ fromCache: false, hasPendingWrites: false });
  const META_PENDING = Object.freeze({ fromCache: false, hasPendingWrites: true });
  const META_CACHE = Object.freeze({ fromCache: true, hasPendingWrites: false });

  function fireAll() {
    for (const l of Array.from(listeners)) {
      try { l(); } catch (err) { setTimeout(() => { throw err; }); }
    }
  }

  /** Drop the overlay entries the server's snapshot now carries. */
  function settleOverlay() {
    for (const [p, o] of overlay) {
      if (o.confirmed === null) continue;
      const d = docs.get(p);
      if (o.deleted ? !d : d && d.version >= o.confirmed) overlay.delete(p);
    }
  }

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
      settleOverlay();
      readyResolve();
      fireAll();
    });
  }

  /** The document as this page sees it: its own unconfirmed write first. */
  function current(p) {
    const o = overlay.get(p);
    if (o) return o.deleted ? null : o;
    return docs.get(p) || null;
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
    const d = current(path);
    if (!d) return Object.freeze({ id, exists: false, data: () => undefined, metadata: META });
    const c = snapCache.get(path);
    if (c && c.version === d.version && c.data === d.data) return c.snap;
    const pending = overlay.has(path);
    const snap = Object.freeze({ id, exists: true, data: () => d.data, metadata: pending ? META_PENDING : META });
    snapCache.set(path, { version: d.version, data: d.data, snap });
    return snap;
  }

  function merge(base, patch) {
    const out = isObj(base) ? { ...base } : {};
    for (const [k, v] of Object.entries(patch)) {
      if (isObj(v) && v.__delete__ === true) delete out[k];
      else out[k] = isObj(v) && isObj(out[k]) ? merge(out[k], v) : v;
    }
    return out;
  }

  async function write(w) {
    if (READONLY) return later().then(() => fail('invalid_argument', 'dev: this viewer may not write shared data'));
    const p = `${w.collection}/${w.doc_id}`;
    // latency compensation: the page sees its own write at once, marked hasPendingWrites
    const cur = current(p);
    const entry = {
      id: w.doc_id, collection: w.collection, version: `p${(overlayN += 1)}`, confirmed: null,
      deleted: w.op === 'delete',
      data: w.op === 'delete' ? null : deepFreeze(w.op === 'update' ? merge(cur && cur.data, w.data) : w.data),
    };
    const prev = overlay.get(p);
    overlay.set(p, entry);
    fireAll();
    await later(); // ?delay: the server's answer takes that long; the page sees its write meanwhile
    let res;
    let body = {};
    try {
      res = await fetch('/api/write', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(w) });
      body = await res.json().catch(() => ({}));
    } catch (_) {
      res = null;
    }
    if (!res || !res.ok) {
      if (overlay.get(p) === entry) {
        if (prev) overlay.set(p, prev);
        else overlay.delete(p);
      }
      fireAll();
      return res ? fail(body.error || 'unavailable', body.message || `HTTP ${res.status}`) : fail('unavailable', 'the dev server is not answering');
    }
    entry.confirmed = typeof body.version === 'number' ? body.version : 0;
    settleOverlay();
    fireAll();
    return undefined;
  }

  function clone(data) {
    if (!isObj(data)) return null;
    try { return JSON.parse(JSON.stringify(data)); } catch (_) { return null; }
  }

  /** Deliver `first` (a fromCache stand-in) at once when ?cache=MS, then start for real. */
  function startListener(isLive, emptySnap, begin) {
    ready.then(later).then(() => {
      if (!isLive()) return;
      if (CACHE) {
        emptySnap();
        setTimeout(() => { if (isLive()) begin(); }, CACHE);
      } else begin();
    });
  }

  function docRef(path) {
    const s = segments(path, 'doc');
    const [collection, id] = s;
    return Object.freeze({
      id,
      path,
      get: () => ready.then(later).then(() => docSnap(path, id)),
      set: (data) => (isObj(data) ? write({ op: 'set', collection, doc_id: id, data: clone(data) }) : fail('invalid_argument', 'a body is a plain object')),
      update: (data) => (isObj(data) ? (current(path) ? write({ op: 'update', collection, doc_id: id, data: clone(data) }) : fail('invalid_argument', `update of a missing document ${path}`)) : fail('invalid_argument', 'a body is a plain object')),
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
          failLater(`doc:${path}`, () => { live = false; listeners.delete(fire); }, error);
        };
        startListener(() => live,
          () => next(Object.freeze({ id, exists: false, data: () => undefined, metadata: META_CACHE })),
          () => { listeners.add(fire); fire(); });
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
      const paths = new Set([...docs.keys(), ...overlay.keys()]);
      for (const p of paths) {
        const d = current(p);
        if (d && d.collection === collection) list.push({ p, d });
      }
      list = list.filter(({ d }) => filters.every(([f, op, v]) => OPS[op](d.data[f], v)));
      list.sort((a, b) => (a.d.id < b.d.id ? -1 : a.d.id > b.d.id ? 1 : 0));
      if (order) {
        const [f, dir] = order;
        list.sort((a, b) => {
          const x = a.d.data[f];
          const y = b.d.data[f];
          if (x === undefined) return y === undefined ? 0 : 1; // missing sorts last
          if (y === undefined) return -1;
          return (x < y ? -1 : x > y ? 1 : 0) * (dir === 'desc' ? -1 : 1);
        });
      }
      if (lim) list = list.slice(0, lim);
      return list.map(({ p, d }) => docSnap(p, d.id));
    };
    const qsnap = (list, prev, metadata) => {
      const changes = [];
      const prevIds = prev ? prev.map((s) => s.id) : [];
      const ids = list.map((s) => s.id);
      if (prev) prev.forEach((s, i) => { if (!ids.includes(s.id)) changes.push({ type: 'removed', doc: s, oldIndex: i, newIndex: -1 }); });
      list.forEach((s, i) => {
        const j = prevIds.indexOf(s.id);
        if (j < 0) changes.push({ type: 'added', doc: s, oldIndex: -1, newIndex: i });
        else if (prev[j] !== s) changes.push({ type: 'modified', doc: s, oldIndex: j, newIndex: i });
      });
      const md = metadata || (list.some((s) => s.metadata.hasPendingWrites) ? META_PENDING : META);
      return Object.freeze({ docs: list, size: list.length, empty: list.length === 0, docChanges: () => changes, metadata: md });
    };
    const q = {
      where: (f, op, v) => {
        if (!OPS[op]) throw new TypeError(`unknown operator ${op}`);
        return query(collection, filters.concat([[f, op, v]]), order, lim);
      },
      orderBy: (f, dir = 'asc') => query(collection, filters, [f, dir], lim),
      limit: (n) => query(collection, filters, order, n),
      get: () => (lim !== null && !(Number.isInteger(lim) && lim >= 1 && lim <= 1000)
        ? fail('invalid_argument', 'limit is 1-1000')
        : ready.then(later).then(() => qsnap(run(), null))),
      onSnapshot(next, error) {
        let live = true;
        let prev = null;
        if (lim !== null && !(Number.isInteger(lim) && lim >= 1 && lim <= 1000)) {
          setTimeout(() => { if (live && typeof error === 'function') error(Object.freeze({ code: 'invalid_argument', message: 'limit is 1-1000' })); }, 0);
          return () => { live = false; };
        }
        const fire = () => {
          if (!live) return;
          const list = run();
          if (prev && prev.length === list.length && prev.every((s, i) => s === list[i])) return;
          const snap = qsnap(list, prev);
          prev = list;
          next(snap);
          failLater(`col:${collection}`, () => { live = false; listeners.delete(fire); }, error);
        };
        startListener(() => live,
          () => next(qsnap([], null, META_CACHE)),
          () => { listeners.add(fire); fire(); });
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

  /** Why the runtime would refuse this sendToClaude target (`invalid`), or null. */
  function badTarget(t) {
    if (!isObj(t)) return 'the target is an object';
    const keys = Object.keys(t).sort().join(' ');
    if (keys !== 'anchor text' && keys !== 'text threadId') return `exactly one of anchor or threadId, with text (got: ${keys})`;
    if (typeof t.text !== 'string' || !t.text.trim()) return 'text is required';
    if (new TextEncoder().encode(t.text).length > 4096) return 'text is over 4 KiB';
    if (/[\u0000-\u0008\u000b-\u001f\u007f]/.test(t.text)) return 'text carries control characters';
    if (t.anchor !== undefined) {
      const a = t.anchor;
      if (!isObj(a) || typeof a.path !== 'string' || !Number.isFinite(a.x) || !Number.isFinite(a.y)) return 'a malformed anchor';
    }
    if (t.threadId !== undefined && (typeof t.threadId !== 'string' || !t.threadId)) return 'a malformed threadId';
    return null;
  }

  async function post(route, body) {
    const res = await fetch(route, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).catch(() => null);
    if (!res) return { ok: false, body: { error: 'upstream_error', message: 'the dev server is not answering' } };
    return { ok: res.ok, body: await res.json().catch(() => ({})) };
  }

  const comments = Object.freeze({
    anchorFor(el) {
      if (!(el instanceof Element) || !el.isConnected) return fail('invalid', 'not an attached element');
      const r = el.getBoundingClientRect();
      return later({ path: cssPath(el), x: Math.round(r.left + r.width / 2 + window.scrollX), y: Math.round(r.top + r.height / 2 + window.scrollY) });
    },
    canSendToClaude: () => later(CANSEND),
    async sendToClaude(target) {
      await later();
      if (WAKEDELAY) await sleep(WAKEDELAY);
      // every call is told to the server (GET /api/wakes?all=1), the refused ones too
      let refuse = null;
      if (WAKEFAIL) refuse = { code: WAKEFAIL, message: `dev: ${WAKEFAIL}` };
      else if (CANSEND !== 'available') refuse = { code: 'claude_unavailable', message: `canSendToClaude is ${CANSEND}` };
      else {
        const bad = badTarget(target);
        if (bad) refuse = { code: 'invalid', message: bad };
      }
      const r = await post('/api/wake', { target: isObj(target) ? target : null, refused: refuse ? refuse.code : null });
      if (refuse) return fail(refuse.code, refuse.message);
      if (!r.ok) return fail(r.body.error || 'upstream_error', r.body.message || 'refused');
      return Object.freeze({ threadId: r.body.threadId, commentId: r.body.commentId });
    },
    create: () => later(Object.freeze({ threadId: `th_plain_${Date.now()}`, commentId: `c_${Date.now()}` })),
    reply: () => later(Object.freeze({ commentId: `c_${Date.now()}` })),
    openComposer: () => later(Object.freeze({ opened: false })),
    async resolve(threadId, resolved) {
      await later();
      if (typeof threadId !== 'string' || typeof resolved !== 'boolean') return fail('invalid', 'resolve(threadId, resolved)');
      const r = await post('/api/resolve', { threadId, resolved });
      if (!r.ok) return fail(r.body.error || 'upstream_error', r.body.message || 'refused');
      return undefined;
    },
    delete: () => later(undefined),
  });

  // ---------- user ----------
  const VIEWER = Object.freeze({ id: 'dev-viewer', name: 'Dev viewer', avatarUrl: '', color: '#8a5a10', email: null, isOwner: true, canEdit: true });
  const canWrite = READONLY === 'quiet' ? null : !READONLY;
  const user = Object.freeze({
    isOwner: () => later(!READONLY),
    canEdit: () => later(!READONLY),
    can: (what) => later(what === 'data.write' ? canWrite : null),
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
