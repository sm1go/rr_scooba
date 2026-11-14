"""F03 Pool Proof: k=10 bands, elasticity, consent + confirmed-claim gating."""

import copy

from app.api.rules import pool


def test_band_boundaries():
    assert pool.band_for(0) == "fewer than 10"
    assert pool.band_for(9) == "fewer than 10"
    assert pool.band_for(10) == "10–19"
    assert pool.band_for(19) == "10–19"
    assert pool.band_for(20) == "20–49"
    assert pool.band_for(49) == "20–49"
    assert pool.band_for(50) == "50+"


def test_demo_bands(conn, draft_card, lumo_card):
    # recorded draft card = 'fluent Finnish' era -> pool collapses
    assert pool.pool_preview(conn, draft_card)["band"] == "fewer than 10"
    # approved card with Finnish B1 -> pool recovers
    assert pool.pool_preview(conn, lumo_card)["band"] == "20–49"


def test_elasticity_per_must_have(conn, lumo_card):
    p = pool.pool_preview(conn, lumo_card)
    assert len(p["elasticity"]) == len(lumo_card["must_haves"])
    for e in p["elasticity"]:
        assert e["requirement_id"] and e["text"]
        assert e["band_without"] in pool.BANDS
    # dropping the CI must-have can only grow the pool (or keep it)
    ci = next(e for e in p["elasticity"] if e["requirement_id"] == "req-lumo-1")
    assert pool.BANDS.index(ci["band_without"]) >= pool.BANDS.index(p["band"])


def test_no_consent_no_count(conn, lumo_card):
    conn.execute("UPDATE talent SET pool_consent=0")
    assert pool.pool_preview(conn, lumo_card)["band"] == "fewer than 10"


def test_unconfirmed_claims_do_not_count(conn, lumo_card):
    conn.execute("UPDATE evidence_claim SET confirmed=0")
    assert pool.pool_preview(conn, lumo_card)["band"] == "fewer than 10"


def test_empty_card_counts_all_consenting(conn, draft_card):
    card = copy.deepcopy(draft_card)
    card["must_haves"], card["languages"] = [], []
    assert pool.pool_preview(conn, card)["band"] == "50+"
