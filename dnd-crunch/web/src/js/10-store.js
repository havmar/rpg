// T.store: the bridge to the platform's db (and comments, for the wake).
//
// It subscribes ONCE to the four singleton docs (game/state, game/morten, game/realm,
// game/rules) and the four collections (story, live, log, moves), keeps their bodies as
// they arrive, and tells its subscribers after every change. It writes only moves, one at
// a time, and after a move lands it wakes the GM through comments.sendToClaude (README:
// The wake). Everything is defensive: window.claude may be missing, use() may resolve
// null or reject, a snapshot may error; the page renders whatever it has.
//
// The bridge, the seq handshake and the wake follow Dream's store.ts (proven on claude.ai)
// and the platform's db.d.ts / comments.d.ts (contract 0.2.90):
// - a listener ended by `unavailable` (the bridge stopped answering) or an unknown code is
//   dead, and a fresh onSnapshot is the only recovery: it is opened again, a few times;
// - every query carries a limit (1-1000), so no default page size cuts a collection;
// - a snapshot from the cache that has nothing yet is not "loaded" (no "empty table"
//   flash before the server answers); our own unconfirmed write (hasPendingWrites) is not
//   "landed" until the store confirms it;
// - the wake is a NEW thread per call, anchored on the answer box, resolved at once (the
//   GM tells a wake's second arrival by its thread); one call at a time, the moves that
//   land meanwhile get one more call naming the newest; never retried on its own; a
//   refusal that is permanent for the view stops the calls for the page load.
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;

  const DOCS = ['state', 'morten', 'realm', 'rules'];
  const COLS = ['story', 'live', 'log', 'moves'];
  const KINDS = ['say', 'play', 'orders', 'fight', 'turn', 'table', 'take'];
  const WRITTEN_GRACE_MS = 10000;
  /** A query's window: the store allows 1-1000; without one a default page might cut it. */
  const LIMIT = 1000;
  /** A move's body, serialised, at most (the store's cap is 256 KiB a document). */
  const MOVE_MAX_BYTES = 64 * 1024;
  /** Fresh subscriptions after a dead one, in a row with no snapshot between. */
  const RESUBSCRIBE_MAX = 4;

  const raw = {
    db: 'pending', // 'pending' until use("db") answers; then 'ok' | 'none' | 'error'
    dbError: '', // why the store stopped, in words
    docs: { state: null, morten: null, realm: null, rules: null }, // bodies, null when missing
    cols: { story: [], live: [], log: [], moves: [] }, // [{id, data, pending}]; pending: our unconfirmed write
    loaded: { state: false, morten: false, realm: false, rules: false, story: false, live: false, log: false, moves: false },
    pending: [], // [{id, seq, kind, body, at, status: 'sending'|'written'|'failed', error}]
    sentIds: [], // move ids this view wrote
    sending: 0, // writes queued or in flight
    // the wake: state idle|off|calling|called|unavailable|failed; reach is canSendToClaude's
    // last answer (null until asked); again: a "Call the GM again" can help
    wake: { state: 'idle', reason: '', move: null, kind: null, at: null, reach: null, again: false, code: '' },
    comments: 'pending', // 'pending' | 'ok' | 'none'
    user: { canWrite: null, canEdit: null },
    rev: 0,
  };

  const listeners = new Set();
  let DB = null;
  let CM = null;
  let commentsP = null;
  let started = null;
  let queue = Promise.resolve();
  let lastSeq = 0;
  const unsubs = [];
  // the wake's own state (README: The wake)
  let calling = false;
  let callAgain = null; // the newest move that landed while a call was in flight: {id, kind}
  let cannotWake = false; // a permanent refusal: no more calls this page load

  function emit() {
    raw.rev += 1;
    for (const fn of Array.from(listeners)) U.safe(() => fn(raw), 'store subscriber');
  }

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

  /** use("comments"), asked once; on arrival canSendToClaude is asked once too (posts nothing). */
  function useComments() {
    if (!commentsP) {
      commentsP = use('comments').then(async (cm) => {
        CM = cm;
        raw.comments = cm ? 'ok' : 'none';
        if (cm) await checkReach();
        else raw.wake.reach = 'none';
        emit();
        return cm;
      });
    }
    return commentsP;
  }

  /** Ask canSendToClaude again: cheap, never prompts. Any other answer or a rejection is "off". */
  async function checkReach() {
    let reach = 'off';
    try {
      const said = CM ? await CM.canSendToClaude() : 'none';
      reach = ['available', 'writers_only', 'no_session', 'off', 'none'].includes(said) ? said : 'off';
    } catch (_) {
      reach = 'off'; // capability_removed on an older platform: no sending
    }
    raw.wake.reach = reach;
    return reach;
  }

  function start() {
    if (started) return started;
    started = (async () => {
      useComments();
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

  // ---------- subscriptions (once each; again only when the platform ended one) ----------
  const SUB_REASON = {
    revoked: 'the table is no longer available in this view',
    invalid_argument: "the page asked the store for something it can't give",
    transform_error: "the page asked the store for something it can't give",
    resource_exhausted: 'the store is busy; reload the page in a minute',
    not_granted: 'this view was not given the table store',
    capability_disabled: 'the table store is not available in this view',
    capability_removed: 'the table store is not available in this view',
  };

  /** A listener's terminal error. `unavailable` and unknown codes: open a fresh one, a few times. */
  function onSubError(err, again, attempt) {
    const code = err && typeof err.code === 'string' ? err.code : 'unavailable';
    if (!SUB_REASON[code] && attempt < RESUBSCRIBE_MAX) {
      setTimeout(again, Math.min(30000, 1000 * 2 ** attempt) + Math.random() * 1500);
      return;
    }
    raw.db = 'error';
    raw.dbError = SUB_REASON[code] || 'the table store stopped answering';
    console.warn('[table] subscription ended:', U.errText(err));
    emit();
  }

  const meta = (s) => (s && U.isObj(s.metadata) ? s.metadata : {});

  function listenDoc(name, attempt) {
    let tries = attempt;
    const again = () => listenDoc(name, tries + 1);
    try {
      const ref = DB.doc(`game/${name}`);
      unsubs.push(ref.onSnapshot(
        (snap) => U.safe(() => {
          const exists = !!(snap && snap.exists);
          // nothing yet, from the cache: the server's answer follows; don't call it empty
          if (!exists && meta(snap).fromCache === true && !raw.loaded[name]) return;
          const body = exists && typeof snap.data === 'function' ? snap.data() : null;
          raw.docs[name] = U.isObj(body) ? body : null;
          raw.loaded[name] = true;
          tries = 0;
          emit();
        }, `game/${name} snapshot`),
        (err) => onSubError(err, again, tries),
      ));
    } catch (err) {
      onSubError(err, again, tries);
    }
  }

  function listenCol(name, attempt) {
    let tries = attempt;
    const again = () => listenCol(name, tries + 1);
    try {
      // the newest sections if there are ever more than the window holds; the rest by id
      let ref = DB.collection(name);
      ref = name === 'story' ? ref.orderBy('seq', 'desc').limit(LIMIT) : ref.limit(LIMIT);
      unsubs.push(ref.onSnapshot(
        (qs) => U.safe(() => {
          const list = qs && Array.isArray(qs.docs) ? qs.docs : [];
          if (!list.length && meta(qs).fromCache === true && !raw.loaded[name]) return;
          raw.cols[name] = list
            .map((d) => ({
              id: d && typeof d.id === 'string' ? d.id : '',
              data: d && typeof d.data === 'function' ? d.data() : null,
              pending: meta(d).hasPendingWrites === true,
            }))
            .filter((d) => d.id && U.isObj(d.data));
          raw.loaded[name] = true;
          tries = 0;
          prune();
          emit();
        }, `${name} snapshot`),
        (err) => onSubError(err, again, tries),
      ));
    } catch (err) {
      onSubError(err, again, tries);
    }
  }

  // A pending move is done once the store confirms it in moves, or a section answers it, or
  // (written, never seen) a while after its write was confirmed.
  function prune() {
    const inMoves = new Set(raw.cols.moves.filter((d) => !d.pending).map((d) => d.id));
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
      if (answered.has(p.id)) return false;
      if (p.status === 'written' && inMoves.has(p.id)) return false;
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

  /** The handshake: one past the highest move seq either side has seen. */
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
      // a verb's `unavailable` is transient: once more after a short randomized delay
      // (a set of the same whole body to the same id is safe to repeat)
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

  /** What a refused write says to the player, and what it does to the view. */
  function onWriteError(entry, err) {
    const code = err && typeof err.code === 'string' ? err.code : 'unavailable';
    if (code === 'invalid_argument' && raw.user.canWrite !== true) {
      // a well-formed write refused: this viewer reads the table but may not write to it
      raw.user.canWrite = false;
      entry.error = 'this view can read the table but not write to it';
    } else if (code === 'not_granted' || code === 'capability_disabled' || code === 'capability_removed') {
      raw.user.canWrite = false;
      entry.error = 'this view cannot write to the table';
    } else if (code === 'revoked') {
      raw.db = 'error';
      raw.dbError = SUB_REASON.revoked;
      entry.error = 'the table is no longer available in this view';
    } else if (code === 'quota_exceeded') {
      entry.error = 'the store is full; the GM has to clear old moves';
    } else if (code === 'resource_exhausted' || code === 'unavailable') {
      entry.error = 'that did not go through; wait a moment and send it again';
    } else {
      entry.error = U.errText(err);
    }
  }

  async function doSend(kind, fields) {
    if (!DB) throw storeError('no_store', raw.db === 'pending' ? 'the table is still opening; send again in a moment' : 'there is no table store in this view');
    if (raw.db === 'error') throw storeError('no_store', raw.dbError || 'the table store stopped answering');
    if (raw.user.canWrite === false) throw storeError('read_only', 'this view can read the table but not write to it');
    const seq = nextSeq();
    const id = `m${U.pad(seq)}`;
    const at = new Date().toISOString();
    const body = Object.assign(plainFields(fields), { v: 1, seq, at, kind });
    if (JSON.stringify(body).length > MOVE_MAX_BYTES) throw storeError('too_long', 'that move is too long to send; shorten it');
    const entry = { id, seq, kind, body, at, status: 'sending', error: '', writtenAt: 0 };
    raw.pending.push(entry);
    lastSeq = seq;
    emit();
    try {
      await writeMove(id, body);
    } catch (err) {
      entry.status = 'failed';
      onWriteError(entry, err);
      emit();
      throw err;
    }
    entry.status = 'written';
    entry.writtenAt = Date.now();
    raw.sentIds.push(id);
    prune();
    emit();
    return { id, seq };
  }

  /**
   * Write one move (moves/mNNNN), then wake the GM. Resolves {id, seq} once the move is
   * stored (the wake follows on its own, never holding the next write); rejects on a
   * failed write. Call it from the click handler itself: the wake needs a recent gesture.
   */
  function send(kind, fields) {
    if (!KINDS.includes(kind)) return Promise.reject(new TypeError(`unknown move kind: ${kind}`));
    raw.sending += 1;
    emit();
    // One write at a time: chain onto whatever is already in flight.
    const job = queue.then(() => doSend(kind, fields));
    queue = job.catch(() => {});
    return job
      .then((res) => {
        wake(res.id, kind).catch((err) => console.warn('[table] the wake failed:', U.errText(err)));
        return res;
      })
      .finally(() => {
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
  };
  /** Refusals that are permanent for this view: stop calling for the page load. */
  const CANNOT_WAKE = {
    forbidden: "commenting from the page is off for you (allow it in the page's comment panel); the GM will read your move next time",
    not_granted: 'this page may not comment here; the GM will read your move next time',
    capability_disabled: 'this view cannot comment from the page; the GM will read your move next time',
    capability_removed: 'this view cannot call the GM from the page; it will read your move next time',
    invalid: 'the page could not call the GM; it will read your move next time',
    transform_error: 'the page could not call the GM; it will read your move next time',
  };
  /** Refusals that may go through next time: the next move (or one tap) tries again. */
  const DID_NOT_WAKE = {
    consent_required: 'the GM was not called: allow this page to comment for you, then call again',
    claude_unavailable: 'the GM could not be reached from this view just now',
    rate_limited: 'the GM was called a lot just now; call again in a minute',
    unavailable: 'the comments did not answer',
    upstream_error: 'the call did not go through',
    not_found: 'the call did not go through',
  };

  function anchorEl() {
    return document.querySelector('[data-wake-anchor]') || document.getElementById('story') || document.body;
  }

  function setWake(fields) {
    Object.assign(raw.wake, fields);
    emit();
  }

  /**
   * Wake the GM for the move that just landed: one new comment thread, sent to Claude,
   * then resolved (the GM answers on the page, not in the thread). One call at a time;
   * moves that land meanwhile get one more call, naming the newest. Never on load, never
   * retried on its own.
   */
  async function wake(id, kind) {
    if (!isWakeOn()) {
      setWake({ state: 'off', reason: '', move: id, kind, at: null, again: false, code: '' });
      return;
    }
    if (calling) {
      callAgain = { id, kind };
      return;
    }
    calling = true;
    try {
      let next = { id, kind };
      while (next) {
        await callGm(next.id, next.kind);
        next = callAgain;
        callAgain = null;
        if (next && !isWakeOn()) {
          setWake({ state: 'off', reason: '', move: next.id, kind: next.kind, at: null, again: false, code: '' });
          next = null;
        }
      }
    } finally {
      calling = false;
      callAgain = null;
    }
  }

  async function callGm(id, kind) {
    const done = (state, reason, again, code) => setWake({ state, reason: reason || '', move: id, kind, at: Date.now(), again: !!again, code: code || '' });
    if (cannotWake) return done('unavailable', raw.wake.reason || CAN_REASON.none, false, raw.wake.code);
    setWake({ state: 'calling', reason: '', move: id, kind, at: null, again: false, code: '' });
    const cm = await useComments();
    if (!cm) return done('unavailable', CAN_REASON.none, false, 'none');
    // a reach learned as anything else may have changed (the GM took the watch): ask again
    const reach = raw.wake.reach === 'available' ? 'available' : await checkReach();
    if (reach !== 'available') return done('unavailable', CAN_REASON[reach] || CAN_REASON.off, true, reach);
    const text = `Table move ${id} (${kind}).`;
    try {
      const anchor = await cm.anchorFor(anchorEl());
      const res = await cm.sendToClaude({ anchor, text });
      const thread = res && typeof res.threadId === 'string' ? res.threadId : '';
      if (thread) Promise.resolve().then(() => cm.resolve(thread, true)).catch(() => {});
      return done('called', '', false, '');
    } catch (err) {
      const code = err && typeof err.code === 'string' ? err.code : 'upstream_error';
      console.warn('[table] the wake failed:', U.errText(err));
      if (Object.prototype.hasOwnProperty.call(CANNOT_WAKE, code)) {
        cannotWake = true;
        return done('unavailable', CANNOT_WAKE[code], false, code);
      }
      checkReach().then(emit, () => {});
      const why = Object.prototype.hasOwnProperty.call(DID_NOT_WAKE, code) ? DID_NOT_WAKE[code] : `the call did not go through (${code})`;
      return done('failed', `${why}; it will read your move next time`, true, code);
    }
  }

  /** The status line's one "Call the GM again" button: one call per tap, from that tap. */
  function wakeAgain() {
    const w = raw.wake;
    if (!w.move || calling || cannotWake || !isWakeOn()) return Promise.resolve();
    return wake(w.move, w.kind || 'say');
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
