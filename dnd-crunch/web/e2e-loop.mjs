#!/usr/bin/env node
// The GM's loop end to end, with the real GM side: tools/table.py writes the store's
// documents and batches, dev/db.mjs applies them to a running serve.mjs (standing in for
// ArtifactData), and the page (Chromium at 412 px) plays the player:
//
//   table.py new (+ wake, + the orders form) → the page reads the opening and sends the
//   month's orders → db.mjs moves + table.py moves read them → table.py open + beat stream a
//   fight onto the live card → table.py section answers the orders → the page shows the
//   section with the player's words under it, and the answer box asks for orders again.
//
//   node dnd-crunch/web/e2e-loop.mjs [--keep] [--shots DIR]
//
// It plays in a scratch campaign (realms3's world files, a fresh sheet); --keep leaves it.
// Node 22, Python 3 and the pre-installed Playwright; no network. Under a minute.
import { createRequire } from 'node:module';
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import net from 'node:net';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const WEB = path.dirname(fileURLToPath(import.meta.url));
const GAME = path.dirname(WEB);
const TOOLS = path.join(GAME, 'tools');
const argv = process.argv.slice(2);
const KEEP = argv.includes('--keep');
const opt = (name) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : null; };
const SHOTS = path.resolve(opt('shots') || process.env.TABLE_E2E_SHOTS || path.join(os.tmpdir(), 'table-e2e'));

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'table-loop-'));
const DIR = path.join(tmp, 'loop');
const EMPTY = path.join(tmp, 'empty');
let port = 0;
let step = '';

class Failed extends Error {}
const expect = (cond, msg) => { if (!cond) throw new Failed(msg); };

function freePort() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.unref();
    s.on('error', reject);
    s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => resolve(p)); });
  });
}

function run(cmd, args, what) {
  const r = spawnSync(cmd, args, { encoding: 'utf8' });
  if (r.status !== 0) throw new Failed(`${what}: exit ${r.status}\n${r.stderr || r.stdout}`);
  return r;
}

/** One verb of the GM's side, its batches applied in order with db.mjs, then `sent`. */
function gm(verb, ...args) {
  step = `table.py ${verb}`;
  const out = path.join(DIR, 'page', 'out');
  if (fs.existsSync(out)) for (const f of fs.readdirSync(out)) if (/^batch.*\.json$/.test(f)) fs.unlinkSync(path.join(out, f));
  const r = run('python3', [path.join(TOOLS, 'table.py'), verb, DIR, ...args], step);
  const batches = fs.existsSync(out) ? fs.readdirSync(out).filter((f) => /^batch.*\.json$/.test(f)).sort((a, b) => a.localeCompare(b, 'en', { numeric: true })) : [];
  for (const b of batches) run(process.execPath, [path.join(WEB, 'dev', 'db.mjs'), 'apply', path.join(out, b), '--port', String(port)], `db.mjs apply ${b} (${verb})`);
  if (batches.length) run('python3', [path.join(TOOLS, 'table.py'), 'sent', DIR], `table.py sent (${verb})`);
  return r.stdout + r.stderr;
}

function md(name, text) {
  const p = path.join(tmp, name);
  fs.writeFileSync(p, text);
  return p;
}

