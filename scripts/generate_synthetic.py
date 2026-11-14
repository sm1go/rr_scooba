#!/usr/bin/env python3
"""Deterministic synthetic seed for Espoo Work Map (spec section 4).

All data is fictional. Run `python scripts/generate_synthetic.py` to write
db/seed/*.json and db/esco-free catalog inputs; the API rebuilds the SQLite
DB from these files automatically when they change the schema version.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "db" / "seed"
SEED = 20261114

EVENT = {
    "id": "ev-2026-11",
    "name": "Espoo Works — recruitment event",
    "date": "2026-11-26",
    "venue": "Leppävaara service point, Sello, 2nd floor",
    "advisor_note": "Advisors from Employment Espoo are there all day to help "
                    "you talk to employers.",
}

# --- catalog vocabulary -------------------------------------------------------

DISTRICTS = [
    {"id": "leppavaara",   "name": "Leppävaara",    "lat": 60.2198, "lon": 24.8135},
    {"id": "tapiola",      "name": "Tapiola",       "lat": 60.1760, "lon": 24.8050},
    {"id": "otaniemi",     "name": "Otaniemi",      "lat": 60.1860, "lon": 24.8278},
    {"id": "matinkyla",    "name": "Matinkylä",     "lat": 60.1600, "lon": 24.7380},
    {"id": "olari",        "name": "Olari",         "lat": 60.1715, "lon": 24.7450},
    {"id": "niittykumpu",  "name": "Niittykumpu",   "lat": 60.1690, "lon": 24.7730},
    {"id": "espoon_keskus","name": "Espoon keskus", "lat": 60.2055, "lon": 24.6560},
    {"id": "espoonlahti",  "name": "Espoonlahti",   "lat": 60.1490, "lon": 24.6600},
    {"id": "kauklahti",    "name": "Kauklahti",     "lat": 60.1880, "lon": 24.6010},
    {"id": "kalajarvi",    "name": "Kalajärvi",     "lat": 60.2950, "lon": 24.5700},
]
DISTRICT = {d["id"]: d for d in DISTRICTS}

FIELDS = [
    {"id": "cleaning",         "name": "Cleaning"},
    {"id": "retail",           "name": "Retail"},
    {"id": "restaurant",       "name": "Restaurant and café"},
    {"id": "care",             "name": "Care work"},
    {"id": "logistics",        "name": "Logistics and driving"},
    {"id": "office",           "name": "Office work"},
    {"id": "customer_service", "name": "Customer service"},
    {"id": "education",        "name": "Education and library"},
    {"id": "construction",     "name": "Construction"},
    {"id": "tech",             "name": "ICT and specialist"},
    {"id": "seasonal",         "name": "Seasonal work"},
]

CONDITION_KEYS = [
    ("step_free_entrance",      "Step-free entrance"),
    ("lift",                    "Lift"),
    ("accessible_toilet",       "Accessible toilet"),
    ("seated_work",             "Work can be done seated"),
    ("flexible_breaks",         "Breaks when you need them"),
    ("quiet_environment",       "Quiet work environment"),
    ("written_instructions",    "Written instructions available"),
    ("sign_language_ok",        "Sign language is welcome"),
    ("assistive_tech_ok",       "You can use your own assistive technology"),
    ("adjustments_negotiable",  "Adjustments can be agreed together"),
]

CONTRACTS = ["permanent", "fixed_term", "seasonal", "gig", "summer_job",
             "traineeship"]

# --- employers (~28; 12 join the event with a booth) --------------------------

EMPLOYERS = [
    # (id, name, about, contact, booth or None)
    ("emp-cafe-koivu",   "Kahvila Koivu", "A small café next to Tapiola library.",
     "Sanna Lehto", "A1"),
    ("emp-siivouspot",   "SiivouSpoT Oy", "Office cleaning across Espoo.",
     "Mikko Halme", "A2"),
    ("emp-kajo",         "Kajo Siivouspalvelu", "School and daycare cleaning.",
     "Tarja Niemi", None),
    ("emp-market-olari", "K-Market Olari", "Neighbourhood grocery shop.",
     "Minna Voutilainen", "A3"),
    ("emp-kivimaa",      "Kivimäen Kauppa", "Small supermarket in Matinkylä.",
     "Jarmo Lehto", None),
    ("emp-mallas",       "Ravintola Mallas", "Lunch restaurant in Tapiola.",
     "Sirkka Aho", "B1"),
    ("emp-bistro",       "Bistro Niitty", "Café-bistro at Niittykumpu metro.",
     "Olli Rinne", None),
    ("emp-aurora-care",  "Hoivakoti Aurora", "A 40-resident care home in Leppävaara.",
     "Päivi Kettunen", "B2"),
    ("emp-kotisatama",   "Kotisatama Palvelutalo", "Home care and a service house in Espoonlahti.",
     "Eero Pakkanen", None),
    ("emp-freight",      "Nordic Freight Oy", "Warehouse and distribution in Kera.",
     "Timo Rajala", "B3"),
    ("emp-vire",         "Lähettipalvelu Vire", "Parcel delivery from Kilo depot.",
     "Hanna Sallinen", None),
    ("emp-avara",        "Toimistopalvelu Avara", "Office support for small firms.",
     "Leena Koski", "C1"),
    ("emp-kanto",        "Tilitoimisto Kanto", "Bookkeeping office in Espoon keskus.",
     "Vesa Tolonen", None),
    ("emp-linja",        "Asiakaspalvelu Linja", "Phone and chat customer service, Leppävaara.",
     "Riina Palo", "C2"),
    ("emp-koulutus",     "Koulutuskeskus Avara", "Adult courses in Karakallio.",
     "Päivi Kettunen", None),
    ("emp-library",      "Espoo city library", "Iso Omena and Matinkylä libraries.",
     "Sara Lind", "C3"),
    ("emp-tiima",        "Rakennus Tiima Oy", "Renovation sites around Espoo.",
     "Jussi Ranta", "D1"),
    ("emp-oivo",         "Maalaus Oivo", "Painting and small repair work.",
     "Antti Sarlin", None),
    ("emp-lumo",         "Lumo Systems Oy", "Booking software for tradespeople, Otaniemi.",
     "Sanna Virtanen", "D2"),
    ("emp-otava",        "Otava Cloud Oy", "Cloud hosting in Keilaniemi.",
     "Mikael Sund", None),
    ("emp-vihrea",       "Puutarhapalvelu Vihreä", "Parks and garden work for the city.",
     "Outi Niemelä", "D3"),
    ("emp-rantaraitti",  "Rantaraitti kiosks", "Ice-cream kiosks on the waterfront.",
     "Daniel Roth", None),
    ("emp-merituuli",    "Hotelli Merituuli", "Small hotel in Kauklahti.",
     "Emma Salonen", None),
    ("emp-paja",         "Liikuntakeskus Paja", "Community sports centre, Espoon keskus.",
     "Petteri Ahola", None),
    ("emp-apteekki",     "Apteekki Leppävaara", "Pharmacy in Sello shopping centre.",
     "Kirsi Laakso", None),
    ("emp-taikinapuu",   "Leipomo Taikinapuu", "Bakery-café in Olari.",
     "Tuomo Heikkilä", None),
    ("emp-raikas",       "Pesula Raikas", "Laundry service in Niittykumpu.",
     "Anne Mäki", None),
    ("emp-weegee",       "Näyttelykeskus WeeGee", "Exhibition centre in Tapiola.",
     "Leena Koski", None),
]

# --- helpers ------------------------------------------------------------------

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

def sh(day, start, end):
    return {"day": day, "start": start, "end": end}


def job(jid, emp, title, field, district, address, mode, pay, unit, duties,
        shifts, hmin, hmax, contract, experience, onboarding, languages,
        apply_q, confirmed_days, conditions, flexible=0, pay_note="",
        exp_note="", quals=None, lifting=None, cv=0, positions=1):
    d = DISTRICT[district]
    rng = random.Random(jid)  # stable jitter per job
    return {
        "id": jid, "employer_id": emp, "title": title, "field": field,
        "duties": duties, "address": address, "district": district,
        "lat": round(d["lat"] + rng.uniform(-0.006, 0.006), 5),
        "lon": round(d["lon"] + rng.uniform(-0.008, 0.008), 5),
        "work_mode": mode,
        "pay_amount": pay, "pay_unit": unit, "pay_note": pay_note,
        "shifts": shifts, "schedule_flexible": flexible,
        "hours_min": hmin, "hours_max": hmax,
        "contract": contract, "experience": experience,
        "experience_note": exp_note, "qualifications": quals or [],
        "onboarding": onboarding, "languages": languages,
        "lifting": lifting, "apply_question": apply_q,
        "cv_required": cv, "positions": positions,
        "status": "open", "source": "employer",
        "confirmed_days_ago": confirmed_days,
        "conditions": conditions,   # {key: "yes"|"no" or {"value":..,"note":..}}
    }


def lang(language, level, task):
    return {"language": language, "level": level, "task": task}


def make_jobs():
    J = []

    # --- scenario jobs --------------------------------------------------------
    J.append(job(
        "job-cafe-weekend", "emp-cafe-koivu", "Café worker — weekends",
        "restaurant", "tapiola", "Kulttuuriaukio 2", "on_site",
        13.50, "hour",
        ["Serve customers at the counter and the till.",
         "Make coffee and heat lunch dishes.",
         "Keep the counter and tables clean.",
         "Help close the café at the end of the day."],
        [sh("sat", "10:00", "16:00"), sh("sun", "10:00", "16:00")],
        12, 16, "permanent", "none",
        "We train you on the till and the coffee machine during your first "
        "two Saturdays.",
        [lang("Finnish", "A2", "serve customers"), lang("English", "B1", "serve tourists")],
        "Tell me about a time you served people — in a café, shop, school or anywhere.",
        3, {"step_free_entrance": "yes", "accessible_toilet": "yes",
            "seated_work": "no", "flexible_breaks": "yes",
            "written_instructions": "yes"}))

    J.append(job(
        "job-clean-office", "emp-siivouspot", "Office cleaner — two evenings a week",
        "cleaning", "otaniemi", "Tekniikantie 14", "on_site",
        12.80, "hour",
        ["Clean two small offices on Tuesday and Thursday evenings.",
         "Vacuum floors, empty bins, wipe desks and kitchen surfaces.",
         "Follow a written cleaning plan for each site."],
        [sh("tue", "18:00", "21:00"), sh("thu", "18:00", "21:00")],
        6, 6, "permanent", "none",
        "No experience needed — training on site on your first evening.",
        [], "Tell me about a place you have kept clean — at home, at a club, anywhere.",
        5, {"written_instructions": "yes", "adjustments_negotiable": "yes",
            "quiet_environment": "yes"}))

    J.append(job(
        "job-library-shelf", "emp-library", "Library shelver — mornings",
        "education", "matinkyla", "Pyörrekuja 6", "on_site",
        12.50, "hour",
        ["Put returned books and magazines back on the shelves.",
         "Keep the shelves in order and help visitors find things.",
         "Bring books between the two floors with a trolley."],
        [sh("mon", "08:00", "11:00"), sh("wed", "08:00", "11:00")],
        6, 6, "fixed_term", "none",
        "A librarian works beside you the first week.",
        [lang("Finnish", "A2", "answer simple questions from visitors")],
        "What do you like about libraries — or about keeping things in order?",
        2, {"lift": "yes", "seated_work": "yes", "flexible_breaks": "yes",
            "quiet_environment": "yes", "written_instructions": "yes",
            "step_free_entrance": "yes"}))

    J.append(job(
        "job-cs-desk", "emp-linja", "Customer service desk — part-time",
        "customer_service", "leppavaara", "Sello, Länsikäytävä 3", "on_site",
        13.20, "hour",
        ["Help visitors at the service desk: directions, tickets, lockers.",
         "Answer simple questions by phone and chat.",
         "Write down requests you cannot solve and pass them on."],
        [sh("mon", "09:00", "15:00"), sh("wed", "09:00", "15:00"),
         sh("fri", "09:00", "13:00")],
        16, 18, "permanent", "some",
        "Two weeks beside an experienced colleague.",
        [lang("Finnish", "B1", "help customers at the desk"),
         lang("English", "B1", "help international visitors")],
        "Tell me about a time you helped someone solve a problem.",
        20,   # stale — Amira's check_conditions request targets this job
        {"seated_work": {"value": "yes", "note": "Desk work, stool provided."},
         "quiet_environment": "no", "written_instructions": "yes",
         "flexible_breaks": "no"}))

    # --- the rest: hand-written variety across fields and districts -----------
    J.append(job(
        "job-clean-school", "emp-kajo", "School cleaner — afternoons",
        "cleaning", "espoonlahti", "Soukankuja 4", "on_site",
        12.40, "hour",
        ["Clean classrooms and corridors after the school day.",
         "Restock soap and paper in the toilets.",
         "Lock the rooms you have cleaned."],
        [sh(d, "15:00", "19:00") for d in ["mon", "tue", "wed", "thu"]],
        16, 16, "permanent", "none",
        "You walk the route with your team leader for one week.",
        [lang("Finnish", "A2", "read the cleaning plan")],
        "Tell me about work you have done on your own and done well.",
        9, {"written_instructions": "yes", "quiet_environment": "yes",
            "lifting_yes_note": "no"}))

    J.append(job(
        "job-clean-gym", "emp-siivouspot", "Sports centre cleaner — early mornings",
        "cleaning", "espoon_keskus", "Kilpikuja 1", "on_site",
        13.00, "hour",
        ["Clean the gym floor, changing rooms and sauna.",
         "Use a floor scrubber — we show you how.",
         "Work starts before the centre opens."],
        [sh(d, "05:30", "09:30") for d in ["mon", "wed", "fri"]],
        12, 12, "permanent", "none", "Training on the machines included.",
        [lang("Finnish", "A2", "understand the supervisor's instructions")],
        "Are you a morning person? Tell me about your mornings.",
        12, {"seated_work": "no", "written_instructions": "yes"},
        lifting="Up to 10 kg, a few times per shift"))

    J.append(job(
        "job-clean-flex", "emp-kajo", "Cleaner — choose your days",
        "cleaning", "kauklahti", "Kauklahdentie 8", "on_site",
        12.60, "hour",
        ["Clean a small office building — you pick which days.",
         "Vacuuming, bins, kitchen and meeting rooms."],
        [], 8, 20, "permanent", "none",
        "First week together, then you work independently.",
        [], "Which days and times would suit you best?",
        7, {"flexible_breaks": "yes", "written_instructions": "yes",
            "adjustments_negotiable": "yes"}, flexible=1))

    J.append(job(
        "job-market-shelf", "emp-market-olari", "Shelf stocker — evenings",
        "retail", "olari", "Olarinluoma 8", "on_site",
        12.90, "hour",
        ["Fill the shelves and keep the shop tidy.",
         "Check dates on milk and bread.",
         "Help close the shop at 21:00."],
        [sh(d, "17:00", "21:00") for d in ["mon", "tue", "thu"]],
        12, 12, "permanent", "none",
        "You shadow a colleague for three shifts.",
        [lang("Finnish", "A2", "answer simple customer questions")],
        "Tell me about a time you noticed something that needed doing — and did it.",
        4, {"written_instructions": "yes", "seated_work": "no"},
        lifting="Crates up to 12 kg"))

    J.append(job(
        "job-market-till", "emp-kivimaa", "Checkout assistant — weekends",
        "retail", "matinkyla", "Merituulentie 20", "on_site",
        12.70, "hour",
        ["Work the till on Saturday and Sunday.",
         "Bag groceries and help customers pack.",
         "Keep the checkout area tidy."],
        [sh("sat", "09:00", "17:00"), sh("sun", "12:00", "18:00")],
        14, 14, "summer_job", "none",
        "Till training on your first weekend.",
        [lang("Finnish", "B1", "serve customers at the till")],
        "What would you do if a queue got long and someone was upset?",
        1, {"seated_work": "yes", "written_instructions": "yes"},
        positions=2))

    J.append(job(
        "job-mallas-kitchen", "emp-mallas", "Kitchen helper — lunch hours",
        "restaurant", "tapiola", "Ahertajantie 5", "on_site",
        13.00, "hour",
        ["Wash dishes and keep the kitchen clean during lunch.",
         "Prepare salads and cold plates.",
         "Help put away deliveries."],
        [sh(d, "10:00", "15:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        20, 25, "permanent", "none",
        "Hygiene passport not needed — we arrange the test.",
        [lang("Finnish", "A2", "understand the kitchen team")],
        "Tell me about a busy place you have worked in.",
        6, {"seated_work": "no", "written_instructions": "yes",
            "flexible_breaks": "yes"},
        lifting="Pots and trays up to 8 kg"))

    J.append(job(
        "job-bistro", "emp-bistro", "Café assistant — mornings",
        "restaurant", "niittykumpu", "Niittykummuntie 9", "on_site",
        13.20, "hour",
        ["Open the café, bake the morning buns (from frozen).",
         "Serve at the counter and the till.",
         "Keep tables clear and the coffee pots full."],
        [sh(d, "06:30", "12:00") for d in ["mon", "tue", "fri"]],
        15, 16, "permanent", "some",
        "You open the café with a colleague for two weeks.",
        [lang("Finnish", "B1", "serve customers"), lang("English", "B1", "serve tourists")],
        "What makes a café visit feel welcoming to you?",
        11, {"seated_work": "no", "written_instructions": "yes",
             "step_free_entrance": "yes", "accessible_toilet": "no"}))

    J.append(job(
        "job-aurora-evening", "emp-aurora-care", "Care assistant — evening shifts",
        "care", "leppavaara", "Vallikalliontie 3", "on_site",
        15.20, "hour",
        ["Help residents with the evening routine: meals, washing, getting ready for bed.",
         "Sit and talk — unhurried time is part of the job.",
         "Write two lines per resident in the care notes."],
        [sh("tue", "15:00", "21:00"), sh("thu", "15:00", "21:00"),
         sh("sat", "15:00", "21:00")],
        18, 18, "permanent", "some",
        "You work beside a mentor for your first month.",
        [lang("Finnish", "B1", "talk with residents and write care notes")],
        "Tell me about someone you have cared for or helped regularly.",
        3, {"seated_work": "yes", "flexible_breaks": "no",
            "written_instructions": "yes", "step_free_entrance": "yes",
            "accessible_toilet": "yes", "lift": "yes"},
        lifting="Helping a resident stand — up to 20 kg with support"))

    J.append(job(
        "job-kotisatama", "emp-kotisatama", "Home care assistant — day shifts",
        "care", "espoonlahti", "Soukkatie 12", "on_site",
        15.00, "hour",
        ["Visit 4–6 clients a day in their homes.",
         "Help with meals, medicine reminders and light tidying.",
         "Travel between clients by car — licence needed."],
        [sh(d, "08:00", "16:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        30, 38, "permanent", "some",
        "First weeks you visit clients together with a colleague.",
        [lang("Finnish", "B1", "talk with clients and document visits")],
        "Tell me about a time you earned someone's trust.",
        11, {"written_instructions": "yes", "adjustments_negotiable": "yes"},
        quals=["Driving licence B"], lifting="Helping clients move — varies"))

    J.append(job(
        "job-freight-pick", "emp-freight", "Warehouse picker — morning shift",
        "logistics", "espoon_keskus", "Keran Hallit 2", "on_site",
        13.80, "hour",
        ["Pick orders with a handheld scanner.",
         "Pack and label parcels for the afternoon routes.",
         "Keep your own area tidy."],
        [sh(d, "06:00", "14:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        30, 38, "permanent", "none",
        "Two days of training with a buddy.",
        [lang("English", "A2", "read pick lists and safety signs")],
        "Tell me about physical or fast-paced work you have done.",
        8, {"written_instructions": "yes", "seated_work": "no",
            "quiet_environment": "no"},
        lifting="Parcels up to 20 kg; a pump truck helps"))

    J.append(job(
        "job-freight-evening", "emp-freight", "Package sorter — evenings",
        "logistics", "espoon_keskus", "Keran Hallit 2", "on_site",
        13.50, "hour",
        ["Sort parcels onto the right cages for morning routes.",
         "Scan each parcel as you place it.",
         "One shift is four hours — evenings only."],
        [sh(d, "17:00", "21:00") for d in ["mon", "wed", "fri"]],
        12, 12, "gig", "none", "Thirty minutes of training on your first evening.",
        [], "Can you keep a steady pace for four hours? Tell me how.",
        10, {"written_instructions": "yes", "quiet_environment": "no"},
        lifting="Parcels up to 15 kg"))

    J.append(job(
        "job-vire-driver", "emp-vire", "Delivery driver — parcels",
        "logistics", "niittykumpu", "Kilonportti 3", "on_site",
        15.50, "hour",
        ["Drive a van on a planned route in Espoo.",
         "Deliver parcels to doors and pick-up points.",
         "Scan every parcel and get a signature or photo."],
        [sh(d, "09:00", "17:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        30, 40, "permanent", "some",
        "You ride along for a week before driving alone.",
        [lang("Finnish", "A2", "talk to customers at the door")],
        "Tell me about your driving — what have you driven and where?",
        13, {"seated_work": "yes", "flexible_breaks": "yes",
             "written_instructions": "yes"},
        quals=["Driving licence B"], lifting="Parcels up to 15 kg"))

    J.append(job(
        "job-avara-reception", "emp-avara", "Reception assistant — part-time",
        "office", "leppavaara", "Vallikatu 7", "on_site",
        14.00, "hour",
        ["Answer the phone and welcome visitors at a small office.",
         "Book meeting rooms and handle the post.",
         "Keep the front desk and kitchen tidy."],
        [sh("mon", "08:00", "16:00"), sh("wed", "08:00", "16:00")],
        16, 16, "permanent", "some",
        "You learn the desk beside our receptionist for two weeks.",
        [lang("Finnish", "B1", "answer calls and greet visitors"),
         lang("English", "B1", "welcome international guests")],
        "Tell me about a time you were the friendly face of a place.",
        22, {"seated_work": "yes", "lift": "yes", "accessible_toilet": "yes",
             "step_free_entrance": "yes", "written_instructions": "yes",
             "quiet_environment": "no"}))

    J.append(job(
        "job-kanto", "emp-kanto", "Office assistant — bookkeeping",
        "office", "espoon_keskus", "Kanslerintie 2", "hybrid",
        14.50, "hour",
        ["Scan and file receipts and invoices.",
         "Enter numbers into our bookkeeping system — we teach it.",
         "Two days at the office, the rest from home if you like."],
        [], 12, 20, "fixed_term", "none",
        "One week of hands-on training.",
        [lang("Finnish", "B1", "read invoices and talk with the team")],
        "Tell me about careful, detailed work you have done.",
        6, {"seated_work": "yes", "quiet_environment": "yes",
             "written_instructions": "yes", "assistive_tech_ok": "yes",
             "flexible_breaks": "yes"}, flexible=1))

    J.append(job(
        "job-koulutus-assist", "emp-koulutus", "Course assistant — evenings",
        "education", "kauklahti", "Lansirinteenkatu 1", "on_site",
        13.80, "hour",
        ["Set up the classroom before evening courses.",
         "Help learners log in and find their materials.",
         "Make coffee and tidy up after the course."],
        [sh("tue", "16:30", "20:30"), sh("thu", "16:30", "20:30")],
        8, 8, "fixed_term", "none",
        "The teacher shows you the routine on your first evening.",
        [lang("Finnish", "B1", "help learners in Finnish")],
        "Tell me about a time you helped someone learn something.",
        4, {"step_free_entrance": "yes", "lift": "yes",
            "accessible_toilet": "yes", "seated_work": "yes",
            "written_instructions": "yes", "quiet_environment": "no"}))

    J.append(job(
        "job-tiima-helper", "emp-tiima", "Site assistant — renovation",
        "construction", "olari", "Satulakatu 4", "on_site",
        14.20, "hour",
        ["Carry materials and keep the site tidy.",
         "Help carpenters — hold, fetch, measure.",
         "Learn the site safety rules on day one."],
        [sh(d, "07:00", "15:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        30, 40, "fixed_term", "none",
        "Safety card arranged by us; you work with an experienced pair.",
        [lang("Finnish", "A2", "understand safety briefings"),
         lang("English", "A2", "work with the crew")],
        "Tell me about practical, hands-on work you have done.",
        6, {"written_instructions": "yes", "seated_work": "no",
            "quiet_environment": "no"},
        lifting="Materials up to 20 kg", positions=3))

    J.append(job(
        "job-oivo", "emp-oivo", "Painter's assistant",
        "construction", "matinkyla", "Piispanmaenkatu 2", "on_site",
        13.60, "hour",
        ["Cover floors and tape edges before painting.",
         "Sand and clean surfaces.",
         "Wash brushes and tidy the site."],
        [sh(d, "07:30", "15:30") for d in ["mon", "tue", "wed", "thu"]],
        24, 32, "gig", "none",
        "You work beside a painter the whole time.",
        [], "What home or renovation projects have you helped with?",
        25, {"written_instructions": "no", "quiet_environment": "no",
             "seated_work": "no"}, lifting="Ladders and paint cans up to 10 kg"))

    J.append(job(
        "job-lumo-junior", "emp-lumo", "Junior developer — booking platform",
        "tech", "otaniemi", "Innopoli 2, Tekniikantie 14", "hybrid",
        2600, "month",
        ["Fix bugs and build small features in our Python backend.",
         "Write tests for the code you touch.",
         "Review code with a senior developer every week."],
        [], 30, 38, "permanent", "some",
        "A named mentor for your first three months.",
        [lang("English", "B2", "work in our English-speaking team")],
        "Show us something you built — a project, a course work, anything — and explain one choice you made.",
        2, {"seated_work": "yes", "quiet_environment": "yes",
            "assistive_tech_ok": "yes", "flexible_breaks": "yes",
            "written_instructions": "yes", "adjustments_negotiable": "yes"},
        quals=["Some programming experience — a course, a hobby project or work"],
        cv=1, flexible=1))

    J.append(job(
        "job-otava-support", "emp-otava", "Service desk agent — hybrid",
        "tech", "otaniemi", "Keilaranta 9", "hybrid",
        15.80, "hour",
        ["Answer customer tickets about our hosting service.",
         "Escalate what you cannot fix to the engineers.",
         "Keep the help centre pages up to date."],
        [], 20, 30, "permanent", "some",
        "Product training for two weeks; a buddy after that.",
        [lang("Finnish", "B1", "answer Finnish tickets"),
         lang("English", "B2", "answer English tickets")],
        "Tell me about a time you explained something technical in simple words.",
        9, {"seated_work": "yes", "quiet_environment": "yes",
            "written_instructions": "yes", "assistive_tech_ok": "yes",
            "step_free_entrance": "yes", "lift": "yes"},
        flexible=1))

    J.append(job(
        "job-vihrea-park", "emp-vihrea", "Park worker — summer",
        "seasonal", "tapiola", "Rantaraitti, meeting at Tapiola depot", "on_site",
        12.20, "hour",
        ["Keep the waterfront parks tidy: litter, paths, flower beds.",
         "Water plants and sweep walkways.",
         "Work outdoors in a small team."],
        [sh(d, "08:00", "16:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        30, 38, "summer_job", "none",
        "All tools and training provided.",
        [lang("Finnish", "A2", "understand the day's tasks")],
        "Tell me about outdoor or physical work you enjoy.",
        3, {"written_instructions": "yes", "seated_work": "no"},
        lifting="Tools and bags up to 15 kg", positions=6))

    J.append(job(
        "job-rantaraitti", "emp-rantaraitti", "Ice-cream kiosk seller",
        "seasonal", "espoonlahti", "Soukanranta kiosk 2", "on_site",
        11.80, "hour",
        ["Sell ice cream, cold drinks and coffee by the sea.",
         "Handle cash and card payments.",
         "Keep the kiosk clean and restock from the freezer."],
        [sh("fri", "12:00", "19:00"), sh("sat", "11:00", "19:00"),
         sh("sun", "11:00", "18:00")],
        15, 22, "seasonal", "none",
        "Two shifts beside an experienced seller.",
        [lang("Finnish", "A2", "serve customers"), lang("English", "A2", "serve tourists")],
        "This job is outdoors, alone, and busy on hot days — how does that sound to you?",
        12, {"written_instructions": "yes", "flexible_breaks": "no"},
        positions=4))

    J.append(job(
        "job-merituuli", "emp-merituuli", "Breakfast host — mornings",
        "restaurant", "kauklahti", "Kauppatie 1", "on_site",
        13.60, "hour",
        ["Lay out and refill the breakfast buffet.",
         "Clear tables and greet guests.",
         "Help the kitchen with simple prep."],
        [sh(d, "06:00", "12:00") for d in ["fri", "sat", "sun"]],
        18, 18, "permanent", "none",
        "You work the breakfast service with a colleague first.",
        [lang("Finnish", "A2", "greet guests"), lang("English", "B1", "help international guests")],
        "Tell me about a morning job or routine you have kept.",
        7, {"step_free_entrance": "yes", "lift": "yes",
            "accessible_toilet": "yes", "written_instructions": "yes"},
        lifting="Trays and chafing dishes up to 8 kg"))

    J.append(job(
        "job-paja-desk", "emp-paja", "Sports centre desk — evenings",
        "customer_service", "espoon_keskus", "Kilpikuja 1", "on_site",
        13.00, "hour",
        ["Welcome visitors, sell single entries and lockers.",
         "Book badminton courts by phone and at the desk.",
         "Check the gym floor once per shift."],
        [sh("mon", "16:00", "21:30"), sh("wed", "16:00", "21:30"),
         sh("sun", "12:00", "18:00")],
        16, 18, "permanent", "none",
        "Two weeks beside the day-shift host.",
        [lang("Finnish", "B1", "serve visitors at the desk")],
        "Tell me about a place where you make people feel welcome.",
        5, {"seated_work": "yes", "step_free_entrance": "yes", "lift": "yes",
            "written_instructions": "yes", "quiet_environment": "no"}))

    J.append(job(
        "job-apteekki", "emp-apteekki", "Pharmacy shop assistant",
        "retail", "leppavaara", "Sello, 1st floor", "on_site",
        14.20, "hour",
        ["Help customers find products on the shelves.",
         "Restock and keep displays tidy.",
         "Work the till — the pharmacist handles all prescriptions."],
        [sh(d, "12:00", "20:00") for d in ["tue", "thu"]],
        16, 16, "permanent", "some",
        "Product training included; always a pharmacist on shift.",
        [lang("Finnish", "B1", "help customers find the right product")],
        "Tell me about careful work where mistakes matter.",
        12, {"seated_work": "yes", "step_free_entrance": "yes", "lift": "yes",
             "accessible_toilet": "yes", "written_instructions": "yes",
             "quiet_environment": "no"}))

    J.append(job(
        "job-taikinapuu", "emp-taikinapuu", "Bakery assistant — early shifts",
        "restaurant", "olari", "Olarinlaitos 4", "on_site",
        13.40, "hour",
        ["Pack bread and pastries for the counter.",
         "Serve customers from 07:00.",
         "Simple baking tasks after training."],
        [sh(d, "05:30", "13:00") for d in ["sat", "sun"]],
        15, 15, "permanent", "none",
        "The baker teaches you the packing list first.",
        [lang("Finnish", "A2", "serve customers")],
        "Early mornings are the heart of this job — tell me how they suit you.",
        9, {"seated_work": "no", "written_instructions": "yes"},
        lifting="Crates up to 10 kg"))

    J.append(job(
        "job-raikas", "emp-raikas", "Laundry worker — daytime",
        "seasonal", "niittykumpu", "Niittysillankuja 3", "on_site",
        12.30, "hour",
        ["Sort, wash, dry and fold laundry for hotels.",
         "Load and unload the machines.",
         "Pack clean linen for delivery."],
        [sh(d, "09:00", "15:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        25, 30, "fixed_term", "none",
        "One week of training.",
        [lang("Finnish", "A2", "understand the work instructions")],
        "Tell me about steady, hands-on work you have kept up.",
        14, {"seated_work": "yes", "written_instructions": "yes",
             "quiet_environment": "no"},
        lifting="Laundry bags up to 12 kg"))

    J.append(job(
        "job-weegee", "emp-weegee", "Gallery assistant — weekends",
        "education", "tapiola", "Ahertajantie 5", "on_site",
        13.10, "hour",
        ["Welcome visitors and check tickets.",
         "Watch the exhibition rooms and answer questions.",
         "Help with small events once a month."],
        [sh("sat", "10:00", "17:00"), sh("sun", "10:00", "17:00")],
        14, 14, "permanent", "none",
        "You learn each exhibition beside a guide.",
        [lang("Finnish", "B1", "talk with visitors"),
         lang("English", "B1", "help international visitors")],
        "Tell me about an exhibition or museum you enjoyed — or about helping visitors anywhere.",
        2, {"step_free_entrance": "yes", "lift": "yes",
            "accessible_toilet": "yes", "seated_work": "yes",
            "quiet_environment": "yes", "written_instructions": "yes",
            "sign_language_ok": "yes"}))

    # --- additional jobs to reach 60 with deliberate variety ------------------
    J.append(job(
        "job-clean-daycare", "emp-kajo", "Daycare cleaner — mornings",
        "cleaning", "kalajarvi", "Kalajärventie 11", "on_site",
        12.40, "hour",
        ["Clean a small daycare: playroom, kitchen, nap room.",
         "Work finishes before the children arrive at 12:00.",
         "Wash toys once a week."],
        [sh(d, "06:00", "12:00") for d in ["mon", "tue", "thu"]],
        18, 18, "permanent", "none",
        "One week with the current cleaner.",
        [lang("Finnish", "A2", "read the cleaning plan")],
        "Tell me about keeping a place clean for other people.",
        21, {"written_instructions": "yes", "quiet_environment": "yes"},
        lifting="Buckets and machines up to 10 kg"))

    J.append(job(
        "job-market-evening-till", "emp-market-olari", "Evening till and closing help",
        "retail", "olari", "Olarinluoma 8", "on_site",
        12.80, "hour",
        ["Work the till during the evening rush.",
         "Help close the shop: count the till, tidy the front.",
         "Answer simple customer questions."],
        [sh(d, "16:00", "21:00") for d in ["wed", "fri", "sat"]],
        15, 15, "permanent", "none",
        "Two evenings beside our head cashier.",
        [lang("Finnish", "B1", "serve customers at the till")],
        "Tell me about a job where you handled money or responsibility.",
        6, {"seated_work": "yes", "written_instructions": "yes",
            "step_free_entrance": "yes"}))

    J.append(job(
        "job-kivimaa-morning", "emp-kivimaa", "Morning shelf filler",
        "retail", "matinkyla", "Merituulentie 20", "on_site",
        12.60, "hour",
        ["Fill fruit and vegetable shelves before opening.",
         "Check freshness and remove bad items.",
         "Work 06:00–10:00, three mornings a week."],
        [sh("mon", "06:00", "10:00"), sh("wed", "06:00", "10:00"),
         sh("fri", "06:00", "10:00")],
        12, 12, "permanent", "none",
        "The produce manager shows you the routine.",
        [lang("Finnish", "A2", "understand the morning list")],
        "Tell me about early-morning work you have done.",
        8, {"written_instructions": "yes", "seated_work": "no"},
        lifting="Crates up to 12 kg"))

    J.append(job(
        "job-aurora-weekend", "emp-aurora-care", "Weekend companion — care home",
        "care", "leppavaara", "Vallikalliontie 3", "on_site",
        15.00, "hour",
        ["Spend time with residents: walks, games, coffee.",
         "Help serve the weekend lunch.",
         "Note anything important for the nurses."],
        [sh("sat", "10:00", "16:00"), sh("sun", "10:00", "14:00")],
        10, 10, "permanent", "none",
        "You shadow a care assistant for two weekends.",
        [lang("Finnish", "B1", "talk with residents")],
        "Tell me about time you have spent with an older person.",
        4, {"step_free_entrance": "yes", "lift": "yes",
            "accessible_toilet": "yes", "seated_work": "yes",
            "written_instructions": "yes", "quiet_environment": "yes"}))

    J.append(job(
        "job-freight-forklift", "emp-freight", "Forklift operator — night",
        "logistics", "espoon_keskus", "Keran Hallit 2", "on_site",
        16.20, "hour",
        ["Move pallets with a reach truck.",
         "Load the morning delivery vans.",
         "Night shift Sunday to Thursday."],
        [sh(d, "22:00", "06:00") for d in ["sun", "mon", "tue", "wed"]],
        32, 32, "permanent", "required",
        "Night premium paid. Forklift card required — we can help renew it.",
        [lang("English", "A2", "read the load lists")],
        "Tell me about your forklift or machine experience.",
        9, {"written_instructions": "yes", "quiet_environment": "no"},
        quals=["Forklift licence"], lifting="None — machines do the lifting",
        positions=2))

    J.append(job(
        "job-avara-scan", "emp-avara", "Document scanner — flexible hours",
        "office", "leppavaara", "Vallikatu 7", "on_site",
        13.00, "hour",
        ["Scan old paper files into our archive.",
         "Name and file the scans so others can find them.",
         "Choose your own hours between 08:00 and 18:00."],
        [], 6, 15, "fixed_term", "none",
        "Half a day of training; headphones welcome while you work.",
        [lang("Finnish", "A2", "name files so others find them")],
        "Tell me about quiet, repetitive work you have kept up.",
        3, {"seated_work": "yes", "quiet_environment": "yes",
            "written_instructions": "yes", "flexible_breaks": "yes",
            "assistive_tech_ok": "yes", "step_free_entrance": "yes",
            "lift": "yes"}, flexible=1))

    J.append(job(
        "job-linja-chat", "emp-linja", "Chat agent — remote",
        "customer_service", "leppavaara", "Remote — office in Leppävaara for training",
        "remote", 13.60, "hour",
        ["Answer customer chats from home.",
         "Use our ready-made answers and write your own in plain language.",
         "One day a week at the office, the rest remote."],
        [], 12, 20, "permanent", "none",
        "Two weeks at the office, then remote with daily check-ins.",
        [lang("Finnish", "B1", "write chat answers"),
         lang("English", "B1", "write chat answers")],
        "Tell me about writing or typing you have done — messages, letters, anything.",
        7, {"seated_work": "yes", "quiet_environment": "yes",
            "assistive_tech_ok": "yes", "flexible_breaks": "yes"},
        flexible=1))

    J.append(job(
        "job-koulutus-remote", "emp-koulutus", "Online course host — evenings",
        "education", "kauklahti", "Remote — courses run online", "remote",
        15.00, "hour",
        ["Open the online classroom and welcome learners.",
         "Help with microphones, cameras and links.",
         "Take notes for the teacher."],
        [sh("wed", "17:00", "20:30")],
        4, 4, "fixed_term", "none",
        "You host one course beside our staff first.",
        [lang("Finnish", "B1", "help learners online")],
        "Tell me about helping people with computers or phones.",
        10, {"seated_work": "yes", "quiet_environment": "yes",
             "assistive_tech_ok": "yes", "written_instructions": "yes"},
        flexible=1))

    J.append(job(
        "job-tiima-finisher", "emp-tiima", "Finishing carpenter",
        "construction", "leppavaara", "Vallikatu 5 site office", "on_site",
        18.50, "hour",
        ["Fit doors, skirting and kitchens on a renovation site.",
         "Work from drawings with the site lead.",
         "Keep your tools and the site safe."],
        [sh(d, "07:00", "15:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        38, 40, "permanent", "required",
        "Experienced role — you get your own rooms to finish.",
        [lang("Finnish", "A2", "follow the site briefing")],
        "Walk me through the last thing you built or fitted.",
        7, {"written_instructions": "yes", "quiet_environment": "no",
             "seated_work": "no"},
        quals=["Carpentry experience or vocational training"],
        lifting="Timber and doors up to 20 kg"))

    J.append(job(
        "job-lumo-senior", "emp-lumo", "Backend developer — payments",
        "tech", "otaniemi", "Innopoli 2, Tekniikantie 14", "hybrid",
        4500, "month",
        ["Build and own the payments part of our platform.",
         "Work with the designer on what to build next.",
         "Keep the payment service fast and tested."],
        [], 38, 40, "permanent", "required",
        "You pair with the current owner of the service for a month.",
        [lang("English", "C1", "write specs and review code")],
        "Describe a service you built — what it does, what broke, what you learned.",
        5, {"seated_work": "yes", "quiet_environment": "yes",
            "assistive_tech_ok": "yes", "flexible_breaks": "yes"},
        quals=["Several years of backend work"], cv=1, flexible=1))

    J.append(job(
        "job-otava-junior", "emp-otava", "Support engineer — first job welcome",
        "tech", "otaniemi", "Keilaranta 9", "hybrid",
        2300, "month",
        ["Help customers set up their websites on our platform.",
         "Learn our tools beside the support team.",
         "Write short how-to answers we can reuse."],
        [], 30, 38, "permanent", "none",
        "A buddy for three months; you never answer alone at first.",
        [lang("English", "B1", "answer customer emails")],
        "Tell me about something technical you learned recently and how.",
        8, {"seated_work": "yes", "quiet_environment": "yes",
            "written_instructions": "yes", "assistive_tech_ok": "yes",
            "step_free_entrance": "yes", "lift": "yes"},
        flexible=1))

    J.append(job(
        "job-vihrea-winter", "emp-vihrea", "Winter path work — as needed",
        "seasonal", "kalajarvi", "Depot at Kalajärventie 2", "on_site",
        13.20, "hour",
        ["Grit and clear walking paths on icy mornings.",
         "Work is called the evening before when frost is forecast.",
         "Early starts, short shifts."],
        [], 0, 15, "seasonal", "none",
        "One morning with the team leader.",
        [lang("Finnish", "A2", "understand the morning message")],
        "Can you start early on short notice? Tell me how that would work for you.",
        24, {"written_instructions": "yes", "seated_work": "no"},
        flexible=1, lifting="Grit bags up to 15 kg"))

    J.append(job(
        "job-merituuli-night", "emp-merituuli", "Night porter — weekends",
        "customer_service", "kauklahti", "Kauppatie 1", "on_site",
        14.80, "hour",
        ["Watch the small hotel at night.",
         "Check in late guests and help with small requests.",
         "Start the coffee for breakfast."],
        [sh("fri", "22:00", "07:00"), sh("sat", "22:00", "07:00")],
        18, 18, "permanent", "some",
        "Two weekends beside the regular porter.",
        [lang("Finnish", "A2", "help guests"), lang("English", "B1", "help guests")],
        "Tell me how you handle quiet, responsible work at night.",
        12, {"seated_work": "yes", "written_instructions": "yes",
             "step_free_entrance": "yes", "lift": "yes"}))

    J.append(job(
        "job-paja-instructor", "emp-paja", "Gym floor instructor",
        "customer_service", "espoon_keskus", "Kilpikuja 1", "on_site",
        14.60, "hour",
        ["Show visitors how to use the gym machines safely.",
         "Keep the gym floor tidy and safe.",
         "Run one beginners' session a week."],
        [sh("tue", "15:00", "21:00"), sh("sat", "09:00", "15:00")],
        12, 12, "permanent", "some",
        "You shadow our instructor for a month.",
        [lang("Finnish", "B1", "explain the machines to visitors")],
        "Tell me about sport or exercise you know well.",
        14, {"seated_work": "no", "step_free_entrance": "yes", "lift": "yes",
             "written_instructions": "yes", "quiet_environment": "no"}))

    J.append(job(
        "job-raikas-driver", "emp-raikas", "Laundry delivery driver",
        "logistics", "niittykumpu", "Niittysillankuja 3", "on_site",
        14.80, "hour",
        ["Deliver clean linen to hotels and care homes.",
         "Pick up the dirty laundry on the same route.",
         "Load with a trolley — the van has a lift."],
        [sh(d, "08:00", "14:00") for d in ["mon", "wed", "fri"]],
        18, 18, "permanent", "some",
        "You ride the route once with our driver.",
        [lang("Finnish", "A2", "talk to the receiving staff")],
        "Tell me about your driving.",
        6, {"seated_work": "yes", "written_instructions": "yes"},
        quals=["Driving licence B"], lifting="Trolleys up to 15 kg"))

    J.append(job(
        "job-market-deli", "emp-market-olari", "Deli counter help — afternoons",
        "retail", "olari", "Olarinluoma 8", "on_site",
        13.10, "hour",
        ["Slice and pack cold cuts and cheese.",
         "Serve customers at the counter.",
         "Keep the display full and clean."],
        [sh(d, "14:00", "20:00") for d in ["wed", "thu", "fri"]],
        18, 18, "permanent", "none",
        "A week beside the deli lead; hygiene passport arranged.",
        [lang("Finnish", "B1", "serve customers at the counter")],
        "Tell me about food work or counter service you have done.",
        5, {"seated_work": "no", "written_instructions": "yes",
            "step_free_entrance": "yes"}))

    J.append(job(
        "job-avara-post", "emp-avara", "Mail room assistant — mornings",
        "office", "leppavaara", "Vallikatu 7", "on_site",
        13.20, "hour",
        ["Sort the morning post for three floors.",
         "Deliver parcels inside the building with a trolley.",
         "Prepare outgoing post before 14:00."],
        [sh(d, "08:00", "14:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        30, 30, "permanent", "none",
        "You walk the route with the current assistant for a week.",
        [lang("Finnish", "A2", "read names and room numbers")],
        "Tell me about work where being on time matters.",
        26, {"seated_work": "no", "lift": "yes",
             "step_free_entrance": "yes", "written_instructions": "yes",
             "quiet_environment": "yes"},
        lifting="Parcels up to 10 kg"))

    J.append(job(
        "job-kanto-remote", "emp-kanto", "Data entry — remote",
        "office", "espoon_keskus", "Remote — Espoon keskus office for training", "remote",
        13.50, "hour",
        ["Enter receipt data into our bookkeeping system.",
         "Flag anything you cannot read for the accountant.",
         "Work from home at your own hours."],
        [], 8, 16, "gig", "none",
        "One training day at the office, then remote.",
        [lang("Finnish", "B1", "read receipts and invoices")],
        "Tell me about careful computer work you have done.",
        5, {"seated_work": "yes", "quiet_environment": "yes",
             "assistive_tech_ok": "yes", "flexible_breaks": "yes"},
        flexible=1))

    J.append(job(
        "job-linja-phone", "emp-linja", "Phone agent — Finnish line",
        "customer_service", "leppavaara", "Länsikäytävä 3, Sello", "hybrid",
        14.00, "hour",
        ["Answer the Finnish customer line.",
         "Use written scripts you can adapt in your own words.",
         "Two days on site, three from home."],
        [sh(d, "09:00", "17:00") for d in ["mon", "tue", "wed", "thu"]],
        32, 32, "permanent", "some",
        "Two weeks of call-listening before your first call.",
        [lang("Finnish", "B2", "answer the customer line"),
         lang("English", "B1", "switch calls when needed")],
        "Tell me about talking to strangers — where have you done it?",
        8, {"seated_work": "yes", "quiet_environment": "yes",
            "written_instructions": "yes", "assistive_tech_ok": "yes",
            "flexible_breaks": "no", "step_free_entrance": "yes", "lift": "yes"}))

    J.append(job(
        "job-tiima-driver", "emp-tiima", "Material driver — construction sites",
        "logistics", "espoon_keskus", "Depot at Kerantie 3", "on_site",
        15.80, "hour",
        ["Drive materials between sites and the depot.",
         "Load and unload with the site crew.",
         "Keep the van and the delivery log in order."],
        [sh(d, "06:30", "14:30") for d in ["mon", "tue", "wed", "thu", "fri"]],
        35, 40, "permanent", "required",
        "You learn the regular sites in your first weeks.",
        [lang("Finnish", "A2", "talk with the site leads")],
        "Tell me about your driving and what you have carried.",
        20, {"seated_work": "yes", "written_instructions": "yes"},
        quals=["Driving licence B"], lifting="Materials up to 20 kg"))

    J.append(job(
        "job-vihrea-autumn", "emp-vihrea", "Leaf and garden work — autumn",
        "seasonal", "olari", "Olari depot, Kuitukatu 1", "on_site",
        12.40, "hour",
        ["Rake leaves and clear beds in housing-company gardens.",
         "Plant spring bulbs in October.",
         "Work in a pair; rain gear provided."],
        [sh(d, "09:00", "15:00") for d in ["tue", "thu"]],
        12, 12, "seasonal", "none",
        "You always work with the regular gardener.",
        [], "Tell me about garden or outdoor work you have done.",
        30, {"written_instructions": "yes", "seated_work": "no",
             "adjustments_negotiable": "yes"},
        lifting="Tools and bags up to 10 kg"))

    J.append(job(
        "job-cafe-weekday", "emp-cafe-koivu", "Café lunch help — weekdays",
        "restaurant", "tapiola", "Kulttuuriaukio 2", "on_site",
        13.60, "hour",
        ["Serve the weekday lunch crowd 10:30–14:30.",
         "Refill the salad bar and the coffee pots.",
         "Clear and wipe tables."],
        [sh(d, "10:00", "15:00") for d in ["mon", "tue", "wed", "thu", "fri"]],
        20, 25, "permanent", "none",
        "You work the lunch shift with Sanna first.",
        [lang("Finnish", "B1", "serve customers")],
        "Tell me about serving a crowd — where have you done it?",
        4, {"step_free_entrance": "yes", "seated_work": "no",
            "flexible_breaks": "yes", "written_instructions": "yes",
            "accessible_toilet": "yes"}))

    J.append(job(
        "job-library-events", "emp-library", "Children's hour helper — Saturdays",
        "education", "matinkyla", "Pyörrekuja 6", "on_site",
        12.80, "hour",
        ["Help set up the Saturday children's story hour.",
         "Hand out craft materials and tidy up.",
         "Welcome families at the door."],
        [sh("sat", "09:30", "13:00")],
        4, 4, "fixed_term", "none",
        "The librarian plans the hour — you help it run.",
        [lang("Finnish", "B1", "talk with children and parents")],
        "Tell me about time you have spent with children.",
        2, {"step_free_entrance": "yes", "lift": "yes",
            "accessible_toilet": "yes", "seated_work": "yes",
            "written_instructions": "yes", "quiet_environment": "no"}))

    J.append(job(
        "job-koulutus-it", "emp-koulutus", "IT basics course assistant",
        "education", "kauklahti", "Lansirinteenkatu 1", "hybrid",
        14.50, "hour",
        ["Help adult learners with mouse, keyboard and files.",
         "Answer the same questions patiently, many times.",
         "Prepare printed step-by-step sheets."],
        [sh("mon", "13:00", "17:00"), sh("wed", "13:00", "17:00")],
        8, 8, "fixed_term", "some",
        "You assist beside the teacher for a full course round.",
        [lang("Finnish", "B1", "explain steps in simple Finnish")],
        "Tell me how you learned computers — and how you'd teach a beginner.",
        7, {"seated_work": "yes", "written_instructions": "yes",
            "step_free_entrance": "yes", "lift": "yes",
            "accessible_toilet": "yes"}))

    J.append(job(
        "job-oivo-shop", "emp-oivo", "Workshop assistant — paint mixing",
        "construction", "matinkyla", "Piispanmaenkatu 2", "on_site",
        13.40, "hour",
        ["Mix paint to order in the workshop.",
         "Label tins and keep the colour book updated.",
         "Load customers' cars."],
        [sh(d, "10:00", "17:00") for d in ["tue", "thu", "sat"]],
        18, 21, "permanent", "none",
        "You learn the mixing machine in your first weeks.",
        [lang("Finnish", "A2", "read the mixing recipes")],
        "Tell me about precise work with your hands.",
        10, {"seated_work": "yes", "written_instructions": "yes"},
        lifting="Paint tins up to 15 kg"))

    J.append(job(
        "job-aurora-day", "emp-aurora-care", "Day-shift care helper",
        "care", "leppavaara", "Vallikalliontie 3", "on_site",
        15.40, "hour",
        ["Help residents with breakfast, lunch and the day's activities.",
         "Walk with residents indoors and in the garden.",
         "Write short care notes after your shift."],
        [sh(d, "07:00", "15:00") for d in ["mon", "wed", "fri"]],
        24, 24, "permanent", "some",
        "A mentor works beside you for the first month.",
        [lang("Finnish", "B1", "talk with residents and write notes")],
        "Tell me about caring for someone — family counts too.",
        12, {"step_free_entrance": "yes", "lift": "yes",
             "accessible_toilet": "yes", "seated_work": "yes",
             "written_instructions": "yes", "flexible_breaks": "no"},
        lifting="Helping a resident stand — up to 20 kg with support"))

    J.append(job(
        "job-taikinapuu-cafe", "emp-taikinapuu", "Bakery café help — weekdays",
        "restaurant", "olari", "Olarinlaitos 4", "on_site",
        13.30, "hour",
        ["Serve at the café counter 10:00–15:00.",
         "Warm sandwiches and keep the case full.",
         "Clear and wipe tables."],
        [sh(d, "10:00", "15:00") for d in ["mon", "wed", "fri"]],
        15, 15, "permanent", "none",
        "You shadow the counter lead for a week.",
        [lang("Finnish", "B1", "serve customers")],
        "Tell me about serving people you have done.",
        5, {"seated_work": "no", "written_instructions": "yes",
            "step_free_entrance": "yes"}))

    J.append(job(
        "job-lumo-office", "emp-lumo", "Office keeper — small tech office",
        "office", "otaniemi", "Innopoli 2, Tekniikantie 14", "on_site",
        14.00, "hour",
        ["Keep our 14-person office running: coffee, post, plants.",
         "Set up meeting rooms and welcome guests.",
         "Order supplies when they run low."],
        [sh(d, "09:00", "14:00") for d in ["mon", "tue", "thu"]],
        15, 15, "permanent", "none",
        "You learn the office week with Sanna.",
        [lang("English", "B1", "talk with the team"),
         lang("Finnish", "A2", "handle deliveries")],
        "Tell me about a place you have kept running smoothly.",
        3, {"seated_work": "yes", "written_instructions": "yes",
            "adjustments_negotiable": "yes", "step_free_entrance": "yes",
            "lift": "yes"}))

    J.append(job(
        "job-otava-nightwatch", "emp-otava", "Data hall monitor — nights",
        "tech", "otaniemi", "Keilaranta 9", "on_site",
        16.50, "hour",
        ["Watch the data hall monitors at night.",
         "Call the on-duty engineer if an alarm goes off.",
         "Walk the hall once per shift and log it."],
        [sh(d, "21:00", "07:00") for d in ["wed", "sat"]],
        20, 20, "permanent", "some",
        "You shadow the night monitor for four shifts.",
        [lang("English", "B1", "read alerts and write the log")],
        "Tell me about night or monitoring work you have done.",
        14, {"seated_work": "yes", "quiet_environment": "yes",
             "written_instructions": "yes", "flexible_breaks": "yes",
             "step_free_entrance": "yes", "lift": "yes"}))

    return J


# --- users, applications, help requests ---------------------------------------

def make_users():
    return [
        {"id": "u-aino", "email": "aino@example.com", "phone": "+358 40 111 2223",
         "password": "demo1234", "role": "resident", "name": "Aino Korhonen",
         "profile": {
             "contact_method": "email", "district": "otaniemi",
             "fields": ["restaurant", "cleaning", "retail"],
             "availability": [
                 "mon-evening", "tue-evening", "wed-evening", "thu-evening",
                 "fri-evening",
                 "sat-morning", "sat-afternoon", "sat-evening",
                 "sun-morning", "sun-afternoon", "sun-evening"],
             "max_hours_per_week": 20, "needs": [],
             "languages": [{"language": "Finnish", "level": "C2"},
                           {"language": "English", "level": "B2"}],
             "about": "Second-year student at Aalto. I can work evenings and "
                      "weekends around my lectures."}},
        {"id": "u-pekka", "email": "pekka@example.com", "phone": "+358 50 444 5556",
         "password": "demo1234", "role": "resident", "name": "Pekka Mäkinen",
         "profile": {
             "contact_method": "phone", "district": "matinkyla",
             "fields": ["education", "retail"],
             "availability": ["mon-morning", "wed-morning"],
             "max_hours_per_week": 10, "needs": [],
             "languages": [{"language": "Finnish", "level": "C2"},
                           {"language": "Swedish", "level": "B1"}],
             "about": "Retired electrician. I would like a few easy hours a "
                      "week, mostly to meet people."}},
        {"id": "u-amira", "email": "amira@example.com",
         "phone": "+358 44 777 8889",
         "password": "demo1234", "role": "resident", "name": "Amira Haddad",
         "profile": {
             "contact_method": "sms", "district": "leppavaara",
             "fields": ["customer_service", "office"],
             "availability": ["mon-morning", "mon-afternoon",
                              "wed-morning", "wed-afternoon",
                              "fri-morning"],
             "max_hours_per_week": 25,
             "needs": ["step_free_entrance", "seated_work"],
             "languages": [{"language": "Arabic", "level": "C2"},
                           {"language": "English", "level": "B2"},
                           {"language": "Finnish", "level": "B1"}],
             "about": "Customer service and office work. I use a wheelchair "
                      "and need a step-free entrance and seated work."}},
        {"id": "u-sanna", "email": "sanna@example.com", "phone": "+358 40 222 3334",
         "password": "demo1234", "role": "employer", "name": "Sanna Lehto",
         "employer_id": "emp-cafe-koivu"},
        {"id": "u-advisor", "email": "advisor@example.com",
         "phone": "+358 40 999 0001",
         "password": "demo1234", "role": "advisor",
         "name": "Leena, Employment Espoo"},
    ]


def make_applications():
    """Three applications to Sanna's café job in different statuses, plus one
    stale 'sent' application that shows in the advisor follow-up queue."""
    return [
        {"id": "ap-001", "job_id": "job-cafe-weekend", "user_id": None,
         "name": "Mikael Okafor", "contact_method": "phone",
         "contact_value": "+358 44 123 4567",
         "availability_note": "Weekends work for me.",
         "answer": "I served lunch at my school café for a year and I like "
                   "busy counter work.",
         "shared_needs": [], "meet_at_event": 0, "status": "sent",
         "status_note": "", "days_ago": 2},
        {"id": "ap-002", "job_id": "job-cafe-weekend", "user_id": "u-aino",
         "name": "Aino Korhonen", "contact_method": "email",
         "contact_value": "aino@example.com",
         "availability_note": "Every weekend, and more in June.",
         "answer": "I ran the coffee stand at our guild's spring fair — "
                   "three busy days, two tills, a lot of customers.",
         "shared_needs": [], "meet_at_event": 1, "status": "interview",
         "status_note": "Come to the café on Thursday at 15:00 — ask for "
                        "Sanna.", "days_ago": 5},
        {"id": "ap-003", "job_id": "job-cafe-weekend", "user_id": None,
         "name": "Sara Kettunen", "contact_method": "sms",
         "contact_value": "+358 45 765 4321",
         "availability_note": "Saturdays only at the moment.",
         "answer": "I helped at our church café for two years.",
         "shared_needs": ["seated_work"], "meet_at_event": 0,
         "status": "not_selected",
         "status_note": "We needed someone who could do both weekend days "
                        "this time — thank you for applying.",
         "days_ago": 9},
        {"id": "ap-004", "job_id": "job-linja-phone", "user_id": None,
         "name": "Yusuf Ali", "contact_method": "phone",
         "contact_value": "+358 46 111 2233",
         "availability_note": "Weekdays after 14:00 as well.",
         "answer": "I answered phones in a repair shop for two years.",
         "shared_needs": [], "meet_at_event": 0, "status": "sent",
         "status_note": "", "days_ago": 9, "created_by_advisor": 1},
    ]


def make_help_requests():
    return [
        {"id": "hr-001", "user_id": "u-amira", "name": "Amira Haddad",
         "contact_method": "sms", "contact_value": "+358 44 777 8889",
         "job_id": "job-cs-desk", "kind": "check_conditions",
         "condition_keys": ["step_free_entrance"],
         "message": "Please check if the entrance and desk are step-free "
                    "before I apply.",
         "consent": 1, "status": "new", "days_ago": 1},
    ]


def make_saved():
    return [{"user_id": "u-aino", "job_id": "job-weegee"}]


def main(out_dir: Path | None = None):
    out_dir = out_dir or SEED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = make_jobs()
    assert len(jobs) == 60, f"expected 60 jobs, wrote {len(jobs)}"
    assert len({j["id"] for j in jobs}) == len(jobs)

    employers = [{"id": eid, "name": name, "about": about,
                  "contact_name": contact,
                  "contact_email": f"info@{eid.split('emp-')[1]}.example.com",
                  "contact_phone": "+358 40 000 0000",
                  "booth": booth}
                 for eid, name, about, contact, booth in EMPLOYERS]

    catalog = {
        "fields": FIELDS,
        "districts": DISTRICTS,
        "condition_keys": [{"id": k, "label": l} for k, l in CONDITION_KEYS],
        "contract_types": CONTRACTS,
        "language_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
    }

    files = {
        "event.json": EVENT,
        "employers.json": employers,
        "jobs.json": jobs,
        "users.json": make_users(),
        "applications.json": make_applications(),
        "help_requests.json": make_help_requests(),
        "saved_jobs.json": make_saved(),
        "catalog.json": catalog,
    }
    for name, payload in files.items():
        (out_dir / name).write_text(json.dumps(payload, indent=2,
                                              ensure_ascii=False),
                                    encoding="utf-8")

    open_jobs = [j for j in jobs if j["status"] == "open"]
    stale = [j["id"] for j in open_jobs if j["confirmed_days_ago"] > 14]
    at_event = [j["id"] for j in open_jobs
                if next(e for e in employers
                        if e["id"] == j["employer_id"])["booth"]]
    print(f"seed written to {out_dir}")
    print(f"{len(open_jobs)} open jobs, {len(employers)} employers, "
          f"{len(at_event)} jobs at the event, {len(stale)} stale jobs")


if __name__ == "__main__":
    sys.exit(main())
