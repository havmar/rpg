// window.T: the page's one namespace. Every other file is an IIFE that hangs its exports
// on T: T.store (10), T.model (20), T.ui (30), T.app (40), T.panels.<name> (50 and up).
// This file also holds the few tiny helpers the others share (T.util).
(() => {
  'use strict';
  const T = (window.T = window.T || {});
  T.panels = T.panels || {};
  T.version = 1;

  const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

  T.util = {
    isObj,
    /** document.querySelector, scoped. */
    $: (sel, root = document) => root.querySelector(sel),
    /** document.querySelectorAll as an array. */
    $$: (sel, root = document) => Array.from(root.querySelectorAll(sel)),
    /** Zero-padded id: pad(7) is "0007". */
    pad: (n, width = 4) => String(Math.max(0, Math.trunc(n))).padStart(width, '0'),
    /** Milliseconds for an ISO time or a number; null when it is neither. */
    ms(at) {
      if (typeof at === 'number' && Number.isFinite(at)) return at;
      if (typeof at !== 'string' || !at) return null;
      const t = Date.parse(at);
      return Number.isFinite(t) ? t : null;
    },
    /** Run fn, log and swallow what it throws; returns fn's value or undefined. */
    safe(fn, label) {
      try {
        return fn();
      } catch (err) {
        console.error(`[table] ${label || 'error'}:`, err);
        return undefined;
      }
    },
    /** A short readable message for any thrown value (a DbError, an Error, a string). */
    errText(err) {
      if (!err) return 'unknown error';
      if (typeof err === 'string') return err;
      if (isObj(err) && typeof err.code === 'string') return err.message ? `${err.code}: ${err.message}` : err.code;
      if (err instanceof Error) return err.message;
      return 'unknown error';
    },
    sleep: (ms) => new Promise((r) => setTimeout(r, ms)),
  };
})();
