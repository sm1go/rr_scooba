"""Talent side (F04): profile, story interview, own-words evidence cards."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from .. import db as db_mod
from .. import llm
from ..models import EvidenceRequest, ExtractRequest, FollowupsRequest
from ..rules import sparks as sparks_mod

router = APIRouter()


def get_conn():
    conn = db_mod.connect()
    try:
        yield conn
    finally:
        conn.close()


def _talent_or_404(conn, talent_id: str):
    t = conn.execute("SELECT * FROM talent WHERE id=?", (talent_id,)).fetchone()
    if not t:
        raise HTTPException(404, f"unknown talent {talent_id}")
    return t


def _evidence_card(conn, talent_id: str) -> dict:
    t = _talent_or_404(conn, talent_id)
    card_row = conn.execute(
        "SELECT headline FROM evidence_card WHERE talent_id=?",
        (talent_id,)).fetchone()
    claims = [dict(r) for r in conn.execute(
        "SELECT id,text,quote,esco_uri,esco_label,evidence_level,confirmed,"
        "original_language,translated FROM evidence_claim"
        " WHERE talent_id=? AND confirmed=1 ORDER BY id", (talent_id,))]
    for c in claims:
        c["confirmed"] = bool(c["confirmed"])
        c["translated"] = bool(c["translated"])
    return {
        "talent_id": t["id"], "pseudonym": t["pseudonym"],
        "headline": card_row["headline"] if card_row else "",
        "claims": claims,
        "languages": json.loads(t["languages"] or "[]"),
        "availability": t["availability"],
    }


@router.get("/talents/{talent_id}")
def get_talent(talent_id: str, conn=Depends(get_conn)):
    t = _talent_or_404(conn, talent_id)
    return {
        "id": t["id"], "pseudonym": t["pseudonym"],
        "languages": json.loads(t["languages"] or "[]"),
        "availability": t["availability"],
        "spark_budget": sparks_mod.spark_budget(conn),
        "sparks_used": sparks_mod.sparks_used(conn, talent_id),
    }


@router.post("/story/followups")
def story_followups(body: FollowupsRequest, conn=Depends(get_conn)):
    _talent_or_404(conn, body.talent_id)
    result = llm.story_followups(body.talent_id, body.transcript, body.language)
    db_mod.audit(conn, "ai", "story_followups",
                 f"talent={body.talent_id} provider={result['provider']} "
                 f"questions={len(result['questions'])}")
    conn.commit()
    return result


@router.post("/story/extract")
def story_extract(body: ExtractRequest, conn=Depends(get_conn)):
    _talent_or_404(conn, body.talent_id)
    result = llm.story_extract(body.talent_id, body.transcript, body.language)
    conn.execute("DELETE FROM evidence_proposal WHERE talent_id=?",
                 (body.talent_id,))
    for claim in result["claims"]:
        proposal_id = f"{body.talent_id}:{claim['id']}"
        conn.execute(
            "INSERT INTO evidence_proposal (id,talent_id,payload,created_at)"
            " VALUES (?,?,?,datetime('now'))",
            (proposal_id, body.talent_id,
             json.dumps(claim, ensure_ascii=False, sort_keys=True)))
    db_mod.audit(conn, "ai", "story_extract",
                 f"talent={body.talent_id} provider={result['provider']} "
                 f"claims={len(result['claims'])} refused={len(result['refused'])}")
    conn.commit()
    return result


@router.post("/evidence/{talent_id}")
def save_evidence(talent_id: str, body: EvidenceRequest, conn=Depends(get_conn)):
    _talent_or_404(conn, talent_id)
    posted = body.claims
    confirmed = [c for c in posted if c.confirmed]
    allowed_esco = {s["uri"]: s["label"] for s in llm._load_esco()}
    for claim in confirmed:
        proposal = conn.execute(
            "SELECT payload FROM evidence_proposal WHERE id=? AND talent_id=?",
            (f"{talent_id}:{claim.id}", talent_id)).fetchone()
        if not proposal:
            raise HTTPException(422, "claim was not proposed by this story session")
        expected = json.loads(proposal["payload"])
        candidate = claim.model_dump()
        candidate["confirmed"] = False
        if candidate != expected:
            raise HTTPException(422, "claim content must match the checked proposal")
        if claim.esco_uri and allowed_esco.get(claim.esco_uri) != claim.esco_label:
            raise HTTPException(422, "skill label does not match the local skill catalogue")
    conn.execute(
        "INSERT OR IGNORE INTO evidence_card (talent_id,headline) VALUES (?, '')",
        (talent_id,))
    # Remove stale unconfirmed claims unless an existing Spark still references
    # them; those stay out of pool counts and cannot power new Sparks.
    kept_ids = {c.id for c in confirmed}
    existing = conn.execute(
        "SELECT id FROM evidence_claim WHERE talent_id=?", (talent_id,)
    ).fetchall()
    for row in existing:
        if row["id"] in kept_ids:
            continue
        referenced = conn.execute(
            "SELECT 1 FROM spark WHERE claim_id=? LIMIT 1", (row["id"],)
        ).fetchone()
        if referenced:
            conn.execute(
                "UPDATE evidence_claim SET confirmed=0 WHERE id=?", (row["id"],)
            )
        else:
            conn.execute("DELETE FROM evidence_claim WHERE id=?", (row["id"],))
    for c in confirmed:
        conn.execute(
            "INSERT INTO evidence_claim (id,talent_id,text,quote,esco_uri,esco_label,"
            "evidence_level,confirmed,original_language,translated)"
            " VALUES (?,?,?,?,?,?,?,1,?,?)"
            " ON CONFLICT(id) DO UPDATE SET text=excluded.text, quote=excluded.quote,"
            "esco_uri=excluded.esco_uri, esco_label=excluded.esco_label,"
            "evidence_level=excluded.evidence_level, confirmed=1,"
            "original_language=excluded.original_language, translated=excluded.translated"
            " WHERE evidence_claim.talent_id=excluded.talent_id",
            (c.id, talent_id, c.text, c.quote, c.esco_uri, c.esco_label,
             c.evidence_level, c.original_language, int(c.translated)))
    conn.execute("DELETE FROM evidence_proposal WHERE talent_id=?", (talent_id,))
    db_mod.audit(conn, "human", "evidence_confirmed",
                 f"talent={talent_id} kept={len(confirmed)} of {len(posted)}")
    conn.commit()
    return _evidence_card(conn, talent_id)


@router.get("/evidence/{talent_id}")
def get_evidence(talent_id: str, conn=Depends(get_conn)):
    return _evidence_card(conn, talent_id)
