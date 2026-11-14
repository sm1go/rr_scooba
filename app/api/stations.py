"""Station lookup for the 'near a station' feature (spec v3 §5).

Loads db/seed/stations.json once (fetched by scripts/fetch_stations.py,
© OpenStreetMap contributors). Straight-line distance only.
"""

from __future__ import annotations

import json
from functools import lru_cache

from .db import SEED_DIR
from .rules.labels import haversine_km


@lru_cache(maxsize=1)
def stations() -> list[dict]:
    path = SEED_DIR / "stations.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["stations"]


def nearest(lat: float | None, lon: float | None) -> dict | None:
    """{name, mode, distance_m} of the closest station, or None."""
    if lat is None or lon is None:
        return None
    best = None
    for s in stations():
        d = haversine_km(lat, lon, s["lat"], s["lon"]) * 1000
        if best is None or d < best["distance_m"]:
            best = {"name": s["name"], "mode": s["mode"],
                    "distance_m": round(d)}
    return best


def reset_cache() -> None:
    stations.cache_clear()
