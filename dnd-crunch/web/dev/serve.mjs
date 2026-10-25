#!/usr/bin/env node
// The local table: dist/table.html over an in-memory fake of the artifact's db, with live
// snapshots over server-sent events. Node 22 standard library only.
//
//   node dnd-crunch/web/dev/serve.mjs [--seed DIR] [--port 8787] [--host 127.0.0.1] [--quiet]
//
// DIR is a store tree: <collection>/<doc_id>.json, each file one document's body
// (game/state.json, story/s0001.json, …). Every seeded document starts at version 1.
// The page is re-read from dist/ on every load, so a rebuild needs no restart.
//
// Routes (JSON in and out):
//   GET  /                     the wrapper page (?nodb=1, ?nocomments=1, ?cansend=no_session)
//   GET  /fake-claude.js       window.claude for the page
//   GET  /events               server-sent events: "snapshot" with every doc on each change
//   GET  /api/docs[?collection=c]  [{collection, doc_id, version, data}]
//   POST /api/write            the page's writes: {op: set|update|delete, collection, doc_id, data}
//   POST /api/batch            an ArtifactData batch {writes: [...]}: versions enforced, all or nothing
//   POST /api/seed             {dir} or {docs: [{collection, doc_id, data}]}: replace the store
//   POST /api/reset            re-seed from --seed DIR and forget the wakes
//   POST /api/wake             the page's comments.sendToClaude: {target, text}
//   GET  /api/wakes            the wakes recorded so far
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.join(HERE, '..', 'dist', 'table.html');
const FAKE = path.join(HERE, 'fake-claude.js');

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 && i + 1 < process.argv.length ? process.argv[i + 1] : fallback;
}
const PORT = parseInt(arg('port', '8787'), 10);
const HOST = arg('host', '127.0.0.1');
const SEED = arg('seed', null);
const QUIET = process.argv.includes('--quiet');
const log = (...a) => { if (!QUIET) console.log(...a); };

// ---------- the store ----------
/** path "collection/doc_id" -> {data, version} */
let store = new Map();
let wakes = [];
const threads = new Set();
const key = (c, d) => `${c}/${d}`;
const SEG = /^[A-Za-z0-9_\-.~:@+]{1,200}$/;
const validSeg = (s) => typeof s === 'string' && SEG.test(s) && s !== '.' && s !== '..';
const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

function readTree(dir) {
  const docs = [];
  const root = path.resolve(dir);
  if (!fs.existsSync(root)) throw new Error(`no such seed folder: ${dir}`);
  for (const col of fs.readdirSync(root, { withFileTypes: true })) {
    if (!col.isDirectory() || !validSeg(col.name)) continue;
    for (const f of fs.readdirSync(path.join(root, col.name))) {
      if (!f.endsWith('.json')) continue;
      const id = f.slice(0, -5);
      if (!validSeg(id)) continue;
      const data = JSON.parse(fs.readFileSync(path.join(root, col.name, f), 'utf8'));
      if (!isObj(data)) throw new Error(`${col.name}/${f} is not a JSON object`);
      docs.push({ collection: col.name, doc_id: id, data });
    }
  }
  return docs;
}

function seed(docs) {
  store = new Map();
  for (const d of docs) store.set(key(d.collection, d.doc_id), { data: d.data, version: 1 });
  broadcast();
}

function list(collection) {
  const out = [];
  for (const [k, v] of store) {
    const [c, d] = k.split('/');
    if (!collection || c === collection) out.push({ collection: c, doc_id: d, version: v.version, data: v.data });
  }
  out.sort((a, b) => (a.collection + a.doc_id < b.collection + b.doc_id ? -1 : 1));
  return out;
}

function merge(base, patch) {
  const out = isObj(base) ? { ...base } : {};
  for (const [k, v] of Object.entries(patch)) out[k] = isObj(v) && isObj(out[k]) ? merge(out[k], v) : v;
  return out;
}

class StoreError extends Error {
  constructor(code, message, status = 400) { super(message); this.code = code; this.status = status; }
}

