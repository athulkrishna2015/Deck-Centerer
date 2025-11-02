from __future__ import annotations
from typing import Optional, Any, Dict
from aqt import mw
from aqt.qt import QTimer
from .config import get_values, get_cfg, save_cfg
from .constants import CFG_KEY_ID, CFG_KEY_NAME
from .js import make_scroll_js

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

def scroll_to_saved_deck_in(deck_browser: Any) -> None:
    if not deck_browser or not getattr(deck_browser, "web", None):
        return

    deck_id, deck_name, center, highlight, retry_ms, max_tries = get_values()
    js = make_scroll_js(deck_id, deck_name, center, highlight)

    tries = {"n": 0}

    def attempt():
        def _cb(ok: Any = None) -> None:
            found = str(ok).lower().strip() == "true"
            if found:
                return
            tries["n"] += 1
            if tries["n"] < max_tries:
                QTimer.singleShot(retry_ms, lambda: deck_browser.web.evalWithCallback(js, _cb))

        deck_browser.web.evalWithCallback(js, _cb)

    QTimer.singleShot(retry_ms, attempt)
