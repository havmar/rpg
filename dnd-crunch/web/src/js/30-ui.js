// T.ui: the helpers every panel builds markup with. Every string from the store goes
// through esc() (or textContent) before it reaches the page; md() escapes first too.
(() => {
  'use strict';
  const T = window.T;
  const U = T.util;

  // ---------- escaping and icons ----------
  const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  /** Escape any value for HTML text or a double-quoted attribute. null/undefined give ''. */
  const esc = (v) => (v === null || v === undefined ? '' : String(v)).replace(/[&<>"']/g, (c) => ESC[c]);

  /** <svg class="ic"><use href="#i-NAME"/></svg>; extra classes in cls. */
  const icon = (name, cls = '') => `<svg class="ic${cls ? ` ${esc(cls)}` : ''}" aria-hidden="true"><use href="#i-${esc(name)}"/></svg>`;

  /** innerHTML only when it changed, so an unchanged panel keeps its focus, folds and scroll. */
  function put(el, html) {
    if (!el) return false;
    if (el.__tableHtml === html) return false;
    el.innerHTML = html;
    el.__tableHtml = html;
    return true;
  }

  // ---------- per-viewer storage ----------
  const PREFIX = 'table.';
  const local = {
    get(key, fallback = null) {
      try {
        const s = window.localStorage.getItem(PREFIX + key);
        return s === null ? fallback : JSON.parse(s);
      } catch (_) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        window.localStorage.setItem(PREFIX + key, JSON.stringify(value));
        return true;
      } catch (_) {
        return false;
      }
    },
    del(key) {
      try {
        window.localStorage.removeItem(PREFIX + key);
      } catch (_) { /* nothing to do */ }
    },
  };

  // ---------- numbers with their units ----------
  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
  const MINUS = '−';
  const fmt = {
    /** 1200 -> "1,200"; non-numbers -> dash. */
    n: (v, dash = '—') => (isNum(v) ? v.toLocaleString('en-GB', { maximumFractionDigits: 2 }) : dash),
    /** +5 / −1 / +0 */
    signed: (v) => (isNum(v) ? (v < 0 ? `${MINUS}${fmt.n(-v)}` : `+${fmt.n(v)}`) : '—'),
    /** "11/20 HP"; "13 HP" without a max; "? HP" with neither. */
    hp: (hp, max) => (isNum(hp) && isNum(max) ? `${fmt.n(hp)}/${fmt.n(max)} HP` : isNum(hp) ? `${fmt.n(hp)} HP` : isNum(max) ? `?/${fmt.n(max)} HP` : '? HP'),
    /** fmt.unit(8, 'dmg') -> "8 dmg". */
    unit: (v, unit) => (isNum(v) ? `${fmt.n(v)} ${unit}` : ''),
    gp: (v) => (isNum(v) ? `${fmt.n(v)} GP` : ''),
    xp: (v) => (isNum(v) ? `${fmt.n(v)} XP` : ''),
    kg: (v) => (isNum(v) ? `${fmt.n(v)} kg` : ''),
    ac: (v) => (isNum(v) ? `AC ${fmt.n(v)}` : ''),
    /** Squares with metres: 6 -> "6 sq (9 m)". */
    sq: (v) => (isNum(v) ? `${fmt.n(v)} sq (${fmt.n(v * 1.5)} m)` : ''),
    /** fmt.plural(3, 'fight') -> "3 fights"; plural(1, 'foe') -> "1 foe"; plural(2, 'ally', 'allies'). */
    plural: (v, one, many) => `${fmt.n(v, '0')} ${v === 1 ? one : many || `${one}s`}`,
    /** "Month 3 · Day 4 · 09:40", leaving out what is missing. */
    when: (o) => {
      const x = o && typeof o === 'object' ? o : {};
      const parts = [];
      if (isNum(x.month)) parts.push(`Month ${x.month}`);
      if (isNum(x.day)) parts.push(`Day ${x.day}`);
      if (typeof x.clock === 'string' && x.clock) parts.push(x.clock);
      return parts.join(' · ');
    },
  };

  /** HP band: '' above half, 'mid' to a quarter, 'low' below. */
  function band(hp, max) {
    if (!isNum(hp) || !isNum(max) || max <= 0) return '';
    const r = hp / max;
    return r > 0.5 ? '' : r > 0.25 ? 'mid' : 'low';
  }

  /** An HP bar: <span class="bar mid"><i style="width:55%"></i></span>; cls adds classes. */
  function bar(hp, max, cls = '') {
    const ok = isNum(hp) && isNum(max) && max > 0;
    const pct = ok ? Math.max(0, Math.min(100, Math.round((hp / max) * 100))) : 0;
    const label = ok ? `${fmt.n(hp)} of ${fmt.n(max)}` : 'unknown';
    return `<span class="bar ${band(hp, max)}${cls ? ` ${esc(cls)}` : ''}" role="img" aria-label="${esc(label)}"><i style="width:${pct}%"></i></span>`;
  }

  /**
   * A chip. chip('the Gnomes march', {kind: 'threat'}) -> <span class="chip threat"><span class="k">threat</span>…</span>.
   * opts: kind ('threat' | 'chance' | 'open' | 'good' | any class), k (the small label; defaults
   * to kind for threat/chance/open), icon (sprite name), html (true: text is trusted markup), tag.
   */
  function chip(textOrHtml, opts = {}) {
    const o = opts || {};
    const kind = typeof o.kind === 'string' ? o.kind : '';
    const k = typeof o.k === 'string' ? o.k : ['threat', 'chance', 'open'].includes(kind) ? kind : '';
    const tag = o.tag === 'button' ? 'button' : 'span';
    const attrs = tag === 'button' ? ' type="button"' : '';
    const body = o.html ? textOrHtml : esc(textOrHtml);
    return `<${tag}${attrs} class="chip${kind ? ` ${esc(kind)}` : ''}">${o.icon ? icon(o.icon) : ''}${k ? `<span class="k">${esc(k)}</span>` : ''}${body}</${tag}>`;
  }

  // ---------- dice ----------
  const RESULT = { hit: ['hit', 'hit'], miss: ['miss', 'miss'], cast: ['cast', 'ok'], fizzle: ['fizzle', 'fizz'], save: ['save', 'ok'], fail: ['fail', 'fail'] };
  const signedMod = (m) => (m < 0 ? `${MINUS}${-m}` : `+${m}`);

  /** The dice part of an expression: "1d20+5" -> "d20", "2d8" -> "2d8". */
  function dieLabel(expr) {
    const m = /(\d*)d(\d+)/i.exec(typeof expr === 'string' ? expr : '');
    if (!m) return typeof expr === 'string' ? expr : '';
    return m[1] && m[1] !== '1' ? `${m[1]}d${m[2]}` : `d${m[2]}`;
  }

  /**
   * A die chip for a Die (README: Line, Die): "d20 14 +5 = 19 vs AC 15 hit". A natural 20
   * is lit brass, a natural 1 red; a fizzle is dashed red. Dice dropped by advantage or
   * disadvantage are struck through.
   */
  function die(d) {
    if (!d || typeof d !== 'object') return '';
    const faces = Array.isArray(d.faces) ? d.faces.filter(isNum) : [];
    const kept = Array.isArray(d.kept) ? d.kept.filter(isNum) : faces;
    const mod = isNum(d.mod) ? d.mod : 0;
    const total = isNum(d.total) ? d.total : null;
    const res = RESULT[d.result] || null;
    const nat = d.nat === 20 || d.nat === 1 ? d.nat : null;
    // faces: the kept ones plain, the dropped ones struck
    const left = kept.slice();
    const shown = faces.map((f) => {
      const i = left.indexOf(f);
      if (i >= 0) {
        left.splice(i, 1);
        return esc(f);
      }
      return `<s>${esc(f)}</s>`;
    });
    const dropped = faces.length > kept.length;
    const facesHtml = dropped ? shown.join(' ') : shown.join('+');
    const showTotal = total !== null && (mod !== 0 || kept.length > 1);
    const cls = ['die'];
    if (nat === 20) cls.push('nat20');
    if (nat === 1) cls.push('nat1');
    if (d.result === 'fizzle') cls.push('fizzle');
    const words = [dieLabel(d.expr), faces.join(dropped ? ' or ' : ' + ')];
    if (mod) words.push(signedMod(mod));
    if (showTotal) words.push(`= ${total}`);
    if (d.vs) words.push(`vs ${d.vs}`);
    if (nat) words.push(`natural ${nat}`);
    if (res) words.push(res[0]);
    return `<span class="${cls.join(' ')}" title="${esc(words.filter(Boolean).join(' '))}"><b>${esc(dieLabel(d.expr) || 'die')}</b> ${facesHtml}`
      + (mod ? ` <i>${esc(signedMod(mod))}</i>` : '')
      + (showTotal ? ` = ${esc(total)}` : '')
      + (d.vs ? ` <u>vs ${esc(d.vs)}</u>` : '')
      + (nat ? ` <span class="r nat">nat ${nat}</span>` : '')
      + (res ? ` <span class="r ${res[1]}">${res[0]}</span>` : '')
      + '</span>';
  }
  const dice = (list) => (Array.isArray(list) ? list.map(die).join(' ') : '');

  // ---------- time ----------
  /** "just now", "4 min ago", "2 h 5 min ago", "3 days ago"; '' for a bad time. */
  function ago(at, now = Date.now()) {
    const t = U.ms(at);
    if (t === null) return '';
    const s = Math.max(0, Math.round((now - t) / 1000));
    if (s < 45) return 'just now';
    const m = Math.round(s / 60);
    if (m < 60) return `${m} min ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return m % 60 && h < 6 ? `${h} h ${m % 60} min ago` : `${h} h ago`;
    const days = Math.round(h / 24);
    return days === 1 ? 'a day ago' : `${days} days ago`;
  }

  // ---------- first-visit notes ----------
  /**
   * A first-visit note, shown until the viewer taps "Got it" (remembered per viewer).
   * html is trusted markup (write it in the panel, never from the store). '' once dismissed.
   */
  function note(id, html) {
    if (local.get(`note.${id}`, false)) return '';
    return `<div class="note" data-note="${esc(id)}">${icon('q')}<span>${html}</span><button type="button" data-note-dismiss="${esc(id)}">Got it</button></div>`;
  }
  const noteSeen = (id) => !!local.get(`note.${id}`, false);
  document.addEventListener('click', (ev) => {
    const b = ev.target && ev.target.closest ? ev.target.closest('[data-note-dismiss]') : null;
    if (!b) return;
    const id = b.getAttribute('data-note-dismiss');
    local.set(`note.${id}`, true);
    const n = b.closest('.note');
    if (n) n.remove();
  });

  // ---------- realms ----------
  const FACTIONS = ['humans', 'gnomes', 'tieflings', 'orcs', 'goblinkind', 'elves'];
  /** The colour class for a realm: fac('Gnomes') -> 'fac-gnomes', the tower -> 'fac-tower'. */
  function fac(name) {
    const s = typeof name === 'string' ? name.toLowerCase() : '';
    if (s === 'tower' || s === 'the tower') return 'fac-tower';
    return FACTIONS.includes(s) ? `fac-${s}` : 'fac-none';
  }

  // ---------- a small, safe Markdown ----------
  function inline(s) {
    // s is already escaped. Code spans first, kept out of the other rules.
    const codes = [];
    let out = s.replace(/`([^`]+)`/g, (_, c) => {
      codes.push(c);
      return `\u0000${codes.length - 1}\u0000`;
    });
    out = out
      .replace(/\*\*([^*]+?)\*\*/g, '<b>$1</b>')
      .replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)/g, '$1<i>$2</i>')
      .replace(/(^|[^\w])_([^_\s][^_]*?)_(?!\w)/g, '$1<i>$2</i>');
    return out.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[+i]}</code>`);
  }
  const cells = (row) => row.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
  const isRule = (row) => /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(row);

  /**
   * Markdown subset -> HTML in <div class="md">: paragraphs, **bold**, *italic*, `code`,
   * bullets (- or *), numbered lists, | tables |, headings (#..###: h4, ####: h5).
   * Everything is escaped first; no links, no raw HTML.
   */
  function md(src) {
    const lines = esc(typeof src === 'string' ? src : '').replace(/\r\n?/g, '\n').split('\n');
    const out = [];
    let para = [];
    const flush = () => {
      if (para.length) out.push(`<p>${inline(para.join(' '))}</p>`);
      para = [];
    };
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      if (!l.trim()) { flush(); continue; }
      const h = /^(#{1,4})\s+(.*)$/.exec(l);
      if (h) { flush(); out.push(h[1].length === 4 ? `<h5>${inline(h[2])}</h5>` : `<h4>${inline(h[2])}</h4>`); continue; }
      if (/^\s*\|/.test(l) && i + 1 < lines.length && isRule(lines[i + 1])) {
        flush();
        const head = cells(l);
        i += 1;
        const body = [];
        while (i + 1 < lines.length && /^\s*\|/.test(lines[i + 1])) { i += 1; body.push(cells(lines[i])); }
        out.push(`<div class="md-table"><table><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join('')}</tr></thead><tbody>${body.map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
        continue;
      }
      const ul = /^\s*[-*+]\s+(.*)$/.exec(l);
      const ol = /^\s*\d+[.)]\s+(.*)$/.exec(l);
      if (ul || ol) {
        flush();
        const tag = ul ? 'ul' : 'ol';
        const re = ul ? /^\s*[-*+]\s+(.*)$/ : /^\s*\d+[.)]\s+(.*)$/;
        const items = [(ul || ol)[1]];
        while (i + 1 < lines.length) {
          const m = re.exec(lines[i + 1]);
          if (m) { items.push(m[1]); i += 1; continue; }
          if (/^\s{2,}\S/.test(lines[i + 1]) && !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i + 1])) { items[items.length - 1] += ` ${lines[i + 1].trim()}`; i += 1; continue; }
          break;
        }
        out.push(`<${tag}${tag === 'ul' ? ' class="bullets"' : ''}>${items.map((t) => `<li>${inline(t)}</li>`).join('')}</${tag}>`);
        continue;
      }
      para.push(l.trim());
    }
    flush();
    return `<div class="md">${out.join('')}</div>`;
  }

  T.ui = { esc, icon, put, local, fmt, band, bar, chip, die, dice, dieLabel, ago, note, noteSeen, fac, md };
  T.icons = { use: icon };
})();
