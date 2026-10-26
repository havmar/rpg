// The Story's checks (src/js/50-story.js): the stream of months, days and sections over
// whatever fixture the run uses (read fresh, nothing hard-coded), folds, the world's turn
// set apart, the orders form's move, the fight and turn boxes, say/play/take moves, the
// live card growing and settling in place, the reading position, and the other trees
// (dev/sample, dev/fixture-live, an empty store) rendering cleanly.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DEV = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'dev');
const pad = (n) => String(n).padStart(4, '0');

async function seed(t, dir) {
  const res = await fetch(`${t.base}/api/seed`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dir === null ? { docs: [] } : { dir }) });
  t.expect(res.ok, `seeding ${dir}`);
}

async function ready(page) {
  await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().loaded.story);
  await page.waitForTimeout(80);
}

async function noSideScroll(t, page, where) {
  const w = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  t.expect(w.sw <= w.cw, `${where}: the page scrolls sideways (${w.sw} > ${w.cw} px)`);
}

async function stateDoc(t) {
  return t.api.doc('game', 'state');
}

async function setState(t, data) {
  await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data });
}

async function nextSeq(t) {
  const st = await stateDoc(t);
  const all = (await t.api.docs()).filter((d) => ['story', 'live', 'log'].includes(d.collection));
  return Math.max(st ? st.data.lastSeq || 0 : 0, ...all.map((d) => d.data.seq || 0)) + 1;
}

async function moveOf(t, kind, pred = () => true) {
  return t.waitFor(async () => (await t.api.docs('moves')).map((d) => d.data).find((d) => d.kind === kind && pred(d)), `a ${kind} move in the store`);
}

const keyed = (k) => `#stream > [data-key="${k}"]`;

