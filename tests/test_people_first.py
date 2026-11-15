"""Spec §7 — people first: personal QR pass, badges, networking."""
from app.api import db as db_mod

E1 = "ev-2027-03"
E0 = "ev-2026-10"
AINO = "u-aino"
SANNA = "u-sanna"
PEKKA = "u-pekka"


def _db(client):
    return db_mod.connect()


def _pass_token(conn, event_id, user_id):
    return conn.execute(
        "SELECT token FROM event_pass WHERE event_id=? AND user_id=?",
        (event_id, user_id)).fetchone()["token"]


def test_passes_exist_for_all_participants(client):
    conn = _db(client)
    regs = conn.execute(
        "SELECT user_id FROM talent_registration WHERE event_id=?"
        " AND status='registered'", (E1,)).fetchall()
    for r in regs:
        tok = _pass_token(conn, E1, r["user_id"])
        assert len(tok) == 22
    # every employer user of an E1 employer has a pass
    for u in conn.execute(
            "SELECT id FROM user WHERE role='employer' AND employer_id IN"
            " (SELECT employer_id FROM employer_event WHERE event_id=?)",
            (E1,)):
        assert _pass_token(conn, E1, u["id"])
    conn.close()


def _reg_aino(client, aino):
    client.post(f"/api/events/{E1}/register", headers=aino,
                json={"time_group": "A", "card": {
                    "looking_for": "x", "done": [{"text": "y"}],
                    "district": "", "availability": []}})


def test_my_pass_endpoint(client, aino):
    _reg_aino(client, aino)
    r = client.get(f"/api/me/events/{E1}/pass", headers=aino)
    assert r.status_code == 200
    assert len(r.json()["token"]) == 22
    assert r.json()["visitor_code"]


def test_scanned_profile_access_rules(client, sanna, advisor, aino):
    _reg_aino(client, aino)
    conn = _db(client)
    tok = _pass_token(conn, E1, AINO)
    conn.close()
    # anonymous -> 401
    assert client.get(f"/api/p/{tok}").status_code == 401
    # signed-in but not in the event -> 403
    other = client.post("/api/auth/register", json={
        "email": "outsider@example.com", "password": "demo1234",
        "name": "Out Sider", "role": "resident"})
    hdr = {"Authorization": f"Bearer {other.json()['token']}"}
    assert client.get(f"/api/p/{tok}", headers=hdr).status_code == 403
    # E1 employer user -> 200
    r = client.get(f"/api/p/{tok}", headers=sanna)
    assert r.status_code == 200
    d = r.json()
    assert d["first_name"] and d["role"] == "resident"
    assert d["viewer_employer"] is True
    # privacy: no contact unless shared (Aino shares nothing by default)
    assert "email" not in d["contact"] and "phone" not in d["contact"]
    # badges from earlier events show up
    labels = {(b["kind"], b["label"]) for b in d["badges"]}
    assert ("attended", "attended") in labels
    assert ("organizer", "pitched") in labels
    assert ("kudos", "explains_clearly") in labels
    # unknown token -> 404
    assert client.get("/api/p/nonononono0000000000",
                      headers=sanna).status_code == 404


def test_share_flags_gate_contact(client, aino, sanna):
    _reg_aino(client, aino)
    conn = _db(client)
    tok = _pass_token(conn, E1, AINO)
    conn.close()
    # turn sharing on via the profile endpoint
    prof = client.get("/api/me/profile", headers=aino).json()
    prof["share_email"] = True
    prof["share_phone"] = True
    prof["public_link"] = "https://example.com/aino"
    assert client.put("/api/me/profile", headers=aino,
                      json=prof).status_code == 200
    d = client.get(f"/api/p/{tok}", headers=sanna).json()
    assert d["contact"]["email"] == "aino@example.com"
    assert d["contact"]["phone"]
    assert d["contact"]["public_link"] == "https://example.com/aino"
    # and off again hides them
    prof["share_email"] = False
    prof["share_phone"] = False
    client.put("/api/me/profile", headers=aino, json=prof)
    d = client.get(f"/api/p/{tok}", headers=sanna).json()
    assert "email" not in d["contact"] and "phone" not in d["contact"]


