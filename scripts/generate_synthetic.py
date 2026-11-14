"""Generate the synthetic seed for the TalentMatch Signal MVP.

Deterministic (fixed RNG seed). Run:

    python scripts/generate_synthetic.py

Writes db/esco/skills.json and db/seed/*.json (+ db/seed/recorded/*.json).
Synthetic data only (constraint C2) — every name is fictional, ESCO URIs are
placeholders and are labelled as such.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "db" / "seed"
ESCO_DIR = ROOT / "db" / "esco"

SEED = 20261114
EVENT = {
    "id": "ev-2026-11",
    "name": "TalentMatch Espoo · Tech & ICT",
    "date": "2026-11-26",
    "format": "hybrid",
    "companies_declared": 40,
    "talents_registered": 300,
}

# --- ESCO-like skill list (labels in ESCO style; URIs are placeholders) -------

SKILLS = [
    ("sk-ci",       "use continuous integration and delivery tools", ["ci", "ci/cd", "pipeline", "jenkins", "github actions", "build"]),
    ("sk-python",   "develop software in Python",                  ["python", "fastapi", "django", "flask"]),
    ("sk-test",     "develop automated software tests",            ["pytest", "automated test", "test suite", "tdd", "testing"]),
    ("sk-react",    "develop web interfaces with React",           ["react", "typescript", "frontend", "front-end"]),
    ("sk-k8s",      "orchestrate containers with Kubernetes",      ["kubernetes", "k8s", "container"]),
    ("sk-sql",      "design and query relational databases",       ["sql", "postgresql", "database"]),
    ("sk-ml",       "deploy machine learning models",              ["machine learning", "ml model", "pytorch", "model deployment"]),
    ("sk-cloud",    "manage cloud infrastructure",                 ["aws", "azure", "gcp", "cloud"]),
    ("sk-iac",      "provision infrastructure as code",            ["terraform", "infrastructure as code", "iac", "pulumi"]),
    ("sk-mobile",   "develop mobile applications",                 ["android", "kotlin", "swift", "ios", "mobile"]),
    ("sk-embedded", "develop embedded software",                   ["embedded", "firmware", "c++", "microcontroller"]),
    ("sk-api",      "design REST and event-driven APIs",           ["rest api", "api design", "openapi", "graphql"]),
    ("sk-secu",     "apply application security practices",        ["security", "owasp", "penetration", "hardening"]),
    ("sk-obs",      "operate observability and monitoring",        ["monitoring", "grafana", "observability", "prometheus"]),
    ("sk-etl",      "build data pipelines and ETL",                ["etl", "data pipeline", "airflow", "spark"]),
    ("sk-a11y",     "implement accessibility standards",           ["accessibility", "wcag", "a11y"]),
    ("sk-geo",      "develop geospatial applications",             ["gis", "geospatial", "postgis", "maps"]),
    ("sk-ui",       "design user interfaces",                      ["figma", "ui design", "ux", "prototype"]),
    ("sk-doc",      "write technical documentation",               ["documentation", "technical writing", "docs"]),
    ("sk-agile",    "coordinate agile software projects",          ["scrum", "agile", "project coordination", "kanban"]),
    ("sk-support",  "provide technical customer support",          ["customer support", "helpdesk", "service desk"]),
    ("sk-robot",    "programme industrial robots",                 ["robotics", "ros", "plc"]),
    ("sk-net",      "administer computer networks",                ["networking", "tcp/ip", "cisco", "network"]),
    ("sk-cad",      "create CAD engineering models",               ["cad", "autocad", "solidworks"]),
]
TRIO = ["sk-ci", "sk-python", "sk-test"]  # the three demo must-haves

CLAIM_TEMPLATES = {
    "sk-ci":       "I helped cut our build time from {a} to {b} minutes.",
    "sk-python":   "I built and maintain the Python services our team ships every week.",
    "sk-test":     "I wrote the automated test suite that catches regressions before release.",
    "sk-react":    "I built the React front end our customers use every day.",
    "sk-k8s":      "I moved our services onto Kubernetes and keep the clusters healthy.",
    "sk-sql":      "I redesigned the database schema that cut our slowest query ten-fold.",
    "sk-ml":       "I took a machine-learning model from notebook to production.",
    "sk-cloud":    "I run our cloud infrastructure and its cost budget.",
    "sk-iac":      "I rebuilt our infrastructure as Terraform so nothing is manual any more.",
    "sk-mobile":   "I shipped the mobile app our field teams use daily.",
    "sk-embedded": "I wrote the firmware that runs on our devices in the field.",
    "sk-api":      "I designed the public API our partners integrate with.",
    "sk-secu":     "I led the security fixes that closed our last audit findings.",
    "sk-obs":      "I set up the monitoring dashboards that cut our incident response time.",
    "sk-etl":      "I built the data pipeline that feeds our reporting every morning.",
    "sk-a11y":     "I made our app pass the WCAG accessibility audit.",
    "sk-geo":      "I built the map features our logistics planners rely on.",
    "sk-ui":       "I designed the interface flows in Figma that we then shipped.",
    "sk-doc":      "I wrote the developer documentation our new hires on-board with.",
    "sk-agile":    "I coordinate the sprint work for a team of six engineers.",
    "sk-support":  "I resolve the trickiest technical tickets our support desk gets.",
    "sk-robot":    "I programmed the robot cell that doubled the line's throughput.",
    "sk-net":      "I run the office network and its firewalls.",
    "sk-cad":      "I model the parts we manufacture in CAD.",
}

# --- fictional name pools (many countries, all invented) ----------------------

FIRST = [
    "Amira", "Priya", "Lauri", "Ngozi", "Mateusz", "Linh", "Wei", "Rafael", "Lucía", "Jonas",
    "Awa", "Dmytro", "Sakura", "Wanjiru", "Bilal", "Farhad", "Elif", "Sanne", "Oskar", "Vien",
    "Katarzyna", "Anders", "Yuki", "Chidi", "Mei", "Diego", "Ingrid", "Tomas", "Fatou",
    "Aleksis", "Noora", "Hamza", "Sofia", "Ivan", "Aino", "Kofi", "Renata", "Omar", "Elsa",
    "Deepak", "Thao", "Milos", "Zanele", "Henrik", "Yara", "Petro", "Aisha", "Ville", "Marta",
    "Sanjay", "Elias", "Bianca", "Risto", "Leila", "Antti", "Greta", "Tunde", "Hana", "Bruno",
]
LAST = [
    "Haddad", "Kowalska", "Virtanen", "Okafor", "Nguyen", "Tanaka", "Silva", "Fernández", "Berg",
    "Diallo", "Shevchenko", "Mori", "Mwangi", "Ahmed", "Karimi", "Yilmaz", "van Dijk", "Lindqvist", "Tran",
    "Nowak", "Johansson", "Sato", "Eze", "Chen", "Costa", "Haugen", "Novák", "Ndiaye",
    "Korhonen", "Heikkinen", "Ali", "Rossi", "Petrov", "Saarinen", "Mensah", "Oliveira", "Hassan", "Laine",
    "Sharma", "Pham", "Jovanovic", "Dlamini", "Nilsson", "Nasser", "Kovalenko", "Diop", "Niemi", "Novak",
    "Reddy", "Holm", "Moretti", "Mäkinen", "Haddad", "Salmi", "Krause", "Adeyemi", "Kimura", "Souza",
]

# language pools keyed loosely by name origin — fictional mapping for flavour
HOME_LANG = [
    "Arabic", "Hindi", "Polish", "Yoruba", "Vietnamese", "Chinese", "Portuguese", "Spanish",
    "German", "Wolof", "Ukrainian", "Japanese", "Swahili", "Urdu", "Persian", "Turkish",
    "Dutch", "Swedish", "French", "Estonian", "Russian", "Somali", "Nepali", "Tagalog",
]
CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]

# demo-persona targets: trio talents matching all three Lumo must-haves
TRIO_C2 = 9          # Finnish C2 among trio holders  -> "fewer than 10"
TRIO_B = 22          # Finnish B1/B2 among trio holders -> 9+22(+Amira B1) = 32 -> "20–49"
TRIO_LOW = 13        # Finnish A1/A2 among trio holders


def weighted_choice(rng: random.Random, pairs):
    total = sum(w for _, w in pairs)
    r = rng.random() * total
    for v, w in pairs:
        r -= w
        if r <= 0:
            return v
    return pairs[-1][0]


def build_skills_file():
    return {
        "meta": {
            "title": "ESCO-like skill subset for the TalentMatch Signal demo",
            "license": "labels inspired by ESCO (CC BY 4.0)",
            "uris": "PLACEHOLDER — these are not real ESCO identifiers",
        },
        "skills": [
            {"uri": f"http://data.europa.eu/esco/skill/placeholder-{i:04d}",
             "id": sid, "label": label, "keywords": kw}
            for i, (sid, label, kw) in enumerate(SKILLS, start=1)
        ],
    }


def make_companies(rng):
    """~12 companies incl. Lumo. Returns (companies, cards)."""
    comp = [
        {"id": "co-lumo", "name": "Lumo Systems Oy", "size": 14, "city": "Espoo",
         "contact_name": "Sanna Virtanen", "slots": 8},
        {"id": "co-otava", "name": "Otava Cloud Oy", "size": 60, "city": "Espoo",
         "contact_name": "Mikael Sund", "slots": 6},
        {"id": "co-taiga", "name": "Taiga Games Ab", "size": 45, "city": "Espoo",
         "contact_name": "Riina Palo", "slots": 6},
        {"id": "co-polar", "name": "Polar Grid Energy Oy", "size": 120, "city": "Espoo",
         "contact_name": "Jussi Ranta", "slots": 8},
        {"id": "co-kide", "name": "Kide Biotech Oy", "size": 30, "city": "Espoo",
         "contact_name": "Sara Lind", "slots": 5},
        {"id": "co-vento", "name": "Vento Mobility Oy", "size": 80, "city": "Espoo",
         "contact_name": "Petteri Ahola", "slots": 6},
        {"id": "co-haaga", "name": "Haaga Learning Oy", "size": 25, "city": "Espoo",
         "contact_name": "Leena Koski", "slots": 5},
        {"id": "co-mero", "name": "Meridian Logistics Oy", "size": 200, "city": "Espoo",
         "contact_name": "Antti Sarlin", "slots": 8},
        {"id": "co-keha", "name": "Kehä Robotics Oy", "size": 55, "city": "Espoo",
         "contact_name": "Outi Niemelä", "slots": 6},
        {"id": "co-aurora", "name": "Aurora Health Tech Oy", "size": 90, "city": "Espoo",
         "contact_name": "Emma Salonen", "slots": 7},
        {"id": "co-kello", "name": "Kello Works Oy", "size": 18, "city": "Espoo",
         "contact_name": "Daniel Roth", "slots": 4},
        {"id": "co-sisu", "name": "Sisu Analytics Oy", "size": 35, "city": "Espoo",
         "contact_name": "Vesa Tolonen", "slots": 6},
    ]
    for c in comp:
        c["event_id"] = EVENT["id"]

    def req(cid, n, text, check, skill_id):
        sk = next(s for s in SKILLS if s[0] == skill_id)
        uri = f"http://data.europa.eu/esco/skill/placeholder-{SKILLS.index(sk) + 1:04d}"
        return {"id": f"{cid}-{n}", "text": text, "how_we_check": check,
                "esco_uri": uri, "esco_label": sk[1]}

    cards = [{
        # the Lumo card as it ends up AFTER the demo rewrite (approved in seed so
        # seeded Sparks have card requirements to point at)
        "id": "card-co-lumo", "company_id": "co-lumo",
        "title": "Backend developer — make our CI fast again",
        "problem_90d": "Our CI pipeline takes 40 minutes for every merge. Releases slip and senior developers burn review time waiting on builds.",
        "must_haves": [
            req("req-lumo", 1, "Has made a slow build or CI pipeline measurably faster",
                "Walk us through one pipeline you sped up — what you changed and the before/after numbers", "sk-ci"),
            req("req-lumo", 2, "Builds backend services in Python",
                "Show and explain a Python service you wrote yourself", "sk-python"),
            req("req-lumo", 3, "Writes automated tests as part of daily work",
                "Describe a test that caught a real bug before release", "sk-test"),
        ],
        "nice_to_haves": ["Interest in mentoring juniors"],
        "languages": [
            {"language": "Finnish", "level": "B1", "task": "customer calls", "from_when": "by month 6"},
            {"language": "English", "level": "B2", "task": "daily team work", "from_when": "from day one"},
        ],
        "work_mode": "hybrid — Otaniemi office, 2 days on site",
        "status": "approved", "company_minutes_spent": 9,
    }]

    other_specs = [
        ("co-otava", "Platform engineer — tame our Kubernetes spend",
         "Cluster costs doubled this year and nobody owns capacity planning.", "sk-k8s", "sk-iac", "sk-obs"),
        ("co-taiga", "Gameplay tools developer — unblock the artists",
         "Artists wait hours for builds; a tool chain refresh is overdue.", "sk-ci", "sk-python", "sk-ui"),
        ("co-polar", "Data engineer — meter data pipeline",
         "Half a million meters report hourly and our ETL misses SLA twice a week.", "sk-etl", "sk-sql", "sk-python"),
        ("co-kide", "Full-stack developer — lab workflow app",
         "Lab technicians track samples on paper; errors cost us a week each quarter.", "sk-react", "sk-api", "sk-test"),
        ("co-vento", "Backend engineer — fleet telemetry",
         "Telemetry ingest drops events at rush hour and we cannot see why.", "sk-api", "sk-obs", "sk-sql"),
        ("co-haaga", "Front-end developer — accessible learning app",
         "Our app fails the municipal accessibility audit we must pass by spring.", "sk-react", "sk-a11y", "sk-test"),
        ("co-mero", "Software engineer — routing microservice",
         "Route recalculation takes 20 minutes; drivers idle while they wait.", "sk-python", "sk-api", "sk-ci"),
        ("co-keha", "Embedded developer — robot cell firmware",
         "Firmware releases require a technician on site; we need OTA updates.", "sk-embedded", "sk-test", "sk-ci"),
        ("co-aurora", "ML engineer — triage assistant",
         "Our triage model works in a notebook but has never been deployed.", "sk-ml", "sk-python", "sk-cloud"),
        ("co-kello", "Mobile developer — field service app",
         "Field techs lose work orders when coverage drops; offline sync is broken.", "sk-mobile", "sk-api", "sk-test"),
        ("co-sisu", "Analytics engineer — customer dashboards",
         "Customers wait weeks for reports our dashboards could render live.", "sk-sql", "sk-etl", "sk-react"),
    ]
    for cid, title, problem, s1, s2, s3 in other_specs:
        cards.append({
            "id": f"card-{cid}", "company_id": cid, "title": title, "problem_90d": problem,
            "must_haves": [
                req(f"req-{cid}", 1, f"Has hands-on experience with {skill_label(s1)}",
                    "Walk us through a concrete example from your own work", s1),
                req(f"req-{cid}", 2, f"Works confidently with {skill_label(s2)}",
                    "Show us something you built and explain your part in it", s2),
                req(f"req-{cid}", 3, f"Practises {skill_label(s3)}",
                    "Describe how you used it to solve a real problem", s3),
            ],
            "nice_to_haves": rng.sample(
                ["Curious about our domain", "Happy to pair-programme", "Writes things down"], 2),
            "languages": [{"language": "English", "level": "B2",
                           "task": "daily team work", "from_when": "from day one"}],
            "work_mode": rng.choice(["hybrid — Espoo office", "on-site Espoo", "remote-first, monthly Espoo day"]),
            "status": "approved", "company_minutes_spent": rng.randint(3, 11),
        })
    return comp, cards


def skill_label(sid):
    return next(s[1] for s in SKILLS if s[0] == sid)


def make_talents(rng, esco_uris):
    """300 talents; exactly enough trio-holders at each Finnish level to make the
    demo pool moment deterministic."""
    trio_ids = set(rng.sample(range(2, 300), TRIO_C2 + TRIO_B + TRIO_LOW))  # 44 picks
    talents, identities = [], []
    trio_list = sorted(trio_ids)
    fin_plan = (["C2"] * TRIO_C2
                + [weighted_choice(rng, [("B1", 0.6), ("B2", 0.4)]) for _ in range(TRIO_B)]
                + [weighted_choice(rng, [("A1", 0.5), ("A2", 0.5)]) for _ in range(TRIO_LOW)])
    rng.shuffle(fin_plan)

    amira_tid = "ta-0427"

    for i in range(1, 300):
        tid = f"ta-{i:04d}"
        first = FIRST[(i * 7 + rng.randrange(len(FIRST))) % len(FIRST)]
        last = LAST[(i * 13 + rng.randrange(len(LAST))) % len(LAST)]
        name = f"{first} {last}"
        if name == "Amira Haddad":  # keep the demo persona unique
            name = "Amira Saarinen"

        home = HOME_LANG[i % len(HOME_LANG)]
        languages = [{"language": home, "level": "C2"}]

        if i in trio_ids:
            fin = fin_plan[trio_list.index(i)]
            skills = list(TRIO) + rng.sample(
                [s for s, _, _ in SKILLS if s not in TRIO], rng.randint(0, 2))
            consent = 1
        else:
            fin = weighted_choice(rng, [("A1", 0.35), ("A2", 0.30), ("B1", 0.18),
                                        ("B2", 0.10), ("C1", 0.05), ("C2", 0.02)])
            skills = rng.sample([s for s, _, _ in SKILLS], rng.randint(1, 3))
            while all(t in skills for t in TRIO):  # never the full demo trio by accident
                skills.remove(rng.choice(TRIO))
            consent = 1 if rng.random() < 0.9 else 0

        languages.append({"language": "Finnish", "level": fin})
        languages.append({"language": "English",
                          "level": weighted_choice(rng, [("B1", 0.3), ("B2", 0.4),
                                                         ("C1", 0.2), ("C2", 0.1)])})

        claims = []
        for j, sk in enumerate(skills):
            tmpl = CLAIM_TEMPLATES[sk]
            if "{a}" in tmpl:
                a = rng.choice([25, 30, 45])
                text = tmpl.format(a=a, b=rng.choice([6, 8, 9]))
            else:
                text = tmpl
            confirmed = 1 if (i in trio_ids and sk in TRIO) or rng.random() < 0.9 else 0
            claims.append({
                "id": f"cl-{tid}-{j}", "text": text, "quote": text,
                "esco_uri": esco_uris[sk], "esco_label": skill_label(sk),
                "evidence_level": "own words", "confirmed": confirmed,
                "original_language": "en", "translated": 0,
            })

        label = skill_label(skills[0]).replace("develop ", "").replace("use ", "")
        talents.append({
            "id": tid, "pseudonym": f"Talent #{tid.split('-')[1]}",
            "languages": languages,
            "availability": rng.choice(["immediately", "in 1 month", "in 3 months"]),
            "pool_consent": consent,
            "headline": f"Works with {label}",
            "claims": claims,
        })
        identities.append({"talent_id": tid, "name": name,
                           "city": rng.choice(["Espoo", "Helsinki", "Vantaa"])})

    # --- Amira, the demo talent -------------------------------------------------
    talents.append({
        "id": amira_tid, "pseudonym": "Talent #0427",
        "languages": [{"language": "Arabic", "level": "C2"},
                      {"language": "English", "level": "B2"},
                      {"language": "Finnish", "level": "B1"}],
        "availability": "immediately", "pool_consent": 1,
        "headline": "Backend engineer — I make builds fast",
        "claims": [
            {"id": "cl-amira-build",
             "text": "I helped cut our build time from 30 to 6 minutes",
             "quote": "I helped cut our build time from 30 to 6 minutes",
             "esco_uri": esco_uris["sk-ci"],
             "esco_label": skill_label("sk-ci"),
             "evidence_level": "own words", "confirmed": 1,
             "original_language": "ar", "translated": 1},
            {"id": "cl-amira-pytest",
             "text": "I wrote most of the pytest suite we still run today",
             "quote": "I wrote most of the pytest suite we still run today",
             "esco_uri": esco_uris["sk-test"],
             "esco_label": skill_label("sk-test"),
             "evidence_level": "own words", "confirmed": 1,
             "original_language": "ar", "translated": 1},
            {"id": "cl-amira-fastapi",
             "text": "I built the FastAPI service that handles our payments",
             "quote": "I built the FastAPI service that handles our payments",
             "esco_uri": esco_uris["sk-python"],
             "esco_label": skill_label("sk-python"),
             "evidence_level": "own words", "confirmed": 1,
             "original_language": "ar", "translated": 1},
        ],
    })
    identities.append({"talent_id": amira_tid, "name": "Amira Haddad", "city": "Espoo"})
    return talents, identities


def make_sparks_and_meetings(rng, talents, cards):
    """Seeded Sparks: several sent into Lumo's inbox across its three card lines,
    two already accepted (=> meetings), one past-deadline refunded, and one of
    Amira's spent on another company."""
    trio_claim = {}
    by_skill = {}
    for t in talents:
        for c in t["claims"]:
            if c["confirmed"]:
                by_skill.setdefault(c["esco_uri"], []).append((t, c))
                if t["id"].startswith("ta-") and c["esco_uri"] == esco_of("sk-ci"):
                    trio_claim[t["id"]] = (t, c)

    sparks, meetings = [], []
    n = [0]

    def spark(talent, card_id, claim, req_id, status, note=None,
              deadline_hours=60, reason_chip=None, slot=None):
        n[0] += 1
        sid = f"sp-{n[0]:03d}"
        revealed = None
        sparks.append({
            "id": sid, "talent_id": talent["id"], "card_id": card_id,
            "claim_id": claim["id"], "requirement_id": req_id, "note": note,
            "status": status, "deadline_hours": deadline_hours,
            "reason_chip": reason_chip, "slot": slot,
        })
        return sid

    # 5 sent sparks to card-co-lumo across its requirements
    pick = {"req-lumo-1": [], "req-lumo-2": [], "req-lumo-3": []}
    lumo_req_skill = {"req-lumo-1": "sk-ci", "req-lumo-2": "sk-python", "req-lumo-3": "sk-test"}
    for req_id, sk in lumo_req_skill.items():
        uri = esco_of(sk)
        pool = [(t, c) for t, c in by_skill.get(uri, []) if t["id"] != "ta-0427"]
        rng.shuffle(pool)
        pick[req_id] = pool

    used = set()
    def take(req_id):
        for t, c in pick[req_id]:
            if t["id"] not in used:
                used.add(t["id"])
                return t, c
        raise RuntimeError("not enough claims")

    notes = {
        "req-lumo-1": ["Our builds were 45 minutes; now they are under 8.",
                       "I made our pipeline four times faster last year.", None],
        "req-lumo-2": ["Python services are my daily work.", None],
        "req-lumo-3": [None, "My tests caught three regressions last month."],
    }
    for req_id, req_notes in notes.items():
        for note in req_notes:
            t, c = take(req_id)
            spark(t, "card-co-lumo", c, req_id, "sent", note=note, deadline_hours=60)

    # 2 accepted sparks -> meetings (names revealed, slots 1 and 2)
    for i, req_id in enumerate(["req-lumo-1", "req-lumo-2"], start=1):
        t, c = take(req_id)
        sid = spark(t, "card-co-lumo", c, req_id, "accepted",
                    deadline_hours=-24, slot=slot_label(i - 1))
        meetings.append({"id": f"mt-{i:03d}", "spark_id": sid, "company_id": "co-lumo",
                         "card_id": "card-co-lumo", "talent_id": t["id"],
                         "slot": slot_label(i - 1)})

    # 1 sent spark that already missed its deadline -> refunded on read
    t, c = take("req-lumo-3")
    spark(t, "card-co-lumo", c, "req-lumo-3", "sent", deadline_hours=-10)

    # Amira has already spent one Spark on another company's card
    amira = next(t for t in talents if t["id"] == "ta-0427")
    mero_card = next(c for c in cards if c["id"] == "card-co-mero")
    spark(amira, mero_card["id"],
          next(c for c in amira["claims"] if c["esco_uri"] == esco_of("sk-python")),
          mero_card["must_haves"][0]["id"], "sent",
          note="Your routing service sounds like the payment service I built.",
          deadline_hours=48)

    # one accepted + meeting elsewhere so organiser/meeting views have content
    otava_card = next(c for c in cards if c["id"] == "card-co-otava")
    uri = esco_of("sk-k8s")
    t2, c2 = next((t, c) for t, c in by_skill.get(uri, []) if t["id"] not in used)
    sid = spark(t2, otava_card["id"], c2, otava_card["must_haves"][0]["id"],
                "accepted", deadline_hours=-30, slot=slot_label(0))
    meetings.append({"id": "mt-010", "spark_id": sid, "company_id": "co-otava",
                     "card_id": otava_card["id"], "talent_id": t2["id"],
                     "slot": slot_label(0)})

    return sparks, meetings


