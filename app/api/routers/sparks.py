"""Sparks (F06) and meetings (F08-lite, F10, F13, F14)."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from .. import db as db_mod
from ..models import (ClosureRequest, RespondRequest, SparkRequest,
                      TicksRequest)
from ..rules import closure as closure_mod
from ..rules import sparks as sparks_mod
from ..rules.sparks import SparkError

router = APIRouter()


def get_conn():
    conn = db_mod.connect()
    try:
        yield conn
    finally:
        conn.close()


def _raise(err: SparkError):
    raise HTTPException(err.status_code, err.detail)


@router.get("/talents/{talent_id}/sparks")
def talent_sparks(talent_id: str, conn=Depends(get_conn)):
    sparks_mod.expire_overdue(conn)
    conn.commit()
    rows = conn.execute(
        "SELECT * FROM spark WHERE talent_id=? ORDER BY created_at, id",
        (talent_id,)).fetchall()
    return [sparks_mod.spark_to_dict(r) for r in rows]


@router.post("/sparks", status_code=201)
def send_spark(body: SparkRequest, conn=Depends(get_conn)):
    try:
        spark = sparks_mod.send_spark(conn, body.talent_id, body.card_id,
                                      body.claim_id, body.requirement_id,
                                      body.note)
    except SparkError as e:
        _raise(e)
    db_mod.audit(conn, "human", "spark_sent",
                 f"talent={body.talent_id} card={body.card_id} spark={spark['id']}")
    conn.commit()
    return spark


@router.get("/companies/{company_id}/sparks")
def company_sparks(company_id: str, conn=Depends(get_conn)):
    if not conn.execute("SELECT 1 FROM company WHERE id=?",
                        (company_id,)).fetchone():
        raise HTTPException(404, f"unknown company {company_id}")
    sparks_mod.expire_overdue(conn)
    conn.commit()

    by_requirement, pending = [], 0
    cards = conn.execute(
        "SELECT id FROM challenge_card WHERE company_id=?", (company_id,)).fetchall()
    for card_row in cards:
        reqs = conn.execute(
            "SELECT * FROM card_requirement WHERE card_id=? ORDER BY position",
            (card_row["id"],)).fetchall()
        for r in reqs:
            entries = []
            srows = conn.execute(
                "SELECT s.*, t.pseudonym FROM spark s"
                " JOIN talent t ON t.id = s.talent_id"
                " WHERE s.requirement_id=? AND s.status != 'refunded'"
                " ORDER BY s.deadline, s.id", (r["id"],)).fetchall()
            for s in srows:
                claim = conn.execute(
                    "SELECT id,text,quote,esco_uri,esco_label,evidence_level,"
                    "confirmed,original_language,translated FROM evidence_claim"
                    " WHERE id=?", (s["claim_id"],)).fetchone()
                claim_d = dict(claim) if claim else None
                if claim_d:
                    claim_d["confirmed"] = bool(claim_d["confirmed"])
                    claim_d["translated"] = bool(claim_d["translated"])
                    # A company sees the work evidence, not the talent's source
                    # language before mutual interest; that detail can bias review.
                    claim_d.pop("original_language", None)
                    claim_d.pop("translated", None)
                e = {"id": s["id"], "pseudonym": s["pseudonym"],
                     "claim": claim_d, "status": s["status"],
                     "deadline": s["deadline"]}
                if s["note"]:
                    e["note"] = s["note"]
                if s["status"] == "sent":
                    pending += 1
                entries.append(e)
            by_requirement.append({
                "requirement": {k: r[k] for k in
                                ("id", "text", "how_we_check", "esco_uri",
                                 "esco_label")},
                "sparks": entries,
            })
    return {"by_requirement": by_requirement,
            "minutes_estimate": pending * 2}


@router.post("/sparks/{spark_id}/respond")
def respond_spark(spark_id: str, body: RespondRequest, conn=Depends(get_conn)):
    try:
        spark = sparks_mod.respond(conn, spark_id, body.decision,
                                   body.reason_chip)
    except SparkError as e:
        _raise(e)
    db_mod.audit(conn, "human", f"spark_{body.decision}ed",
                 f"spark={spark_id}")
    conn.commit()
    return spark


@router.get("/companies/{company_id}/meetings")
def company_meetings(company_id: str, conn=Depends(get_conn)):
    rows = conn.execute(
        "SELECT m.id, m.spark_id, m.slot, m.card_id, i.name AS talent_name"
        " FROM meeting m JOIN talent_identity i ON i.talent_id = m.talent_id"
        " WHERE m.company_id=? ORDER BY m.slot, m.id", (company_id,)).fetchall()
    return [dict(r) for r in rows]


def _sheet(conn, meeting_id: str):
    m = conn.execute("SELECT * FROM meeting WHERE id=?", (meeting_id,)).fetchone()
    if not m:
        raise HTTPException(404, f"unknown meeting {meeting_id}")
    reqs = conn.execute(
        "SELECT id,text,how_we_check FROM card_requirement WHERE card_id=?"
        " ORDER BY position", (m["card_id"],)).fetchall()
    ticks = {t["requirement_id"]: t for t in conn.execute(
        "SELECT requirement_id,seen,note FROM conversation_tick WHERE meeting_id=?",
        (meeting_id,))}
    return {
        "meeting_id": meeting_id,
        "questions": [{"requirement_id": r["id"], "question": r["text"],
                       "how_we_check": r["how_we_check"]} for r in reqs],
        "ticks": [{"requirement_id": r["id"],
                   "seen": bool(ticks[r["id"]]["seen"]) if r["id"] in ticks else False,
                   **({"note": ticks[r["id"]]["note"]}
                      if r["id"] in ticks and ticks[r["id"]]["note"] else {})}
                  for r in reqs],
    }


@router.get("/meetings/{meeting_id}/sheet")
def get_sheet(meeting_id: str, conn=Depends(get_conn)):
    return _sheet(conn, meeting_id)


@router.post("/meetings/{meeting_id}/ticks")
def post_ticks(meeting_id: str, body: TicksRequest, conn=Depends(get_conn)):
    sheet = _sheet(conn, meeting_id)  # 404 if unknown
    allowed = {q["requirement_id"] for q in sheet["questions"]}
    if any(t.requirement_id not in allowed for t in body.ticks):
        raise HTTPException(422, "ticks must use requirements from this meeting card")
    for t in body.ticks:
        conn.execute(
            "INSERT OR REPLACE INTO conversation_tick (meeting_id,requirement_id,"
            "seen,note) VALUES (?,?,?,?)",
            (meeting_id, t.requirement_id, int(t.seen), t.note))
    db_mod.audit(conn, "human", "meeting_ticks",
                 f"meeting={meeting_id} seen={sum(1 for t in body.ticks if t.seen)}")
    conn.commit()
    return _sheet(conn, meeting_id)


@router.post("/meetings/{meeting_id}/closure")
def post_closure(meeting_id: str, body: ClosureRequest, conn=Depends(get_conn)):
    m = conn.execute("SELECT * FROM meeting WHERE id=?", (meeting_id,)).fetchone()
    if not m:
        raise HTTPException(404, f"unknown meeting {meeting_id}")
    card = db_mod.get_card(conn, m["card_id"])
    try:
        closure_mod.validate_chips(card, body.reason_chips)
    except closure_mod.ChipError as e:
        raise HTTPException(422, {"detail": str(e), "allowed": e.allowed})

    company = conn.execute("SELECT name FROM company WHERE id=?",
                           (m["company_id"],)).fetchone()
    ident = conn.execute("SELECT name FROM talent_identity WHERE talent_id=?",
                         (m["talent_id"],)).fetchone()
    redirect = None
    if body.redirect_company_id:
        r = conn.execute("SELECT name FROM company WHERE id=?",
                         (body.redirect_company_id,)).fetchone()
        redirect = r["name"] if r else None

    banner = closure_mod.support_banner_for(body.outcome)
    message = closure_mod.build_message(
        company["name"], ident["name"] if ident else None, card, body.outcome,
        body.reason_chips, body.next_step, redirect)

    n = conn.execute("SELECT COUNT(*) AS c FROM closure").fetchone()["c"] + 1
    cid = f"clz-{n:03d}"
    while conn.execute("SELECT 1 FROM closure WHERE id=?", (cid,)).fetchone():
        n += 1
        cid = f"clz-{n:03d}"
    conn.execute(
        "INSERT INTO closure (id,meeting_id,outcome,reason_chips,next_step,"
        "redirect_company_id,message_to_talent,support_banner)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (cid, meeting_id, body.outcome, json.dumps(body.reason_chips),
         body.next_step, body.redirect_company_id, message, banner))
    db_mod.audit(conn, "human", "closure_recorded",
                 f"meeting={meeting_id} outcome={body.outcome}")
    conn.commit()

    closure = {"id": cid, "meeting_id": meeting_id, "outcome": body.outcome,
               "reason_chips": body.reason_chips}
    if body.next_step:
        closure["next_step"] = body.next_step
    if body.redirect_company_id:
        closure["redirect_company_id"] = body.redirect_company_id
    out = {"closure": closure, "message_to_talent": message}
    if banner:
        out["support_banner"] = banner
    return out
