#!/usr/bin/env python3
"""Event-mode demo data (spec v4 section 6). Deterministic: re-running
writes byte-identical files.

Writes: events.json (E1 TalentMatch + E2 treffit), talent_registrations.json,
event_invites.json, and E1 additions to users.json / event_plan.json /
event_talks.json. Meetings are NOT written — the DB seeder computes them by
calling the real book_if_mutual() for every seeded invite.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "db" / "seed"

E1 = "ev-2027-03"
E2 = "ev-2026-11"


def _load(name: str):
    return json.loads((SEED / name).read_text(encoding="utf-8"))


def _dump(name: str, data) -> None:
    (SEED / name).write_text(json.dumps(data, indent=2, ensure_ascii=False)
                             + "\n", encoding="utf-8")


def _rank(key: str) -> str:
    return hashlib.md5(key.encode()).hexdigest()


# --- events ---------------------------------------------------------------------

E1_EVENT = {
    "id": E1,
    "name": "Espoo TalentMatch — spring 2027 (demo)",
    "date": "2027-03-19",
    "venue": "Aalto University metro square, Otaniemi (demo venue)",
    "advisor_note": "Advisors from Employment Espoo are there all day to "
                    "help you talk to employers.",
    "format": "talentmatch", "language": "en",
    "starts_at": "2027-03-19T13:00:00", "ends_at": "2027-03-19T17:30:00",
    "address": "Otaniementie 14, Espoo",
    "description": "A recruitment event for people who want to show what "
                   "they can do — employers describe a real need, you meet "
                   "them by mutual interest.",
    "programme": [
        {"start": "13:00", "end": "14:00", "title": "Employer pitches",
         "kind": "pitch"},
        {"start": "13:00", "end": "14:30",
         "title": "Workshop: talking about transferable skills",
         "kind": "workshop"},
        {"start": "14:30", "end": "17:30", "title": "1:1 meetings",
         "kind": "one_to_one"},
        {"start": "14:30", "end": "17:30", "title": "Job fair",
         "kind": "fair"},
        {"start": "13:00", "end": "17:30", "title": "Explore fair",
         "kind": "presentation"},
    ],
    "capacity": 300, "slot_minutes": 10,
    "need_deadline": "2027-02-19", "publish_date": "2027-03-05",
    "time_groups": [
        {"id": "A", "label": "Group A", "entry": "14:30"},
        {"id": "B", "label": "Group B", "entry": "15:30"},
        {"id": "C", "label": "Group C", "entry": "16:30"},
    ],
}

E2_EVENT = {
    "id": E2,
    "name": "Työnantajatreffit at Sello library (demo)",
    "date": "2026-11-26",
    "venue": "Leppävaara service point, Sello, 2nd floor",
    "advisor_note": "Advisors from Employment Espoo are there all day to "
                    "help you talk to employers.",
    "format": "treffit", "language": "fi",
    "starts_at": "2026-11-26T12:00:00", "ends_at": "2026-11-26T15:00:00",
    "address": "Leppävaarankatu 3–9, Espoo",
    "description": "Meet employers face to face. An employer presentation "
                   "at 12:00, then walk-in conversations.",
    "programme": [
        {"start": "12:00", "end": "12:30", "title": "Employer presentation",
         "kind": "presentation"},
        {"start": "12:30", "end": "15:00", "title": "Walk-in interviews",
         "kind": "walk_in"},
    ],
    "capacity": 0, "slot_minutes": 10,
    "need_deadline": "", "publish_date": "",
    "time_groups": [],
}

# --- need cards (9 submitted, 2 late, 3 missing) -----------------------------------

def _card(first_week, must_haves, will_teach, languages, job_ids):
    return {"first_week": first_week,
            "must_haves": [{"text": t, "why": w} for t, w in must_haves],
            "will_teach": will_teach, "languages": languages,
            "job_ids": job_ids}


NEED = {
    "emp-cafe-koivu": _card(
        ["Learn the till and the coffee menu with a buddy",
         "Serve the lunch queue 11:00–14:00",
         "Do the closing clean-up with a teammate"],
        [("You can stand and move for a 4-hour shift",
          "lunch service happens standing at the counter"),
         ("You can work some Saturdays",
          "Saturday is our busiest day")],
        ["Hygiene basics for food work", "The till system"],
        [{"name": "Finnish", "level": "A2",
          "task": "understand lunch orders"}],
        ["job-cafe-weekday", "job-cafe-weekend"]),
    "emp-siivouspot": _card(
        ["Do the school cleaning round with an experienced cleaner",
         "Learn which products go on which surface"],
        [("You are careful with details",
          "schools are checked room by room")],
        ["All machines and products", "The safety rules"],
        [{"name": "Finnish", "level": "A1",
          "task": "understand the daily work list"}],
        []),
    "emp-market-olari": _card(
        ["Restock shelves in the morning delivery",
         "Run the till during the evening rush",
         "Help customers find products"],
        [("You can lift crates up to 10 kg",
          "the morning delivery has to be shelved fast"),
         ("You can work evenings until 21:00",
          "the evening rush needs extra hands")],
        ["The till and the ordering system"],
        [{"name": "Finnish", "level": "A2",
          "task": "help customers at the till"}],
        []),
    "emp-aurora-care": _card(
        ["Join the morning round with a care worker",
         "Sit with residents at coffee time",
         "Help serve lunch"],
        [("You are patient and calm",
          "residents need time and attention")],
        ["Safe ways to help people move", "The daily routines"],
        [{"name": "Finnish", "level": "B1",
          "task": "chat with residents"}],
        []),
    "emp-freight": _card(
        ["Learn the parcel sorting line",
         "Load delivery vans with a scanner"],
        [("You can do physical work for a full shift",
          "parcels are lifted and sorted all shift")],
        ["The scanner and the sorting codes", "Safe lifting"],
        [{"name": "Finnish", "level": "A1",
          "task": "understand safety instructions"}],
        ["job-freight-pick"]),
    "emp-tiima": _card(
        ["Work with a finisher on the sports hall site",
         "Carry materials and keep the site tidy"],
        [("You have a valid occupational safety card",
          "the site requires it by law"),
         ("You are on time at 7:00",
          "the crew briefs together every morning")],
        ["Site routines", "Power tools basics"],
        [{"name": "Finnish", "level": "A2",
          "task": "follow spoken instructions on site"}],
        ["job-tiima-helper"]),
    "emp-otava": _card(
        ["Pair with a developer on a real bug",
         "Join the daily stand-up and demo Fridays"],
        [("You have built something on your own",
          "we need to see how you solve problems")],
        ["Our stack and code review habits"],
        [{"name": "English", "level": "B2",
          "task": "discuss technical work"}],
        []),
    "emp-kuusikko": _card(
        ["Help teachers in the lunch room and the yard",
         "Run a craft table for the after-school club"],
        [("You like working with children",
          "every task is with the kids, not behind a desk")],
        ["The school's daily rhythm", "Child safety basics"],
        [{"name": "Finnish", "level": "B1",
          "task": "talk with children and parents"}],
        []),
    "emp-rantala": _card(
        ["Do the maintenance round in two housing companies",
         "Learn the fault-report app"],
        [("You can use a phone for work reports",
          "faults are logged in the app, not on paper")],
        ["The round routes", "Basic plumbing and lighting fixes"],
        [{"name": "Finnish", "level": "A2",
          "task": "read work orders"}],
        ["job-rantala-huolto"]),
}

# employer_id, booth, slots, formats, submitted_at (None = missing)
E1_EMPLOYERS = [
    ("emp-cafe-koivu",  "A1",  8,  ["one_to_one", "walk_in"], "2027-02-16"),
    ("emp-siivouspot",  "A2",  10, ["one_to_one"],            "2027-02-18"),
    ("emp-market-olari","A3",  6,  ["one_to_one", "walk_in"], "2027-02-15"),
    ("emp-aurora-care", "A4",  8,  ["one_to_one", "pitch"],   "2027-02-17"),
    ("emp-freight",     "B1",  12, ["one_to_one", "walk_in"], "2027-02-19"),
    ("emp-tiima",       "B2",  8,  ["one_to_one"],            "2027-02-18"),
    ("emp-otava",       "B3",  6,  ["one_to_one"],            "2027-02-22"),  # late
    ("emp-kuusikko",    "B4",  6,  ["one_to_one", "walk_in"], "2027-02-25"),  # late
    ("emp-rantala",     "C1",  9,  ["one_to_one"],            "2027-02-14"),
    ("emp-espoolive",   "C2",  8,  ["walk_in", "pitch"],      None),
    ("emp-hymy",        "C3",  6,  ["one_to_one"],            None),
    ("emp-kulma",       "C4",  10, ["one_to_one", "walk_in"], None),
]

# --- talent cards -----------------------------------------------------------------

DONE_EN = [
    "Ran the till alone on Saturdays at a kiosk",
    "Fixed bikes for neighbours",
    "Organised a 40-person food bank shift",
    "Cooked lunch for a crew of twenty",
    "Kept a hockey team's equipment room in order",
    "Drove an aunt to appointments every week",
    "Ran a market stall two summers in a row",
    "Built shelves and repaired chairs at home",
    "Coached a kids' football team for a season",
    "Handled returns and complaints at a clothing shop",
    "Cleaned a stairwell company contract alone",
    "Translated letters for a community group",
    "Packed online orders in a warehouse for a summer",
    "Led a sewing circle at the library",
    "Cared for two grandparents at home",
    "Picked berries for a farm every July",
    "Managed the cash box for a school fair",
    "Painted flats for a small contractor",
    "Walked shelter dogs every weekend",
    "Set up phones and tablets for older people",
]

DONE_FI = [
    "Hoidin kassan yksin lauantaisin kioskilla",
    "Korjasin naapurien pyöriä",
    "Järjestin 40 hengen ruokajakeluvuoron",
    "Tein ruuat parikymmenelle työmiehelle",
    "Pidin harrastusjoukkueen varustehuonetta kunnossa",
    "Ajoin mummon lääkärikäynneille joka viikko",
    "Myin toriaalla kaksi kesää",
    "Tein hyllyjä ja korjasin tuoleja kotona",
    "Valmensin lasten jalkapallojoukkuetta kauden",
    "Hoidin palautukset vaatekaupassa",
    "Siivosin portaistalon sopimuksella yksin",
    "Käänsin kirjeitä yhdistykselle",
    "Pakkesin verkkokauppatilauksia varastolla",
    "Johdin ompelupiiriä kirjastossa",
    "Hoidin kahta vanhusta kotona",
    "Poimin marjoja tilalla joka heinäkuu",
    "Hoidin koulun talkoiden rahat",
    "Maalasin asuntoja pienyrityksessä",
    "Ulkoilutin koiran tarhalla viikonloppuisin",
    "Opetin vanhuksia käyttämään puhelinta",
]

LOOKING = {
    "en": "Steady part-time work I can do for a long time",
    "fi": "Vakaa osa-aikatyö, jota voin tehdä pitkään",
    "ar": "Steady part-time work I can do for a long time",
    "ru": "Steady part-time work I can do for a long time",
    "uk": "Steady part-time work I can do for a long time",
}

DISTRICTS = ["leppavaara", "tapiola", "otaniemi", "matinkyla", "olari",
             "niittykumpu", "espoon_keskus", "espoonlahti", "kauklahti"]

FIRST = ["Aisha", "Bogdan", "Camila", "Dmytro", "Elif", "Farah", "Gabriel",
         "Hanna", "Ivan", "Jasmin", "Kofi", "Leila", "Mateo", "Nadia",
         "Omar", "Priya", "Qasim", "Rosa", "Samir", "Tara", "Umar", "Vera",
         "Wei", "Xiomara", "Youssef", "Zahra", "Abel", "Bianca", "Cyrus",
         "Dalia", "Emil", "Fatou", "Giorgi", "Hector", "Ines", "Jamal",
         "Katya", "Luca", "Mira", "Noah"]
LAST = ["Ahmed", "Baran", "Costa", "Diallo", "Elmi", "Farsi", "Garcia",
        "Haddad", "Ilic", "Jafari", "Kaur", "Lopez", "Mbeki", "Ngo",
        "Osei", "Petros", "Quintero", "Rahmani", "Sall", "Traore",
        "Usman", "Vega", "Wang", "Xu", "Yilmaz", "Zayed", "Aziz", "Brito",
        "Camara", "Demir", "Eze", "Fofana", "Gupta", "Hassan", "Idris",
        "Jallow", "Kone", "Lema", "Mansour"]

LANG_ORDER = (["en"] * 10 + ["fi"] * 10 + ["ar"] * 10
              + ["ru"] * 5 + ["uk"] * 5)   # 40, indices 0-39


def _talent_user(i: int, lang: str) -> dict:
    """TalentNN: fictional name, varied district/availability."""
    name = f"{FIRST[i % len(FIRST)]} {LAST[i % len(LAST)]}"
    district = DISTRICTS[int(_rank(f"d{i}")[:4], 16) % len(DISTRICTS)]
    base = {"en": "English", "fi": "Finnish", "ar": "Arabic",
            "ru": "Russian", "uk": "Ukrainian"}[lang]
    avail = ["fri-afternoon"]
    if int(_rank(f"a{i}")[:2], 16) % 2:
        avail += ["sat-morning", "sat-afternoon"]
    if int(_rank(f"b{i}")[:2], 16) % 3:
        avail += ["mon-morning", "wed-afternoon"]
    return {
        "id": f"u-talent{i + 1:02d}",
        "email": f"talent{i + 1:02d}@example.com",
        "password": "demo1234", "role": "resident", "name": name,
        "profile": {
            "contact_method": "email", "district": district,
            "fields": [], "availability": avail,
            "max_hours_per_week": 20 + int(_rank(f"h{i}")[:2], 16) % 18,
            "needs": [],
            "languages": [{"language": base, "level": "C2"},
                          {"language": "English",
                           "level": ["A2", "B1", "B2", "C1"]
                           [int(_rank(f"l{i}")[:2], 16) % 4]},
                          {"language": "Finnish",
                           "level": ["A1", "A2", "B1"]
                           [int(_rank(f"f{i}")[:2], 16) % 3]}],
            "about": "",
        },
    }


def _card_for(i: int, lang: str) -> dict:
    """done items from the EN or FI pool, deterministic per talent."""
    pool = DONE_FI if lang == "fi" else DONE_EN
    n = 2 + int(_rank(f"n{i}")[:2], 16) % 2          # 2 or 3 items
    start = int(_rank(f"s{i}")[:4], 16) % len(pool)
    items = [pool[(start + k * 7) % len(pool)] for k in range(n)]
    return {
        "done": [{"text": t, "own_words": t} for t in items],
        "looking_for": LOOKING[lang],
        "district": DISTRICTS[int(_rank(f"d{i}")[:4], 16) % len(DISTRICTS)],
        "availability": ["fri-afternoon"]
        + (["sat-morning"] if int(_rank(f"a{i}")[:2], 16) % 2 else []),
    }


def _special_card(uid: str) -> dict:
    cards = {
        "u-aino": {"done": [
            {"text": "Hoidin kassan ja kahvit yksin torikahviossa",
             "own_words": "Hoidin kassan ja kahvit yksin torikahviossa"},
            {"text": "Järjestin kirjaston satutunnan vapaaehtoisena",
             "own_words": "Järjestin kirjaston satutunnan vapaaehtoisena"}],
            "looking_for": LOOKING["fi"], "district": "otaniemi",
            "availability": ["fri-afternoon", "sat-morning"]},
        "u-pekka": {"done": [
            {"text": "Ajoin jakeluautoa yötöissä kaksi vuotta",
             "own_words": "Ajoin jakeluautoa yötöissä kaksi vuotta"},
            {"text": "Korjasin taloyhtiön pyöriä ja rappusia",
             "own_words": "Korjasin taloyhtiön pyöriä ja rappusia"}],
            "looking_for": LOOKING["fi"], "district": "matinkyla",
            "availability": ["fri-afternoon"]},
        "u-amira": {"done": [
            {"text": "Cooked iftar meals for sixty people",
             "own_words": "Cooked iftar meals for sixty people"},
            {"text": "Kept a neighbourhood WhatsApp group running",
             "own_words": "Kept a neighbourhood WhatsApp group running"}],
            "looking_for": LOOKING["ar"], "district": "espoonlahti",
            "availability": ["fri-afternoon", "sat-afternoon"]},
    }
    return cards[uid]


def main() -> int:
    users = _load("users.json")
    users = [u for u in users if not u["id"].startswith("u-talent")]
    users += [_talent_user(i, LANG_ORDER[i]) for i in range(40)]
    _dump("users.json", users)

    # registrations: demo residents first, then talent01..40
    regs = [
        {"id": "tr-e1-001", "event_id": E1, "user_id": "u-aino",
         "time_group": "A", "status": "registered",
         "card_language": "fi", "card": _special_card("u-aino"),
         "days_ago": 20},
        {"id": "tr-e1-002", "event_id": E1, "user_id": "u-pekka",
         "time_group": "B", "status": "registered",
         "card_language": "fi", "card": _special_card("u-pekka"),
         "days_ago": 19},
        {"id": "tr-e1-003", "event_id": E1, "user_id": "u-amira",
         "time_group": "C", "status": "registered",
         "card_language": "ar", "card": _special_card("u-amira"),
         "days_ago": 18},
    ]
    groups = "A" * 14 + "B" * 13 + "C" * 13
    for i in range(40):
        lang = LANG_ORDER[i]
        regs.append({
            "id": f"tr-e1-{i + 4:03d}", "event_id": E1,
            "user_id": f"u-talent{i + 1:02d}", "time_group": groups[i],
            "status": "registered", "card_language": lang,
            "card": _card_for(i, lang), "days_ago": 15 - (i % 12)})
    _dump("talent_registrations.json", regs)

    # employers on the event
    e1 = dict(E1_EVENT)
    e1["employers"] = [
        {"employer_id": eid, "booth": booth, "slots": slots,
         "formats": fmts,
         "need_card": NEED.get(eid) if submitted else None,
         "need_submitted_at": submitted,
         "need_by": "employer" if submitted else None,
         "reminders_sent": 1 if submitted is None else 0,
         "last_reminder_at": "2027-02-20T10:00:00"
         if submitted is None else None}
        for eid, booth, slots, fmts, submitted in E1_EMPLOYERS]
    _dump("events.json", [e1, dict(E2_EVENT)])

    # interests ~70: reg index -> employer picks (deterministic)
    emp_ids = [e[0] for e in E1_EMPLOYERS]
    plans = [p for p in _load("event_plan.json") if p["event_id"] != E1]
    e1_plans = []
    # demo residents are interested in the employers they will talk to
    forced = [("u-aino", "emp-cafe-koivu"), ("u-pekka", "emp-freight"),
              ("u-amira", "emp-aurora-care")]
    for uid, eid in forced:
        mh = NEED.get(eid, {}).get("must_haves", [])
        e1_plans.append({"user_id": uid, "event_id": E1,
                         "employer_id": eid,
                         "meets": list(range(len(mh))),
                         "language_levels": {l["name"]: l["level"]
                                             for l in NEED.get(eid, {})
                                             .get("languages", [])}})
    for ri, reg in enumerate(regs):
        uid, rid = reg["user_id"], reg["id"]
        n = [2, 1, 2, 1, 2, 2, 1, 2][ri % 8]        # avg ~1.9 -> ~70
        order = sorted(emp_ids, key=lambda e: _rank(uid + e))
        for eid in order[:n]:
            mh = NEED.get(eid, {}).get("must_haves", [])
            meets = list(range(len(mh))) \
                if int(_rank(uid + eid)[:2], 16) % 3 else \
                list(range(max(0, len(mh) - 1)))
            langs = {l["name"]: l["level"]
                     for l in NEED.get(eid, {}).get("languages", [])}
            e1_plans.append({"user_id": uid, "event_id": E1,
                             "employer_id": eid,
                             "meets": meets, "language_levels": langs})
    _dump("event_plan.json", plans + e1_plans)

    # invites ~40: employers invite interested talents; a few outside for
    # mutuals that never become meetings
    interest_pairs = {(p["user_id"], p["employer_id"])
                      for p in e1_plans}
    by_emp: dict[str, list[str]] = {}
    reg_by_user = {r["user_id"]: r["id"] for r in regs}
    for p in e1_plans:
        by_emp.setdefault(p["employer_id"], []).append(p["user_id"])
    invites = []
    invited_pairs = {(iv["employer_id"], iv["registration_id"])
                     for iv in invites}
    for eid, *_ in E1_EMPLOYERS:
        cands = sorted(by_emp.get(eid, []), key=lambda u: _rank(eid + u))
        # ~4-5 per card employer, fewer for the missing-card ones
        want = 5 if eid in NEED else 3
        first = [u for u, e in forced if e == eid]
        for uid in first + [u for u in cands if u not in first][:want - len(first)]:
            invites.append({"event_id": E1, "employer_id": eid,
                            "registration_id": reg_by_user[uid],
                            "days_ago": 10})
    invites = invites[:40]
    _dump("event_invites.json", invites)

    # talks for a subset of mutual pairs (meeting_id resolved at seed);
    # >=3 talks for the demo residents
    talks = [t for t in _load("event_talks.json") if t["event_id"] != E1]
    mutual = [(iv["employer_id"],
               next(r["user_id"] for r in regs
                    if r["id"] == iv["registration_id"]))
              for iv in invites
              if (next(r["user_id"] for r in regs
                       if r["id"] == iv["registration_id"]),
                  iv["employer_id"]) in interest_pairs]
    want_pairs = [("emp-cafe-koivu", "u-aino"),
                  ("emp-freight", "u-pekka"),
                  ("emp-aurora-care", "u-amira")]
    rest = [m for m in mutual if (m[0], m[1]) not in want_pairs][:12]
    talk_pairs = want_pairs + rest
    for k, (eid, uid) in enumerate(talk_pairs):
        fw = NEED.get(eid, {}).get("first_week", [])
        answered = k % 3 != 1
        t = {"id": f"et-e1-{k + 1:03d}", "event_id": E1, "user_id": uid,
             "employer_id": eid,
             "observed": fw[:2],
             "status": "answered" if answered else "talked",
             "days_ago_talked": 2 + (k % 4)}
        if answered:
            t["outcome"] = "next_step" if k % 4 else "not_now"
            t["employer_note"] = (
                "Asked them to come for a trial shift next week."
                if t["outcome"] == "next_step" else
                "Not this time — needs more spoken Finnish for the till.")
            t["days_ago_answered"] = 1 + (k % 2)
        talks.append(t)
    _dump("event_talks.json", talks)

    # visitor codes for every E1 registration (4-digit, deterministic)
    vis = [v for v in _load("event_visitors.json")
           if v["event_id"] != E1]
    vis += [{"user_id": r["user_id"], "event_id": E1,
             "code": f"{1000 + int(r['id'].rsplit('-', 1)[1]) * 37 % 9000:04d}"}
            for r in regs if r["event_id"] == E1]
    _dump("event_visitors.json", vis)

    n_mutual = sum(1 for m in mutual)
    from collections import Counter
    langs = Counter(r["card_language"] for r in regs)
    print(f"events: {[e['id'] for e in _load('events.json')]}")
    print(f"registrations: {len(regs)} by language {dict(langs)}")
    print(f"interests: {len(e1_plans)}, invites: {len(invites)}, "
          f"mutual: {n_mutual}, talks: {len(talk_pairs)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
