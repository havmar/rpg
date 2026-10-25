// The shell's checks: the now line, the views and the bottom bar, the drawer at 1280 px,
// sending a move and the wake, a live beat landing, the page without a store, the themes.
// Panels add their own files (e2e/50-story.mjs, …) with the same shape.

const VIEWS = ['story', 'morten', 'realm', 'fights', 'more'];
const PANES = ['story', 'morten', 'realm', 'fights', 'months', 'rules', 'talk', 'table'];

async function visiblePanes(page) {
  return page.evaluate((ids) => ids.filter((id) => {
    const el = document.getElementById(id);
    return el && el.getClientRects().length > 0 && getComputedStyle(el).display !== 'none';
  }), PANES);
}

async function noSideScroll(t, page, where) {
  const w = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  t.expect(w.sw <= w.cw, `${where}: the page scrolls sideways (${w.sw} > ${w.cw} px)`);
}

async function wakeOn(t) {
  const d = await t.api.doc('game', 'state');
  if (!(d && d.data.wake && d.data.wake.on === true)) await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { wake: { on: true } } });
}

async function state(t) {
  const d = await t.api.doc('game', 'state');
  return d ? d.data : null;
}

export const checks = [
  {
    name: 'phone: the now line shows the month and the HUD',
    async run(t) {
      const st = await state(t);
      const page = await t.open();
      if (st && Number.isInteger(st.month)) {
        await t.waitFor(() => page.locator('#now-where').innerText().then((s) => s.includes(`Month ${st.month}`)), `"Month ${st.month}" in the now line`);
      }
      if (st && st.hud && typeof st.hud.hp === 'number') {
        const hud = await page.locator('#hud').innerText();
        t.expect(hud.includes(`${st.hud.hp}/${st.hud.maxHp} HP`), `the HUD shows ${st.hud.hp}/${st.hud.maxHp} HP, got "${hud}"`);
      }
      t.expect(await page.locator('#notice').isHidden(), 'no store notice with a working store');
      const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
      t.expect(bg && bg !== 'rgba(0, 0, 0, 0)', 'body has an explicit background');
      await noSideScroll(t, page, 'story');
      await t.shot(page, 'phone-story');
    },
  },
  {
    name: 'phone: each bottom-bar tab switches the view, no sideways scroll',
    async run(t) {
      const page = await t.open();
      for (const v of VIEWS) {
        await page.click(`#tabs button[data-view="${v}"]`);
        const shown = await visiblePanes(page);
        const want = v === 'more' ? 'months' : v;
        t.expect(shown.length === 1 && shown[0] === want, `after ${v}: visible panes ${JSON.stringify(shown)}, want ["${want}"]`);
        t.expect(await page.getAttribute(`#tabs button[data-view="${v}"]`, 'aria-current') === 'true', `${v} is marked current`);
        await noSideScroll(t, page, v);
        await t.shot(page, `phone-${v}`);
      }
      for (const m of ['rules', 'talk', 'table', 'months']) {
        await page.click(`#more-tabs button[data-more="${m}"]`);
        const shown = await visiblePanes(page);
        t.expect(shown.length === 1 && shown[0] === m, `More → ${m}: visible panes ${JSON.stringify(shown)}`);
      }
      // the view is remembered across a reload
      await page.click('#tabs button[data-view="realm"]');
      await page.reload();
      await page.waitForFunction(() => window.T && window.T.app && window.T.app.view());
      t.expect((await visiblePanes(page))[0] === 'realm', 'the last view comes back after a reload');
    },
  },
  {
    name: 'phone: the shell\'s tap targets are 44 px or more',
    async run(t) {
      const page = await t.open();
      await page.click('#tabs button[data-view="more"]');
      const small = await page.evaluate(() => Array.from(document.querySelectorAll('#tabs button, #more-tabs button, .note button'))
        .filter((b) => b.getClientRects().length)
        .map((b) => ({ t: b.textContent.trim(), h: b.getBoundingClientRect().height, w: b.getBoundingClientRect().width }))
        .filter((r) => r.h < 44 || r.w < 44));
      t.expect(!small.length, `small tap targets: ${JSON.stringify(small)}`);
    },
  },
  {
    name: 'a say move lands in moves/ and wakes the GM: a new thread per move, each resolved',
    async run(t) {
      const st = await state(t);
      t.expect(st, 'the fixture has game/state');
      await wakeOn(t);
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      t.expect((await page.evaluate(() => T.app.view().wake.reach)) === 'available', 'canSendToClaude is asked once at load');
      t.expect((await t.api.calls()).length === 0, 'nothing is sent on load');
      const moves0 = await t.api.docs('moves');
      const want = Math.max(st.lastMove || 0, ...moves0.map((d) => d.data.seq || 0)) + 1;
      const id = `m${String(want).padStart(4, '0')}`;
      const r = await page.evaluate(() => T.store.send('say', { text: 'Leave the sleeping boar; go round.', ooc: false }));
      t.expect(r && r.id === id, `the move id is ${id}, got ${JSON.stringify(r)}`);
      const doc = await t.waitFor(() => t.api.doc('moves', id), `${id} in the store`);
      const d = doc.data;
      t.expect(d.v === 1 && d.kind === 'say' && d.seq === want && d.text === 'Leave the sleeping boar; go round.' && d.ooc === false && typeof d.at === 'string', `the move's body: ${JSON.stringify(d)}`);
      const wakes = await t.waitFor(async () => { const w = await t.api.wakes(); return w.length && w[0].resolved ? w : null; }, 'a wake, resolved');
      t.expect(wakes[0].text === `Table move ${id} (say).`, `the wake's text: ${wakes[0].text}`);
      t.expect(wakes[0].anchor, 'the wake starts a thread at an anchor');
      await page.waitForFunction(() => T.app.view().wake.state === 'called');
      await t.waitFor(() => page.evaluate(() => T.app.view().pending.length === 0), 'nothing pending once the move is in the store');
      t.expect(await page.evaluate((mid) => T.app.view().moves.some((m) => m.id === mid && m.mine), id), 'the move shows as sent, and mine');
      const r2 = await page.evaluate(() => T.store.send('play', { scope: 'fight', text: '' }));
      const w2 = await t.waitFor(async () => { const w = await t.api.wakes(); return w.length > 1 && w[1].resolved ? w : null; }, 'a second wake, resolved');
      t.expect(r2.id === `m${String(want + 1).padStart(4, '0')}`, `the second move is the next seq, got ${r2.id}`);
      t.expect(w2[1].anchor && w2[1].threadId !== wakes[0].threadId, 'the second wake is a thread of its own (the GM tells a wake\'s second arrival by its thread)');
      t.expect(w2.length === 2, `one wake per move: ${w2.length}`);
      await t.shot(page, 'phone-sent');
    },
  },
  {
    name: 'the wake while a call is in flight: moves that land meanwhile get one more call, naming the newest',
    async run(t) {
      await wakeOn(t);
      const page = await t.open({ query: 'wakedelay=700' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      const ids = await page.evaluate(async () => {
        const a = await T.store.send('say', { text: 'one', ooc: false });
        const b = await T.store.send('say', { text: 'two', ooc: false });
        const c = await T.store.send('say', { text: 'three', ooc: false });
        return [a.id, b.id, c.id];
      });
      await page.waitForFunction(() => T.app.view().wake.state === 'called' && T.app.view().wake.move !== null);
      await page.waitForTimeout(1600);
      const w = await t.api.calls();
      t.expect(w.length === 2, `two calls for three quick moves, got ${w.length}: ${w.map((x) => x.text).join(' | ')}`);
      t.expect(w[0].text.includes(ids[0]) && w[1].text.includes(ids[2]), `the first names ${ids[0]}, the second the newest ${ids[2]}: ${w.map((x) => x.text).join(' | ')}`);
      t.expect((await page.evaluate(() => T.app.view().wake.move)) === ids[2], 'the status names the newest move');
      t.expect((await t.api.docs('moves')).length >= 3, 'every move landed: a call in flight holds no write');
    },
  },
  {
    name: 'the wake when the GM is not watching: a reason, one call-again',
    async run(t) {
      await wakeOn(t);
      const page = await t.open({ query: 'cansend=no_session' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      await page.evaluate(() => T.store.send('say', { text: 'Anyone there?', ooc: true }));
      await page.waitForFunction(() => T.app.view().wake.state === 'unavailable');
      const w = await page.evaluate(() => T.app.view().wake);
      t.expect(/not watching/.test(w.reason), `the reason says the GM is not watching: "${w.reason}"`);
      t.expect(w.reach === 'no_session' && w.again === true, `reach no_session, a call-again offered: ${JSON.stringify(w)}`);
      t.expect((await t.api.calls()).length === 0, 'nothing was sent: canSendToClaude said no');
      await page.waitForTimeout(400);
      t.expect((await t.api.calls()).length === 0, 'and none is retried in a loop');
    },
  },
  {
    name: 'the wake refused for good (forbidden): no more calls this page load',
    async run(t) {
      await wakeOn(t);
      const page = await t.open({ query: 'wakefail=forbidden' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      await page.evaluate(() => T.store.send('say', { text: 'first', ooc: false }));
      await page.waitForFunction(() => T.app.view().wake.state === 'unavailable');
      const w = await page.evaluate(() => T.app.view().wake);
      t.expect(w.code === 'forbidden' && w.again === false && /commenting from the page is off/.test(w.reason), `a permanent refusal: ${JSON.stringify(w)}`);
      await page.evaluate(() => T.store.send('say', { text: 'second', ooc: false }));
      await page.evaluate(() => T.store.wakeAgain());
      await page.waitForTimeout(300);
      t.expect((await t.api.calls()).length === 1, `one call only: ${(await t.api.calls()).length}`);
      t.expect((await t.api.docs('moves')).length >= 2, 'the moves still land');
    },
  },
  {
    name: 'the wake refused for now (rate_limited): the next move tries again',
    async run(t) {
      await wakeOn(t);
      const page = await t.open({ query: 'wakefail=rate_limited' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      await page.evaluate(() => T.store.send('say', { text: 'first', ooc: false }));
      await page.waitForFunction(() => T.app.view().wake.state === 'failed');
      const w = await page.evaluate(() => T.app.view().wake);
      t.expect(w.code === 'rate_limited' && w.again === true, `a refusal for now: ${JSON.stringify(w)}`);
      await page.waitForTimeout(300);
      t.expect((await t.api.calls()).length === 1, 'not retried on its own');
      await page.evaluate(() => T.store.send('say', { text: 'second', ooc: false }));
      await t.waitFor(async () => (await t.api.calls()).length === 2, 'the next move calls again');
    },
  },
  {
    name: 'the wake off in game/state: no call, the status says so',
    async run(t) {
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { wake: { on: false } } });
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      await page.evaluate(() => T.store.send('say', { text: 'quietly', ooc: false }));
      await page.waitForFunction(() => T.app.view().wake.state === 'off');
      t.expect((await t.api.calls()).length === 0, 'no call');
    },
  },
  {
    name: 'a move is pending until the store confirms it (our own write shows at once, unconfirmed)',
    async run(t) {
      const page = await t.open({ query: 'delay=500' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      const id = await page.evaluate(() => {
        const p = T.store.send('say', { text: 'slowly', ooc: false });
        window.__sent = p;
        return new Promise((r) => setTimeout(() => r(T.store.raw().pending.map((x) => x.id)[0]), 250));
      });
      const early = await page.evaluate((mid) => ({
        local: T.store.raw().cols.moves.some((d) => d.id === mid && d.pending),
        pending: T.app.view().pending.some((p) => p.id === mid && p.status === 'sending'),
        sent: T.app.view().moves.some((m) => m.id === mid),
      }), id);
      t.expect(early.local && early.pending && !early.sent, `before the store confirms: ${JSON.stringify(early)}`);
      await page.evaluate(() => window.__sent);
      await t.waitFor(() => page.evaluate((mid) => T.app.view().pending.length === 0 && T.app.view().moves.some((m) => m.id === mid && m.mine), id), 'the move confirmed: sent, not pending');
    },
  },
  {
    name: 'a read-only viewer: the store refuses the write and the page stops offering it',
    async run(t) {
      const page = await t.open({ query: 'readonly=quiet' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      t.expect((await page.evaluate(() => T.app.view().canWrite)) === true, 'can("data.write") said nothing: the inputs stay');
      const code = await page.evaluate(() => T.store.send('say', { text: 'x', ooc: false }).then(() => 'sent', (e) => e.code));
      t.expect(code === 'invalid_argument', `the write is refused: ${code}`);
      await page.waitForFunction(() => T.app.view().canWrite === false);
      const v = await page.evaluate(() => ({ canWrite: T.app.view().canWrite, failed: T.app.view().pending.find((p) => p.status === 'failed') }));
      t.expect(v.canWrite === false && v.failed && /not write/.test(v.failed.error), `read-only for the rest of the visit: ${JSON.stringify(v)}`);
      const again = await page.evaluate(() => T.store.send('say', { text: 'y', ooc: false }).then(() => 'sent', (e) => e.code));
      t.expect(again === 'read_only', `the next send is refused before the store: ${again}`);
      t.expect((await t.api.docs('moves')).length === 0, 'nothing was written');
      const page2 = await t.open({ query: 'readonly=1' });
      await page2.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().canWrite === false);
    },
  },
  {
    name: 'a slow first load: the cache\'s empty snapshot is not "the table is empty"',
    async run(t) {
      const page = await t.open({ query: 'cache=1200' });
      await page.waitForTimeout(400);
      const early = await page.evaluate(() => ({ ready: T.app.view().ready, opening: T.app.view().opening, notice: document.getElementById('notice').hidden }));
      t.expect(!early.ready && early.opening && early.notice, `still opening, no notice: ${JSON.stringify(early)}`);
      await page.waitForFunction(() => T.app.view().ready && T.app.view().state);
    },
  },
  {
    name: 'a dead bridge (unavailable on a listener): a fresh subscription, and the page stays live',
    async run(t) {
      const page = await t.open({ query: 'dbfailonce=unavailable' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      await page.waitForTimeout(2500);
      t.expect((await page.evaluate(() => T.app.view().db)) === 'ok', 'the store is still ok');
      const at = new Date().toISOString();
      await t.api.batch([{ op: 'set', collection: 'log', doc_id: 'l9001', data: { v: 1, seq: 9001, text: 'after the bridge came back', at } }]);
      await t.waitFor(() => page.evaluate(() => T.app.view().logs.some((l) => l.id === 'l9001')), 'a write after the resubscribe shows live', 8000);
    },
  },
  {
    name: 'a live beat applied as a batch updates the page without a reload',
    async run(t) {
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      const st = await t.api.doc('game', 'state');
      const all = (await t.api.docs()).filter((d) => ['story', 'live', 'log'].includes(d.collection));
      const seq = Math.max(st.data.lastSeq || 0, ...all.map((d) => d.data.seq || 0)) + 1;
      const id = `b${String(seq).padStart(4, '0')}`;
      const at = new Date().toISOString();
      await t.api.batch([
        { op: 'set', collection: 'live', doc_id: id, data: { v: 1, seq, section: { kind: 'fight', title: 'Test fight' }, round: 3, text: 'Ray of Frost hits for 5 dmg.', lines: [], state: {}, at } },
        { op: 'update', collection: 'game', doc_id: 'state', if_version: st.version, data: { lastSeq: seq, status: 'playing', doing: 'writing the e2e beat up' } },
      ]);
      await t.waitFor(() => page.locator('#now-where').innerText().then((s) => s.includes('writing the e2e beat up')), 'the new activity in the now line');
      await t.waitFor(() => page.evaluate((bid) => T.app.view().beats.some((b) => b.id === bid), id), 'the beat in the view model');
      const since = await page.locator('#now-where').innerText();
      t.expect(/just now/.test(since), `the time since the last beat reads "just now": "${since}"`);
      await t.shot(page, 'phone-live-beat');
    },
  },
  {
    name: 'wide (1280 px): the Story and the drawer side by side',
    async run(t) {
      const page = await t.open({ width: 1280, height: 900 });
      const story = await page.locator('#story').boundingBox();
      const drawer = await page.locator('#drawer').boundingBox();
      t.expect(story && drawer && story.x + story.width <= drawer.x + 1, `two zones: story ${JSON.stringify(story)}, drawer ${JSON.stringify(drawer)}`);
      t.expect(await page.locator('#tabs').isHidden(), 'no bottom bar at 1280 px');
      t.expect(await page.locator('#dtabs').isVisible(), 'the drawer tabs show');
      for (const d of ['realm', 'morten', 'fights', 'months', 'rules', 'talk', 'table']) {
        await page.click(`#dtabs button[data-drawer="${d}"]`);
        const shown = await visiblePanes(page);
        t.expect(shown.length === 2 && shown.includes('story') && shown.includes(d), `drawer ${d}: visible ${JSON.stringify(shown)}`);
      }
      await page.click('#dtabs button[data-drawer="realm"]');
      await noSideScroll(t, page, 'wide');
      await t.shot(page, 'wide');
    },
  },
  {
    name: 'no db: a calm notice, and the shell still works',
    async run(t) {
      const page = await t.open({ query: 'nodb=1' });
      await page.waitForFunction(() => T.app.view() && T.app.view().db === 'none');
      const n = await page.locator('#notice').innerText();
      t.expect(n.includes('No table store in this view'), `the notice: "${n}"`);
      for (const v of VIEWS) {
        await page.click(`#tabs button[data-view="${v}"]`);
        t.expect((await visiblePanes(page)).includes(v === 'more' ? 'months' : v), `${v} opens without a store`);
      }
      await page.click('#tabs button[data-view="story"]');
      await noSideScroll(t, page, 'no db');
      await t.shot(page, 'phone-nodb');
    },
  },
  {
    name: 'a revoked store: the page says it stopped updating, keeps what it had',
    async run(t) {
      const page = await t.open({ query: 'dbfail=revoked' });
      await page.waitForFunction(() => T.app.view() && T.app.view().db === 'error');
      const n = await page.locator('#notice').innerText();
      t.expect(n.includes('stopped updating'), `the notice: "${n}"`);
      const st = await state(t);
      if (st && Number.isInteger(st.month)) t.expect((await page.locator('#now-where').innerText()).includes(`Month ${st.month}`), 'the now line keeps the last state');
      const r = await page.evaluate(() => T.store.send('say', { text: 'x' }).then(() => 'sent', (e) => e.code));
      t.expect(r === 'no_store', `a send is refused: ${r}`);
    },
  },
  {
    name: 'no window.claude at all: the shell renders with the notice',
    async run(t) {
      const page = await t.open({ query: 'noclaude=1' });
      await page.waitForFunction(() => T.app.view() && T.app.view().db === 'none');
      t.expect((await page.locator('#notice').innerText()).includes('No table store in this view'), 'the no-store notice');
    },
  },
  {
    name: 'themes: dark by the system, the switch flips it, both have a background',
    async run(t) {
      const page = await t.open({ colorScheme: 'dark' });
      const bgDark = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
      t.expect(bgDark === 'rgb(18, 23, 26)', `dark body background: ${bgDark}`);
      await t.shot(page, 'phone-story-dark');
      await page.click('#tabs button[data-view="more"]');
      await page.click('#more-tabs [data-theme-switch]');
      const theme = await page.evaluate(() => document.documentElement.dataset.theme);
      const bgLight = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
      t.expect(theme === 'light' && bgLight === 'rgb(225, 230, 228)', `after the switch: theme ${theme}, background ${bgLight}`);
      const wide = await t.open({ width: 1280, height: 900, colorScheme: 'dark' });
      await t.shot(wide, 'wide-dark');
    },
  },
];
