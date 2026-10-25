#!/usr/bin/env node
// The dev store's CLI: play the GM's side against a running serve.mjs. Node 22 stdlib only.
//
//   node dnd-crunch/web/dev/db.mjs apply BATCH.json      apply an ArtifactData batch (versions enforced)
//   node dnd-crunch/web/dev/db.mjs dump [COLLECTION]     print the documents with their versions
//   node dnd-crunch/web/dev/db.mjs seed DIR              replace the store with a tree <collection>/<doc_id>.json
//   node dnd-crunch/web/dev/db.mjs reset                 re-seed from serve.mjs's --seed and forget the wakes
//   node dnd-crunch/web/dev/db.mjs wakes [--all]         list the wakes the page sent (comments.sendToClaude);
//                                                        --all: every call, the refused ones too
//   node dnd-crunch/web/dev/db.mjs moves --out DIR       write each move as DIR/moves/<id>.json
//
// Options: --url http://localhost:8787 (or TABLE_DEV_URL), --port N (shorthand for the URL).
//
// A batch is ArtifactData's: {"writes": [{"op": "set"|"update"|"delete", "collection",
// "doc_id", "data" | "file_path", "if_version"}]}. A file_path is read here and sent as
// data; a relative one resolves against the current directory, then the batch's folder.
// The store's rules: a create carries no if_version, a write to an existing document
// carries its current version, and the batch applies all or nothing. It prints the new
// versions, one line each: "set story/s0042 v1".
//
// moves --out writes {"collection": "moves", "doc_id": "m0007", "version": 1, "data": {…}}
// per move, and deletes DIR/moves/*.json files of moves no longer in the store.
import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
function opt(name) {
  const i = argv.indexOf(`--${name}`);
  if (i < 0) return null;
  const v = argv[i + 1];
  argv.splice(i, 2);
  return v;
}
const port = opt('port');
const BASE = (opt('url') || process.env.TABLE_DEV_URL || `http://127.0.0.1:${port || 8787}`).replace(/\/$/, '');
const out = opt('out');
const ALL = argv.includes('--all');
if (ALL) argv.splice(argv.indexOf('--all'), 1);
const [cmd, ...rest] = argv;

function die(msg, code = 1) {
  console.error(`db.mjs: ${msg}`);
  process.exit(code);
}

async function call(method, route, body) {
  let res;
  try {
    res = await fetch(BASE + route, { method, headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
  } catch (err) {
    die(`no dev server at ${BASE} (start it: node dnd-crunch/web/dev/serve.mjs --seed DIR)`, 2);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) die(`${data.error || res.status}: ${data.message || 'refused'}${route === '/api/batch' ? ' (nothing was written)' : ''}`);
  return data;
}

function readBatch(file) {
  let batch;
  try {
    batch = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (err) {
    die(`cannot read ${file}: ${err.message}`);
  }
  const writes = batch && Array.isArray(batch.writes) ? batch.writes : null;
  if (!writes) die(`${file} is not a batch: {"writes": [...]}`);
  const dir = path.dirname(path.resolve(file));
  for (const w of writes) {
    if (w && typeof w.file_path === 'string' && w.data === undefined && w.op !== 'delete') {
      const tries = path.isAbsolute(w.file_path) ? [w.file_path] : [path.resolve(w.file_path), path.join(dir, w.file_path)];
      const found = tries.find((p) => fs.existsSync(p));
      if (!found) die(`file_path not found: ${w.file_path}`);
      try {
        w.data = JSON.parse(fs.readFileSync(found, 'utf8'));
      } catch (err) {
        die(`${found} is not JSON: ${err.message}`);
      }
      delete w.file_path;
    }
  }
  return { writes };
}

async function main() {
  switch (cmd) {
    case 'apply': {
      if (!rest[0]) die('apply takes a batch file');
      const r = await call('POST', '/api/batch', readBatch(rest[0]));
      for (const x of r.results) console.log(`${x.op} ${x.collection}/${x.doc_id}${x.version ? ` v${x.version}` : ''}`);
      return;
    }
    case 'dump': {
      const docs = await call('GET', `/api/docs${rest[0] ? `?collection=${encodeURIComponent(rest[0])}` : ''}`);
      console.log(JSON.stringify(docs, null, 2));
      return;
    }
    case 'seed': {
      if (!rest[0]) die('seed takes a folder');
      const r = await call('POST', '/api/seed', { dir: path.resolve(rest[0]) });
      console.log(`seeded ${r.count} documents from ${rest[0]}`);
      return;
    }
    case 'reset': {
      const r = await call('POST', '/api/reset');
      console.log(`reset: ${r.count} documents`);
      return;
    }
    case 'wakes': {
      const w = await call('GET', `/api/wakes${ALL ? '?all=1' : ''}`);
      if (!w.length) console.log('no wakes yet');
      for (const x of w) console.log(`${x.n}. ${x.at} ${x.threadId || '-'} ${x.text}${x.resolved ? ' (resolved)' : ''}${x.refused ? ` (refused: ${x.refused})` : ''}`);
      return;
    }
    case 'moves': {
      if (!out) die('moves takes --out DIR');
      const docs = await call('GET', '/api/docs?collection=moves');
      const dir = path.join(out, 'moves');
      fs.mkdirSync(dir, { recursive: true });
      const keep = new Set();
      for (const d of docs) {
        const f = path.join(dir, `${d.doc_id}.json`);
        fs.writeFileSync(f, `${JSON.stringify({ collection: 'moves', doc_id: d.doc_id, version: d.version, data: d.data }, null, 2)}\n`);
        keep.add(`${d.doc_id}.json`);
        console.log(f);
      }
      for (const f of fs.readdirSync(dir)) if (f.endsWith('.json') && !keep.has(f)) fs.unlinkSync(path.join(dir, f));
      if (!docs.length) console.log(`no moves (${dir} is empty)`);
      return;
    }
    default:
      die('commands: apply BATCH.json · dump [COLLECTION] · seed DIR · reset · wakes · moves --out DIR', cmd ? 1 : 0);
  }
}

main();