export const checks = [
  {
    name: 'story: the months, days and sections of the fixture, folds kept, the world set apart',
    async run(t) {
      const page = await t.open();
      await ready(page);
      const story = (await t.api.docs('story')).map((d) => ({ id: d.doc_id, ...d.data })).sort((a, b) => a.seq - b.seq);
      t.expect(story.length, 'the fixture has story sections');
      const months = [...new Set(story.map((s) => s.month).filter(Number.isInteger))];
      const newest = Math.max(...months);
      for (const m of months) t.expect(await page.locator(keyed(`m-${m}`)).count() === 1, `a header for month ${m}`);
      const inNewest = story.filter((s) => s.month === newest);
      for (const s of inNewest) t.expect(await page.locator(keyed(s.id)).count() === 1, `section ${s.id} (${s.kind}) is in the stream`);
      const days = [...new Set(inNewest.filter((s) => s.kind !== 'domain' && Number.isInteger(s.day)).map((s) => s.day))];
      for (const d of days) t.expect(await page.locator(keyed(`d-${newest}-${d}`)).count() === 1, `a day row for day ${d}`);
      // each section's story first: its headline is in its card
      for (const s of inNewest.filter((x) => x.headline).slice(0, 6)) {
        const txt = await page.locator(keyed(s.id)).innerText();
        t.expect(txt.includes(s.headline.slice(0, 40)), `${s.id} shows its headline`);
      }
      // the words the player sent show under the section that answered them
      for (const s of inNewest.filter((x) => Array.isArray(x.words) && x.words.length)) {
        t.expect(await page.locator(keyed(`w-${s.id}`)).innerText().then((x) => x.includes(s.words[0].text.slice(0, 30))), `the player's words under ${s.id}`);
      }
      // the month's sum once it is over, its orders in one line
      const st = (await stateDoc(t)).data;
      if (st.month > newest || inNewest.some((s) => s.kind === 'domain')) {
        const h = await page.locator(keyed(`m-${newest}`)).innerText();
        t.expect(/XP/.test(h) && /death/.test(h), `month ${newest}'s sum: "${h}"`);
      }
      // a trace fold opens and stays open across a re-render
      const traced = inNewest.find((s) => s.kind !== 'fight' && s.kind !== 'domain' && Array.isArray(s.trace) && s.trace.length) || inNewest.find((s) => Array.isArray(s.trace) && s.trace.length);
      if (traced) {
        const sum = page.locator(`${keyed(traced.id)} details.trace > summary`).first();
        await sum.scrollIntoViewIfNeeded();
        await sum.click();
        t.expect(await page.locator(`${keyed(traced.id)} details.trace`).first().evaluate((d) => d.open), `${traced.id}'s trace opens`);
        const dice = await page.locator(`${keyed(traced.id)} details.trace .die`).count();
        t.expect(dice > 0, `${traced.id}'s trace shows dice as chips`);
        await t.api.batch([{ op: 'set', collection: 'log', doc_id: 'l9001', data: { v: 1, seq: 9001, text: 'a re-render', at: new Date().toISOString() } }]);
        await t.waitFor(() => page.evaluate(() => T.app.view().logs.some((l) => l.id === 'l9001')), 'the log line');
        await page.waitForTimeout(100);
        t.expect(await page.locator(`${keyed(traced.id)} details.trace`).first().evaluate((d) => d.open), `${traced.id}'s trace is still open after a render`);
      }
      // Morten's and the foes' lines are told apart in a fight's trace
      const fight = inNewest.find((s) => s.kind === 'fight' && s.trace.some((l) => l.who === 'foe') && s.trace.some((l) => l.who === 'morten'));
      if (fight) {
        const card = page.locator(keyed(fight.id));
        await card.locator('details.trace > summary').first().click();
        const cls = await card.locator('details.trace .ln').evaluateAll((els) => els.map((e) => e.className));
        t.expect(cls.some((c) => /them/.test(c)) && cls.some((c) => !/them/.test(c)), `foes' lines and Morten's differ: ${JSON.stringify(cls.slice(0, 4))}`);
      }
      // the world's turn: set apart, numbered, coloured, chips
      const dom = story.find((s) => s.kind === 'domain' && s.domain);
      if (dom && dom.month === newest) {
        const w = page.locator(`${keyed(dom.id)} .sec.world`);
        t.expect(await w.count() === 1, 'the world\'s turn is a .sec.world');
        const other = inNewest.find((s) => ['orders', 'travel', 'opening', 'delve', 'shop'].includes(s.kind));
        if (other) {
          const bgW = await w.evaluate((e) => getComputedStyle(e).backgroundColor);
          const bgO = await page.locator(`${keyed(other.id)} .sec`).first().evaluate((e) => getComputedStyle(e).backgroundColor);
          t.expect(bgW !== bgO, `the world's turn has its own tint (${bgW} vs ${bgO})`);
        }
        const evs = await w.locator('.events li[data-event]').evaluateAll((els) => els.map((e) => ({ n: e.dataset.event, cls: e.className, who: !!e.querySelector('.who') })));
        t.expect(evs.length === dom.domain.happened.length, `${evs.length} events, want ${dom.domain.happened.length}`);
        dom.domain.happened.forEach((h, i) => {
          t.expect(evs[i].n === (h.n === null ? '' : String(h.n)), `event ${i} is numbered ${h.n} like the map's badge (v3: a realm's sentence with no event has no number)`);
          t.expect(evs[i].cls.startsWith('fac-') && evs[i].who, `event ${h.n} has its realm's colour and its who: ${evs[i].cls}`);
        });
        const nx = dom.domain.next;
        for (const [k, list] of [['threat', nx.threats], ['chance', nx.chances], ['open', nx.open]]) {
          t.expect(await w.locator(`.chip.${k}`).count() === list.length, `${list.length} ${k} chips`);
        }
        t.expect(await w.locator('.delta-rows li').count() === dom.domain.tower.length, 'the tower now as before → after rows');
        t.expect(!(await w.locator('details.trace').first().evaluate((d) => d.open)), 'the script\'s log is folded by default');
        await t.shot(page, 'phone-story-world');
        await setState(t, { table: Object.assign({}, st.table, { world: 'report' }) });
        await t.waitFor(() => w.locator('details.trace').first().evaluate((d) => d.open), 'the script\'s log unfolded with world: report');
      }
      await noSideScroll(t, page, 'story');
      await page.evaluate(() => window.scrollTo(0, 0));
      await t.shot(page, 'phone-story-top');
    },
  },
  {
    name: 'story: months before the newest fold; "Older months" opens them; a header toggles its month',
    async run(t) {
      await seed(t, path.join(DEV, 'sample'));
      const page = await t.open();
      await ready(page);
      const story = (await t.api.docs('story')).map((d) => ({ id: d.doc_id, ...d.data }));
      const months = [...new Set(story.map((s) => s.month))].sort((a, b) => a - b);
      t.expect(months.length > 1, 'the sample has several months');
      const newest = months[months.length - 1];
      const old = story.filter((s) => s.month !== newest);
      for (const s of old) t.expect(await page.locator(keyed(s.id)).count() === 0, `${s.id} (month ${s.month}) is folded`);
      for (const m of months) t.expect(await page.locator(keyed(`m-${m}`)).count() === 1, `month ${m}'s header shows`);
      t.expect(await page.locator(`${keyed(`m-${months[0]}`)} .month.folded`).count() === 1, 'an old month header is marked folded');
      await page.locator('.older').click();
      await t.waitFor(async () => (await page.locator(keyed(old[0].id)).count()) === 1, 'the older months open');
      t.expect(await page.locator('.older').count() === 0, 'the button goes once they are open');
      await page.locator(`${keyed(`m-${newest}`)} .month`).click();
      const newSec = story.find((s) => s.month === newest);
      await t.waitFor(async () => (await page.locator(keyed(newSec.id)).count()) === 0, 'the newest month folds on its header');
      await page.locator(`${keyed(`m-${newest}`)} .month`).click();
      await t.waitFor(async () => (await page.locator(keyed(newSec.id)).count()) === 1, 'and opens again');
      // the sample is a live fight: its live card shows under the stream
      const beats = await t.api.docs('live');
      if (beats.length) t.expect(await page.locator(`${keyed('live')} [data-live], ${keyed('live')} .live`).count() >= 1, 'the sample\'s live card');
      await noSideScroll(t, page, 'sample');
      await t.shot(page, 'phone-sample');
    },
  },
  {
    name: 'story: the orders form sends one orders move with the picks',
    async run(t) {
      const st = (await stateDoc(t)).data;
      if (!st.awaiting || st.awaiting.kind !== 'orders' || !st.awaiting.orders) {
        console.log('        (the fixture waits for no orders; skipped)');
        return;
      }
      await setState(t, { wake: { on: true } });
      const o = st.awaiting.orders;
      const page = await t.open();
      await ready(page);
      t.expect(await page.locator('[data-row="travel"]').count() === 1, 'the travel row');
      // a hex other than where Morten is, with a mission in it
      const target = o.hexes.find((h) => h.id !== st.hex && o.missions.some((m) => m.hex === h.id)) || o.hexes[o.hexes.length - 1];
      let btn = page.locator(`[data-f="travel"][data-v="${target.id}"]`);
      if (!(await btn.count())) await page.locator('[data-act="all-hexes"]').click();
      btn = page.locator(`[data-f="travel"][data-v="${target.id}"]`);
      await btn.click();
      await t.waitFor(() => btn.getAttribute('aria-pressed').then((v) => v === 'true'), 'the hex is picked');
      const mIdx = o.missions.findIndex((m) => m.hex === target.id || !m.hex);
      const mission = mIdx >= 0 ? o.missions[mIdx] : null;
      if (mission) {
        // only that hex's missions are offered
        const offered = await page.locator('[data-f="mission"][data-v]:not([data-v=""])').evaluateAll((els) => els.map((e) => +e.dataset.v));
        t.expect(offered.every((i) => !o.missions[i].hex || o.missions[i].hex === target.id), `missions offered for ${target.id}: ${offered}`);
        await page.locator(`[data-f="mission"][data-v="${mIdx}"]`).click();
      }
      // v3: the tower's goal row offers the engine's take/ally/topple choices
      const goal = o.version === 3 && o.goals.length ? o.goals[0] : null;
      if (goal) {
        t.expect(await page.locator('[data-row="goal"]').count() === 1, 'the goal row (v3)');
        await page.locator(`[data-f="goal"][data-v="${goal.goal}"]`).click();
      }
      const aIdx = o.actions.findIndex((a) => a.affordable !== false);
      if (aIdx >= 0) await page.locator(`[data-f="action"][data-v="${aIdx}"]`).click();
      else if (o.actions.length) t.expect(await page.locator('[data-f="action"][data-v="0"]').isDisabled(), 'an action the tower cannot afford is greyed out');
      const realm = o.realms[0];
      if (realm) {
        await page.locator(`[data-f="give"][data-v="${realm}"]`).click();
        await page.fill('[data-a="gp"]', '20');
      }
      await page.fill('#answer-text', 'Safe XP next door; the tower saves.');
      await t.shot(page, 'phone-orders');
      await page.locator('[data-act="send"]').click();
      const mv = await moveOf(t, 'orders');
      const want = {
        travel: target.id,
        mission: mission ? { type: mission.type, target: mission.target } : null,
        give: realm ? { realm, gp: 20 } : null,
        plan: 'Safe XP next door; the tower saves.',
      };
      if (o.version === 3) {
        want.goal = goal ? goal.goal : null;
        want.actions = aIdx >= 0 ? [o.actions[aIdx].action] : [];
      } else want.action = aIdx >= 0 ? o.actions[aIdx].action : null;
      for (const k of Object.keys(want)) t.expect(JSON.stringify(mv[k]) === JSON.stringify(want[k]), `orders.${k}: ${JSON.stringify(mv[k])}, want ${JSON.stringify(want[k])}`);
      t.expect(mv.v === 1 && Number.isInteger(mv.seq) && typeof mv.at === 'string', `the move's frame: ${JSON.stringify(mv)}`);
      await t.waitFor(() => page.locator('[data-wake-anchor] .status').innerText().then((s) => /the GM has been called/.test(s)), 'the status line says the GM was called');
      t.expect(await page.locator(`${keyed(`p-m${pad(mv.seq)}`)}`).count() === 1, 'the sent move shows as a bubble at the bottom');
      t.expect((await page.inputValue('#answer-text')) === '', 'the why line is cleared after the send');
      // the orders are with the GM: the form folds to a line, the now line and status say so
      await t.waitFor(() => page.locator('[data-row="sent"]').count(), 'the box: the orders are with the GM');
      t.expect(!(await page.locator('[data-row="travel"]').count()), 'the orders form is folded away');
      t.expect(/The GM's move/.test(await page.locator('[data-wake-anchor] .status').innerText()), 'the status line: the GM\'s move');
      t.expect(/the GM has your orders/.test(await page.locator('#now').innerText()), 'the now line: the GM has your orders');
      await page.reload();
      await page.waitForFunction(() => window.T && T.app.view() && T.app.view().ready);
      await t.waitFor(() => page.locator('[data-row="sent"]').count(), 'still with the GM after a reload');
      await page.locator('[data-act="revise"]').click();
      await t.waitFor(() => page.locator('[data-row="travel"]').count(), 'Change the orders brings the form back');
      await t.shot(page, 'phone-orders-sent');
    },
  },
  {
    name: 'story: before a fight, Morten\'s turn, while playing: the matching moves',
    async run(t) {
      const page = await t.open();
      await ready(page);
      const foe = { name: 'Giant Wolf Spider', cr: '1/4', ac: 13, hp: 11, maxHp: 11, speed: '8 sq (12 m)', attacks: ['Bite +5, 1d4+3 piercing'], count: 3 };
      await setState(t, { status: 'awaiting', awaiting: { kind: 'fight', prompt: 'Room 2.5: fight it?', orders: null, fight: { title: 'Room 2.5 · 3 Giant Wolf Spiders (CR 1/4 each)', foes: [foe], difficulty: 'Moderate', xp: 150 }, turn: null } });
      await t.waitFor(() => page.locator('[data-act="choice"][data-v="avoid"]').count(), 'the fight chips');
      t.expect((await page.locator('.box .foes').innerText()).includes('Giant Wolf Spider'), 'the foes in the box');
      await page.locator('[data-act="choice"][data-v="avoid"]').click();
      await page.locator('[data-act="send"]').click();
      await moveOf(t, 'fight', (d) => d.choice === 'avoid');
      // the call is with the GM: the box says so and offers to change it
      await t.waitFor(() => page.locator('[data-row="sent"]').count(), 'the box says the call is with the GM');
      t.expect(/The GM's move/.test(await page.locator('[data-wake-anchor] .status').innerText()), 'the status line: the GM\'s move');
      await page.locator('[data-act="revise"]').click();
      await t.waitFor(() => page.locator('[data-act="choice"][data-v="plan"]').count(), 'the fight chips again, to change the call');
      await page.locator('[data-act="choice"][data-v="plan"]').click();
      // the box re-renders on the next frame: wait for the plan's button before reading it
      await t.waitFor(() => page.locator('[data-act="send"]').innerText().then((x) => /plan/i.test(x)), 'the plan\'s send button');
      t.expect(await page.locator('[data-act="send"]').isDisabled(), 'a plan needs words');
      await page.fill('#answer-text', 'Web the doorway first.');
      await page.locator('[data-act="send"]').click();
      await moveOf(t, 'fight', (d) => d.choice === 'plan' && d.text === 'Web the doorway first.');
      await t.shot(page, 'phone-box-fight');

      await setState(t, { awaiting: { kind: 'turn', prompt: "Morten's turn, round 3", orders: null, fight: null, turn: { board: 'Positions: Morten C13 · Spider A C12 (1 sq)\nState: Morten 20/20 HP', lines: ['move 6 sq · action · bonus action · reaction ✓'], options: ['Fire Bolt', 'Sleep', 'Dagger'] } } });
      await t.waitFor(() => page.locator('[data-act="insert"][data-v="Fire Bolt"]').count(), 'the spell chips');
      t.expect((await page.locator('.board').innerText()).includes('Spider A C12'), 'the board');
      await page.locator('[data-act="insert"][data-v="Fire Bolt"]').click();
      await page.locator('#answer-text').pressSequentially('at Spider A');
      t.expect((await page.inputValue('#answer-text')) === 'Fire Bolt at Spider A', `the chip dropped its text in: "${await page.inputValue('#answer-text')}"`);
      await page.locator('[data-act="send"]').click();
      await moveOf(t, 'turn', (d) => d.text === 'Fire Bolt at Spider A');
      await t.shot(page, 'phone-box-turn');

      await setState(t, { status: 'playing', awaiting: { kind: 'none', prompt: '', orders: null, fight: null, turn: null } });
      await t.waitFor(() => page.locator('[data-act="stop"]').count(), 'the stop button while playing');
      await page.fill('#answer-text', 'leave the sleeping boar, go round');
      await page.locator('[data-act="stop"]').click();
      await moveOf(t, 'play', (d) => d.scope === 'stop' && d.text === 'leave the sleeping boar, go round');
      await page.locator('[data-act="take"]').click();
      await moveOf(t, 'take', (d) => d.who === 'you');

      await setState(t, { status: 'awaiting', awaiting: { kind: 'word', prompt: 'Your word', orders: null, fight: null, turn: null } });
      await t.waitFor(() => page.locator('[data-act="play"][data-scope="month"]').count(), 'the play row');
      await page.locator('[data-act="play"][data-scope="matters"]').click();
      await moveOf(t, 'play', (d) => d.scope === 'matters');
      await page.locator('[data-act="ooc"]').click();
      await page.fill('#answer-text', 'Does Shield stack with Mage Armor?');
      await page.locator('.send [data-act="say"]').click();
      await moveOf(t, 'say', (d) => d.ooc === true && d.text === 'Does Shield stack with Mage Armor?');
      const small = await page.evaluate(() => Array.from(document.querySelectorAll('#story button, #story .month')).filter((b) => b.getClientRects().length)
        .map((b) => ({ t: b.textContent.trim().slice(0, 30), h: Math.round(b.getBoundingClientRect().height) })).filter((r) => r.h < 44));
      t.expect(!small.length, `story tap targets under 44 px: ${JSON.stringify(small)}`);
      await noSideScroll(t, page, 'answer box');
    },
  },
  {
    name: 'story: the wake refused, and one "Call the GM again"',
    async run(t) {
      await setState(t, { wake: { on: true }, status: 'awaiting', awaiting: { kind: 'word', prompt: '', orders: null, fight: null, turn: null } });
      const page = await t.open({ query: 'cansend=no_session' });
      await ready(page);
      await page.fill('#answer-text', 'Anyone there?');
      await page.locator('.send [data-act="say"]').click();
      await t.waitFor(() => page.locator('[data-act="wake-again"]').count(), 'the call-again button');
      t.expect(/not watching/.test(await page.locator('[data-wake-anchor] .status').innerText()), 'the reason is said');
      t.expect(await page.locator('.wait i').count() === 1, 'the waiting bar shows while the move is unanswered');
      await page.locator('[data-act="wake-again"]').click();
      await page.waitForTimeout(300);
      t.expect((await t.api.wakes()).length === 0, 'no wake gets through, and none loops');
    },
  },
  {
    name: 'story: a beat grows the live card; its section replaces it in place, no jump',
    async run(t) {
      const page = await t.open();
      await ready(page);
      const st = await stateDoc(t);
      const seq = await nextSeq(t);
      const month = st.data.month || 1;
      const day = (st.data.day || 1) + 1;
      const foes = [{ name: 'Darkmantle', cr: '1/2', ac: 11, hp: 22, maxHp: 22, speed: '2 sq (3 m), fly 6 sq (9 m)', attacks: ['Crush +5, 1d6+3 bludgeoning'], count: 1 }];
      const section = { kind: 'fight', title: 'Room 9.1 · Darkmantle (CR 1/2)', month, day, where: 'Floor 9 · room 9.1', foes };
      const at = () => new Date().toISOString();
      const die = (f, mod, vs, result) => ({ expr: `1d20+${mod}`, faces: [f], kept: [f], mod, total: f + mod, vs, result, nat: null });
      await t.api.batch([
        { op: 'set', collection: 'live', doc_id: `b${pad(seq)}`, data: { v: 1, seq, section, round: 1, text: 'It drops from the ceiling and misses.', lines: [{ text: 'Crush: miss.', who: 'foe', kind: 'attack', round: 1, dice: [die(2, 5, 'AC 15', 'miss')] }], state: { morten: { hp: 20, maxHp: 20 }, foes: [{ name: 'Darkmantle', hp: 22, maxHp: 22 }] }, at: at() } },
        { op: 'update', collection: 'game', doc_id: 'state', if_version: st.version, data: { status: 'playing', lastSeq: seq, doing: 'rolling round 2', live: { kind: 'fight', title: section.title, month, day, openedAt: at() } } },
      ]);
      await t.waitFor(() => page.locator(keyed('live')).count(), 'the live card');
      const card = page.locator(keyed('live'));
      t.expect((await card.innerText()).includes('It drops from the ceiling'), 'the first beat\'s words');
      t.expect(await page.locator(keyed('activity')).innerText().then((s) => s.includes('rolling round 2')), 'the activity line');
      const lines1 = await card.locator('.ln').count();
      await card.scrollIntoViewIfNeeded();
      await t.shot(page, 'phone-live-1');
      await t.api.batch([
        { op: 'set', collection: 'live', doc_id: `b${pad(seq + 1)}`, data: { v: 1, seq: seq + 1, section, round: 2, text: 'Magic Missile holds: 9 force dmg, the Darkmantle is on 13/22 HP.', lines: [{ text: 'Magic Missile holds.', who: 'morten', kind: 'cast', round: 2, dice: [die(10, 5, 'DC 11', 'cast')] }], state: { morten: { hp: 20, maxHp: 20 }, foes: [{ name: 'Darkmantle', hp: 13, maxHp: 22 }] }, at: at() } },
      ]);
      await t.waitFor(async () => (await card.locator('.ln').count()) > lines1, 'the live card grows a line');
      t.expect((await card.innerText()).includes('13/22'), 'the foe\'s HP moved');
      // put the live card mid-screen, note where things are, settle the fight
      await page.evaluate(() => {
        const el = document.querySelector('#stream > [data-key="live"]');
        window.scrollBy(0, el.getBoundingClientRect().top - 300);
      });
      await page.waitForTimeout(150);
      const before = await page.evaluate(() => {
        const el = document.querySelector('#stream > [data-key="live"]');
        const prev = el.previousElementSibling;
        return { top: el.getBoundingClientRect().top, prevKey: prev.dataset.key, prevTop: prev.getBoundingClientRect().top, y: window.scrollY };
      });
      const st2 = await stateDoc(t);
      const sid = `s${pad(seq + 2)}`;
      await t.api.batch([
        { op: 'set', collection: 'story', doc_id: sid, data: { v: 1, seq: seq + 2, kind: 'fight', month, day, clock: '10:00', hex: st.data.hex || 'A5', where: section.where, title: `${section.title} · Moderate, 100 XP · cleared`, headline: 'Two Magic Missiles and it fell off the ceiling for good.', prose: [], bullets: [{ label: 'The dice', text: 'its crush rolled a 2.' }], trace: [{ text: 'Crush: miss.', who: 'foe', kind: 'attack', round: 1, dice: [die(2, 5, 'AC 15', 'miss')] }, { text: 'Magic Missile holds.', who: 'morten', kind: 'cast', round: 2, dice: [die(10, 5, 'DC 11', 'cast')] }], answered: [], after: { hp: 20, maxHp: 20, xp: 2225, coins: '7 SP', lost: [] }, fight: { foes, difficulty: 'Moderate', budget: 225, xp: 100, initiative: ['Darkmantle 21', 'Morten 17'], rounds: 2, outcome: 'cleared', verdict: 'clean', hpTrack: [{ name: 'Morten', max: 20, hp: [20, 20, 20] }, { name: 'Darkmantle', max: 22, hp: [22, 22, 0] }], loot: '+10 GP', lost: [], potion: false, xpBefore: 2125, xpAfter: 2225 }, words: [] } },
        { op: 'delete', collection: 'live', doc_id: `b${pad(seq)}`, if_version: 1 },
        { op: 'delete', collection: 'live', doc_id: `b${pad(seq + 1)}`, if_version: 1 },
        { op: 'update', collection: 'game', doc_id: 'state', if_version: st2.version, data: { status: 'awaiting', lastSeq: seq + 2, live: null, doing: '' } },
      ]);
      await t.waitFor(async () => (await page.locator(keyed(sid)).count()) === 1 && (await page.locator(keyed('live')).count()) === 0, 'the section in the live card\'s place');
      await page.waitForTimeout(150);
      const after = await page.evaluate(([sidIn, prevKey]) => {
        const el = document.querySelector(`#stream > [data-key="${sidIn}"]`);
        const prev = document.querySelector(`#stream > [data-key="${prevKey}"]`);
        return { top: el.getBoundingClientRect().top, prevTop: prev ? prev.getBoundingClientRect().top : null, y: window.scrollY, prevKeyNow: el.previousElementSibling.dataset.key };
      }, [sid, before.prevKey]);
      t.expect(after.prevKeyNow === before.prevKey, `the section sits where the live card was (after ${before.prevKey}, got ${after.prevKeyNow})`);
      t.expect(Math.abs(after.top - before.top) <= 2, `the section's top is where the live card's was: ${before.top} → ${after.top}`);
      t.expect(after.prevTop !== null && Math.abs(after.prevTop - before.prevTop) <= 2, `what is above did not move: ${before.prevTop} → ${after.prevTop}`);
      await t.shot(page, 'phone-live-settled');
    },
  },
  {
    name: 'story: the live button jumps to the live card and follows it',
    async run(t) {
      await seed(t, path.join(DEV, 'fixture-live'));
      const page = await t.open({ height: 700 });
      await ready(page);
      t.expect(await page.locator(keyed('live')).count() === 1, 'fixture-live has a live card');
      await page.evaluate(() => window.scrollTo(0, 0));
      await t.waitFor(() => page.locator('.jump[data-mode="live"]').isVisible(), 'the live button');
      await page.locator('.jump').click();
      await page.waitForTimeout(100);
      const r = await page.evaluate(() => { const b = document.querySelector('#stream > [data-key="live"]').getBoundingClientRect(); return { top: b.top, bottom: b.bottom, vh: innerHeight }; });
      t.expect(r.bottom <= r.vh && r.bottom > 0, `the live card is on screen after the jump: ${JSON.stringify(r)}`);
      await t.shot(page, 'phone-live-follow');
      const wide = await t.open({ width: 1280, height: 900 });
      await ready(wide);
      await noSideScroll(t, wide, 'wide live');
      await t.shot(wide, 'wide-live');
    },
  },
  {
    name: 'story: the reading position comes back after a reload',
    async run(t) {
      const page = await t.open();
      await ready(page);
      const keys = await page.locator('#stream > [data-key^="s"]').evaluateAll((els) => els.map((e) => e.dataset.key));
      t.expect(keys.length > 3, 'enough sections to scroll');
      const k = keys[Math.floor(keys.length / 2)];
      await page.evaluate((key) => { const el = document.querySelector(`#stream > [data-key="${key}"]`); window.scrollBy(0, el.getBoundingClientRect().top - 140); }, k);
      await page.waitForTimeout(500);
      await page.reload();
      await page.waitForFunction(() => window.T && T.app && T.app.view());
      await ready(page);
      await page.waitForTimeout(200);
      const top = await page.evaluate((key) => document.querySelector(`#stream > [data-key="${key}"]`).getBoundingClientRect().top, k);
      t.expect(Math.abs(top - 140) <= 3, `${k} is back at 140 px: ${top}`);
    },
  },
  {
    name: 'story: dev/sample, dev/fixture-live and an empty store render, light and dark, phone and wide',
    async run(t) {
      for (const [name, dir] of [['sample', path.join(DEV, 'sample')], ['fixture-live', path.join(DEV, 'fixture-live')], ['fixture', t.fixture]]) {
        await seed(t, dir);
        for (const [w, h, scheme] of [[412, 915, 'light'], [412, 915, 'dark'], [1280, 900, 'light'], [1280, 900, 'dark']]) {
          const page = await t.open({ width: w, height: h, colorScheme: scheme });
          await ready(page);
          t.expect(await page.locator('#stream > [data-key^="s"]').count() > 0, `${name}: sections render`);
          await noSideScroll(t, page, `${name} ${w}`);
          await t.shot(page, `story-${name}-${w}-${scheme}`);
          await page.context().close();
        }
      }
      await seed(t, null);
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      t.expect(await page.locator('#stream .empty').count() === 1 || await page.locator('#stream').innerText().then((s) => s.length < 400), 'an empty store says so calmly');
      await noSideScroll(t, page, 'empty');
      const noDb = await t.open({ query: 'nodb=1' });
      await noDb.waitForFunction(() => T.app.view() && T.app.view().db === 'none');
      t.expect((await noDb.locator('[data-a="closed"]').innerText()).includes('No table store'), 'no store: the box says why');
    },
  },
];