def esco_of(skill_id):
    i = next(i for i, s in enumerate(SKILLS, start=1) if s[0] == skill_id)
    return f"http://data.europa.eu/esco/skill/placeholder-{i:04d}"


def slot_label(i):
    from datetime import datetime, timedelta
    base = datetime(2026, 11, 26, 10, 0) + timedelta(minutes=20 * i)
    return base.strftime("%a %d %b · %H:%M")


# --- recorded demo content ----------------------------------------------------

def recorded_files():
    ad_text = (
        "Lumo Systems Oy is hiring a backend developer!\n"
        "We are a young and dynamic team of 14 in Otaniemi, Espoo, building the "
        "booking platform Finnish tradespeople rely on.\n\n"
        "You will fit right in if you have:\n"
        "- fluent Finnish (our customers call in Finnish)\n"
        "- Master's degree required in Computer Science or similar\n"
        "- solid Python experience and a habit of automated testing\n"
        "- no unexplained gaps in your CV\n\n"
        "The real problem waiting for you: our CI pipeline takes 40 minutes for "
        "every merge and it is eating the team's day. In your first 90 days you "
        "make it fast again.\n"
        "Photo on the CV appreciated. Apply now!"
    )
    card = {
        "id": "card-co-lumo-draft", "company_id": "co-lumo",
        "title": "Backend developer — make our CI fast again",
        "problem_90d": "Our CI pipeline takes 40 minutes for every merge. Releases slip and senior developers burn review time waiting on builds.",
        "must_haves": [
            {"id": "reqd-lumo-1", "text": "Has made a slow build or CI pipeline measurably faster",
             "how_we_check": "Walk us through one pipeline you sped up — what you changed and the before/after numbers",
             "esco_uri": esco_of("sk-ci"), "esco_label": skill_label("sk-ci")},
            {"id": "reqd-lumo-2", "text": "Builds backend services in Python",
             "how_we_check": "Show and explain a Python service you wrote yourself",
             "esco_uri": esco_of("sk-python"), "esco_label": skill_label("sk-python")},
            {"id": "reqd-lumo-3", "text": "Writes automated tests as part of daily work",
             "how_we_check": "Describe a test that caught a real bug before release",
             "esco_uri": esco_of("sk-test"), "esco_label": skill_label("sk-test")},
        ],
        "nice_to_haves": ["A fit for our young and dynamic team",
                          "Master's degree required"],
        "languages": [{"language": "Finnish", "level": "C2", "task": "",
                       "from_when": "day one"}],
        "work_mode": "hybrid — Otaniemi office, 2 days on site",
        "status": "draft", "company_minutes_spent": 0,
    }
    ad_lumo = {
        "company_id": "co-lumo",
        "match_substrings": ["Lumo Systems", "CI pipeline takes 40 minutes"],
        "ad_text": ad_text,
        "card": card,
        "followups": [
            "Is Finnish needed for customer calls or only internal chat — and by when?",
            "Which pipeline is the slow one — build, test or deploy?",
            "Is the Master's degree about a specific skill we should name instead?",
        ],
    }

    transcript = (
        "In my previous team at a payments company, our release builds took 30 minutes "
        "and everyone complained but nobody owned it. I helped cut our build time from "
        "30 to 6 minutes by caching the dependencies and splitting the test suite so "
        "the slow parts run in parallel. I wrote most of the pytest suite we still run "
        "today, and I built the FastAPI service that handles our payments. I also "
        "helped the team move to small daily releases instead of the big monthly one."
    )
    amira_story = {
        "talent_id": "ta-0427",
        "match_substrings": ["build time from", "pytest suite"],
        "transcript": transcript,
        "followups": [
            "You said the build dropped from 30 to 6 minutes — what exactly did you change?",
            "Was splitting the test suite your idea or the team's?",
            "Can you remember a time a fast build saved a release?",
        ],
        "claims": [
            {"id": "cl-amira-build", "text": "I helped cut our build time from 30 to 6 minutes",
             "quote": "I helped cut our build time from 30 to 6 minutes",
             "esco_uri": esco_of("sk-ci"), "esco_label": skill_label("sk-ci"),
             "evidence_level": "own words", "confirmed": True,
             "original_language": "ar", "translated": True},
            {"id": "cl-amira-pytest", "text": "I wrote most of the pytest suite we still run today",
             "quote": "I wrote most of the pytest suite we still run today",
             "esco_uri": esco_of("sk-test"), "esco_label": skill_label("sk-test"),
             "evidence_level": "own words", "confirmed": True,
             "original_language": "ar", "translated": True},
            {"id": "cl-amira-fastapi", "text": "I built the FastAPI service that handles our payments",
             "quote": "I built the FastAPI service that handles our payments",
             "esco_uri": esco_of("sk-python"), "esco_label": skill_label("sk-python"),
             "evidence_level": "own words", "confirmed": True,
             "original_language": "ar", "translated": True},
        ],
        "refused": [
            {"text": "Led the CI/CD transformation and owned the release pipeline end-to-end",
             "reason": "inflated verb: 'led/owned' — the quote only supports 'helped'"},
            {"text": "Expert in Kubernetes cluster operations",
             "reason": "no quote: nothing in the transcript supports this claim"},
        ],
    }

    twin_report = {
        "note": "PRECOMPUTED PLACEHOLDER — real batch runs on Modal (F18)",
        "runs": 2, "pairs": 1000,
        "variants": [
            {"name": "plain vs AI-polished prose", "flip_rate_pct": 2.1, "n": 1000},
            {"name": "Finnish name vs international name", "flip_rate_pct": 1.4, "n": 1000},
            {"name": "Finnish vs Arabic strongest language", "flip_rate_pct": 3.0, "n": 1000},
        ],
        "threshold_pct": 5.0, "passed": True, "provider": "mock",
        "generated_at": "2026-11-14T09:00:00+02:00",
    }
    return {"ad_lumo.json": ad_lumo, "amira_story.json": amira_story,
            "twin_report_at_root": twin_report}


