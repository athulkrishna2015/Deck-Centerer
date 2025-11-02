from __future__ import annotations

# Config keys
CFG_KEY_ID = "last_deck_id"
CFG_KEY_NAME = "last_deck_name"
CFG_KEY_CENTER = "center_on_scroll"
CFG_KEY_HIGHLIGHT = "show_highlight"  # NEW
CFG_KEY_RETRY_MS = "retry_ms"
CFG_KEY_MAX_TRIES = "max_tries"

# Defaults (mirror config.json)
DEFAULTS = {
    CFG_KEY_ID: None,
    CFG_KEY_NAME: None,
    CFG_KEY_CENTER: True,
    CFG_KEY_HIGHLIGHT: True,  # NEW
    CFG_KEY_RETRY_MS: 120,
    CFG_KEY_MAX_TRIES: 15,
}
