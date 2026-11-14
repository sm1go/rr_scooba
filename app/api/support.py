"""City support programmes (spec v3 §7).

Facts come from db/seed/support_programs.json (authored by the product lead
— loaded verbatim, never rewritten). The tiny `job_rule` language:
  always | contract in (a, b) | hours_min >= N | hours_max >= N
joined by `and`. Unknown hours -> rule not matched.
"""

from __future__ import annotations

import re
from functools import lru_cache

from .db import SEED_DIR


@lru_cache(maxsize=1)
def load_programs() -> dict:
    path = SEED_DIR / "support_programs.json"
    return __import__("json").loads(path.read_text(encoding="utf-8"))


def rule_matches(rule: str | None, job: dict) -> bool:
    """Evaluate one job_rule against a decoded job dict."""
    if not rule:
        return False
    for clause in [c.strip() for c in rule.split("and")]:
        if clause == "always":
            continue
        m = re.fullmatch(r"contract in \(([^)]+)\)", clause)
        if m:
            allowed = {v.strip() for v in m.group(1).split(",")}
            if job.get("contract") not in allowed:
                return False
            continue
        m = re.fullmatch(r"hours_(min|max) >= (\d+)", clause)
        if m:
            field, n = f"hours_{m.group(1)}", int(m.group(2))
            val = job.get(field)
            if val is None or val < n:
                return False
            continue
        return False                            # unknown clause -> no match
    return True


def matching_programs(job: dict) -> list[dict]:
    """Employer-side programmes whose job_rule matches this job."""
    return [p for p in load_programs()["programs"]
            if p.get("job_rule") and rule_matches(p["job_rule"], job)
            and p.get("for_employer")]


def catalogue() -> dict:
    """GET /api/support payload — verbatim data + meta."""
    return load_programs()
