from __future__ import annotations

from typing import Any, Tuple

from aqt import gui_hooks
from aqt.deckbrowser import DeckBrowser  # type: ignore

from .config import ensure_defaults
from .decks import (
    remember_current_deck,
    scroll_to_saved_deck_in,
    install_toggle_guard,
    should_skip,
    mark_skip_for,
)


def _on_profile_did_open() -> None:
    ensure_defaults()


def _on_state_did_change(new_state: str, old_state: str) -> None:
    if new_state in ("overview", "review"):
        remember_current_deck()


def _on_deck_browser_did_render(deck_browser: Any) -> None:
    # Always ensure guard is present on the fresh DOM
    install_toggle_guard(deck_browser)
    # Skip scrolling if a recent toggle was detected
    if should_skip():
        return
    scroll_to_saved_deck_in(deck_browser)


def _on_webview_msg(handled: Tuple[bool, Any], message: str, context: Any) -> Tuple[bool, Any]:
    # Accept our message only from the Deck Browser context
    if message != "ldc_mark_skip":
        return handled
    try:
        if not isinstance(context, DeckBrowser):
            return handled
    except Exception:
        return handled
    mark_skip_for(1500)
    return (True, None)


def register_hooks() -> None:
    gui_hooks.profile_did_open.append(_on_profile_did_open)
    gui_hooks.state_did_change.append(_on_state_did_change)
    gui_hooks.deck_browser_did_render.append(_on_deck_browser_did_render)
    gui_hooks.webview_did_receive_js_message.append(_on_webview_msg)
