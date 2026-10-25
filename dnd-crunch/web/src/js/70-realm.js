// STUB, owned by the Realm panel (README: File ownership): the tower card, the map, the
// hex entry and the realm rows, from game/realm. This stand-in renders one line. Replace it whole.
(() => {
  'use strict';
  const T = window.T;
  const { esc, fmt, put } = T.ui;
  let box = null;
  T.panels.realm = {
    mount(el) { box = el; },
    render(view) {
      const r = view.realm;
      put(box, `<p class="stub" data-stub="realm">${r
        ? `Realm: ${esc(fmt.plural(r.hexes.length, 'hex', 'hexes'))} · ${esc(fmt.plural(r.factions.length, 'realm'))} · ${esc(fmt.plural(r.events.length, 'event'))} last month`
        : 'Realm: no map yet'}</p>`);
    },
  };
})();
