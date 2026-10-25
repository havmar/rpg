// The More panels (README: File ownership): Months, Rules, Talk and Table, plus two things
// that decorate the whole page from here without touching the shell:
// - the first-visit notes for every tab (T.notes.for(tab) for a panel to place; Morten,
//   Realm and Fights get theirs before their pane when the panel shows no note of its own),
// - the unread marks: a dot on the Story tab (new sections or beats), on Talk (a new aside)
//   and on Fights (a new fight) until the viewer has looked, the last seen kept per viewer.
// And the hook a Months row uses to open the Story at a month: the `table:goto` event.
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;
  const ui = T.ui;
  const { esc, icon, fmt, put } = ui;
  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
  const canSend = (view) => !!(view && view.state && view.canWrite && view.db === 'ok');

  // ====================================================================================
  // First-visit notes, one line a tab. T.notes.for(tab) gives the note's HTML ('' once
  // dismissed) and tells this file the panel placed it itself.
  // ====================================================================================
  const NOTE_TEXT = {
    story: 'The <b>Story</b>: what happened, oldest at the top. Each section tells it first; its trace, folded under it, has every roll. Your answer box is at the end.',
    morten: '<b>Morten</b>: his sheet as it stands now: HP, AC, his spells (a struck-out one is lost until a Long Rest), his gear and the coins he carries.',
    realm: 'The <b>Realm</b>: the tower and the map of the six realms. Tap a hex for who holds it, what is there and how far it is from Morten.',
    fights: '<b>Fights</b>: every fight so far, with its foes and their CR, how it went round by round, and the dice.',
    more: '<b>More</b>: the months at a glance, the house rules, table talk with the GM, and the table\'s settings.',
  };
  const claimed = {};
  T.notes = {
    text: NOTE_TEXT,
    /** The first-visit note for a tab (story, morten, realm, fights, more), or '' once dismissed. */
    for(tab) {
      if (!NOTE_TEXT[tab]) return '';
      claimed[tab] = true;
      return ui.note(`tab.${tab}`, NOTE_TEXT[tab]);
    },
  };
  // A dismissed note can show in several places (the More note is in all four panels).
  document.addEventListener('click', (ev) => {
    const b = ev.target && ev.target.closest ? ev.target.closest('[data-note-dismiss]') : null;
    if (!b) return;
    const id = b.getAttribute('data-note-dismiss');
    for (const n of U.$$('.note[data-note]')) if (n.getAttribute('data-note') === id) n.remove();
    if (T.app) T.app.render();
  });

  /**
   * The note for a drawer tab whose panel shows none of its own (and has not called
   * T.notes.for): put just before the pane, in the shell's drawer, never inside the
   * panel's container. CSS shows it only while its tab is the one in view. The Story
   * is left to its panel (it sits in the page's two-column grid).
   */
  function placeNotes() {
    for (const tab of ['morten', 'realm', 'fights']) {
      const pane = document.getElementById(tab);
      if (!pane || !pane.parentNode) continue;
      const id = `tab.${tab}`;
      let wrap = U.$(`.tab-note[data-for="${tab}"]`);
      const want = !claimed[tab] && !ui.noteSeen(id) && !pane.querySelector('.note');
      if (!want) {
        if (wrap) wrap.remove();
        continue;
      }
      if (!wrap) {
        wrap = document.createElement('div');
        wrap.className = 'tab-note';
        wrap.setAttribute('data-for', tab);
        pane.parentNode.insertBefore(wrap, pane);
      }
      if (!wrap.querySelector('.note')) wrap.innerHTML = ui.note(id, NOTE_TEXT[tab]);
    }
  }

  // ====================================================================================
  // Unread marks. Each mark has a signature of what its tab shows; the one last seen is
  // kept per viewer (T.ui.local 'seen'). A tab never seen adopts what it shows, so a first
  // visit is not all marks. Dots decorate the shell's tab buttons by DOM.
  // ====================================================================================
  const MARKS = {
    story: {
      sig: (v) => (v.loaded.story ? Math.max(0, ...v.sections.map((s) => s.seq), ...v.beats.map((b) => b.seq)) : null),
      looking: (nav, wide) => wide || nav.view === 'story',
      targets: ['#tabs button[data-view="story"]'],
    },
    talk: {
      sig: (v) => (v.loaded.story ? Math.max(0, ...v.sections.filter((s) => s.kind === 'aside').map((s) => s.seq)) : null),
      looking: (nav, wide) => nav.drawer === 'talk' && (wide || nav.view === 'more'),
      targets: ['#tabs button[data-view="more"]', '#more-tabs button[data-more="talk"]', '#dtabs button[data-drawer="talk"]'],
    },
    fights: {
      sig: (v) => (v.state ? v.state.lastFight || '' : null),
      looking: (nav, wide) => (wide ? nav.drawer === 'fights' : nav.view === 'fights'),
      targets: ['#tabs button[data-view="fights"]', '#dtabs button[data-drawer="fights"]'],
    },
  };
  let seen = null;

  function unread(view) {
    if (!seen) {
      const s = ui.local.get('seen', null);
      seen = U.isObj(s) ? Object.assign({}, s) : {};
    }
    const nav = T.app.nav();
    const wide = T.app.wide();
    let changed = false;
    const lit = {};
    for (const [id, m] of Object.entries(MARKS)) {
      const sig = m.sig(view);
      if (sig === null) continue;
      if (seen[id] === undefined || m.looking(nav, wide) || (typeof sig === 'number' && sig < seen[id])) {
        if (seen[id] !== sig) {
          seen[id] = sig;
          changed = true;
        }
        continue;
      }
      lit[id] = typeof sig === 'number' ? sig > seen[id] : sig !== '' && sig !== seen[id];
    }
    if (changed) ui.local.set('seen', seen);
    // a button can be the target of two marks (More: Talk); any lit one lights it
    const on = new Map();
    for (const [id, m] of Object.entries(MARKS)) {
      for (const sel of m.targets) {
        const b = U.$(sel);
        if (b) on.set(b, (on.get(b) || false) || !!lit[id]);
      }
    }
    for (const [b, isOn] of on) {
      let dot = b.querySelector('.dot');
      if (!dot) {
        dot = document.createElement('i');
        dot.className = 'dot';
        dot.setAttribute('aria-hidden', 'true');
        b.appendChild(dot);
      }
      dot.hidden = !isOn;
      if (isOn) b.setAttribute('data-unread', 'true');
      else b.removeAttribute('data-unread');
    }
  }

  // ====================================================================================
  // Opening the Story at a month (a Months row). The Story panel can take it over: it
  // listens for `table:goto` on document and calls preventDefault() when it scrolls itself.
  // ====================================================================================
  function gotoMonth(month) {
    ui.local.set('goto', { month, at: Date.now() });
    T.app.go('story');
    const ev = new CustomEvent('table:goto', { detail: { month }, cancelable: true });
    if (!document.dispatchEvent(ev)) return;
    // after the Story has rendered for the new view
    requestAnimationFrame(() => requestAnimationFrame(() => setTimeout(() => scrollToMonth(month), 0)));
  }

  function scrollToMonth(month) {
    const story = document.getElementById('story');
    if (!story) return false;
    let el = story.querySelector(`[data-month="${month}"]`) || story.querySelector(`.month[data-m="${month}"]`);
    if (!el) {
      const re = new RegExp(`^\\s*Month ${month}\\b`);
      el = U.$$('h1, h2, h3, h4, header, summary', story).find((h) => re.test(h.textContent || '')) || null;
    }
    if (!el) return false;
    if (el.tagName === 'SUMMARY' && el.parentElement && el.parentElement.tagName === 'DETAILS') el.parentElement.open = true;
    else if (el.getAttribute('aria-expanded') === 'false') el.click(); // a folded month header unfolds on its own tap
    const nowH = (document.getElementById('now') || {}).offsetHeight || 0;
    window.scrollTo({ top: Math.max(0, el.getBoundingClientRect().top + window.scrollY - nowH - 10) });
    return true;
  }

  // ====================================================================================
  // Months: one row a month from the story's sections.
  // ====================================================================================
  const PIP = {
    cleared: ['won', 'cleared'], going: ['going', 'going on'], died: ['lost', 'he died'],
    fled: ['fled', 'he fled'], bypassed: ['bypassed', 'bypassed'],
  };

  function lootGp(s) {
    const m = /([+−-]?)\s*(\d[\d,]*)\s*GP/i.exec(typeof s === 'string' ? s : '');
    if (!m) return 0;
    const n = parseInt(m[2].replace(/,/g, ''), 10);
    return m[1] === '-' || m[1] === '−' ? -n : n;
  }

  function homeHex(view) {
    const r = view.realm;
    const tower = r && r.factions.find((f) => f.tower);
    return tower && tower.seat ? tower.seat : '';
  }

  /** The months, oldest first, each with what the Months row shows. */
  function monthsOf(view) {
    const by = new Map();
    for (const s of view.sections) {
      if (s.month === null) continue;
      if (!by.has(s.month)) by.set(s.month, []);
      by.get(s.month).push(s);
    }
    const st = view.state;
    const playing = st && st.month !== null && st.status !== 'ended' ? st.month : null;
    if (playing !== null && !by.has(playing)) by.set(playing, []);
    let prevEnd = null;
    return [...by.keys()].sort((a, b) => a - b).map((m) => {
      const secs = by.get(m);
      const fights = secs.filter((s) => s.fight || s.kind === 'fight');
      const withXp = secs.filter((s) => s.after && isNum(s.after.xp));
      const firstFight = fights.find((s) => s.fight && isNum(s.fight.xpBefore));
      let start = prevEnd;
      if (start === null && firstFight) start = firstFight.fight.xpBefore;
      if (start === null && withXp.length) start = withXp[0].after.xp;
      let end = withXp.length ? withXp[withXp.length - 1].after.xp : null;
      if (m === playing && st && isNum(st.xp)) end = st.xp;
      if (end !== null) prevEnd = end;
      const route = [];
      for (const s of secs) if (s.hex && route[route.length - 1] !== s.hex) route.push(s.hex);
      const pips = fights.map((s) => ({ outcome: s.fight ? s.fight.outcome : 'going', title: s.title }));
      if (m === playing && st.live && st.live.kind === 'fight' && !pips.some((p) => p.outcome === 'going')) pips.push({ outcome: 'going', title: st.live.title });
      const deaths = Math.max(secs.filter((s) => s.kind === 'death').length, fights.filter((s) => s.fight && s.fight.outcome === 'died').length);
      const days = secs.map((s) => s.day).filter(isNum);
      const world = secs.filter((s) => s.kind === 'domain').pop() || null;
      const gold = world && world.domain ? world.domain.tower.find((t) => /gold/i.test(t.what)) : null;
      return {
        month: m,
        playing: m === playing,
        count: secs.length,
        days: days.length ? [Math.min(...days), Math.max(...days)] : null,
        route,
        pips,
        xp: start !== null && end !== null ? end - start : null,
        loot: fights.reduce((sum, s) => sum + (s.fight ? lootGp(s.fight.loot) : 0), 0),
        deaths,
        world: world ? world.headline || world.title || "the world's turn" : '',
        gold: gold && (gold.before || gold.after) ? gold : null,
      };
    });
  }

  function hexWords(id, view, home) {
    if (id === home) return '<span>home</span>';
    const names = view.realm ? view.realm.hexNames : {};
    const name = names[id];
    return name ? `<span>${esc(name)} <small>${esc(id)}</small></span>` : `<span>${esc(id)}</span>`;
  }

  function monthRow(mo, view, home) {
    const sub = mo.playing ? 'in play' : mo.days ? (mo.days[0] === mo.days[1] ? `day ${mo.days[0]}` : `days ${mo.days[0]}–${mo.days[1]}`) : '';
    const route = mo.route.length > 6 ? mo.route.slice(0, 2).concat(['…'], mo.route.slice(-3)) : mo.route;
    const parts = [];
    if (route.length) {
      parts.push(`<span class="route">${icon('boots')}${route.map((h) => (h === '…' ? '<span class="muted">…</span>' : hexWords(h, view, home))).join('<span class="arr" aria-hidden="true">→</span>')}</span>`);
    } else if (mo.playing && !mo.count) {
      parts.push('<span class="route muted">not played yet</span>');
    }
    if (mo.pips.length) {
      const counts = {};
      for (const p of mo.pips) counts[p.outcome] = (counts[p.outcome] || 0) + 1;
      const words = Object.entries(counts).map(([k, n]) => `${n} ${(PIP[k] || PIP.going)[1]}`).join(', ');
      parts.push(`<span class="fightpips"><span class="pips" role="img" aria-label="${esc(`${fmt.plural(mo.pips.length, 'fight')}: ${words}`)}">${mo.pips.map((p) => `<i class="${(PIP[p.outcome] || PIP.going)[0]}" title="${esc(p.title)}"></i>`).join('')}</span><small>${esc(fmt.plural(mo.pips.length, 'fight'))}</small></span>`);
    }
    const gains = [];
    if (mo.xp !== null && (mo.xp !== 0 || mo.count)) gains.push(`${mo.xp >= 0 ? '+' : ''}${fmt.xp(mo.xp)}${mo.playing && mo.count ? ' so far' : ''}`);
    if (mo.loot) gains.push(`${mo.loot > 0 ? '+' : ''}${fmt.gp(mo.loot)} found`);
    if (gains.length) parts.push(`<small class="gains">${esc(gains.join(' · '))}</small>`);
    if (mo.deaths) parts.push(`<small class="bad deaths">${icon('skull')}${esc(fmt.plural(mo.deaths, 'death'))}</small>`);
    if (mo.world) {
      const gold = mo.gold ? ` <small>the tower's gold ${esc(mo.gold.before)} → ${esc(mo.gold.after)}</small>` : '';
      parts.push(`<span class="world">${icon('globe')}<span>${esc(mo.world)}${gold}</span></span>`);
    } else if (mo.count) {
      parts.push(`<span class="world muted">${icon('globe')}<span>the world's turn ${mo.playing ? 'to come' : 'not written up'}</span></span>`);
    }
    return `<li class="mrow${mo.playing ? ' playing' : ''}"><div class="n"><b>Month ${esc(mo.month)}</b>${sub ? `<small>${esc(sub)}</small>` : ''}</div>`
      + `<button type="button" class="cell" data-goto-month="${esc(mo.month)}">${parts.join('')}<span class="go" aria-hidden="true">${icon('chev')}</span><span class="vh">Open the story at month ${esc(mo.month)}</span></button></li>`;
  }

  (() => {
    let box = null;
    T.panels.months = {
      mount(el) {
        box = el;
        el.addEventListener('click', (ev) => {
          const b = ev.target.closest('[data-goto-month]');
          if (!b) return;
          const m = parseInt(b.getAttribute('data-goto-month'), 10);
          if (Number.isFinite(m)) gotoMonth(m);
        });
      },
      render(view) {
        const months = monthsOf(view);
        const home = homeHex(view);
        let body;
        if (!months.length) {
          body = `<p class="muted empty">${view.db !== 'ok' ? 'The months show when the table is open.' : view.ready ? 'No months yet: the first one shows here when the GM opens the campaign.' : 'Opening the table…'}</p>`;
        } else {
          body = `<ol class="months">${months.map((mo) => monthRow(mo, view, home)).join('')}</ol>`;
        }
        put(box, `${ui.note('tab.more', NOTE_TEXT.more)}<div class="card more-card"><h3>${icon('cal')}The months <small>a row opens the story there</small></h3>${body}</div>`);
      },
    };
  })();

  // ====================================================================================
  // Rules: game/rules.sections, a contents list, a filter box and a fold each.
  // ====================================================================================
  (() => {
    let box = null;
    let top = null;
    let bar = null;
    let body = null;
    let input = null;
    let q = '';
    const open = new Set();
    const fold = (id) => U.$$('details.rule', box).find((d) => d.getAttribute('data-rule') === id) || null;
    const norm = (t) => String(t || '').toLowerCase();

    /** Wrap each match of q in the visible text of el with <mark> (text nodes only: safe). */
    function mark(el, needle) {
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const hits = [];
      for (let n = walker.nextNode(); n; n = walker.nextNode()) if (norm(n.nodeValue).includes(needle)) hits.push(n);
      for (const n of hits) {
        const text = n.nodeValue;
        const low = norm(text);
        const frag = document.createDocumentFragment();
        let i = 0;
        for (let j = low.indexOf(needle); j >= 0; j = low.indexOf(needle, i)) {
          if (j > i) frag.appendChild(document.createTextNode(text.slice(i, j)));
          const m = document.createElement('mark');
          m.textContent = text.slice(j, j + needle.length);
          frag.appendChild(m);
          i = j + needle.length;
        }
        if (i < text.length) frag.appendChild(document.createTextNode(text.slice(i)));
        n.parentNode.replaceChild(frag, n);
      }
    }

    T.panels.rules = {
      mount(el) {
        box = el;
        el.innerHTML = '<div data-r="top"></div>'
          + '<label class="rsearch" data-r="bar" hidden><svg class="ic" aria-hidden="true"><use href="#i-eye"/></svg>'
          + '<input type="search" data-r="q" placeholder="Find in the rules: Shield, Rob, death…" aria-label="Find in the rules" autocomplete="off"></label>'
          + '<div data-r="body"></div>';
        top = U.$('[data-r="top"]', el);
        bar = U.$('[data-r="bar"]', el);
        body = U.$('[data-r="body"]', el);
        input = U.$('[data-r="q"]', el);
        input.addEventListener('input', () => {
          q = norm(input.value.trim());
          T.panels.rules.render(T.app.view());
        });
        el.addEventListener('toggle', (ev) => {
          const d = ev.target;
          if (!d || !d.matches || !d.matches('details.rule')) return;
          if (q) return; // a fold opened by the filter is not remembered
          const id = d.getAttribute('data-rule');
          if (d.open) open.add(id);
          else open.delete(id);
          const all = U.$('[data-rules-all]', box);
          if (all) all.textContent = U.$$('details.rule', box).every((x) => x.open) ? 'Fold all' : 'Open all';
        }, true);
        el.addEventListener('click', (ev) => {
          const t = ev.target.closest('[data-rule-go]');
          if (t) {
            const d = fold(t.getAttribute('data-rule-go'));
            if (!d) return;
            d.open = true;
            const nowH = (document.getElementById('now') || {}).offsetHeight || 0;
            if (T.app.wide()) d.scrollIntoView({ block: 'start' });
            else window.scrollTo({ top: Math.max(0, d.getBoundingClientRect().top + window.scrollY - nowH - 10) });
            return;
          }
          if (ev.target.closest('[data-rules-clear]')) {
            input.value = '';
            q = '';
            T.panels.rules.render(T.app.view());
            input.focus();
            return;
          }
          if (ev.target.closest('[data-rules-all]')) {
            const all = U.$$('details.rule', box);
            const to = !all.every((x) => x.open);
            for (const d of all) d.open = to;
          }
        });
      },
      render(view) {
        if (!box || !view) return;
        const secs = view.rules ? view.rules.sections : [];
        let head;
        let folds = '';
        bar.hidden = !secs.length;
        if (!secs.length) {
          head = `<div class="card more-card"><h3>${icon('book')}Rules</h3><p class="muted empty">${view.loaded.rules || view.db !== 'ok' ? 'The GM has not put the rules on the table yet.' : 'Opening the rules…'}</p></div>`;
        } else {
          // the filter: a section matches by its title or its text; matches open, the rest hide
          const shown = q ? secs.filter((s) => norm(s.title).includes(q) || norm(s.md).includes(q)) : secs;
          const allOpen = shown.length && shown.every((s) => q || open.has(s.id));
          head = `<div class="card more-card"><h3>${icon('book')}Rules <small>the house rules, cut from the campaign</small></h3>`
            + `<nav class="toc" aria-label="The rules' contents">${shown.map((s) => `<button type="button" data-rule-go="${esc(s.id)}">${esc(s.title || s.id)}</button>`).join('')}</nav>`
            + (q
              ? `<p class="rfound" role="status">${shown.length ? `${esc(fmt.plural(shown.length, 'section'))} with “${esc(input.value.trim())}”` : `Nothing in the rules says “${esc(input.value.trim())}”.`} <button type="button" class="toggle" data-rules-clear>Clear</button></p>`
              : `<div class="toc-bar"><button type="button" class="toggle" data-rules-all>${allOpen ? 'Fold all' : 'Open all'}</button></div>`)
            + '</div>';
          folds = shown.map((s) => `<details class="sec rule" data-rule="${esc(s.id)}"${q || open.has(s.id) ? ' open' : ''}><summary>${icon('chev')}<span>${esc(s.title || s.id)}</span></summary>${ui.md(s.md)}</details>`).join('');
        }
        put(top, `${ui.note('tab.more', NOTE_TEXT.more)}${head}`);
        const key = `${q}\u0000${folds}`;
        if (body.dataset.k !== key) {
          body.dataset.k = key;
          body.innerHTML = folds;
          if (q) for (const d of U.$$('details.rule', body)) mark(d, q);
        }
      },
    };
  })();

  // ====================================================================================
  // Talk: every aside and every out-of-game say, in order, and a box to ask the GM.
  // ====================================================================================
  (() => {
    let box = null;
    let els = null;
    let lastSent = null; // {id, text} of this box's last send
    let error = '';
    let busy = false;
    const OOC_KEY = 'talk.ooc';

    function oocIds() {
      const v = ui.local.get(OOC_KEY, []);
      return new Set(Array.isArray(v) ? v.filter((x) => typeof x === 'string') : []);
    }

    function you(text, label, cls = '', extra = '') {
      return `<div class="you${cls ? ` ${cls}` : ''}"><span class="label">${label}</span><p>${esc(text)}</p>${extra}</div>`;
    }

    function items(view) {
      const out = [];
      const mine = oocIds();
      for (const s of view.sections) {
        const isAside = s.kind === 'aside';
        const asked = s.words.filter((w) => isAside || mine.has(w.move));
        if (!isAside && !asked.length) continue;
        for (const w of asked) out.push(you(w.text, 'You, out of game'));
        if (!isAside) continue;
        const when = fmt.when(s);
        const head = s.ooc ? 'The GM, out of game' : s.title && s.title !== 'Aside' ? s.title : "The GM's aside";
        const prose = s.prose.length ? s.prose : s.headline ? [s.headline] : [];
        out.push(`<article class="sec aside" data-seq="${esc(s.seq)}"><div class="sec-head">${icon('speech')}<div><h3>${esc(head)}${when ? `<small>${esc(when)}</small>` : ''}</h3>${prose.map((p) => `<p>${esc(p)}</p>`).join('')}</div></div></article>`);
      }
      for (const m of view.moves) {
        if (m.kind !== 'say' || !m.ooc) continue;
        const ago = m.at ? ui.ago(m.at, view.now) : '';
        out.push(you(m.text, `You, out of game · sent${ago ? ` ${esc(ago)}` : ''} · waiting for the GM`, 'sent'));
      }
      for (const p of view.pending) {
        if (!p.move || p.move.kind !== 'say' || !p.move.ooc) continue;
        if (p.status === 'failed') {
          out.push(you(p.move.text, `<span class="bad">not sent: ${esc(p.error || 'the write failed')}</span>`, 'failed',
            `<div class="acts"><button type="button" data-retry="${esc(p.id)}">Send again</button><button type="button" data-dismiss="${esc(p.id)}">Drop it</button></div>`));
        } else out.push(you(p.move.text, 'You, out of game · sending…', 'pending'));
      }
      return out;
    }

    function hint(view) {
      if (error) return `<span class="bad">${esc(error)}</span>`;
      if (view.db !== 'ok') return 'opens with the table';
      if (!view.canWrite) return 'watching: asking needs edit access';
      const w = view.wake;
      // once the GM has answered it (the move is gone from the store), the hint is the usual one
      const open = lastSent && (view.moves.some((m) => m.id === lastSent.id) || view.pending.some((p) => p.id === lastSent.id));
      if (open && w.move === lastSent.id) {
        if (w.state === 'calling') return 'sent · calling the GM…';
        if (w.state === 'called') return 'sent · the GM has been called';
        if (w.state === 'off') return 'sent · the GM reads it at the next stop';
        if (w.state === 'unavailable' || w.state === 'failed') return `sent · ${esc(w.reason)}`;
      }
      return 'answered here, as an aside';
    }

    function update(view) {
      if (!els) return;
      const list = items(view);
      put(els.list, list.length ? list.join('') : '<p class="muted empty">No table talk yet. The GM\'s asides and your out-of-game questions gather here, in order.</p>');
      put(els.hint, hint(view));
      els.send.disabled = busy || !canSend(view) || !els.text.value.trim();
      els.text.disabled = !canSend(view);
      put(els.note, ui.note('tab.more', NOTE_TEXT.more));
    }

    function send() {
      const view = T.app.view();
      const text = els.text.value.trim();
      if (!text || !canSend(view) || busy) return;
      busy = true;
      error = '';
      els.send.disabled = true;
      T.store.send('say', { text, ooc: true }).then((r) => {
        lastSent = { id: r.id, text };
        const ids = [...oocIds(), r.id].slice(-60);
        ui.local.set(OOC_KEY, ids);
        if (els.text.value.trim() === text) els.text.value = '';
      }, (err) => {
        error = `not sent: ${U.errText(err)}`;
      }).finally(() => {
        busy = false;
        T.app.render();
      });
    }

    T.panels.talk = {
      mount(el) {
        box = el;
        box.innerHTML = '<div data-talk-note></div>'
          + `<div class="card more-card talk"><h3>${icon('speech')}Table talk <small>every aside, in order</small></h3><div class="talk-list" data-talk-list></div>`
          + '<div class="box talk-box"><label class="vh" for="talk-text">Ask the GM something out of game</label><textarea id="talk-text" rows="2" placeholder="Ask the GM something out of game."></textarea>'
          + '<div class="send"><span class="hint" data-talk-hint></span><button type="button" id="talk-send">Send</button></div></div></div>';
        els = {
          note: U.$('[data-talk-note]', box),
          list: U.$('[data-talk-list]', box),
          hint: U.$('[data-talk-hint]', box),
          text: U.$('#talk-text', box),
          send: U.$('#talk-send', box),
        };
        els.send.addEventListener('click', send);
        els.text.addEventListener('input', () => {
          error = '';
          const v = T.app.view();
          els.send.disabled = busy || !canSend(v) || !els.text.value.trim();
        });
        els.text.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey)) {
            ev.preventDefault();
            send();
          }
        });
        box.addEventListener('click', (ev) => {
          const r = ev.target.closest('[data-retry]');
          if (r) {
            T.store.retry(r.getAttribute('data-retry')).catch(() => {});
            return;
          }
          const d = ev.target.closest('[data-dismiss]');
          if (d) T.store.dismiss(d.getAttribute('data-dismiss'));
        });
      },
      render: update,
      tick: update,
    };
  })();

  // ====================================================================================
  // Table: the dials (plan section 5), the three presets, taking Morten, the habits and
  // the theme. A change sends one `table` move with the whole dials object; a control shows
  // "pending" until game/state.table comes back equal.
  // ====================================================================================
  const KEYS = ['who', 'stop', 'fights', 'world', 'dice', 'mode'];
  const DIALS = [
    { key: 'who', name: 'Who moves Morten', line: 'with you, the GM stops for each of his turns and choices', opts: [['dm', 'the GM'], ['you', 'you']] },
    { key: 'stop', name: 'Stop for your word', line: "where the GM's run ends", opts: [['month', 'never in the month'], ['orders', "at each month's orders"], ['fight', 'before each fight'], ['round', 'each round'], ['matters', 'when something matters']] },
    { key: 'fights', name: 'Fights', line: 'how they reach the page; the trace keeps every round', opts: [['live', 'live, every round'], ['turning', 'turning points'], ['summary', 'summary after'], ['line', 'one line']] },
    { key: 'world', name: "The world's turn", line: "the GM's story, or the script's report unfolded", opts: [['story', 'as a story'], ['report', 'the full report']] },
    { key: 'dice', name: 'Dice in the story', line: 'the trace keeps every die', opts: [['key', 'key rolls'], ['all', 'all'], ['none', 'none']] },
    { key: 'mode', name: 'Table', line: 'how much of the foes you see', opts: [['open', "open: foes' HP as numbers"], ['closed', 'closed: Healthy, Bloodied, Near death']] },
  ];
  const PRESETS = [
    { id: 'autoplay', name: 'Autoplay', line: 'the GM plays the month through and the fights live', set: { who: 'dm', stop: 'month', fights: 'live', world: 'story' } },
    { id: 'folded', name: 'Autoplay, fights folded', line: 'the same, each fight one line; the realms in front', set: { who: 'dm', stop: 'month', fights: 'line', world: 'story' } },
    { id: 'input', name: 'More input', line: 'you move Morten; the GM stops before each fight', set: { who: 'you', stop: 'fight' } },
  ];
  const label = (key, val) => {
    const d = DIALS.find((x) => x.key === key);
    const o = d && d.opts.find((x) => x[0] === val);
    return o ? o[1] : String(val);
  };
  const sameList = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
  const sameTable = (a, b) => !!a && !!b && KEYS.every((k) => a[k] === b[k]) && sameList(a.habits, b.habits);
  const copyTable = (t) => ({ who: t.who, stop: t.stop, fights: t.fights, world: t.world, dice: t.dice, mode: t.mode, habits: t.habits.slice() });

  (() => {
    let box = null;
    let els = null;
    let want = null; // {table, id, error}: the dials this view sent, until the state agrees or the move is answered
    let take = null; // {who, id, error}
    let dirty = false; // the habits are being edited
    let habitsKey = null;

    const present = (view, id) => !!id && (view.moves.some((m) => m.id === id) || view.pending.some((p) => p.id === id));

    /** The newest table move not yet answered (this view's or another's). */
    function inFlight(view) {
      let best = null;
      for (const m of view.moves) if (m.kind === 'table' && m.table && (!best || m.seq > best.seq)) best = { seq: m.seq, table: m.table };
      for (const p of view.pending) if (p.move && p.move.kind === 'table' && p.move.table && p.status !== 'failed' && (!best || p.seq > best.seq)) best = { seq: p.seq, table: p.move.table };
      return best ? best.table : null;
    }

    function settle(view) {
      const st = view.state;
      if (want && st && sameTable(want.table, st.table)) want = null;
      else if (want && want.id && !present(view, want.id)) want = null; // answered: the state is the GM's word
      if (take && st && st.table.who === take.who) take = null;
      else if (take && take.id && !present(view, take.id)) take = null;
    }

    /** What the controls show: the dials asked for, else the state's. */
    function shown(view) {
      const st = view.state;
      if (want && !want.error) return want.table;
      const fl = inFlight(view);
      if (fl && st && !sameTable(fl, st.table)) return fl;
      return st ? st.table : null;
    }

    function sendTable(table) {
      const w = { table: copyTable(table), id: null, error: '' };
      want = w;
      T.store.send('table', { table: w.table }).then((r) => {
        w.id = r.id;
      }, (err) => {
        w.error = `not sent: ${U.errText(err)}`;
      }).finally(() => T.app.render());
      T.app.render();
    }

    function onClick(ev) {
      const view = T.app.view();
      const th = ev.target.closest('[data-theme-set]');
      if (th) {
        const v = th.getAttribute('data-theme-set');
        T.app.setTheme(v === 'system' ? null : v);
        // pressed at once (the panel's own render follows on the next frame)
        for (const x of U.$$('[data-theme-set]', th.parentNode)) x.setAttribute('aria-pressed', String(x === th));
        T.app.render();
        return;
      }
      const b = ev.target.closest('button');
      if (!b || b.disabled || !canSend(view)) return;
      const cur = shown(view);
      if (!cur) return;
      if (b.hasAttribute('data-dial')) {
        const key = b.getAttribute('data-dial');
        const val = b.getAttribute('data-val');
        if (cur[key] === val && !(want && want.error)) return;
        sendTable(Object.assign(copyTable(cur), { [key]: val }));
        return;
      }
      if (b.hasAttribute('data-preset')) {
        const p = PRESETS.find((x) => x.id === b.getAttribute('data-preset'));
        if (p) sendTable(Object.assign(copyTable(cur), p.set));
        return;
      }
      if (b.hasAttribute('data-take')) {
        const who = b.getAttribute('data-take');
        const t = { who, id: null, error: '' };
        take = t;
        T.store.send('take', { who }).then((r) => {
          t.id = r.id;
        }, (err) => {
          t.error = `not sent: ${U.errText(err)}`;
        }).finally(() => T.app.render());
        T.app.render();
        return;
      }
      if (b.hasAttribute('data-habits-send')) {
        const lines = U.$$('textarea[data-habit]', els.habits).map((x) => x.value.replace(/\s+/g, ' ').trim()).filter(Boolean);
        dirty = false;
        habitsKey = null;
        sendTable(Object.assign(copyTable(cur), { habits: lines }));
        return;
      }
      if (b.hasAttribute('data-habits-undo')) {
        dirty = false;
        habitsKey = null;
        T.app.render();
        return;
      }
      if (b.hasAttribute('data-habit-add')) {
        const list = U.$('[data-habit-list]', els.habits);
        list.insertAdjacentHTML('beforeend', habitRow(''));
        const ta = list.lastElementChild.querySelector('textarea');
        dirty = true;
        habitButtons(view);
        if (ta) ta.focus();
        return;
      }
      if (b.hasAttribute('data-habit-del')) {
        const row = b.closest('.habit');
        if (row) row.remove();
        dirty = true;
        habitButtons(view);
      }
    }

    function habitRow(text) {
      const rows = Math.max(1, Math.min(6, Math.ceil(text.length / 44)));
      return `<li class="habit"><textarea data-habit rows="${rows}" aria-label="A habit" placeholder="A standing order, in words">${esc(text)}</textarea><button type="button" data-habit-del aria-label="Remove this habit" title="Remove this habit">${icon('off')}</button></li>`;
    }

    function habitButtons(view) {
      const on = canSend(view);
      const s = U.$('[data-habits-send]', els.habits);
      const u = U.$('[data-habits-undo]', els.habits);
      const a = U.$('[data-habit-add]', els.habits);
      if (s) s.disabled = !on || !dirty;
      if (u) u.hidden = !dirty;
      if (a) a.disabled = !on;
      for (const x of U.$$('textarea[data-habit], [data-habit-del]', els.habits)) x.disabled = !on;
    }

    function renderHabits(view, cur, st) {
      const habits = cur ? cur.habits : [];
      const pending = cur && st && !sameList(cur.habits, st.table.habits);
      const on = canSend(view);
      const key = JSON.stringify([habits, on]);
      if (!dirty && key !== habitsKey) {
        habitsKey = key;
        els.habits.innerHTML = `<div class="d"><b>Habits</b><small>standing orders the GM plays Morten by, one a line</small><span class="pending" data-habits-pending></span></div>`
          + `<ul class="habit-list" data-habit-list>${habits.map(habitRow).join('')}</ul>`
          + '<div class="habit-acts"><button type="button" class="toggle" data-habit-add>Add a habit</button><button type="button" class="toggle" data-habits-undo hidden>Undo my changes</button><button type="button" class="primary" data-habits-send disabled>Send the habits</button></div>';
      }
      const p = U.$('[data-habits-pending]', els.habits);
      if (p) p.textContent = pending ? 'pending' : '';
      habitButtons(view);
    }

    function dialRow(d, cur, st, on) {
      const val = cur[d.key];
      const now = st ? st.table[d.key] : val;
      const pend = val !== now;
      return `<div class="dial" data-dial-row="${d.key}"><div class="d"><b>${esc(d.name)}</b><small>${esc(d.line)}</small>${pend ? `<span class="pending">pending: ${esc(label(d.key, val))}</span>` : ''}</div>`
        + `<div class="seg" role="group" aria-label="${esc(d.name)}">${d.opts.map(([v, l]) => `<button type="button" data-dial="${d.key}" data-val="${v}" aria-pressed="${v === val}"${pend && v === now ? ' class="was"' : ''}${on ? '' : ' disabled'}>${esc(l)}${pend && v === now ? '<small>now</small>' : ''}</button>`).join('')}</div></div>`;
    }

    function render(view) {
      if (!els) return;
      settle(view);
      const st = view.state;
      const cur = shown(view);
      const on = canSend(view);
      put(els.note, ui.note('tab.more', NOTE_TEXT.more));
      if (!cur) {
        put(els.top, `<p class="muted empty">${view.db !== 'ok' ? 'The table\'s settings show when the table is open.' : 'The settings show when the GM has set the table.'}</p>`);
        put(els.dials, '');
        els.habits.hidden = true;
      } else {
        els.habits.hidden = false;
        const msgs = [];
        if (!view.canWrite && view.db === 'ok') msgs.push(`<p class="muted watch">${icon('eye')}You are watching: changing the table needs edit access.</p>`);
        if (want && want.error) msgs.push(`<p class="bad err">${esc(want.error)}</p>`);
        if (take && take.error) msgs.push(`<p class="bad err">${esc(take.error)}</p>`);
        // who moves Morten now, and the take move
        const who = st ? st.table.who : cur.who;
        const tPend = take && !take.error ? take.who : null;
        const takeTo = (tPend || who) === 'you' ? 'dm' : 'you';
        const whoLine = tPend
          ? `<span>${tPend === 'you' ? 'You take Morten' : 'You hand Morten back'}</span><span class="pending">pending</span>`
          : `<span>${who === 'you' ? '<b>You</b> move Morten.' : '<b>The GM</b> moves Morten.'}</span>`;
        const takeBtn = `<button type="button" class="primary" data-take="${takeTo}"${on && !tPend ? '' : ' disabled'}>${icon('hand')}${takeTo === 'you' ? 'Take over Morten' : 'Hand him back'}</button>`;
        const active = PRESETS.find((p) => Object.entries(p.set).every(([k, v]) => cur[k] === v));
        const presets = `<div class="dial presets"><div class="d"><b>Modes</b><small>one tap sets the dials</small></div><div class="seg preset-seg">${PRESETS.map((p) => `<button type="button" data-preset="${p.id}" aria-pressed="${active === p}"${on ? '' : ' disabled'}><span>${esc(p.name)}</span><small>${esc(p.line)}</small></button>`).join('')}</div></div>`;
        put(els.top, `${msgs.join('')}<div class="take" data-take-row>${whoLine}${takeBtn}</div>${presets}`);
        put(els.dials, DIALS.map((d) => dialRow(d, cur, st, on)).join(''));
        renderHabits(view, cur, st);
      }
      const t = ui.local.get('theme', null);
      const theme = t === 'dark' || t === 'light' ? t : 'system';
      put(els.theme, `<div class="d"><b>Look</b><small>for this browser only</small></div><div class="seg" role="group" aria-label="Look">${[['light', 'Light', 'sun'], ['dark', 'Dark', 'moon'], ['system', 'As the device', 'gear']].map(([v, l, ic]) => `<button type="button" data-theme-set="${v}" aria-pressed="${theme === v}">${icon(ic)}${l}</button>`).join('')}</div>`);
    }

    T.panels.table = {
      mount(el) {
        box = el;
        box.innerHTML = '<div data-table-note></div>'
          + `<div class="card more-card dials"><h3>${icon('gear')}The table <small>a change goes to the GM</small></h3>`
          + '<div data-table-top></div><div data-table-dials></div><div class="dial habits-dial" data-table-habits></div><div class="dial" data-table-theme></div></div>';
        els = {
          note: U.$('[data-table-note]', box),
          top: U.$('[data-table-top]', box),
          dials: U.$('[data-table-dials]', box),
          habits: U.$('[data-table-habits]', box),
          theme: U.$('[data-table-theme]', box),
        };
        box.addEventListener('click', onClick);
        els.habits.addEventListener('input', (ev) => {
          if (!ev.target.matches('textarea[data-habit]')) return;
          dirty = true;
          habitButtons(T.app.view());
        });
      },
      render(view) {
        render(view);
        // last of the panels to render: decorate the page
        U.safe(() => unread(view), 'unread marks');
        U.safe(placeNotes, 'tab notes');
      },
    };
  })();

  // for the checks and for other panels
  T.more = { monthsOf, gotoMonth, scrollToMonth, PRESETS, DIALS };
})();
