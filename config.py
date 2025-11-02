from __future__ import annotations
from typing import Any, Optional, Dict
from aqt import mw
from .constants import (
    CFG_KEY_ID, CFG_KEY_NAME, CFG_KEY_CENTER, CFG_KEY_HIGHLIGHT,
    CFG_KEY_RETRY_MS, CFG_KEY_MAX_TRIES, DEFAULTS
)

def get_cfg() -> Dict[str, Any]:
    # Coerce None to {} if no config shipped
    return mw.addonManager.getConfig(__name__) or {}

def save_cfg(cfg: Dict[str, Any]) -> None:
    mw.addonManager.writeConfig(__name__, cfg)

def ensure_defaults() -> Dict[str, Any]:
    cfg = get_cfg()
    # Do not prefill user-specific IDs or names beyond None
    for k, v in DEFAULTS.items():
        cfg.setdefault(k, v)
    save_cfg(cfg)
    return cfg

def get_values():
    cfg = ensure_defaults()
    deck_id: Optional[int] = cfg.get(CFG_KEY_ID)
    deck_name: Optional[str] = cfg.get(CFG_KEY_NAME)
    center: bool = bool(cfg.get(CFG_KEY_CENTER, True))
    highlight: bool = bool(cfg.get(CFG_KEY_HIGHLIGHT, True))  # NEW
    retry_ms: int = int(cfg.get(CFG_KEY_RETRY_MS, 120))
    max_tries: int = int(cfg.get(CFG_KEY_MAX_TRIES, 15))
    return deck_id, deck_name, center, highlight, retry_ms, max_tries
