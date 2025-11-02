from __future__ import annotations
from typing import Any
from aqt import gui_hooks
from .config import ensure_defaults
from .decks import remember_current_deck, scroll_to_saved_deck_in

def _on_profile_did_open() -> None:
    ensure_defaults()

def _on_state_did_change(new_state: str, old_state: str) -> None:
    if new_state in ("overview", "review"):
        remember_current_deck()

def _on_deck_browser_did_render(deck_browser: Any) -> None:
    scroll_to_saved_deck_in(deck_browser)

def register_hooks() -> None:
    gui_hooks.profile_did_open.append(_on_profile_did_open)
    gui_hooks.state_did_change.append(_on_state_did_change)
    gui_hooks.deck_browser_did_render.append(_on_deck_browser_did_render)
