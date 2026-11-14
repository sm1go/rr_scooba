"""Resident endpoints: saved jobs, applications, help requests (spec 3)."""

from __future__ import annotations

import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from .. import auth as auth_mod
from .. import db as db_mod
from ..db import get_conn
from ..models import ApplicationIn, HelpRequestIn
from ..serialize import application_out, help_request_out
from ..serialize import CONDITION_KEYS

router = APIRouter(prefix="/api", tags=["resident"])

MAX_ACTIVE_APPLICATIONS = 5
_ACTIVE = ("sent", "interview")


def _resident(user) -> None:
    if user["role"] != "resident":
        raise HTTPException(403, "This is not available for your account.")


# --- saved jobs -----------------------------------------------------------------

@router.get("/me/saved")
def list_saved(conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(auth_mod.current_user)):
    _resident(user)
    from ..serialize import job_out
    rows = conn.execute(
        "SELECT j.* FROM saved_job s JOIN job j ON j.id = s.job_id"
        " WHERE s.user_id=? ORDER BY j.title", (user["id"],)).fetchall()
    return {"jobs": [job_out(conn, r) for r in rows]}


@router.put("/me/saved/{job_id}", status_code=204)
def save_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn),
             user=Depends(auth_mod.current_user)):
    _resident(user)
    if not conn.execute("SELECT 1 FROM job WHERE id=?", (job_id,)).fetchone():
        raise HTTPException(404, "Job not found.")
    conn.execute("INSERT OR IGNORE INTO saved_job (user_id,job_id)"
                 " VALUES (?,?)", (user["id"], job_id))
    conn.commit()
    return None


@router.delete("/me/saved/{job_id}", status_code=204)
def unsave_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(auth_mod.current_user)):
    _resident(user)
    conn.execute("DELETE FROM saved_job WHERE user_id=? AND job_id=?",
                 (user["id"], job_id))
    conn.commit()
    return None


# --- applications ---------------------------------------------------------------

def _create_application(conn: sqlite3.Connection, payload: ApplicationIn,
                        *, user=None, by_advisor: bool = False) -> dict:
    job = conn.execute("SELECT * FROM job WHERE id=?",
                       (payload.job_id,)).fetchone()
    if not job or job["status"] != "open":
        raise HTTPException(409, "This job is not open for applications.")
    open_hiring = "open_hiring" in json.loads(job["commitments"] or "[]")
    if not open_hiring and not payload.answer.strip():
        raise HTTPException(422, "The answer to the question is empty.")
    if job["cv_required"] and not (payload.cv_text or "").strip():
        raise HTTPException(422, "This job asks for a CV text.")
    bad = [k for k in payload.shared_needs if k not in CONDITION_KEYS]
    if bad:
        raise HTTPException(422, "Unknown shared_needs keys.")

    if by_advisor:
        if not payload.consent:
            raise HTTPException(422, "The person's consent is required.")
        name = (payload.name or "").strip()
        if not name:
            raise HTTPException(422, "The person's name is required.")
        user_id = payload.user_id
    else:
        _resident(user)
        name = user["name"]
        user_id = user["id"]
        if conn.execute("SELECT 1 FROM application WHERE job_id=? AND user_id=?",
                        (payload.job_id, user["id"])).fetchone():
            raise HTTPException(409, "You have already applied to this job.")
        active = conn.execute(
            "SELECT COUNT(*) c FROM application WHERE user_id=? AND status IN"
            " ('sent','interview')", (user["id"],)).fetchone()["c"]
        if active >= MAX_ACTIVE_APPLICATIONS:
            raise HTTPException(
                409, "You have 5 open applications. Withdraw one or wait for "
                     "an answer.")

    app_id = db_mod.new_id(conn, "ap")
    conn.execute(
        "INSERT INTO application (id,job_id,user_id,name,contact_method,"
        "contact_value,availability_note,answer,cv_text,shared_needs,"
        "meet_at_event,meets_must_haves,wants_tryout,contract_eligible,"
        "shared_credentials,shared_event_records,status,"
        "created_by_advisor)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (app_id, payload.job_id, user_id, name, payload.contact_method,
         payload.contact_value, payload.availability_note, payload.answer,
         payload.cv_text if not open_hiring else None,
         json.dumps(payload.shared_needs, ensure_ascii=False),
         int(payload.meet_at_event), int(payload.meets_must_haves),
         int(payload.wants_tryout),
         int(payload.contract_eligible) if job["contract_id"] else 0,
         json.dumps(_credential_snapshot(conn, user_id)
                    if payload.share_credentials else []),
         json.dumps(_event_records_snapshot(conn, user_id)
                    if getattr(payload, "share_event_records", False) else []),
         "sent", int(by_advisor)))
    db_mod.audit(conn, (user["id"] if user else "advisor"),
                 "application_created",
                 f"{app_id}:job={payload.job_id}"
                 + (":by_advisor" if by_advisor else ""))
    conn.commit()
    return application_out(conn, conn.execute(
        "SELECT * FROM application WHERE id=?", (app_id,)).fetchone())


