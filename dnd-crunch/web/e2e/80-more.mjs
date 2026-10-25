// The More panels' checks: Months, Rules, Talk, Table, the first-visit notes and the
// unread marks. Each reads the seeded store fresh; no fixture value is hard-coded.

const KEYS = ['who', 'stop', 'fights', 'world', 'dice', 'mode', 'habits'];

async function state(t) {
  const d = await t.api.doc('game', 'state');
  return d ? d.data : null;
}

async function ready(page) {
  await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().loaded.story);
}

async function openMore(t, chip, opts = {}) {
  const page = await t.open(opts);
  await ready(page);
  if (opts.width && opts.width >= 900) await page.click(`#dtabs button[data-drawer="${chip}"]`);
  else {
    await page.click('#tabs button[data-view="more"]');
    await page.click(`#more-tabs button[data-more="${chip}"]`);
  }
  await page.waitForSelector(`#${chip} .card`, { state: 'visible' });
  return page;
}

async function noSideScroll(t, page, where) {
  const w = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  t.expect(w.sw <= w.cw, `${where}: the page scrolls sideways (${w.sw} > ${w.cw} px)`);
}

async function smallTargets(page, root) {
  return page.evaluate((r) => Array.from(document.querySelectorAll(`${r} button`))
    .filter((b) => b.getClientRects().length && !b.closest('.note'))
    .map((b) => ({ t: b.textContent.trim().slice(0, 30), h: Math.round(b.getBoundingClientRect().height), w: Math.round(b.getBoundingClientRect().width) }))
    .filter((x) => x.h < 44 || x.w < 44), root);
}

async function lastMove(t, kind) {
  const docs = (await t.api.docs('moves')).filter((d) => d.data.kind === kind).sort((a, b) => b.data.seq - a.data.seq);
  return docs[0] || null;
}

