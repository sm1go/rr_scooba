"""§5 commute rework: compute ALL missing (parallel pool of 5), cache
reuse, failures logged + job kept with null, remote always kept, cached
commute attached whenever a district is given."""

import logging
import threading

import pytest

from app.api import digitransit


def _node(minutes=24):
    return {
        "start": "2026-11-16T08:26:00+02:00",
        "end": "2026-11-16T08:50:00+02:00",
        "duration": minutes * 60,
        "walkDistance": 420,
        "legs": [
            {"mode": "WALK", "distance": 300, "duration": 360,
             "from": {"name": "Origin"}, "to": {"name": "Matinkylä"},
             "trip": None},
            {"mode": "BUS", "distance": 3100, "duration": 780,
             "from": {"name": "Matinkylä"}, "to": {"name": "Olari"},
             "trip": {"routeShortName": "533"}},
            {"mode": "WALK", "distance": 120, "duration": 120,
             "from": {"name": "Olari"}, "to": {"name": "Destination"},
             "trip": None},
        ],
    }


class Fake:
    """Fake Digitransit client — no network."""

    def __init__(self, node=None, fail=False):
        self.node = node or _node()
        self.fail = fail
        self.calls = 0
        self._lock = threading.Lock()

    def plan(self, *_args):
        with self._lock:
            self.calls += 1
        if self.fail:
            raise digitransit.CommuteUnavailable("service down (fake)")
        return self.node


@pytest.fixture()
def commute_on(monkeypatch):
    from app.api import settings
    monkeypatch.setattr(settings, "commute_enabled", lambda: True)
    yield
    digitransit.set_client(None)


def test_commute_max_computes_all_missing(client, commute_on):
    fake = Fake()
    digitransit.set_client(fake)
    r = client.get("/api/jobs?district=matinkyla&commute_max=60")
    assert r.status_code == 200
    jobs = r.json()["jobs"]
    commuted = [j for j in jobs
                if j.get("commute") and j["commute"].get("minutes")]
    # the old cap computed at most 5 — all missing must be computed now
    assert len(commuted) > 5
    assert fake.calls == len(commuted)
    assert all(j["commute"]["minutes"] <= 60 for j in commuted)


def test_commute_max_filters_out_long_trips(client, commute_on):
    fake = Fake(_node(minutes=45))
    digitransit.set_client(fake)
    r = client.get("/api/jobs?district=matinkyla&commute_max=30")
    assert r.status_code == 200
    for j in r.json()["jobs"]:
        assert (j.get("commute") is None
                or j["commute"].get("minutes") is None
                or j["commute"]["minutes"] <= 30)


def test_parallel_pool_of_five_and_cache(client, commute_on, monkeypatch):
    from app.api.routers import jobs as jobs_mod
    real = jobs_mod.ThreadPoolExecutor
    used = []

    class Spy(real):
        def __init__(self, max_workers=None, **kw):
            used.append(max_workers)
            super().__init__(max_workers=max_workers, **kw)

    monkeypatch.setattr(jobs_mod, "ThreadPoolExecutor", Spy)
    fake = Fake()
    digitransit.set_client(fake)
    client.get("/api/jobs?district=matinkyla&commute_max=60")
    assert used == [5]
    calls = fake.calls

    # second call: everything comes from the 7-day cache
    client.get("/api/jobs?district=matinkyla&commute_max=60")
    assert fake.calls == calls

    # district without commute_max attaches cached values, never computes
    r = client.get("/api/jobs?district=matinkyla")
    assert r.status_code == 200
    assert fake.calls == calls
    assert any(j.get("commute") for j in r.json()["jobs"])


def test_failures_logged_and_jobs_kept(client, commute_on, caplog):
    digitransit.set_client(Fake(fail=True))
    with caplog.at_level(logging.WARNING):
        r = client.get("/api/jobs?district=matinkyla&commute_max=60")
    assert r.status_code == 200
    jobs = r.json()["jobs"]
    assert jobs, "failed computations must not drop jobs"
    assert all(j.get("commute") is None for j in jobs)
    assert any("commute failed for job" in m for m in caplog.messages)


def test_remote_jobs_kept_with_null(client, commute_on):
    digitransit.set_client(Fake())
    r = client.get("/api/jobs?district=matinkyla&commute_max=1")
    assert r.status_code == 200
    remotes = [j for j in r.json()["jobs"] if j["work_mode"] == "remote"]
    assert remotes, "seed has remote jobs — they must survive the filter"
    for j in remotes:
        assert j.get("commute") is None


def test_district_alone_never_computes(client, commute_on):
    fake = Fake()
    digitransit.set_client(fake)
    r = client.get("/api/jobs?district=matinkyla")
    assert r.status_code == 200
    assert fake.calls == 0
    assert all(j.get("commute") is None for j in r.json()["jobs"])