def test_scan_creates_scan_connection_and_attended(client, sanna, pekka):
    conn = _db(client)
    tok = _pass_token(conn, E1, "u-talent01")
    before_scans = conn.execute(
        "SELECT COUNT(*) c FROM event_scan WHERE event_id=?", (E1,)).fetchone()["c"]
    conn.close()
    d = client.get(f"/api/p/{tok}", headers=sanna).json()
    conn = _db(client)
    assert conn.execute(
        "SELECT 1 FROM event_scan WHERE event_id=? AND scanner_id=?"
        " AND scanned_id=?", (E1, SANNA, "u-talent01")).fetchone()
    a, b = sorted([SANNA, "u-talent01"])
    assert conn.execute(
        "SELECT 1 FROM connection WHERE user_a=? AND user_b=? AND event_id=?",
        (a, b, E1)).fetchone()
    assert conn.execute(
        "SELECT 1 FROM badge WHERE user_id=? AND event_id=?"
        " AND kind='attended'", ("u-talent01", E1)).fetchone()
    # second scan idempotent
    client.get(f"/api/p/{tok}", headers=sanna)
    after = conn.execute(
        "SELECT COUNT(*) c FROM event_scan WHERE event_id=?", (E1,)).fetchone()["c"]
    assert after == before_scans + 1
    assert conn.execute(
        "SELECT COUNT(*) c FROM connection WHERE user_a=? AND user_b=?"
        " AND event_id=?", (a, b, E1)).fetchone()["c"] == 1
    conn.close()


def test_kudos_rules(client, sanna, advisor):
    conn = _db(client)
    tok = _pass_token(conn, E1, "u-talent11")
    conn.close()
    # no relation yet -> 403
    r = client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                    json={"user_id": "u-talent11", "label": "reliable"})
    assert r.status_code == 403
    # scan creates the relation -> allowed
    client.get(f"/api/p/{tok}", headers=sanna)
    r = client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                    json={"user_id": "u-talent11", "label": "reliable",
                          "note": "Calm and on time"})
    assert r.status_code == 201
    # duplicate label for same pair/event -> 409
    assert client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                       json={"user_id": "u-talent11",
                             "label": "reliable"}).status_code == 409
    # banned wording in the note -> 422
    assert client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                       json={"user_id": "u-talent11", "label": "learns_fast",
                             "note": "native speaker"}).status_code == 422
    # unknown label -> 422
    assert client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                       json={"user_id": "u-talent11",
                             "label": "nice"}).status_code == 422
    # 11th kudos by one employer in one event -> 409 (u-talent11 has a
    # scan relation; fill 8 more directly so the count reaches 9)
    conn = _db(client)
    for i in range(1, 9):
        conn.execute(
            "INSERT OR IGNORE INTO badge (id,user_id,employer_id,event_id,"
            "kind,label) VALUES (?,?,?,?,'kudos',?)",
            (f"bd-fill-{i}", f"u-talent{i + 12:02d}", "emp-cafe-koivu",
             E1, "reliable"))
    conn.commit()
    conn.close()
    r = client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                    json={"user_id": "u-talent11", "label": "learns_fast"})
    assert r.status_code == 201, r.text          # 10th is fine
    r = client.post(f"/api/employer/events/{E1}/kudos", headers=sanna,
                    json={"user_id": "u-talent11", "label": "team_player"})
    assert r.status_code == 409                  # 11th refused
    # advisor can give organizer + hired badges
    r = client.post(f"/api/advisor/events/{E1}/badges", headers=advisor,
                    json={"kind": "organizer", "user_id": "u-talent22",
                          "label": "volunteer"})
    assert r.status_code == 201
    r = client.post(f"/api/advisor/events/{E1}/badges", headers=advisor,
                    json={"kind": "hired", "user_id": "u-talent23",
                          "employer_id": "emp-cafe-koivu"})
    assert r.status_code == 201
    assert client.post(f"/api/advisor/events/{E1}/badges", headers=advisor,
                       json={"kind": "hired", "user_id": "u-talent23",
                             "employer_id": "emp-cafe-koivu"}
                       ).status_code == 409
    # non-advisor cannot
    assert client.post(f"/api/advisor/events/{E1}/badges", headers=sanna,
                       json={"kind": "hired", "user_id": "u-talent23",
                             "employer_id": "emp-cafe-koivu"}
                       ).status_code in (403, 404)


def test_hidden_badge_not_shown_to_scanners(client, aino, sanna):
    _reg_aino(client, aino)
    conn = _db(client)
    tok = _pass_token(conn, E1, AINO)
    bid = conn.execute(
        "SELECT id FROM badge WHERE user_id=? AND kind='kudos' LIMIT 1",
        (AINO,)).fetchone()["id"]
    conn.close()
    r = client.put(f"/api/me/badges/{bid}/hide", headers=aino,
                   json={"hidden": True})
    assert r.status_code == 200
    d = client.get(f"/api/p/{tok}", headers=sanna).json()
    assert all(b["id"] != bid for b in d["badges"])
    mine = client.get("/api/me/badges", headers=aino).json()["badges"]
    assert any(b["id"] == bid and b["hidden"] for b in mine)
    # restore + cannot hide someone else's badge
    client.put(f"/api/me/badges/{bid}/hide", headers=aino,
               json={"hidden": False})
    assert client.put(f"/api/me/badges/{bid}/hide", headers=sanna,
                      json={"hidden": True}).status_code in (403, 404)


