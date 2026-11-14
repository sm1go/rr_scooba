"""Spec v3 additions: config, AI helpers (fake clients), commute, support,
event mode. No test calls the network — fake clients are injected."""

from __future__ import annotations

import json

import pytest

from tests.conftest import login

pytestmark = pytest.mark.usefixtures("client")


class FakeLLM:
    """Returns canned JSON; records calls."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = 0

    def chat(self, messages):
        self.calls += 1
        if not self.replies:
            raise AssertionError("FakeLLM got an unexpected call")
        return self.replies.pop(0)


class FakeDigitransit:
    """Recorded-shape planConnection node (docs-confirmed fields)."""

    def __init__(self, node=None):
        self.calls = 0
        self.node = node or {
            "start": "2026-11-16T08:31:00+02:00",
            "end": "2026-11-16T08:55:00+02:00",
            "duration": 1440, "walkDistance": 630,
            "legs": [
                {"mode": "WALK", "distance": 420, "duration": 360,
                 "start": {"scheduledTime": "2026-11-16T08:31:00+02:00"},
                 "end": {"scheduledTime": "2026-11-16T08:37:00+02:00"},
                 "from": {"name": "Origin", "stop": None},
                 "to": {"name": "Matinkylä", "stop": {"name": "Matinkylä"}},
                 "trip": None},
                {"mode": "BUS", "distance": 3100, "duration": 780,
                 "start": {"scheduledTime": "2026-11-16T08:37:00+02:00"},
                 "end": {"scheduledTime": "2026-11-16T08:50:00+02:00"},
                 "from": {"name": "Matinkylä", "stop": {"name": "Matinkylä"}},
                 "to": {"name": "Olari", "stop": {"name": "Olarinniitty"}},
                 "trip": {"routeShortName": "533"}},
            ],
        }

    def plan(self, o_lat, o_lon, d_lat, d_lon, arrive_by):
        self.calls += 1
        return self.node


@pytest.fixture()
def ai_on(monkeypatch):
    from app.api import llm, settings
    monkeypatch.setattr(settings, "ai_enabled", lambda: True)
    yield
    llm.set_client(None)


@pytest.fixture()
def commute_on(monkeypatch):
    from app.api import digitransit, settings
    monkeypatch.setattr(settings, "commute_enabled", lambda: True)
    yield
    digitransit.set_client(None)


@pytest.fixture(autouse=True)
def _rate_reset():
    from app.api.routers import ai as ai_router
    ai_router._reset_rate_limit()
    yield


# --- config -------------------------------------------------------------------

def test_config_flags_off_without_keys(client, no_keys):
    r = client.get("/api/config")
    assert r.status_code == 200
    assert r.json() == {"ai": False, "commute": False}


@pytest.fixture()
def no_keys(monkeypatch):
    """Simulate the no-key machine even when a real .env key exists."""
    from app.api import settings
    monkeypatch.setattr(settings, "ai_enabled", lambda: False)
    monkeypatch.setattr(settings, "commute_enabled", lambda: False)
    yield


# --- /api/ai/filters ------------------------------------------------------------

def test_filters_rules_retiree_sentence(client):
    r = client.post("/api/ai/filters", json={
        "text": "two mornings a week near Matinkylä", "ui_language": "en"})
    assert r.status_code == 200
    out = r.json()
    assert out["source"] == "rules"
    assert out["filters"]["district"] == "matinkyla"
    assert set(out["filters"]["slots"]) == {
        f"{d}-morning" for d in ("mon", "tue", "wed", "thu", "fri")}


def test_filters_rules_student_finnish(client):
    r = client.post("/api/ai/filters", json={
        "text": "opiskelija iltaisin viikonloppuisin", "ui_language": "fi"})
    out = r.json()
    assert out["source"] == "rules"
    assert "students" in out["filters"]["labels"]
    assert set(out["filters"]["slots"]) == {"sat-evening", "sun-evening"}


def test_filters_rules_needs_and_lifting_note(client):
    r = client.post("/api/ai/filters", json={
        "text": "step-free entrance and seated work, no heavy lifting",
        "ui_language": "en"})
    out = r.json()
    assert set(out["filters"]["needs"]) == {
        "step_free_entrance", "seated_work"}
    assert out["filters"]["needs_mode"] == "yes"
    assert any("lifting" in n for n in out["not_understood"])


def test_filters_ai_path_whitelist(client, ai_on):
    from app.api import llm
    llm.set_client(FakeLLM({
        "district": "matinkyla", "km": 3, "favourite_color": "blue",
        "near_station": True, "labels": ["retirement", "bogus"],
        "explanation": ["Area you named."], "not_understood": []}))
    r = client.post("/api/ai/filters",
                    json={"text": "anything", "ui_language": "en"})
    out = r.json()
    assert out["source"] == "ai"
    assert out["filters"] == {"district": "matinkyla", "km": 3,
                             "near_station": True, "labels": ["retirement"]}
    assert any("favourite_color" in n for n in out["not_understood"])


def test_filters_rate_limit(client):
    for _ in range(10):
        r = client.post("/api/ai/filters",
                        json={"text": "student", "ui_language": "en"})
        assert r.status_code == 200
    r = client.post("/api/ai/filters",
                    json={"text": "student", "ui_language": "en"})
    assert r.status_code == 429


# --- /api/ai/job-draft -----------------------------------------------------------

GOOD_DRAFT = {
    "title": "Café assistant", "employer_name": "Kahvila X",
    "field": "restaurant", "duties": ["Serve customers"], "address": "Iso Omena",
    "work_mode": "on_site", "pay_amount": 15.5, "pay_unit": "hour",
    "pay_note": None, "shifts": [{"day": "sat", "start": "10:00",
                                  "end": "16:00"}],
    "schedule_flexible": False, "hours_min": 10, "hours_max": 20,
    "contract": "part_time_wrong", "experience": "none",
    "experience_note": None, "qualifications": [],
    "onboarding": "We show you", "languages": [
        {"language": "Finnish", "level": "B1", "task": "customers"},
        {"language": "English", "level": "X9", "task": None}],
    "lifting": None, "contact": "call 040",
    "missing": ["lifting"], "wording_warnings": ["young team"],
    "source_quotes": {"title": "Café assistant"},
}


def test_job_draft_validation(client, sanna, ai_on):
    from app.api import llm
    fake = FakeLLM(dict(GOOD_DRAFT))
    llm.set_client(fake)
    r = client.post("/api/ai/job-draft", headers=sanna,
                    json={"text": "notice text"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["draft"]["contract"] is None            # bad enum -> null
    assert "contract" in out["missing"]
    assert out["draft"]["languages"][1]["level"] is None   # bad CEFR
    assert out["wording_warnings"] == ["young team"]   # kept out of fields
    assert "young" not in json.dumps(out["draft"]).lower()
    # nothing saved
    jobs = client.get("/api/jobs").json()["jobs"]
    assert all(j["title"] != "Café assistant" for j in jobs)


def test_job_draft_503_without_ai(client, sanna):
    r = client.post("/api/ai/job-draft", headers=sanna,
                    json={"text": "x"})
    assert r.status_code == 503


# --- /api/ai/simplify -------------------------------------------------------------

def _open_job_id(client):
    return client.get("/api/jobs").json()["jobs"][0]["id"]


def test_simplify_rejects_changed_numbers(client, ai_on):
    from app.api import llm
    job = client.get("/api/jobs").json()["jobs"][0]
    sections = {"title": job["title"], "duties": job["duties"],
                "experience_note": job["experience_note"],
                "qualifications": job["qualifications"],
                "onboarding": job["onboarding"] or None,
                "pay_note": "Pay is 99 euros", "lifting": job["lifting"],
                "apply_question": job["apply_question"] or None,
                "language_tasks": [l["task"] for l in job["languages"]
                                   if l.get("task")] or None}
    llm.set_client(FakeLLM(dict(sections), dict(sections)))
    r = client.post("/api/ai/simplify", json={"job_id": job["id"],
                                              "language": "fi"})
    assert r.status_code == 502                      # '99' not in source


def test_simplify_ok_and_cache(client, ai_on):
    from app.api import llm
    job = client.get("/api/jobs").json()["jobs"][0]
    sections = {
        "title": "Easy title",
        "duties": ["easy duty"] * len(job["duties"]),
        "experience_note": job["experience_note"] or None,
        "qualifications": ["easy qual"] * len(job["qualifications"]),
        "onboarding": job["onboarding"] or None,
        "pay_note": job["pay_note"] or None,
        "lifting": job["lifting"],
        "apply_question": job["apply_question"] or None,
        "language_tasks": [l["task"] for l in job["languages"]
                           if l.get("task")] or None,
    }
    fake = FakeLLM(dict(sections))
    llm.set_client(fake)
    r1 = client.post("/api/ai/simplify", json={"job_id": job["id"],
                                               "language": "sv"})
    assert r1.status_code == 200 and r1.json()["machine"] is True
    r2 = client.post("/api/ai/simplify", json={"job_id": job["id"],
                                               "language": "sv"})
    assert r2.status_code == 200 and fake.calls == 1   # cache hit


def test_simplify_list_length_mismatch(client, ai_on):
    from app.api import llm
    job = client.get("/api/jobs").json()["jobs"][0]
    sections = {"title": "x", "duties": ["only one"],
                "experience_note": None, "qualifications": [],
                "onboarding": None, "pay_note": None, "lifting": None,
                "apply_question": None, "language_tasks": None}
    llm.set_client(FakeLLM(dict(sections), dict(sections)))
    r = client.post("/api/ai/simplify", json={"job_id": job["id"],
                                              "language": "uk"})
    assert r.status_code == 502


# --- advisor helpers ---------------------------------------------------------------

def test_advisor_questions_rules_fallback(client, advisor):
    from app.api.rules.call_script import unknown_fields
    r = client.post("/api/ai/advisor/questions", headers=advisor,
                    json={"job_id": _open_job_id(client)})
    assert r.status_code == 200
    out = r.json()
    assert out["source"] == "rules"
    assert out["opening"]
    asked = {q["field"] for q in out["questions"]}
    assert asked  # covers the unknown fields, one question each
    assert all(f in out["kinds"] for f in asked)


def test_advisor_note_validation(client, advisor, ai_on):
    from app.api import llm
    llm.set_client(FakeLLM({
        "type": "job_conditions", "person_name": "Matti",
        "contact_method": "carrier_pigeon", "contact_value": None,
        "job_hint": "the café", "kind": "nonsense",
        "message": "Steps at the door.",
        "conditions": [{"key": "step_free_entrance", "value": "no",
                        "note": "three steps"},
                       {"key": "bogus", "value": "yes"}],
        "consent_mentioned": True,
        "left_out": ["blood pressure reading — health, not recorded"]}))
    r = client.post("/api/ai/advisor/note", headers=advisor,
                    json={"text": "Matti said three steps at the door."})
    out = r.json()
    assert out["contact_method"] is None               # bad enum dropped
    assert out["kind"] is None
    assert out["conditions"] == [{"key": "step_free_entrance", "value": "no",
                                  "note": "three steps"}]
    assert out["consent_mentioned"] is True
    # nothing persisted
    j = client.get("/api/jobs").json()["jobs"][0]
    assert all(c["source"] != "advisor" or c["key"] != "step_free_entrance"
               or c["checked_at"] != "2026-11-15" for c in j["conditions"])


def test_advisor_note_503_without_ai(client, advisor):
    r = client.post("/api/ai/advisor/note", headers=advisor,
                    json={"text": "x"})
    assert r.status_code == 503


# --- stations / commute -------------------------------------------------------------

def test_nearest_station_and_label(client):
    jobs = client.get("/api/jobs").json()["jobs"]
    with_ns = [j for j in jobs if j["nearest_station"]]
    assert with_ns, "expected stations next to on-site jobs"
    near = [j for j in with_ns if j["nearest_station"]["distance_m"] <= 800]
    assert near and all(any(l["id"] == "near_station" for l in j["labels"])
                        for j in near)


def test_near_station_filter(client):
    r = client.get("/api/jobs?near_station=1")
    assert r.status_code == 200
    for j in r.json()["jobs"]:
        assert j["nearest_station"]["distance_m"] <= 800


def test_commute_503_without_key(client, no_keys):
    r = client.get("/api/commute?job_id=job-cafe-weekday&district=matinkyla")
    assert r.status_code == 503


def test_commute_with_fake_client_and_cache(client, commute_on):
    from app.api import digitransit
    fake = FakeDigitransit()
    digitransit.set_client(fake)
    r = client.get("/api/commute?job_id=job-cafe-weekday&district=matinkyla")
    assert r.status_code == 200
    out = r.json()
    assert out["minutes"] == 24 and out["source"] == "HSL"
    assert out["legs"][1]["route"] == "533"
    r2 = client.get("/api/commute?job_id=job-cafe-weekday&district=matinkyla")
    assert r2.status_code == 200 and fake.calls == 1    # cache hit


def test_commute_max_filter(client, commute_on):
    from app.api import digitransit
    digitransit.set_client(FakeDigitransit())
    r = client.get("/api/jobs?district=matinkyla&commute_max=20")
    assert r.status_code == 200
    for j in r.json()["jobs"]:
        assert "commute" in j
        if j["commute"] is not None and j["commute"].get("minutes"):
            assert j["commute"]["minutes"] <= 20
    r = client.get("/api/jobs?commute_max=20")          # needs district
    assert r.status_code == 422


# --- support -------------------------------------------------------------------------

def test_support_catalogue_and_rule(client):
    r = client.get("/api/support")
    assert r.status_code == 200
    data = r.json()
    assert data["programs"] and data.get("meta")
    from app.api.support import matching_programs, rule_matches
    job = {"contract": "permanent", "hours_min": 30, "hours_max": 37}
    assert rule_matches("always", job)
    assert rule_matches("contract in (permanent, fixed_term) "
                        "and hours_min >= 20", job)
    assert not rule_matches("contract in (gig)", job)
    assert not rule_matches("hours_max >= 40", {"hours_max": None})
    matched = matching_programs(job)
    assert isinstance(matched, list)


def test_no_programme_ids_on_applications(client, aino):
    r = client.get("/api/me/applications", headers=aino)
    assert r.status_code == 200
    blob = json.dumps(r.json()).lower()
    for pid in ("pay_subsidy", "program", "eligibility", "situation"):
        assert pid not in blob


def test_employer_support_help_kind(client, sanna):
    r = client.post("/api/help-requests", headers=sanna, json={
        "kind": "employer_support", "message": "Call me about pay subsidy",
        "consent": True, "contact_method": "email",
        "contact_value": "sanna@example.com"})
    assert r.status_code == 201
    assert r.json()["kind"] == "employer_support"


# --- event mode ------------------------------------------------------------------------

def test_event_has_booths_and_jobs(client):
    ev = client.get("/api/event").json()
    assert ev["event"]["id"] == "ev-2026-11"
    emp = next(e for e in ev["employers"] if e["id"] == "emp-cafe-koivu")
    assert emp["booth"] == "A1" and emp["jobs"]


def test_event_plan_and_visitor_code(client, aino):
    r = client.get("/api/me/event-plan", headers=aino)
    assert r.status_code == 200
    out = r.json()
    assert out["code"] == "5821"
    assert [b["booth"] for b in out["booths"]] == \
        sorted(b["booth"] for b in out["booths"])
    employers = client.get("/api/event").json()["employers"]
    other = next(e["id"] for e in employers
                 if e["id"] not in {b["employer_id"] for b in out["booths"]})
    r = client.put(f"/api/me/event-plan/{other}", headers=aino)
    assert r.status_code == 201
    assert any(b["employer_id"] == other for b in r.json()["booths"])
    r = client.delete(f"/api/me/event-plan/{other}", headers=aino)
    assert r.status_code == 200
    assert all(b["employer_id"] != other for b in r.json()["booths"])


def test_talk_record_answer_and_privacy(client, sanna, register_resident):
    # seeded: et-001 answered, et-002 talked -> code 9042 is a duplicate
    r = client.post("/api/employer/event/talks", headers=sanna,
                    json={"code": "9042"})
    assert r.status_code == 409
    r = client.post("/api/employer/event/talks", headers=sanna,
                    json={"code": "0000"})
    assert r.status_code == 404
    # a fresh resident gets a code on first plan view
    hdrs = register_resident(email="visitor@example.com", name="Ville Vieras")
    code = client.get("/api/me/event-plan", headers=hdrs).json()["code"]
    assert code and len(code) == 4
    # before a talk the employer sees only a count
    ev = client.get("/api/employer/event", headers=sanna).json()
    assert ev["visitors_planned"] >= 1
    assert not any(t.get("person_name") == "Ville Vieras"
                   for t in ev["talks"])
    r = client.post("/api/employer/event/talks", headers=sanna,
                    json={"code": code})
    assert r.status_code == 201
    assert r.json()["person_name"] == "Ville Vieras"
    assert r.json()["person_contact_value"]
    talk_id = r.json()["id"]
    r = client.post(f"/api/employer/event/talks/{talk_id}/answer",
                    headers=sanna,
                    json={"outcome": "next_step", "employer_note": ""})
    assert r.status_code == 422                        # note required
    r = client.post(f"/api/employer/event/talks/{talk_id}/answer",
                    headers=sanna,
                    json={"outcome": "next_step",
                          "employer_note": "Come Monday 9:00."})
    assert r.status_code == 200 and r.json()["status"] == "answered"
    # resident sees the answer + note on their tracker
    talks = client.get("/api/me/event-talks", headers=hdrs).json()["talks"]
    assert talks[0]["employer_note"] == "Come Monday 9:00."
    assert talks[0]["employer_name"]
