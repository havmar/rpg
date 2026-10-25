// STUB, owned by Fights & Morten (README: File ownership): the Morten tab, the sheet from
// game/morten. This stand-in renders one line. Replace it whole.
(() => {
  'use strict';
  const T = window.T;
  const { esc, fmt, put } = T.ui;
  let box = null;
  T.panels.morten = {
    mount(el) { box = el; },
    render(view) {
      const m = view.morten;
      put(box, `<p class="stub" data-stub="morten">${m
        ? `Morten: ${esc(m.class || m.name)} · ${esc(fmt.hp(m.hp, m.maxHp))} · ${esc(fmt.plural(m.spells.length, 'spell'))} · ${esc(fmt.plural(m.gear.length, 'gear row'))}`
        : 'Morten: no sheet yet'}</p>`);
    },
  };
})();
