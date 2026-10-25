// STUB, owned by the More panel (README: File ownership): Months, Rules, Talk and Table.
// Each stand-in renders one line. Replace this file whole.
(() => {
  'use strict';
  const T = window.T;
  const { esc, fmt, put } = T.ui;
  const one = (render) => {
    let box = null;
    return { mount(el) { box = el; }, render(view) { put(box, `<p class="stub">${render(view)}</p>`); } };
  };
  T.panels.months = one((v) => {
    const months = new Set(v.sections.map((s) => s.month).filter((m) => m !== null));
    return `Months: ${esc(fmt.plural(months.size, 'month'))}`;
  });
  T.panels.rules = one((v) => `Rules: ${esc(fmt.plural(v.rules ? v.rules.sections.length : 0, 'section'))}`);
  T.panels.talk = one((v) => `Talk: ${esc(fmt.plural(v.sections.filter((s) => s.kind === 'aside').length, 'aside'))}`);
  T.panels.table = one((v) => {
    const t = v.state && v.state.table;
    return t ? `Table: ${esc(t.mode)} · ${t.who === 'dm' ? 'the GM moves Morten' : 'you move Morten'} · stops at ${esc(t.stop)}` : 'Table: no dials yet';
  });
})();