export const checks = [
  {
    name: 'more: Months lists the months played and a row opens the Story there',
    async run(t) {
      const st = await state(t);
      const story = await t.api.docs('story');
      const months = new Set(story.map((d) => d.data.month).filter((m) => Number.isInteger(m)));
      if (st && Number.isInteger(st.month) && st.status !== 'ended') months.add(st.month);
      const page = await openMore(t, 'months');
      const rows = await page.locator('#months [data-goto-month]').evaluateAll((bs) => bs.map((b) => +b.dataset.gotoMonth));
      t.expect(JSON.stringify(rows) === JSON.stringify([...months].sort((a, b) => a - b)), `rows ${JSON.stringify(rows)}, want ${JSON.stringify([...months])}`);
      const text = await page.locator('#months').innerText();
      for (const m of months) t.expect(text.includes(`Month ${m}`), `"Month ${m}" in the Months tab`);
      const fights = story.filter((d) => d.data.kind === 'fight').length;
      const pips = await page.locator('#months .pips i').count();
      t.expect(pips >= fights, `a pip a fight: ${pips} pips for ${fights} fights`);
      t.expect(!/\b[A-D][1-5]\b →/.test(text), 'hexes are named in words, not codes first');
      await noSideScroll(t, page, 'months');
      const small = await smallTargets(page, '#months');
      t.expect(!small.length, `small tap targets: ${JSON.stringify(small)}`);
      await t.shot(page, 'phone-months');
      // a row opens the Story on that month and says so to the Story panel
      await page.evaluate(() => { window.__goto = null; document.addEventListener('table:goto', (e) => { window.__goto = e.detail; }); });
      const first = rows[0];
      await page.click(`#months [data-goto-month="${first}"]`);
      await t.waitFor(() => page.evaluate(() => T.app.nav().view === 'story'), 'the Story view');
      const got = await page.evaluate(() => window.__goto);
      t.expect(got && got.month === first, `table:goto with month ${first}, got ${JSON.stringify(got)}`);
      const local = await page.evaluate(() => T.ui.local.get('goto', null));
      t.expect(local && local.month === first, 'the goto is kept in T.ui.local');
      // the Story has the month's header in view (the Story's own scroll, or this file's)
      const top = await page.evaluate((m) => {
        const el = document.querySelector(`#story [data-month="${m}"], #story .month[data-m="${m}"]`);
        return el ? el.getBoundingClientRect().top : null;
      }, first);
      if (top !== null) t.expect(top >= 0 && top < 400, `the month ${first} header is near the top: ${top} px`);
    },
  },
  {
    name: 'more: Rules shows every section, folded, with a contents list',
    async run(t) {
      const rules = await t.api.doc('game', 'rules');
      const secs = rules ? rules.data.sections : [];
      const page = await openMore(t, 'rules');
      const n = await page.locator('#rules details.rule').count();
      t.expect(n === secs.length, `${n} folds for ${secs.length} sections`);
      if (!secs.length) return;
      t.expect(await page.locator('#rules .toc button').count() === secs.length, 'a contents entry a section');
      t.expect(await page.locator('#rules details.rule[open]').count() === 0, 'folded at first');
      const last = secs[secs.length - 1];
      await page.click(`#rules .toc button[data-rule-go="${last.id}"]`);
      t.expect(await page.locator(`#rules details.rule[data-rule="${last.id}"]`).evaluate((d) => d.open), 'the contents entry opens its section');
      t.expect(await page.locator(`#rules details.rule[data-rule="${last.id}"] .md`).isVisible(), 'the section\'s Markdown shows');
      // the fold survives a store change (a re-render)
      await t.api.batch([{ op: 'set', collection: 'log', doc_id: 'l0990', data: { v: 1, seq: 990, text: 'thinking', at: new Date().toISOString() } }]);
      await t.waitFor(() => page.evaluate(() => T.app.view().logs.some((l) => l.seq === 990)), 'the log line');
      await page.waitForTimeout(100);
      t.expect(await page.locator(`#rules details.rule[data-rule="${last.id}"]`).evaluate((d) => d.open), 'the fold stays open across a render');
      await noSideScroll(t, page, 'rules');
      await t.shot(page, 'phone-rules');
    },
  },
  {
    name: 'more: Talk lists the asides and sends an out-of-game say move',
    async run(t) {
      const story = await t.api.docs('story');
      const asides = story.filter((d) => d.data.kind === 'aside').length;
      const page = await openMore(t, 'talk');
      t.expect(await page.locator('#talk .sec.aside').count() === asides, `${asides} asides shown`);
      t.expect(await page.locator('#talk-send').isDisabled(), 'Send is off with an empty box');
      const q = 'Does a Shadow\'s Strength drain stack with exhaustion?';
      await page.fill('#talk-text', q);
      await page.click('#talk-send');
      const mv = await t.waitFor(async () => (await t.api.docs('moves')).find((d) => d.data.kind === 'say' && d.data.text === q), 'the say move in the store');
      const keys = Object.keys(mv.data).sort().join(',');
      t.expect(keys === 'at,kind,ooc,seq,text,v', `the move's fields: ${keys}`);
      t.expect(mv.data.ooc === true && mv.data.v === 1 && mv.doc_id === `m${String(mv.data.seq).padStart(4, '0')}`, `the move's shape: ${JSON.stringify(mv)}`);
      await t.waitFor(() => page.locator('#talk .talk-list').innerText().then((s) => s.includes(q)), 'the question in the list');
      await t.waitFor(async () => (await page.inputValue('#talk-text')) === '', 'the box cleared');
      // the GM answers: the move goes, an aside lands with the words
      await t.api.batch([
        { op: 'delete', collection: 'moves', doc_id: mv.doc_id, if_version: mv.version },
        { op: 'set', collection: 'story', doc_id: 's0991', data: { v: 1, seq: 991, kind: 'aside', ooc: true, month: 3, day: 1, title: 'Aside (out of game)', prose: ['They stack: the drain is its own thing.'], answered: [mv.doc_id], words: [{ move: mv.doc_id, text: q }] } },
      ]);
      await t.waitFor(() => page.locator('#talk .sec.aside').count().then((n) => n === asides + 1), 'the answer as an aside');
      const list = await page.locator('#talk .talk-list').innerText();
      t.expect(list.indexOf(q) < list.indexOf('They stack'), 'the question before its answer');
      t.expect(!list.includes('waiting for the GM'), 'no longer waiting');
      await noSideScroll(t, page, 'talk');
      await t.shot(page, 'phone-talk');
    },
  },
  {
    name: 'more: a dial sends a table move with the whole dials object and shows pending',
    async run(t) {
      const st = await state(t);
      const page = await openMore(t, 'table');
      const cur = st.table;
      const to = cur.fights === 'turning' ? 'summary' : 'turning';
      await page.click(`#table [data-dial="fights"][data-val="${to}"]`);
      await t.waitFor(() => page.locator('#table [data-dial-row="fights"] .pending').isVisible(), 'pending on the dial');
      const mv = await t.waitFor(() => lastMove(t, 'table'), 'the table move');
      const tb = mv.data.table;
      t.expect(KEYS.every((k) => k in tb) && Object.keys(tb).length === KEYS.length, `the whole dials object: ${JSON.stringify(tb)}`);
      t.expect(tb.fights === to, `fights is ${to}`);
      for (const k of KEYS) if (k !== 'fights') t.expect(JSON.stringify(tb[k]) === JSON.stringify(cur[k]), `${k} unchanged`);
      t.expect(await page.getAttribute(`#table [data-dial="fights"][data-val="${to}"]`, 'aria-pressed') === 'true', 'the asked setting is pressed');
      await t.shot(page, 'phone-table-pending');
      // the GM writes it back: pending goes
      const sd = await t.api.doc('game', 'state');
      await t.api.batch([
        { op: 'delete', collection: 'moves', doc_id: mv.doc_id, if_version: mv.version },
        { op: 'update', collection: 'game', doc_id: 'state', data: { table: tb }, if_version: sd.version },
      ]);
      await t.waitFor(() => page.locator('#table [data-dial-row="fights"] .pending').count().then((n) => n === 0), 'pending cleared');
      const small = await smallTargets(page, '#table');
      t.expect(!small.length, `small tap targets: ${JSON.stringify(small)}`);
      await noSideScroll(t, page, 'table');
    },
  },
  {
    name: 'more: the presets set the right dials, and Take over sends a take move',
    async run(t) {
      const st = await state(t);
      const page = await openMore(t, 'table');
      await page.click('#table [data-preset="folded"]');
      let mv = await t.waitFor(() => lastMove(t, 'table'), 'the folded preset\'s move');
      let tb = mv.data.table;
      t.expect(tb.who === 'dm' && tb.stop === 'month' && tb.fights === 'line' && tb.world === 'story', `folded: ${JSON.stringify(tb)}`);
      t.expect(tb.dice === st.table.dice && tb.mode === st.table.mode, 'the preset leaves dice and the table mode');
      t.expect(await page.getAttribute('#table [data-preset="folded"]', 'aria-pressed') === 'true', 'the preset shows as on');
      const seq = mv.data.seq;
      await page.click('#table [data-preset="input"]');
      mv = await t.waitFor(async () => { const m = await lastMove(t, 'table'); return m && m.data.seq > seq ? m : null; }, 'the more-input preset\'s move');
      tb = mv.data.table;
      t.expect(tb.who === 'you' && tb.stop === 'fight' && tb.fights === 'line', `more input keeps the fights setting asked before: ${JSON.stringify(tb)}`);
      await page.click('#table [data-preset="autoplay"]');
      mv = await t.waitFor(async () => { const m = await lastMove(t, 'table'); return m && m.data.seq > seq + 1 ? m : null; }, 'the autoplay preset\'s move');
      tb = mv.data.table;
      t.expect(tb.who === 'dm' && tb.stop === 'month' && tb.fights === 'live' && tb.world === 'story', `autoplay: ${JSON.stringify(tb)}`);
      // take over
      const want = st.table.who === 'you' ? 'dm' : 'you';
      await page.click(`#table [data-take="${want}"]`);
      const tk = await t.waitFor(() => lastMove(t, 'take'), 'the take move');
      t.expect(tk.data.who === want, `take ${want}: ${JSON.stringify(tk.data)}`);
      await t.waitFor(() => page.locator('#table [data-take-row] .pending').isVisible(), 'the take is pending');
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { table: Object.assign({}, st.table, { who: want }) } });
      await t.waitFor(() => page.locator(`#table [data-take="${want === 'you' ? 'dm' : 'you'}"]`).isVisible(), 'the button turns round');
      await t.shot(page, 'phone-table');
    },
  },
  {
    name: 'more: the habits are edited and sent as lines',
    async run(t) {
      const st = await state(t);
      const page = await openMore(t, 'table');
      const n = await page.locator('#table textarea[data-habit]').count();
      t.expect(n === st.table.habits.length, `${n} habit lines for ${st.table.habits.length}`);
      await page.click('#table [data-habit-add]');
      await page.locator('#table textarea[data-habit]').last().fill('Drop the purse before each new door.');
      // a store change does not lose the typing
      await t.api.batch([{ op: 'set', collection: 'log', doc_id: 'l0992', data: { v: 1, seq: 992, text: 'x', at: new Date().toISOString() } }]);
      await t.waitFor(() => page.evaluate(() => T.app.view().logs.some((l) => l.seq === 992)), 'the log line');
      t.expect(await page.locator('#table textarea[data-habit]').count() === n + 1, 'the new line survives a render');
      await page.click('#table [data-habits-send]');
      const mv = await t.waitFor(() => lastMove(t, 'table'), 'the table move');
      const h = mv.data.table.habits;
      t.expect(h.length === n + 1 && h[n] === 'Drop the purse before each new door.', `habits: ${JSON.stringify(h)}`);
      t.expect(mv.data.table.fights === st.table.fights, 'the dials ride along unchanged');
    },
  },
  {
    name: 'more: the unread dot shows for a new section and clears on the Story',
    async run(t) {
      const st = await state(t);
      const page = await t.open();
      await ready(page);
      const dot = '#tabs button[data-view="story"] .dot';
      t.expect(await page.locator(dot).isHidden(), 'no dot on a first visit');
      await page.click('#tabs button[data-view="realm"]');
      const seq = (st ? st.lastSeq : 0) + 50;
      await t.api.batch([{ op: 'set', collection: 'story', doc_id: `s${String(seq).padStart(4, '0')}`, data: { v: 1, seq, kind: 'travel', month: st ? st.month : 1, day: 2, hex: 'B5', title: 'A new day on the road', prose: ['He walked.'] } }]);
      await t.waitFor(() => page.locator(dot).isVisible(), 'the dot on Story');
      // it outlives a reload while unseen
      await page.reload();
      await ready(page);
      await t.waitFor(() => page.locator(dot).isVisible(), 'the dot after a reload');
      await t.shot(page, 'phone-unread');
      await page.click('#tabs button[data-view="story"]');
      await t.waitFor(() => page.locator(dot).isHidden(), 'the dot gone on the Story');
      await page.click('#tabs button[data-view="morten"]');
      await page.waitForTimeout(150);
      t.expect(await page.locator(dot).isHidden(), 'and it stays gone');
      // a new aside marks Talk (and More)
      await t.api.batch([{ op: 'set', collection: 'story', doc_id: `s${String(seq + 1).padStart(4, '0')}`, data: { v: 1, seq: seq + 1, kind: 'aside', ooc: false, month: st ? st.month : 1, title: 'Aside', prose: ['A ruling.'] } }]);
      await t.waitFor(() => page.locator('#tabs button[data-view="more"] .dot').isVisible(), 'the dot on More for a new aside');
      await page.click('#tabs button[data-view="more"]');
      await page.click('#more-tabs button[data-more="talk"]');
      await t.waitFor(() => page.locator('#tabs button[data-view="more"] .dot').isHidden(), 'the More dot gone on Talk');
    },
  },
  {
    name: 'more: first-visit notes on every tab, dismissed once',
    async run(t) {
      const page = await t.open();
      await ready(page);
      // every tab opens with a note: the panel's own, or the one this file places before its pane
      for (const tab of ['story', 'morten', 'realm', 'fights']) {
        await page.click(`#tabs button[data-view="${tab}"]`);
        await t.waitFor(() => page.evaluate((id) => Array.from(document.querySelectorAll(`#${id} .note, .tab-note[data-for="${id}"] .note`))
          .some((n) => n.getClientRects().length > 0), tab), `a first-visit note on ${tab}`);
      }
      // a placed note shows on its own tab only
      const placed = await page.locator('.tab-note[data-for="morten"] .note').count();
      if (placed) {
        await page.click('#tabs button[data-view="fights"]');
        t.expect(await page.locator('.tab-note[data-for="morten"]').isHidden(), 'Morten\'s note hides on Fights');
        await page.click('#tabs button[data-view="morten"]');
        await page.click('.tab-note[data-for="morten"] .note button');
        await page.reload();
        await ready(page);
        await page.waitForTimeout(150);
        t.expect(await page.locator('.tab-note[data-for="morten"] .note').count() === 0, 'Morten\'s note stays dismissed');
      }
      await page.click('#tabs button[data-view="more"]');
      await t.waitFor(() => page.locator('#months .note[data-note="tab.more"]').isVisible(), 'the More note');
      await page.click('#months .note[data-note="tab.more"] button');
      await page.click('#more-tabs button[data-more="rules"]');
      await page.waitForTimeout(150);
      t.expect(await page.locator('.note[data-note="tab.more"]').count() === 0, 'the More note is gone from every More tab');
    },
  },
  {
    name: 'more: the Table tab switches the theme',
    async run(t) {
      const page = await openMore(t, 'table');
      await page.click('#table [data-theme-set="dark"]');
      t.expect(await page.evaluate(() => T.app.theme()) === 'dark', 'dark');
      t.expect(await page.getAttribute('#table [data-theme-set="dark"]', 'aria-pressed') === 'true', 'Dark pressed');
      await t.shot(page, 'phone-table-dark');
      await page.click('#table [data-theme-set="system"]');
      t.expect(await page.evaluate(() => document.documentElement.dataset.theme === undefined), 'follows the device');
    },
  },
  {
    name: 'more: the four tabs at 1280 px and in the dark, and with no store',
    async run(t) {
      for (const scheme of ['light', 'dark']) {
        for (const w of [412, 1280]) {
          for (const chip of ['months', 'rules', 'talk', 'table']) {
            const page = await openMore(t, chip, { width: w, height: w > 900 ? 900 : 915, colorScheme: scheme });
            await noSideScroll(t, page, `${chip} ${w} ${scheme}`);
            if (chip === 'rules') await page.locator('#rules details.rule').first().evaluate((d) => { d.open = true; }).catch(() => {});
            await t.shot(page, `${w < 900 ? 'phone' : 'wide'}-${chip}-${scheme}`);
            await page.context().close();
          }
        }
      }
      const page = await t.open({ query: 'nodb=1' });
      await page.click('#tabs button[data-view="more"]');
      for (const chip of ['months', 'rules', 'talk', 'table']) {
        await page.click(`#more-tabs button[data-more="${chip}"]`);
        const txt = await page.locator(`#${chip}`).innerText();
        t.expect(txt.trim().length > 0, `${chip} says something with no store`);
      }
      t.expect(await page.locator('#talk-send').isDisabled(), 'no sending with no store');
    },
  },
];