def test_anonymous_cards_only_kudos(client, sanna, aino):
    _reg_aino(client, aino)
    reg = client.get(f"/api/events/{E1}/my", headers=aino
                     ).json()["registration"]
    r = client.get(f"/api/employer/events/{E1}/cards?all=true",
                   headers=sanna)
    assert r.status_code == 200
    aino_card = next(c for c in r.json()["cards"]
                     if c["id"] == reg["id"])
    kudos = {k["label"]: k["count"] for k in aino_card["kudos"]}
    assert kudos == {"explains_clearly": 1, "helped_others": 1}
    blob = str(aino_card)
    for banned in ("attended", "hired", "organizer", "pitched",
                   "given_by", "emp-cafe-koivu"):
        assert banned not in blob


def test_employer_answered_badge_rule(client, sanna):
    conn = _db(client)
    # emp-cafe-koivu answered every E1 talk -> company badge exists
    assert conn.execute(
        "SELECT 1 FROM badge WHERE employer_id='emp-cafe-koivu' AND"
        " kind='employer_answered'").fetchone()
    # an employer with an unanswered talk has none
    late = conn.execute(
        "SELECT employer_id FROM event_talk WHERE event_id=? AND"
        " answered_at IS NULL LIMIT 1", (E1,)).fetchone()
    if late:
        assert not conn.execute(
            "SELECT 1 FROM badge WHERE employer_id=? AND event_id=? AND"
            " kind='employer_answered'",
            (late["employer_id"], E1)).fetchone()
    conn.close()
    # need cards carry the company badge
    d = client.get(f"/api/events/{E1}", headers=sanna).json()
    koivu = next(n for n in d["employers"]
                 if n["employer_id"] == "emp-cafe-koivu")
    assert "employer_answered" in koivu["company_badges"]


def test_employer_answered_not_when_late(client):
    """A talk answered >7 days after talking blocks the company badge."""
    conn = _db(client)
    conn.execute(
        "UPDATE event_talk SET talked_at='2026-10-01T10:00:00',"
        " answered_at='2026-10-20T10:00:00' WHERE event_id=? AND"
        " employer_id='emp-freight' LIMIT 1".replace(" LIMIT 1", ""),
        (E0,))
    conn.execute("DELETE FROM badge WHERE kind='employer_answered' AND"
                 " employer_id='emp-freight' AND event_id=?", (E0,))
    from app.api.routers.events import _maybe_award_employer_answered
    _maybe_award_employer_answered(conn, E0, "emp-freight")
    assert not conn.execute(
        "SELECT 1 FROM badge WHERE employer_id='emp-freight' AND"
        " event_id=? AND kind='employer_answered'", (E0,)).fetchone()
    conn.close()


def test_qr_talk_flow(client, sanna):
    conn = _db(client)
    tok = _pass_token(conn, E1, "u-talent20")
    conn.close()
    client.get(f"/api/p/{tok}", headers=sanna)
    r = client.post(f"/api/employer/events/{E1}/talk", headers=sanna,
                    json={"user_id": "u-talent20"})
    assert r.status_code == 201
    tid = r.json()["talk_id"]
    # the talk shows in the 7-day follow-up list
    ws = client.get(f"/api/employer/events/{E1}", headers=sanna).json()
    talks = ws.get("talks") or []
    assert any(t["id"] == tid for t in talks)


def test_connections_lists_shared_contact_only(client, aino, sanna):
    r = client.get("/api/me/connections", headers=aino)
    assert r.status_code == 200
    conns = r.json()["connections"]
    assert len(conns) >= 5                      # seeded + scans above
    sanna_c = next(c for c in conns if c["user_id"] == SANNA)
    assert sanna_c["role"] == "employer" and sanna_c["company"]
    # talent-to-talent connection exists too
    assert any(c["role"] == "resident" for c in conns)
    # private note stays private
    conn = _db(client)
    a, b = sorted([AINO, "u-talent07"])
    col = "note_a" if a == AINO else "note_b"
    conn.execute(
        f"UPDATE connection SET {col}='met at workshop' WHERE user_a=?"
        " AND user_b=? AND event_id=?", (a, b, E0))
    conn.commit()
    conn.close()
    other = client.get("/api/me/connections", headers=sanna).json()
    for c in other["connections"]:
        assert "met at workshop" not in str(c)
    # remove a connection
    t7 = {"Authorization": aino["Authorization"]}
    r = client.delete(f"/api/me/connections/{E0}/u-talent07", headers=t7)
    assert r.status_code == 200
