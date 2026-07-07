from __future__ import annotations

from typing import Optional
import json


def make_scroll_js(
    deck_id: Optional[int],
    deck_name: Optional[str],
    center: bool,
    highlight: bool,
    is_override: bool = False,
) -> str:
    behavior_block = "center" if center else "nearest"
    is_override_js = "true" if is_override else "false"

    return f"""
(() => {{
  const isOverride = {is_override_js};
  if (!isOverride) {{
    // Skip auto-scroll if a prior toggle indicated a skip window; read from localStorage to survive re-render
    try {{
      const raw = localStorage.getItem('ldcSkipUntil');
      const until = raw ? parseInt(raw, 10) : 0;
      if (until && Date.now() < until) {{
        const savedScroll = localStorage.getItem('ldcScrollY');
        if (savedScroll !== null) {{
          window.scrollTo(0, parseInt(savedScroll, 10));
        }}
        return true;
      }}
    }} catch (e) {{}}
  }}

  const deckId = {json.dumps(deck_id)};
  const deckName = {json.dumps(deck_name)};
  const doHighlight = {json.dumps(highlight)};

  const selectors = deckId != null ? [
    `[data-did="${{deckId}}"]`,
    `[data-deck-id="${{deckId}}"]`,
    `#deck-${{deckId}}`,
    `[id$="-${{deckId}}"]`,
    `[data-node-id="${{deckId}}"]`,
  ] : [];

  function normalizeTarget(node) {{
    if (!node) return null;
    return node.closest("tr") || node;
  }}

  function findById() {{
    const byHtmlId = normalizeTarget(document.getElementById(String(deckId)));
    if (byHtmlId) return byHtmlId;

    const byOpenCmd = normalizeTarget(
      document.querySelector(`a.deck[onclick="return pycmd('open:${{deckId}}')"]`)
    );
    if (byOpenCmd) return byOpenCmd;

    for (const sel of selectors) {{
      const el = normalizeTarget(document.querySelector(sel));
      if (el) return el;

      const nodes = Array.from(document.querySelectorAll("tr, li, div, a, span"));
      for (const n of nodes) {{
        const ds = n.dataset || {{}};
        if (String(ds.did) === String(deckId) ||
            String(ds.deckId) === String(deckId) ||
            String(ds.nodeId) === String(deckId)) {{
          return normalizeTarget(n);
        }}
      }}
    }}
    return null;
  }}

  function textOf(node) {{ return (node.textContent || "").trim(); }}

  function findByName() {{
    if (!deckName) return null;
    const want = String(deckName).trim();
    const parts = want.split("::");
    const last = parts[parts.length - 1];

    const candidates = Array.from(document.querySelectorAll("a.deck, li, div, a, span"));

    for (const n of candidates) {{
      if (textOf(n) === want) return normalizeTarget(n);
    }}

    for (const n of candidates) {{
      if (textOf(n) === last) return normalizeTarget(n);
    }}

    return null;
  }}

  let target = null;
  if (deckId != null) {{
    target = findById();
  }}
  if (!target) {{
    target = findByName();
  }}
  if (!target) {{
    return false;
  }}

  try {{
    target.scrollIntoView({{ behavior: "auto", block: "{behavior_block}", inline: "nearest" }});
  }} catch (e) {{}}

  if (doHighlight) {{
    try {{
      const prev = target.style.outline;
      target.style.outline = "2px solid #21a366";
      setTimeout(() => {{ target.style.outline = prev; }}, 1200);
    }} catch (e) {{}}
  }}

  return true;
}})();
"""
