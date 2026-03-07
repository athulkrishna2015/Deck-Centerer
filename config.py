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
    changed = False
    # Do not prefill user-specific IDs or names beyond None
    for k, v in DEFAULTS.items():
        if k not in cfg:
            cfg[k] = v
            changed = True
    if changed:
        save_cfg(cfg)
    return cfg


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _coerce_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _coerce_optional_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def get_values():
    cfg = ensure_defaults()
    deck_id = _coerce_optional_int(cfg.get(CFG_KEY_ID))
    deck_name = _coerce_optional_str(cfg.get(CFG_KEY_NAME))
    center = _coerce_bool(cfg.get(CFG_KEY_CENTER), DEFAULTS[CFG_KEY_CENTER])
    highlight = _coerce_bool(
        cfg.get(CFG_KEY_HIGHLIGHT), DEFAULTS[CFG_KEY_HIGHLIGHT]
    )
    retry_ms = _coerce_int(
        cfg.get(CFG_KEY_RETRY_MS),
        DEFAULTS[CFG_KEY_RETRY_MS],
        minimum=20,
        maximum=5000,
    )
    max_tries = _coerce_int(
        cfg.get(CFG_KEY_MAX_TRIES),
        DEFAULTS[CFG_KEY_MAX_TRIES],
        minimum=1,
        maximum=100,
    )
    return deck_id, deck_name, center, highlight, retry_ms, max_tries
