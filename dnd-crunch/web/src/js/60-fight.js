// STUB, owned by Fights & Morten (README: File ownership). The real file holds
// T.panels.fightCard (the fight card the Story and the Fights tab share) and the Fights
// tab. This stand-in renders one line: how many fights the story holds. Replace it whole.
(() => {
  'use strict';
  const T = window.T;
  const { esc, fmt, put } = T.ui;
  let box = null;
  T.panels.fights = {
    mount(el) { box = el; },
    render(view) {
      const fights = view.sections.filter((s) => s.kind === 'fight');
      const going = view.state && view.state.live && view.state.live.kind === 'fight' ? ' · one going on' : '';
      put(box, `<p class="stub" data-stub="fights">Fights: ${esc(fmt.plural(fights.length, 'fight'))}${esc(going)}</p>`);
    },
  };
})();
