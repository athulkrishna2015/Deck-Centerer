from __future__ import annotations

from typing import Optional, Any, Dict
import time

from aqt import mw
from aqt.qt import QTimer

from .config import get_values, get_cfg, save_cfg
from .constants import CFG_KEY_ID, CFG_KEY_NAME
from .js import make_scroll_js

# Python-side skip guard, set by JS via pycmd and auto-expires
_skip_until_ts: float = 0.0


def mark_skip_for(ms: int = 1500) -> None:
    global _skip_until_ts
    _skip_until_ts = time.time() + (ms / 1_000.0)


def should_skip() -> bool:
    return time.time() < _skip_until_ts


def remember_current_deck() -> None:
    if not mw or not mw.col:
        return

    deck: Optional[Dict[str, Any]] = mw.col.decks.current()
    if not deck:
        return

    cfg = get_cfg()
    deck_id = deck.get("id", None)
    deck_name = deck.get("name", None)

    cfg[CFG_KEY_ID] = int(deck_id) if deck_id is not None else None
    cfg[CFG_KEY_NAME] = deck_name or None
    save_cfg(cfg)


def install_toggle_guard(deck_browser: Any) -> None:
    """Inject a guard that marks a skip window on expand/collapse by mouse, keyboard, or aria-expanded mutations, persisting across re-renders."""
    if not deck_browser or not getattr(deck_browser, "web", None):
        return

    script = r"""
    (() => {
      if (window.__ldc_guard_installed) { return; }
      window.__ldc_guard_installed = true;

      const persist = (ms=1500) => {
        const until = Date.now() + ms;
        try { localStorage.setItem('ldcSkipUntil', String(until)); } catch(e) {}
        try { if (typeof pycmd === 'function') { pycmd('ldc_mark_skip'); } } catch(e) {}
      };

      const mark = () => persist(1500);

      // Mouse/pointer/touch toggles
      const onClick = (e) => {
        const t = e.target;
        if (!t) return;
        const toggle = t.closest('[aria-expanded], .collapse, .expand, .expander, .caret, .toggle, .collapse-toggle, .deck-collapse, .tree-item .collapse, .tree-item .expander, li, [role="treeitem"]');
        if (toggle) { mark(); }
      };
      document.addEventListener('click', onClick, true);
      document.addEventListener('pointerdown', onClick, true);
      document.addEventListener('mousedown', onClick, true);

      // Keyboard toggles (arrows, enter, space, vim h/l)
      document.addEventListener('keydown', (e) => {
        const k = e.key;
        if (k === 'ArrowLeft' || k === 'ArrowRight' || k === 'ArrowUp' || k === 'ArrowDown' || k === 'Enter' || k === ' ' || k === 'h' || k === 'l') {
          mark();
        }
      }, true);

      // Mutation observer for aria-expanded flips (programmatic toggles)
      try {
        const mo = new MutationObserver((recs) => {
          for (const r of recs) {
            if (r.type === 'attributes' && r.attributeName === 'aria-expanded') { mark(); break; }
          }
        });
        mo.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['aria-expanded'] });
      } catch (e) {}
    })();
    """
    try:
        deck_browser.web.eval(script)
    except Exception:
        # Best-effort on older builds
        pass


def scroll_to_saved_deck_in(deck_browser: Any) -> None:
    if not deck_browser or not getattr(deck_browser, "web", None):
        return

    deck_id, deck_name, center, highlight, retry_ms, max_tries = get_values()
    js = make_scroll_js(deck_id, deck_name, center, highlight)

    tries = {"n": 0}

    def attempt():
        def _cb(ok: Any = None) -> None:
            try:
                found = str(ok).lower().strip() == "true"
            except Exception:
                found = False

            if found:
                return

            tries["n"] += 1
            if tries["n"] >= max_tries:
                return
            QTimer.singleShot(retry_ms, attempt)

        try:
            deck_browser.web.evalWithCallback(js, _cb)
        except Exception:
            try:
                deck_browser.web.eval(js)
            except Exception:
                pass

    attempt()
