// The Fights tab and the fight card (src/js/60-fight.js): the rows, a row opening its
// card, the HP track (one line per combatant), folds kept across re-renders, a live fight
// from beats, and no sideways scroll at 412 px and 1280 px in both themes.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

async function noSideScroll(t, page, where) {
  const w = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  t.expect(w.sw <= w.cw, `${where}: the page scrolls sideways (${w.sw} > ${w.cw} px)`);
}

async function fightDocs(t) {
  const docs = await t.api.docs('story');
  return docs.filter((d) => d.data && (d.data.kind === 'fight' || d.data.fight)).sort((a, b) => b.data.seq - a.data.seq);
}

async function openFights(t, opts = {}) {
  const page = await t.open(opts);
  await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().loaded.story);
  if ((opts.width || 412) >= 900) await page.click('#dtabs button[data-drawer="fights"]');
  else await page.click('#tabs button[data-view="fights"]');
  await page.locator('#fights .card.fights').waitFor();
  return page;
}

/** Two beats of a live fight: from dev/fixture-live when it has them, else made here. */
function liveBeats() {
  const dir = path.join(WEB, 'dev', 'fixture-live', 'live');
  if (fs.existsSync(dir)) {
    const files = fs.readdirSync(dir).filter((f) => /^b\d+\.json$/.test(f)).sort();
    const beats = files.map((f) => ({ id: f.replace(/\.json$/, ''), data: JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')) }));
    if (beats.length >= 2) return beats.slice(0, 2);
  }
  const foe = { name: 'Darkmantle', cr: '1/2', ac: 11, hp: 22, maxHp: 22, speed: '2 sq (3 m), fly 6 sq (9 m)', attacks: ['Crush +5, 1d6+3 bludgeoning'], notes: '', count: 1 };
  const section = { kind: 'fight', title: 'Room 2.4 · Darkmantle (CR 1/2)', month: 2, day: 4, where: 'Floor 2 · room 2.4', foes: [foe] };
  const mk = (seq, round, mh, fh, text) => ({ id: `b${String(seq).padStart(4, '0')}`, data: { v: 1, seq, section, round, text, lines: [{ text, who: 'morten', kind: 'cast', round, dice: [] }], state: { morten: { hp: mh, maxHp: 20 }, foes: [{ name: 'Darkmantle', hp: fh, maxHp: 22 }] }, at: new Date().toISOString() } });
  return [mk(900, 1, 20, 13, 'Magic Missile for 9 dmg.'), mk(901, 2, 14, 13, 'Crush hits Morten for 6 dmg.')];
}

export const checks = [
  {
    name: 'fights: every fight is a row, newest first, with the right count',
    async run(t) {
      const fights = await fightDocs(t);
      const page = await openFights(t);
      const rows = page.locator('#fights .frow');
      await t.waitFor(async () => (await rows.count()) === fights.length, `${fights.length} rows`);
      if (fights.length) {
        const sub = await page.locator('#fights .card.fights > h3 small').innerText();
        t.expect(sub.includes(`${fights.length} fight`), `the count in the heading, got "${sub}"`);
        const first = await page.locator('#fights .frow').first().getAttribute('data-frow');
        t.expect(first === fights[0].doc_id, `the newest fight first (${fights[0].doc_id}), got ${first}`);
        const months = [...new Set(fights.map((d) => d.data.month))];
        if (months.length > 1) t.expect(await page.locator('#fights [data-fmonth]').count() === months.length + 1, 'a month filter: all and each month');
      } else {
        t.expect(await page.locator('#fights .empty').isVisible(), 'the empty note');
      }
      await noSideScroll(t, page, 'fights');
      await t.shot(page, 'phone-fights');
    },
  },
  {
    name: 'fights: a row opens its card; the HP track has one line per combatant; folds survive a re-render',
    async run(t) {
      const fights = await fightDocs(t);
      const withTrack = fights.find((d) => d.data.fight && Array.isArray(d.data.fight.hpTrack) && d.data.fight.hpTrack.length > 1) || fights[0];
      if (!withTrack) return;
      const page = await openFights(t);
      await page.click(`#fights .frow[data-frow="${withTrack.doc_id}"]`);
      const card = page.locator(`#fights .fcard[data-fight="fights:${withTrack.doc_id}"]`);
      await card.waitFor();
      t.expect(await card.locator('.sec-head h3').isVisible(), 'the card has its head');
      const track = (withTrack.data.fight && withTrack.data.fight.hpTrack) || [];
      if (track.length) {
        const lines = await card.locator('figure.track > svg path.ln').count();
        t.expect(lines === track.length, `the HP track draws ${track.length} lines, got ${lines}`);
        const labels = await card.locator('figure.track > svg text.end').count();
        t.expect(labels === track.length, 'each line named at its end');
        // the numbers, one tap away
        await card.locator('details.numbers > summary').click();
        t.expect(await card.locator('details.numbers table').isVisible(), 'the HP numbers open');
      }
      // the rounds fold, then a re-render (a log line lands): the fold stays open
      if ((withTrack.data.trace || []).length) {
        await card.locator('details.trace > summary').click();
        t.expect(await card.locator('details.trace .round').first().isVisible(), 'the rounds open');
        const chips = await card.locator('details.trace .die').count();
        t.expect(chips > 0, 'the dice are chips');
        await t.api.batch([{ op: 'set', collection: 'log', doc_id: 'l0990', data: { v: 1, seq: 990, text: 'rolling', at: new Date().toISOString() } }]);
        await t.waitFor(() => page.evaluate(() => T.app.view().logs.some((l) => l.id === 'l0990')), 'the log line');
        await page.waitForTimeout(100);
        t.expect(await card.locator('details.trace').evaluate((d) => d.open), 'the rounds stay open after a re-render');
      }
      await noSideScroll(t, page, 'fight card');
      await t.shot(page, 'phone-fight-card');
      // the same card closes again
      await page.click(`#fights .frow[data-frow="${withTrack.doc_id}"]`);
      await t.waitFor(async () => (await page.locator('#fights .fcard').count()) === 0, 'the card closes');
    },
  },
  {
    name: 'fights: a live fight shows at the top, its HP bars moving as beats land',
    async run(t) {
      const [b1, b2] = liveBeats();
      const sec = b1.data.section;
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { live: { kind: 'fight', title: sec.title, month: sec.month, day: sec.day, openedAt: new Date().toISOString() } } });
      await t.api.batch([{ op: 'set', collection: 'live', doc_id: b1.id, data: b1.data }]);
      const page = await openFights(t);
      const row = page.locator('#fights .frow[data-frow="live"]');
      await row.waitFor();
      t.expect((await row.innerText()).includes('going on'), 'the live row says going on');
      await row.click();
      const card = page.locator('#fights .fcard.live');
      await card.waitFor();
      const bars = card.locator('.hprow .hp');
      const want = 1 + (b1.data.state.foes || []).length;
      t.expect(await bars.count() === want, `${want} HP bars`);
      await t.api.batch([{ op: 'set', collection: 'live', doc_id: b2.id, data: b2.data }]);
      const m2 = b2.data.state.morten;
      await t.waitFor(() => card.locator('.hprow .hp.me b').innerText().then((s) => s.includes(`${m2.hp}/${m2.maxHp} HP`)), `Morten's bar at ${m2.hp}/${m2.maxHp} HP`);
      await t.waitFor(async () => (await card.locator('.round h5').count()) >= 2, 'the second round appended');
      t.expect(await card.locator('.story').count() === 0, 'no story while live');
      await noSideScroll(t, page, 'live fight');
      await t.shot(page, 'phone-fight-live');
    },
  },
  {
    name: 'fights: the card at 1280 px and in the dark, no sideways scroll',
    async run(t) {
      const fights = await fightDocs(t);
      for (const colorScheme of ['light', 'dark']) {
        const page = await openFights(t, { width: 1280, height: 900, colorScheme });
        if (fights[0]) {
          const pick = fights.find((d) => d.data.fight && (d.data.fight.hpTrack || []).length > 2) || fights[0];
          await page.click(`#fights .frow[data-frow="${pick.doc_id}"]`);
          await page.locator('#fights .fcard').waitFor();
          await page.locator('#fights details.trace > summary').click().catch(() => {});
        }
        await noSideScroll(t, page, `fights at 1280 px, ${colorScheme}`);
        await t.shot(page, `wide-fights-${colorScheme}`);
        const phone = await openFights(t, { colorScheme });
        if (fights[0]) {
          const pick = fights.find((d) => d.data.fight && (d.data.fight.hpTrack || []).length > 2) || fights[0];
          await phone.click(`#fights .frow[data-frow="${pick.doc_id}"]`);
          await phone.locator('#fights .fcard').waitFor();
        }
        await noSideScroll(t, phone, `fights at 412 px, ${colorScheme}`);
        await t.shot(phone, `phone-fights-card-${colorScheme}`);
      }
    },
  },
  {
    name: 'fight card: renders a bare section, a closed-table foe and an empty one without throwing',
    async run(t) {
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      const out = await page.evaluate(() => {
        const a = T.panels.fightCard.html({}, {});
        const b = T.panels.fightCard.html({ id: 's9', title: 'Room 9 · Ogre (CR 2)', fight: T.model.parse.fight({ foes: [{ name: 'Ogre', cr: '2', ac: 11, hp: null, state: 'bloodied' }], outcome: 'fled', hpTrack: [{ name: 'Morten', max: 20, hp: [20, null, 12] }, { name: 'Ogre', max: null, hp: [null, null] }] }) }, { live: false });
        const c = T.panels.fightCard.html({ title: 'x' }, { live: true, beats: [] });
        return { a: a.length > 0, b: b.includes('Bloodied') && b.includes('fled'), c: c.includes('in progress') };
      });
      t.expect(out.a && out.b && out.c, `bare cards render: ${JSON.stringify(out)}`);
    },
  },
];
