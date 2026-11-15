#!/usr/bin/env python3
"""Event-mode demo data (spec v4 section 6). Deterministic: re-running
writes byte-identical files.

Writes: events.json (E1 TalentMatch + E3 online + E0 past), talent_registrations.json,
event_invites.json, and E1 additions to users.json / event_plan.json /
event_talks.json. Meetings are NOT written — the DB seeder computes them by
calling the real book_if_mutual() for every seeded invite.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "db" / "seed"

E1 = "ev-2027-03"
E3 = "ev-2027-02"   # online event (spec §9.1)
E0 = "ev-2026-10"


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
    "format": "in_person", "series": "talentmatch", "language": "en",
    "starts_at": "2027-03-19T13:00:00", "ends_at": "2027-03-19T17:30:00",
    "address": "Otaniementie 14, Espoo",
    "registration_opens": "2027-02-01T09:00:00",
    "matching_closes": "2027-03-14T23:59:00",
    "answers_due": "2027-03-26T23:59:00",
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

E3_EVENT = {
    "id": E3,
    "name": "Espoo TalentMatch Online — customer service & IT (demo)",
    "date": "2027-02-10",
    "venue": "Online — in the event lobby (demo)",
    "advisor_note": "Advisors from Employment Espoo answer in the lobby "
                    "all day.",
    "format": "online", "series": "talentmatch", "language": "en",
    "starts_at": "2027-02-10T10:00:00",
    "ends_at": "2027-02-10T14:00:00",
    "address": "",
    "registration_opens": "2027-01-12T09:00:00",
    "matching_closes": "2027-02-05T23:59:00",
    "answers_due": "2027-02-17T23:59:00",
    "description": "The same mutual-choice recruitment event, held "
                   "online. Employers pitch on the stage, talks happen "
                   "in video calls you can join from the lobby.",
    "programme": [
        {"start": "09:55", "end": "10:00", "title": "Lobby opens",
         "kind": "presentation"},
        {"start": "10:00", "end": "10:30", "title": "Employer pitches",
         "kind": "pitch"},
        {"start": "10:30", "end": "13:30", "title": "1:1 video meetings",
         "kind": "one_to_one"},
        {"start": "11:00", "end": "11:30",
         "title": "Workshop: talking about transferable skills",
         "kind": "workshop"},
        {"start": "13:30", "end": "14:00",
         "title": "Networking lounge open hour", "kind": "lounge"},
    ],
    "capacity": 80, "slot_minutes": 15,
    "need_deadline": "2027-01-30", "publish_date": "2027-01-26",
    "time_groups": [
        {"id": "A", "label": "Lobby entry", "entry": "09:55"},
    ],
}

# 8 online employers (customer service & IT), V1..V8 virtual booths
E3_EMPLOYERS = [
    ("emp-lumo",       "V1", 8),
    ("emp-otava",      "V2", 6),
    ("emp-koodikallio","V3", 6),
    ("emp-datavirta",  "V4", 6),
    ("emp-linja",      "V5", 8),
    ("emp-laguuni",    "V6", 8),
    ("emp-avara",      "V7", 6),
    ("emp-merituuli",  "V8", 6),
]

E0_EVENT = {
    "id": E0,
    "name": "Työnantajatreffit at Iso Omena — autumn 2026 (demo)",
    "date": "2026-10-08",
    "venue": "Iso Omena library (demo)",
    "advisor_note": "",
    "format": "in_person", "series": "treffit", "language": "fi",
    "starts_at": "2026-10-08T12:00:00", "ends_at": "2026-10-08T15:00:00",
    "address": "Suomenlahdentie 1, Espoo",
    "registration_opens": "2026-09-01T09:00:00",
    "matching_closes": "2026-10-03T23:59:00",
    "answers_due": "2026-10-15T23:59:00",
    "description": "A past recruitment afternoon at Iso Omena library.",
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

E0_EMPLOYERS = ["emp-cafe-koivu", "emp-market-olari", "emp-aurora-care",
                "emp-freight", "emp-siivouspot", "emp-rantala"]

# E0 participants: demo residents + talent users (15 people)
E0_TALENT = ["u-aino", "u-pekka", "u-amira"] +     [f"u-talent{i:02d}" for i in range(1, 13)]

# ~15 E0 conversations (employer, talent) — all answered within 7 days
E0_TALKS = [
    ("emp-cafe-koivu",  "u-aino",     "next_step"),
    ("emp-cafe-koivu",  "u-talent02", "not_now"),
    ("emp-cafe-koivu",  "u-talent07", "next_step"),
    ("emp-market-olari","u-aino",     "next_step"),
    ("emp-market-olari","u-talent03", "not_now"),
    ("emp-aurora-care", "u-amira",    "next_step"),
    ("emp-aurora-care", "u-talent05", "next_step"),
    ("emp-aurora-care", "u-talent09", "not_now"),
    ("emp-freight",     "u-pekka",    "next_step"),
    ("emp-freight",     "u-talent04", "not_now"),
    ("emp-siivouspot",  "u-talent01", "next_step"),
    ("emp-siivouspot",  "u-talent06", "not_now"),
    ("emp-rantala",     "u-talent08", "next_step"),
    ("emp-rantala",     "u-talent10", "not_now"),
    ("emp-rantala",     "u-talent11", "next_step"),
]

# ~12 kudos given at E0 (label set from the fixed list)
E0_KUDOS = [
    ("emp-cafe-koivu",  "u-aino",     "explains_clearly"),
    ("emp-market-olari","u-aino",     "helped_others"),
    ("emp-cafe-koivu",  "u-talent02", "customer_focus"),
    ("emp-market-olari","u-talent03", "reliable"),
    ("emp-aurora-care", "u-amira",    "team_player"),
    ("emp-aurora-care", "u-talent05", "learns_fast"),
    ("emp-aurora-care", "u-talent09", "customer_focus"),
    ("emp-freight",     "u-pekka",    "reliable"),
    ("emp-freight",     "u-talent04", "solved_task"),
    ("emp-siivouspot",  "u-talent01", "learns_fast"),
    ("emp-rantala",     "u-talent08", "team_player"),
    ("emp-rantala",     "u-talent11", "explains_clearly"),
]

# 20 connections (event, person a, person b) — canonical order is set by
# the loader; a mix of employer-talent and talent-talent
E0_CONNECTIONS = [
    ("u-sanna",    "u-aino"),     ("u-sanna",    "u-talent02"),
    ("u-sanna",    "u-talent07"), ("u-aino",     "u-pekka"),
    ("u-aino",     "u-amira"),    ("u-aino",     "u-talent03"),
    ("u-pekka",    "u-talent04"), ("u-amira",    "u-talent05"),
    ("u-talent01", "u-talent02"), ("u-talent03", "u-talent04"),
    ("u-talent05", "u-talent06"), ("u-talent07", "u-talent08"),
    ("u-talent09", "u-talent10"), ("u-talent11", "u-talent12"),
    ("u-sanna",    "u-talent01"), ("u-aino",     "u-talent07"),
    ("u-pekka",    "u-talent06"), ("u-amira",    "u-talent09"),
    ("u-talent08", "u-talent12"), ("u-sanna",    "u-pekka"),
]

E1_CONNECTIONS = [
    ("u-sanna",    "u-aino"),     ("u-aino",     "u-talent02"),
]


def _pass_token(event_id: str, user_id: str) -> str:
    import hashlib
    return hashlib.sha256(
        f"pass:{event_id}:{user_id}".encode()).hexdigest()[:22]

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
    ("emp-market-olari","A3",  8,  ["one_to_one", "walk_in"], "2027-02-15"),
    ("emp-aurora-care", "A4",  8,  ["one_to_one", "pitch"],   "2027-02-17"),
    ("emp-freight",     "B1",  12, ["one_to_one", "walk_in"], "2027-02-19"),
    ("emp-tiima",       "B2",  8,  ["one_to_one"],            "2027-02-18"),
    ("emp-otava",       "B3",  6,  ["one_to_one"],            "2027-02-22"),  # late
    ("emp-kuusikko",    "B4",  8,  ["one_to_one", "walk_in"], "2027-02-25"),  # late
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

LOOKING_EN = [
    "Steady part-time work I can keep for a long time",
    "A job with people, a few days a week",
    "Work where I can use my hands",
    "Shop or café work near home",
    "Cleaning or kitchen work, mornings or evenings",
    "Care or helper work with older people",
    "Warehouse or delivery work I can learn fast",
    "Customer work where I can use my languages",
    "A calm job I can combine with family life",
    "Work with children or in a school",
    "Any honest work — I learn quickly",
    "Computer or office work I can grow into",
]
LOOKING_FI = [
    "Vakaa osa-aikatyö, jota voin tehdä pitkään",
    "Työ ihmisten parissa muutamana päivänä viikossa",
    "Työ, jossa pääsen käyttämään käsiä",
    "Kaupan tai kahvilan työ lähellä kotia",
    "Siivous- tai keittiötyö aamuin tai illoin",
    "Vanhusten avustamis- tai hoitotyö",
    "Varasto- tai jakelutyö, jonka opin nopeasti",
    "Asiakastyö, jossa pääsen käyttämään kieliä",
    "Rauhallinen työ, jonka voin yhdistää perhe-elämään",
    "Työ lasten kanssa tai koulussa",
    "Rehellistä työtä — opin nopeasti",
    "Toimisto- tai tietokonetyö, jossa voin kasvaa",
]
LOOKING = {
    "en": LOOKING_EN[0],
    "fi": LOOKING_FI[0],
    "ar": LOOKING_EN[0],
    "ru": LOOKING_EN[0],
    "uk": LOOKING_EN[0],
}


def _looking(done_texts: list[str], lang: str) -> str:
    """A plain phrase that varies with the person's done items."""
    pool = LOOKING_FI if lang == "fi" else LOOKING_EN
    h = int(_rank("look|" + "|".join(done_texts))[:6], 16)
    return pool[h % len(pool)]

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
        "looking_for": _looking(items, lang),
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
            "looking_for": "Kaupan, kahvilan tai kirjaston työ",
            "district": "otaniemi",
            "availability": ["fri-afternoon", "sat-morning"]},
        "u-pekka": {"done": [
            {"text": "Ajoin jakeluautoa yötöissä kaksi vuotta",
             "own_words": "Ajoin jakeluautoa yötöissä kaksi vuotta"},
            {"text": "Korjasin taloyhtiön pyöriä ja rappusia",
             "own_words": "Korjasin taloyhtiön pyöriä ja rappusia"}],
            "looking_for": "Kuljetus- tai korjaustyö, jossa näkee tuloksen",
            "district": "matinkyla",
            "availability": ["fri-afternoon"]},
        "u-amira": {"done": [
            {"text": "Cooked iftar meals for sixty people",
             "own_words": "Cooked iftar meals for sixty people"},
            {"text": "Kept a neighbourhood WhatsApp group running",
             "own_words": "Kept a neighbourhood WhatsApp group running"}],
            "looking_for": "Kitchen or community work, part-time",
            "district": "espoonlahti",
            "availability": ["fri-afternoon", "sat-afternoon"]},
    }
    return cards[uid]


