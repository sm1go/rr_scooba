#!/usr/bin/env python3
"""Fetch metro + railway stations in/next to Espoo from OpenStreetMap.

Writes db/seed/stations.json (name, mode 'metro'|'train', lat, lon).
Data © OpenStreetMap contributors (ODbL) — mirrored in the file meta.

Primary path: the Overpass API (spec docs/03-product/app-v3-additions.md §5).
Fallback: Nominatim lookups for each known Espoo-area station name — same
OSM data, used when every Overpass mirror is unreachable. Coordinates always
come from OSM; they are never written by hand.

Usage: python scripts/fetch_stations.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "db" / "seed" / "stations.json"

# Bounding box covering Espoo + Kauniainen + the immediate Helsinki edge
# (stations "in and next to Espoo"): south,west,north,east
BBOX = "60.05,24.40,60.40,25.05"
SOUTH, WEST, NORTH, EAST = (float(v) for v in BBOX.split(","))

QUERY = f"""[out:json][timeout:30];
(
  node["railway"="station"]({BBOX});
  node["railway"="halt"]({BBOX});
  node["station"="subway"]({BBOX});
);
out tags;"""

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
]

UA = {"User-Agent": "EspooWorkMap/1.0 (Junction hackathon)"}

# Known Espoo-area stations used by the Nominatim fallback: the name is only
# the lookup key — coordinates always come from the OSM result. Each entry is
# (queries to try, mode); the first result that is a station inside the
# bounding box wins, and the OSM display name is stored.
FALLBACK_STATIONS = [
    # Länsimetro (metro) — Espoo side + the Helsinki end-stations
    (["Kivenlahti station", "Kivenlahti"], "metro"),
    (["Espoonlahti station", "Espoonlahti"], "metro"),
    (["Soukka station", "Soukka"], "metro"),
    (["Kaitaa station", "Kaitaa"], "metro"),
    (["Finnoo station", "Finnoo"], "metro"),
    (["Matinkylä station", "Matinkylä"], "metro"),
    (["Niittykumpu station", "Niittykumpu"], "metro"),
    (["Tapiola station", "Tapiola"], "metro"),
    (["Urheilupuisto station", "Urheilupuisto"], "metro"),
    (["Aalto-yliopisto station", "Aalto-yliopisto"], "metro"),
    (["Keilaniemi station", "Keilaniemi"], "metro"),
    (["Koivusaari station", "Koivusaari"], "metro"),
    (["Lauttasaari station", "Lauttasaari"], "metro"),
    # coastal commuter rail in / next to Espoo
    (["Kauklahti station", "Kauklahti"], "train"),
    (["Espoon rautatieasema station", "Espoo asema"], "train"),
    (["Tuomarila station", "Tuomarila"], "train"),
    (["Koivuhovi station", "Koivuhovi"], "train"),
    (["Kauniainen station", "Kauniaisten rautatieasema"], "train"),
    (["Kera station", "Kera"], "train"),
    (["Kilo railway station", "Kilon rautatieasema"], "train"),
    (["Leppävaaran asema station", "Leppävaara station"], "train"),
    (["Mäkkylä railway station", "Mäkkylä Espoo"], "train"),
    (["Valimo station", "Valimo Helsinki"], "train"),
]


def _get(url: str, body: bytes | None = None) -> dict:
    req = urllib.request.Request(url, data=body, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def fetch_overpass() -> dict | None:
    body = ("data=" + urllib.parse.quote(QUERY)).encode()
    for base in MIRRORS:
        for attempt in range(3):
            try:
                data = _get(base, body)
                if data.get("elements"):
                    print(f"  Overpass via {base}")
                    return data
                print(f"  {base}: empty response")
                break
            except Exception as e:                   # noqa: BLE001
                print(f"  {base} (try {attempt + 1}): "
                      f"{type(e).__name__} {str(e)[:80]}")
                time.sleep(3)
    return None


def _inside(lat: float, lon: float) -> bool:
    return SOUTH <= lat <= NORTH and WEST <= lon <= EAST


def _station_elements(data: dict) -> dict[str, dict]:
    stations = {}
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name or "lat" not in el:
            continue
        is_metro = (tags.get("station") == "subway"
                    or tags.get("subway") == "yes")
        stations[name] = {"name": name,
                          "mode": "metro" if is_metro else "train",
                          "lat": el["lat"], "lon": el["lon"]}
    return stations


def fetch_nominatim() -> dict[str, dict]:
    """Fallback: look each station name up in Nominatim (OSM data) and keep
    results that are stations inside the Espoo bounding box."""
    found: dict[str, dict] = {}
    for queries, mode in FALLBACK_STATIONS:
        got = None
        for q0 in queries:
            if got:
                break
            q = urllib.parse.quote(q0)
            url = ("https://nominatim.openstreetmap.org/search"
                   f"?format=jsonv2&limit=6&countrycodes=fi&q={q}")
            try:
                for r in _get(url):
                    typ = (r.get("type") or "").lower()
                    cls = (r.get("class") or "").lower()
                    lat, lon = float(r["lat"]), float(r["lon"])
                    is_station = ("station" in typ or "subway" in typ
                                  or "halt" in typ or cls == "railway")
                    if is_station and _inside(lat, lon):
                        osm_name = r["display_name"].split(",")[0]
                        got = {"name": osm_name, "mode": mode,
                               "lat": lat, "lon": lon}
                        break
            except Exception as e:                   # noqa: BLE001
                print(f"  nominatim {q0}: {type(e).__name__} {e}")
            time.sleep(1.1)                          # Nominatim usage policy
        if got:
            found[got["name"]] = got
        else:
            print(f"  !! no OSM station result for {queries[0]}")
    return found


def main() -> int:
    data = fetch_overpass()
    if data is not None:
        stations = _station_elements(data)
        source = "OpenStreetMap via Overpass API"
    else:
        print("  Overpass unreachable — falling back to Nominatim (same "
              "OSM data).")
        stations = fetch_nominatim()
        source = "OpenStreetMap via Nominatim"
    out = {
        "meta": {
            "source": source,
            "attribution": "© OpenStreetMap contributors (ODbL)",
            "bbox": BBOX,
            "fetched": "2026-11-14",
        },
        "stations": sorted(stations.values(), key=lambda s: s["name"]),
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"{len(out['stations'])} stations -> {OUT}")
    for s in out["stations"]:
        print(f"  {s['mode']:5} {s['name']:20} {s['lat']:.5f} {s['lon']:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
