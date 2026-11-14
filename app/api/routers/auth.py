"""Auth endpoints: register, login, logout, /api/me (spec section 3)."""

from __future__ import annotations

import json
import re
import sqlite3

from fastapi import APIRouter, Depends, Header, HTTPException

from .. import auth as auth_mod
from .. import db as db_mod
from ..db import get_conn
from ..models import LoginIn, ProfileIn, RegisterIn

router = APIRouter(prefix="/api", tags=["auth"])

_SAME_401 = "The login or password is wrong, or the account does not exist."
EMAIL_RX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _session(conn: sqlite3.Connection, user_id: str) -> str:
    token = auth_mod.new_token()
    conn.execute("INSERT INTO session (token,user_id) VALUES (?,?)",
                 (token, user_id))
    return token


@router.post("/auth/register", status_code=201)
def register(payload: RegisterIn,
             conn: sqlite3.Connection = Depends(get_conn)):
    """Residents and employers only — advisors are seeded accounts."""
    email = (payload.email or "").strip().lower() or None
    phone = (payload.phone or "").strip() or None
    if not email and not phone:
        raise HTTPException(422, "Give an email or a phone number.")
    if email and not EMAIL_RX.match(email):
        raise HTTPException(422, "The email address does not look right.")
    if len(payload.password) < auth_mod.MIN_PASSWORD_LEN:
        raise HTTPException(422, "The password needs at least 8 characters.")
    if email and conn.execute("SELECT 1 FROM user WHERE lower(email)=?",
                              (email,)).fetchone():
        raise HTTPException(409, "An account with this email already exists.")

    employer_id = None
    if payload.role == "employer":
        if not (payload.employer_name or "").strip():
            raise HTTPException(422, "Give the company or organisation name.")
        employer_id = db_mod.new_id(conn, "emp")
        conn.execute(
            "INSERT INTO employer (id,name,contact_name,contact_email,"
            "contact_phone) VALUES (?,?,?,?,?)",
            (employer_id, payload.employer_name.strip(), payload.name.strip(),
             email or "", phone or ""))

    user_id = db_mod.new_id(conn, "u")
    conn.execute(
        "INSERT INTO user (id,email,phone,password_hash,role,name,employer_id)"
        " VALUES (?,?,?,?,?,?,?)",
        (user_id, email, phone, auth_mod.hash_password(payload.password),
         payload.role, payload.name.strip(), employer_id))
    if payload.role == "resident":
        conn.execute("INSERT INTO resident_profile (user_id) VALUES (?)",
                     (user_id,))
    token = _session(conn, user_id)
    db_mod.audit(conn, user_id, "registered", payload.role)
    conn.commit()
    row = conn.execute("SELECT * FROM user WHERE id=?", (user_id,)).fetchone()
    return {"token": token, "user": auth_mod.user_payload(row, conn)}


@router.post("/auth/login")
def login(payload: LoginIn, conn: sqlite3.Connection = Depends(get_conn)):
    """Email or phone + password. Same 401 whether the login exists or not."""
    row = auth_mod.find_user_by_login(conn, payload.login)
    if not row or not auth_mod.verify_password(payload.password,
                                               row["password_hash"]):
        raise HTTPException(401, _SAME_401)
    token = _session(conn, row["id"])
    db_mod.audit(conn, row["id"], "login")
    conn.commit()
    return {"token": token, "user": auth_mod.user_payload(row, conn)}


@router.post("/auth/logout", status_code=204)
def logout(authorization: str | None = Header(default=None),
           conn: sqlite3.Connection = Depends(get_conn)):
    if authorization and authorization.startswith("Bearer "):
        conn.execute("DELETE FROM session WHERE token=?",
                     (authorization.removeprefix("Bearer ").strip(),))
        conn.commit()
    return None


@router.get("/me")
def me(conn: sqlite3.Connection = Depends(get_conn),
       user=Depends(auth_mod.current_user)):
    return auth_mod.user_payload(user, conn)


# --- profile -------------------------------------------------------------------

def profile_out(conn: sqlite3.Connection, user) -> dict:
    row = conn.execute("SELECT * FROM resident_profile WHERE user_id=?",
                       (user["id"],)).fetchone()
    base = {"contact_method": None, "district": None, "fields": [],
            "availability": [], "max_hours_per_week": None, "needs": [],
            "languages": [], "about": ""}
    if row:
        base.update({"contact_method": row["contact_method"],
                     "district": row["district"],
                     "fields": json.loads(row["fields"] or "[]"),
                     "availability": json.loads(row["availability"] or "[]"),
                     "max_hours_per_week": row["max_hours_per_week"],
                     "needs": json.loads(row["needs"] or "[]"),
                     "languages": json.loads(row["languages"] or "[]"),
                     "about": row["about"],
                     "share_email": bool(row["share_email"]),
                     "share_phone": bool(row["share_phone"]),
                     "public_link": row["public_link"] or ""})
    base["name"] = user["name"]
    base["email"] = user["email"]
    base["phone"] = user["phone"]
    return base


