// T.app: the shell. The views and the bottom bar (phone), the drawer and its tabs (from
// 900 px), More's chips, the theme switch, the now line and the HUD, the store notice,
// and render scheduling: at most once per animation frame, every T.panels.<name> that
// has a container is mounted once and rendered with the view model.
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;
  const ui = T.ui;
  const { esc, icon, fmt } = ui;

  /** Panels the shell mounts: T.panels[name] renders into the element with id=name. */
  const CONTAINERS = ['story', 'morten', 'realm', 'fights', 'months', 'rules', 'talk', 'table'];
  const VIEWS = ['story', 'morten', 'realm', 'fights', 'more'];
  const MORE = ['months', 'rules', 'talk', 'table'];
  const DRAWER = ['realm', 'morten', 'fights', 'months', 'rules', 'talk', 'table'];
  const TICK_MS = 20000;

  const nav = { view: 'story', more: 'months', drawer: 'realm' };
  const scrolls = {};
  const mounted = new Map();
  let current = null;
  let raf = 0;
  let timer = 0;
  let booted = false;
  const el = (id) => document.getElementById(id);
  const isWide = () => window.matchMedia('(min-width: 900px)').matches;

  // ---------- navigation ----------
  function saveNav() {
    ui.local.set('nav', nav);
  }

  function applyNav() {
    const app = el('app');
    if (!app) return;
    app.dataset.view = nav.view;
    app.dataset.more = nav.more;
    app.dataset.drawer = nav.drawer;
    for (const b of U.$$('#tabs button[data-view]')) b.setAttribute('aria-current', String(b.dataset.view === nav.view));
    for (const b of U.$$('#more-tabs button[data-more]')) b.setAttribute('aria-pressed', String(b.dataset.more === nav.more));
    for (const b of U.$$('#dtabs button[data-drawer]')) b.setAttribute('aria-pressed', String(b.dataset.drawer === nav.drawer));
  }

  function setView(v) {
    if (!VIEWS.includes(v)) return;
    const was = nav.view;
    if (was === v) {
      if (!isWide()) window.scrollTo({ top: 0 });
      return;
    }
    scrolls[was] = window.scrollY;
    nav.view = v;
    if (DRAWER.includes(v)) nav.drawer = v;
    if (v === 'more') nav.drawer = nav.more;
    applyNav();
    saveNav();
    if (!isWide()) window.scrollTo({ top: scrolls[v] || 0 });
    schedule();
  }

  function setMore(m) {
    if (!MORE.includes(m)) return;
    nav.more = m;
    nav.drawer = m;
    applyNav();
    saveNav();
    schedule();
  }

  function setDrawer(d) {
    if (!DRAWER.includes(d)) return;
    nav.drawer = d;
    if (MORE.includes(d)) {
      nav.more = d;
      nav.view = 'more';
    } else nav.view = d;
    applyNav();
    saveNav();
    const dr = el('drawer');
    if (dr && isWide()) dr.scrollTop = 0;
    schedule();
  }

  /** Open a place on the page: a view (story, morten, realm, fights, more) or a drawer tab (months, rules, talk, table). */
  function go(name) {
    if (name === 'story') {
      setView('story');
      return;
    }
    if (MORE.includes(name)) {
      nav.more = name;
      setView('more');
      setMore(name);
      return;
    }
    if (DRAWER.includes(name)) {
      setView(name);
      setDrawer(name);
      return;
    }
    if (name === 'more') setView('more');
  }

  function fromHash() {
    const h = (window.location.hash || '').replace(/^#/, '');
    if (VIEWS.includes(h) || MORE.includes(h)) go(h);
  }

  // ---------- theme ----------
  function effectiveDark() {
    const t = document.documentElement.dataset.theme;
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function themeButtons() {
    const dark = effectiveDark();
    for (const b of U.$$('[data-theme-switch]')) {
      b.innerHTML = `${icon(dark ? 'sun' : 'moon')}<span>${dark ? 'Light' : 'Dark'}</span>`;
      b.setAttribute('aria-label', dark ? 'Switch to the light theme' : 'Switch to the dark theme');
    }
  }

  /** setTheme('dark' | 'light' | null); null follows the system. Remembered per viewer. */
  function setTheme(t) {
    const root = document.documentElement;
    if (t === 'dark' || t === 'light') {
      root.dataset.theme = t;
      ui.local.set('theme', t);
    } else {
      delete root.dataset.theme;
      ui.local.del('theme');
    }
    themeButtons();
  }

  // ---------- the now line ----------
  function renderNow(view) {
    const where = el('now-where');
    if (!where) return;
    const st = view.state;
    let html;
    if (!st) {
      const why = view.db === 'none' ? 'no table store in this view'
        : view.db === 'error' ? 'the table stopped updating'
          : view.opening ? 'opening the table…' : 'the GM has not set the table yet';
      html = `<b>Morten's table</b><span class="place">${esc(why)}</span>`;
    } else {
      const when = fmt.when(st) || (st.campaign ? st.campaign : "Morten's table");
      html = `<b>${esc(when)}</b>${st.where ? `<span class="place">${esc(st.where)}</span>` : st.hex ? `<span class="place">${esc(st.hex)}</span>` : ''}`;
      const since = view.lastBeatAt ? ui.ago(view.lastBeatAt, view.now) : '';
      if (st.status === 'playing') {
        html += `<span class="doing" data-now="doing"><i class="pulse" aria-hidden="true"></i><span>the GM: ${esc(view.activity || 'playing')}</span>${since ? `<span class="ago">· ${esc(since)}</span>` : ''}</span>`;
      } else if (st.status === 'ended') {
        html += '<span class="doing ended" data-now="doing">the campaign has ended</span>';
      } else if (T.panels.story && typeof T.panels.story.withGm === 'function' && T.panels.story.withGm(view)) {
        const w = T.panels.story.withGm(view);
        html += `<span class="doing" data-now="doing"><i class="pulse" aria-hidden="true"></i><span>the GM has your ${w.kind === 'orders' ? 'orders' : 'move'}</span></span>`;
      } else {
        const p = st.awaiting.prompt;
        html += `<span class="doing yours" data-now="doing">${icon('hand')}<span>your move${p ? `: ${esc(p)}` : ''}</span>${since ? `<span class="ago">· last beat ${esc(since)}</span>` : ''}</span>`;
      }
    }
    ui.put(where, html);
    renderHud(view);
  }

  function renderHud(view) {
    const hudEl = el('hud');
    if (!hudEl) return;
    const st = view.state;
    const h = st && st.hud;
    if (!h || !h.known) {
      ui.put(hudEl, '');
      return;
    }
    const parts = [];
    if (h.hp !== null || h.maxHp !== null) parts.push(`<span>${icon('heart', 'bad')}${ui.bar(h.hp, h.maxHp)}<b>${esc(fmt.hp(h.hp, h.maxHp))}</b></span>`);
    // hud.ac is the AC now; armorOn says Mage Armor holds (acArmor is the AC with it).
    const armor = h.armorOn === true || (h.armorOn === null && h.acArmor !== null && h.acArmor === h.ac);
    if (h.ac !== null) {
      const tip = h.acArmor !== null && !armor ? ` title="${esc(`${h.acArmor} with Mage Armor`)}"` : '';
      parts.push(`<span${tip}>${icon('shield')}<b>AC ${esc(h.ac)}</b>${armor ? ' Mage Armor' : ''}</span>`);
    }
    if (h.light) parts.push(`<span>${icon('lantern')}${esc(h.light)}</span>`);
    if (h.conc) parts.push(`<span>${icon('eye')}conc <b>${esc(h.conc)}</b></span>`);
    parts.push(`<span>${icon('spark')}lost <b>${esc(h.lost.length ? h.lost.join(', ') : 'none')}</b></span>`);
    if (h.conditions.length) parts.push(`<span class="warn">${esc(h.conditions.join(', '))}</span>`);
    if (h.exhaustion > 0) parts.push(`<span class="bad">exhaustion <b>${esc(h.exhaustion)}</b></span>`);
    const inFight = (st.live && st.live.kind === 'fight') || st.awaiting.kind === 'turn';
    if (inFight && h.reaction !== null) parts.push(`<span class="${h.reaction ? '' : 'spent'}">reaction ${h.reaction ? '✓' : '✗'}</span>`);
    if (h.inspiration !== null) parts.push(`<span class="${h.inspiration ? 'lit' : 'spent'}" title="Heroic Inspiration ${h.inspiration ? 'ready' : 'spent'}">${icon('d20')}insp</span>`);
    if (h.freeArmor !== null) parts.push(`<span class="${h.freeArmor ? 'lit' : 'spent'}" title="The free Mage Armor ${h.freeArmor ? 'ready' : 'used today'}">${icon('shield')}free armor</span>`);
    if (h.coins) parts.push(`<span title="coins on him (lost if he dies)">${icon('coins')}<b>${esc(h.coins)}</b></span>`);
    ui.put(hudEl, parts.join(''));
  }

  // ---------- the store notice ----------
  function renderNotice(view) {
    const n = el('notice');
    if (!n) return;
    let html = '';
    let err = false;
    if (view.db === 'none') {
      html = `${icon('off')}<span><b>No table store in this view.</b> The game shows here when the page is opened as the table on claude.ai, where the GM writes to it.</span>`;
    } else if (view.db === 'error') {
      err = true;
      html = `${icon('off')}<span><b>The table stopped updating:</b> ${esc(view.dbError || 'the store stopped answering')}. Reload the page to reconnect.</span>`;
    } else if (view.ready && !view.state) {
      html = `${icon('q')}<span><b>The table is empty.</b> The GM sets it up from the campaign (table.py new); the game appears here as soon as it does.</span>`;
    } else if (view.ready && view.canWrite === false) {
      html = `${icon('eye')}<span><b>You are watching this table.</b> You can read everything; playing needs edit access.</span>`;
    }
    n.classList.toggle('err', err);
    n.hidden = !html;
    ui.put(n, html);
  }

  // ---------- panels ----------
  function failCard(name, err) {
    return `<div class="panel-error">This part of the page failed (${esc(name)}): ${esc(U.errText(err))}</div>`;
  }

  function mountPanels() {
    for (const name of CONTAINERS) {
      const p = T.panels[name];
      const box = el(name);
      if (!p || !box || mounted.get(name) === p) continue;
      try {
        if (typeof p.mount === 'function') p.mount(box);
        mounted.set(name, p);
      } catch (err) {
        console.error(`[table] mounting ${name} failed:`, err);
        mounted.set(name, null);
        box.innerHTML = failCard(name, err);
      }
    }
  }

  function renderPanels(view) {
    for (const [name, p] of mounted) {
      if (!p || typeof p.render !== 'function') continue;
      try {
        p.render(view);
      } catch (err) {
        console.error(`[table] rendering ${name} failed:`, err);
      }
    }
  }

  // ---------- rendering, at most once a frame ----------
  function flush() {
    if (raf) cancelAnimationFrame(raf);
    if (timer) clearTimeout(timer);
    raf = 0;
    timer = 0;
    const view = U.safe(() => T.model.view(T.store.raw()), 'view model');
    if (!view) return;
    current = view;
    U.safe(() => renderNow(view), 'now line');
    U.safe(() => renderNotice(view), 'notice');
    mountPanels();
    renderPanels(view);
  }

  /** Ask for a render; many asks in one frame give one render. */
  function schedule() {
    if (!booted || raf || timer) return;
    raf = requestAnimationFrame(flush);
    timer = setTimeout(flush, 250); // a hidden or throttled frame still renders
  }

  function tick() {
    if (!current) return;
    const view = Object.assign({}, current, { now: Date.now() });
    current = view;
    U.safe(() => renderNow(view), 'now line');
    for (const [name, p] of mounted) {
      if (p && typeof p.tick === 'function') U.safe(() => p.tick(view), `${name} tick`);
    }
  }

  // ---------- boot ----------
  function wire() {
    const tabs = el('tabs');
    if (tabs) tabs.addEventListener('click', (ev) => {
      const b = ev.target.closest('button[data-view]');
      if (b) setView(b.dataset.view);
    });
    const more = el('more-tabs');
    if (more) more.addEventListener('click', (ev) => {
      const b = ev.target.closest('button[data-more]');
      if (b) setMore(b.dataset.more);
    });
    const dt = el('dtabs');
    if (dt) dt.addEventListener('click', (ev) => {
      const b = ev.target.closest('button[data-drawer]');
      if (b) setDrawer(b.dataset.drawer);
    });
    document.addEventListener('click', (ev) => {
      if (ev.target.closest('[data-theme-switch]')) setTheme(effectiveDark() ? 'light' : 'dark');
    });
    window.addEventListener('hashchange', fromHash);
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) mq.addEventListener('change', themeButtons);
    const wq = window.matchMedia('(min-width: 900px)');
    if (wq.addEventListener) wq.addEventListener('change', schedule);
    const now = el('now');
    if (now && 'ResizeObserver' in window) {
      new ResizeObserver(() => document.documentElement.style.setProperty('--now-h', `${now.offsetHeight}px`)).observe(now);
    }
  }

  function boot() {
    if (booted) return;
    booted = true;
    const saved = ui.local.get('nav', null);
    if (U.isObj(saved)) {
      if (VIEWS.includes(saved.view)) nav.view = saved.view;
      if (MORE.includes(saved.more)) nav.more = saved.more;
      if (DRAWER.includes(saved.drawer)) nav.drawer = saved.drawer;
    }
    const t = ui.local.get('theme', null);
    setTheme(t === 'dark' || t === 'light' ? t : null);
    applyNav();
    fromHash();
    wire();
    T.store.subscribe(schedule);
    T.store.start();
    flush();
    setInterval(tick, TICK_MS);
  }

  T.app = {
    CONTAINERS,
    /** Ask for a render of everything (coalesced to one per frame). */
    render: schedule,
    go,
    /** The last view model rendered (null before the first). */
    view: () => current,
    /** Where the viewer is: {view, more, drawer}. */
    nav: () => Object.assign({}, nav),
    wide: isWide,
    setTheme,
    theme: () => (effectiveDark() ? 'dark' : 'light'),
  };

  // Boot after the whole script has run, so every panel file has registered first.
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else setTimeout(boot, 0);
})();
