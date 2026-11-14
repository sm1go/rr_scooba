"""F06 Sparks: budget formula, refund paths, reveal-on-accept, first free slot."""

import pytest

from app.api.rules import sparks


def test_budget_formula(conn):
    # sum(slots) = 75, 300 talents -> round(112.5/300)=0 -> clamp to 3
    assert sparks.spark_budget(conn) == 3
    conn.execute("UPDATE company SET slots=70")
    # sum = 840 -> round(1260/300)=4 -> interior value survives the clamp
    assert sparks.spark_budget(conn) == 4
    conn.execute("UPDATE company SET slots=2000")
    # clamps at 5
    assert sparks.spark_budget(conn) == 5


def test_send_spark_validates(conn):
    with pytest.raises(sparks.SparkError) as e:
        sparks.send_spark(conn, "ta-9999", "card-co-lumo", "cl-x", "req-lumo-1", None)
    assert e.value.status_code == 404
    # claim must belong to the talent
    with pytest.raises(sparks.SparkError) as e:
        sparks.send_spark(conn, "ta-0427", "card-co-lumo", "cl-ta-0001-0",
                          "req-lumo-1", None)
    assert e.value.status_code == 422


def test_send_respond_accept_reveals_name_and_slot(conn):
    spark = sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                              "cl-amira-build", "req-lumo-1", "hi")
    assert spark["status"] == "sent"
    assert "revealed_name" not in spark
    assert spark["deadline"]

    accepted = sparks.respond(conn, spark["id"], "accept", None)
    assert accepted["status"] == "accepted"
    assert accepted["revealed_name"] == "Amira Haddad"
    # Lumo already has 2 meetings seeded -> third slot label
    assert accepted["slot"] == sparks.slot_label("2026-11-26", 2)
    m = conn.execute("SELECT * FROM meeting WHERE spark_id=?",
                     (spark["id"],)).fetchone()
    assert m and m["slot"] == accepted["slot"]


def test_decline_refunds_budget(conn):
    used_before = sparks.sparks_used(conn, "ta-0427")
    spark = sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                              "cl-amira-build", "req-lumo-1", None)
    assert sparks.sparks_used(conn, "ta-0427") == used_before + 1
    declined = sparks.respond(conn, spark["id"], "decline", "req-lumo-1")
    assert declined["status"] == "declined"
    assert sparks.sparks_used(conn, "ta-0427") == used_before


def test_budget_exhausted_409(conn):
    # burn the budget: Amira already has 1 sent (seeded) -> 2 more then 409
    sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                      "cl-amira-build", "req-lumo-1", None)
    sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                      "cl-amira-pytest", "req-lumo-3", None)
    with pytest.raises(sparks.SparkError) as e:
        sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                          "cl-amira-fastapi", "req-lumo-2", None)
    assert e.value.status_code == 409


def test_overdue_spark_is_refunded(conn):
    # seed holds one sent spark past its deadline
    row = conn.execute(
        "SELECT id FROM spark WHERE status='sent' AND deadline < ?",
        (sparks.now_helsinki().isoformat(),)).fetchone()
    assert row
    sparks.expire_overdue(conn)
    after = conn.execute("SELECT status FROM spark WHERE id=?",
                         (row["id"],)).fetchone()
    assert after["status"] == "refunded"


def test_note_max_140(conn):
    with pytest.raises(sparks.SparkError) as e:
        sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                          "cl-amira-build", "req-lumo-1", "x" * 141)
    assert e.value.status_code == 422


def test_full_company_cannot_accept_and_reveal_without_a_slot(conn):
    conn.execute("UPDATE company SET slots=2 WHERE id='co-lumo'")
    spark = sparks.send_spark(conn, "ta-0427", "card-co-lumo",
                              "cl-amira-build", "req-lumo-1", None)
    with pytest.raises(sparks.SparkError) as e:
        sparks.respond(conn, spark["id"], "accept", None)
    assert e.value.status_code == 409
    row = conn.execute("SELECT status,revealed_name FROM spark WHERE id=?",
                       (spark["id"],)).fetchone()
    assert row["status"] == "sent"
    assert row["revealed_name"] is None


def test_spark_requires_approved_card(conn):
    from app.api import db
    draft = dict(db.get_card(conn, "card-co-lumo"))
    draft.update({"id": "card-unapproved", "status": "draft"})
    db.save_card(conn, draft)
    with pytest.raises(sparks.SparkError) as e:
        sparks.send_spark(conn, "ta-0427", "card-unapproved",
                          "cl-amira-build", "req-lumo-1", None)
    assert e.value.status_code == 409
