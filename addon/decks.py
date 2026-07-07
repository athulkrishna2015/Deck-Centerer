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

# Override targets when expanding or collapsing
_override_deck_id: Optional[int] = None
_override_deck_name: Optional[str] = None
_override_until_ts: float = 0.0


def set_temporary_override(deck_id: Optional[str], deck_name: Optional[str]) -> None:
    global _override_deck_id, _override_deck_name, _override_until_ts
    try:
        _override_deck_id = int(deck_id) if deck_id else None
    except ValueError:
        _override_deck_id = None
    _override_deck_name = deck_name
    _override_until_ts = time.time() + 2.5



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


def get_toggle_guard_script() -> str:
    """Return the toggle guard JavaScript to be injected into the deck browser HTML."""
    try:
        _, _, _, _, _, _, center_on_toggle = get_values()
        center_on_toggle_js = "true" if center_on_toggle else "false"
    except Exception:
        center_on_toggle_js = "true"

    return f"""
    (() => {{
      try {{ localStorage.setItem('ldcCenterOnToggle', '{center_on_toggle_js}'); }} catch(e) {{}}

      // Intercept window.scrollTo to prevent visual layout flashes during Anki's render lifecycle
      let done = false;
      const doCustomScroll = () => {{
        if (done) return;
        done = true;

        if (window.__ldc_original_scrollTo) {{
          window.scrollTo = window.__ldc_original_scrollTo;
        }}

        try {{
          const centerOnToggle = localStorage.getItem('ldcCenterOnToggle') !== 'false';
          const toggleDeckId = localStorage.getItem('ldcToggleDeckId');
          const toggleDeckName = localStorage.getItem('ldcToggleDeckName');
          let scrolled = false;

          if (centerOnToggle && (toggleDeckId || toggleDeckName)) {{
            const selectors = toggleDeckId ? [
              `[data-did="${{toggleDeckId}}"]`,
              `[data-deck-id="${{toggleDeckId}}"]`,
              `#deck-${{toggleDeckId}}`,
              `[id$="-${{toggleDeckId}}"]`,
              `[data-node-id="${{toggleDeckId}}"]`,
            ] : [];

            let target = null;
            if (toggleDeckId) {{
              const elById = document.getElementById(toggleDeckId);
              if (elById) target = elById.closest('tr') || elById;
              if (!target) {{
                const elByOpen = document.querySelector(`a.deck[onclick="return pycmd('open:${{toggleDeckId}}')"]`);
                if (elByOpen) target = elByOpen.closest('tr') || elByOpen;
              }}
              if (!target) {{
                for (const sel of selectors) {{
                  const el = document.querySelector(sel);
                  if (el) {{
                    target = el.closest('tr') || el;
                    break;
                  }}
                }}
              }}
            }}
            if (!target && toggleDeckName) {{
              const want = toggleDeckName.trim();
              const candidates = Array.from(document.querySelectorAll('a.deck, li, div, a, span'));
              for (const n of candidates) {{
                if ((n.textContent || "").trim() === want) {{
                  target = n.closest('tr') || n;
                  break;
                }}
              }}
            }}

            if (target) {{
              target.scrollIntoView({{ behavior: 'auto', block: 'center', inline: 'nearest' }});
              scrolled = true;
            }}
          }}

          if (!scrolled) {{
            const savedScroll = localStorage.getItem('ldcScrollY');
            if (savedScroll !== null) {{
              if (window.__ldc_original_scrollTo) {{
                window.__ldc_original_scrollTo(0, parseInt(savedScroll, 10));
              }} else {{
                window.scrollTo(0, parseInt(savedScroll, 10));
              }}
            }}
          }}
        }} catch (e) {{}}
      }};

      try {{
        const raw = localStorage.getItem('ldcSkipUntil');
        const until = raw ? parseInt(raw, 10) : 0;
        if (until && Date.now() < until) {{
          if (!window.__ldc_original_scrollTo) {{
            window.__ldc_original_scrollTo = window.scrollTo;
          }}
          window.scrollTo = function(x, y) {{
            doCustomScroll();
          }};
          setTimeout(doCustomScroll, 0);
        }}
      }} catch (e) {{}}

      if (window.__ldc_guard_installed) {{ return; }}
      window.__ldc_guard_installed = true;
      let lastMarkTime = 0;
      const toggleSelector = '[aria-expanded], a.collapse, .expand, .expander, .caret, .toggle, .collapse-toggle, .deck-collapse, .tree-item .collapse, .tree-item .expander, [onclick*="collapse"], [onclick*="toggle"]';

      const persist = (ms=1500) => {{
        const until = Date.now() + ms;
        try {{ localStorage.setItem('ldcSkipUntil', String(until)); }} catch(e) {{}}
        try {{ if (typeof pycmd === 'function') {{ pycmd('ldc_mark_skip'); }} }} catch(e) {{}}
      }};

      const mark = () => {{
        persist(2500);
        try {{
          localStorage.setItem('ldcScrollY', String(window.scrollY || document.documentElement.scrollTop));
        }} catch(e) {{}}
      }};

      const isToggleTarget = (node) => {{
        if (!node) return false;
        let curr = node;
        while (curr && curr !== document && curr.nodeType === 1) {{
          const onclickAttr = curr.getAttribute('onclick') || '';
          if (onclickAttr.includes('collapse:') || onclickAttr.includes('toggle:')) {{
            return true;
          }}
          const cls = curr.className || '';
          if (typeof cls === 'string' && (
            cls.includes('collapse') || 
            cls.includes('expand') || 
            cls.includes('expander') || 
            cls.includes('caret') || 
            cls.includes('toggle') || 
            cls.includes('arrow')
          )) {{
            return true;
          }}
          if (curr.hasAttribute('aria-expanded')) {{
            return true;
          }}
          curr = curr.parentNode;
        }}

        try {{
          const txt = (node.textContent || "").trim();
          if (txt === "+" || txt === "-" || txt === "−" || txt === "▸" || txt === "▾" || txt === "▶" || txt === "▼") {{
            return true;
          }}
        }} catch (e) {{}}

        return false;
      }};

      const detectAndMarkToggle = (t) => {{
        if (!t) return;
        if (!isToggleTarget(t)) return;

        const now = Date.now();
        if (now - lastMarkTime < 250) return;
        lastMarkTime = now;

        let deckId = "";
        let deckName = "";
        let curr = t;
        while (curr && curr !== document && curr.nodeType === 1) {{
          const did = curr.getAttribute('data-did') || curr.getAttribute('data-deck-id') || (curr.dataset && (curr.dataset.did || curr.dataset.deckId));
          if (did) {{
            deckId = did;
            break;
          }}
          const idAttr = curr.getAttribute('id') || '';
          const match = idAttr.match(/deck-(\\d+)/) || idAttr.match(/-(\\d+)$/);
          if (match) {{
            deckId = match[1];
            break;
          }}
          curr = curr.parentNode;
        }}

        const row = t.closest ? (t.closest('tr') || t.closest('li') || t.closest('.deck-row')) : null;
        if (row) {{
          const deckLink = row.querySelector('a.deck');
          if (deckLink) {{
            deckName = (deckLink.textContent || "").trim();
          }}
        }}

        try {{
          if (deckId || deckName) {{
            localStorage.setItem('ldcToggleDeckId', deckId);
            localStorage.setItem('ldcToggleDeckName', deckName);
          }} else {{
            localStorage.removeItem('ldcToggleDeckId');
            localStorage.removeItem('ldcToggleDeckName');
          }}
        }} catch(e) {{}}

        if (deckId || deckName) {{
          try {{
            if (typeof pycmd === 'function') {{
              pycmd('ldc_mark_toggle:' + deckId + ':' + deckName);
            }}
          }} catch(e) {{}}
        }}
        mark();
      }};

      // Mouse/pointer/touch toggles
      const onClick = (e) => {{
        const t = e.target;
        if (t) {{ detectAndMarkToggle(t); }}
      }};
      document.addEventListener('click', onClick, true);

      // Keyboard toggles (left/right, enter, space, vim h/l)
      document.addEventListener('keydown', (e) => {{
        const k = e.key;
        const focus = document.activeElement || e.target;
        if ((k === 'ArrowLeft' || k === 'ArrowRight' || k === 'Enter' || k === ' ' || k === 'h' || k === 'l')) {{
          if (focus && isToggleTarget(focus)) {{
            detectAndMarkToggle(focus);
          }} else if (e.target && isToggleTarget(e.target)) {{
            detectAndMarkToggle(e.target);
          }}
        }}
      }}, true);

      // Mutation observer for aria-expanded flips (programmatic toggles)
      try {{
        const mo = new MutationObserver((recs) => {{
          for (const r of recs) {{
            if (r.type === 'attributes' && r.attributeName === 'aria-expanded') {{ mark(); break; }}
          }}
        }});
        mo.observe(document.body, {{ subtree: true, attributes: true, attributeFilter: ['aria-expanded'] }});
      }} catch (e) {{}}
    }})();
    """


def install_toggle_guard(deck_browser: Any) -> None:
    """Inject a guard that marks a skip window on expand/collapse by mouse, keyboard, or aria-expanded mutations, persisting across re-renders."""
    if not deck_browser or not getattr(deck_browser, "web", None):
        return
    try:
        deck_browser.web.eval(get_toggle_guard_script())
    except Exception:
        pass


def scroll_to_saved_deck_in(deck_browser: Any) -> None:
    if not deck_browser or not getattr(deck_browser, "web", None):
        return

    deck_id, deck_name, center, highlight, retry_ms, max_tries, center_on_toggle = get_values()
    is_override = (time.time() < _override_until_ts) and center_on_toggle
    if is_override:
        deck_id = _override_deck_id
        deck_name = _override_deck_name
        center = True
        highlight = False

    if deck_id is None and not deck_name:
        return
    js = make_scroll_js(deck_id, deck_name, center, highlight, is_override=is_override)

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