# --- v12: employer profiles + need cards for E2 and E0 ---------------------------

PALETTE = ["#1e3a8a", "#14532d", "#7c2d12", "#4a044e",
           "#713f12", "#0c4a6e", "#831843", "#3f3f46"]

FIELD_TAGLINE = {
    "cleaning": "Cleaning services for schools, offices and homes",
    "retail": "A local shop with a small steady team",
    "restaurant": "Food and coffee, made on site",
    "care": "Care work where people know your name",
    "logistics": "Deliveries and driving in the Helsinki region",
    "office": "Office and admin support for local companies",
    "customer_service": "Helping customers by phone, chat and face to face",
    "education": "Learning and library work for the city",
    "construction": "Building and renovation work in Espoo",
    "tech": "Software and IT work, small expert teams",
    "seasonal": "Seasonal outdoor work through the year",
    "manufacturing": "Workshop and production work",
    "health": "Health services close to home",
    "maintenance": "Keeping buildings running every day",
}

FIELD_WELCOME = {
    "cleaning": "You work with an experienced cleaner for your first two "
                "weeks and learn each site with them.",
    "retail": "You shadow a colleague at the till for your first days "
              "before working alone.",
    "restaurant": "You start with a buddy shift and learn the menu and "
                  "the till before your own shifts.",
    "care": "New staff get a named mentor and joint shifts before "
            "taking residents alone.",
    "logistics": "You ride along on routes first; your own routes start "
                 "after the first week.",
    "office": "You get a named colleague for questions and a written "
              "first-week plan.",
    "customer_service": "You listen in on calls first, then take calls "
                        "with a coach beside you.",
    "education": "A colleague shows you the daily routines and you plan "
                 "your first week together.",
    "construction": "You always start paired with a senior worker and "
                    "a safety walkthrough on day one.",
    "tech": "You get a buddy, a small first task and code review support "
            "from week one.",
    "seasonal": "You learn the tools and routes with the team lead "
                "during your first days.",
    "manufacturing": "You train on each machine with an instructor "
                     "before working it alone.",
    "health": "You shadow appointments first and get a named mentor "
              "for your first month.",
    "maintenance": "You do rounds with a senior technician first and "
                   "get your own list after week two.",
}

