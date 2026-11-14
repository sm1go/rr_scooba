"""End-to-end smoke test: the whole demo story through TestClient."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _recorded(name):
    return json.loads((ROOT / "db" / "seed" / "recorded" / name)
                      .read_text(encoding="utf-8"))


def test_demo_story(client):
    # --- Sanna: company + event ------------------------------------------------
    ev = client.get("/api/event").json()
    assert ev["id"] == "ev-2026-11" and ev["companies_declared"] == 40
    lumo = client.get("/api/companies/co-lumo").json()
    assert lumo["contact_name"] == "Sanna Virtanen"

    # --- F01: paste last year's ad -> draft card + trace -----------------------
    ad = _recorded("ad_lumo.json")
    r = client.post("/api/compiler/draft",
                    json={"company_id": "co-lumo", "text": ad["ad_text"]})
    assert r.status_code == 200, r.text
    draft = r.json()
    assert draft["provider"] == "mock"
    card = draft["card"]
    assert len(card["must_haves"]) == 3
    assert all(m["how_we_check"] for m in card["must_haves"])
    assert [t["tool"] for t in draft["trace"]] == [
        "esco_search", "lint_requirements", "pool_preview", "submit_card"]

    # --- F02/F03: fluent Finnish flagged, pool collapses then recovers ---------
    lang_hint = next(h for h in draft["lint"] if h["rule"] == "language_proxy")
    assert lang_hint["pool_before"] == "fewer than 10"
    assert lang_hint["pool_after"] == "20–49"
    assert draft["pool"]["band"] == "fewer than 10"

    # Sanna applies the rewrite and approves
    for need in card["languages"]:
        if need["language"] == "Finnish":
            need.update({"level": "B1", "task": "customer calls",
                         "from_when": "by month 6"})
    r = client.post("/api/pool", json={"card": card})
    assert r.json()["band"] == "20–49"
    r = client.post("/api/cards", json={"card": card})
    assert r.status_code == 200 and r.json()["status"] == "approved"

    # --- F04: Amira's story -> followups -> guarded claims -> evidence card ----
    me = client.get("/api/talents/ta-0427").json()
    assert me["pseudonym"] == "Talent #0427" and "name" not in me
    assert me["spark_budget"] == 3 and me["sparks_used"] == 1

    story = _recorded("amira_story.json")
    r = client.post("/api/story/followups",
                    json={"talent_id": "ta-0427", "transcript": story["transcript"],
                          "language": "ar"})
    assert len(r.json()["questions"]) <= 3

    r = client.post("/api/story/extract",
                    json={"talent_id": "ta-0427", "transcript": story["transcript"],
                          "language": "ar"})
    ext = r.json()
    assert len(ext["claims"]) == 3 and len(ext["refused"]) >= 1
    assert all(c["quote"] in story["transcript"] for c in ext["claims"])
    assert all(c["confirmed"] is False for c in ext["claims"])

    forged = [dict(ext["claims"][0], confirmed=True, quote="a made-up quote")]
    assert client.post("/api/evidence/ta-0427",
                       json={"claims": forged}).status_code == 422
    confirmed = [dict(c, confirmed=True) for c in ext["claims"]]
    r = client.post("/api/evidence/ta-0427", json={"claims": confirmed})
    ec = r.json()
    assert ec["pseudonym"] == "Talent #0427" and len(ec["claims"]) == 3

    # --- F06: Amira sparks the CI line -----------------------------------------
    spark = client.post("/api/sparks", json={
        "talent_id": "ta-0427", "card_id": "card-co-lumo",
        "claim_id": "cl-amira-build", "requirement_id": "req-lumo-1",
        "note": "Your 40-minute pipeline sounds like the one I fixed."}).json()
    assert spark["status"] == "sent" and "revealed_name" not in spark

    inbox = client.get("/api/companies/co-lumo/sparks").json()
    group = next(g for g in inbox["by_requirement"]
                 if g["requirement"]["id"] == "req-lumo-1")
    entry = next(s for s in group["sparks"] if s["id"] == spark["id"])
    assert entry["pseudonym"] == "Talent #0427"
    assert "name" not in entry["claim"] and entry["claim"]["quote"]
    assert "original_language" not in entry["claim"]
    assert "translated" not in entry["claim"]

    # Sanna accepts -> name appears, first free slot booked
    r = client.post(f"/api/sparks/{spark['id']}/respond",
                    json={"decision": "accept"})
    accepted = r.json()
    assert accepted["revealed_name"] == "Amira Haddad"
    assert accepted["slot"]

    meetings = client.get("/api/companies/co-lumo/meetings").json()
    mt = next(m for m in meetings if m["spark_id"] == spark["id"])
    assert mt["talent_name"] == "Amira Haddad"

    # --- F10: one-screen sheet = exactly the card must-haves --------------------
    sheet = client.get(f"/api/meetings/{mt['id']}/sheet").json()
    assert len(sheet["questions"]) == 3
    assert {q["requirement_id"] for q in sheet["questions"]} == {
        "req-lumo-1", "req-lumo-2", "req-lumo-3"}
    sheet = client.post(f"/api/meetings/{mt['id']}/ticks", json={"ticks": [
        {"requirement_id": "req-lumo-1", "seen": True,
         "note": "30 -> 6 min, showed the graph"},
        {"requirement_id": "req-lumo-2", "seen": True},
        {"requirement_id": "req-lumo-3", "seen": False}]}).json()
    assert sum(1 for t in sheet["ticks"] if t["seen"]) == 2

    # --- F13: closure with card chips + F14 banner ------------------------------
    r = client.post(f"/api/meetings/{mt['id']}/closure", json={
        "outcome": "next_step", "reason_chips": ["req-lumo-1"],
        "next_step": "paid trial day on Thursday"})
    body = r.json()
    assert "don't sign before the decision" in body["support_banner"]

    # a bogus chip is refused
    r = client.post(f"/api/meetings/{mt['id']}/closure", json={
        "outcome": "not_now", "reason_chips": ["vibes were off"]})
    assert r.status_code == 422

    # --- organiser + trust + audit ---------------------------------------------
    ov = client.get("/api/organiser/overview").json()
    assert ov["cards_approved"] >= 12 and ov["meetings"] >= 1
    tw = client.get("/api/trust/twin-report").json()
    assert tw["provider"] == "mock" and tw["placeholder"] is True
    assert tw["passed"] is False and tw["pairs"] == 0
    log = client.get("/api/audit").json()
    actors = {e["actor"] for e in log}
    assert actors == {"ai", "human"}
    assert len(log) <= 50


def test_spark_budget_conflict(client):
    # Amira has 1 sent spark + budget 3 -> the 4th send is a 409
    for claim, req in (("cl-amira-build", "req-lumo-1"),
                       ("cl-amira-pytest", "req-lumo-3")):
        r = client.post("/api/sparks", json={
            "talent_id": "ta-0427", "card_id": "card-co-lumo",
            "claim_id": claim, "requirement_id": req})
        assert r.status_code == 201
    r = client.post("/api/sparks", json={
        "talent_id": "ta-0427", "card_id": "card-co-lumo",
        "claim_id": "cl-amira-fastapi", "requirement_id": "req-lumo-2"})
    assert r.status_code == 409


def test_twin_report_does_not_claim_a_placeholder_pass(client):
    report = client.get("/api/trust/twin-report").json()
    assert report["placeholder"] is True
    assert report["passed"] is False
    assert report["pairs"] == 0
    assert report["variants"] == []