@router.get("/me/profile")
def get_profile(conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(auth_mod.current_user)):
    if user["role"] != "resident":
        raise HTTPException(403, "This is not available for your account.")
    return profile_out(conn, user)


@router.put("/me/profile")
def put_profile(payload: ProfileIn,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(auth_mod.current_user)):
    if user["role"] != "resident":
        raise HTTPException(403, "This is not available for your account.")
    conn.execute(
        "INSERT INTO resident_profile (user_id,contact_method,district,fields,"
        "availability,max_hours_per_week,needs,languages,about)"
        " VALUES (?,?,?,?,?,?,?,?,?)"
        " ON CONFLICT(user_id) DO UPDATE SET contact_method=excluded.contact_method,"
        " district=excluded.district, fields=excluded.fields,"
        " availability=excluded.availability,"
        " max_hours_per_week=excluded.max_hours_per_week,"
        " needs=excluded.needs, languages=excluded.languages,"
        " about=excluded.about",
        (user["id"], payload.contact_method, payload.district,
         json.dumps(payload.fields, ensure_ascii=False),
         json.dumps(payload.availability, ensure_ascii=False),
         payload.max_hours_per_week,
         json.dumps(payload.needs, ensure_ascii=False),
         json.dumps(payload.languages, ensure_ascii=False), payload.about))
    conn.execute(
        "UPDATE resident_profile SET share_email=?, share_phone=?,"
        " public_link=? WHERE user_id=?",
        (1 if payload.share_email else 0,
         1 if payload.share_phone else 0,
         payload.public_link or "", user["id"]))
    if payload.name is not None or payload.email is not None \
            or payload.phone is not None:
        conn.execute(
            "UPDATE user SET name=COALESCE(?,name), email=COALESCE(?,email),"
            " phone=COALESCE(?,phone) WHERE id=?",
            (payload.name,
             (payload.email or "").strip().lower() or None,
             (payload.phone or "").strip() or None, user["id"]))
    db_mod.audit(conn, user["id"], "profile_updated")
    conn.commit()
    row = conn.execute("SELECT * FROM user WHERE id=?", (user["id"],)).fetchone()
    return profile_out(conn, row)


@router.get("/me/export")
def export_me(conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(auth_mod.current_user)):
    """Download of everything stored about the account."""
    data = {"user": auth_mod.user_payload(user, conn)}
    if user["role"] == "resident":
        data["profile"] = profile_out(conn, user)
        data["saved_jobs"] = [r["job_id"] for r in conn.execute(
            "SELECT job_id FROM saved_job WHERE user_id=?", (user["id"],))]
    data["applications"] = [dict(r) for r in conn.execute(
        "SELECT id,job_id,name,contact_method,contact_value,availability_note,"
        "answer,cv_text,shared_needs,meet_at_event,status,status_note,"
        "created_at,updated_at FROM application WHERE user_id=?",
        (user["id"],))]
    for a in data["applications"]:
        a["shared_needs"] = json.loads(a["shared_needs"] or "[]")
    data["help_requests"] = [dict(r) for r in conn.execute(
        "SELECT id,name,contact_method,contact_value,job_id,kind,"
        "condition_keys,message,status,advisor_reply,created_at"
        " FROM help_request WHERE user_id=?", (user["id"],))]
    for h in data["help_requests"]:
        h["condition_keys"] = json.loads(h["condition_keys"] or "[]")
    return data


@router.delete("/me")
def delete_me(conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(auth_mod.current_user)):
    """Removes profile, saved jobs and sessions; applications and help
    requests are anonymised (spec section 3)."""
    conn.execute(
        "UPDATE application SET user_id=NULL, name='Deleted user',"
        " contact_method='', contact_value='', answer='', cv_text=NULL,"
        " shared_needs='[]', availability_note='' WHERE user_id=?",
        (user["id"],))
    conn.execute(
        "UPDATE help_request SET user_id=NULL, name='Deleted user',"
        " contact_method='', contact_value='', message='' WHERE user_id=?",
        (user["id"],))
    conn.execute("DELETE FROM saved_job WHERE user_id=?", (user["id"],))
    conn.execute("DELETE FROM resident_profile WHERE user_id=?", (user["id"],))
    conn.execute("DELETE FROM session WHERE user_id=?", (user["id"],))
    conn.execute("DELETE FROM user WHERE id=?", (user["id"],))
    db_mod.audit(conn, "system", "account_deleted", user["id"])
    conn.commit()
    return {"deleted": True}
