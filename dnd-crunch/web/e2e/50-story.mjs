// The Story's checks. STUB: these test the stand-in answer box in src/js/50-story.js; the
// Story's owner replaces this file with checks of the real Story.
export const checks = [
  {
    name: 'story (stub): the answer box sends a say move and shows the GM was called',
    async run(t) {
      await t.api.write({ op: 'update', collection: 'game', doc_id: 'state', data: { wake: { on: true } } });
      const page = await t.open();
      await page.waitForFunction(() => T.app.view() && T.app.view().ready && T.app.view().comments === 'ok');
      await page.fill('#answer-text', 'Morten checks the ceiling first.');
      await page.click('#answer-send');
      await t.waitFor(async () => (await t.api.docs('moves')).some((d) => d.data.kind === 'say' && d.data.text === 'Morten checks the ceiling first.'), 'the say move in the store');
      await t.waitFor(() => page.locator('[data-wake-anchor] .status').innerText().then((s) => s.includes('the GM has been called')), 'the status line');
      t.expect((await page.inputValue('#answer-text')) === '', 'the box is cleared after the send');
      await t.shot(page, 'phone-story-sent');
    },
  },
];
