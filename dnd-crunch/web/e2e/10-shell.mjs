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
    name: 'a say move lands in moves/ and wakes the GM, twice on one thread',
    async run(t) {
      const st = await state(t);
      t.expect(st, 'the fixture has game/state');
      if (!(st.wake && st.wake.on === true)) await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { wake: { on: true } } });
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      const moves0 = await t.api.docs('moves');
      const want = Math.max(st.lastMove || 0, ...moves0.map((d) => d.data.seq || 0)) + 1;
      const id = `m${String(want).padStart(4, '0')}`;
      const r = await page.evaluate(() => T.store.send('say', { text: 'Leave the sleeping boar; go round.', ooc: false }));
      t.expect(r && r.id === id, `the move id is ${id}, got ${JSON.stringify(r)}`);
      const doc = await t.waitFor(() => t.api.doc('moves', id), `${id} in the store`);
      const d = doc.data;
      t.expect(d.v === 1 && d.kind === 'say' && d.seq === want && d.text === 'Leave the sleeping boar; go round.' && d.ooc === false && typeof d.at === 'string', `the move's body: ${JSON.stringify(d)}`);
      const wakes = await t.waitFor(async () => { const w = await t.api.wakes(); return w.length ? w : null; }, 'a wake');
      t.expect(wakes[0].text === `Table move ${id} (say).`, `the wake's text: ${wakes[0].text}`);
      t.expect(wakes[0].anchor, 'the first wake starts a thread at an anchor');
      await page.waitForFunction(() => T.app.view().wake.state === 'called');
      t.expect((await page.evaluate(() => T.app.view().pending.length)) === 0, 'nothing pending once the move is in the store');
      const r2 = await page.evaluate(() => T.store.send('play', { scope: 'fight', text: '' }));
      const w2 = await t.waitFor(async () => { const w = await t.api.wakes(); return w.length > 1 ? w : null; }, 'a second wake');
      t.expect(r2.id === `m${String(want + 1).padStart(4, '0')}`, `the second move is the next seq, got ${r2.id}`);
      t.expect(w2[1].threadId === wakes[0].threadId && !w2[1].anchor, 'the second wake replies on the same thread');
      await t.shot(page, 'phone-sent');
    },
  },
  {
    name: 'the wake when the GM is not watching: a reason, one call-again',
    async run(t) {
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { wake: { on: true } } });
      const page = await t.open({ query: 'cansend=no_session' });
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      await page.evaluate(() => T.store.send('say', { text: 'Anyone there?', ooc: true }));
      await page.waitForFunction(() => T.app.view().wake.state === 'unavailable');
      const reason = await page.evaluate(() => T.app.view().wake.reason);
      t.expect(/not watching/.test(reason), `the reason says the GM is not watching: "${reason}"`);
      t.expect((await t.api.wakes()).length === 0, 'no wake was recorded');
      await page.waitForTimeout(400);
      t.expect((await t.api.wakes()).length === 0, 'and none is retried in a loop');
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
