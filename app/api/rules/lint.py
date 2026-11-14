"""Job wording check (spec section 3): plain-language tips shown to the
employer while writing a job. Advisory only — `POST /api/jobs/check-wording`
returns tips; publishing is blocked (422) only when a protected-ground
requirement (age, health, gender, nationality, religion, family) is stated
in `experience_note` or `qualifications`.
"""

from __future__ import annotations

import re

NONDECR = "Non-Discrimination Act 1325/2014"
EQUALITY = "Equality Act 609/1986"

# (id, pattern, tip, suggestion)
TIPS = [
    ("age_words",
     r"\b(young|digital native|recent graduate|junior spirit|energetic team|"
     r"older applicants|retiree[s]?\s+only|age\s+\d+|over\s+\d{2}|under\s+\d{2})\b",
     "Age-coded words screen people out and can be illegal.",
     "Describe the work, not the age — e.g. 'a small team that ships weekly'."),
    ("native_language",
     r"\b(native\s+\w*\s*speaker|native[- ]level|mother[- ]?tongue|"
     r"fluent\s+\w+|perfect\s+(finnish|swedish|english))\b",
     "Asking for native-level language screens out capable people — the law "
     "treats it as possible origin discrimination.",
     "Name the task and level instead — e.g. 'Finnish A2 to read the cleaning plan'."),
    ("gendered_words",
     r"\b(salesman|chairman|foreman|manpower|he will|she will|guys|ninja|rockstar|"
     r"men only|women only|male|female)\b",
     "Gendered words deter whole groups from applying.",
     "Use the neutral form — 'sales assistant', 'the team', 'you'."),
    ("health_words",
     r"\b(healthy|fit and strong|physically fit|no disabilities|good health|"
     r"drug[- ]free|clean bill of health)\b",
     "Health or disability requirements are a protected ground — ask only "
     "what the task really needs.",
     "Name the concrete task — e.g. 'carries parcels up to 15 kg'."),
    ("nationality_words",
     r"\b(citizenship|citizens?|nationality|nationals?|finnish only|"
     r"eu citizens? only|ethnic|origin)\b",
     "Nationality or origin requirements are illegal unless a law demands them.",
     "Ask only about the right to work in Finland."),
    ("family_words",
     r"\b(no children|childless|no plans to start a family|must not be pregnant|"
     r"religion|religious|political views)\b",
     "Family plans, pregnancy, religion and political views are protected grounds.",
     "Remove it — ask about the work only."),
    ("degree_without_reason",
     r"\b(master'?s|bachelor'?s|degree|diploma|phd|university)\b",
     "A degree requirement without a stated task shrinks who can apply.",
     "Name what the person must be able to do — e.g. 'can write clear reports'."),
    ("no_gaps",
     r"\bno (unexplained )?gaps|gap[- ]free|uninterrupted (career|cv|employment)\b",
     "Demanding gap-free histories penalises parental leave, illness and migration.",
     "Remove it — ask what the person can do now."),
    ("photo",
     r"\b(photo|picture|headshot)\b",
     "Requesting a photo invites bias before anything else is seen.",
     "Drop the photo request."),
]


def _text_fields(job: dict):
    """Every wording surface of a job payload."""
    for key in ("title", "pay_note", "experience_note", "onboarding",
                "apply_question", "lifting"):
        yield key, job.get(key) or ""
    for i, d in enumerate(job.get("duties") or []):
        yield f"duties[{i}]", d or ""
    for i, q in enumerate(job.get("qualifications") or []):
        yield f"qualifications[{i}]", q or ""


def check_wording(job: dict, max_tips: int = 5) -> list[dict]:
    """Advisory tips over the whole job payload."""
    tips = []
    seen = set()
    for tip_id, pattern, why, suggestion in TIPS:
        rx = re.compile(pattern, re.I)
        for field, text in _text_fields(job):
            m = rx.search(text)
            if m and tip_id not in seen:
                seen.add(tip_id)
                tips.append({"id": f"tip-{tip_id}", "rule": tip_id,
                             "field": field, "trigger": m.group(0),
                             "why": why, "suggestion": suggestion})
                break
        if len(tips) >= max_tips:
            break

    # a high language level with no stated task is the structured form of
    # 'fluent Finnish' — advisory like the literal wording above
    if len(tips) < max_tips:
        for need in job.get("languages") or []:
            if need.get("level") in ("C1", "C2") \
                    and not (need.get("task") or "").strip() \
                    and "native_language" not in seen:
                tips.append({
                    "id": "tip-language_without_task", "rule": "language_without_task",
                    "field": "languages",
                    "trigger": f"{need.get('language')} {need.get('level')} with no task",
                    "why": "A high language level without naming the task can be "
                           "unnecessary — say what the language is for.",
                    "suggestion": f"Add the task, e.g. '{need.get('language')} "
                                  "B1 to answer the customer line'."})
                break
    return tips


# blocking applies only to the free-text requirement fields
_BLOCKED_FIELDS = ("experience_note", "qualifications")
_BLOCKED_IDS = {"age_words", "health_words", "gendered_words",
                "nationality_words", "family_words"}


def blocking_issues(job: dict) -> list[dict]:
    """Protected-ground requirements stated as a requirement. Publishing is
    refused (422) while any of these remain."""
    issues = []
    for tip_id, pattern, why, suggestion in TIPS:
        if tip_id not in _BLOCKED_IDS:
            continue
        rx = re.compile(pattern, re.I)
        for field in _BLOCKED_FIELDS:
            texts = job.get(field) or []
            if isinstance(texts, str):
                texts = [texts]
            for text in texts:
                m = rx.search(text)
                if m:
                    issues.append({"rule": tip_id, "field": field,
                                   "trigger": m.group(0), "why": why,
                                   "suggestion": suggestion})
                    break
            if issues:
                break
    return issues
