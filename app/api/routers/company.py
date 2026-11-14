"""Company side (F01, F02, F03): event, companies, compiler, lint, pool, cards."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from .. import db as db_mod
from .. import llm
from ..models import (ApproveCardRequest, ChallengeCard, DraftRequest,
                      LintRequest, PoolRequest)
from ..rules import lint as lint_mod
from ..rules import pool as pool_mod
from ..rules.pool import band_for

router = APIRouter()


def get_conn():
    conn = db_mod.connect()
    try:
        yield conn
    finally:
        conn.close()


@router.get("/event")
def get_event(conn=Depends(get_conn)):
    ev = conn.execute("SELECT * FROM event LIMIT 1").fetchone()
    registered = conn.execute("SELECT COUNT(*) AS n FROM talent").fetchone()["n"]
    return {
        "id": ev["id"], "name": ev["name"], "date": ev["date"],
        "format": ev["format"], "companies_declared": ev["companies_declared"],
        "talents_registered_band": band_for(registered),
    }


@router.get("/companies/{company_id}")
def get_company(company_id: str, conn=Depends(get_conn)):
    c = conn.execute("SELECT * FROM company WHERE id=?",
                     (company_id,)).fetchone()
    if not c:
        raise HTTPException(404, f"unknown company {company_id}")
    return {"id": c["id"], "name": c["name"], "size": c["size"],
            "city": c["city"], "contact_name": c["contact_name"],
            "slots": c["slots"]}


@router.post("/compiler/draft")
def compiler_draft(body: DraftRequest, conn=Depends(get_conn)):
    company = conn.execute("SELECT * FROM company WHERE id=?",
                           (body.company_id,)).fetchone()
    if not company:
        raise HTTPException(404, f"unknown company {body.company_id}")
    result = llm.compiler_draft(conn, dict(company), body.text, body.image_base64)
    db_mod.audit(conn, "ai", "compiler_draft",
                 f"company={body.company_id} provider={result['provider']} "
                 f"card={result['card']['id']}")
    conn.commit()
    return result


@router.post("/lint")
def post_lint(body: LintRequest, conn=Depends(get_conn)):
    hints = lint_mod.lint_card(conn, body.card.model_dump())
    db_mod.audit(conn, "ai", "lint_requirements",
                 f"card={body.card.id} hints={len(hints)}")
    conn.commit()
    return {"hints": hints}


@router.post("/pool")
def post_pool(body: PoolRequest, conn=Depends(get_conn)):
    return pool_mod.pool_preview(conn, body.card.model_dump())


@router.post("/cards")
def approve_card(body: ApproveCardRequest, conn=Depends(get_conn)):
    if not conn.execute("SELECT 1 FROM company WHERE id=?",
                        (body.card.company_id,)).fetchone():
        raise HTTPException(404, f"unknown company {body.card.company_id}")
    card = body.card.model_dump()
    card["status"] = "approved"
    db_mod.save_card(conn, card)
    db_mod.audit(conn, "human", "card_approved",
                 f"company={card['company_id']} card={card['id']}")
    conn.commit()
    return db_mod.get_card(conn, card["id"])


@router.get("/cards")
def list_cards(conn=Depends(get_conn)):
    rows = conn.execute(
        "SELECT * FROM challenge_card WHERE status='approved' ORDER BY id").fetchall()
    return [db_mod.card_from_row(conn, r) for r in rows]


@router.get("/cards/{card_id}")
def get_card(card_id: str, conn=Depends(get_conn)):
    card = db_mod.get_card(conn, card_id)
    if not card:
        raise HTTPException(404, f"unknown card {card_id}")
    return card
