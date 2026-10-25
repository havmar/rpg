// STUB, owned by the Story panel (README: File ownership). It stands in until the Story is
// built: a one-line summary of what the Story will show, the newest live beat, and a
// minimal answer box (a text box and Send, as one `say` move) with its status line, so
// the shell's send and wake can be tried end to end. Replace this file whole.
(() => {
  'use strict';
  const T = window.T;
  const ui = T.ui;
  const { esc, fmt } = ui;
  let els = null;

  function status(view) {
    const st = view.state;
    const failed = view.pending.find((p) => p.status === 'failed');
    if (failed) return `<span class="bad">${esc(failed.id)} was not sent: ${esc(failed.error)}</span><button type="button" data-retry="${esc(failed.id)}">Send again</button>`;
    const sending = view.pending.find((p) => p.status === 'sending');
    if (sending) return `<span>Sending ${esc(sending.id)}…</span>`;
    const w = view.wake;
    if (w.move) {
      const when = w.at ? ` · ${esc(ui.ago(w.at, view.now))}` : '';
      if (w.state === 'calling') return `<span>Sent ${esc(w.move)}</span><span class="sep">·</span><span>calling the GM…</span>`;
      if (w.state === 'called') return `<span>Sent ${esc(w.move)}</span><span class="sep">·</span><span>the GM has been called${when}</span>`;
      if (w.state === 'off') return `<span>Sent ${esc(w.move)}</span><span class="sep">·</span><span>the GM reads it at the next stop</span>`;
      if (w.state === 'unavailable' || w.state === 'failed') return `<span>Sent ${esc(w.move)}</span><span class="sep">·</span><span>${esc(w.reason)}</span><button type="button" data-wake-again>Call the GM again</button>`;
    }
    if (!st) return '<span>The answer box opens when the table does.</span>';
    if (st.status === 'playing') return '<span>The GM is playing</span>';
    return `<span>Your move</span>${st.awaiting.prompt ? `<span class="sep">·</span><span>${esc(st.awaiting.prompt)}</span>` : ''}`;
  }

  T.panels.story = {
    mount(el) {
      el.innerHTML = '<p class="stub" data-stub="story"></p><p class="stub" data-stub="beat"></p>'
        + '<section class="answer" data-wake-anchor aria-label="Your word"><p class="status" data-stub="status"></p>'
        + '<div class="box"><label class="vh" for="answer-text">Your word to the GM</label><textarea id="answer-text" rows="2" placeholder="Morten\'s words, or a question for the GM"></textarea>'
        + '<div class="send"><span class="hint">sent as a say move</span><button type="button" id="answer-send">Send</button></div></div></section>';
      els = {
        sum: el.querySelector('[data-stub="story"]'),
        beat: el.querySelector('[data-stub="beat"]'),
        status: el.querySelector('[data-stub="status"]'),
        text: el.querySelector('#answer-text'),
        send: el.querySelector('#answer-send'),
      };
      els.send.addEventListener('click', () => {
        const text = els.text.value.trim();
        if (!text) return;
        T.store.send('say', { text, ooc: false }).then(() => { els.text.value = ''; }, () => {});
      });
      el.addEventListener('click', (ev) => {
        if (ev.target.closest('[data-wake-again]')) T.store.wakeAgain();
        const r = ev.target.closest('[data-retry]');
        if (r) T.store.retry(r.getAttribute('data-retry'));
      });
    },
    render(view) {
      if (!els) return;
      const months = new Set(view.sections.map((s) => s.month).filter((m) => m !== null));
      const newest = view.sections[view.sections.length - 1];
      ui.put(els.sum, `Story: ${esc(fmt.plural(view.sections.length, 'section'))} in ${esc(fmt.plural(months.size, 'month'))}`
        + ` · ${esc(fmt.plural(view.beats.length, 'beat'))} live · ${esc(fmt.plural(view.moves.length, 'move'))} waiting`
        + (newest ? ` · newest: ${esc(newest.title || newest.kind)}` : ''));
      const b = view.beats[view.beats.length - 1];
      ui.put(els.beat, b ? `Live: ${esc(b.text)} ${ui.dice(b.lines.flatMap((l) => l.dice))}` : '');
      ui.put(els.status, status(view));
      const busy = view.sending || !view.canWrite;
      els.send.disabled = busy;
    },
    tick(view) {
      if (els) ui.put(els.status, status(view));
    },
  };
})();
