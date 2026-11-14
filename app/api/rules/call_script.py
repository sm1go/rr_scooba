"""Fixed 'prepare a call to the employer' script (spec v3 §4 fallback).

One question per unknown field, in field order — used when the AI helper
is not connected, and as the field list for the AI version.
"""

from __future__ import annotations

from ..serialize import CONDITION_KEYS

# field id -> (kind, question). kind 'condition' -> Yes/No + note control;
# 'edit' -> small field editor -> PUT /api/jobs/{id}
QUESTIONS: dict[str, tuple[str, str]] = {
    **{f"condition.{k}": ("condition", q) for k, q in [
        ("step_free_entrance",
         "Is the entrance step-free, or are there steps — and how many?"),
        ("lift", "If the workplace is not on the ground floor, is there a lift?"),
        ("accessible_toilet",
         "Is there an accessible toilet that a wheelchair user can use?"),
        ("seated_work", "Can the work be done seated, at least most of the time?"),
        ("flexible_breaks",
         "Can the worker take a break when they need one, for example to sit down or take medicine?"),
        ("quiet_environment", "Is the work environment mostly quiet?"),
        ("written_instructions",
         "Can the instructions for the job be given in writing?"),
        ("sign_language_ok",
         "Could a person who uses sign language work here?"),
        ("assistive_tech_ok",
         "May the worker use their own assistive technology, for example a screen reader?"),
        ("adjustments_negotiable",
         "Can small adjustments to the work be agreed together if needed?"),
    ]},
    "pay_amount": ("edit",
                   "What is the pay, per hour or per month?"),
    "pay_unit": ("edit", "Is that pay per hour or per month?"),
    "hours_min": ("edit", "How many hours a week does the job offer, roughly?"),
    "hours_max": ("edit", "And is there a maximum number of hours a week?"),
    "shifts": ("edit", "On which days and at what times is the work done?"),
    "onboarding": ("edit",
                   "How do you teach or introduce a new person to the work?"),
    "lifting": ("edit",
                "Does the work involve lifting, and if so, how heavy and how often?"),
    "language_tasks": ("edit",
                       "What does the worker actually need the language for — customers, written work, safety?"),
}


def unknown_fields(job: dict) -> list[str]:
    """Field ids that are still unknown on a decoded job dict."""
    fields: list[str] = []
    rows = {c["key"]: c for c in job.get("conditions", [])}
    for k in CONDITION_KEYS:
        if not rows.get(k) or rows[k]["value"] == "unknown":
            fields.append(f"condition.{k}")
    if job.get("pay_amount") is None:
        fields.append("pay_amount")
        fields.append("pay_unit")
    if job.get("hours_min") is None:
        fields.append("hours_min")
    if job.get("hours_max") is None:
        fields.append("hours_max")
    if not job.get("shifts") and not job.get("schedule_flexible"):
        fields.append("shifts")
    if not (job.get("onboarding") or "").strip():
        fields.append("onboarding")
    if not job.get("lifting"):
        fields.append("lifting")
    for lang in job.get("languages") or []:
        if not (lang.get("task") or "").strip():
            fields.append("language_tasks")
            break
    return fields


def script(job: dict, employer_name: str = "") -> dict:
    """Deterministic call script covering every unknown field."""
    fields = unknown_fields(job)
    return {
        "opening": (f"Hello, this is Employment Espoo — I'd like to check "
                    f"a few details about your job posting"
                    + (f" at {employer_name}" if employer_name else "")
                    + "."),
        "questions": [{"field": f, "question": QUESTIONS[f][1]}
                      for f in fields],
        "kinds": {f: QUESTIONS[f][0] for f in fields},
        "source": "rules",
    }