@router.post("/applications", status_code=201)
def create_application(payload: ApplicationIn,
                       conn: sqlite3.Connection = Depends(get_conn),
                       user=Depends(auth_mod.current_user)):
    return _create_application(conn, payload, user=user)


@router.get("/me/applications")
def my_applications(conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(auth_mod.current_user)):
    _resident(user)
    rows = conn.execute(
        "SELECT * FROM application WHERE user_id=? ORDER BY created_at DESC",
        (user["id"],)).fetchall()
    return {"applications": [application_out(conn, r) for r in rows]}


@router.post("/applications/{app_id}/withdraw")
def withdraw_application(app_id: str,
                         conn: sqlite3.Connection = Depends(get_conn),
                         user=Depends(auth_mod.current_user)):
    _resident(user)
    row = conn.execute("SELECT * FROM application WHERE id=?",
                       (app_id,)).fetchone()
    if not row or row["user_id"] != user["id"]:
        raise HTTPException(404, "Application not found.")
    if row["status"] not in _ACTIVE:
        raise HTTPException(409, "This application already has an answer.")
    conn.execute(
        "UPDATE application SET status='withdrawn', updated_at=datetime('now')"
        " WHERE id=?", (app_id,))
    db_mod.audit(conn, user["id"], "application_status",
                 f"{app_id}:withdrawn")
    conn.commit()
    return application_out(conn, conn.execute(
        "SELECT * FROM application WHERE id=?", (app_id,)).fetchone())


def _credential_snapshot(conn: sqlite3.Connection,
                         user_id: str) -> list[dict]:
    return [{"label": r["label"], "checked_at": r["checked_at"]}
            for r in conn.execute(
                "SELECT label,checked_at FROM credential WHERE user_id=?"
                " ORDER BY checked_at DESC", (user_id,))]


def _event_records_snapshot(conn: sqlite3.Connection,
                            user_id: str) -> list[dict]:
    """'Seen at the event' record: employer, date, observed items."""
    out = []
    for r in conn.execute(
            "SELECT t.employer_id, e.name employer, t.talked_at, t.observed"
            " FROM event_talk t JOIN employer e ON e.id=t.employer_id"
            " WHERE t.user_id=? AND t.observed != '[]'"
            " ORDER BY t.talked_at DESC", (user_id,)):
        out.append({"employer": r["employer"], "date": r["talked_at"][:10],
                    "observed": json.loads(r["observed"])})
    return out


@router.get("/me/event-records")
def my_event_records(conn: sqlite3.Connection = Depends(get_conn),
                     user=Depends(auth_mod.current_user)):
    _resident(user)
    return {"records": _event_records_snapshot(conn, user["id"])}