LEGAL = {"oy", "ab", "ky", "oyj", "tmi", "osakeyhtio", "ry", "r.y."}


_BAR_HIGH = re.compile(
    r"\b(years|senior|expert|extensive|proven|solid|deep)\b", re.I)
_BAR_LOW = re.compile(
    r"\b(some|basic|hobby|interest|willing|familiar|motivation)\b", re.I)
_TOPIC_RX = [
    ("dev", re.compile(
        r"program|backend|frontend|developer|cod|software|python", re.I)),
    ("clean", re.compile(r"clean", re.I)),
    ("service", re.compile(r"customer|till|shop|sales|serv", re.I)),
    ("drive", re.compile(r"driv|licen[cs]e|\bcar\b", re.I)),
    ("child", re.compile(r"child|kids|school", re.I)),
    ("physical", re.compile(r"lift|physical|stand|carry", re.I)),
    ("lang", re.compile(r"finnish|swedish|english", re.I)),
]


def _topic(text: str) -> str:
    """Rough topic bucket so contradictory requirements on the same
    subject can be filtered out."""
    for name, rx in _TOPIC_RX:
        if rx.search(text):
            return name
    return (text.lower().split() or [""])[0]


def _employer_need(eid: str, jobs: list, lang: str) -> dict | None:
    """Build a need card for an employer from their open jobs.
    Deterministic; passes the wording checker."""
    open_jobs = [j for j in jobs
                 if j["employer_id"] == eid and j["status"] == "open"]
    if not open_jobs:
        return None
    first_week, seen = [], set()
    for j in open_jobs:
        for d in (j.get("duties") or []):
            t = d.rstrip(".")
            if t and t not in seen:
                seen.add(t)
                first_week.append(t)
            if len(first_week) >= 5:
                break
        if len(first_week) >= 5:
            break
    first_week = [t[0].upper() + t[1:] for t in first_week[:5]]
    must = []
    bars: dict[str, str] = {}
    for j in open_jobs:
        duty0 = ((j.get("duties") or [""])[0]).rstrip(".")
        why = (f"for work like '{duty0[0].lower() + duty0[1:]}'"
               if duty0 else "needed in the daily work")
        for q in (j.get("qualifications") or []):
            t = q.rstrip(".")
            if not t or t in {m["text"] for m in must}:
                continue
            bar = ("high" if _BAR_HIGH.search(t)
                   else "low" if _BAR_LOW.search(t) else "")
            topic = _topic(t)
            # skip a requirement that contradicts one already kept —
            # e.g. "Some programming experience" vs "Several years of
            # backend work" from a different job ad
            if bar and bars.get(topic) and bars[topic] != bar:
                continue
            if bar:
                bars[topic] = bar
            must.append({"text": t[0].upper() + t[1:], "why": why})
            if len(must) >= 3:
                break
        if len(must) >= 3:
            break
    if not must:
        must = [{"text": "You can work reliably to agreed times",
                 "why": "the team plans shifts around it"}]
    teach = []
    for j in open_jobs:
        onb = (j.get("onboarding") or "").strip()
        if onb and onb not in teach:
            teach.append(onb.rstrip("."))
        if len(teach) >= 2:
            break
    if not teach:
        teach = ["All the tools and routines of this job"]
    langs = []
    for j in open_jobs:
        for l in (j.get("languages") or []):
            name = l.get("language")
            # one level per language; use the job's own task text
            if len(langs) < 2 and name and \
                    name not in {x["name"] for x in langs}:
                langs.append({"name": name,
                              "level": l.get("level") or "A2",
                              "task": l.get("task")
                              or "daily work with customers and the team"})
        if len(langs) >= 2:
            break
    if not langs:
        langs = [{"name": "Finnish", "level": "A2",
                  "task": "daily work with the team"}]
    return {"first_week": first_week, "must_haves": must,
            "will_teach": teach, "languages": langs,
            "job_ids": [j["id"] for j in open_jobs[:3]]}