/** A page write: last writer wins, versions bump, no version checks (the page has none). */
function pageWrite(w) {
  if (!isObj(w) || !validSeg(w.collection) || !validSeg(w.doc_id)) throw new StoreError('invalid_argument', 'bad path');
  const k = key(w.collection, w.doc_id);
  const cur = store.get(k);
  if (w.op === 'delete') { store.delete(k); return null; }
  if (!isObj(w.data)) throw new StoreError('invalid_argument', 'the body must be a JSON object');
  if (JSON.stringify(w.data).length > 256 * 1024) throw new StoreError('invalid_argument', 'document over 256 KiB');
  if (w.op === 'set') { store.set(k, { data: w.data, version: cur ? cur.version + 1 : 1 }); return store.get(k).version; }
  if (w.op === 'update') {
    if (!cur) throw new StoreError('invalid_argument', `update of a missing document ${k}`);
    store.set(k, { data: merge(cur.data, w.data), version: cur.version + 1 });
    return store.get(k).version;
  }
  throw new StoreError('invalid_argument', `unknown op ${w.op}`);
}

/**
 * An ArtifactData batch, with the real store's version rules: a create carries no
 * if_version; a write to an existing document must carry its current version; all or
 * nothing. Returns [{op, collection, doc_id, version}] (version null for a delete).
 */
function applyBatch(batch) {
  const writes = isObj(batch) && Array.isArray(batch.writes) ? batch.writes : null;
  if (!writes || !writes.length) throw new StoreError('invalid_argument', 'a batch is {"writes": [...]} with at least one write');
  const next = new Map(store);
  const results = [];
  writes.forEach((w, i) => {
    const where = `write ${i + 1}`;
    if (!isObj(w)) throw new StoreError('invalid_argument', `${where} is not an object`);
    const { op, collection, doc_id: id } = w;
    if (!['set', 'update', 'delete'].includes(op)) throw new StoreError('invalid_argument', `${where}: op must be set, update or delete`);
    if (!validSeg(collection) || !validSeg(id)) throw new StoreError('invalid_argument', `${where}: bad collection or doc_id`);
    const k = key(collection, id);
    const cur = next.get(k);
    const pinned = w.if_version !== undefined && w.if_version !== null;
    if (pinned && !Number.isInteger(w.if_version)) throw new StoreError('invalid_argument', `${where}: if_version must be an integer`);
    if (cur && !pinned) throw new StoreError('failed_precondition', `${where}: ${k} exists (version ${cur.version}); pass if_version`, 409);
    if (!cur && pinned) throw new StoreError('failed_precondition', `${where}: ${k} does not exist; a create carries no if_version`, 409);
    if (cur && pinned && cur.version !== w.if_version) throw new StoreError('failed_precondition', `${where}: ${k} is at version ${cur.version}, not ${w.if_version}`, 409);
    if (op === 'delete') {
      if (!cur) throw new StoreError('failed_precondition', `${where}: ${k} does not exist`, 409);
      next.delete(k);
      results.push({ op, collection, doc_id: id, version: null });
      return;
    }
    if (!isObj(w.data)) throw new StoreError('invalid_argument', `${where}: data must be a JSON object (db.mjs inlines file_path)`);
    if (op === 'update' && !cur) throw new StoreError('failed_precondition', `${where}: update of a missing document ${k}`, 409);
    const data = op === 'update' ? merge(cur.data, w.data) : w.data;
    const version = cur ? cur.version + 1 : 1;
    next.set(k, { data, version });
    results.push({ op, collection, doc_id: id, version });
  });
  store = next;
  broadcast();
  return results;
}

// ---------- live snapshots ----------
const clients = new Set();
function snapshotEvent() {
  return `event: snapshot\ndata: ${JSON.stringify({ docs: list(null) })}\n\n`;
}
function broadcast() {
  const ev = snapshotEvent();
  for (const res of clients) res.write(ev);
}
setInterval(() => { for (const res of clients) res.write(': keep-alive\n\n'); }, 15000).unref();