async function waitFor(fn, what, ms = 8000) {
  const until = Date.now() + ms;
  while (Date.now() < until) {
    const v = await fn();
    if (v) return v;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Failed(`timed out waiting for ${what}`);
}

async function main() {
  const t0 = Date.now();
  fs.mkdirSync(SHOTS, { recursive: true });
  fs.mkdirSync(DIR, { recursive: true });
  fs.mkdirSync(EMPTY, { recursive: true });
  const src = path.join(GAME, 'campaigns', 'realms3');
  for (const f of ['map.json', 'realms.json', 'gm-secrets.md', 'rules.md', 'world.md']) fs.copyFileSync(path.join(src, f), path.join(DIR, f));
  const tower = JSON.parse(fs.readFileSync(path.join(DIR, 'map.json'), 'utf8')).morten.hex;

  port = await freePort();
  const server = spawn(process.execPath, [path.join(WEB, 'dev', 'serve.mjs'), '--seed', EMPTY, '--port', String(port), '--quiet'], { stdio: ['ignore', 'pipe', 'pipe'] });
  await new Promise((resolve, reject) => {
    server.stdout.on('data', (d) => { if (String(d).includes('the table:')) resolve(); });
    server.on('exit', (c) => reject(new Error(`serve.mjs exited (${c})`)));
    setTimeout(() => reject(new Error('serve.mjs did not start')), 10000);
  });
  const base = `http://127.0.0.1:${port}`;
  const browser = await chromium.launch();
  const errors = [];
  let ok = false;
  try {
    // ---- the first publish: seed, wake, the orders form ----
    gm('new', '--sheet', 'fresh', '--campaign', 'loop', '--hex', tower, '--where', `the tower (${tower})`, '--file', md('open.md',
      `---\nkind: opening\ntitle: Month 1 opens at the tower\nmonth: 1\nday: 1\nclock: "08:00"\nhex: ${tower}\n`
      + 'headline: Morten wakes in his tower on 20/20 HP with 47 GP 7 SP 5 CP.\n---\nFloor 1 lies under the tower.\n'));
    run('python3', [path.join(TOOLS, 'table.py'), 'sent', DIR, '--url', 'https://claude.ai/artifact/e2e-loop'], 'sent --url');
    gm('wake');
    gm('state', '--awaiting', 'orders', '--status', 'awaiting', '--prompt', "Month 1's orders");

    // ---- the player: reads the opening, sends the orders from the form ----
    step = 'the page';
    const ctx = await browser.newContext({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 1 });
    await ctx.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.fulfill({ status: 200, contentType: 'text/css', body: '' }));
    const page = await ctx.newPage();
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(`${base}/`);
    await page.waitForFunction(() => window.T && T.app && T.app.view() && T.app.view().ready);
    await waitFor(() => page.locator('#story [data-sec="s0001"]').count(), 'the opening section');
    await waitFor(() => page.locator('#story .answer [data-row="travel"]').count(), 'the orders form');
    const delve = page.locator('#story .answer [data-f="mission"]').filter({ hasText: /Delve/ }).first();
    expect(await delve.count(), 'the form offers a Delve at the tower');
    await delve.click();
    const plan = 'Floor 1 first: safe XP under the tower.';
    await page.fill('#answer-text', plan);
    await page.locator('#story .answer [data-act="send"]').click();
    await waitFor(() => page.locator('#story .answer [data-row="sent"]').count(), 'the box: the orders are with the GM');
    const wakes = await waitFor(async () => { const w = await (await fetch(`${base}/api/wakes`)).json(); return w.length ? w : null; }, 'the wake');
    expect(/Table move m0001 \(orders\)\./.test(wakes[0].text), `the wake's text: ${wakes[0].text}`);

    // ---- the GM's turn: read the move ----
    const inDir = path.join(DIR, 'page', 'in');
    fs.rmSync(inDir, { recursive: true, force: true });
    run(process.execPath, [path.join(WEB, 'dev', 'db.mjs'), 'moves', '--out', inDir, '--port', String(port)], 'db.mjs moves');
    const read = run('python3', [path.join(TOOLS, 'table.py'), 'moves', DIR, '--file', inDir], 'table.py moves').stdout;
    expect(/m0001 .*orders: travel to/.test(read) && read.includes(plan), `table.py moves reads the orders in words:\n${read}`);
    gm('log', 'reading your orders');

    // ---- a fight streamed onto the live card, then settled ----
    const foes = JSON.stringify([{ name: 'Flying Snake', cr: '1/8', ac: 14, hp: 5, maxHp: 5, speed: '6 sq (9 m), fly 12 sq (18 m)', attacks: ['Bite +4, 1 piercing + 2d4 poison'], notes: 'Flyby', count: 2 }]);
    gm('open', '--kind', 'fight', '--title', 'Room 1.1 · 2 Flying Snakes (CR 1/8 each)', '--where', 'Floor 1 · room 1.1', '--foes', foes, '--doing', 'fighting the snakes');
    gm('beat', '--round', '1', '--text', 'Fire Bolt kills one snake; the other bites for 6 dmg. Morten is on 14/20 HP.',
      '--line', 'morten/attack/2: Fire Bolt: hit, 7 fire dmg. Flying Snake A 5 → 0 HP, dead.', '--line', 'foe/attack/2: Snake B bites: hit, 6 dmg. Morten 20 → 14 HP.',
      '--die', '1d20+5:15:AC 14:hit', '--die', '1d10:7', '--die', '1d20+4:17:AC 15:hit', '--die', '2d4:3,2',
      '--hp', '14/20', '--foe', 'Flying Snake A=0');
    step = 'the live card';
    await waitFor(() => page.locator('#story .sec.live').filter({ hasText: 'Fire Bolt kills one snake' }).count(), 'the beat on the live card');
    const hud = await waitFor(() => page.locator('#hud').innerText().then((x) => (/14\/20 HP/.test(x) ? x : null)), 'the HUD following the beat (14/20 HP)');
    expect(hud, 'the HUD');
    await page.locator('#story .sec.live').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(SHOTS, 'loop-live.png') });
    gm('morten', '--xp', '+50', '--coins', '+5 GP');
    gm('section', '--file', md('fight.md', '---\nkind: fight\ntitle: Room 1.1 · 2 Flying Snakes (CR 1/8 each) · Low, 50 XP · cleared\n'
      + 'difficulty: Low\nxp: 50\noutcome: cleared\nloot: +5 GP\n---\nTwo Fire Bolts and the snakes were done.\n\n### Trace\n'
      + '- R2 morten/attack/2: Fire Bolt: hit, 8 fire dmg. Flying Snake B 5 → 0 HP, dead.\n'), '--die', '1d20+5:18:AC 14:hit', '--die', '1d10:8');
    gm('state', '--awaiting', 'orders', '--status', 'awaiting', '--prompt', "Month 2's orders", '--month', '2', '--day', '1', '--doing', '');

    // ---- the page: the section with the player's words, the box back to orders ----
    step = 'the settled section';
    const sec = page.locator('#story article.fcard:not(.live)').filter({ hasText: 'Two Fire Bolts' });
    await waitFor(() => sec.count(), 'the fight section');
    const words = await waitFor(async () => {
      const t = await page.locator('#story .you').allInnerTexts();
      return t.find((x) => x.includes(plan)) || null;
    }, "the player's words under the section that answered them");
    expect(/Orders: to .*Delve floor 1/.test(words), `the words name the orders: ${words}`);
    expect(!(await page.locator('#story .sec.live').count()), 'the live card is gone (the section replaced it)');
    await waitFor(() => page.locator('#story .answer [data-row="travel"]').count(), 'the answer box offers the orders form again');
    const status = await page.locator('#story .answer .status').innerText();
    expect(/Your move/.test(status) && /Month 2's orders/.test(status), `the status line asks for month 2's orders: ${status}`);
    expect(await page.locator('#story .fcard .track svg').count() >= 1, 'the fight card has its HP chart');
    await page.screenshot({ path: path.join(SHOTS, 'loop-settled.png'), fullPage: false });
    const left = JSON.parse(run(process.execPath, [path.join(WEB, 'dev', 'db.mjs'), 'dump', 'moves', '--port', String(port)], 'db.mjs dump').stdout);
    expect(!left.length, `the answered move is gone from the store: ${JSON.stringify(left)}`);
    const check = spawnSync('python3', [path.join(TOOLS, 'check_table.py'), DIR], { encoding: 'utf8' });
    expect(check.status === 0, `check_table: ${check.stdout}${check.stderr}`);
    expect(!errors.length, `console errors: ${errors.join('\n')}`);
    ok = true;
    console.log(`e2e-loop: ok (${Date.now() - t0} ms) · shots ${SHOTS}`);
  } catch (err) {
    console.log(`e2e-loop: FAIL at ${step}\n  ${err instanceof Failed ? err.message : err.stack}`);
  } finally {
    await browser.close();
    server.kill();
    if (!KEEP) fs.rmSync(tmp, { recursive: true, force: true });
    else console.log(`kept: ${tmp}`);
  }
  process.exit(ok ? 0 : 1);
}

main().catch((err) => { console.error(err); process.exit(2); });
