"""F13 closure: reason chips from card requirements, F14 support banner."""

import pytest

from app.api import db
from app.api.rules import closure


def test_chips_must_come_from_card(conn):
    card = db.get_card(conn, "card-co-lumo")
    closure.validate_chips(card, ["req-lumo-1"])          # id ok
    closure.validate_chips(card, [card["must_haves"][0]["text"]])  # text ok
    with pytest.raises(closure.ChipError) as e:
        closure.validate_chips(card, ["bad vibes", "she was late"])
    assert e.value.invalid == ["bad vibes", "she was late"]
    assert "req-lumo-1" in e.value.allowed


def test_banner_only_on_next_step():
    assert closure.support_banner_for("next_step") == closure.SUPPORT_BANNER
    assert closure.support_banner_for("not_now") is None
    assert "don't sign before the decision" in closure.SUPPORT_BANNER


def test_message_mentions_reasons_and_redirect(conn):
    card = db.get_card(conn, "card-co-lumo")
    msg = closure.build_message("Lumo Systems Oy", "Amira Haddad", card,
                                "not_now", ["req-lumo-1"], None,
                                "Kehä Robotics Oy")
    assert "Lumo Systems Oy" in msg
    assert card["must_haves"][0]["text"].rstrip(".") in msg
    assert "Kehä Robotics Oy" in msg


def test_message_next_step(conn):
    card = db.get_card(conn, "card-co-lumo")
    msg = closure.build_message("Lumo Systems Oy", "Amira Haddad", card,
                                "next_step", [], "paid trial day next week", None)
    assert "paid trial day next week" in msg
