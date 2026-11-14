"""Jobs: public browsing + employer/advisor management (spec section 3)."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db as db_mod
from .. import settings, stations
from ..auth import current_user, optional_user
from ..db import get_conn, SEED_DIR
from ..models import ConditionCheckIn, JobIn, WordingCheckIn
from ..rules import lint
from ..rules.labels import fits_availability, haversine_km, job_labels
from ..serialize import CONDITION_KEYS, conditions_out, job_out

router = APIRouter(prefix="/api", tags=["jobs"])

CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]


def _district_center(district_id: str) -> tuple[float, float] | None:
    cat = json.loads((SEED_DIR / "catalog.json").read_text(encoding="utf-8"))
    d = next((d for d in cat["districts"] if d["id"] == district_id), None)
    return (d["lat"], d["lon"]) if d else None


def _label_ids(job: dict, cond_count: int) -> set[str]:
    return {l["id"] for l in job_labels(job, cond_count)}


def _decode(row: sqlite3.Row) -> dict:
    job = dict(row)
    for f in ("duties", "shifts", "qualifications", "languages"):
        job[f] = json.loads(job[f] or "[]")
    job["schedule_flexible"] = bool(job["schedule_flexible"])
    job["cv_required"] = bool(job["cv_required"])
    return job


@router.get("/jobs")
def list_jobs(
    label: list[str] = Query(default=[]),
    field: str | None = None,
    slots: str | None = None,
    hours_max: int | None = None,
    pay_min: float | None = None,
    pay_unit: str | None = None,
    contract: str | None = None,
    experience: str | None = None,
    work_mode: str | None = None,
    language: str | None = None,
    level_max: str | None = None,
    needs: str | None = None,
    needs_mode: str = "yes",
    district: str | None = None,
    km: float | None = None,
    at_event: int | None = None,
    near_station: int | None = None,
    commute_max: int | None = None,
    q: str | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
    user=Depends(optional_user),   # noqa: ARG001 — output identical either way
):
    """Open jobs, filtered. Same output for anonymous and signed-in callers."""
    rows = conn.execute("SELECT * FROM job WHERE status='open'").fetchall()
    center = _district_center(district) if district else None
    need_keys = [k for k in (needs or "").split(",") if k]
    slot_list = [s for s in (slots or "").split(",") if s]
    want_labels = set(label)
    out = []

    matched: list[sqlite3.Row] = []
    for row in rows:
        job = _decode(row)
        conds = conditions_out(conn, job["id"])
        cond_val = {c["key"]: c["value"] for c in conds}
        known = sum(1 for c in conds if c["value"] != "unknown")

        if want_labels and not want_labels <= _label_ids(job, known):
            continue
        if field and job["field"] != field:
            continue
        if slot_list and not fits_availability(
                job["shifts"], job["schedule_flexible"], slot_list):
            continue
        if hours_max is not None and (job["hours_max"] is None
                                      or job["hours_max"] > hours_max):
            continue
        if pay_min is not None:
            unit = pay_unit or "hour"
            if job["pay_unit"] != unit or job["pay_amount"] is None \
                    or job["pay_amount"] < pay_min:
                continue
        if contract and job["contract"] != contract:
            continue
        if experience and job["experience"] != experience:
            continue
        if work_mode and job["work_mode"] != work_mode:
            continue
        if language and level_max:
            need = next((n for n in job["languages"]
                         if (n.get("language") or "").lower()
                         == language.lower()), None)
            if need and need.get("level") in CEFR \
                    and CEFR.index(need["level"]) > CEFR.index(level_max):
                continue
        if need_keys:
            if needs_mode == "not_no":
                if any(cond_val.get(k) == "no" for k in need_keys):
                    continue
            else:
                if any(cond_val.get(k) != "yes" for k in need_keys):
                    continue
        if center and km is not None:
            if job["work_mode"] != "remote":
                if job["lat"] is None or haversine_km(
                        center[0], center[1], job["lat"], job["lon"]) > km:
                    continue
        if at_event:
            ev = conn.execute("SELECT 1 FROM employer_event WHERE employer_id=?",
                              (job["employer_id"],)).fetchone()
            if not ev:
                continue
        if q:
            emp = conn.execute("SELECT name FROM employer WHERE id=?",
                               (job["employer_id"],)).fetchone()
            hay = " ".join([job["title"], " ".join(job["duties"]),
                            emp["name"] if emp else ""]).lower()
            if q.lower() not in hay:
                continue
        if near_station:
            if job["work_mode"] == "remote" or job["lat"] is None:
                continue
            ns = stations.nearest(job["lat"], job["lon"])
            if not ns or ns["distance_m"] > 800:
                continue
        out.append(job_out(conn, row, center))
        matched.append(row)

    # Commute (§5): with a district chosen, attach the cached estimate to
    # every job (no network). commute_max additionally computes every
    # missing one — up to 5 routing calls in parallel — then filters.
    # Remote jobs and ones we cannot compute keep commute: null and are
    # never filtered out.
    if district:
        from . import commute as commute_mod
        center = _district_center(district)
        commutable = []
        for item, row in zip(out, matched):
            job = _decode(row)
            if job["work_mode"] == "remote" or job["lat"] is None \
                    or not center:
                item["commute"] = None
                continue
            payload = commute_mod.cached_commute(conn, job["id"], district)
            if payload is not None:
                item["commute"] = payload     # absent = "not tried yet"
            else:
                commutable.append((item, job))

        if commute_max is None:
            pass                        # cached values only
        elif not settings.commute_enabled():
            pass                        # no key: nothing to compute
        elif commutable:
            def fetch(job: dict):
                try:
                    return commute_mod.compute_commute_uncached(
                        job, district, center)
                except Exception as e:
                    logger.warning("commute failed for job %s: %s",
                                   job["id"], e)
                    return None
            # batches of 5 parallel calls, a short pause between batches
            # so a cold cache doesn't hammer the routing service
            todo = [j for _, j in commutable]
            payloads = []
            with ThreadPoolExecutor(max_workers=5) as pool:
                for i in range(0, len(todo), 5):
                    payloads.extend(pool.map(fetch, todo[i:i + 5]))
                    if i + 5 < len(todo):
                        time.sleep(0.2)
            for (item, job), payload in zip(commutable, payloads):
                if payload is not None:
                    commute_mod.store_commute(conn, job["id"], district,
                                              payload)
                item["commute"] = payload
            conn.commit()

        if commute_max is not None:
            out = [j for j in out
                   if j.get("commute") is None
                   or j["commute"].get("minutes") is None
                   or j["commute"]["minutes"] <= commute_max]
    elif commute_max is not None:
        raise HTTPException(422,
                            "commute_max needs a district to start from.")

    out.sort(key=lambda j: j["title"])
    out.sort(key=lambda j: j["confirmed_at"] or "", reverse=True)
    return {"jobs": out, "count": len(out)}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn),
            user=Depends(optional_user)):
    row = conn.execute("SELECT * FROM job WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found.")
    if row["status"] != "open":
        allowed = user and (user["role"] == "advisor"
                            or (user["role"] == "employer"
                                and user["employer_id"] == row["employer_id"]))
        if not allowed:
            raise HTTPException(404, "Job not found.")
    return job_out(conn, row)


# --- writes --------------------------------------------------------------------

def _job_fields(payload: JobIn) -> dict:
    d = payload.model_dump(exclude={"conditions", "employer_id"})
    for f in ("duties", "shifts", "qualifications", "languages"):
        d[f] = json.dumps(d[f], ensure_ascii=False)
    d["schedule_flexible"] = int(d["schedule_flexible"])
    d["cv_required"] = int(d["cv_required"])
    return d


def _check_owner(conn, user, row) -> None:
    if user["role"] == "advisor":
        return
    if user["role"] == "employer" and user["employer_id"] == row["employer_id"]:
        return
    raise HTTPException(403, "This is not your job.")


def _write_job_conditions(conn: sqlite3.Connection, job_id: str,
                          conditions: dict, writer: str) -> None:
    """Employer writes never overwrite an advisor row unless the value
    changes — then the source becomes the writer again (spec 3.5)."""
    for key, val in (conditions or {}).items():
        if key not in CONDITION_KEYS:
            continue
        row = conn.execute("SELECT * FROM job_condition WHERE job_id=? AND key=?",
                           (job_id, key)).fetchone()
        if val == "unknown":
            if row and row["source"] != "advisor":
                conn.execute("DELETE FROM job_condition WHERE job_id=? AND key=?",
                             (job_id, key))
            continue
        if row and row["value"] == val:
            continue                              # nothing changes
        conn.execute(
            "INSERT OR REPLACE INTO job_condition (job_id,key,value,source,"
            "checked_at,note) VALUES (?,?,?,?,?,?)",
            (job_id, key, val, writer, date.today().isoformat(), ""))


@router.post("/jobs", status_code=201)
def create_job(payload: JobIn, conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(current_user)):
    if user["role"] == "employer":
        employer_id, source = user["employer_id"], "employer"
    elif user["role"] == "advisor":
        employer_id = payload.employer_id
        if not employer_id:
            raise HTTPException(422, "employer_id is required.")
        source = "advisor"
    else:
        raise HTTPException(403, "This is not available for your account.")
    if not employer_id or not conn.execute(
            "SELECT 1 FROM employer WHERE id=?", (employer_id,)).fetchone():
        raise HTTPException(422, "Unknown employer.")
    if payload.status == "open" and lint.blocking_issues(payload.model_dump()):
        raise HTTPException(422, "The wording must be fixed before publishing.",
                            )  # details returned by check-wording
    job_id = db_mod.new_id(conn, "job")
    fields = _job_fields(payload)
    fields["status"] = payload.status or "draft"
    conn.execute(
        "INSERT INTO job (id,employer_id,title,field,duties,address,district,"
        "lat,lon,work_mode,pay_amount,pay_unit,pay_note,shifts,"
        "schedule_flexible,hours_min,hours_max,contract,experience,"
        "experience_note,qualifications,onboarding,languages,lifting,"
        "apply_question,cv_required,positions,status,source,confirmed_at)"
        " VALUES (:id,:employer_id,:title,:field,:duties,:address,:district,"
        ":lat,:lon,:work_mode,:pay_amount,:pay_unit,:pay_note,:shifts,"
        ":schedule_flexible,:hours_min,:hours_max,:contract,:experience,"
        ":experience_note,:qualifications,:onboarding,:languages,:lifting,"
        ":apply_question,:cv_required,:positions,:status,:source,:confirmed_at)",
        {**fields, "id": job_id, "employer_id": employer_id, "source": source,
         "confirmed_at": date.today().isoformat()})
    _write_job_conditions(conn, job_id, payload.conditions, source)
    db_mod.audit(conn, user["id"], "job_created", job_id)
    conn.commit()
    return job_out(conn, conn.execute("SELECT * FROM job WHERE id=?",
                                      (job_id,)).fetchone())


@router.put("/jobs/{job_id}")
def update_job(job_id: str, payload: JobIn,
               conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(current_user)):
    row = conn.execute("SELECT * FROM job WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found.")
    _check_owner(conn, user, row)
    if payload.status == "open" and lint.blocking_issues(payload.model_dump()):
        raise HTTPException(422, "The wording must be fixed before publishing.")
    fields = _job_fields(payload)
    fields["status"] = payload.status or row["status"]
    conn.execute(
        "UPDATE job SET title=:title,field=:field,duties=:duties,"
        "address=:address,district=:district,lat=:lat,lon=:lon,"
        "work_mode=:work_mode,pay_amount=:pay_amount,pay_unit=:pay_unit,"
        "pay_note=:pay_note,shifts=:shifts,schedule_flexible=:schedule_flexible,"
        "hours_min=:hours_min,hours_max=:hours_max,contract=:contract,"
        "experience=:experience,experience_note=:experience_note,"
        "qualifications=:qualifications,onboarding=:onboarding,"
        "languages=:languages,lifting=:lifting,apply_question=:apply_question,"
        "cv_required=:cv_required,positions=:positions,status=:status"
        " WHERE id=:id", {**fields, "id": job_id})
    source = "advisor" if user["role"] == "advisor" else "employer"
    _write_job_conditions(conn, job_id, payload.conditions, source)
    db_mod.audit(conn, user["id"], "job_updated", job_id)
    conn.commit()
    return job_out(conn, conn.execute("SELECT * FROM job WHERE id=?",
                                      (job_id,)).fetchone())


def _get_job_row(conn, job_id, user):
    row = conn.execute("SELECT * FROM job WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found.")
    _check_owner(conn, user, row)
    return row


def mark_confirmed(conn, job_id: str, actor: str) -> None:
    conn.execute("UPDATE job SET confirmed_at=? WHERE id=?",
                 (date.today().isoformat(), job_id))
    db_mod.audit(conn, actor, "job_confirmed", job_id)


def mark_closed(conn, job_id: str, actor: str) -> None:
    conn.execute("UPDATE job SET status='closed' WHERE id=?", (job_id,))
    conn.execute(
        "UPDATE application SET status='job_closed', updated_at=datetime('now')"
        " WHERE job_id=? AND status IN ('sent','interview')", (job_id,))
    db_mod.audit(conn, actor, "job_closed", job_id)


@router.post("/jobs/{job_id}/confirm")
def confirm_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    _get_job_row(conn, job_id, user)
    mark_confirmed(conn, job_id, user["id"])
    conn.commit()
    return job_out(conn, conn.execute("SELECT * FROM job WHERE id=?",
                                      (job_id,)).fetchone())


@router.post("/jobs/{job_id}/close")
def close_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(current_user)):
    _get_job_row(conn, job_id, user)
    mark_closed(conn, job_id, user["id"])
    conn.commit()
    return job_out(conn, conn.execute("SELECT * FROM job WHERE id=?",
                                      (job_id,)).fetchone())


@router.post("/jobs/{job_id}/publish")
def publish_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    row = _get_job_row(conn, job_id, user)
    issues = lint.blocking_issues(_decode(row))
    if issues:
        raise HTTPException(422, detail={
            "message": "The wording must be fixed before publishing.",
            "issues": issues})
    conn.execute("UPDATE job SET status='open', confirmed_at=? WHERE id=?",
                 (date.today().isoformat(), job_id))
    db_mod.audit(conn, user["id"], "job_published", job_id)
    conn.commit()
    return job_out(conn, conn.execute("SELECT * FROM job WHERE id=?",
                                      (job_id,)).fetchone())


@router.post("/jobs/check-wording")
def check_wording(payload: WordingCheckIn,
                  conn: sqlite3.Connection = Depends(get_conn),  # noqa: ARG001
                  user=Depends(current_user)):                   # noqa: ARG001
    """Advisory wording tips (age, 'native' language, gender, health,
    nationality; a high language level with no task)."""
    return {"tips": lint.check_wording(payload.model_dump())}


# --- advisor -------------------------------------------------------------------

@router.put("/advisor/jobs/{job_id}/conditions")
def advisor_check_condition(job_id: str, payload: ConditionCheckIn,
                            conn: sqlite3.Connection = Depends(get_conn),
                            user=Depends(current_user)):
    if user["role"] != "advisor":
        raise HTTPException(403, "This is not available for your account.")
    if payload.key not in CONDITION_KEYS:
        raise HTTPException(422, "Unknown condition key.")
    if not conn.execute("SELECT 1 FROM job WHERE id=?", (job_id,)).fetchone():
        raise HTTPException(404, "Job not found.")
    conn.execute(
        "INSERT OR REPLACE INTO job_condition (job_id,key,value,source,"
        "checked_at,note) VALUES (?,?,?,?,?,?)",
        (job_id, payload.key, payload.value, "advisor",
         date.today().isoformat(), payload.note))
    db_mod.audit(conn, user["id"], "condition_checked",
                 f"{job_id}:{payload.key}={payload.value}")
    conn.commit()
    return job_out(conn, conn.execute("SELECT * FROM job WHERE id=?",
                                      (job_id,)).fetchone())