def _enrich_employers() -> None:
    """Company profile fields for every seeded employer — derived from
    their jobs where possible, deterministic otherwise."""
    import hashlib
    employers = _load("employers.json")
    jobs = _load("jobs.json")
    districts = {d["id"]: d for d in _load("catalog.json")["districts"]}
    for e in employers:
        eid = e["id"]
        ej = [j for j in jobs if j["employer_id"] == eid]
        h = hashlib.sha256(f"emp:{eid}".encode()).hexdigest()
        if ej:
            field = max({j["field"] for j in ej},
                        key=lambda f: sum(1 for j in ej if j["field"] == f))
            dist = max({j["district"] for j in ej},
                       key=lambda d: sum(1 for j in ej if j["district"] == d))
            addr = ej[0].get("address") or ""
        else:
            field = "office"
            dist = ""
            addr = ""
        e["field"] = field
        e["district"] = dist
        e["address"] = addr or (districts.get(dist, {}).get("name", "Espoo")
                                + " (address at booth)")
        e["size_band"] = ["1", "2-9", "10-49", "50-249", "250+"][
            int(h[:2], 16) % 5]
        e["founded"] = 1988 + int(h[2:4], 16) % 34
        e["logo_color"] = PALETTE[int(h[4:6], 16) % len(PALETTE)]
        e["work_languages"] = (
            ["Finnish"] if int(h[6:8], 16) % 3 == 0 else
            (["Finnish", "English"] if int(h[6:8], 16) % 3 == 1
             else ["Finnish", "English", "Swedish"]))
        if not e.get("tagline"):
            e["tagline"] = FIELD_TAGLINE.get(field, "Local employer")
        if not e.get("how_we_welcome"):
            e["how_we_welcome"] = FIELD_WELCOME.get(
                field, "You get a named colleague for your first days.")
        base = (e.get("about") or "").strip()
        # strip a previously generated tail so re-runs stay identical
        for marker in (f" {e['name']} is a ", f" {e['name']} works in "):
            if marker in base:
                base = base[:base.index(marker)]
        size_txt = ("The team has a few people."
                    if e["size_band"] in ("1", "2-9") else
                    "A mid-size local team.")
        extra = (f"{e['name']} works in "
                 f"{FIELD_TAGLINE.get(field, 'local services').lower()}. "
                 f"{size_txt}")
        e["about"] = (base + " " if base else "") + extra
    _dump("employers.json", employers)


