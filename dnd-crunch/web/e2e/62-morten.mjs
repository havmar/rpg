// The Morten tab (src/js/62-morten.js): HP, AC, spells and gear from the fixture, a lost
// spell struck through, a spell's line on a tap, no sideways scroll, both themes, 1280 px.

async function noSideScroll(t, page, where) {
  const w = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  t.expect(w.sw <= w.cw, `${where}: the page scrolls sideways (${w.sw} > ${w.cw} px)`);
}

async function openMorten(t, opts = {}) {
  const page = await t.open(opts);
  await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().loaded.morten);
  if ((opts.width || 412) >= 900) await page.click('#dtabs button[data-drawer="morten"]');
  else await page.click('#tabs button[data-view="morten"]');
  await page.locator('#morten .card').first().waitFor();
  return page;
}

export const checks = [
  {
    name: 'morten: the sheet shows HP, AC, spells and gear from the store',
    async run(t) {
      const m = (await t.api.doc('game', 'morten'))?.data;
      const st = (await t.api.doc('game', 'state'))?.data;
      const page = await openMorten(t);
      if (!m) {
        t.expect((await page.locator('#morten').innerText()).includes('No sheet yet'), 'the no-sheet note');
        return;
      }
      const hud = st && st.hud ? st.hud : m;
      const text = await page.locator('#morten').innerText();
      t.expect(text.includes(`${hud.hp} / ${hud.maxHp} HP`), `HP ${hud.hp} / ${hud.maxHp} HP`);
      const ac = await page.locator('#morten .mhud .stat').first().innerText();
      t.expect(ac.includes(String(hud.ac)) && ac.includes('AC'), `AC ${hud.ac}, got "${ac}"`);
      if (!hud.armorOn && typeof m.acArmor === 'number' && m.acArmor !== hud.ac) t.expect(ac.includes(`with Mage Armor ${m.acArmor}`), 'with Mage Armor');
      const spells = (m.spells || []).length;
      t.expect(await page.locator('#morten .spell').count() === spells, `${spells} spell chips`);
      const gear = (m.gear || []).length;
      t.expect(await page.locator('#morten .mgear .inv').first().locator('.nm').count() === gear, `${gear} gear rows`);
      if (m.load) t.expect(text.includes(`${m.load.kg} of ${m.load.max} kg`), 'the load in kg');
      if (typeof m.xp === 'number' && typeof m.nextXp === 'number') t.expect(text.includes(`${m.xp.toLocaleString('en-GB')} of ${m.nextXp.toLocaleString('en-GB')} XP`), 'the XP bar');
      // a tap shows the spell's one line
      const s = (m.spells || []).find((x) => x.line);
      if (s) {
        await page.locator(`#morten .spell[data-pick="spell:${s.name}"]`).click();
        await t.waitFor(() => page.locator('#morten .sline').innerText().then((x) => x.includes(s.line)).catch(() => false), 'the spell line');
      }
      await noSideScroll(t, page, 'morten');
      await t.shot(page, 'phone-morten');
    },
  },
  {
    name: 'morten: a lost spell is struck through, back after a Long Rest',
    async run(t) {
      const doc = await t.api.doc('game', 'morten');
      if (!doc || !(doc.data.spells || []).length) return;
      const spells = doc.data.spells.map((s, i) => (i === Math.min(6, doc.data.spells.length - 1) ? { ...s, lost: true } : s));
      const lost = spells.find((s) => s.lost);
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'morten', data: { spells } });
      const page = await openMorten(t);
      const chip = page.locator(`#morten .spell.lost[data-pick="spell:${lost.name}"]`);
      await chip.waitFor();
      const deco = await chip.locator('.nm').evaluate((e) => getComputedStyle(e).textDecorationLine);
      t.expect(deco.includes('line-through'), `struck through, got ${deco}`);
      t.expect((await chip.innerText()).includes('back after a Long Rest'), 'says when it comes back');
      await t.shot(page, 'phone-morten-lost');
    },
  },
  {
    name: 'morten: 1280 px and dark, no sideways scroll',
    async run(t) {
      for (const colorScheme of ['light', 'dark']) {
        const wide = await openMorten(t, { width: 1280, height: 900, colorScheme });
        await noSideScroll(t, wide, `morten 1280 px ${colorScheme}`);
        await t.shot(wide, `wide-morten-${colorScheme}`);
      }
      const phone = await openMorten(t, { colorScheme: 'dark' });
      await noSideScroll(t, phone, 'morten 412 px dark');
      await t.shot(phone, 'phone-morten-dark');
    },
  },
];
