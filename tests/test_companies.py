"""Owner feedback round — company profiles, need cards everywhere,
event summaries and after-history."""
import json

from app.api import db as db_mod

E1 = "ev-2027-03"
E2 = "ev-2027-02"
E0 = "ev-2026-10"

PALETTE = {"#1e3a8a", "#14532d", "#7c2d12", "#4a044e",
           "#713f12", "#0c4a6e", "#831843", "#3f3f46"}


def _db():
    return db_mod.connect()


def _event_employers(conn, event_id):
    return [r["employer_id"] for r in conn.execute(
        "SELECT employer_id FROM employer_event WHERE event_id=?",
        (event_id,))]


def test_company_profile_fields(client):
    conn = _db()
    eid = _event_employers(conn, E2)[0]
    conn.close()
    r = client.get(f"/api/companies/{eid}")
    assert r.status_code == 200
    c = r.json()
    for k in ("name", "tagline", "field", "size_band", "founded",
              "work_languages", "logo_color", "about", "how_we_welcome",
              "contact_name", "contact_email", "contact_phone",
              "jobs", "contracts", "badges", "events", "commitments"):
        assert k in c, k
    assert c["size_band"] in ("1", "2-9", "10-49", "50-249", "250+")
    assert isinstance(c["work_languages"], list)
    assert len(c["about"].split(".")) >= 2


def test_company_profile_open_jobs_only_and_no_private_data(client):
    conn = _db()
    eid = conn.execute(
        "SELECT id FROM employer WHERE id IN (SELECT employer_id FROM job)"
        " LIMIT 1").fetchone()["id"]
    closed = conn.execute(
        "SELECT COUNT(*) c FROM job WHERE employer_id=? AND status!='open'",
        (eid,)).fetchone()["c"]
    conn.close()
    r = client.get(f"/api/companies/{eid}")
    jobs = r.json()["jobs"]
    assert all(j.get("status", "open") == "open" or "status" not in j
               for j in jobs)
    if closed:
        assert all(j["status"] == "open" for j in jobs)
    # no private user data anywhere in the payload
    body = json.dumps(r.json())
    for banned in ("@example.com", "u-aino", "password"):
        assert banned not in body


def test_company_profile_404(client):
    assert client.get("/api/companies/emp-nope").status_code == 404


def test_logo_color_in_palette(client):
    conn = _db()
    for r in conn.execute("SELECT logo_color FROM employer"):
        assert r["logo_color"] in PALETTE, r["logo_color"]
    conn.close()


def test_all_e2_and_e0_employers_have_need_cards(client):
    conn = _db()
    for ev in (E2, E0):
        for eid in _event_employers(conn, ev):
            nc = conn.execute(
                "SELECT need_card FROM employer_event WHERE event_id=?"
                " AND employer_id=?", (ev, eid)).fetchone()["need_card"]
            assert nc, f"{ev} {eid} has no need card"
            card = json.loads(nc)
            assert card["first_week"], "first_week empty"
            assert len(card["must_haves"]) <= 3
            for m in card["must_haves"]:
                assert m["why"], f"must_have without why: {m}"
            assert card["will_teach"]
            open_jobs = {r["id"] for r in conn.execute(
                "SELECT id FROM job WHERE employer_id=? AND status='open'",
                (eid,))}
            assert set(card["job_ids"]) <= open_jobs
    conn.close()


def test_need_cards_pass_wording_checker(client):
    from app.api.rules import lint
    conn = _db()
    for ev in (E1, E2, E0):
        for r in conn.execute(
                "SELECT need_card FROM employer_event WHERE event_id=?"
                " AND need_card IS NOT NULL", (ev,)):
            card = json.loads(r["need_card"])
            mhs = card.get("must_haves") or []
            job_like = {
                "title": "", "pay_note": "", "experience_note": "",
                "onboarding": "", "apply_question": "", "lifting": "",
                "duties": card.get("first_week") or [],
                "qualifications":
                    [m.get("text", "") for m in mhs]
                    + [m.get("why", "") for m in mhs]
                    + list(card.get("will_teach") or []),
                "languages": [
                    {"language": l.get("name"), "level": l.get("level"),
                     "task": l.get("task")}
                    for l in card.get("languages") or []],
            }
            issues = lint.blocking_issues(job_like)
            assert issues == [], (ev, issues)
    conn.close()


def test_e2_needs_endpoint_returns_cards(client):
    r = client.get(f"/api/events/{E2}/needs")
    assert r.status_code == 200
    cards = r.json()["cards"]
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) c FROM employer_event WHERE event_id=?",
        (E2,)).fetchone()["c"]
    conn.close()
    assert len(cards) == n
    assert all(c["need"] for c in cards)


def test_e0_summary_matches_db(client):
    r = client.get(f"/api/events/{E0}/summary")
    assert r.status_code == 200
    s = r.json()
    conn = _db()
    assert s["employers"] == conn.execute(
        "SELECT COUNT(DISTINCT employer_id) c FROM employer_event"
        " WHERE event_id=?", (E0,)).fetchone()["c"]
    assert s["participants"] == conn.execute(
        "SELECT COUNT(*) c FROM talent_registration WHERE event_id=?"
        " AND status='registered'", (E0,)).fetchone()["c"]
    assert s["talks"] == conn.execute(
        "SELECT COUNT(*) c FROM event_talk WHERE event_id=?",
        (E0,)).fetchone()["c"]
    assert s["next_steps"] == conn.execute(
        "SELECT COUNT(*) c FROM event_talk WHERE event_id=?"
        " AND outcome='next_step'", (E0,)).fetchone()["c"]
    assert s["hired"] == conn.execute(
        "SELECT COUNT(*) c FROM badge WHERE event_id=? AND kind='hired'",
        (E0,)).fetchone()["c"]
    conn.close()
    # aggregate only — no personal data
    body = json.dumps(s)
    for banned in ("aino", "pekka", "@example.com", "Korhonen"):
        assert banned not in body.lower(), banned


def test_summary_rejects_unfinished_event(client):
    # decision: 409 for unfinished events (demo clock at registration
    # stage -> E1 still ahead, E2 already finished)
    for ev, want in ((E1, 409), (E2, 200)):
        r = client.get(f"/api/events/{ev}/summary")
        assert r.status_code == want, (ev, r.status_code, r.text)


def test_after_endpoint_history_for_aino(client, aino):
    r = client.get(f"/api/events/{E2}/after", headers=aino)
    assert r.status_code == 200
    d = r.json()
    assert any(s["event_id"] == E0 for s in d["summaries"])
    mine = [h for h in d["mine"] if h["event_id"] == E0]
    assert len(mine) == 1
    h = mine[0]
    assert len(h["talks"]) >= 2
    assert h["records"]
    assert h["badges"]
    assert len(h["people"]) >= 2


def test_after_endpoint_no_history_for_new_user(client, register_resident):
    hdr = register_resident(email="fresh@example.com")
    r = client.get(f"/api/events/{E2}/after", headers=hdr)
    assert r.status_code == 200
    assert r.json()["mine"] == []


def test_after_endpoint_public_for_anonymous(client):
    r = client.get(f"/api/events/{E1}/after")
    assert r.status_code == 200
    d = r.json()
    assert d["mine"] == []
    assert any(s["event_id"] == E0 for s in d["summaries"])