@router.get("/me/credentials")
def my_credentials(conn: sqlite3.Connection = Depends(get_conn),
                   user=Depends(auth_mod.current_user)):
    _resident(user)
    return {"credentials": [dict(r) for r in conn.execute(
        "SELECT id,label,checked_at,advisor_id FROM credential"
        " WHERE user_id=? ORDER BY checked_at DESC", (user["id"],))]}


@router.delete("/me/credentials/{cred_id}", status_code=204)
def delete_credential(cred_id: str,
                      conn: sqlite3.Connection = Depends(get_conn),
                      user=Depends(auth_mod.current_user)):
    _resident(user)
    cur = conn.execute("DELETE FROM credential WHERE id=? AND user_id=?",
                       (cred_id, user["id"]))
    if cur.rowcount == 0:
        raise HTTPException(404, "Document not found.")
    conn.commit()


# --- help requests --------------------------------------------------------------

def _create_help_request(conn: sqlite3.Connection, payload: HelpRequestIn,
                         user) -> dict:
    if payload.kind == "check_document":
        if not user:
            raise HTTPException(401, "Sign in to continue.")
        if not payload.document_label.strip():
            raise HTTPException(422, "Tell us which document you have.")
    if not payload.consent:
        raise HTTPException(422, "Please tick the consent box so an advisor "
                                 "can contact you.")
    if payload.job_id and not conn.execute(
            "SELECT 1 FROM job WHERE id=?", (payload.job_id,)).fetchone():
        raise HTTPException(422, "Unknown job.")
    bad = [k for k in payload.condition_keys if k not in CONDITION_KEYS]
    if bad:
        raise HTTPException(422, "Unknown condition keys.")
    if user:
        name = user["name"]
        contact_method = payload.contact_method
        contact_value = payload.contact_value
        if not contact_method or not contact_value:
            prof = conn.execute(
                "SELECT contact_method FROM resident_profile WHERE user_id=?",
                (user["id"],)).fetchone()
            contact_method = contact_method or (prof["contact_method"]
                                                if prof else None)
            contact_value = contact_value or user["email"] or user["phone"]
        if not contact_method or not contact_value:
            raise HTTPException(422, "Give a way for the advisor to reach you.")
    else:
        name = (payload.name or "").strip()
        contact_method = payload.contact_method
        contact_value = (payload.contact_value or "").strip()
        if not name or not contact_method or not contact_value:
            raise HTTPException(422, "Without an account we need your name and "
                                     "a way to reach you.")
    hr_id = db_mod.new_id(conn, "hr")
    conn.execute(
        "INSERT INTO help_request (id,user_id,name,contact_method,"
        "contact_value,job_id,kind,condition_keys,document_label,"
        "message,consent) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (hr_id, user["id"] if user else None, name, contact_method,
         contact_value, payload.job_id, payload.kind,
         json.dumps(payload.condition_keys, ensure_ascii=False),
         payload.document_label.strip(), payload.message, 1))
    db_mod.audit(conn, (user["id"] if user else "anonymous"),
                 "help_request_created", f"{hr_id}:{payload.kind}")
    conn.commit()
    return help_request_out(conn.execute(
        "SELECT * FROM help_request WHERE id=?", (hr_id,)).fetchone())


@router.post("/help-requests", status_code=201)
def create_help_request(payload: HelpRequestIn,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(auth_mod.optional_user)):
    """Works with or without an account — residents, employers
    (asking for help with a job post) and anonymous callers."""
    if user and user["role"] not in ("resident", "employer", "advisor"):
        raise HTTPException(403, "This is not available for your account.")
    return _create_help_request(conn, payload, user)


@router.get("/me/help-requests")
def my_help_requests(conn: sqlite3.Connection = Depends(get_conn),
                     user=Depends(auth_mod.current_user)):
    _resident(user)
    rows = conn.execute(
        "SELECT * FROM help_request WHERE user_id=?"
        " ORDER BY created_at DESC", (user["id"],)).fetchall()
    return {"help_requests": [help_request_out(r) for r in rows]}
