#!/usr/bin/env node
// The table's end-to-end test: serve.mjs over a fixture, Chromium (Playwright) at 412 px
// and 1280 px, and the checks in web/e2e/*.mjs, in file-name order.
//
//   node dnd-crunch/web/e2e.mjs [--only TEXT] [--shots DIR] [--fixture DIR] [--fonts]
//
// --only runs the checks whose name contains TEXT. --shots is where screenshots go
// (default: $TABLE_E2E_SHOTS or <tmp>/table-e2e). --fixture defaults to dev/fixture when
// it holds game/state.json, else dev/sample. Google Fonts are stubbed (empty CSS) so the
// run needs no network; --fonts lets them load.
//
// A check file exports `checks`: [{name, run: async (t) => {}, allowErrors?: true}].
// Before each check the store is re-seeded from the fixture and the wakes are cleared.
// After it, every page it opened must have logged no console error. `t` is the kit:
//   t.open({width, height, query, colorScheme})  -> a Playwright page on the table
//   t.shot(page, name)                           -> saves <shots>/<name>.png (full page)
//   t.expect(cond, message)                      -> throws when cond is falsy
//   t.waitFor(async () => value, what, ms)       -> polls until value is truthy, returns it
//   t.api.docs(collection?) / t.api.doc(c, id) / t.api.batch(writes) / t.api.write(w)
//   t.api.wakes() / t.api.calls() / t.api.reset() -> the dev store (serve.mjs routes);
//                                                   calls() lists refused wakes too
//   t.fixture, t.base, t.shots
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import net from 'node:net';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const WEB = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const opt = (name) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : null; };
const ONLY = opt('only');
const SHOTS = path.resolve(opt('shots') || process.env.TABLE_E2E_SHOTS || path.join(os.tmpdir(), 'table-e2e'));
const FONTS = argv.includes('--fonts');
const FIXTURE = path.resolve(opt('fixture') || (fs.existsSync(path.join(WEB, 'dev', 'fixture', 'game', 'state.json')) ? path.join(WEB, 'dev', 'fixture') : path.join(WEB, 'dev', 'sample')));

function freePort() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.unref();
    s.on('error', reject);
    s.listen(0, '127.0.0.1', () => { const { port } = s.address(); s.close(() => resolve(port)); });
  });
}

function startServer(port) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [path.join(WEB, 'dev', 'serve.mjs'), '--seed', FIXTURE, '--port', String(port), '--quiet'], { stdio: ['ignore', 'pipe', 'pipe'] });
    let err = '';
    child.stderr.on('data', (d) => { err += d; });
    child.stdout.on('data', (d) => { if (String(d).includes('the table:')) resolve(child); });
    child.on('exit', (code) => reject(new Error(`serve.mjs exited (${code}): ${err}`)));
    setTimeout(() => reject(new Error(`serve.mjs did not start: ${err}`)), 10000);
  });
}

class CheckFailed extends Error {}

async function main() {
  fs.mkdirSync(SHOTS, { recursive: true });
  const files = fs.readdirSync(path.join(WEB, 'e2e')).filter((f) => f.endsWith('.mjs')).sort();
  const checks = [];
  for (const f of files) {
    const mod = await import(pathToFileURL(path.join(WEB, 'e2e', f)).href);
    for (const c of mod.checks || []) checks.push({ ...c, file: f });
  }
  const chosen = checks.filter((c) => !ONLY || c.name.includes(ONLY));

  const port = await freePort();
  const server = await startServer(port);
  const base = `http://127.0.0.1:${port}`;
  const browser = await chromium.launch();

  const call = async (method, route, body) => {
    const res = await fetch(base + route, { method, headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new CheckFailed(`${route}: ${data.error}: ${data.message}`);
    return data;
  };
  const api = {
    docs: (c) => call('GET', `/api/docs${c ? `?collection=${c}` : ''}`),
    doc: async (c, id) => (await call('GET', `/api/docs?collection=${c}`)).find((d) => d.doc_id === id) || null,
    batch: (writes) => call('POST', '/api/batch', { writes }),
    write: (w) => call('POST', '/api/write', w),
    wakes: () => call('GET', '/api/wakes'),
    calls: () => call('GET', '/api/wakes?all=1'),
    reset: () => call('POST', '/api/reset'),
  };

  let failed = 0;
  console.log(`e2e: ${chosen.length} checks · fixture ${path.relative(process.cwd(), FIXTURE) || FIXTURE} · shots ${SHOTS}`);
  for (const check of chosen) {
    const contexts = [];
    const errors = [];
    const t = {
      api,
      base,
      fixture: FIXTURE,
      shots: SHOTS,
      async open({ width = 412, height = 915, query = '', colorScheme = 'light' } = {}) {
        const context = await browser.newContext({ viewport: { width, height }, colorScheme, deviceScaleFactor: 1 });
        contexts.push(context);
        if (!FONTS) await context.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.fulfill({ status: 200, contentType: 'text/css', body: '' }));
        const page = await context.newPage();
        page.on('console', (m) => { if (m.type() === 'error') errors.push(`console: ${m.text()}`); });
        page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));
        await page.goto(`${base}/${query ? `?${query.replace(/^\?/, '')}` : ''}`);
        await page.waitForFunction(() => window.T && window.T.app && window.T.app.view());
        return page;
      },
      async shot(page, name) {
        await page.screenshot({ path: path.join(SHOTS, `${name}.png`), fullPage: true });
      },
      expect(cond, message) {
        if (!cond) throw new CheckFailed(message);
      },
      async waitFor(fn, what, ms = 5000) {
        const until = Date.now() + ms;
        let last;
        while (Date.now() < until) {
          last = await fn();
          if (last) return last;
          await new Promise((r) => setTimeout(r, 100));
        }
        throw new CheckFailed(`timed out waiting for ${what}`);
      },
    };
    const t0 = Date.now();
    try {
      await api.reset();
      await check.run(t);
      if (!check.allowErrors && errors.length) throw new CheckFailed(`console errors:\n    ${errors.join('\n    ')}`);
      console.log(`  ok    ${check.name} (${Date.now() - t0} ms)`);
    } catch (err) {
      failed += 1;
      console.log(`  FAIL  ${check.name} [${check.file}]\n        ${err instanceof CheckFailed ? err.message : err.stack}`);
    } finally {
      for (const c of contexts) await c.close().catch(() => {});
    }
  }
  await browser.close();
  server.kill();
  console.log(failed ? `e2e: ${failed} of ${chosen.length} failed` : `e2e: all ${chosen.length} passed`);
  process.exit(failed ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(2);
});
