"""F04 quote guard: 'no quote, no claim' + verb-inflation refusal."""

from app.api.rules import quote_guard

TRANSCRIPT = ("I helped cut our build time from 30 to 6 minutes by caching "
              "dependencies. I wrote most of the pytest suite we still run.")


def test_exact_quote_passes():
    c = {"text": "I helped cut our build time from 30 to 6 minutes",
         "quote": "I helped cut our build time from 30 to 6 minutes"}
    assert quote_guard.check_claim(c["text"], c["quote"], TRANSCRIPT) is None


def test_quote_must_be_exact_substring():
    c = {"text": "I cut build time by 80%",
         "quote": "I cut our build time by 80 percent"}  # paraphrase, not verbatim
    reason = quote_guard.check_claim(c["text"], c["quote"], TRANSCRIPT)
    assert reason and "no quote" in reason


def test_inflated_verb_refused():
    c = {"text": "Led the CI/CD transformation and owned the release pipeline",
         "quote": "I helped cut our build time from 30 to 6 minutes"}
    reason = quote_guard.check_claim(c["text"], c["quote"], TRANSCRIPT)
    assert reason and "inflated verb" in reason and "'led'" in reason


def test_strong_verb_supported_by_quote_passes():
    c = {"text": "I wrote most of the pytest suite we still run",
         "quote": "I wrote most of the pytest suite we still run"}
    assert quote_guard.check_claim(c["text"], c["quote"], TRANSCRIPT) is None


def test_guarded_extract_splits(amira_story):
    proposed = list(amira_story["claims"]) + [
        {"text": "Led the CI/CD transformation and owned the release pipeline",
         "quote": "I helped cut our build time from 30 to 6 minutes"},
        {"text": "Expert in Kubernetes", "quote": "I am an expert in Kubernetes"},
    ]
    ok, refused = quote_guard.guarded_extract(proposed, amira_story["transcript"])
    assert len(ok) == 3
    assert len(refused) == 2
    assert all("reason" in r for r in refused)
