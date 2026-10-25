// The Morten tab (#morten; table-plan.md 4.3): the sheet from game/morten, with what is
// true now (HP, AC, light, concentration, lost spells, coins) from game/state.hud when it
// is there. Cards: the HUD, Spells (tap one for its line), Fighting, Gear, Progress and
// Habits. UI state kept across renders: the spell picked, the open folds.
(() => {
  'use strict';
  const T = window.T;
  const { esc, icon, put, fmt, bar } = T.ui;
  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
  const arr = (v) => (Array.isArray(v) ? v : []);

  let box = null;
  let picked = null; // the spell (or feature) whose line shows: 'spell:Name' | 'feat:Name'
  const opened = new Set();

  /** The value now: game/state.hud's when it has one, else the sheet's. */
  function now(view) {
    const m = view.morten || {};
    const h = view.state && view.state.hud && view.state.hud.known ? view.state.hud : null;
    const pick = (k) => (h && h[k] !== null && h[k] !== undefined && h[k] !== '' ? h[k] : m[k] !== undefined ? m[k] : null);
    const coins = h && h.coins ? h.coins : m.coins ? m.coins.on : '';
    const lost = new Set([...(h ? h.lost : []), ...arr(m.spells).filter((s) => s.lost).map((s) => s.name)]);
    return {
      hp: pick('hp'), maxHp: pick('maxHp'), ac: pick('ac'), acArmor: pick('acArmor'), armorOn: pick('armorOn'),
      light: pick('light') || '', conc: pick('conc'), conditions: h && h.conditions.length ? h.conditions : arr(m.conditions),
      exhaustion: Math.max(h ? h.exhaustion : 0, m.exhaustion || 0), reaction: pick('reaction'),
      inspiration: pick('inspiration'), freeArmor: pick('freeArmor'), coins, lost,
    };
  }

  const signed = (v) => (isNum(v) ? fmt.signed(v) : '');
  /** "lamp, about 1 h of oil left" -> ["lamp", "about 1 h of oil left"]. */
  function split(s) {
    const t = typeof s === 'string' ? s.trim() : '';
    const i = t.indexOf(',');
    if (i > 0 && i <= 18) return [t.slice(0, i), t.slice(i + 1).trim()];
    return t.length <= 14 ? [t, ''] : ['', t];
  }
  /** "6 sq (9 m)" -> ["9 m", "6 sq"]. */
  function speedParts(s) {
    const m = /^(.*?)\s*\(([^)]*)\)\s*(.*)$/.exec(typeof s === 'string' ? s : '');
    return m ? [m[2], [m[1], m[3]].filter(Boolean).join(' ')] : [s || '', ''];
  }

  function glyph(on, iconName, onText, offText) {
    if (on === null || on === undefined) return '';
    return `<span class="chip glyph ${on ? 'lit' : 'spent'}">${icon(iconName)}<span>${esc(on ? onText : offText)}</span></span>`;
  }

  // ---------- the HUD ----------
  function hudCard(view, m, n) {
    const who = [m.species, m.class, m.background].filter(Boolean).join(' · ');
    const hpOk = isNum(n.hp);
    const stats = [];
    if (isNum(n.ac)) {
      const sub = n.armorOn === true ? 'Mage Armor holds' : isNum(n.acArmor) && n.acArmor !== n.ac ? `with Mage Armor ${fmt.n(n.acArmor)}` : '';
      stats.push(`<div class="stat"><span class="v">${icon('shield')}${esc(fmt.n(n.ac))}</span><span class="label">AC</span>${sub ? `<span class="sub">${esc(sub)}</span>` : ''}</div>`);
    }
    if (m.hitDice) {
      const [hv, hs] = m.hitDice.split(/\s+(?=d\d)/);
      stats.push(`<div class="stat"><span class="v">${icon('d20')}${esc(hv)}</span><span class="label">Hit Dice</span>${hs ? `<span class="sub">${esc(hs)} each</span>` : ''}</div>`);
    }
    if (n.light) {
      const [lv, ls] = split(n.light);
      stats.push(`<div class="stat"><span class="v">${icon('lantern')}${esc(lv || 'lit')}</span><span class="label">Light</span>${ls ? `<span class="sub">${esc(ls)}</span>` : ''}</div>`);
    } else if (view.state && view.state.hud && view.state.hud.known) {
      stats.push(`<div class="stat"><span class="v">${icon('lantern')}none</span><span class="label">Light</span></div>`);
    }
    if (m.speed) {
      const [sv, ss] = speedParts(m.speed);
      stats.push(`<div class="stat"><span class="v">${icon('boots')}${esc(sv)}</span><span class="label">Speed</span>${ss ? `<span class="sub">${esc(ss)}</span>` : ''}</div>`);
    }
    const chips = [];
    chips.push(n.conc ? `<span class="chip open"><span class="k">conc.</span>${esc(n.conc)}</span>` : '<span class="chip quiet">no concentration</span>');
    if (n.conditions.length) for (const c of n.conditions) chips.push(`<span class="chip threat"><span class="k">condition</span>${esc(c)}</span>`);
    else chips.push('<span class="chip quiet">no conditions</span>');
    chips.push(n.exhaustion > 0 ? `<span class="chip threat">exhaustion ${esc(n.exhaustion)}</span>` : '<span class="chip quiet">exhaustion 0</span>');
    chips.push(glyph(n.reaction, 'hand', 'reaction free', 'reaction used'));
    chips.push(glyph(n.inspiration, 'spark', 'Heroic Inspiration ready', 'Heroic Inspiration spent'));
    chips.push(glyph(n.freeArmor, 'shield', 'free Mage Armor ready', 'free Mage Armor used'));
    if (n.coins) chips.push(`<span class="chip">${icon('coins')}<span>${esc(n.coins)} on him</span></span>`);
    return `<div class="card mhud">`
      + `<h3>${icon('hat')}${esc(m.name || 'Morten')}${who ? ` <small>${esc(who)}</small>` : ''}</h3>`
      + `<div class="hpbig">${icon('heart')}${bar(n.hp, n.maxHp)}<b>${hpOk ? esc(isNum(n.maxHp) ? `${fmt.n(n.hp)} / ${fmt.n(n.maxHp)} HP` : fmt.hp(n.hp)) : '? HP'}</b></div>`
      + (stats.length ? `<div class="stat-row">${stats.join('')}</div>` : '')
      + `<div class="chips">${chips.filter(Boolean).join('')}</div>`
      + '</div>';
  }

  // ---------- spells ----------
  function spellChip(s, n, freeArmor) {
    const lost = n.lost.has(s.name);
    const free = !lost && freeArmor === true && /^mage armor$/i.test(s.name);
    const bits = [];
    if (s.level > 0) bits.push(`L${s.level}`);
    if (isNum(s.dc)) bits.push(`DC ${fmt.n(s.dc)}`);
    if (s.conc) bits.push('conc.');
    if (s.ritual) bits.push('ritual');
    if (free) bits.push('free once a day');
    const cls = ['spell', lost ? 'lost' : '', s.conc ? 'conc' : '', s.ritual ? 'ritual' : '', free ? 'free' : ''].filter(Boolean).join(' ');
    const key = `spell:${s.name}`;
    return `<button type="button" class="${cls}" data-pick="${esc(key)}" aria-pressed="${picked === key}"${lost ? ` aria-label="${esc(`${s.name}, lost, back after a Long Rest`)}"` : ''}>`
      + `<span class="nm">${esc(s.name)}</span>${bits.length ? `<small>${esc(bits.join(' · '))}</small>` : ''}`
      + (lost ? '<small class="back">back after a Long Rest</small>' : '')
      + '</button>';
  }

  function lineBox(title, sub, text, lost) {
    return `<div class="sline" role="note"><b>${esc(title)}</b>${sub ? ` <small>${esc(sub)}</small>` : ''}${text ? `<p>${esc(text)}</p>` : ''}${lost ? '<p class="bad">Lost: back after a Long Rest.</p>' : ''}</div>`;
  }

  function group(label, list, m, n) {
    if (!list.length) return '';
    const pickedHere = list.find((s) => picked === `spell:${s.name}`);
    let line = '';
    if (pickedHere) {
      const s = pickedHere;
      const sub = [s.level ? `level ${s.level}` : 'cantrip', isNum(s.dc) ? `cast DC ${s.dc}` : '', s.time, s.range, s.conc ? 'concentration' : '', s.ritual ? 'ritual' : '', s.note].filter(Boolean).join(' · ');
      line = lineBox(s.name, sub, s.line, n.lost.has(s.name));
    }
    return `<span class="label">${label}</span><div class="spells">${list.map((s) => spellChip(s, n, n.freeArmor)).join('')}</div>${line}`;
  }

  function spellsCard(m, n) {
    const spells = arr(m.spells);
    const feats = arr(m.features);
    const ar = feats.find((f) => /arcane recovery/i.test(f.name));
    if (!spells.length && !ar) return '';
    const cantrips = spells.filter((s) => s.level === 0 && s.prepared);
    const prepared = spells.filter((s) => s.level > 0 && s.prepared);
    const book = spells.filter((s) => !s.prepared);
    const sub = [isNum(m.spellAttack) ? `cast d20 ${fmt.signed(m.spellAttack)} vs DC 10 + level` : '', isNum(m.saveDc) ? `save DC ${m.saveDc}` : ''].filter(Boolean).join(' · ');
    let arHtml = '';
    if (ar) {
      const ready = /ready|unused|free/i.test(ar.state);
      const key = `feat:${ar.name}`;
      arHtml = `<div class="arow"><button type="button" class="chip glyph arc ${ready ? 'lit' : 'spent'}" data-pick="${esc(key)}" aria-pressed="${picked === key}">${icon('spark')}<span>${esc(ar.name)} ${ready ? 'ready' : esc(ar.state || 'used')}</span></button></div>`
        + (picked === key ? lineBox(ar.name, ar.state, ar.line, false) : '');
    }
    const lostN = spells.filter((s) => n.lost.has(s.name)).length;
    return `<div class="card mspells">`
      + `<h3>${icon('spark')}Spells${sub ? ` <small>${esc(sub)}</small>` : ''}</h3>`
      + group(`Cantrips${cantrips[0] && isNum(cantrips[0].dc) ? ` · DC ${esc(cantrips[0].dc)}` : ''}`, cantrips, m, n)
      + group(`Prepared${lostN ? ` · ${esc(fmt.plural(lostN, 'spell'))} lost, back after a Long Rest` : ' · a lost one comes back after a Long Rest'}`, prepared, m, n)
      + group('In the book, not prepared · rituals need no roll', book, m, n)
      + arHtml
      + '<p class="muted hint">Tap a spell for its one line.</p>'
      + '</div>';
  }

  // ---------- fighting ----------
  function fightingCard(m) {
    const atk = arr(m.attacks);
    const ab = arr(m.abilities);
    const sk = arr(m.skills);
    if (!atk.length && !ab.length && !sk.length) return '';
    const stats = [];
    const add = (v, label, sub) => { if (v !== '' && v !== null && v !== undefined) stats.push(`<div class="stat"><span class="v">${esc(v)}</span><span class="label">${label}</span>${sub ? `<span class="sub">${esc(sub)}</span>` : ''}</div>`); };
    add(m.initiative, 'Initiative');
    add(isNum(m.passivePerception) ? m.passivePerception : '', 'Passive Perc.');
    const [sv, ss] = speedParts(m.speed);
    add(sv, 'Speed', ss);
    add(isNum(m.spellAttack) ? fmt.signed(m.spellAttack) : '', 'Spell attack');
    add(isNum(m.saveDc) ? m.saveDc : '', 'Save DC');
    add(isNum(m.prof) ? fmt.signed(m.prof) : '', 'Proficiency');
    return `<div class="card mfight">`
      + `<h3>${icon('sword')}Fighting</h3>`
      + (atk.length ? `<div class="atks" role="table" aria-label="Attacks"><div class="atk head" role="row"><span role="columnheader">Attack</span><span role="columnheader">To hit</span><span role="columnheader">Damage · range</span></div>${atk.map((a) => `<div class="atk" role="row"><b role="cell">${esc(a.name)}</b><span class="hit" role="cell">${esc(a.hit)}</span><span class="dmg" role="cell">${esc([a.damage, a.range].filter(Boolean).join(' · '))}</span></div>`).join('')}</div>` : '')
      + (ab.length ? `<span class="label">Abilities and saves</span><div class="stat-row abil">${ab.map((a) => `<div class="stat${a.saveProf ? ' prof' : ''}"><span class="v">${esc(fmt.n(a.score))} <small class="muted">${esc(signed(a.mod))}</small></span><span class="label">${esc(a.key)}</span>${isNum(a.save) ? `<span class="sub">save ${esc(fmt.signed(a.save))}${a.saveProf ? ' ✦' : ''}</span>` : ''}</div>`).join('')}</div>` : '')
      + (sk.length ? `<span class="label">Skills</span><div class="chips skills">${sk.map((s) => `<span class="chip">${esc(s.name)} <b class="num">${esc(signed(s.mod))}</b></span>`).join('')}</div>` : '')
      + (stats.length ? `<div class="stat-row">${stats.join('')}</div>` : '')
      + '</div>';
  }

  // ---------- gear ----------
  function pips(count) {
    if (!isNum(count) || count < 2 || count > 12) return '';
    return `<span class="pips" aria-hidden="true">${'<i></i>'.repeat(count)}</span>`;
  }
  const kg = (v) => (isNum(v) ? `${fmt.n(Math.round(v * 100) / 100)} kg` : '');

  function gearCard(m) {
    const gear = arr(m.gear);
    const load = m.load;
    const coins = m.coins || { on: '', purse: '' };
    const trader = arr(m.trader);
    if (!gear.length && !load && !coins.on && !trader.length) return '';
    let loadHtml = '';
    if (load && isNum(load.kg) && isNum(load.max) && load.max > 0) {
      const r = load.kg / load.max;
      const pct = Math.max(0, Math.min(100, Math.round(r * 100)));
      loadHtml = `<div class="load"><span class="label">Load</span><span class="bar load-bar ${r > 1 ? 'low' : r > 0.75 ? 'mid' : ''}" role="img" aria-label="${esc(`${fmt.n(load.kg)} of ${fmt.n(load.max)} kg`)}"><i style="width:${pct}%"></i></span><b>${esc(`${fmt.n(load.kg)} of ${fmt.n(load.max)} kg`)}</b></div>`;
    }
    const rows = gear.map((g) => {
      const total = isNum(g.kg) ? (isNum(g.count) ? g.kg * g.count : g.kg) : null;
      const ct = isNum(g.count) && g.count !== 1 ? `×${fmt.n(g.count)}` : g.count === 0 ? 'none left' : '';
      return `<span class="nm${g.count === 0 ? ' none' : ''}">${esc(g.name)} ${pips(g.count)}${g.note ? `<small>${esc(g.note)}</small>` : ''}</span><span class="kg">${esc(total === null ? '—' : kg(total))}</span><span class="ct">${esc(ct)}</span>`;
    }).join('');
    const coinRows = [];
    if (coins.on) coinRows.push(`<span class="nm">On him <small>lost if he dies</small></span><span class="kg"></span><span class="ct">${esc(coins.on)}</span>`);
    if (coins.purse) coinRows.push(`<span class="nm">The purse in the tower</span><span class="kg"></span><span class="ct">${esc(coins.purse)}</span>`);
    const sub = load && isNum(load.kg) && isNum(load.max) ? `${fmt.n(load.kg)} of ${fmt.n(load.max)} kg` : '';
    return `<div class="card mgear">`
      + `<h3>${icon('bag')}Gear${sub ? ` <small>${esc(sub)}</small>` : ''}</h3>`
      + loadHtml
      + (gear.length ? `<div class="inv">${rows}</div>` : '')
      + (coinRows.length ? `<div class="inv"><span class="label">${icon('coins')} Coins</span>${coinRows.join('')}</div>` : '')
      + (trader.length ? `<div class="inv trader"><span class="label">${icon('cart')} The trader, while he is home</span>${trader.map((t) => `<span class="nm">${esc(t.name)}</span><span class="kg"></span><span class="ct">${esc(t.price)}</span>`).join('')}</div>` : '')
      + '</div>';
  }

  // ---------- progress and habits ----------
  function progressCard(m, view) {
    const xp = isNum(m.xp) ? m.xp : view.state ? view.state.xp : null;
    const next = m.nextXp;
    const level = isNum(m.level) ? m.level : view.state ? view.state.level : null;
    if (!isNum(xp) && !isNum(level)) return '';
    const pct = isNum(xp) && isNum(next) && next > 0 ? Math.max(0, Math.min(100, Math.round((xp / next) * 100))) : 0;
    const chips = [];
    if (isNum(level)) chips.push(`<span class="chip">level ${esc(level)}</span>`);
    if (isNum(xp) && isNum(next) && next > xp && isNum(level)) chips.push(`<span class="chip">level ${esc(level + 1)} in ${esc(fmt.xp(next - xp))}</span>`);
    chips.push(`<span class="chip">${icon('skull')}<span>${esc(fmt.plural(m.deaths || 0, 'death'))}</span></span>`);
    chips.push(m.familiar ? `<span class="chip"><span class="k">familiar</span>${esc(m.familiar)}</span>` : '<span class="chip quiet">no familiar</span>');
    return `<div class="card mprog">`
      + `<h3>${icon('flag')}Progress</h3>`
      + (isNum(xp) ? `<div class="hpbig xp">${icon('spark')}<span class="bar xp-bar" role="img" aria-label="${esc(`${fmt.n(xp)} of ${fmt.n(next)} XP`)}"><i style="width:${pct}%"></i></span><b>${esc(isNum(next) ? `${fmt.n(xp)} of ${fmt.n(next)} XP` : fmt.xp(xp))}</b></div>` : '')
      + `<div class="chips">${chips.join('')}</div>`
      + '</div>';
  }

  function habitsCard(m, view) {
    const habits = m.habits && m.habits.length ? m.habits : view.state ? view.state.table.habits : [];
    return `<div class="card mhabits">`
      + `<h3>${icon('book')}Habits <small>his standing orders</small></h3>`
      + (habits.length ? `<ul class="bullets">${habits.map((h) => `<li>${esc(h)}</li>`).join('')}</ul>` : '<p class="muted">None set yet.</p>')
      + '<button type="button" class="toggle" data-go="table">Change them on the Table tab</button>'
      + '</div>';
  }

  function featuresCard(m) {
    const feats = arr(m.features).filter((f) => !/arcane recovery/i.test(f.name));
    if (!feats.length) return '';
    const k = 'features';
    return `<details class="card mfeat" data-mfold="${k}"${opened.has(k) ? ' open' : ''}><summary>${icon('chev')}<span>Features</span> <small>${esc(fmt.plural(feats.length, 'feature'))}</small></summary>`
      + feats.map((f) => `<div class="feat">${icon('spark')}<span><b>${esc(f.name)}</b> ${esc(f.line)}</span><span class="st">${esc(f.state === 'always' ? '' : f.state)}</span></div>`).join('')
      + '</details>';
  }

  function render(view) {
    if (!box) return;
    const m = view.morten;
    if (!m) {
      put(box, `<div class="card"><h3>${icon('hat')}Morten</h3><p class="muted">${view.loaded.morten || view.db !== 'ok' ? 'No sheet yet: it arrives with the GM\'s first write to the table.' : 'Opening his sheet…'}</p></div>`);
      return;
    }
    const n = now(view);
    put(box, hudCard(view, m, n) + spellsCard(m, n) + fightingCard(m) + gearCard(m) + progressCard(m, view) + habitsCard(m, view) + featuresCard(m));
  }

  T.panels.morten = {
    mount(el) {
      box = el;
      el.addEventListener('click', (ev) => {
        const t = ev.target && ev.target.closest ? ev.target : null;
        if (!t) return;
        const p = t.closest('[data-pick]');
        if (p) {
          const k = p.getAttribute('data-pick');
          picked = picked === k ? null : k;
          if (T.app && T.app.render) T.app.render();
          return;
        }
        const g = t.closest('[data-go]');
        if (g && T.app && T.app.go) T.app.go(g.getAttribute('data-go'));
      });
      el.addEventListener('toggle', (ev) => {
        const d = ev.target;
        if (!d || !d.matches || !d.matches('details[data-mfold]')) return;
        const k = d.getAttribute('data-mfold');
        if (d.open) opened.add(k); else opened.delete(k);
      }, true);
    },
    render,
  };
})();
