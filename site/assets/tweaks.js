// gemeinwert — Tweaks panel (vanilla JS, no framework).
// Talks to the host shell via window.parent postMessage so the toolbar Tweaks
// toggle works. Outside the host shell it still works as a self-contained UI.

(function () {
  'use strict';

  const DEFAULTS = /*EDITMODE-BEGIN*/{
    "motto": "auto",
    "accent": "gold",
    "pulse": true,
    "density": "default"
  }/*EDITMODE-END*/;

  // If motto is "auto", read from <html lang="..."> on this page so each
  // language landing keeps its own hero copy on first load. The user can
  // still cycle through mottos via the Tweaks panel.
  function resolveAutoMotto() {
    const lang = (document.documentElement.lang || 'en').toLowerCase().slice(0, 2);
    if (lang === 'de' || lang === 'it') return lang;
    return 'en';
  }

  const state = { ...DEFAULTS };
  if (state.motto === 'auto') state.motto = resolveAutoMotto();

  const MOTTOS = {
    en:   { eyebrow: 'GEMEINWERT · BIM CVP · COMMON VALUE PROTOCOL', title: 'The open layer for <em>signed</em> construction.' },
    de:   { eyebrow: 'GEMEINWERT · BIM CVP · COMMON VALUE PROTOCOL', title: 'The open layer for <em>signed</em> construction.' },
    it:   { eyebrow: 'GEMEINWERT · BIM CVP · COMMON VALUE PROTOCOL', title: 'The open layer for <em>signed</em> construction.' },
    short:{ eyebrow: 'GEMEINWERT · BIM CVP', title: '<em>Gemeinwert.</em> Signed.' },
  };

  function persist() {
    try {
      window.parent.postMessage({ type: '__edit_mode_set_keys', edits: { ...state } }, '*');
    } catch (e) { /* not in host */ }
  }

  function applyMotto(key) {
    const m = MOTTOS[key] || MOTTOS.en;
    const eb = document.getElementById('hero-eyebrow');
    const tt = document.getElementById('hero-title');
    if (eb) eb.textContent = m.eyebrow;
    if (tt) tt.innerHTML = m.title;
  }
  function applyAccent(key) {
    document.body.classList.remove('accent-blue', 'accent-cyan', 'accent-orange');
    if (key === 'blue')   document.body.classList.add('accent-blue');
    if (key === 'cyan')   document.body.classList.add('accent-cyan');
    if (key === 'orange') document.body.classList.add('accent-orange');
  }
  function applyPulse(on) {
    document.body.classList.toggle('no-pulse', !on);
  }
  function applyDensity(key) {
    document.body.classList.toggle('density-dense', key === 'dense');
  }

  function applyAll() {
    applyMotto(state.motto);
    applyAccent(state.accent);
    applyPulse(state.pulse);
    applyDensity(state.density);
    syncUi();
  }

  function syncUi() {
    document.querySelectorAll('.tweak-row__controls button').forEach(btn => {
      const group = btn.dataset.group;
      const value = btn.dataset.value;
      const cur = String(state[group]);
      btn.classList.toggle('active', cur === value);
    });
  }

  function setKey(group, value) {
    if (group === 'pulse') value = (value === 'true' || value === true);
    state[group] = value;
    applyAll();
    persist();
  }

  // Build panel UI
  function build() {
    const panel = document.getElementById('tweaks');
    if (!panel) return;
    panel.querySelectorAll('.tweak-row__controls').forEach(row => {
      row.addEventListener('click', e => {
        const b = e.target.closest('button');
        if (!b) return;
        setKey(b.dataset.group, b.dataset.value);
      });
    });
    const close = document.getElementById('tweaks-close');
    if (close) close.addEventListener('click', () => {
      panel.classList.remove('open');
      try { window.parent.postMessage({ type: '__edit_mode_dismissed' }, '*'); } catch (e) {}
    });
  }

  // Host-shell wiring (Tweaks toolbar toggle)
  window.addEventListener('message', (ev) => {
    const t = ev.data && ev.data.type;
    if (t === '__activate_edit_mode')   document.getElementById('tweaks')?.classList.add('open');
    if (t === '__deactivate_edit_mode') document.getElementById('tweaks')?.classList.remove('open');
  });

  document.addEventListener('DOMContentLoaded', () => {
    build();
    applyAll();
    try { window.parent.postMessage({ type: '__edit_mode_available' }, '*'); } catch (e) {}
  });

  // Top-bar date stamp
  document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('today');
    if (!el) return;
    const d = new Date();
    const pad = n => String(n).padStart(2, '0');
    el.textContent = pad(d.getDate()) + '.' + pad(d.getMonth() + 1) + '.' + String(d.getFullYear()).slice(-2);
  });
})();
