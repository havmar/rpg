// T.store: the bridge to the platform's db (and comments, for the wake).
//
// It subscribes ONCE to the four singleton docs (game/state, game/morten, game/realm,
// game/rules) and the four collections (story, live, log, moves), keeps their bodies as
// they arrive, and tells its subscribers after every change. It writes only moves, one at
// a time, and after a move lands it wakes the GM through comments.sendToClaude (README:
// The wake). Everything is defensive: window.claude may be missing, use() may resolve
// null or reject, a snapshot may error; the page renders whatever it has.
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;

  const DOCS = ['state', 'morten', 'realm', 'rules'];
  const COLS = ['story', 'live', 'log', 'moves'];
  const KINDS = ['say', 'play', 'orders', 'fight', 'turn', 'table', 'take'];
  const WRITTEN_GRACE_MS = 10000;

  const raw = {
    db: 'pending', // 'pending' until use("db") answers; then 'ok' | 'none' | 'error'
    dbError: '', // why the store stopped, in words
    docs: { state: null, morten: null, realm: null, rules: null }, // bodies, null when missing
    cols: { story: [], live: [], log: [], moves: [] }, // [{id, data}]
    loaded: { state: false, morten: false, realm: false, rules: false, story: false, live: false, log: false, moves: false },
    pending: [], // [{id, seq, kind, body, at, status: 'sending'|'written'|'failed', error}]
    sentIds: [], // move ids this view wrote
    sending: 0, // writes queued or in flight
    wake: { state: 'idle', reason: '', move: null, kind: null, at: null },
    comments: 'pending', // 'pending' | 'ok' | 'none'
    user: { canWrite: null, canEdit: null },
    rev: 0,
  };

  const listeners = new Set();
  let DB = null;
  let CM = null;
  let started = null;
  let queue = Promise.resolve();
  let lastSeq = 0;
  const unsubs = [];

  function emit() {
    raw.rev += 1;
    for (const fn of Array.from(listeners)) U.safe(() => fn(raw), 'store subscriber');
  }

  const local = () => (T.ui && T.ui.local) || { get: (k, d) => d, set() {}, del() {} };

  // ---------- capabilities ----------
  function use(name) {
    const c = window.claude;
    if (!c || typeof c.use !== 'function') return Promise.resolve(null);
    return Promise.resolve()
      .then(() => c.use(name))
      .then((ns) => ns || null)
      .catch((err) => {
        console.warn(`[table] claude.use("${name}") rejected:`, U.errText(err));
        return null;
      });
  }

  function start() {
    if (started) return started;
    started = (async () => {
      use('comments').then((cm) => {
        CM = cm;
        raw.comments = cm ? 'ok' : 'none';
        emit();
      });
      use('user').then(async (u) => {
        if (!u) return;
        try {
          const w = typeof u.can === 'function' ? await u.can('data.write') : null;
          raw.user.canWrite = typeof w === 'boolean' ? w : null;
        } catch (_) { /* unknown: keep the inputs */ }
        try {
          const e = typeof u.canEdit === 'function' ? await u.canEdit() : null;
          raw.user.canEdit = typeof e === 'boolean' ? e : null;
        } catch (_) { /* unknown */ }
        emit();
      });
      const db = await use('db');
      if (!db) {
        raw.db = 'none';
        emit();
        return;
      }
      DB = db;
      raw.db = 'ok';
      for (const name of DOCS) listenDoc(name, 0);
      for (const name of COLS) listenCol(name, 0);
      emit();
    })().catch((err) => {
      raw.db = 'error';
      raw.dbError = `the table's store did not open (${U.errText(err)})`;
      emit();
    });
    return started;
  }

  // ---------- subscriptions (once each) ----------
  const SUB_REASON = {
    revoked: 'this view lost access to the table',
    invalid_argument: "the page asked the store for something it can't give",
    resource_exhausted: 'the store is busy; reload the page in a minute',
    not_granted: 'this view was not given the table store',
    capability_disabled: 'the table store is not available in this view',
    capability_removed: 'the table store is not available in this view',
  };

  function onSubError(err, again, attempt) {
    const code = err && typeof err.code === 'string' ? err.code : 'unavailable';
    if (code === 'unavailable' && attempt < 2) {
      setTimeout(again, 2000 + Math.random() * 3000);
      return;
    }
    raw.db = 'error';
    raw.dbError = SUB_REASON[code] || 'the table store stopped answering';
    console.warn('[table] subscription ended:', U.errText(err));
    emit();
  }

  function listenDoc(name, attempt) {
    const again = () => listenDoc(name, attempt + 1);
    try {
      const ref = DB.doc(`game/${name}`);
      unsubs.push(ref.onSnapshot(
        (snap) => U.safe(() => {
          const body = snap && snap.exists && typeof snap.data === 'function' ? snap.data() : null;
          raw.docs[name] = U.isObj(body) ? body : null;
          raw.loaded[name] = true;
          emit();
        }, `game/${name} snapshot`),
        (err) => onSubError(err, again, attempt),
      ));
    } catch (err) {
      onSubError(err, again, attempt);
    }
  }

  function listenCol(name, attempt) {
    const again = () => listenCol(name, attempt + 1);
    try {
      const ref = DB.collection(name);
      unsubs.push(ref.onSnapshot(
        (qs) => U.safe(() => {
          const list = qs && Array.isArray(qs.docs) ? qs.docs : [];
          raw.cols[name] = list
            .map((d) => ({ id: d && typeof d.id === 'string' ? d.id : '', data: d && typeof d.data === 'function' ? d.data() : null }))
            .filter((d) => d.id && U.isObj(d.data));
          raw.loaded[name] = true;
          prune();
          emit();
        }, `${name} snapshot`),
        (err) => onSubError(err, again, attempt),
      ));
    } catch (err) {
      onSubError(err, again, attempt);
    }
  }

  // A pending move is done once it shows in moves, or a section answers it, or (written,
  // never seen) a while after its write was confirmed.
  function prune() {
    const inMoves = new Set(raw.cols.moves.map((d) => d.id));
    const answered = new Set();
    for (const s of raw.cols.story) {
      const a = s.data.answered;
      if (Array.isArray(a)) for (const id of a) if (typeof id === 'string') answered.add(id);
      const w = s.data.words;
      if (Array.isArray(w)) for (const x of w) if (U.isObj(x) && typeof x.move === 'string') answered.add(x.move);
    }
    const now = Date.now();
    raw.pending = raw.pending.filter((p) => {
      if (p.status === 'failed') return true;
      if (inMoves.has(p.id) || answered.has(p.id)) return false;
      if (p.status === 'written' && now - p.writtenAt > WRITTEN_GRACE_MS) return false;
      return true;
    });
  }

  // ---------- writing a move ----------
  function seqOf(d) {
    if (d && U.isObj(d.data) && typeof d.data.seq === 'number' && Number.isFinite(d.data.seq)) return d.data.seq;
    const m = d && typeof d.id === 'string' ? /^m(\d+)$/.exec(d.id) : null;
    return m ? parseInt(m[1], 10) : 0;
  }

  function nextSeq() {
    const st = raw.docs.state;
    let max = st && typeof st.lastMove === 'number' && Number.isFinite(st.lastMove) ? st.lastMove : 0;
    for (const d of raw.cols.moves) max = Math.max(max, seqOf(d));
    for (const p of raw.pending) max = Math.max(max, p.seq);
    return Math.max(max, lastSeq) + 1;
  }

  function storeError(code, message) {
    return { code, message };
  }

  async function writeMove(id, body) {
    const ref = DB.collection('moves').doc(id);
    try {
      await ref.set(body);
    } catch (err) {
      if (err && err.code === 'unavailable') {
        await U.sleep(300 + Math.random() * 700);
        await ref.set(body);
        return;
      }
      throw err;
    }
  }

  function plainFields(fields) {
    if (!U.isObj(fields)) return {};
    try {
      const copy = JSON.parse(JSON.stringify(fields));
      return U.isObj(copy) ? copy : {};
    } catch (_) {
      return {};
    }
  }

  async function doSend(kind, fields) {
    if (!DB) throw storeError('no_store', 'there is no table store in this view');
    if (raw.db === 'error') throw storeError('no_store', raw.dbError || 'the table store stopped answering');
    if (raw.user.canWrite === false) throw storeError('read_only', 'this view can read the table but not write to it');
    const seq = nextSeq();
    const id = `m${U.pad(seq)}`;
    const at = new Date().toISOString();
    const body = Object.assign(plainFields(fields), { v: 1, seq, at, kind });
    const entry = { id, seq, kind, body, at, status: 'sending', error: '', writtenAt: 0 };
    raw.pending.push(entry);
    lastSeq = seq;
    emit();
    // Ask early, alongside the write, so the wake still runs inside the viewer's gesture.
    const wakeOn = isWakeOn();
    const canP = wakeOn && CM ? Promise.resolve().then(() => CM.canSendToClaude()).catch(() => 'error') : null;
    try {
      await writeMove(id, body);
    } catch (err) {
      entry.status = 'failed';
      entry.error = err && err.code === 'quota_exceeded' ? 'the store is full; the GM has to clear old moves' : U.errText(err);
      if (err && err.code === 'invalid_argument' && raw.user.canWrite === null) raw.user.canWrite = false;
      emit();
      throw err;
    }
    entry.status = 'written';
    entry.writtenAt = Date.now();
    raw.sentIds.push(id);
    prune();
    emit();
    if (wakeOn) await callGm(id, kind, canP);
    else {
      raw.wake = { state: 'off', reason: '', move: id, kind, at: null };
      emit();
    }
    return { id, seq };
  }

  /** Write one move (moves/mNNNN), then wake the GM. Resolves {id, seq}; rejects on a failed write. */
  function send(kind, fields) {
    if (!KINDS.includes(kind)) return Promise.reject(new TypeError(`unknown move kind: ${kind}`));
    raw.sending += 1;
    emit();
    const job = queue.then(() => doSend(kind, fields));
    queue = job.catch(() => {});
    return job.finally(() => {
      raw.sending = Math.max(0, raw.sending - 1);
      emit();
    });
  }

  // ---------- the wake ----------
  function isWakeOn() {
    const st = raw.docs.state;
    return !!(st && U.isObj(st.wake) && st.wake.on === true);
  }

  const CAN_REASON = {
    no_session: 'the GM is not watching; it will read your move next time',
    writers_only: "only the table's editors can call the GM; it will read your move next time",
    off: 'calling the GM is off here; it will read your move next time',
    none: 'this view cannot call the GM; it will read your move next time',
    error: 'the GM could not be called; it will read your move next time',
  };
  const SEND_REASON = {
    consent_required: 'the GM was not called: allow this page to comment for you, then call again',
    forbidden: 'commenting from the page is off here; the GM will read your move next time',
    rate_limited: 'the GM was called a lot just now; call again in a minute',
    claude_unavailable: 'the GM could not be reached from this view; it will read your move next time',
    invalid: 'the call to the GM was refused; it will read your move next time',
  };

  function anchorEl() {
    return document.querySelector('[data-wake-anchor]') || document.getElementById('story') || document.body;
  }

  async function callGm(id, kind, canP) {
    raw.wake = { state: 'calling', reason: '', move: id, kind, at: null };
    emit();
    const done = (state, reason) => {
      raw.wake = { state, reason: reason || '', move: id, kind, at: Date.now() };
      emit();
    };
    if (!CM) return done('unavailable', CAN_REASON.none);
    let can;
    try {
      can = await (canP || CM.canSendToClaude());
    } catch (_) {
      can = 'error';
    }
    if (can !== 'available') return done('unavailable', CAN_REASON[can] || CAN_REASON.error);
    const text = `Table move ${id} (${kind}).`;
    let thread = local().get('wake.thread', null);
    try {
      let res = null;
      if (typeof thread === 'string' && thread) {
        try {
          res = await CM.sendToClaude({ threadId: thread, text });
        } catch (err) {
          if (!(err && err.code === 'not_found')) throw err;
          local().del('wake.thread');
          thread = null;
        }
      }
      if (!res) {
        const anchor = await CM.anchorFor(anchorEl());
        res = await CM.sendToClaude({ anchor, text });
      }
      if (res && typeof res.threadId === 'string' && res.threadId) local().set('wake.thread', res.threadId);
      return done('called', '');
    } catch (err) {
      const code = err && typeof err.code === 'string' ? err.code : '';
      console.warn('[table] the wake failed:', U.errText(err));
      return done('failed', SEND_REASON[code] || `the GM could not be called (${code || 'error'}); it will read your move next time`);
    }
  }

  /** The status line's one "Call the GM again" button. Never loops; one call per tap. */
  function wakeAgain() {
    const w = raw.wake;
    if (!w.move || w.state === 'calling') return Promise.resolve();
    return callGm(w.move, w.kind || 'say', null);
  }

  /** Send a failed move again, as a new move (it gets the next seq). */
  function retry(id) {
    const i = raw.pending.findIndex((p) => p.id === id && p.status === 'failed');
    if (i < 0) return Promise.resolve(null);
    const [p] = raw.pending.splice(i, 1);
    const fields = Object.assign({}, p.body);
    for (const k of ['v', 'seq', 'at', 'kind']) delete fields[k];
    return send(p.kind, fields);
  }

  /** Forget a failed move. */
  function dismiss(id) {
    const before = raw.pending.length;
    raw.pending = raw.pending.filter((p) => !(p.id === id && p.status === 'failed'));
    if (raw.pending.length !== before) emit();
  }

  T.store = {
    KINDS,
    start,
    /** fn(raw) after every change; returns an unsubscribe. */
    subscribe(fn) {
      if (typeof fn !== 'function') return () => {};
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    raw: () => raw,
    send,
    wakeAgain,
    retry,
    dismiss,
    /** Stop every subscription (tests, teardown). */
    stop() {
      while (unsubs.length) U.safe(() => unsubs.pop()(), 'unsubscribe');
    },
  };

  setInterval(() => {
    const before = raw.pending.length;
    prune();
    if (raw.pending.length !== before) emit();
  }, 5000);
})();
