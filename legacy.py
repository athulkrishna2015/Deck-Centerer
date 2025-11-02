from __future__ import annotations
from typing import Any
from aqt import mw

def register_legacy(deck_render_cb) -> None:
    try:
        from anki.hooks import addHook  # type: ignore
    except Exception:
        return

    def _legacy_deck_browser_did_render(*args, **kwargs):
        db = kwargs.get("deck_browser", None) or getattr(mw, "deckBrowser", None)
        if db:
            deck_render_cb(db)

    try:
        addHook("deckBrowserDidRender", _legacy_deck_browser_did_render)
    except Exception:
        pass
