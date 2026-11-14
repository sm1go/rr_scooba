"""Working-week bundles: interval/compatible helpers + /api/bundles rules."""

from __future__ import annotations

from app.api.routers.jobs import _compatible, _intervals

J = {"employer_id": "e1", "district": "d1", "lat": 60.2, "lon": 24.8,
     "work_mode": "on_site", "schedule_flexible": False,
     "hours_min": None, "hours_max": 10, "pay_unit": "hour",
     "pay_amount": 15.0, "shifts": [], "commitments": []}


def _job(day="mon", start="09:00", end="12:00", **kw):
    j = {**J, "shifts": [{"day": day, "start": start, "end": end}]}
    j.update(kw)
    return j


def test_intervals_splits_overnight():
    iv = _intervals([{"day": "fri", "start": "22:00", "end": "02:00"}])
    assert (4, 22 * 60, 1440) in iv
    assert (5, 0, 2 * 60) in iv


def test_compatible_rejects_overlap():
    a = _job(end="13:00")
    b = _job(start="12:00", employer_id="e2")
    assert not _compatible(a, b)


def test_compatible_gap_rules():
    a = _job(end="12:00")
    same = _job(start="12:15", employer_id="e2")
    ok30 = _job(start="12:30", employer_id="e2")
    far = _job(start="12:45", employer_id="e2", district="d2")
    far_ok = _job(start="13:00", employer_id="e2", district="d2")
    assert not _compatible(a, same)          # 15 min gap, same district
    assert _compatible(a, ok30)            # 30 min same district ok
    assert not _compatible(a, far)         # 45 min across districts
    assert _compatible(a, far_ok)          # 60 min across districts ok


def test_compatible_same_employer_rejected():
    a = _job(end="10:00")
    b = _job(start="14:00")
    assert not _compatible(a, b)


def _check_bundle(b, target=30):
    assert 2 <= len(b["jobs"]) <= 3
    assert b["hours_max"] >= target - 4
    assert b["hours_min"] <= target + 4
    for j in b["jobs"]:
        assert j["work_mode"] != "remote"
    # pairwise day-gap check on the public week grid
    by_day: dict[str, list] = {}
    for j in b["jobs"]:
        for s in j["shifts"]:
            by_day.setdefault(s["day"], []).append(
                (s["start"], s["end"], j["district"]))
    for ivs in by_day.values():
        ivs.sort()
        for (s1, e1, d1), (s2, e2, d2) in zip(ivs, ivs[1:]):
            gap = (int(s2[:2]) * 60 + int(s2[3:])) \
                  - (int(e1[:2]) * 60 + int(e1[3:]))
            assert gap >= (30 if d1 == d2 else 60), (s1, e1, s2, d1, d2)


def test_bundles_endpoint_rules(client):
    r = client.get("/api/bundles?hours=30")
    assert r.status_code == 200, r.text
    d = r.json()
    used: dict[str, int] = {}
    for b in d["bundles"]:
        _check_bundle(b)
        for j in b["jobs"]:
            used[j["id"]] = used.get(j["id"], 0) + 1
    assert all(n <= 2 for n in used.values())


def test_bundles_slots_filter(client):
    # weekday mornings only -> every shift in every bundle inside those
    slots = ",".join(f"{d}-morning"
                     for d in ("mon", "tue", "wed", "thu", "fri"))
    r = client.get(f"/api/bundles?hours=30&slots={slots}")
    assert r.status_code == 200
    for b in r.json()["bundles"]:
        for j in b["jobs"]:
            for s in j["shifts"]:
                assert s["day"] in ("mon", "tue", "wed", "thu", "fri")
                assert s["end"] <= "12:00"


def test_bundles_hours8_excludes_bigger_jobs(client):
    r = client.get("/api/bundles?hours=8")
    assert r.status_code == 200
    for b in r.json()["bundles"]:
        for j in b["jobs"]:
            assert j["hours_max"] is None or j["hours_max"] < 8
