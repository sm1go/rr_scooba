"""Requirement identifiers remain unique across independently authored cards."""

from app.api import db


def test_reused_requirement_id_is_namespaced(conn):
    first = db.get_card(conn, "card-co-lumo")
    second = {
        **first,
        "id": "card-new-company",
        "company_id": "co-aurora",
        "status": "draft",
        "must_haves": [{
            **first["must_haves"][0],
            "id": first["must_haves"][0]["id"],
        }],
    }

    db.save_card(conn, second)

    assert second["must_haves"][0]["id"].startswith("card-new-company::")
    assert len(db.get_card(conn, "card-co-lumo")["must_haves"]) == 3
