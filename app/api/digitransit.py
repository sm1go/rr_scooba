"""Digitransit (HSL) routing client (spec v3 §5).

`DIGITRANSIT_API_KEY` missing -> commute features hidden; straight-line
distance stays. Tests inject a fake via `set_client()` — no network in tests.

Only fields confirmed in the official docs are used:
  https://digitransit.fi/en/developers/apis/1-routing-api/itinerary-planning/
  https://docs.opentripplanner.org/api/dev-2.x/graphql-gtfs/queries/planConnection
  - dateTime { latestArrival }  (PlanDateTimeInput)
  - node: start, end, duration, walkDistance
  - leg:  mode, distance, duration, from/to {name, stop {name}},
          trip {routeShortName}, start/end {scheduledTime}
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from . import settings

HELSINKI = ZoneInfo("Europe/Helsinki")

ENDPOINT = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
TIMEOUT = 20

# The whole GraphQL query, kept here so it is reviewable in one place.
PLAN_QUERY = """{
  planConnection(
    origin: {location: {coordinate: {latitude: %(origin_lat)s, longitude: %(origin_lon)s}}}
    destination: {location: {coordinate: {latitude: %(dest_lat)s, longitude: %(dest_lon)s}}}
    first: 3
    dateTime: {latestArrival: "%(arrive_by)s"}
  ) {
    edges {
      node {
        start
        end
        duration
        walkDistance
        legs {
          mode
          distance
          duration
          start { scheduledTime }
          end { scheduledTime }
          from { name stop { name } }
          to { name stop { name } }
          trip { routeShortName }
        }
      }
    }
  }
}"""


class CommuteUnavailable(Exception):
    """No key configured, or the routing service could not be reached."""


class DigitransitClient:
    def __init__(self, api_key: str | None = None,
                 endpoint: str = ENDPOINT):
        self.api_key = (api_key if api_key is not None
                        else settings.digitransit_api_key())
        self.endpoint = endpoint

    def plan(self, origin_lat: float, origin_lon: float,
             dest_lat: float, dest_lon: float,
             arrive_by: datetime) -> dict | None:
        """Fastest itinerary arriving by `arrive_by` (ISO local datetime with
        offset). Returns the raw GraphQL node or None when no itinerary."""
        if not self.api_key:
            raise CommuteUnavailable("No DIGITRANSIT_API_KEY configured.")
        when = (arrive_by.replace(tzinfo=HELSINKI)
                if arrive_by.tzinfo is None else arrive_by)
        query = PLAN_QUERY % {
            "origin_lat": origin_lat, "origin_lon": origin_lon,
            "dest_lat": dest_lat, "dest_lon": dest_lon,
            "arrive_by": when.isoformat(timespec="minutes"),
        }
        try:
            r = requests.post(
                self.endpoint,
                json={"query": query},
                headers={"digitransit-subscription-key": self.api_key,
                         "Content-Type": "application/json"},
                timeout=TIMEOUT)
        except requests.RequestException as e:
            raise CommuteUnavailable(f"Routing service unreachable: {e}") from e
        if r.status_code >= 400:
            raise CommuteUnavailable(f"Routing service error {r.status_code}")
        edges = (r.json().get("data", {}).get("planConnection", {})
                 or {}).get("edges", [])
        if not edges:
            return None
        # pick the itinerary with the shortest duration
        best = min(edges, key=lambda e: e["node"].get("duration") or 10**9)
        return best["node"]


_client = None


def set_client(client) -> None:
    """Tests inject a fake here (must provide .plan(...) -> node dict|None)."""
    global _client
    _client = client


def get_client():
    global _client
    if _client is None:
        _client = DigitransitClient()
    return _client


def leg_out(leg: dict) -> dict:
    route = ((leg.get("trip") or {}).get("routeShortName"))
    return {
        "mode": leg.get("mode"),
        "route": route,
        "from": ((leg.get("from") or {}).get("stop") or {}).get("name")
                or (leg.get("from") or {}).get("name"),
        "to": ((leg.get("to") or {}).get("stop") or {}).get("name")
              or (leg.get("to") or {}).get("name"),
        "minutes": round((leg.get("duration") or 0) / 60),
    }


def commute_out(node: dict | None, arrive_by: datetime) -> dict | None:
    """Raw itinerary node -> API payload (spec §5 shape)."""
    if node is None:
        return None
    minutes = round((node.get("duration") or 0) / 60)
    legs = [leg_out(l) for l in node.get("legs", [])]
    transfers = max(0, sum(1 for l in legs if l["mode"] != "WALK") - 1)
    return {
        "minutes": minutes,
        "walk_m": round(node.get("walkDistance") or 0),
        "transfers": transfers,
        "legs": legs,
        "arrive_by": node.get("end") or arrive_by.isoformat(timespec="minutes"),
        "date": arrive_by.date().isoformat(),
        "source": "HSL",
    }