def main(out_dir: Path | None = None):
    out_dir = out_dir or SEED_DIR
    esco_dir = ESCO_DIR
    rec_dir = out_dir / "recorded"
    for d in (out_dir, esco_dir, rec_dir):
        d.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)

    skills_file = build_skills_file()
    esco_uris = {s["id"]: s["uri"] for s in skills_file["skills"]}
    (esco_dir / "skills.json").write_text(
        json.dumps(skills_file, indent=2, ensure_ascii=False), encoding="utf-8")

    companies, cards = make_companies(rng)
    talents, identities = make_talents(rng, esco_uris)
    sparks, meetings = make_sparks_and_meetings(rng, talents, cards)

    # one seeded closure so the organiser tile has content
    closures = [{
        "id": "clz-001", "meeting_id": "mt-010", "outcome": "not_now",
        "reason_chips": ["Has hands-on experience with orchestrate containers with Kubernetes"],
        "next_step": None, "redirect_company_id": "co-keha",
        "message_to_talent": "Thank you for meeting Otava Cloud Oy. This time we are not "
                             "moving forward — the deciding requirement was hands-on "
                             "Kubernetes experience. Kehä Robotics Oy is looking for "
                             "adjacent skills and may be a better fit.",
        "support_banner": None, "created_hours_ago": 20,
    }]

    seed_files = {
        "event.json": EVENT,
        "companies.json": companies,
        "cards.json": cards,
        "talents.json": talents,
        "identities.json": identities,
        "sparks.json": sparks,
        "meetings.json": meetings,
        "closures.json": closures,
        "twin_report.json": recorded_files()["twin_report_at_root"],
    }
    for name, payload in seed_files.items():
        (out_dir / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                                    encoding="utf-8")

    rec = recorded_files()
    for name in ("ad_lumo.json", "amira_story.json"):
        (rec_dir / name).write_text(json.dumps(rec[name], indent=2, ensure_ascii=False),
                                    encoding="utf-8")

    # quick sanity print for whoever runs it
    c2 = sum(1 for t in talents
             if t["pool_consent"] and any(l["language"] == "Finnish" and l["level"] == "C2"
                                          for l in t["languages"])
             and all(any(c["confirmed"] and c["esco_uri"] == esco_uris[s] for c in t["claims"])
                     for s in TRIO))
    b1 = sum(1 for t in talents
             if t["pool_consent"] and any(l["language"] == "Finnish"
                                          and CEFR.index(l["level"]) >= CEFR.index("B1")
                                          for l in t["languages"])
             and all(any(c["confirmed"] and c["esco_uri"] == esco_uris[s] for c in t["claims"])
                     for s in TRIO))
    print(f"seed written to {out_dir}")
    print(f"demo pool check: trio+Finnish C2 = {c2} (want <10) | trio+Finnish B1+ = {b1} (want 20-49)")


if __name__ == "__main__":
    sys.exit(main())
