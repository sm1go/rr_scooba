"""Occupation search: keywords from free text, q matching, hours_min."""

from app.api.routers.ai import _clean_filters
from app.api.routers.jobs import text_matches
from app.api.rules.filter_words import parse


def test_text_matches_word_family_and_alternatives():
    assert text_matches("welder", "Welding of steel frames")
    assert text_matches("electrician,welder", "TIG welder, stainless steel")
    assert text_matches("it support", "IT support desk")
    assert not text_matches("weld", "Field work in parks")


def test_rules_find_occupation_in_other_languages():
    for text in ("chcę pracować jako spawacz", "olen hitsaaja", "welder"):
        out = parse(text)
        assert out["filters"]["keywords"][0] == "welder"
        assert "field" not in out["filters"]


def test_rules_say_when_nothing_was_understood():
    out = parse("qwerty blah")
    assert out["filters"] == {}
    assert out["not_understood"]


def test_ai_keywords_are_validated():
    out = _clean_filters({"keywords": ["welder", "", 5, "x" * 99],
                          "hours_min": 35})
    assert out["filters"]["keywords"] == ["welder", "x" * 40]
    assert out["filters"]["hours_min"] == 35


def test_jobs_q_and_hours_min(client):
    all_jobs = client.get("/api/jobs").json()["jobs"]
    title = all_jobs[0]["title"].split()[0]
    hits = client.get("/api/jobs", params={"q": title}).json()["jobs"]
    assert hits and all(title.lower()[:4] in (j["title"] + " ".join(j["duties"])).lower()
                        for j in hits)
    assert client.get("/api/jobs", params={"q": "zzzzqqq"}).json()["count"] == 0
    full = client.get("/api/jobs", params={"hours_min": 35}).json()["jobs"]
    assert all(j["hours_max"] is not None and j["hours_max"] >= 35 for j in full)
