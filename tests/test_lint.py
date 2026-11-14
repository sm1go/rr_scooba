"""F02 Requirement Reality Check: rulebook triggers, cap of 5, pool bands."""

import copy

from app.api.rules import lint


def test_demo_card_triggers_language_age_degree(conn, draft_card):
    hints = lint.lint_card(conn, draft_card)
    rules = {h["rule"] for h in hints}
    assert "language_proxy" in rules
    assert "age_words" in rules
    assert "degree_without_reason" in rules
    assert len(hints) <= 5


def test_language_hint_rewrite_moves_pool(conn, draft_card):
    """The demo moment: 'fluent' -> 'fewer than 10', B1 rewrite -> '20–49'."""
    hint = next(h for h in lint.lint_card(conn, draft_card)
                if h["rule"] == "language_proxy")
    assert hint["pool_before"] == "fewer than 10"
    assert hint["pool_after"] == "20–49"
    assert hint["law"] == "Non-Discrimination Act 1325/2014"
    assert "B1" in hint["suggestion"]


def test_each_hint_has_contract_fields(conn, draft_card):
    for h in lint.lint_card(conn, draft_card):
        for k in ("id", "rule", "trigger", "why", "suggestion",
                  "pool_before", "pool_after"):
            assert k in h and h[k] is not None


def test_clean_card_no_hints(conn, lumo_card):
    # the approved (rewritten) Lumo card should lint clean
    assert lint.lint_card(conn, lumo_card) == []


def test_triggers_native_gaps_fit_photo(conn, draft_card):
    card = copy.deepcopy(draft_card)
    card["languages"] = []  # isolate literal triggers
    card["nice_to_haves"] = [
        "native speaker preferred", "no unexplained gaps",
        "a great cultural fit", "attach a photo", "only Finnish citizens",
        "a real salesman at heart",
    ]
    rules = {h["rule"] for h in lint.lint_card(conn, card)}
    # capped at five hints — the five earliest rules in book order
    assert len(rules) == 5
    assert "language_proxy" in rules  # 'native speaker'
    assert "nationality" in rules
    assert "gendered_words" in rules
    assert "photo" in rules
