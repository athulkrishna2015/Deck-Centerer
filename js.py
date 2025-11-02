from __future__ import annotations
from typing import Optional
import json

def make_scroll_js(deck_id: Optional[int], deck_name: Optional[str], center: bool, highlight: bool) -> str:
    # Choose block behavior identical to current behavior
    behavior_block = "center" if center else "nearest"

    return """
(() => {
  const deckId = %s;
  const deckName = %s;
  const doHighlight = %s;

  const selectors = deckId != null ? [
    `[data-did="${deckId}"]`,
    `[data-deck-id="${deckId}"]`,
    `#deck-${deckId}`,
    `[id$="-${deckId}"]`,
    `[data-node-id="${deckId}"]`
  ] : [];

  function findById() {
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    // Some builds put the id on a child; scan common containers
    const nodes = Array.from(document.querySelectorAll("li, div, a, span"));
    for (const n of nodes) {
      const ds = n.dataset || {};
      if (String(ds.did) === String(deckId) ||
          String(ds.deckId) === String(deckId) ||
          String(ds.nodeId) === String(deckId)) {
        return n;
      }
    }
    return null;
  }

  function findByName() {
    if (!deckName) return null;
    const want = String(deckName).trim();
    const parts = want.split("::");
    const last = parts[parts.length - 1];

    const candidates = Array.from(document.querySelectorAll("li, div, a, span"));

    // Exact full-path text match
    for (const n of candidates) {
      const t = (n.textContent || "").trim();
      if (t === want) return n;
    }

    // Then try last component or suffix match
    for (const n of candidates) {
      const t = (n.textContent || "").trim();
      if (t === last || t.endsWith(" " + last)) return n;
    }

    return null;
  }

  const target = findById() || findByName();
  if (!target) return false;

  let row = target.closest("li, .deck, .row, .tree-item") || target;

  try {
    row.scrollIntoView({ block: "%s", inline: "nearest" });
  } catch {
    row.scrollIntoView();
  }

  if (doHighlight) {
    try {
      row.classList.add("last-deck-focus");
      const style = document.createElement("style");
      style.textContent = `.last-deck-focus { outline: 2px solid #3fa; outline-offset: 2px; }`;
      document.documentElement.appendChild(style);
      setTimeout(() => row.classList.remove("last-deck-focus"), 1200);
    } catch {}
  }

  return true;
})();
""" % (
        json.dumps(deck_id),
        json.dumps(deck_name or None),
        "true" if highlight else "false",
        behavior_block,
    )
