"""Derived labels + availability fit rules (spec section 2)."""

from __future__ import annotations

from app.api.rules.labels import fits_availability, haversine_km, job_labels


def _job(**kw):
    base = {"hours_min": 10, "hours_max": 20, "schedule_flexible": 0,
            "shifts": [], "experience": "some", "onboarding": ""}
    base.update(kw)
    return base


def ids(labels):
    return {l["id"] for l in labels}


def test_students_weekend():
    j = _job(hours_max=16, shifts=[{"day": "sat", "start": "10:00",
                                  "end": "16:00"}])
    assert "students" in ids(job_labels(j, 0))


def test_students_evening_start():
    j = _job(hours_max=12, shifts=[{"day": "tue", "start": "18:00",
                                  "end": "21:00"}])
    assert "students" in ids(job_labels(j, 0))


def test_students_flexible():
    j = _job(hours_max=20, schedule_flexible=1)
    assert "students" in ids(job_labels(j, 0))


def test_no_students_label_weekday_mornings():
    j = _job(hours_max=15, shifts=[{"day": "mon", "start": "08:00",
                                  "end": "12:00"}])
    assert "students" not in ids(job_labels(j, 0))


def test_students_needs_hours_le_25():
    j = _job(hours_max=30, schedule_flexible=1)
    assert "students" not in ids(job_labels(j, 0))


def test_retirement_early_end():
    j = _job(hours_max=8, shifts=[{"day": "mon", "start": "08:00",
                                 "end": "11:00"}])
    assert "retirement" in ids(job_labels(j, 0))


def test_retirement_late_end_no_flex():
    j = _job(hours_max=18, shifts=[{"day": "mon", "start": "15:00",
                                  "end": "21:00"}])
    assert "retirement" not in ids(job_labels(j, 0))


def test_retirement_flexible():
    j = _job(hours_max=10, schedule_flexible=1)
    assert "retirement" in ids(job_labels(j, 0))


def test_first_job():
    assert "first_job" in ids(job_labels(
        _job(experience="none", onboarding="We train you."), 0))
    assert "first_job" not in ids(job_labels(
        _job(experience="none", onboarding=""), 0))
    assert "first_job" not in ids(job_labels(
        _job(experience="some", onboarding="We train you."), 0))


def test_side_and_part_time():
    assert {"side_job", "part_time"} <= ids(job_labels(_job(hours_max=18), 0))
    assert "side_job" not in ids(job_labels(_job(hours_max=25), 0))
    assert "part_time" not in ids(job_labels(_job(hours_max=30), 0))


def test_access_info_needs_four_rows():
    assert "access_info" not in ids(job_labels(_job(), 3))
    assert "access_info" in ids(job_labels(_job(), 4))


def test_unknown_hours_no_hour_labels():
    got = ids(job_labels(_job(hours_min=None, hours_max=None), 0))
    assert not ({"students", "retirement", "side_job", "part_time"} & got)


def test_every_label_has_a_why():
    j = _job(hours_max=10, schedule_flexible=1, experience="none",
             onboarding="Training.")
    for label in job_labels(j, 5):
        assert label["why"].strip()


# --- availability fit ---------------------------------------------------------

def test_fit_inside_slots():
    shifts = [{"day": "tue", "start": "18:00", "end": "21:00"}]
    assert fits_availability(shifts, False, ["tue-evening"])
    assert not fits_availability(shifts, False, ["tue-morning"])
    assert not fits_availability(shifts, False, ["wed-evening"])


def test_fit_spanning_shift_needs_both_parts():
    shifts = [{"day": "sat", "start": "10:00", "end": "16:00"}]
    assert not fits_availability(shifts, False, ["sat-morning"])
    assert not fits_availability(shifts, False, ["sat-afternoon"])
    assert fits_availability(shifts, False, ["sat-morning", "sat-afternoon"])


def test_fit_flexible_always():
    assert fits_availability([], True, [])
    assert fits_availability([{"day": "mon", "start": "23:00",
                               "end": "23:59"}], True, ["tue-morning"])


def test_fit_empty_shifts_no_flex():
    assert not fits_availability([], False, ["mon-morning"])


def test_fit_every_shift_must_match():
    shifts = [{"day": "mon", "start": "08:00", "end": "11:00"},
              {"day": "wed", "start": "08:00", "end": "11:00"}]
    assert not fits_availability(shifts, False, ["mon-morning"])
    assert fits_availability(shifts, False, ["mon-morning", "wed-morning"])


def test_haversine_sane():
    # Leppävaara -> Tapiola is ~4-5 km
    d = haversine_km(60.2198, 24.8135, 60.1760, 24.8050)
    assert 3 < d < 6
