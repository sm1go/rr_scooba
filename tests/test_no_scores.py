"""Contract guarantee: no endpoint returns a score, rank or ordered list
of people. Scan every response body recursively for forbidden keys."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {"score", "scores", "rank", "ranking", "ranked", "rating",
             "fit_score", "match_score", "order", "ordered"}


def _walk(node, path="$", hits=None):
    hits = hits if hits is not None else []
    if isinstance(node, dict):
        for k, v in node.items():
            if str(k).lower() in FORBIDDEN:
                hits.append(f"{path}.{k}")
            _walk(v, f"{path}.{k}", hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, f"{path}[{i}]", hits)
    return hits


def test_no_response_contains_score_or_rank(client):
    story = json.loads((ROOT / "db" / "seed" / "recorded" / "amira_story.json")
                       .read_text(encoding="utf-8"))
    ad = json.loads((ROOT / "db" / "seed" / "recorded" / "ad_lumo.json")
                    .read_text(encoding="utf-8"))

    calls = [
        ("GET", "/api/health", None),
        ("GET", "/api/event", None),
        ("GET", "/api/companies/co-lumo", None),
        ("GET", "/api/companies/co-lumo/sparks", None),
        ("GET", "/api/companies/co-lumo/meetings", None),
        ("GET", "/api/cards", None),
        ("GET", "/api/cards/card-co-lumo", None),
        ("POST", "/api/compiler/draft",
         {"company_id": "co-lumo", "text": ad["ad_text"]}),
        ("POST", "/api/lint", {"card": ad["card"]}),
        ("POST", "/api/pool", {"card": ad["card"]}),
        ("GET", "/api/talents/ta-0427", None),
        ("GET", "/api/talents/ta-0427/sparks", None),
        ("POST", "/api/story/followups",
         {"talent_id": "ta-0427", "transcript": story["transcript"], "language": "ar"}),
        ("POST", "/api/story/extract",
         {"talent_id": "ta-0427", "transcript": story["transcript"], "language": "ar"}),
        ("GET", "/api/evidence/ta-0427", None),
        ("GET", "/api/meetings/mt-001/sheet", None),
        ("GET", "/api/organiser/overview", None),
        ("GET", "/api/trust/twin-report", None),
        ("GET", "/api/audit", None),
    ]
    for method, url, body in calls:
        resp = getattr(client, method.lower())(url, json=body) if body else \
            getattr(client, method.lower())(url)
        assert resp.status_code == 200, f"{method} {url}: {resp.status_code}"
        hits = _walk(resp.json())
        assert not hits, f"{method} {url} returned forbidden keys: {hits}"

        # also: never a bare list of people
        if isinstance(resp.json(), list):
            assert not any(isinstance(x, dict) and "name" in x
                           for x in resp.json()), f"{url} leaked names in a list"
