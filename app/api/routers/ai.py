"""Optional AI helpers (spec v3 §0–4) + GET /api/config.

Every endpoint works without a key where the spec gives a rules fallback;
endpoints that need AI return 503 "The AI assistant is not connected."
No personal text is stored or audited; the note text is never persisted.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sqlite3
import time
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from .. import db as db_mod
from .. import llm, settings
from ..auth import current_user, optional_user
from ..db import get_conn
from ..models import (AdvisorNoteIn, FiltersIn, JobDraftIn, SimplifyIn)
from ..prompts import (ADVISOR_NOTE_SYSTEM, ADVISOR_QUESTIONS_SYSTEM,
                       FILTERS_SYSTEM, JOB_FROM_PHOTO_SYSTEM, SIMPLIFY_SYSTEM)
from ..rules import call_script, filter_words, lint
from ..serialize import CONDITION_KEYS, job_out

router = APIRouter(prefix="/api", tags=["ai"])

MAX_IMAGE_BYTES = 4 * 1024 * 1024

FILTER_WHITELIST = {
    "labels": {"students", "retirement", "first_job", "side_job", "part_time"},
    "field": {"cleaning", "retail", "restaurant", "care", "logistics",
              "office", "customer_service", "education", "construction",
              "tech", "seasonal", "manufacturing", "health", "maintenance"},
    "work_mode": {"on_site", "hybrid", "remote"},
    "experience": {"none"},
    "district": {"leppavaara", "tapiola", "otaniemi", "matinkyla", "olari",
                 "niittykumpu", "espoon_keskus", "espoonlahti", "kauklahti",
                 "kalajarvi"},
    "needs": set(CONDITION_KEYS),
    "level_max": {"A1", "A2", "B1", "B2", "C1", "C2"},
    "pay_unit": {"hour", "month"},
}
_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
_PARTS = {"morning", "afternoon", "evening"}

NOTE_TYPES = {"help_request", "application", "job_conditions"}
NOTE_KINDS = {"check_conditions", "prepare_application", "arrange_contact",
              "other"}

# 10 requests per minute per IP for the public AI endpoints (spec §2)
_hits: dict[str, list[float]] = defaultdict(list)


def _rate_limit(request: Request, limit: int = 10, window: float = 60.0):
    ip = request.client.host if request.client else "?"
    now = time.monotonic()
    hits = [t for t in _hits[ip] if now - t < window]
    hits.append(now)
    _hits[ip] = hits
    if len(hits) > limit:
        raise HTTPException(429, "Too many requests — wait a moment "
                                 "and try again.")


def _reset_rate_limit() -> None:
    _hits.clear()


@router.get("/config")
def config():
    """Feature flags — the UI only shows controls that can work."""
    return {"ai": settings.ai_enabled(),
            "commute": settings.commute_enabled()}


def _require_ai():
    if not settings.ai_enabled():
        raise HTTPException(503, "The AI assistant is not connected.")


def _ai(messages, conn, action):
    try:
        return llm.chat(messages, conn=conn, action=action)
    except llm.LLMUnavailable as e:
        raise HTTPException(503, "The AI assistant is not connected.") from e
    except llm.LLMBadReply as e:
        raise HTTPException(502, "The assistant gave an unusable answer. "
                                 "Please try again.") from e


# --- 1. photo/text -> job draft -------------------------------------------------

FIELD_ENUM = {"cleaning", "retail", "restaurant", "care", "logistics",
              "office", "customer_service", "education", "construction",
              "tech", "seasonal", "manufacturing", "health", "maintenance",
              "other"}
CONTRACT_ENUM = {"permanent", "fixed_term", "seasonal", "gig", "summer_job",
                 "traineeship"}
EXPERIENCE_ENUM = {"none", "some", "required"}
WORK_MODE_ENUM = {"on_site", "hybrid", "remote"}
PAY_UNIT_ENUM = {"hour", "month"}
CEFR_ENUM = {"A1", "A2", "B1", "B2", "C1", "C2"}

DRAFT_KEYS = {
    "title": "str", "employer_name": "str", "field": "enum",
    "duties": "list_str", "address": "str", "work_mode": "enum",
    "pay_amount": "num", "pay_unit": "enum", "pay_note": "str",
    "shifts": "shifts", "schedule_flexible": "bool",
    "hours_min": "int", "hours_max": "int", "contract": "enum",
    "experience": "enum", "experience_note": "str",
    "qualifications": "list_str", "onboarding": "str",
    "languages": "langs", "lifting": "str", "contact": "str",
}


def _clean_draft(raw: dict) -> dict:
    """Validate the model's draft: unknown keys dropped, enums checked,
    invalid values -> null and added to `missing` (spec §1)."""
    draft: dict[str, Any] = {}
    missing = [m for m in raw.get("missing", []) if isinstance(m, str)]
    warnings = [w for w in raw.get("wording_warnings", [])
                if isinstance(w, str)]
    quotes = {k: v for k, v in (raw.get("source_quotes") or {}).items()
              if isinstance(k, str) and isinstance(v, str)}

    def bad(key: str):
        draft[key] = None if DRAFT_KEYS[key] != "list_str" else []
        if key not in missing:
            missing.append(key)

    for key, kind in DRAFT_KEYS.items():
        v = raw.get(key)
        if kind == "str":
            if v is None or (isinstance(v, str) and not v.strip()):
                bad(key) if key != "contact" else draft.update(contact=None)
                if key == "contact":
                    continue
            elif isinstance(v, str):
                draft[key] = v.strip()
            else:
                bad(key)
        elif kind == "num":
            if v is None:
                bad(key)
            elif isinstance(v, (int, float)) and v >= 0:
                draft[key] = v
            else:
                bad(key)
        elif kind == "int":
            if v is None:
                bad(key)
            elif isinstance(v, int) and v >= 0:
                draft[key] = v
            else:
                bad(key)
        elif kind == "bool":
            draft[key] = bool(v) if isinstance(v, bool) else None
        elif kind == "enum":
            allowed = {"field": FIELD_ENUM, "work_mode": WORK_MODE_ENUM,
                       "pay_unit": PAY_UNIT_ENUM, "contract": CONTRACT_ENUM,
                       "experience": EXPERIENCE_ENUM}[key]
            if v is None:
                bad(key)
            elif v in allowed:
                draft[key] = v
            else:
                bad(key)
        elif kind == "list_str":
            if v is None:
                draft[key] = []
            elif isinstance(v, list):
                draft[key] = [str(x) for x in v if isinstance(x, str)]
            else:
                bad(key)
        elif kind == "shifts":
            ok = isinstance(v, list) and all(
                isinstance(s, dict) and s.get("day") in _DAYS
                and re.fullmatch(r"\d{2}:\d{2}", str(s.get("start", "")))
                and re.fullmatch(r"\d{2}:\d{2}", str(s.get("end", "")))
                for s in v)
            draft[key] = ([{"day": s["day"], "start": s["start"],
                            "end": s["end"]} for s in v] if ok and v
                          else [])
            if v is not None and not ok:
                missing.append("shifts")
        elif kind == "langs":
            out_langs = []
            if isinstance(v, list):
                for item in v:
                    if not isinstance(item, dict) or not item.get("language"):
                        continue
                    lv = item.get("level")
                    out_langs.append({
                        "language": str(item["language"]),
                        "level": lv if lv in CEFR_ENUM else None,
                        "task": item.get("task") if isinstance(
                            item.get("task"), str) else None})
            draft[key] = out_langs
    # pay consistency: amount without unit (or vice versa) is incomplete
    if draft.get("pay_amount") is not None and draft.get("pay_unit") is None:
        if "pay_unit" not in missing:
            missing.append("pay_unit")
    return {"draft": draft, "missing": sorted(set(missing)),
            "wording_warnings": warnings, "source_quotes": quotes}


@router.post("/ai/job-draft")
def job_draft(payload: JobDraftIn,
              conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(current_user)):
    """Photo or dictated text -> structured draft; nothing is saved (§1)."""
    if user["role"] not in ("employer", "advisor"):
        raise HTTPException(403, "This is not available for your account.")
    _require_ai()
    if not payload.image_base64 and not (payload.text or "").strip():
        raise HTTPException(422, "Send a photo or some text.")
    content: list[dict] = []
    if payload.image_base64:
        try:
            raw = base64.b64decode(payload.image_base64, validate=True)
        except Exception:
            raise HTTPException(422, "The photo could not be read.")
        if len(raw) > MAX_IMAGE_BYTES:
            raise HTTPException(413, "The photo is too large "
                                     "(over 4 MB).")
        mime = payload.image_mime or "image/jpeg"
        content.append({"type": "image_url", "image_url": {
            "url": f"data:{mime};base64,{payload.image_base64}"}})
    if (payload.text or "").strip():
        content.append({"type": "text", "text": payload.text.strip()})
    raw_out = _ai([{"role": "system", "content": JOB_FROM_PHOTO_SYSTEM},
                   {"role": "user", "content": content}],
                  conn, "ai_job_draft")
    if not isinstance(raw_out, dict):
        raise HTTPException(502, "The assistant gave an unusable answer.")
    return _clean_draft(raw_out)


# --- 2. free text -> filters -----------------------------------------------------

def _clean_filters(raw: dict) -> dict:
    """Whitelist validation of FILTERS_SYSTEM output (spec §2)."""
    filters: dict[str, Any] = {}
    not_understood = [str(x) for x in raw.get("not_understood", [])
                      if isinstance(x, str)]
    explanation = [str(x) for x in raw.get("explanation", [])
                   if isinstance(x, str)]

    def drop(key: str):
        note = f"{key}: {raw.get(key)!r} was not a known filter"
        if note not in not_understood:
            not_understood.append(note)

    for key, val in raw.items():
        if key in ("explanation", "not_understood") or val in (None, "", []):
            continue
        if key == "labels" and isinstance(val, list):
            ok = [x for x in val if x in FILTER_WHITELIST["labels"]]
            if ok:
                filters["labels"] = ok
            else:
                drop(key)
        elif key in ("field", "work_mode", "district", "pay_unit",
                     "experience", "level_max"):
            if val in FILTER_WHITELIST[key]:
                filters[key] = val
            else:
                drop(key)
        elif key == "slots" and isinstance(val, list):
            ok = [s for s in val
                  if isinstance(s, str) and len(s.split("-")) == 2
                  and s.split("-")[0] in _DAYS
                  and s.split("-")[1] in _PARTS]
            if ok:
                filters["slots"] = ok
            elif val:
                drop(key)
        elif key == "needs" and isinstance(val, list):
            ok = [x for x in val if x in FILTER_WHITELIST["needs"]]
            if ok:
                filters["needs"] = ok
                filters["needs_mode"] = "yes"
            elif val:
                drop(key)
        elif key == "keywords" and isinstance(val, list):
            ok = [x.strip()[:40] for x in val
                  if isinstance(x, str) and len(x.strip()) >= 2][:8]
            if ok:
                filters["keywords"] = ok
            elif val:
                drop(key)
        elif key in ("hours_max", "hours_min", "km") and isinstance(val, int) \
                and not isinstance(val, bool):
            filters[key] = val
        elif key == "pay_min" and isinstance(val, (int, float)) \
                and not isinstance(val, bool):
            filters[key] = val
        elif key == "language" and isinstance(val, str) and val.strip():
            filters[key] = val.strip()
        elif key == "near_station":
            if val is True:
                filters["near_station"] = True
        else:
            drop(key)
    return {"filters": filters, "explanation": explanation,
            "not_understood": not_understood, "source": "ai"}


@router.post("/ai/filters")
def filters(payload: FiltersIn, request: Request,
            conn: sqlite3.Connection = Depends(get_conn)):
    """'Tell us what you are looking for' -> filter set (§2).

    With AI the output is validated; without AI (or on failure) the
    deterministic keyword parser answers instead. The text is not stored."""
    _rate_limit(request)
    text = payload.text.strip()
    if not text:
        raise HTTPException(422, "Write a few words first.")
    if settings.ai_enabled():
        try:
            raw = llm.chat(
                [{"role": "system", "content": FILTERS_SYSTEM},
                 {"role": "user", "content": json.dumps(
                     {"text": text, "ui_language": payload.ui_language},
                     ensure_ascii=False)}],
                conn=conn, action="ai_filters")
            if isinstance(raw, dict):
                return _clean_filters(raw)
        except (llm.LLMUnavailable, llm.LLMBadReply):
            pass                                    # fall through to rules
    out = filter_words.parse(text)
    out["source"] = "rules"
    return out


# --- 3. simplify ----------------------------------------------------------------

SIMPLIFY_LANG_NAMES = {
    "en": "English", "fi": "Finnish", "sv": "Swedish", "ru": "Russian",
    "ar": "Arabic", "et": "Estonian", "zh": "Chinese", "fa": "Farsi",
    "sq": "Albanian", "uk": "Ukrainian"}


def _simplify_input(job: dict) -> dict:
    return {
        "title": job["title"],
        "duties": job["duties"],
        "experience_note": job["experience_note"] or None,
        "qualifications": job["qualifications"],
        "onboarding": job["onboarding"] or None,
        "pay_note": job["pay_note"] or None,
        "lifting": job["lifting"],
        "apply_question": job["apply_question"] or None,
        "language_tasks": [l["task"] for l in job["languages"]
                           if l.get("task")] or None,
    }


def _digits(text: str) -> list[str]:
    return re.findall(r"\d+", text)


def _flatten_sections(sections: dict) -> str:
    parts: list[str] = []
    for v in sections.values():
        if isinstance(v, list):
            parts.extend(str(x) for x in v if x)
        elif v:
            parts.append(str(v))
    return " ".join(parts)


def _check_simplified(inp: dict, out: dict) -> bool:
    """Server-side checks (spec §3): same keys, same list lengths, every
    digit sequence in the output also occurs in the input."""
    if not isinstance(out, dict) or set(out.keys()) != set(inp.keys()):
        return False
    for key, src in inp.items():
        val = out[key]
        if src is None:
            if val is not None:
                return False
        elif isinstance(src, list):
            if not isinstance(val, list) or len(val) != len(src):
                return False
        elif not isinstance(val, str):
            return False
    in_digits = _digits(_flatten_sections(inp))
    out_digits = _digits(_flatten_sections(out))
    return all(any(d == i for i in in_digits) for d in out_digits)


@router.post("/ai/simplify")
def simplify(payload: SimplifyIn, request: Request,
             conn: sqlite3.Connection = Depends(get_conn)):
    """A simpler rewrite of the free-text parts only (§3)."""
    _rate_limit(request)
    _require_ai()
    row = conn.execute("SELECT * FROM job WHERE id=?",
                       (payload.job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found.")
    job = {k: row[k] for k in row.keys()}
    for f in ("duties", "shifts", "qualifications", "languages"):
        job[f] = json.loads(job[f] or "[]")
    inp = _simplify_input(job)
    source_hash = hashlib.sha256(
        json.dumps(inp, sort_keys=True, ensure_ascii=False)
        .encode()).hexdigest()
    cached = conn.execute(
        "SELECT payload FROM job_text_cache WHERE job_id=? AND language=?"
        " AND source_hash=?", (payload.job_id, payload.language,
                               source_hash)).fetchone()
    if cached:
        return json.loads(cached["payload"])

    lang_name = SIMPLIFY_LANG_NAMES[payload.language]
    messages = [{"role": "system",
                 "content": SIMPLIFY_SYSTEM.format(language_name=lang_name)},
                {"role": "user", "content": json.dumps(
                    inp, ensure_ascii=False)}]
    last: dict | None = None
    for _ in range(2):                              # one retry on a bad reply
        try:
            out = llm.get_client().chat(messages)
        except llm.LLMUnavailable as e:
            raise HTTPException(503, "The AI assistant is not connected."
                                ) from e
        except llm.LLMBadReply:
            continue
        last = out
        if _check_simplified(inp, out):
            result = {"language": payload.language, "sections": out,
                      "machine": True}
            conn.execute(
                "INSERT OR REPLACE INTO job_text_cache"
                " (job_id,language,source_hash,payload) VALUES (?,?,?,?)",
                (payload.job_id, payload.language, source_hash,
                 json.dumps(result, ensure_ascii=False)))
            db_mod.audit(conn, "ai", "ai_simplify", payload.job_id)
            conn.commit()
            return result
    raise HTTPException(502, "We could not make a simpler version right now.")


# --- 4. advisor helpers -----------------------------------------------------------

def _advisor_role(user):
    if user["role"] != "advisor":
        raise HTTPException(403, "This is not available for your account.")


@router.post("/ai/advisor/questions")
def advisor_questions(payload: dict,
                      conn: sqlite3.Connection = Depends(get_conn),
                      user=Depends(current_user)):
    """'Prepare a call to the employer' script (§4)."""
    _advisor_role(user)
    job_id = payload.get("job_id", "")
    row = conn.execute("SELECT * FROM job WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found.")
    job = {k: row[k] for k in row.keys()}
    for f in ("duties", "shifts", "qualifications", "languages"):
        job[f] = json.loads(job[f] or "[]")
    job["conditions"] = [{"key": r["key"], "value": r["value"]}
                         for r in conn.execute(
            "SELECT key,value FROM job_condition WHERE job_id=?",
            (job_id,))]
    emp = conn.execute(
        "SELECT name, contact_name, contact_email, contact_phone"
        " FROM employer WHERE id=?", (job["employer_id"],)).fetchone()
    fields = call_script.unknown_fields(job)
    employer = ({"name": emp["name"], "contact_name": emp["contact_name"],
                 "contact_email": emp["contact_email"],
                 "contact_phone": emp["contact_phone"]}
                if emp else None)

    if settings.ai_enabled():
        try:
            raw = llm.chat(
                [{"role": "system", "content": ADVISOR_QUESTIONS_SYSTEM},
                 {"role": "user", "content": json.dumps(
                     {"job": job, "unknown_fields": fields},
                     ensure_ascii=False)}],
                conn=conn, action="ai_advisor_questions")
            if isinstance(raw, dict) and isinstance(raw.get("questions"),
                                                    list):
                qs = [{"field": q["field"], "question": str(q["question"])}
                      for q in raw["questions"]
                      if isinstance(q, dict) and q.get("field") in fields
                      and q.get("question")]
                got = {q["field"] for q in qs}
                qs += [{"field": f, "question": call_script.QUESTIONS[f][1]}
                       for f in fields if f not in got]
                return {"opening": str(raw.get("opening") or
                            "Hello, this is Employment Espoo."),
                        "questions": qs,
                        "kinds": {f: call_script.QUESTIONS[f][0]
                                  for f in fields},
                        "employer": employer,
                        "source": "ai"}
        except (llm.LLMUnavailable, llm.LLMBadReply):
            pass
    return {**call_script.script(job, emp["name"] if emp else ""),
            "employer": employer}


def _clean_note(raw: dict) -> dict:
    """Validate ADVISOR_NOTE_SYSTEM output (spec §4). Nothing persisted."""
    t = raw.get("type")
    if t not in NOTE_TYPES:
        t = "help_request"
    cm = raw.get("contact_method")
    kind = raw.get("kind")
    needs = [n for n in (raw.get("needs") or [])
             if n in FILTER_WHITELIST["needs"]]
    conds = []
    for c in raw.get("conditions") or []:
        if isinstance(c, dict) and c.get("key") in CONDITION_KEYS \
                and c.get("value") in ("yes", "no"):
            conds.append({"key": c["key"], "value": c["value"],
                          "note": str(c.get("note") or "")})
    def s(k):
        v = raw.get(k)
        return v.strip() if isinstance(v, str) and v.strip() else None
    return {
        "type": t, "person_name": s("person_name"),
        "contact_method": cm if cm in ("phone", "sms", "email") else None,
        "contact_value": s("contact_value"), "job_hint": s("job_hint"),
        "kind": kind if kind in NOTE_KINDS else None,
        "message": s("message"),
        "availability_note": s("availability_note"), "answer": s("answer"),
        "needs": needs, "conditions": conds,
        "consent_mentioned": bool(raw.get("consent_mentioned")),
        "left_out": [str(x) for x in raw.get("left_out", [])
                     if isinstance(x, str)],
    }


@router.post("/ai/advisor/note")
def advisor_note(payload: AdvisorNoteIn,
                 conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(current_user)):
    """Turn the advisor's note into a draft record (§4). The note text is
    sent to the model and never stored."""
    _advisor_role(user)
    _require_ai()
    raw = _ai([{"role": "system", "content": ADVISOR_NOTE_SYSTEM},
               {"role": "user", "content": payload.text}],
              conn, "ai_advisor_note")
    if not isinstance(raw, dict):
        raise HTTPException(502, "The assistant gave an unusable answer.")
    return _clean_note(raw)