def _event_needs() -> None:
    """Need cards for every employer of E2 and E0, from their open jobs.
    E2 employers get an employers list in events.json (they also carry
    booth, so employer_event rows already exist — need_card goes there)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
    from api.rules import lint
    events = _load("events.json")
    jobs = _load("jobs.json")
    for ev in events:
        if ev["id"] == E3:
            for ee in ev["employers"]:
                ee["need_card"] = _employer_need(
                    ee["employer_id"], jobs, "en")
                ee["need_submitted_at"] = "2027-01-20"
                ee["need_by"] = "employer"
        if ev["id"] == E0:
            for ee in ev["employers"]:
                ee["need_card"] = _employer_need(
                    ee["employer_id"], jobs, "fi")
                ee["need_submitted_at"] = "2026-09-28"
                ee["need_by"] = "employer"
    # assert every card passes the wording checker (same shape rules as
    # the API, simplified here)
    for ev in events:
        for ee in ev.get("employers") or []:
            c = ee.get("need_card")
            if not c:
                continue
            texts = list(c.get("first_week") or []) + [
                m.get("text", "") + " " + m.get("why", "")
                for m in c.get("must_haves") or []
            ] + list(c.get("will_teach") or []) + [
                l.get("task", "") for l in c.get("languages") or []]
            assert texts, f"empty need card {ee['employer_id']}"
            assert all(len(t) > 3 for t in texts)
            mhs = c.get("must_haves") or []
            job_like = {
                "title": "", "pay_note": "", "experience_note": "",
                "onboarding": "", "apply_question": "", "lifting": "",
                "duties": c.get("first_week") or [],
                "qualifications":
                    [m.get("text", "") for m in mhs]
                    + [m.get("why", "") for m in mhs]
                    + list(c.get("will_teach") or []),
                "languages": [
                    {"language": l.get("name"), "level": l.get("level"),
                     "task": l.get("task")}
                    for l in c.get("languages") or []],
            }
            issues = lint.blocking_issues(job_like)
            assert not issues, (ee["employer_id"], issues)
    _dump("events.json", events)


def main() -> int:
    users = _load("users.json")
    users = [u for u in users if not u["id"].startswith("u-talent")]
    users += [_talent_user(i, LANG_ORDER[i]) for i in range(40)]
    _dump("users.json", users)

    # registrations: demo residents first, then talent01..40
    # Aino is NOT registered in the upcoming events (spec §9.5) — the
    # demo starts from zero and she goes through the real journey
    regs = [
        {"id": "tr-e1-001", "event_id": E1, "user_id": "u-pekka",
         "time_group": "B", "status": "registered",
         "card_language": "fi", "card": _special_card("u-pekka"),
         "days_ago": 19},
        {"id": "tr-e1-002", "event_id": E1, "user_id": "u-amira",
         "time_group": "C", "status": "registered",
         "card_language": "ar", "card": _special_card("u-amira"),
         "days_ago": 18},
    ]
    groups = "A" * 14 + "B" * 13 + "C" * 13
    for i in range(40):
        lang = LANG_ORDER[i]
        regs.append({
            "id": f"tr-e1-{i + 3:03d}", "event_id": E1,
            "user_id": f"u-talent{i + 1:02d}", "time_group": groups[i],
            "status": "registered", "card_language": lang,
            "card": _card_for(i, lang), "days_ago": 15 - (i % 12)})
    # ~30 registrations for the online event (Aino is not one of them)
    e3_people = (["u-pekka", "u-amira"]
                 + [f"u-talent{i:02d}" for i in range(1, 29)])
    for k, uid in enumerate(e3_people):
        lang = ("fi" if uid == "u-pekka" else
                "ar" if uid == "u-amira" else
                LANG_ORDER[int(uid.rsplit('t', 1)[-1]) - 1])
        regs.append({"id": f"tr-e3-{k + 1:03d}", "event_id": E3,
                     "user_id": uid, "time_group": "A",
                     "status": "registered", "card_language": lang,
                     "card": _special_card(uid) if uid in
                     ("u-pekka", "u-amira") else
                     _card_for(int(uid.rsplit('t', 1)[-1]) - 1, lang),
                     "days_ago": 8 - (k % 6)})
    for k, uid in enumerate(E0_TALENT):
        regs.append({"id": f"tr-e0-{k + 1:03d}", "event_id": E0,
                     "user_id": uid, "time_group": "",
                     "status": "registered", "card_language": "fi",
                     "card": {}, "days_ago": 50})
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
    e3 = dict(E3_EVENT)
    e3["employers"] = [
        {"employer_id": eid, "booth": booth, "slots": slots,
         "formats": ["one_to_one"],
         "need_card": None, "need_submitted_at": None,
         "need_by": None}
        for eid, booth, slots in E3_EMPLOYERS]
    e0 = dict(E0_EVENT)
    e0["employers"] = [{"employer_id": eid, "booth": f"B{i+1}",
                        "slots": 8, "formats": ["walk_in"],
                        "need_card": None, "need_submitted_at": None,
                        "need_by": None}
                       for i, eid in enumerate(E0_EMPLOYERS)]
    _dump("events.json", [e1, e3, e0])

    # interests ~70: reg index -> employer picks (deterministic)
    emp_ids = [e[0] for e in E1_EMPLOYERS]
    plans = [p for p in _load("event_plan.json")
             if p["event_id"] not in (E1, E3)]
    e1_plans = []
    # demo residents are interested in the employers they will talk to
    forced = [("u-pekka", "emp-freight"), ("u-amira", "emp-aurora-care")]
    forced_inv: list = []
    for uid, eid in forced:
        mh = NEED.get(eid, {}).get("must_haves", [])
        e1_plans.append({"user_id": uid, "event_id": E1,
                         "employer_id": eid,
                         "meets": list(range(len(mh))),
                         "language_levels": {l["name"]: l["level"]
                                             for l in NEED.get(eid, {})
                                             .get("languages", [])}})
    for ri, reg in enumerate(
            r for r in regs if r["event_id"] == E1):
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
    # E3 interests: each online registration picks 1–3 employers
    e3_ids = [e[0] for e in E3_EMPLOYERS]
    e3_plans = []
    for ri, reg in enumerate(
            r for r in regs if r["event_id"] == E3):
        uid = reg["user_id"]
        n = 1 + int(_rank(f"e3n{uid}")[:2], 16) % 3
        order = sorted(e3_ids, key=lambda e: _rank(uid + e))
        for eid in order[:n]:
            e3_plans.append({"user_id": uid, "event_id": E3,
                             "employer_id": eid,
                             "meets": [], "language_levels": {}})
    # §9.5: people who chose Sanna's café but are not invited, so her
    # card chooser always has fresh candidates in the demo
    for uid in ("u-talent02", "u-talent04", "u-talent10", "u-talent15"):
        if (uid, "emp-cafe-koivu") not in {(p["user_id"],
                                          p["employer_id"])
                                         for p in e1_plans}:
            e1_plans.append({"user_id": uid, "event_id": E1,
                             "employer_id": "emp-cafe-koivu",
                             "meets": [], "language_levels": {}})
    _dump("event_plan.json", plans + e1_plans + e3_plans)

    # invites ~40: employers invite interested talents; a few outside for
    # mutuals that never become meetings
    interest_pairs = {(p["user_id"], p["employer_id"])
                      for p in e1_plans}
    by_emp: dict[str, list[str]] = {}
    reg_by_user = {r["user_id"]: r["id"] for r in regs
                   if r["event_id"] == E1}
    for p in e1_plans:
        by_emp.setdefault(p["employer_id"], []).append(p["user_id"])
    invites = []
    invited_pairs = {(iv["employer_id"], iv["registration_id"])
                     for iv in invites}
    for eid, *_ in E1_EMPLOYERS:
        cands = sorted(by_emp.get(eid, []), key=lambda u: _rank(eid + u))
        # ~4-5 per card employer, fewer for the missing-card ones
        want = 5 if eid in NEED else 3
        first = [u for u, e in forced + forced_inv if e == eid]
        for uid in first + [u for u in cands if u not in first][:want - len(first)]:
            invites.append({"event_id": E1, "employer_id": eid,
                            "registration_id": reg_by_user[uid],
                            "days_ago": 10})
    # E3: employers invite some of the people who chose them -> the
    # mutual ones get video meetings when seed booking runs
    e3_reg_by_user = {r["user_id"]: r["id"] for r in regs
                      if r["event_id"] == E3}
    e3_interest = {(p["user_id"], p["employer_id"]) for p in e3_plans}
    for eid, *_ in E3_EMPLOYERS:
        cands = sorted(
            (u for u, e in e3_interest if e == eid),
            key=lambda u: _rank("e3" + eid + u))
        for uid in cands[:2]:
            invites.append({"event_id": E3, "employer_id": eid,
                            "registration_id": e3_reg_by_user[uid],
                            "days_ago": 6})
    invites = invites[:40] + [iv for iv in invites[40:] if
                              iv["event_id"] == E3]
    _dump("event_invites.json", invites)

    # talks for a subset of mutual pairs (meeting_id resolved at seed);
    # >=3 talks for the demo residents
    talks = [t for t in _load("event_talks.json")
             if t["event_id"] not in (E1, E0)]
    mutual = [(iv["employer_id"],
               next(r["user_id"] for r in regs
                    if r["id"] == iv["registration_id"]))
              for iv in invites
              if (next(r["user_id"] for r in regs
                       if r["id"] == iv["registration_id"]),
                  iv["employer_id"]) in interest_pairs]
    want_pairs = [("emp-freight", "u-pekka"),
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
    jobs0 = _load("jobs.json")
    for k, (eid, uid, outcome) in enumerate(E0_TALKS):
        fw0 = _employer_need(eid, jobs0, "fi").get("first_week") or []
        talks.append({"id": f"et-e0-{k + 1:03d}", "event_id": E0,
                      "user_id": uid, "employer_id": eid,
                      "observed": fw0[:2],
                      "status": "answered", "outcome": outcome,
                      "employer_note":
                          "Kiitos jutusta — otetaan yhteyttä."
                          if outcome == "next_step" else
                          "Ei tällä kertaa, mutta pidetään yhteys.",
                      "days_ago_talked": 37,
                      "days_ago_answered": 34})
    _dump("event_talks.json", talks)

    # visitor codes for every E1 registration (4-digit, deterministic)
    vis = [v for v in _load("event_visitors.json")
           if v["event_id"] not in (E1, E3)]
    for ev_id in (E1, E3):
        vis += [{"user_id": r["user_id"], "event_id": ev_id,
                 "code": f"{1000 + int(r['id'].rsplit('-', 1)[1]) * 37 % 9000:04d}"}
                for r in regs
                if r["event_id"] == ev_id and r["status"] == "registered"]
    _dump("event_visitors.json", vis)

    # --- people first: passes, badges, connections --------------------
    passes = []
    for r in regs:
        if r["event_id"] in (E1, E3) and r["status"] == "registered":
            passes.append({"token": _pass_token(r["event_id"],
                                              r["user_id"]),
                           "event_id": r["event_id"],
                           "user_id": r["user_id"]})
    for u in _load("users.json"):
        if u["role"] == "employer":
            for ev_obj in (e1, e3):
                if any(e["employer_id"] == u.get("employer_id")
                       for e in ev_obj["employers"]):
                    passes.append({"token": _pass_token(ev_obj["id"],
                                                        u["id"]),
                                   "event_id": ev_obj["id"],
                                   "user_id": u["id"]})
    _dump("event_passes.json", passes)

    badges = []
    for uid in E0_TALENT:
        badges.append({"id": f"bd-e0-att-{uid.split('-')[1]}",
                       "user_id": uid, "employer_id": None,
                       "event_id": E0, "kind": "attended",
                       "label": "attended", "given_by": "system",
                       "created_at": "2026-10-08T15:00:00"})
    for k, (eid, uid, label) in enumerate(E0_KUDOS):
        badges.append({"id": f"bd-e0-k{k + 1:03d}", "user_id": uid,
                       "employer_id": eid, "event_id": E0, "kind": "kudos",
                       "label": label, "given_by": "u-sanna",
                       "created_at": "2026-10-08T16:00:00"})
    badges.append({"id": "bd-e0-h01", "user_id": "u-pekka",
                   "employer_id": "emp-freight", "event_id": E0,
                   "kind": "hired", "label": "hired",
                   "given_by": "u-advisor",
                   "created_at": "2026-10-20T09:00:00"})
    badges.append({"id": "bd-e0-h02", "user_id": "u-talent05",
                   "employer_id": "emp-aurora-care", "event_id": E0,
                   "kind": "hired", "label": "hired",
                   "given_by": "u-advisor",
                   "created_at": "2026-10-22T09:00:00"})
    badges.append({"id": "bd-e0-o01", "user_id": "u-aino",
                   "employer_id": None, "event_id": E0,
                   "kind": "organizer", "label": "pitched",
                   "given_by": "u-advisor",
                   "created_at": "2026-10-08T14:00:00"})
    badges.append({"id": "bd-e0-o02", "user_id": "u-talent12",
                   "employer_id": None, "event_id": E0,
                   "kind": "organizer", "label": "volunteer",
                   "given_by": "u-advisor",
                   "created_at": "2026-10-08T14:00:00"})
    _dump("badges.json", badges)

    conns = [{"user_a": a, "user_b": b, "event_id": E0,
              "created_at": "2026-10-08T14:30:00"}
             for a, b in E0_CONNECTIONS]
    conns += [{"user_a": a, "user_b": b, "event_id": E1,
               "created_at": "2027-03-19T15:00:00"}
              for a, b in E1_CONNECTIONS]
    _dump("connections.json", conns)
    print(f"passes: {len(passes)}, badges: {len(badges)}, "
          f"connections: {len(conns)}")

    # --- §9.7 online event: booth Q&A board + networking lounge ---------
    e3_users = [r["user_id"] for r in regs
                if r["event_id"] == E3 and r["status"] == "registered"]
    cname = {e["id"]: e.get("contact_name") or "The booth team"
             for e in _load("employers.json")}
    QTEXT = [
        ("emp-lumo", "Is this job remote or at the office?",
         "Two days remote, three at the Leppävaara office."),
        ("emp-lumo", "Do I need customer service experience?",
         "No — we teach you. Finnish A2 is enough to start."),
        ("emp-lumo", "What are the usual shift times?", None),
        ("emp-otava", "Can I work only daytime shifts?",
         "Yes, most of our warehouse shifts are 7–15."),
        ("emp-koodikallio", "Is the IT support job English-only?",
         "English works; Finnish is a plus for some customers."),
        ("emp-koodikallio", "Do you provide a laptop for remote days?",
         None),
        ("emp-datavirta", "Is there a mentor for the first weeks?",
         "Every new person pairs with a named buddy for 6 weeks."),
        ("emp-linja", "Can students work just weekends?", None),
        ("emp-laguuni", "Are the shifts fixed or rotating?",
         "Rotating, published three weeks ahead."),
        ("emp-avara", "Is the warehouse work heavy lifting?", None),
    ]
    qs = [{"id": f"eq-{k + 1:03d}", "event_id": E3, "employer_id": eid,
           "user_id": e3_users[k % len(e3_users)], "text": text,
           "answer": ans, "answered_by": cname.get(eid) if ans else None,
           "created_at": f"2027-02-10T11:{10 + k:02d}:00",
           "answered_at": f"2027-02-10T11:{40 + k:02d}:00" if ans else None}
          for k, (eid, text, ans) in enumerate(QTEXT)]
    _dump("event_questions.json", qs)

    lounge = [{"event_id": E3, "user_id": uid,
               "joined_at": "2027-02-10T10:05:00"}
              for uid in e3_users[:10]]
    _dump("lounge_members.json", lounge)
    print(f"questions: {len(qs)}, lounge: {len(lounge)}")

    _enrich_employers()
    _event_needs()

    n_mutual = len(mutual)
    from collections import Counter
    langs = Counter(r["card_language"] for r in regs)
    print(f"events: {[e['id'] for e in _load('events.json')]}")
    print(f"registrations: {len(regs)} by language {dict(langs)}")
    print(f"interests: {len(e1_plans)}+{len(e3_plans)}, "
          f"invites: {len(invites)}, mutual E1: {n_mutual}, "
          f"talks: {len(talk_pairs)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
