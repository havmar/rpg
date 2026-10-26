// The Realm tab's checks: the map, the hex entry, Codes, the realm rows, the tokens, a
// hostile realm's marks, and no sideways scroll at 412 px and in the 1280 px drawer.

async function realmDoc(t) {
  const d = await t.api.doc('game', 'realm');
  return d ? d.data : null;
}

async function openRealm(t, opts = {}) {
  const page = await t.open(opts);
  await page.waitForFunction(() => T.app.view() && T.app.view().ready);
  if ((opts.width || 412) < 900) await page.click('#tabs button[data-view="realm"]');
  await page.waitForSelector('#realm svg.map .hit[data-hex]');
  return page;
}

async function noSideScroll(t, page, where) {
  const w = await page.evaluate(() => {
    const d = document.getElementById('drawer');
    return { sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, dsw: d ? d.scrollWidth : 0, dcw: d ? d.clientWidth : 0 };
  });
  t.expect(w.sw <= w.cw, `${where}: page scrolls sideways (${w.sw} > ${w.cw})`);
  if (w.cw >= 900) t.expect(w.dsw <= w.dcw + 1, `${where}: the drawer scrolls sideways (${w.dsw} > ${w.dcw})`);
}

export const checks = [
  {
    name: 'realm: the map draws every hex and a token for every piece',
    async run(t) {
      const realm = await realmDoc(t);
      const page = await openRealm(t);
      const hexes = await page.locator('#realm svg.map .hit[data-hex]').count();
      t.expect(hexes === realm.hexes.length, `hexes drawn ${hexes}, in the doc ${realm.hexes.length}`);
      if (t.fixture.includes('fixture')) t.expect(hexes === 20, `the fixture has 20 hexes, drawn ${hexes}`);
      const pieces = realm.hexes.reduce((n, h) => n + Math.min((h.assets || []).length, 6), 0);
      const toks = await page.locator('#realm svg.map .tokn').count();
      t.expect(toks === pieces, `tokens drawn ${toks}, pieces ${pieces}`);
      // a hex's tap target is 44 px and more
      const bb = await page.locator('#realm svg.map .hit[data-hex]').first().boundingBox();
      t.expect(bb && bb.width >= 44 && bb.height >= 44, `hex target ${JSON.stringify(bb)}`);
      // the tower card: v2's regime and three attributes in words; v3's tier, Renown and Hold
      const tower = await page.locator('#realm .tower').innerText();
      if (realm.version === 3) {
        const tw = realm.factions.find((f) => f.tower);
        t.expect(tower.includes(tw.tierName) && new RegExp(`Renown ${tw.renown}\\b`).test(tower), `tower card names the tier and Renown: ${tower.slice(0, 200)}`);
        t.expect(new RegExp(`Hold ${tw.hold} of ${tw.maxHold}`).test(tower), `tower card gives Hold: ${tower.slice(0, 200)}`);
      } else {
        t.expect(/Regime \d+\/\d+/.test(tower), `tower card regime: ${tower.slice(0, 200)}`);
        t.expect(/Force/.test(tower) && /Cunning/.test(tower) && /Wealth/.test(tower), 'tower card names Force, Cunning, Wealth');
      }
      t.expect(/GP/.test(tower) && /a month/.test(tower), 'tower card gives gold and income');
      // badges for last month's moves, and Moves hides them
      const nev = realm.eventsWords.filter((e) => e.from || e.to).length;
      const badges = await page.locator('#realm svg.map .mv').count();
      t.expect(badges === nev, `move badges ${badges}, events with a hex ${nev}`);
      await page.click('#realm [data-t="moves"]');
      t.expect(await page.locator('#realm svg.map .mv').count() === 0, 'Moves off hides the badges');
      await page.click('#realm [data-t="moves"]');
      await t.shot(page, 'phone-realm');
      await noSideScroll(t, page, '412 px');
    },
  },
  {
    name: 'realm: tapping a hex opens its entry with days from Morten',
    async run(t) {
      const realm = await realmDoc(t);
      const page = await openRealm(t);
      const from = realm.morten.hex;
      const far = realm.hexes.find((h) => realm.days && realm.days[h.id] >= 2) || realm.hexes.find((h) => h.id !== from);
      await page.locator(`#realm svg.map .hit[data-hex="${far.id}"]`).click();
      await t.waitFor(() => page.evaluate((id) => document.querySelector('#realm .entry').dataset.hex === id, far.id), 'the entry for the tapped hex');
      const txt = await page.locator('#realm .entry').innerText();
      t.expect(txt.includes(`level ${far.level}`), `entry names the level: ${txt.slice(0, 160)}`);
      t.expect(/\d+ days? from Morten/.test(txt), `entry gives days from Morten: ${txt.slice(0, 300)}`);
      if (realm.days && typeof realm.days[far.id] === 'number') t.expect(txt.includes(`${realm.days[far.id]} day`), `entry's days match the doc (${realm.days[far.id]})`);
      t.expect(/The floor under it/i.test(txt), 'entry shows the floor under it');
      t.expect(/Next to/i.test(txt), 'entry lists the neighbours');
      // a neighbour button moves the entry
      const nb = page.locator('#realm .entry .hexbtn[data-hex]').first();
      const nid = await nb.getAttribute('data-hex');
      await nb.click();
      await t.waitFor(() => page.evaluate((id) => document.querySelector('#realm .entry').dataset.hex === id, nid), 'the neighbour opens');
      // Morten's own hex says he is there
      await page.locator(`#realm svg.map .hit[data-hex="${from}"]`).click();
      await t.waitFor(() => page.locator('#realm .entry').innerText().then((s) => s.includes('Morten is here')), 'Morten is here');
      // a hex with pieces shows piece rows with HP and what Morten can do
      const withPieces = realm.hexes.find((h) => (h.assets || []).some((a) => a.owner !== 'tower'));
      if (withPieces) {
        await page.locator(`#realm svg.map .hit[data-hex="${withPieces.id}"]`).click();
        await t.waitFor(() => page.evaluate((id) => document.querySelector('#realm .entry').dataset.hex === id, withPieces.id), 'the pieces hex');
        const rows = await page.locator('#realm .entry .piece').count();
        t.expect(rows === withPieces.assets.length, `piece rows ${rows} for ${withPieces.assets.length}`);
        const p = await page.locator('#realm .entry .piece').first().innerText();
        if (realm.version === 3) t.expect(/tier \d · a (Low|Moderate|High) fight/.test(p) && /Strike/.test(p), `site row: ${p}`);
        else t.expect(/\d+\/\d+ HP/.test(p) && /Strike/.test(p), `piece row: ${p}`);
        await t.shot(page, 'phone-realm-entry');
      }
    },
  },
  {
    name: 'realm: Codes shows the hex codes, off by default',
    async run(t) {
      const page = await openRealm(t);
      const vis = () => page.locator('#realm svg.map .hid').first().isVisible();
      t.expect(!(await vis()), 'codes hidden by default');
      await page.click('#realm [data-t="codes"]');
      await t.waitFor(vis, 'codes shown');
      t.expect((await page.getAttribute('#realm [data-t="codes"]', 'aria-pressed')) === 'true', 'Codes is pressed');
      await page.click('#realm [data-t="key"]');
      t.expect(await page.locator('#realm .keyover').isVisible(), 'the key shows over the map');
      await t.shot(page, 'phone-realm-codes-key');
      await page.click('#realm .keyover [data-t="key"]');
      t.expect(!(await page.locator('#realm .keyover').count()), 'the key closes');
      await page.click('#realm [data-t="codes"]');
      t.expect(!(await vis()), 'codes hidden again');
    },
  },
  {
    name: 'realm: the realm rows unfold, allies first',
    async run(t) {
      const realm = await realmDoc(t);
      const page = await openRealm(t);
      const names = await page.locator('#realm .rrow').evaluateAll((els) => els.map((e) => e.dataset.realm));
      const others = realm.factions.filter((f) => !f.tower);
      t.expect(names.length === others.length, `rows ${names.length} for ${others.length} realms`);
      const allies = others.filter((f) => f.ally).map((f) => f.name);
      t.expect(allies.every((a, i) => names[i] === a || allies.includes(names[i])), `allies first: ${names.join(', ')}`);
      const first = page.locator('#realm .rrow').first();
      t.expect((await first.getAttribute('data-open')) === 'false', 'rows start folded');
      await first.locator('.rhead').click();
      await t.waitFor(() => first.getAttribute('data-open').then((v) => v === 'true'), 'the row unfolds');
      const txt = await first.innerText();
      t.expect(/in the coffers/.test(txt) && /a month/.test(txt), `treasury and income: ${txt.slice(0, 300)}`);
      t.expect(await first.locator('.hexbtn').count() > 0, 'its hexes as buttons');
      // the tower card's ally link opens that row
      const link = page.locator('#realm .tower [data-goto-realm]').last();
      if (await link.count()) {
        const n = await link.getAttribute('data-goto-realm');
        await link.click();
        await t.waitFor(() => page.evaluate((nm) => [...document.querySelectorAll('#realm .rrow')].some((r) => r.dataset.realm === nm && r.dataset.open === 'true'), n), 'the linked row opens');
      }
      await t.shot(page, 'phone-realm-rows');
      await noSideScroll(t, page, '412 px, rows open');
    },
  },
  {
    name: 'realm: a hostile realm\'s tokens carry the red ring and skull',
    async run(t) {
      const realm = await realmDoc(t);
      const owner = realm.hexes.flatMap((h) => h.assets || []).map((a) => a.owner).find((o) => o && o !== 'tower');
      if (!owner) return;
      const v3 = realm.version === 3;
      const factions = realm.factions.map((f) => (f.name === owner ? (v3 ? { ...f, standing: -2, standingWord: 'enemy', ally: false } : { ...f, hostile: 2, ally: false }) : f));
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'realm', data: { factions } });
      const page = await openRealm(t, { colorScheme: 'dark' });
      await t.waitFor(() => page.locator('#realm svg.map .tokn.hos').count().then((n) => n > 0), 'hostile tokens');
      t.expect(await page.locator('#realm svg.map .tokn.hos .skull-g').count() > 0, 'a skull on a hostile token');
      const tower = await page.locator('#realm .tower').innerText();
      t.expect(tower.includes(owner), `the tower card names the hostile ${owner}`);
      const row = await page.locator(`#realm .rrow[data-realm="${owner}"]`).innerText();
      if (v3) t.expect(/enemy/i.test(row), `the row says enemy: ${row.slice(0, 200)}`);
      else t.expect(/hostile/i.test(row) && /2 months left/i.test(row), `the row says hostile: ${row.slice(0, 200)}`);
      await t.shot(page, 'phone-realm-hostile-dark');
    },
  },
  {
    name: 'realm: in the 1280 px drawer, no sideways scroll, entry opens',
    async run(t) {
      for (const colorScheme of ['light', 'dark']) {
        const page = await openRealm(t, { width: 1280, height: 900, colorScheme });
        t.expect(await page.locator('#realm svg.map').isVisible(), 'the map shows in the drawer');
        const bb = await page.locator('#realm svg.map').boundingBox();
        const dr = await page.locator('#drawer').boundingBox();
        t.expect(bb.x >= dr.x - 1 && bb.x + bb.width <= dr.x + dr.width + 1, `map inside the drawer ${JSON.stringify(bb)} ${JSON.stringify(dr)}`);
        const id = await page.locator('#realm svg.map .hit[data-hex]').nth(7).getAttribute('data-hex');
        await page.locator(`#realm svg.map .hit[data-hex="${id}"]`).click();
        await t.waitFor(() => page.evaluate((x) => document.querySelector('#realm .entry').dataset.hex === x, id), 'the entry in the drawer');
        await page.locator('#realm .rrow .rhead').first().click();
        await noSideScroll(t, page, `1280 px ${colorScheme}`);
        await t.shot(page, `wide-realm-${colorScheme}`);
      }
    },
  },
  {
    name: 'realm: "Travel here" in a hex entry picks the orders\' travel in the Story',
    async run(t) {
      const st = (await t.api.doc('game', 'state')).data;
      t.expect(st.awaiting && st.awaiting.kind === 'orders', 'the fixture awaits orders');
      const far = st.awaiting.orders.hexes.slice().sort((a, b) => b.days - a.days)[0];
      const page = await openRealm(t);
      await page.click(`#realm svg.map .hit[data-hex="${far.id}"]`);
      const btn = page.locator(`#realm [data-travel-here="${far.id}"]`);
      await t.waitFor(() => btn.count(), 'the Travel here button');
      t.expect(/Travel here/.test(await btn.innerText()), 'it says Travel here, with the days');
      const bb = await btn.boundingBox();
      t.expect(bb && bb.height >= 44, `a 44 px target: ${JSON.stringify(bb)}`);
      await t.shot(page, 'phone-realm-travel-here');
      await btn.click();
      await t.waitFor(() => page.evaluate(() => T.app.nav().view === 'story'), 'the Story opens');
      await t.waitFor(() => page.locator(`#story [data-f="travel"][data-v="${far.id}"][aria-pressed="true"]`).count(), `${far.id} picked in the orders form (even though it is far)`);
      // with no orders asked, the entry offers no travel
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { status: 'playing', awaiting: { kind: 'none', prompt: '', orders: null, fight: null, turn: null } } });
      await page.click('#tabs button[data-view="realm"]');
      await t.waitFor(() => page.evaluate(() => T.app.view().state.status === 'playing'), 'the state change');
      await page.waitForTimeout(100);
      t.expect(!(await page.locator('#realm [data-travel-here]').count()), 'no Travel here while the GM plays');
    },
  },
  {
    name: 'realm (v3): the tower card shows the tier, Hold boxes and the goal; a realm row shows its clock',
    async run(t) {
      const realm = await realmDoc(t);
      if (realm.version !== 3) {
        console.log('        (a v2 fixture; skipped)');
        return;
      }
      const tw = realm.factions.find((f) => f.tower);
      const page = await openRealm(t);
      const tower = page.locator('#realm .tower');
      t.expect(await tower.locator('.tierline').innerText().then((s) => s.includes(tw.tierName)), 'the tier name on the tower card');
      t.expect(await tower.locator('.hold i').count() === tw.maxHold, `${tw.maxHold} Hold boxes`);
      t.expect(await tower.locator('.hold i.on').count() === tw.hold, `${tw.hold} of them filled`);
      // every realm row shows ruler, Force, the standing word and its goal as a clock
      for (const f of realm.factions.filter((x) => !x.tower)) {
        const row = page.locator(`#realm .rrow[data-realm="${f.name}"]`);
        const txt = await row.innerText();
        t.expect(txt.includes(`${f.leader.label}: ${f.leader.verb}`), `${f.name}: label: verb`);
        t.expect(new RegExp(`Force ${f.force}\\b`).test(txt), `${f.name}: Force`);
        t.expect(new RegExp(f.standingWord, 'i').test(txt), `${f.name}: the standing word (shown in capitals)`);
        if (f.goal) {
          t.expect(txt.includes(f.goal.text), `${f.name}: the goal ${f.goal.text}`);
          t.expect(await row.locator('.clock i').count() === f.goal.size, `${f.name}: a clock of ${f.goal.size}`);
          t.expect(await row.locator('.clock i.on').count() === f.goal.marks, `${f.name}: ${f.goal.marks} marks`);
        }
      }
      // the tower's goal, once declared, is a clock on the tower card
      const take = realm.hexes.find((h) => h.holder && h.holder !== 'tower');
      const goal = { text: `take ${take.id} from the ${take.holder}`, kind: 'take', target: take.holder, hex: take.id, marks: 2, size: 5, waits: 0, since: 1 };
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'realm', data: { factions: realm.factions.map((f) => (f.tower ? { ...f, goal } : f)) } });
      await t.waitFor(() => tower.locator('.goal .clock').count(), "the tower's goal clock");
      t.expect(await tower.locator('.goal .clock i.on').count() === 2, '2 of 5 marks on it');
      t.expect(/Take .* from the/.test(await tower.innerText()), 'the goal in words');
      // the hex entry lists sites with their fight tier, and the clock aimed at the hex
      await page.locator(`#realm svg.map .hit[data-hex="${take.id}"]`).click();
      await t.waitFor(() => page.evaluate((id) => document.querySelector('#realm .entry').dataset.hex === id, take.id), 'the entry');
      const entry = await page.locator('#realm .entry').innerText();
      t.expect(/Sites here/i.test(entry), 'the entry heads its sites');
      t.expect(await page.locator('#realm .entry .piece.site').count() === take.assets.length, `${take.assets.length} site rows`);
      await t.shot(page, 'phone-realm-v3');
      await noSideScroll(t, page, '412 px, v3');
    },
  },
  {
    name: 'realm: no map doc renders a quiet card',
    async run(t) {
      await t.api.write({ op: 'delete', collection: 'game', doc_id: 'realm' });
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready);
      await page.click('#tabs button[data-view="realm"]');
      await t.waitFor(() => page.locator('#realm').innerText().then((s) => /No map/.test(s)), 'the no-map card');
    },
  },
];
