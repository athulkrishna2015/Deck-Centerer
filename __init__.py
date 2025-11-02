from __future__ import annotations
from .hooks import register_hooks
from .legacy import register_legacy
from .settings import register_config_action  # NEW

def _setup():
    # Register modern hooks
    register_hooks()
    # Register legacy compatibility
    from .hooks import _on_deck_browser_did_render
    register_legacy(_on_deck_browser_did_render)
    # Register the Config button handler (robust to 0/1 args)
    register_config_action()  # NEW

_setup()
