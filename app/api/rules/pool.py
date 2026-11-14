"""Pool Proof (F03): banded, k-anonymous counts over consenting registrants.

Only talents with pool_consent=1 and *confirmed* claims count. Counts are never
exposed — only bands ("fewer than 10", "10–19", "20–49", "50+"), k = 10.
"""

from __future__ import annotations

import json
import sqlite3

BANDS = ["fewer than 10", "10–19", "20–49", "50+"]
CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


def band_for(n: int) -> str:
    if n < 10:
        return "fewer than 10"
    if n < 20:
        return "10–19"
    if n < 50:
        return "20–49"
    return "50+"


def _cefr_at_least(level: str, required: str) -> bool:
    try:
        return CEFR_ORDER.index(level) >= CEFR_ORDER.index(required)
    except ValueError:
        return False


def _card_constraints(card: dict) -> tuple[list[dict], list[dict]]:
    """must-haves that constrain the pool (need an ESCO uri) and language needs."""
    musts = [r for r in card.get("must_haves", []) if r.get("esco_uri")]
    langs = card.get("languages", [])
    return musts, langs


def count_pool(conn: sqlite3.Connection, card: dict,
               drop_requirement_id: str | None = None) -> int:
    musts, langs = _card_constraints(card)
    if drop_requirement_id is not None:
        musts = [r for r in musts if r["id"] != drop_requirement_id]

    claims_by_talent: dict[str, set] = {}
    for row in conn.execute(
            "SELECT talent_id, esco_uri FROM evidence_claim WHERE confirmed=1"):
        claims_by_talent.setdefault(row["talent_id"], set()).add(row["esco_uri"])

    n = 0
    for t in conn.execute(
            "SELECT id, languages FROM talent WHERE pool_consent=1"):
        esco_hits = claims_by_talent.get(t["id"], set())
        if any(r["esco_uri"] not in esco_hits for r in musts):
            continue
        t_langs = {l["language"].lower(): l["level"]
                   for l in json.loads(t["languages"] or "[]")}
        ok = True
        for need in langs:
            have = t_langs.get(str(need["language"]).lower())
            if not have or not _cefr_at_least(have, need["level"]):
                ok = False
                break
        if ok:
            n += 1
    return n


def pool_preview(conn: sqlite3.Connection, card: dict) -> dict:
    """Pool shape from the contract: band + elasticity per must-have."""
    band = band_for(count_pool(conn, card))
    elasticity = [{
        "requirement_id": r["id"],
        "text": r["text"],
        "band_without": band_for(count_pool(conn, card, drop_requirement_id=r["id"])),
    } for r in card.get("must_haves", [])]
    return {"band": band, "elasticity": elasticity}