// ---------- the page ----------
const SKELETON_HEAD = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
<script src="/fake-claude.js"></script>
</head>
<body>
`;

function page() {
  const dist = fs.existsSync(DIST) ? fs.readFileSync(DIST, 'utf8') : '<p>No build yet: run python3 dnd-crunch/web/build.py</p>';
  return `${SKELETON_HEAD}${dist}\n</body>\n</html>\n`;
}

// ---------- http ----------
function send(res, status, body, type = 'application/json; charset=utf-8') {
  const text = typeof body === 'string' ? body : JSON.stringify(body, null, 1);
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(text);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let s = '';
    req.setEncoding('utf8');
    req.on('data', (c) => { s += c; if (s.length > 8 * 1024 * 1024) reject(new StoreError('invalid_argument', 'body too large')); });
    req.on('end', () => {
      if (!s) return resolve({});
      try { resolve(JSON.parse(s)); } catch { reject(new StoreError('invalid_argument', 'the body is not JSON')); }
    });
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  try {
    if (req.method === 'GET' && (url.pathname === '/' || url.pathname === '/index.html')) return send(res, 200, page(), 'text/html; charset=utf-8');
    if (req.method === 'GET' && url.pathname === '/fake-claude.js') return send(res, 200, fs.readFileSync(FAKE, 'utf8'), 'text/javascript; charset=utf-8');
    if (req.method === 'GET' && url.pathname === '/favicon.ico') { res.writeHead(204); return res.end(); }
    if (req.method === 'GET' && url.pathname === '/events') {
      res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-store', Connection: 'keep-alive' });
      res.write(snapshotEvent());
      clients.add(res);
      req.on('close', () => clients.delete(res));
      return undefined;
    }
    if (req.method === 'GET' && url.pathname === '/api/docs') return send(res, 200, list(url.searchParams.get('collection')));
    if (req.method === 'GET' && url.pathname === '/api/wakes') return send(res, 200, wakes);
    if (req.method === 'POST') {
      const body = await readBody(req);
      if (url.pathname === '/api/write') {
        const version = pageWrite(body);
        broadcast();
        log(`page ${body.op} ${body.collection}/${body.doc_id}${version ? ` -> v${version}` : ''}`);
        return send(res, 200, { ok: true, version });
      }
      if (url.pathname === '/api/batch') {
        const results = applyBatch(body);
        log(`batch: ${results.map((r) => `${r.op} ${r.collection}/${r.doc_id}${r.version ? ` v${r.version}` : ''}`).join(', ')}`);
        return send(res, 200, { ok: true, results });
      }
      if (url.pathname === '/api/seed') {
        const docs = Array.isArray(body.docs) ? body.docs : body.dir ? readTree(body.dir) : null;
        if (!docs) throw new StoreError('invalid_argument', 'seed takes {dir} or {docs}');
        seed(docs);
        log(`seeded ${docs.length} documents`);
        return send(res, 200, { ok: true, count: docs.length });
      }
      if (url.pathname === '/api/reset') {
        seed(SEED ? readTree(SEED) : []);
        wakes = [];
        threads.clear();
        return send(res, 200, { ok: true, count: store.size });
      }
      if (url.pathname === '/api/wake') {
        const t = isObj(body.target) ? body.target : {};
        const text = typeof t.text === 'string' ? t.text : '';
        if (!text.trim()) throw new StoreError('invalid', 'empty text');
        let threadId = t.threadId;
        if (threadId !== undefined) {
          if (!threads.has(threadId)) throw new StoreError('not_found', `no thread ${threadId}`, 404);
        } else {
          if (!isObj(t.anchor)) throw new StoreError('invalid', 'a new thread needs an anchor');
          threadId = `th_${threads.size + 1}`;
          threads.add(threadId);
        }
        const w = { n: wakes.length + 1, at: new Date().toISOString(), threadId, text, anchor: t.anchor || null, commentId: `c_${wakes.length + 1}` };
        wakes.push(w);
        log(`wake ${w.n}: ${text} (${threadId})`);
        return send(res, 200, { threadId, commentId: w.commentId });
      }
    }
    return send(res, 404, { error: 'not_found', message: `${req.method} ${url.pathname}` });
  } catch (err) {
    const status = err instanceof StoreError ? err.status : 500;
    const code = err instanceof StoreError ? err.code : 'internal';
    if (status >= 500) console.error(err);
    return send(res, status, { error: code, message: err.message });
  }
});

if (SEED) seed(readTree(SEED));
server.listen(PORT, HOST, () => {
  const { port } = server.address();
  console.log(`the table: http://localhost:${port}/  (${store.size} documents${SEED ? ` from ${SEED}` : ''})`);
});
