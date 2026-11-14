"""Own-words guard (F04): "no quote, no claim".

Server-side verification for every extracted claim, whatever the LLM said:
  1. the quote must be an exact substring of the transcript;
  2. no inflated verbs — 'led/owned/architected' is refused when the quote only
     supports 'helped/worked on'.
"""

from __future__ import annotations

import re

STRONG_VERBS = [
    "led", "lead", "owned", "own", "architected", "spearheaded", "headed",
    "directed", "drove", "managed", "single-handedly", "masterminded",
    "transformed", "built", "created", "delivered",
]
WEAK_MARKERS = [
    "helped", "helping", "worked on", "worked with", "contributed",
    "assisted", "supported", "participated", "was part of", "joined",
    "took part", "was involved",
]


def _verb_hit(text: str, verbs: list[str]) -> str | None:
    for v in verbs:
        if re.search(rf"\b{re.escape(v)}\b", text):
            return v
    return None


def check_claim(claim_text: str, quote: str, transcript: str) -> str | None:
    """Return a refusal reason, or None if the claim is allowed."""
    if not quote or quote not in transcript:
        return "no quote: the claim's quote is not an exact substring of the transcript"
    strong = _verb_hit(claim_text.lower(), STRONG_VERBS)
    weak = _verb_hit(quote.lower(), WEAK_MARKERS)
    if strong and strong not in quote.lower() and weak:
        return (f"inflated verb: '{strong}' — the quote only supports '{weak}'")
    return None


def guarded_extract(claims: list[dict], transcript: str) -> tuple[list[dict], list[dict]]:
    """Split model-proposed claims into allowed claims and refused proposals."""
    ok, refused = [], []
    for c in claims:
        reason = check_claim(c.get("text", ""), c.get("quote", ""), transcript)
        if reason:
            refused.append({"text": c.get("text", ""), "reason": reason})
        else:
            ok.append(c)
    return ok, refused
