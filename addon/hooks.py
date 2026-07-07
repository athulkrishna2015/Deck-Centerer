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
    set_temporary_override,
    get_toggle_guard_script,
)


def get_addon_version() -> str:
    import json
    from pathlib import Path
    try:
        addon_dir = Path(__file__).resolve().parent
        manifest_path = addon_dir / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                return str(manifest.get("version", "2.2.1"))
    except Exception:
        pass
    return "2.2.1"


def check_addon_update() -> None:
    from aqt import mw
    from aqt.qt import QTimer
    from .config import get_cfg, save_cfg

    addon_package = __name__.split(".")[0]
    meta = mw.addonManager.addonMeta(addon_package)
    if meta.get("supporter_opt_out", False):
        return

    current_ver = get_addon_version()
    cfg = get_cfg()
    last_ver = cfg.get("last_version", "")

    if current_ver != last_ver:
        cfg["last_version"] = current_ver
        save_cfg(cfg)

        from .settings import open_settings
        QTimer.singleShot(2000, lambda: open_settings(select_support_tab=True))


def _on_profile_did_open() -> None:
    ensure_defaults()
    check_addon_update()


def _on_state_did_change(new_state: str, old_state: str) -> None:
    if new_state in ("overview", "review"):
        remember_current_deck()


def _on_deck_browser_did_render(deck_browser: Any) -> None:
    # Always ensure guard is present on the fresh DOM
    install_toggle_guard(deck_browser)

    import time
    from .decks import _override_until_ts
    # If a temporary override is active (meaning user expanded/collapsed a subdeck),
    # the synchronous HTML script has already centered it instantly. We skip the python scroll fallback.
    if time.time() < _override_until_ts:
        return

    # Skip scrolling if a recent toggle was detected and no override is active
    if should_skip():
        return
    scroll_to_saved_deck_in(deck_browser)


def _on_webview_msg(handled: Tuple[bool, Any], message: str, context: Any) -> Tuple[bool, Any]:
    if message == "ldc_mark_skip":
        mark_skip_for(2500)
        return (True, None)
    elif message.startswith("ldc_mark_toggle:"):
        parts = message.split(":")
        toggle_deck_id = parts[1] if len(parts) > 1 and parts[1] else None
        toggle_deck_name = parts[2] if len(parts) > 2 and parts[2] else None
        set_temporary_override(toggle_deck_id, toggle_deck_name)
        return (True, None)
    return handled


def _on_deck_browser_will_render_content(deck_browser: Any, content: Any) -> None:
    try:
        content.tree += f"\n<script>{get_toggle_guard_script()}</script>"
    except Exception:
        pass


def register_hooks() -> None:
    gui_hooks.profile_did_open.append(_on_profile_did_open)
    gui_hooks.state_did_change.append(_on_state_did_change)
    gui_hooks.deck_browser_will_render_content.append(_on_deck_browser_will_render_content)
    gui_hooks.deck_browser_did_render.append(_on_deck_browser_did_render)
    gui_hooks.webview_did_receive_js_message.append(_on_webview_msg)
