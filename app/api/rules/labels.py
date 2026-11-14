"""Derived job labels and availability fit (spec section 2).

Labels describe the job's conditions only — a label means "fits", never
"only for". Unknown hours produce no label. Every label carries a plain
`why` sentence explaining which rule fired.
"""

from __future__ import annotations

import math

# slot vocabulary: "<day>-<part>", part bounds in minutes: morning(06-12),
# afternoon(12-17), evening(17-23)
PARTS = {"morning": (6 * 60, 12 * 60), "afternoon": (12 * 60, 17 * 60),
         "evening": (17 * 60, 23 * 60)}
DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}

LABELS_META = [
    {"id": "students",   "name": "Fits students"},
    {"id": "retirement", "name": "Extra work in retirement"},
    {"id": "first_job",  "name": "First job / no experience"},
    {"id": "side_job",   "name": "Side job"},
    {"id": "part_time",  "name": "Part-time"},
    {"id": "access_info","name": "Access details given"},
    {"id": "near_station","name": "Near a station"},
]


def station_label(nearest: dict | None) -> dict | None:
    """near_station label (spec v3 §5): within 800 m, straight line."""
    if not nearest or nearest["distance_m"] > 800:
        return None
    kind = "metro station" if nearest["mode"] == "metro" \
        else "train station"
    return {"id": "near_station",
            "why": f"About {nearest['distance_m']} m from "
                   f"{nearest['name']} {kind}, in a straight line."}


def _minutes(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _shift_parts(shift: dict) -> list[str]:
    """Which named parts a shift touches. A shift spanning a boundary counts
    as touching every part it overlaps (10:00-16:00 = morning + afternoon)."""
    start, end = _minutes(shift["start"]), _minutes(shift["end"])
    return [p for p, (lo, hi) in PARTS.items() if start < hi and end > lo]


def fits_availability(shifts: list[dict], flexible: bool,
                      slots: list[str]) -> bool:
    """Every shift must lie inside a selected slot, or schedule_flexible."""
    if flexible:
        return True
    if not shifts or not slots:
        return False
    selected = set(slots)
    for shift in shifts:
        day = shift.get("day")
        for part in _shift_parts(shift):
            if f"{day}-{part}" not in selected:
                return False
    return True


def job_labels(job: dict, condition_count: int) -> list[dict]:
    """Return [{id, why}] for a job dict (already decoded) + number of
    condition rows it has. Rules straight from the spec table."""
    labels = []
    hours_max = job.get("hours_max")
    shifts = job.get("shifts") or []
    flexible = bool(job.get("schedule_flexible"))

    if hours_max is not None:
        weekend = all(s["day"] in ("sat", "sun") for s in shifts)
        evening_start = all(_minutes(s["start"]) >= 16 * 60 for s in shifts)
        if hours_max <= 25 and (flexible or (shifts and (weekend or evening_start))):
            labels.append({
                "id": "students",
                "why": ("The hours are low enough to fit around studies"
                        + (" and the schedule is flexible." if flexible
                           else " and the shifts are in the evening or on the weekend."))})
        early_end = any(_minutes(s["end"]) <= 18 * 60 for s in shifts)
        if hours_max <= 20 and (flexible or early_end):
            labels.append({
                "id": "retirement",
                "why": ("Light weekly hours"
                        + (" with a flexible schedule." if flexible
                           else " and at least one shift that ends by 18:00."))})
        if hours_max <= 20:
            labels.append({"id": "side_job",
                           "why": "At most 20 hours a week, so it can fit beside other work."})
        if hours_max < 30:
            labels.append({"id": "part_time",
                           "why": "Under 30 hours a week."})

    if job.get("experience") == "none" and (job.get("onboarding") or "").strip():
        labels.append({
            "id": "first_job",
            "why": "No experience is asked for, and the employer explains "
                   "how you will be trained."})
    if condition_count >= 4:
        labels.append({
            "id": "access_info",
            "why": "The employer or an advisor has given details about the "
                   "working conditions."})
    return labels


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def shift_summary(job: dict) -> str:
    """Compact 'Tue, Thu 18–21' style text for list rows."""
    shifts = job.get("shifts") or []
    if not shifts:
        return "Agreed together" if job.get("schedule_flexible") else ""
    days = []
    for s in shifts:
        days.append(s["day"].capitalize())
    day_txt = ", ".join(days)
    first = shifts[0]
    return f"{day_txt} {first['start']}–{first['end']}"


def language_filter_ok(job: dict, language: str, level_max: str,
                       levels: list[str]) -> bool:
    """Keep the job when its need for `language` is at or below `level_max`,
    or it does not need that language at all."""
    for need in job.get("languages") or []:
        if (need.get("language") or "").lower() == language.lower():
            return need.get("level") in levels[:levels.index(level_max) + 1] \
                if level_max in levels else True
    return True
