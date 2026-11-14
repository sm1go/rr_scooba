#!/usr/bin/env python3
"""Add ~90 extra synthetic jobs (and their employers) to the seed.

All data is fictional (constraint C2): companies, people, e-mails
(*.example.com) and phone numbers (+358 40 000 01xx) are invented.

The script is idempotent and deterministic: it keeps the 60 jobs and 28
employers written by `scripts/generate_synthetic.py` untouched, removes any
earlier copy of its own rows and appends them again. Run it AFTER
`generate_synthetic.py` (which rewrites jobs.json, employers.json and
catalog.json from scratch):

    python scripts/generate_synthetic.py
    python scripts/gen_more_jobs.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "db" / "seed"

NEW_FIELDS = [
    {"id": "manufacturing", "name": "Manufacturing and metal work"},
    {"id": "health", "name": "Health care"},
    {"id": "maintenance", "name": "Property maintenance and trades"},
]

# --- employers ------------------------------------------------------------------
# (id, name, about, contact person) — no event booths for these.

EMPLOYERS = [
    ("emp-terasmetso", "Teräsmetso Works Oy", "Steel frames and machine parts, a 40-person workshop in Kauklahti.", "Jari Kallunki"),
    ("emp-rosteri", "Rosteri Linja Oy", "Stainless-steel process equipment for food and pharma plants.", "Marko Vainio"),
    ("emp-arcmec", "Arcmec Assembly Oy", "Electrical cabinets and robot welding in Olari.", "Satu Hirvelä"),
    ("emp-hila", "Pakkaamo Hila Oy", "Food packing plant for ready meals and salads.", "Kimmo Laaksonen"),
    ("emp-virta", "Sähkö-Virta Espoo Oy", "Electrical installation for homes and housing companies.", "Tero Huhta"),
    ("emp-lvikaari", "LVI-Kaari Oy", "Plumbing, heating and ventilation renovations.", "Pasi Ojala"),
    ("emp-rantala", "Kiinteistöhuolto Rantala Oy", "Property maintenance for 120 housing companies in south Espoo.", "Merja Rantala"),
    ("emp-lastu", "Puusepänliike Lastu", "Small carpentry firm: stairs, terraces and renovation.", "Heikki Lastunen"),
    ("emp-savy", "Pintamaalaus Sävy Oy", "Interior and facade painting.", "Niina Kaarto"),
    ("emp-kivisauma", "Laattatyö Kivisauma", "Tiling and wet-room renovation.", "Ari Saumala"),
    ("emp-peruskivi", "Rakennusliike Peruskivi Oy", "Apartment building sites in Espoon keskus.", "Janne Kivelä"),
    ("emp-routa", "Kuljetusliike Routa Oy", "Regional deliveries and a cross-dock warehouse.", "Sami Routio"),
    ("emp-lahilinja", "Lähilinja Bus Oy", "Bus operator running local routes in west Espoo.", "Kaisa Linjala"),
    ("emp-apaja", "Palvelutaksi Apaja", "Accessible taxi and school transport.", "Raimo Apajalahti"),
    ("emp-kuura", "Lääkärikeskus Kuura", "Private medical clinic with a small laboratory.", "Helena Kuusela"),
    ("emp-hymy", "Hammasklinikka Hymy", "Dental clinic with four treatment rooms.", "Laura Hymynen"),
    ("emp-kaisla", "Apteekki Kaisla", "Pharmacy in the Espoonlahti shopping centre.", "Tiina Kaislanen"),
    ("emp-kaste", "Kotihoito Kaste Oy", "Home care for older people in west Espoo.", "Marja Kastela"),
    ("emp-silta", "Avustajapalvelu Silta", "Matches personal assistants with disabled clients.", "Johanna Siltanen"),
    ("emp-satakieli", "Päiväkoti Satakieli", "Private daycare with Finnish and English groups.", "Riikka Laulaja"),
    ("emp-kuusikko", "Kuusikon koulu", "Fictional primary school (grades 1-6) used in this demo.", "Mervi Kuusinen"),
    ("emp-havu", "Ravintola Havu", "Lunch and à la carte restaurant near Leppävaara station.", "Toni Havukainen"),
    ("emp-fornello", "Pizzeria Fornello", "Wood-fired pizza, eat-in and delivery.", "Luca Bianchi"),
    ("emp-pavut", "Paahtimo Pavut", "Coffee roastery café on the university campus.", "Elina Paahtola"),
    ("emp-laguuni", "Hotelli Laguuni", "120-room business hotel in Keilaniemi.", "Petra Laguna"),
    ("emp-kauppakulma", "Supermarket Kauppakulma", "Large supermarket in Espoon keskus.", "Juha Kulmala"),
    ("emp-oravanpesa", "Tavaratalo Oravanpesä", "Department store in Matinkylä.", "Sari Oravisto"),
    ("emp-kielo", "Kukkakauppa Kielo", "Flower shop near Leppävaara station.", "Anja Kielonen"),
    ("emp-saksi", "Kampaamo Saksi", "Hair salon with six chairs.", "Minna Saksala"),
    ("emp-mantymaki", "Autokorjaamo Mäntymäki", "Car repair and tyre hotel.", "Kari Mäntylä"),
    ("emp-polku", "Pyöräpaja Polku", "Bike repair and rental.", "Ville Polkunen"),
    ("emp-vahti", "Turvapalvelu Vahti Oy", "Security guarding for shops, offices and events.", "Mika Vahtera"),
    ("emp-laskelma", "Taloushallinto Laskelma Oy", "Accounting and payroll for 300 small businesses.", "Eija Laskunen"),
    ("emp-kulma", "Yrityskeskus Kulma", "Shared offices and meeting rooms in Tapiola.", "Hanna Kulmanen"),
    ("emp-sanasilta", "Käännöstoimisto Sanasilta", "Translation and interpreting agency.", "Olga Sanakoski"),
    ("emp-koodikallio", "Koodikallio Oy", "Software studio building apps for public services.", "Aleksi Koodari"),
    ("emp-datavirta", "Datavirta Analytics Oy", "Data and IT services for retailers.", "Noora Virtala"),
    ("emp-bioteekki", "Bioteekki Labs Oy", "Contract laboratory for food and water testing.", "Pekka Biolahti"),
    ("emp-espoolive", "Espoo Live Events (fictional)", "Organises outdoor concerts and markets.", "Roosa Tapahtuma"),
    ("emp-kesaduuni", "Kesäduuni — youth summer work (demo)", "Fictional city-style summer job programme for 15-17-year-olds.", "Tuuli Kesälä"),
    ("emp-kanerva", "Viherrakennus Kanerva", "Garden building and maintenance.", "Oskari Kanervo"),
    ("emp-helmi", "Puhtauspalvelu Helmi Oy", "Office, shop and building-site cleaning.", "Liisa Helmelä"),
]

DISTRICTS = {
    "leppavaara": (60.2198, 24.8135), "tapiola": (60.1760, 24.8050),
    "otaniemi": (60.1860, 24.8278), "matinkyla": (60.1600, 24.7380),
    "olari": (60.1715, 24.7450), "niittykumpu": (60.1690, 24.7730),
    "espoon_keskus": (60.2055, 24.6560), "espoonlahti": (60.1490, 24.6600),
    "kauklahti": (60.1880, 24.6010), "kalajarvi": (60.2950, 24.5700),
}

COND_KEYS = {
    "sfe": "step_free_entrance", "lift": "lift", "toilet": "accessible_toilet",
    "seated": "seated_work", "breaks": "flexible_breaks",
    "quiet": "quiet_environment", "written": "written_instructions",
    "sign": "sign_language_ok", "assist": "assistive_tech_ok",
    "adjust": "adjustments_negotiable",
}

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# --- helpers ------------------------------------------------------------------


def sh(days, start, end):
    """sh('mon-fri', '07:00', '15:30') or sh('sat,sun', ...)."""
    if "-" in days:
        a, b = days.split("-")
        ds = DAYS[DAYS.index(a):DAYS.index(b) + 1]
    else:
        ds = days.split(",")
    return [{"day": d, "start": start, "end": end} for d in ds]


def L(language, level, task):
    return {"language": language, "level": level, "task": task}


def C(**kw):
    """C(sfe='y', seated=('n', 'note')) -> conditions dict."""
    out = {}
    for k, v in kw.items():
        key = COND_KEYS[k]
        if isinstance(v, tuple):
            out[key] = {"value": "yes" if v[0] == "y" else "no", "note": v[1]}
        else:
            out[key] = "yes" if v == "y" else "no"
    return out


JOBS: list[dict] = []


def J(jid, emp, title, field, district, address, pay, unit, duties, shifts,
      hours, contract, exp, onboarding, langs, ask, days, cond, *,
      mode="on_site", flexible=0, pay_note="", exp_note="", quals=None,
      lifting=None, cv=0, positions=1, source="employer"):
    lat0, lon0 = DISTRICTS[district]
    rng = random.Random(f"{emp}|{address}")   # same address -> same pin
    JOBS.append({
        "id": jid, "employer_id": emp, "title": title, "field": field,
        "duties": duties, "address": address, "district": district,
        "lat": round(lat0 + rng.uniform(-0.0018, 0.0018), 5),
        "lon": round(lon0 + rng.uniform(-0.0028, 0.0028), 5),
        "work_mode": mode, "pay_amount": pay, "pay_unit": unit,
        "pay_note": pay_note, "shifts": shifts, "schedule_flexible": flexible,
        "hours_min": hours[0], "hours_max": hours[1], "contract": contract,
        "experience": exp, "experience_note": exp_note,
        "qualifications": quals or [], "onboarding": onboarding,
        "languages": langs, "lifting": lifting, "apply_question": ask,
        "cv_required": cv, "positions": positions, "status": "open",
        "source": source, "confirmed_days_ago": days, "conditions": cond,
    })


HOT = "Hot work card (tulityökortti)"
SAFE = "Occupational safety card (työturvallisuuskortti)"
HYG = "Hygiene passport (hygieniapassi)"
VALVIRA = "Valvira registration (JulkiTerhikki)"
BLIC = "Driving licence B"

# --- manufacturing and metal work ---------------------------------------------

J("job-terasmetso-mig", "emp-terasmetso", "Welder — MIG/MAG", "manufacturing",
  "kauklahti", "Hansakallio 4", 17.8, "hour",
  ["Weld steel frames and brackets with MIG/MAG (fillet and butt welds).",
   "Read simple workshop drawings and check measurements.",
   "Grind and finish welds; keep your booth tidy."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "permanent", "required",
  "Two days with the foreman, then a test piece before you work alone.",
  [L("Finnish", "A2", "read safety signs and short work orders"),
   L("English", "B1", "talk with the foreman")],
  "Which welding positions have you done (PA, PB, PF…)? Tell me about one tricky weld.",
  2, C(written=("y", "Drawings and work orders are on paper at every booth."),
       seated="n", breaks="n", quiet="n"),
  quals=["SC welding certificate (EN ISO 9606-1, MAG 135/136)", HOT],
  lifting="Steel parts up to 25 kg; an overhead crane lifts anything heavier",
  positions=2, pay_note="Shift supplement for the evening shift.")

J("job-terasmetso-trainee", "emp-terasmetso", "Welder trainee", "manufacturing",
  "kauklahti", "Hansakallio 4", 13.2, "hour",
  ["Learn MAG welding from our welding instructor.",
   "Help with cutting, grinding and fitting parts.",
   "Take the SC certificate test at the end — we pay for it."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "traineeship", "none",
  "A 4-month in-house programme; pay rises to the welder rate after the certificate.",
  [L("Finnish", "A2", "follow safety instructions"),
   L("English", "A2", "follow safety instructions (if no Finnish)")],
  "Have you done any hands-on work — metal, cars, bikes, building? Tell me about it.",
  5, C(written="y", adjust="y"),
  lifting="Parts up to 20 kg", positions=2)

J("job-terasmetso-sheet", "emp-terasmetso", "Sheet-metal worker — evening shift", "manufacturing",
  "kauklahti", "Hansakallio 4", 16.4, "hour",
  ["Bend sheet metal on a CNC press brake.",
   "Set up tools from the job card and check the first part.",
   "Deburr and stack finished parts for the welders."],
  sh("mon-thu", "14:30", "23:00"), (34, 34), "permanent", "some",
  "One week on the day shift with an experienced bender.",
  [L("Finnish", "A2", "read job cards"), L("English", "B1", "ask the shift lead")],
  "Have you used a press brake, guillotine or punch? What did you make?",
  9, C(seated="n"),
  lifting="Sheets up to 15 kg; vacuum lifter for big sheets",
  pay_note="Evening shift supplement +1.30 €/h on top of the hourly pay.")

J("job-rosteri-tig", "emp-rosteri", "TIG welder, stainless steel", "manufacturing",
  "espoon_keskus", "Kuurinniityntie 12", 19.6, "hour",
  ["TIG-weld stainless pipes and tanks (AISI 316L) to hygiene standards.",
   "Purge gas set-up and visual inspection of your welds.",
   "Some installation trips to customer plants in the Helsinki region."],
  sh("mon-fri", "06:30", "15:00"), (37.5, 37.5), "permanent", "required",
  "Weld test on your first day, then a week with a senior welder.",
  [L("Finnish", "B1", "talk with customers on installation trips"),
   L("English", "B1", "work in the workshop (Finnish not needed there)")],
  "Tell me about stainless or thin-wall pipe welding you have done.",
  1, C(sfe="y", toilet="y", written="y", seated="n", breaks="n", quiet="n", adjust="y"),
  quals=["SC welding certificate (EN ISO 9606-1, TIG 141, stainless)", HOT, BLIC],
  lifting="Pipes and fittings up to 15 kg", exp_note="At least 2 years of TIG welding.",
  cv=1)

J("job-rosteri-cnc", "emp-rosteri", "CNC machinist", "manufacturing",
  "espoon_keskus", "Kuurinniityntie 12", 18.2, "hour",
  ["Run CNC lathes and milling machines (Fanuc and Heidenhain controls).",
   "Set up tools, load programmes and measure parts with micrometers.",
   "Small programme edits at the machine."],
  sh("mon-fri", "06:00", "14:00") + sh("mon-fri", "14:00", "22:00"), (37.5, 37.5),
  "permanent", "some",
  "Two weeks with the machine shop lead; written set-up sheets for every part.",
  [L("Finnish", "A2", "read set-up sheets"), L("English", "B1", "talk with the shop lead")],
  "Which machines and controls have you used?", 6,
  C(written="y", quiet="n"),
  lifting="Blanks up to 20 kg; hoist at each machine",
  pay_note="Two-shift work: mornings one week, evenings the next. Evening supplement +1.10 €/h.",
  exp_note="Vocational qualification in machining or about a year at a CNC machine.")

J("job-arcmec-assembly", "emp-arcmec", "Assembly worker — electrical cabinets", "manufacturing",
  "olari", "Juvanpuistonkatu 3", 15.1, "hour",
  ["Mount rails, terminals and cable ducts following an assembly picture.",
   "Cut, strip and connect wires; label every wire.",
   "Check your own work with a checklist."],
  sh("mon-fri", "07:00", "15:00"), (37.5, 37.5), "permanent", "none",
  "Picture-based instructions at every workbench; a mentor for two weeks.",
  [L("Finnish", "A2", "read the checklist"), L("English", "A2", "read the checklist (English version exists)")],
  "Do you like detailed hand work? Tell me about something you built or repaired.",
  2, C(sfe="y", lift="y", toilet="y", seated=("y", "Height-adjustable benches; stand or sit."),
       breaks="n", quiet="n", written="y", assist="y", adjust="y"),
  lifting="Light — parts under 5 kg", positions=3)

J("job-arcmec-evening", "emp-arcmec", "Assembly worker — 4 evenings a week", "manufacturing",
  "olari", "Juvanpuistonkatu 3", 15.1, "hour",
  ["Assemble cable sets and small components.",
   "Pack finished cabinets parts for the next morning.",
   "Keep the work area tidy at the end of the shift."],
  sh("mon-thu", "16:00", "21:00"), (20, 20), "fixed_term", "none",
  "First evening with the shift lead; same picture instructions as the day shift.",
  [L("Finnish", "A1", "greet colleagues"), L("English", "A2", "follow instructions")],
  "Which evenings can you work, and from when can you start?", 4,
  C(seated="y", written="y"),
  lifting="Light — under 5 kg", pay_note="Evening supplement +1.00 €/h.")

J("job-arcmec-robot", "emp-arcmec", "Robot welding cell operator", "manufacturing",
  "olari", "Juvanpuistonkatu 3", 16.9, "hour",
  ["Load and unload parts in two welding robot cells.",
   "Start programmes, watch weld quality and fix small faults.",
   "Do touch-up welding by hand when needed (MIG/MAG)."],
  sh("mon-fri", "06:00", "14:00") + sh("mon-fri", "14:00", "22:00"), (37.5, 37.5),
  "permanent", "some",
  "Robot course with the supplier (3 days), then a month on shift with an operator.",
  [L("Finnish", "B1", "read robot screen messages and fault reports"),
   L("English", "A2", "talk with colleagues")],
  "Have you welded or run any production machine? What did you do there?", 11,
  C(sfe="y", written="y", seated="n"),
  quals=[HOT], lifting="Parts up to 15 kg; lifting aids at the cell",
  pay_note="Rotating two shifts, evening supplement +1.10 €/h.")

J("job-hila-packer", "emp-hila", "Factory packer — food production", "manufacturing",
  "kalajarvi", "Lahnuksentie 18", 14.2, "hour",
  ["Pack salads and ready meals on a production line.",
   "Label boxes and stack them on pallets.",
   "Work in a cool room (+6 °C); warm workwear is provided."],
  sh("mon-fri", "06:00", "14:00"), (30, 37.5), "permanent", "none",
  "Hygiene training on day one; a buddy for your first week.",
  [L("Finnish", "A1", "understand basic words — picture signs everywhere"),
   L("English", "A2", "follow the line lead")],
  "When could you start, and can you be at work by 6 in the morning?", 3,
  C(written=("y", "Picture instructions at every line station."), seated="n", breaks="n"),
  quals=[HYG + " — we help you get it"], lifting="Boxes up to 10 kg", positions=4)

J("job-hila-weekend", "emp-hila", "Factory packer — weekends", "manufacturing",
  "kalajarvi", "Lahnuksentie 18", 14.2, "hour",
  ["Pack and label food products for Monday deliveries.",
   "Clean the line at the end of the shift."],
  sh("sat,sun", "07:00", "15:00"), (8, 16), "permanent", "none",
  "One training shift on a weekday.",
  [L("Finnish", "A1", "basic words"), L("English", "A2", "follow instructions")],
  "Can you work both weekend days or only one?", 7,
  C(seated="n"),
  quals=[HYG], lifting="Boxes up to 10 kg", pay_note="Sunday work is paid double.",
  positions=2)

J("job-hila-line", "emp-hila", "Production line operator", "manufacturing",
  "kalajarvi", "Lahnuksentie 18", 15.6, "hour",
  ["Run and adjust a tray-sealing and labelling line.",
   "Change film rolls and labels; record checks in the tablet.",
   "Report faults to maintenance."],
  sh("mon-fri", "06:00", "14:00") + sh("mon-fri", "14:00", "22:00") + sh("sun-thu", "22:00", "06:00"),
  (37.5, 37.5), "permanent", "some",
  "Three weeks with an operator on each shift.",
  [L("Finnish", "B1", "record quality checks")],
  "Have you run a machine or a production line before? Tell me about it.", 8,
  C(),
  quals=[HYG], lifting="Film rolls up to 18 kg",
  pay_note="Three-shift rotation; evening and night supplements.")

# --- property maintenance and trades -----------------------------------------

J("job-virta-electrician", "emp-virta", "Electrician", "maintenance",
  "espoon_keskus", "Kamreerintie 6", 19.4, "hour",
  ["Electrical installation and renovation in apartments and housing companies.",
   "Fault finding and repairs; measurement and commissioning reports.",
   "Drive the company van between sites."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "permanent", "required",
  "You start in a pair with a senior electrician for two weeks.",
  [L("Finnish", "B1", "talk with residents and read site documents")],
  "What kind of electrical work have you done most — new builds, renovation, service?",
  4, C(written="y", seated="n"),
  quals=["Electrical safety qualification S2 (sähköpätevyys)",
         "Electrical work safety card (sähkötyöturvallisuuskortti)", SAFE, BLIC],
  lifting="Cable reels and tools up to 20 kg", exp_note="Vocational qualification in electrical installation.",
  cv=1, pay_note="Tool allowance and daily travel allowance paid.")

J("job-virta-assistant", "emp-virta", "Electrician's assistant", "maintenance",
  "espoon_keskus", "Kamreerintie 6", 14.6, "hour",
  ["Pull cables, mount boxes and ducts with an electrician.",
   "Carry materials and keep sites tidy.",
   "Learn the trade — apprenticeship (oppisopimus) possible later."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "fixed_term", "none",
  "We pay for the occupational and electrical work safety cards in your first month.",
  [L("Finnish", "A2", "understand instructions on site"), L("English", "B1", "talk with your electrician")],
  "Why would you like to learn electrical work?", 8,
  C(adjust="y"),
  lifting="Materials up to 20 kg", exp_note="No experience needed.")

J("job-lvikaari-plumber", "emp-lvikaari", "Plumber", "maintenance",
  "kauklahti", "Kauklahdenväylä 9", 18.6, "hour",
  ["Pipe renovations (putkiremontti) in apartment buildings.",
   "Install water pipes, drains, taps and toilets.",
   "Pressure tests and handover paperwork."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "permanent", "required",
  "A week with the site foreman to learn our way of working.",
  [L("Finnish", "B1", "talk with residents and the site foreman")],
  "Tell me about the biggest plumbing job you have done.", 6,
  C(seated="n", breaks="y"),
  quals=[HOT, SAFE, BLIC], lifting="Pipes and fittings up to 25 kg",
  exp_note="Vocational qualification in plumbing or 3+ years of experience.")

J("job-lvikaari-hvac", "emp-lvikaari", "HVAC installer (ventilation)", "maintenance",
  "kauklahti", "Kauklahdenväylä 9", 17.4, "hour",
  ["Install ventilation ducts, units and grilles in renovation sites.",
   "Balance air flows with the measurement team.",
   "Work on ladders and scaffolds."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "permanent", "some",
  "Work in a pair with an experienced installer.",
  [L("Finnish", "A2", "read the site plan"), L("English", "B1", "talk with your pair")],
  "Have you worked on building sites? What did you do?", 13,
  C(),
  quals=[HOT, SAFE], lifting="Ducts up to 20 kg, often overhead")

J("job-rantala-huolto", "emp-rantala", "Property maintenance worker (kiinteistöhuoltaja)", "maintenance",
  "matinkyla", "Piispansilta 9", 2650, "month",
  ["Daily rounds in housing companies: heating, water, lighting, doors.",
   "Fix small faults and call contractors for bigger ones.",
   "Yard work: in winter snow and grit, in summer lawns."],
  sh("mon-fri", "07:00", "15:00"), (37.5, 37.5), "permanent", "some",
  "Two weeks on rounds with a senior maintenance worker; written site cards for every building.",
  [L("Finnish", "B1", "talk with residents and write fault notes")],
  "What have you fixed or maintained yourself — at home, at work, anywhere?", 2,
  C(sfe="y", toilet="y", written="y", seated="n", breaks="y", quiet="n", adjust="y"),
  quals=[BLIC, SAFE], lifting="Tools and grit bags up to 20 kg",
  pay_note="On-call week every 6 weeks with a separate on-call allowance.")

J("job-rantala-apprentice", "emp-rantala", "Property maintenance apprentice", "maintenance",
  "matinkyla", "Piispansilta 9", 2150, "month",
  ["Learn property maintenance on the job with a mentor.",
   "Study one day a month for the vocational qualification (oppisopimus).",
   "Rounds, small repairs and yard work."],
  sh("mon-fri", "07:00", "15:00"), (37.5, 37.5), "traineeship", "none",
  "Your mentor works with you every day for the first three months.",
  [L("Finnish", "A2", "talk with your mentor; we support your Finnish")],
  "Why does maintenance work interest you?", 10,
  C(adjust="y", written="y"),
  quals=[BLIC], lifting="Up to 20 kg")

J("job-rantala-janitor", "emp-rantala", "Janitor — school building", "maintenance",
  "matinkyla", "Matinkatu 15", 2380, "month",
  ["Open the school building, check heating, locks and alarms.",
   "Small repairs: lamps, furniture, doors.",
   "Help with deliveries and keep the yard safe."],
  sh("mon-fri", "06:00", "14:00"), (37.5, 37.5), "permanent", "some",
  "Hand-over week with the retiring janitor.",
  [L("Finnish", "B1", "talk with school staff and pupils"),
   L("Swedish", "A2", "greet staff in the Swedish-language wing (nice to have)")],
  "Tell me about a time you kept a place running — a home, a club, a workplace.", 6,
  C(sfe="y", lift="y", toilet="y"),
  lifting="Furniture with a trolley, up to 15 kg")

J("job-rantala-weekend", "emp-rantala", "Weekend caretaker rounds — 8 h a week", "maintenance",
  "olari", "Olarinkatu 12", 15.2, "hour",
  ["Weekend rounds in six buildings: check boiler rooms, doors and lights.",
   "Note faults in the phone app for Monday."],
  sh("sat,sun", "09:00", "13:00"), (8, 8), "permanent", "some",
  "One weekend together with the regular caretaker.",
  [L("Finnish", "A2", "write short fault notes"), L("English", "B1", "report faults")],
  "Can you work every weekend, or every other?", 5,
  C(written="y"), lifting=None)

J("job-rantala-snow", "emp-rantala", "Snow clearing — seasonal, on call", "seasonal",
  "matinkyla", "Piispansilta 9", 16.0, "hour",
  ["Clear snow from entrances and paths by hand and with a small tractor.",
   "Spread grit on icy mornings.",
   "Work starts early when it snows — we call by 4 a.m."],
  [], (0, 30), "seasonal", "none",
  "Tractor training in November before the snow.",
  [L("Finnish", "A2", "understand the call-out message"),
   L("English", "A2", "understand the call-out message")],
  "Can you start at 4 a.m. at short notice? How would you get to Matinkylä?", 20,
  C(written="n"),
  flexible=1, quals=[BLIC + " (tractor training given)"],
  lifting="Shovelling and grit bags up to 20 kg",
  pay_note="November–March. Night and Sunday supplements.", positions=3)

J("job-lastu-carpenter", "emp-lastu", "Carpenter (kirvesmies)", "construction",
  "kalajarvi", "Lahnuksentie 30", 18.0, "hour",
  ["Build terraces, stairs and interior wood work.",
   "Renovation: doors, windows, floors.",
   "Measure and cut on site."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "permanent", "required",
  "You work with the owner for the first weeks.",
  [L("Finnish", "B1", "talk with home owners")],
  "Tell me about one wood job you are proud of.", 12,
  C(seated="n"),
  quals=[SAFE, BLIC], lifting="Timber up to 25 kg",
  source="advisor", exp_note="Carpenter qualification or several years on sites.")

J("job-savy-painter", "emp-savy", "Painter", "construction",
  "leppavaara", "Perkkaantie 4", 16.8, "hour",
  ["Prepare walls: fill, sand, tape.",
   "Paint interiors in apartments and offices; facades in summer.",
   "Protect floors and furniture; clean up."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "permanent", "some",
  "Two weeks with a team leader.",
  [L("Finnish", "A2", "talk with the team"), L("English", "B1", "talk with the team")],
  "Have you painted before — at work or at home? What went well?", 3,
  C(seated="n", breaks="y"),
  quals=[SAFE], lifting="Paint buckets up to 15 kg; ladders")

J("job-kivisauma-tile", "emp-kivisauma", "Tile setter", "construction",
  "espoonlahti", "Ulappakatu 2", 19.0, "hour",
  ["Waterproof and tile bathrooms and saunas.",
   "Lay floor and wall tiles; grout and seal.",
   "Plan tile layouts with the customer."],
  sh("mon-fri", "07:30", "16:00"), (30, 37.5), "permanent", "required",
  "One joint job with the owner, then your own sites.",
  [L("Finnish", "B1", "talk with customers")],
  "Show or tell me about a bathroom you tiled.", 26,
  C(),
  quals=["Wet-room installer certificate (märkätilasertifikaatti)", BLIC],
  lifting="Tile boxes and mortar bags up to 25 kg", pay_note="Piece-rate bonus possible.")

J("job-peruskivi-labourer", "emp-peruskivi", "Construction labourer", "construction",
  "espoon_keskus", "Kirkkojärventie 20", 15.5, "hour",
  ["Carry and lift materials, build and take down supports.",
   "Keep the site clean and safe.",
   "Help carpenters and concrete workers."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "fixed_term", "none",
  "Site induction on day one; a foreman tells you each morning what to do.",
  [L("Finnish", "A1", "understand safety words"), L("English", "A2", "talk with the foreman")],
  "Are you used to physical work outdoors in all weather?", 1,
  C(seated="n", breaks="n", written="y"),
  quals=[SAFE + " — we can arrange the course"], lifting="Materials up to 25 kg",
  positions=4)

J("job-peruskivi-summer", "emp-peruskivi", "Summer site helper (18+)", "construction",
  "espoon_keskus", "Kirkkojärventie 20", 13.8, "hour",
  ["Site cleaning, waste sorting and carrying materials.",
   "Help the site storage keeper."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "summer_job", "none",
  "Site induction and safety walk on day one.",
  [L("Finnish", "A2", "understand site safety rules"), L("English", "A2", "talk with colleagues")],
  "Which summer weeks can you work?", 8,
  C(seated="n"),
  quals=[SAFE], lifting="Up to 20 kg", pay_note="June–August.")

J("job-mantymaki-mechanic", "emp-mantymaki", "Car mechanic", "maintenance",
  "espoon_keskus", "Kuurinniityntie 30", 17.2, "hour",
  ["Service and repair cars of all brands.",
   "Read fault codes with diagnostic tools.",
   "Explain the repair to the customer service desk."],
  sh("mon-fri", "08:00", "16:30"), (37.5, 37.5), "permanent", "required",
  "One week to learn our system; manufacturer courses during the year.",
  [L("Finnish", "A2", "read work orders"), L("English", "B1", "talk with the workshop lead")],
  "Which car brands and systems do you know best?", 5,
  C(sfe="y", toilet="y", seated="n"),
  quals=[BLIC], lifting="Wheels and parts up to 25 kg",
  exp_note="Vehicle mechanic qualification or equivalent experience.")

J("job-mantymaki-tyre", "emp-mantymaki", "Tyre fitter — autumn and spring season", "seasonal",
  "espoon_keskus", "Kuurinniityntie 30", 14.5, "hour",
  ["Change and balance tyres.",
   "Take tyres in and out of the tyre hotel.",
   "Torque wheels and fill in the checklist."],
  sh("mon-fri", "07:00", "17:00") + sh("sat", "09:00", "15:00"), (25, 40), "seasonal", "none",
  "Two days with an experienced fitter.",
  [L("Finnish", "A1", "basic words"), L("English", "A2", "follow instructions")],
  "Can you work long days in October–November?", 7,
  C(seated="n"),
  quals=[BLIC], lifting="Wheels up to 25 kg, all day",
  source="advisor", positions=3)

J("job-polku-bike", "emp-polku", "Bike mechanic — spring and summer", "seasonal",
  "tapiola", "Länsituulentie 2", 14.0, "hour",
  ["Repair and service bikes and e-bikes.",
   "Prepare rental bikes each morning.",
   "Help customers choose parts."],
  sh("tue-sat", "10:00", "18:00"), (20, 37.5), "seasonal", "some",
  "A trial day in the workshop.",
  [L("English", "B1", "serve customers"), L("Finnish", "A2", "serve customers (nice to have)")],
  "What bikes have you fixed?", 9,
  C(sfe="y", seated=("y", "Stool at the repair stand."), breaks="y"),
  lifting="Bikes up to 25 kg", pay_note="April–September.")

# --- logistics and driving ----------------------------------------------------

J("job-routa-delivery", "emp-routa", "Delivery driver (C licence)", "logistics",
  "kauklahti", "Lasihytti 5", 17.2, "hour",
  ["Drive a 12-tonne truck on regional routes.",
   "Load with a tail lift; deliver to shops and building sites.",
   "Scan deliveries with a hand scanner."],
  sh("mon-fri", "06:00", "14:30"), (37.5, 37.5), "permanent", "required",
  "Two days as co-driver on your routes.",
  [L("Finnish", "A2", "talk with receivers"), L("English", "B1", "talk with dispatch")],
  "Tell me about your driving experience with trucks.", 3,
  C(written="y"),
  quals=["C driving licence", "Driver's professional competence (ammattipätevyys)",
         "Digital tachograph card"],
  lifting="Parcels up to 25 kg; pallet jack for pallets")

J("job-routa-picker", "emp-routa", "Warehouse picker — evenings", "logistics",
  "kauklahti", "Lasihytti 5", 14.0, "hour",
  ["Pick orders with a hand scanner.",
   "Wrap and label pallets for the morning trucks.",
   "Count stock on Fridays."],
  sh("mon-fri", "15:00", "23:00"), (30, 37.5), "permanent", "none",
  "One shift with a picker; scanner instructions in five languages.",
  [L("Finnish", "A1", "basic words"), L("English", "A2", "read scanner screens")],
  "Can you work every weekday evening?", 2,
  C(written=("y", "Scanner screens in Finnish, English, Russian, Estonian and Arabic."),
    seated="n", breaks="n"),
  lifting="Boxes up to 20 kg", pay_note="Evening supplement +1.20 €/h.", positions=3)

J("job-routa-weekend", "emp-routa", "Warehouse picker — weekends, 8–16 h", "logistics",
  "kauklahti", "Lasihytti 5", 14.0, "hour",
  ["Pick and pack web-shop orders.", "Help unload containers."],
  sh("sat,sun", "08:00", "16:00"), (8, 16), "permanent", "none",
  "One training shift.",
  [L("English", "A2", "read scanner screens")],
  "One or both weekend days?", 5,
  C(seated="n"),
  lifting="Boxes up to 20 kg", pay_note="Sunday work paid double.")

J("job-routa-forklift", "emp-routa", "Forklift driver", "logistics",
  "kauklahti", "Lasihytti 5", 15.4, "hour",
  ["Unload and load trucks with a counterbalance forklift.",
   "Put pallets away to high racks with a reach truck.",
   "Keep the yard safe."],
  sh("mon-fri", "06:00", "14:00") + sh("mon-fri", "14:00", "22:00"), (37.5, 37.5),
  "permanent", "some",
  "Two days learning our racks and safety routes.",
  [L("Finnish", "A2", "talk with drivers"), L("English", "A2", "talk with drivers")],
  "How long have you driven a forklift and which types?", 7,
  C(seated=("y", "You sit in the forklift most of the shift.")),
  quals=["Forklift card (trukkikortti)"], lifting="Mostly machine lifting",
  pay_note="Two shifts, rotating weekly.")

J("job-routa-van", "emp-routa", "Van driver (B licence) — gig work", "logistics",
  "kauklahti", "Lasihytti 5", 15.0, "hour",
  ["Deliver parcels with a company van.",
   "Use the route app; photograph each delivery."],
  [], (0, 25), "gig", "none",
  "One ride-along day.",
  [L("English", "A2", "use the route app"), L("Finnish", "A1", "greet customers")],
  "Which days are you usually free?", 11,
  C(), flexible=1, quals=[BLIC], lifting="Parcels up to 20 kg")

J("job-lahilinja-bus", "emp-lahilinja", "Bus driver", "logistics",
  "kauklahti", "Kauklahdentie 40", 16.1, "hour",
  ["Drive local bus routes in west Espoo.",
   "Help passengers with prams and wheelchairs.",
   "Check the bus before and after your shift."],
  sh("mon-fri", "05:30", "13:30") + sh("mon-fri", "13:30", "21:30") + sh("sat,sun", "08:00", "16:00"),
  (30, 37.5), "permanent", "required",
  "Route training on each line before you drive alone.",
  [L("Finnish", "B1", "answer passenger questions and talk with traffic control"),
   L("Swedish", "A2", "help Swedish-speaking passengers (nice to have)")],
  "Tell me how you handle a stressful situation in traffic.", 4,
  C(seated="y", toilet=("y", "Staff toilets at route end stops."), breaks="n"),
  quals=["D driving licence", "Driver's professional competence (ammattipätevyys)"],
  pay_note="Rotating shift list; evening, Saturday and Sunday supplements.",
  positions=4)

J("job-lahilinja-trainee", "emp-lahilinja", "Bus driver trainee — we pay your D licence", "logistics",
  "kauklahti", "Kauklahdentie 40", 12.8, "hour",
  ["Take the D licence and professional competence training paid by us.",
   "Practise driving with an instructor.",
   "Work as a driver after you qualify (2-year commitment)."],
  sh("mon-fri", "08:00", "16:00"), (37.5, 37.5), "traineeship", "none",
  "About 4 months of training with pay.",
  [L("Finnish", "B1", "pass the theory test in Finnish or Swedish")],
  "Why would you like to drive a bus?", 12,
  C(),
  quals=[BLIC + " held for at least 1 year"])

J("job-apaja-taxi", "emp-apaja", "Transport service driver (taxi)", "logistics",
  "leppavaara", "Hevosenkenkä 3", 15.3, "hour",
  ["Drive older and disabled passengers with an accessible taxi.",
   "Help passengers in and out; secure wheelchairs.",
   "Trips booked through the app — no street hailing."],
  sh("mon-fri", "07:00", "15:00") + sh("mon-fri", "15:00", "23:00"), (20, 37.5),
  "permanent", "some",
  "Wheelchair-securing training and two days with a driver.",
  [L("Finnish", "B1", "talk with passengers"), L("Swedish", "A2", "greet Swedish-speaking passengers")],
  "Tell me about a time you helped someone who needed extra time.", 6,
  C(seated="y", breaks="y"),
  quals=["Taxi driver's licence (taksinkuljettajan ajolupa)", BLIC],
  lifting="Helping passengers; wheelchairs with a ramp")

J("job-apaja-school", "emp-apaja", "School transport driver — mornings and afternoons", "logistics",
  "leppavaara", "Hevosenkenkä 3", 15.3, "hour",
  ["Drive pupils to and from school in a minibus.",
   "Same route and children every day."],
  sh("mon-fri", "07:00", "09:00") + sh("mon-fri", "13:00", "16:00"), (20, 25),
  "fixed_term", "some",
  "You drive the route once with the previous driver.",
  [L("Finnish", "B1", "talk with children and parents")],
  "Have you worked with children?", 9,
  C(seated="y"),
  quals=["Taxi driver's licence (taksinkuljettajan ajolupa)", BLIC,
         "Criminal record extract for work with children"],
  pay_note="School year August–June; split shift.")

# --- health care --------------------------------------------------------------

J("job-kuura-rn", "emp-kuura", "Registered nurse (sairaanhoitaja)", "health",
  "leppavaara", "Leppävaarankatu 7", 3150, "month",
  ["Nurse appointments: vaccinations, wound care, blood pressure follow-up.",
   "Assist doctors in small procedures.",
   "Phone and chat advice to patients."],
  sh("mon-fri", "08:00", "16:00"), (37.5, 37.5), "permanent", "some",
  "Two-week orientation with a named mentor nurse.",
  [L("Finnish", "B2", "advise patients and write patient records"),
   L("Swedish", "B1", "serve Swedish-speaking patients (bonus)")],
  "What kind of nursing work do you enjoy most and why?", 2,
  C(sfe="y", lift="y", toilet="y", seated=("y", "Desk and stool in every nurse room."),
    breaks="n", quiet="y", written="y", adjust="y"),
  quals=[VALVIRA + " as a registered nurse"],
  exp_note="New graduates welcome; 1 year of experience is a plus.", cv=1)

J("job-kuura-rn-evening", "emp-kuura", "Registered nurse — evening and Saturday clinic", "health",
  "leppavaara", "Leppävaarankatu 7", 24.5, "hour",
  ["Nurse appointments in the evening clinic.",
   "Triage walk-in patients."],
  sh("tue,thu", "16:00", "21:00") + sh("sat", "09:00", "15:00"), (10, 16), "permanent", "some",
  "One orientation shift.",
  [L("Finnish", "B2", "advise patients")],
  "Which evenings fit you?", 14,
  C(sfe="y", lift="y"),
  quals=[VALVIRA + " as a registered nurse"],
  pay_note="Evening and Saturday supplements included in the hourly pay.")

J("job-kuura-pn", "emp-kuura", "Practical nurse (lähihoitaja) — clinic", "health",
  "leppavaara", "Leppävaarankatu 7", 2580, "month",
  ["Prepare treatment rooms and instruments.",
   "Take blood samples and ECGs after training.",
   "Book follow-up appointments."],
  sh("mon-fri", "07:30", "15:30"), (37.5, 37.5), "permanent", "none",
  "Sampling training in your first two weeks.",
  [L("Finnish", "B1", "talk with patients")],
  "Tell me about your practical nurse studies or work.", 5,
  C(sfe="y", lift="y", toilet="y"),
  quals=[VALVIRA + " as a practical nurse"])

J("job-kuura-lab", "emp-kuura", "Laboratory nurse — mornings", "health",
  "leppavaara", "Leppävaarankatu 7", 2850, "month",
  ["Take blood samples from 07:00 when the lab opens.",
   "Send samples to the central lab and record them."],
  sh("mon-fri", "07:00", "13:00"), (30, 30), "fixed_term", "some",
  "One week with the lab nurse.",
  [L("Finnish", "B1", "talk with patients"), L("English", "B1", "serve English-speaking patients")],
  "How much venipuncture experience do you have?", 22,
  C(seated="y"),
  quals=[VALVIRA + " (biomedical laboratory scientist or nurse)"],
  pay_note="Part-time 30 h/week, monthly pay shown for full-time equivalent.")

J("job-kuura-reception", "emp-kuura", "Clinic receptionist", "customer_service",
  "leppavaara", "Leppävaarankatu 7", 2350, "month",
  ["Check in patients and take payments.",
   "Answer the phone and book appointments.",
   "Keep the waiting room tidy."],
  sh("mon-fri", "07:30", "15:30") + sh("mon-fri", "12:00", "20:00"), (37.5, 37.5),
  "permanent", "none",
  "Booking system training in the first week.",
  [L("Finnish", "B2", "serve patients on the phone"), L("English", "B1", "serve patients"),
   L("Swedish", "A2", "greet patients (nice to have)")],
  "Tell me about a time you served a stressed customer.", 3,
  C(sfe="y", lift="y", toilet="y", seated="y", assist="y", quiet="n"),
  pay_note="Morning and evening shifts in turns.")

J("job-hymy-dental", "emp-hymy", "Dental assistant", "health",
  "tapiola", "Tapionaukio 5", 2480, "month",
  ["Assist the dentist chair-side.",
   "Clean and sterilise instruments.",
   "Prepare materials and keep patient records."],
  sh("mon-fri", "08:00", "16:00"), (37.5, 37.5), "permanent", "some",
  "Two weeks with our senior assistant.",
  [L("Finnish", "B1", "talk with patients")],
  "What do you know about infection control in dental work?", 8,
  C(sfe="y", lift="y", toilet="y", seated="y"),
  quals=["Dental assistant qualification (hammashoitaja) or practical nurse with dental studies"])

J("job-hymy-apprentice", "emp-hymy", "Dental assistant apprentice", "health",
  "tapiola", "Tapionaukio 5", 2100, "month",
  ["Learn sterilisation and chair-side work.",
   "Study for the qualification through an apprenticeship (oppisopimus)."],
  sh("mon-fri", "08:00", "16:00"), (37.5, 37.5), "traineeship", "none",
  "A named mentor for the whole training.",
  [L("Finnish", "B1", "talk with patients and study")],
  "Why does dental care interest you?", 27,
  C(sfe="y", lift="y"))

J("job-kaisla-pharmacy", "emp-kaisla", "Pharmacy assistant (tekninen apulainen)", "health",
  "espoonlahti", "Espoonlahdenkatu 4", 14.9, "hour",
  ["Unpack deliveries and fill shelves.",
   "Serve customers at the self-care products till.",
   "Collect prescription orders for the pharmacists."],
  sh("mon-fri", "12:00", "20:00") + sh("sat", "10:00", "18:00"), (20, 30), "permanent", "some",
  "A week with a colleague; product training online.",
  [L("Finnish", "B1", "serve customers"), L("Swedish", "B1", "serve Swedish-speaking customers (welcome)")],
  "Tell me about your customer service experience.", 6,
  C(sfe="y", lift="y", toilet="y", seated="n"),
  lifting="Boxes up to 10 kg", pay_note="Evening and Saturday supplements.")

# --- care work ----------------------------------------------------------------

J("job-kaste-pn", "emp-kaste", "Practical nurse — home care", "care",
  "espoon_keskus", "Kirkkojärventie 8", 2720, "month",
  ["Visit older clients at home: medication, wound care, meals.",
   "Drive between clients with a company car.",
   "Write visit notes on a phone."],
  sh("mon-sun", "07:00", "15:00") + sh("mon-sun", "13:30", "21:00"), (30, 37.5),
  "permanent", "some",
  "Two weeks with a mentor on the same route.",
  [L("Finnish", "B1", "talk with clients and write visit notes")],
  "Tell me about a client or relative you have cared for.", 1,
  C(written="y", seated="n", adjust="y"),
  quals=[VALVIRA + " as a practical nurse", BLIC],
  lifting="Helping clients move; lifting aids at homes",
  pay_note="Rotating shifts; every third weekend.", positions=3)

J("job-kaste-homecare", "emp-kaste", "Home care worker (hoiva-avustaja)", "care",
  "espoon_keskus", "Kirkkojärventie 8", 14.6, "hour",
  ["Help clients with washing, dressing and meals.",
   "Cleaning and shopping help.",
   "Travel between clients by bus or e-bike."],
  sh("mon-fri", "07:00", "14:00"), (25, 35), "permanent", "none",
  "Paid care assistant training (hoiva-avustaja) during your first year.",
  [L("Finnish", "B1", "talk with clients")],
  "Why do you want to work with older people?", 4,
  C(),
  lifting="Helping clients stand — with support")

J("job-kaste-weekend", "emp-kaste", "Home care worker — weekends", "care",
  "espoon_keskus", "Kirkkojärventie 8", 14.6, "hour",
  ["Weekend visits: meals and medicine reminders.", "Keep clients company."],
  sh("sat,sun", "08:00", "14:00"), (12, 12), "permanent", "none",
  "Two training shifts with a colleague.",
  [L("Finnish", "B1", "talk with clients")],
  "Can you work every weekend?", 25,
  C(), pay_note="Sunday double pay.", source="advisor")

J("job-silta-evening", "emp-silta", "Personal assistant for a wheelchair user — evenings", "care",
  "niittykumpu", "Merituulentie 30", 13.9, "hour",
  ["Help a young man in a wheelchair with evening routines.",
   "Cooking, shopping and getting to hobbies.",
   "He tells you what he needs — you are his hands."],
  sh("mon-fri", "17:00", "21:00"), (20, 20), "permanent", "none",
  "Two evenings with the current assistant. No qualification needed.",
  [L("Finnish", "B1", "talk with the client")],
  "What would make you a good assistant for someone your age?", 3,
  C(sfe="y", lift="y", toilet="y", breaks="y"),
  lifting="Transfers with a ceiling lift; no heavy lifting",
  pay_note="Evening supplement included.")

J("job-silta-english", "emp-silta", "Personal assistant — English-speaking student", "care",
  "otaniemi", "Otakaari 20", 13.9, "hour",
  ["Assist a visually impaired university student on campus.",
   "Guide to lectures, read signs, help with lunch.",
   "Some note-taking."],
  sh("mon-thu", "09:00", "14:00"), (15, 20), "fixed_term", "none",
  "One week together with the current assistant.",
  [L("English", "B2", "talk and take notes"), L("Finnish", "A1", "not needed")],
  "Tell me about a time you helped someone get around or learn.", 9,
  C(sfe="y", lift="y", toilet="y", seated="y", breaks="y"),
  pay_note="Academic year, September–May.")

J("job-silta-swedish", "emp-silta", "Personal assistant — weekends, Swedish-speaking client", "care",
  "tapiola", "Itätuulenkuja 6", 14.1, "hour",
  ["Help an older woman with walking, shopping and cooking.",
   "Accompany her to church and concerts."],
  sh("sat,sun", "10:00", "16:00"), (12, 12), "permanent", "none",
  "Meet the client first over coffee.",
  [L("Swedish", "B1", "talk with the client"), L("Finnish", "A2", "small talk")],
  "What do you enjoy doing on weekends?", 8,
  C(sfe="y", lift="y"),
  lifting="Light support when walking")

# --- education ----------------------------------------------------------------

J("job-satakieli-teacher", "emp-satakieli", "Early childhood teacher (varhaiskasvatuksen opettaja)", "education",
  "olari", "Kuitinmäentie 22", 2950, "month",
  ["Plan and lead the pedagogy of a group of 3–5-year-olds.",
   "Work in a team with two childcare assistants.",
   "Parent meetings and early childhood education plans."],
  sh("mon-fri", "07:00", "15:00") + sh("mon-fri", "09:00", "17:00"), (37.5, 37.5),
  "permanent", "some",
  "Orientation week before you start with the group.",
  [L("Finnish", "B2", "talk with children and parents and write plans")],
  "Tell me about an activity that worked well with small children.", 4,
  C(sfe="y", toilet="y", seated="n", breaks="n", adjust="y"),
  quals=["Bachelor of Education (ECE) or Bachelor of Social Services with ECE teacher qualification",
         "Criminal record extract for work with children"])

J("job-satakieli-english", "emp-satakieli", "English-speaking ECE teacher — language-immersion group", "education",
  "olari", "Kuitinmäentie 22", 2950, "month",
  ["Lead an English-language group of 4–6-year-olds.",
   "Plan play-based English activities."],
  sh("mon-fri", "08:00", "16:00"), (37.5, 37.5), "permanent", "some",
  "Two weeks with our pedagogical lead.",
  [L("English", "C1", "teach children"), L("Finnish", "A2", "talk with colleagues and parents")],
  "How would you help a child who does not yet understand English?", 11,
  C(sfe="y", toilet="y"),
  quals=["Teacher qualification in early childhood education (degree recognised by the Finnish National Agency for Education)"])

J("job-satakieli-assistant", "emp-satakieli", "Childcare assistant (lastenhoitaja)", "education",
  "olari", "Kuitinmäentie 22", 2380, "month",
  ["Care for children in daily routines: meals, naps, outdoors.",
   "Support the teacher's activities."],
  sh("mon-fri", "07:00", "15:00") + sh("mon-fri", "09:30", "17:30"), (37.5, 37.5),
  "fixed_term", "none",
  "A buddy colleague for your first month.",
  [L("Finnish", "B1", "talk with children")],
  "What do you enjoy doing with children?", 7,
  C(seated="n"),
  quals=["Vocational qualification in education and guidance or practical nurse (or studying)",
         "Criminal record extract for work with children"],
  lifting="Lifting small children")

J("job-kuusikko-assistant", "emp-kuusikko", "School assistant (koulunkäynnin ohjaaja)", "education",
  "espoon_keskus", "Kirkkojärventie 34", 13.8, "hour",
  ["Support pupils with learning needs in class.",
   "Help in breaks and lunch.",
   "Work with the class teacher's plan."],
  sh("mon-fri", "08:00", "13:00"), (25, 25), "fixed_term", "some",
  "Meet the teacher and the pupils in August.",
  [L("Finnish", "B1", "help pupils with tasks"), L("Arabic", "B1", "support Arabic-speaking pupils (bonus)")],
  "Tell me about a time you helped a child learn something.", 10,
  C(sfe="y", lift="y", toilet="y"),
  quals=["Criminal record extract for work with children"],
  pay_note="School year August–May.")

J("job-kuusikko-club", "emp-kuusikko", "After-school club instructor", "education",
  "espoon_keskus", "Kirkkojärventie 34", 13.0, "hour",
  ["Run play, crafts and outdoor games for 1st–2nd graders.",
   "Serve a snack and make sure everyone is picked up."],
  sh("mon-fri", "12:30", "16:30"), (20, 20), "fixed_term", "none",
  "One afternoon alongside the club leader.",
  [L("Finnish", "B1", "talk with children and parents")],
  "What games or crafts could you run with children?", 13,
  C(sfe="y"),
  quals=["Criminal record extract for work with children"])

J("job-kuusikko-cook", "emp-kuusikko", "School cook — lunch kitchen", "restaurant",
  "espoon_keskus", "Kirkkojärventie 34", 14.4, "hour",
  ["Cook lunch for 400 pupils from set recipes.",
   "Prepare special diets.",
   "Wash up and clean the kitchen."],
  sh("mon-fri", "06:30", "14:30"), (37.5, 37.5), "permanent", "some",
  "Recipes and diet lists are written; a week with the head cook.",
  [L("Finnish", "A2", "read recipes and diet lists")],
  "Have you cooked in big quantities?", 6,
  C(written="y", seated="n"),
  quals=[HYG], lifting="Pots up to 15 kg; trolleys", pay_note="Holidays in summer.")

# --- restaurant and café ------------------------------------------------------

J("job-havu-cook", "emp-havu", "Cook", "restaurant",
  "leppavaara", "Leppävaarankatu 3", 15.3, "hour",
  ["Cook lunch buffet and à la carte dishes.",
   "Prepare ingredients and follow recipes.",
   "Keep the kitchen clean and do self-checks."],
  sh("mon-fri", "07:00", "15:00") + sh("thu-sat", "14:00", "22:00"), (30, 37.5),
  "permanent", "required",
  "Trial shift, then one week with the head chef.",
  [L("Finnish", "A2", "read orders"), L("English", "B1", "talk in the kitchen")],
  "What is your favourite dish to cook for 100 people?", 2,
  C(seated="n", breaks="n", quiet="n"),
  quals=[HYG, "Cook's vocational qualification or 2 years in a restaurant kitchen"],
  lifting="Pots and crates up to 15 kg", pay_note="Evening supplement after 18:00.")

J("job-havu-dish", "emp-havu", "Dishwasher — evenings", "restaurant",
  "leppavaara", "Leppävaarankatu 3", 12.9, "hour",
  ["Run the dish machine and wash pots.",
   "Take out rubbish and recycling.",
   "Clean the kitchen floor at closing."],
  sh("wed-sat", "16:00", "22:00"), (18, 24), "permanent", "none",
  "One shift with the kitchen porter.",
  [L("English", "A2", "talk with the cooks — Finnish not needed")],
  "Which evenings can you work?", 1,
  C(seated="n", written="y", sign=("y", "One of our cooks signs FinSL.")),
  lifting="Racks and crates up to 12 kg", pay_note="Evening supplement after 18:00.",
  positions=2)

J("job-havu-dish-weekend", "emp-havu", "Kitchen helper — weekends, 4–8 h a week", "restaurant",
  "leppavaara", "Leppävaarankatu 3", 12.9, "hour",
  ["Wash dishes and help prepare salads at weekend brunch."],
  sh("sat", "10:00", "14:00") + sh("sun", "10:00", "14:00"), (4, 8), "permanent", "none",
  "We show you everything on the first shift.",
  [L("English", "A2", "talk with the cooks"), L("Finnish", "A1", "basic words")],
  "Saturday, Sunday or both?", 9,
  C(), quals=[HYG + " within 3 months"], lifting="Crates up to 10 kg")

J("job-fornello-pizza", "emp-fornello", "Pizza baker", "restaurant",
  "espoonlahti", "Ulappakatu 6", 14.2, "hour",
  ["Make dough and stretch pizzas.",
   "Bake in a wood-fired oven.",
   "Keep the station clean."],
  sh("wed-sun", "15:00", "22:00"), (25, 35), "permanent", "some",
  "Two shifts with our pizzaiolo.",
  [L("English", "A2", "talk with colleagues"), L("Italian", "A2", "with the owner (nice to have)")],
  "How many pizzas an hour can you make?", 6,
  C(seated="n"),
  quals=[HYG], lifting="Flour sacks up to 25 kg", source="advisor")

J("job-pavut-barista", "emp-pavut", "Barista", "restaurant",
  "otaniemi", "Otakaari 1", 13.6, "hour",
  ["Make espresso drinks and filter coffee.",
   "Serve pastries and take payments.",
   "Talk with customers about our coffees."],
  sh("mon-fri", "09:00", "15:00"), (15, 30), "permanent", "some",
  "Barista training with our roaster in the first week.",
  [L("English", "B1", "serve students and staff — Finnish not needed")],
  "What coffee do you make best?", 3,
  C(sfe="y", lift="y", toilet="y", seated="n"),
  quals=[HYG], lifting="Milk crates up to 10 kg")

J("job-pavut-morning", "emp-pavut", "Barista — early mornings", "restaurant",
  "otaniemi", "Otakaari 1", 13.6, "hour",
  ["Open the café at 07:00 and bake croissants.", "Serve the morning rush."],
  sh("mon-fri", "06:30", "11:00"), (15, 22.5), "fixed_term", "none",
  "We train you on the espresso machine.",
  [L("English", "B1", "serve customers"), L("Finnish", "A2", "serve customers (nice to have)")],
  "Can you be here at 6:30 every weekday?", 12,
  C(sfe="y"), quals=[HYG])

J("job-laguuni-breakfast", "emp-laguuni", "Breakfast server", "restaurant",
  "otaniemi", "Keilaranta 8", 13.4, "hour",
  ["Fill the breakfast buffet and clear tables.",
   "Make coffee and greet guests."],
  sh("mon-fri", "06:00", "11:00") + sh("sat,sun", "07:00", "12:00"), (15, 25), "permanent", "none",
  "Two shifts with a colleague.",
  [L("English", "B1", "serve hotel guests"), L("Finnish", "A1", "greet guests")],
  "Tell me about a time you made a guest or customer happy.", 5,
  C(sfe="y", lift="y", toilet="y", seated="n"),
  lifting="Trays up to 8 kg")

# --- hotel, customer service, security ----------------------------------------

J("job-laguuni-reception", "emp-laguuni", "Hotel receptionist", "customer_service",
  "otaniemi", "Keilaranta 8", 14.6, "hour",
  ["Check guests in and out.",
   "Answer phone and e-mail bookings.",
   "Solve guests' problems — taxis, lost keys, restaurant tips."],
  sh("mon-sun", "07:00", "15:00") + sh("mon-sun", "15:00", "23:00"), (30, 37.5),
  "permanent", "some",
  "Two weeks of training in the booking system.",
  [L("English", "B2", "serve international guests"), L("Finnish", "B1", "serve Finnish guests"),
   L("Swedish", "A2", "greet Swedish guests (nice to have)")],
  "Tell me about a difficult customer you helped.", 2,
  C(sfe="y", lift="y", toilet="y", seated=("y", "Stools behind the desk."), assist="y"),
  pay_note="Rotating morning and evening shifts; weekend supplements.")

J("job-laguuni-night", "emp-laguuni", "Night receptionist", "customer_service",
  "otaniemi", "Keilaranta 8", 15.8, "hour",
  ["Look after the hotel at night: late check-ins, phone, security rounds.",
   "Night audit of the day's sales."],
  sh("sun-wed", "23:00", "07:00"), (30, 32), "permanent", "some",
  "Two nights with the current night receptionist.",
  [L("English", "B2", "serve guests"), L("Finnish", "B1", "serve guests")],
  "How do you stay alert on night shifts?", 20,
  C(seated="y", quiet="y"), pay_note="Night supplement included.")

J("job-laguuni-housekeeper", "emp-laguuni", "Hotel housekeeper", "cleaning",
  "otaniemi", "Keilaranta 8", 13.2, "hour",
  ["Clean and prepare guest rooms.",
   "Change bed linen and refill supplies.",
   "Report damage to the supervisor."],
  sh("mon-fri", "08:00", "14:00") + sh("sat,sun", "09:00", "15:00"), (20, 37.5),
  "permanent", "none",
  "A colleague works with you for the first 3 days; picture checklist for every room.",
  [L("English", "A2", "read the room list"), L("Finnish", "A1", "greet guests")],
  "When can you start?", 4,
  C(sfe="y", lift="y", seated="n", written="y", breaks="n"),
  lifting="Linen trolley; mattresses lifted in pairs", positions=3)

J("job-kulma-reception", "emp-kulma", "Receptionist — business centre", "customer_service",
  "tapiola", "Tapionaukio 2", 2380, "month",
  ["Greet visitors and hand out keys.",
   "Book meeting rooms; answer the phone.",
   "Order coffee and supplies."],
  sh("mon-fri", "08:00", "16:00"), (37.5, 37.5), "permanent", "none",
  "One week with the office manager.",
  [L("Finnish", "B1", "serve visitors"), L("English", "B2", "serve international tenants"),
   L("Swedish", "B1", "serve Swedish-speaking tenants (welcome)")],
  "Tell me why you would enjoy front-desk work.", 13,
  C(sfe="y", lift="y", toilet="y", seated="y", quiet="n", assist="y", adjust="y"))

J("job-kulma-office", "emp-kulma", "Office assistant", "office",
  "tapiola", "Tapionaukio 2", 2300, "month",
  ["Post, archiving and invoice scanning.",
   "Update tenant lists in Excel.",
   "Help the reception at lunchtime."],
  sh("mon-fri", "09:00", "15:00"), (30, 30), "fixed_term", "none",
  "Written step-by-step guides for every task.",
  [L("Finnish", "B1", "read and file letters")],
  "Which computer programs do you use?", 8,
  C(sfe="y", lift="y", toilet="y", seated="y", quiet="y", written="y", assist="y"),
  pay_note="Monthly pay shown for full-time; 30 h/week = about 1,840 €.")

J("job-vahti-guard", "emp-vahti", "Security guard", "customer_service",
  "leppavaara", "Hevosenkenkä 9", 15.6, "hour",
  ["Guard shopping centres and offices; patrol and respond to alarms.",
   "Help customers and staff.",
   "Write incident reports."],
  sh("mon-sun", "06:00", "14:00") + sh("mon-sun", "14:00", "22:00") + sh("mon-sun", "22:00", "06:00"),
  (20, 37.5), "permanent", "some",
  "Two weeks of site training with a senior guard.",
  [L("Finnish", "B1", "talk with the public and write reports"), L("English", "B1", "help visitors")],
  "Tell me about a situation you calmed down.", 3,
  C(seated="n", breaks="n"),
  quals=["Security guard card (vartijakortti)", "First aid EA1"],
  pay_note="Evening, night and weekend supplements.", positions=3)

J("job-vahti-event", "emp-vahti", "Event steward (järjestyksenvalvoja) — gig", "seasonal",
  "tapiola", "Tapionaukio 1", 15.0, "hour",
  ["Check tickets and bags at concerts and sports events.",
   "Guide crowds and help visitors."],
  [], (0, 20), "gig", "none",
  "Event briefing before every shift.",
  [L("Finnish", "A2", "guide visitors"), L("English", "B1", "guide visitors")],
  "Which weekends are you free?", 28,
  C(seated="n"),
  flexible=1, quals=["Crowd steward card (järjestyksenvalvojakortti)"])

# --- retail -------------------------------------------------------------------

J("job-kauppakulma-cashier", "emp-kauppakulma", "Cashier — evenings and weekends", "retail",
  "espoon_keskus", "Espoontori 2", 12.9, "hour",
  ["Serve customers at the till and self-checkouts.",
   "Help customers find products.",
   "Fill shelves when it is quiet."],
  sh("mon-fri", "16:00", "21:30") + sh("sat,sun", "12:00", "20:00"), (12, 24), "permanent", "none",
  "Till training on your first two shifts.",
  [L("Finnish", "A2", "serve customers"), L("English", "B1", "serve customers")],
  "Tell me about a time you served customers.", 1,
  C(sfe="y", toilet="y", seated=("y", "Cashier chairs at every till.")),
  pay_note="Evening and Sunday supplements (retail collective agreement).", positions=3)

J("job-kauppakulma-morning", "emp-kauppakulma", "Store worker — early mornings", "retail",
  "espoon_keskus", "Espoontori 2", 13.3, "hour",
  ["Unload deliveries and fill shelves before opening.",
   "Check use-by dates."],
  sh("mon-fri", "05:00", "10:00"), (20, 25), "permanent", "none",
  "One shift with the morning team.",
  [L("Finnish", "A1", "basic words"), L("English", "A2", "talk with the team")],
  "Can you start at 5 every morning?", 7,
  C(seated="n"),
  lifting="Crates up to 15 kg", pay_note="Early-morning supplement before 06:00.")

J("job-oravanpesa-sales", "emp-oravanpesa", "Sales assistant — home electronics", "retail",
  "matinkyla", "Piispansilta 11", 13.4, "hour",
  ["Advise customers on TVs, phones and appliances.",
   "Sell warranties and arrange deliveries.",
   "Keep shelves and displays tidy."],
  sh("mon-fri", "12:00", "20:00") + sh("sat", "10:00", "18:00"), (25, 37.5), "permanent", "some",
  "Product training online and a week with a colleague.",
  [L("Finnish", "B1", "advise customers"), L("English", "B1", "advise customers")],
  "Which product would you love to sell and why?", 4,
  C(sfe="y", lift="y", toilet="y", seated="n"),
  lifting="Boxes up to 15 kg", pay_note="Sales bonus monthly.")

J("job-oravanpesa-xmas", "emp-oravanpesa", "Christmas season sales assistant", "seasonal",
  "matinkyla", "Piispansilta 11", 13.1, "hour",
  ["Serve customers in the toy and gift departments.",
   "Wrap gifts and fill shelves.",
   "Work 20 November – 6 January."],
  sh("mon-fri", "15:00", "21:00") + sh("sat,sun", "10:00", "18:00"), (15, 30), "seasonal", "none",
  "Half-day training in November.",
  [L("Finnish", "A2", "serve customers"), L("English", "B1", "serve customers")],
  "Which days in December can you work?", 0,
  C(sfe="y", lift="y", toilet="y"),
  lifting="Boxes up to 10 kg", positions=6)

J("job-kielo-florist", "emp-kielo", "Florist", "retail",
  "leppavaara", "Leppävaarankatu 1", 13.6, "hour",
  ["Make bouquets and funeral arrangements.",
   "Care for plants and serve customers.",
   "Take phone and web-shop orders."],
  sh("tue-sat", "09:00", "17:00"), (30, 37.5), "permanent", "required",
  "A trial day.",
  [L("Finnish", "B1", "serve customers and take phone orders")],
  "Bring a photo of an arrangement you made.", 22,
  C(sfe="y", seated="n"),
  quals=["Florist vocational qualification or 2 years in a flower shop"],
  lifting="Water buckets up to 12 kg", source="advisor")

J("job-saksi-hair", "emp-saksi", "Hairdresser", "customer_service",
  "matinkyla", "Matinkatu 3", 2200, "month",
  ["Cuts, colouring and styling.",
   "Book your own appointments in the system.",
   "Sell hair care products."],
  sh("tue-fri", "10:00", "18:00") + sh("sat", "09:00", "15:00"), (30, 37.5), "permanent", "required",
  "Model day with the owner.",
  [L("Finnish", "B1", "talk with clients"), L("English", "B1", "talk with international clients")],
  "What kind of cuts do you specialise in?", 10,
  C(sfe="y", seated="n"),
  quals=["Hairdresser vocational qualification (parturi-kampaaja)"],
  pay_note="Guaranteed base pay + 40 % commission above target.", source="advisor")

# --- cleaning -----------------------------------------------------------------

J("job-helmi-office", "emp-helmi", "Office cleaner — early mornings", "cleaning",
  "niittykumpu", "Niittykummuntie 6", 13.0, "hour",
  ["Clean offices before staff arrive.",
   "Empty bins and refill kitchens.",
   "Use a small floor machine."],
  sh("mon-fri", "05:30", "09:30"), (20, 20), "permanent", "none",
  "Picture-based cleaning plan; a colleague trains you for 3 mornings.",
  [L("Finnish", "A1", "basic words"), L("English", "A2", "read the cleaning plan")],
  "Can you start at 5:30 on weekdays?", 2,
  C(sfe="y", lift="y", written="y", quiet="y", seated="n"),
  lifting="Buckets up to 8 kg")

J("job-helmi-sidejob", "emp-helmi", "Cleaner — side job, 4 h a week", "cleaning",
  "tapiola", "Länsituulentie 10", 13.0, "hour",
  ["Clean a small office every Tuesday and Thursday evening."],
  sh("tue,thu", "17:00", "19:00"), (4, 4), "permanent", "none",
  "One evening with the supervisor.",
  [L("English", "A2", "read the task list")],
  "Are Tuesdays and Thursdays good for you?", 6,
  C(quiet="y"), lifting=None)

J("job-helmi-site", "emp-helmi", "Construction site cleaner (rakennussiivous)", "cleaning",
  "espoon_keskus", "Kirkkojärventie 22", 13.6, "hour",
  ["Final cleaning of new apartments before handover.",
   "Wash windows, floors and kitchens."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "fixed_term", "some",
  "Site induction on day one.",
  [L("Finnish", "A2", "talk with the supervisor"), L("English", "A2", "talk with the supervisor")],
  "Have you done heavy cleaning before?", 5,
  C(seated="n"),
  quals=[SAFE], lifting="Machines up to 15 kg", positions=2)

# --- office -------------------------------------------------------------------

J("job-laskelma-accountant", "emp-laskelma", "Accountant", "office",
  "niittykumpu", "Merituulentie 34", 3350, "month",
  ["Bookkeeping and VAT returns for 40 small businesses.",
   "Monthly and annual closing.",
   "Answer client questions by e-mail and phone."],
  [], (37.5, 37.5), "permanent", "required",
  "Two weeks with a senior accountant; written process guides.",
  [L("Finnish", "B2", "talk with clients and read Finnish tax rules"),
   L("English", "B1", "serve English-speaking entrepreneurs")],
  "Which accounting software have you used?", 5,
  C(sfe="y", lift="y", toilet="y", seated="y", quiet="y", written="y", assist="y", breaks="y"),
  mode="hybrid", flexible=1,
  quals=["Degree or vocational qualification in business/accounting"],
  exp_note="2+ years of bookkeeping.", cv=1, pay_note="Hybrid: 2 office days a week.")

J("job-laskelma-payroll", "emp-laskelma", "Payroll specialist", "office",
  "niittykumpu", "Merituulentie 34", 3450, "month",
  ["Run monthly payroll for 60 client companies.",
   "Apply collective agreements and reporting to the Incomes Register.",
   "Answer employees' pay questions."],
  [], (37.5, 37.5), "permanent", "required",
  "Process training with our payroll lead.",
  [L("Finnish", "B2", "read collective agreements")],
  "What payroll systems and collective agreements do you know?", 14,
  C(seated="y", quiet="y"),
  mode="hybrid", flexible=1, exp_note="2+ years of payroll work.", cv=1)

J("job-laskelma-assistant", "emp-laskelma", "Accounting assistant — part-time", "office",
  "niittykumpu", "Merituulentie 34", 15.5, "hour",
  ["Scan and match receipts.", "Check bank entries."],
  [], (15, 20), "fixed_term", "none",
  "Written step-by-step guides.",
  [L("Finnish", "B1", "read receipts"), L("English", "B1", "talk with the team")],
  "Do you enjoy careful, precise work?", 14,
  C(seated="y", quiet="y", written="y"),
  mode="hybrid", flexible=1)

J("job-sanasilta-translator", "emp-sanasilta", "Translator (Finnish–English), freelance", "office",
  "tapiola", "Tapionaukio 4", 26.0, "hour",
  ["Translate public-service texts between Finnish and English.",
   "Proofread colleagues' translations.",
   "Use a translation memory tool."],
  [], (5, 25), "gig", "required",
  "A paid test translation and a style guide.",
  [L("Finnish", "C1", "translate"), L("English", "C2", "translate")],
  "Which kinds of texts do you translate best?", 7,
  C(seated="y", quiet="y", assist="y"),
  mode="remote", flexible=1,
  pay_note="Paid per word; about 26 €/h on average.", cv=1)

J("job-sanasilta-interpreter", "emp-sanasilta", "Community interpreter — Ukrainian and Russian", "office",
  "tapiola", "Tapionaukio 4", 30.0, "hour",
  ["Interpret at health, social and school appointments.",
   "Mostly phone and video; some on-site visits in Espoo."],
  [], (4, 25), "gig", "some",
  "Briefing on interpreter ethics.",
  [L("Ukrainian", "C1", "interpret"), L("Russian", "C1", "interpret"), L("Finnish", "B2", "interpret")],
  "Tell me about your interpreting experience.", 1,
  C(seated="y"),
  mode="hybrid", flexible=1, pay_note="Minimum 1 hour billed per assignment.")

# --- ICT and specialist -------------------------------------------------------

J("job-koodikallio-dev", "emp-koodikallio", "Software developer (TypeScript / Python)", "tech",
  "otaniemi", "Tekniikantie 14", 4600, "month",
  ["Build web apps for public-service clients.",
   "Write tests and review code.",
   "Work in a team of five with a designer."],
  [], (37.5, 37.5), "permanent", "required",
  "A buddy developer and a first small task in week one.",
  [L("English", "B2", "work in the team — Finnish not needed")],
  "Show us something you built (link or short description).", 3,
  C(sfe="y", lift="y", toilet="y", seated="y", quiet="y", assist="y", adjust="y", breaks="y"),
  mode="hybrid", flexible=1, exp_note="3+ years of professional development.", cv=1,
  pay_note="Range 3,800–5,200 € depending on experience.")

J("job-koodikallio-test", "emp-koodikallio", "Test engineer", "tech",
  "otaniemi", "Tekniikantie 14", 3750, "month",
  ["Plan and run tests; automate them with Playwright.",
   "Test accessibility (WCAG) with screen readers."],
  [], (37.5, 37.5), "permanent", "some",
  "Two weeks pairing with the QA lead.",
  [L("English", "B2", "work in the team"), L("Finnish", "B1", "test Finnish UI texts (bonus)")],
  "Tell me about a bug you were proud to find.", 10,
  C(seated="y", quiet="y", assist="y"),
  mode="hybrid", flexible=1, quals=["ISTQB Foundation (nice to have)"])

J("job-koodikallio-ux", "emp-koodikallio", "UX designer", "tech",
  "otaniemi", "Tekniikantie 14", 4100, "month",
  ["Interview users and test prototypes.",
   "Design in Figma with our design system.",
   "Work closely with developers."],
  [], (37.5, 37.5), "permanent", "required",
  "Portfolio walk-through with the team in week one.",
  [L("English", "B2", "work in the team"), L("Finnish", "B2", "run user interviews (strong plus)")],
  "Share a portfolio case and what you learned from users.", 6,
  C(seated="y", quiet="y"),
  mode="hybrid", flexible=1, cv=1)

J("job-datavirta-analyst", "emp-datavirta", "Data analyst", "tech",
  "leppavaara", "Perkkaantie 10", 3900, "month",
  ["Build sales dashboards for retail clients (Power BI).",
   "Write SQL queries and clean data.",
   "Present findings to clients."],
  [], (37.5, 37.5), "permanent", "some",
  "A month working with a senior analyst.",
  [L("English", "B2", "work in the team"), L("Finnish", "B1", "present to Finnish clients (plus)")],
  "Tell me about an analysis that changed a decision.", 4,
  C(seated="y", quiet="y", written="y"),
  mode="remote", flexible=1, quals=["SQL"])

J("job-datavirta-support", "emp-datavirta", "IT support specialist", "tech",
  "leppavaara", "Perkkaantie 10", 2750, "month",
  ["Help store staff by phone and remote tools.",
   "Set up laptops, phones and tills.",
   "Document fixes in the ticket system."],
  sh("mon-fri", "08:00", "16:00") + sh("mon-fri", "12:00", "20:00"), (37.5, 37.5),
  "permanent", "some",
  "Two weeks of shadowing on the help desk.",
  [L("Finnish", "B1", "help store staff by phone"), L("English", "B1", "write tickets")],
  "Tell me about a tech problem you solved for someone else.", 6,
  C(sfe="y", lift="y", toilet="y", seated="y", assist="y"),
  quals=["IT support vocational qualification or similar experience"])

J("job-datavirta-junior", "emp-datavirta", "Junior data engineer — traineeship", "tech",
  "leppavaara", "Perkkaantie 10", 2450, "month",
  ["Learn data pipelines with Python and SQL.", "Support analysts with data checks."],
  [], (37.5, 37.5), "traineeship", "none",
  "A 6-month programme with a mentor.",
  [L("English", "B2", "work in the team")],
  "What have you learned about data so far — courses, projects?", 9,
  C(seated="y"),
  mode="hybrid", flexible=1)

J("job-bioteekki-lab", "emp-bioteekki", "Laboratory technician", "tech",
  "otaniemi", "Tekniikantie 21", 2950, "month",
  ["Prepare and analyse food and water samples.",
   "Run analysers and record results in the LIMS.",
   "Follow ISO 17025 quality rules."],
  sh("mon-fri", "07:30", "15:30"), (37.5, 37.5), "permanent", "some",
  "Method training with written work instructions.",
  [L("Finnish", "B1", "read work instructions"), L("English", "B2", "read methods and reports")],
  "Which lab methods have you used?", 8,
  C(sfe="y", lift="y", toilet="y", seated="n", written="y"),
  quals=["Laboratory technician qualification or BSc in chemistry/biology"],
  lifting="Sample boxes up to 10 kg")

# --- seasonal, summer and gardening ---------------------------------------------

J("job-espoolive-staff", "emp-espoolive", "Festival staff — summer events", "seasonal",
  "tapiola", "Tapionaukio 1", 13.2, "hour",
  ["Sell drinks and merchandise.", "Guide visitors and keep areas clean."],
  sh("fri", "16:00", "23:00") + sh("sat", "12:00", "23:00"), (0, 20), "gig", "none",
  "Briefing before each event.",
  [L("English", "B1", "serve visitors"), L("Finnish", "A2", "serve visitors")],
  "Which summer weekends can you work?", 11,
  C(seated="n", toilet="y"),
  lifting="Crates up to 10 kg", positions=6, pay_note="June–August.")

J("job-espoolive-crew", "emp-espoolive", "Festival build crew", "seasonal",
  "tapiola", "Tapionaukio 1", 14.5, "hour",
  ["Build stages, fences and tents before events.", "Take them down after."],
  sh("thu,fri", "08:00", "16:00") + sh("sun", "22:00", "04:00"), (10, 30), "seasonal", "none",
  "Safety briefing and a crew lead for each build.",
  [L("English", "A2", "follow the crew lead")],
  "Are you used to physical outdoor work?", 29,
  C(),
  quals=[SAFE], lifting="Fence panels up to 25 kg — in pairs", positions=4)

J("job-kesaduuni-park", "emp-kesaduuni", "Summer job for youth — park helper (15–17)", "seasonal",
  "espoon_keskus", "Kirkkojärventie 2", 10.5, "hour",
  ["Pick litter, water plants and help the park team.",
   "Two weeks, 6 hours a day, in June."],
  sh("mon-fri", "08:00", "14:00"), (30, 30), "summer_job", "none",
  "The park team leader guides you every day.",
  [L("Finnish", "A2", "understand instructions"), L("English", "A2", "understand instructions")],
  "Why would you like a summer job — what do you want to learn?", 0,
  C(written="y", seated="n"),
  lifting="Watering cans and bags up to 10 kg", positions=10,
  pay_note="Two-week summer job; pay follows the fictional programme's flat rate.")

J("job-kesaduuni-library", "emp-kesaduuni", "Summer job for youth — library helper (15–17)", "seasonal",
  "matinkyla", "Suomenlahdentie 1", 10.5, "hour",
  ["Shelve books and help at summer reading events.", "Two weeks, 6 hours a day."],
  sh("mon-fri", "10:00", "16:00"), (30, 30), "summer_job", "none",
  "A librarian is your mentor.",
  [L("Finnish", "A2", "help visitors"), L("Swedish", "A2", "help visitors (welcome)")],
  "Which books, games or hobbies could you tell other kids about?", 2,
  C(sfe="y", lift="y", toilet="y", seated="y", quiet="y"),
  positions=4)

J("job-kesaduuni-sport", "emp-kesaduuni", "Summer job for youth — sports camp helper (15–17)", "seasonal",
  "espoonlahti", "Espoonlahdenkatu 10", 10.5, "hour",
  ["Help instructors at day camps for 7–10-year-olds.", "Lead games and keep kids safe."],
  sh("mon-fri", "09:00", "15:00"), (30, 30), "summer_job", "none",
  "One-day camp instructor course in May.",
  [L("Finnish", "B1", "talk with children"), L("English", "B1", "talk with children")],
  "What sports or games do you like?", 4,
  C(toilet="y"), positions=6)

J("job-kanerva-gardener", "emp-kanerva", "Gardener", "seasonal",
  "kalajarvi", "Lahnuksentie 44", 14.8, "hour",
  ["Plant, prune and mow in housing company yards.",
   "Build stone edges and small paths.",
   "Drive a ride-on mower."],
  sh("mon-fri", "07:00", "15:30"), (37.5, 37.5), "fixed_term", "some",
  "Machine training in April.",
  [L("Finnish", "A2", "talk with the team"), L("English", "A2", "talk with the team")],
  "What garden work have you done?", 13,
  C(seated="n", breaks="y"),
  quals=[BLIC + " (a plus)"], lifting="Soil bags and stones up to 25 kg",
  pay_note="April–October, possible snow work in winter.", positions=2)


# --- write --------------------------------------------------------------------


def _load(name):
    return json.loads((SEED_DIR / name).read_text(encoding="utf-8"))


def _dump(name, payload):
    (SEED_DIR / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                                 encoding="utf-8")


def validate(jobs, employers, catalog):
    fields = {f["id"] for f in catalog["fields"]}
    districts = {d["id"] for d in catalog["districts"]}
    contracts = set(catalog["contract_types"])
    levels = set(catalog["language_levels"])
    ckeys = {c["id"] for c in catalog["condition_keys"]}
    emp_ids = {e["id"] for e in employers}
    assert len(emp_ids) == len(employers), "duplicate employer id"
    assert len({j["id"] for j in jobs}) == len(jobs), "duplicate job id"
    for j in JOBS:                      # base jobs are not ours to judge
        jid = j["id"]
        assert j["employer_id"] in emp_ids, jid
        assert j["field"] in fields, (jid, j["field"])
        assert j["district"] in districts, jid
        assert j["contract"] in contracts, jid
        assert j["experience"] in ("none", "some", "required"), jid
        assert j["pay_unit"] in ("hour", "month"), jid
        assert j["work_mode"] in ("on_site", "hybrid", "remote"), jid
        assert j["source"] in ("employer", "advisor"), jid
        assert all(l["level"] in levels for l in j["languages"]), jid
        assert set(j["conditions"]) <= ckeys, jid
        assert j["hours_min"] <= j["hours_max"], jid
        assert 0 <= j["confirmed_days_ago"] <= 30, jid
        lat0, lon0 = DISTRICTS[j["district"]]
        assert abs(j["lat"] - lat0) < 0.01 and abs(j["lon"] - lon0) < 0.012, jid
        for s in j["shifts"]:
            assert s["day"] in DAYS, jid


def _rank(job_id: str) -> str:
    """Stable order per job id — no unseeded randomness."""
    return hashlib.md5(job_id.encode()).hexdigest()


def _assign_commitments(jobs: list[dict]) -> None:
    """Fair-hiring promises, deterministic by job id. Targets: ~12 open
    hiring, ~25 guaranteed talk, ~25 tryout, ~20 skills first."""
    def pick(pool: list[dict], n: int, first: list[dict] | None = None) -> set:
        chosen = [j["id"] for j in (first or [])]
        chosen += [j["id"] for j in sorted(pool, key=lambda j: _rank(j["id"]))
                   if j["id"] not in chosen][:n - len(chosen)]
        return set(chosen)

    open_eligible = [j for j in jobs
                     if j.get("experience") == "none"
                     and not j.get("qualifications")
                     and not j.get("cv_required")
                     and j["field"] in {"cleaning", "retail", "restaurant",
                                        "logistics", "seasonal",
                                        "manufacturing"}]
    tryout_eligible = [j for j in jobs
                       if j.get("contract") in ("permanent", "fixed_term")]
    welders = [j for j in tryout_eligible
               if "weld" in (j["title"] + " ".join(j.get("duties", []))).lower()]
    skills_eligible = [j for j in jobs if j.get("experience") != "none"]

    open_ids = pick(open_eligible, 12)
    talk_ids = pick(jobs, 25)
    tryout_ids = pick(tryout_eligible, 25,
                      first=sorted(welders, key=lambda j: _rank(j["id"]))[:1])
    skills_ids = pick(skills_eligible, 20)

    for j in jobs:
        c = []
        if j["id"] in open_ids:
            c.append("open_hiring")
        if j["id"] in talk_ids:
            c.append("guaranteed_talk")
        if j["id"] in tryout_ids:
            c.append("tryout")
        if j["id"] in skills_ids:
            c.append("skills_first")
        j["commitments"] = c


def _assign_contracts(jobs: list[dict], catalog: dict) -> None:
    """Link open jobs to city-contract employers (työllistämisehto),
    deterministic by job id. 1-3 jobs per contract employer."""
    try:
        contracts = _load("procurement.json")
    except FileNotFoundError:
        return
    for j in jobs:
        j.pop("contract_id", None)
    for con in sorted(contracts, key=lambda c: c["id"]):
        pool = [j for j in jobs
                if j["employer_id"] == con["employer_id"]
                and j.get("status") in (None, "open")]
        if not pool:
            continue
        n = 1 + int(hashlib.md5(con["id"].encode()).hexdigest(), 16) % 3
        for j in sorted(pool, key=lambda x: _rank(x["id"]))[:n]:
            j["contract_id"] = con["id"]


def _fix_hours(jobs: list[dict]) -> None:
    """Make listed shift times consistent with stated hours, deterministically.
    alt days or rota-like totals -> rota=1; otherwise model the unpaid break
    or shorten shifts; lower stated hours when shifts genuinely total less."""
    DAY_MIN = 24 * 60

    def _m(t: str) -> int:
        h, m = t.split(":")
        return int(h) * 60 + int(m)

    def _fmt(m: int) -> str:
        m %= DAY_MIN
        return f"{m // 60:02d}:{m % 60:02d}"

    def _per_day(shifts: list[dict]) -> dict:
        best: dict[str, int] = {}
        for sh in shifts:
            dur = (_m(sh["end"]) - _m(sh["start"])) % DAY_MIN
            if dur > best.get(sh["day"], 0):
                best[sh["day"]] = dur
        return best

    def _effective(j: dict) -> float:
        """Weekly paid hours implied by shifts minus the unpaid break."""
        per = _per_day(j["shifts"])
        return sum(per.values()) / 60.0 - len(per) * j["break_min"] / 60.0

    rota = broke = shortened = lowered = 0
    for j in jobs:
        prev_break = j.get("break_min", 0)
        j["break_min"] = prev_break          # idempotent: keep explicit
        j["rota"] = j.get("rota", 0)
        shifts = j.get("shifts") or []
        if not shifts or j.get("schedule_flexible"):
            j["rota"] = 0
            j["break_min"] = 0
            continue
        per = _per_day(shifts)
        days = len(per)
        alt = len(shifts) > days
        tot = sum(per.values()) / 60.0
        hmax = j.get("hours_max")
        hmin = j.get("hours_min")
        if hmax is None:
            hmax = tot
        if hmin is None:
            hmin = hmax
        if j["rota"] or alt or tot - hmax > 1.0 * days + 0.01:
            j["rota"] = 1
            j["break_min"] = 0
            rota += 1
            continue
        j["rota"] = 0
        # already consistent from a previous run -> keep as is
        if hmin - 0.01 <= _effective(j) <= hmax + 0.01:
            continue
        excess = tot - hmax
        if excess <= 0.01:
            j["break_min"] = 0
            if tot < hmin - 0.01:
                j["hours_min"] = j["hours_max"] = round(tot, 2)
                lowered += 1
            continue
        e = excess / days
        if e <= 0.25 + 0.01:
            j["break_min"] = 15
        elif e <= 0.5 + 0.01:
            j["break_min"] = 30
        else:
            for sh in shifts:
                sh["end"] = _fmt(_m(sh["end"]) - 30)
            j["break_min"] = 30
            shortened += 1
        if j["break_min"]:
            broke += 1
    # consistency check for every non-rota fixed-shift job
    for j in jobs:
        if not j.get("shifts") or j.get("schedule_flexible") or j.get("rota"):
            continue
        lo = j["hours_min"] if j["hours_min"] is not None else j["hours_max"]
        eff = _effective(j)
        assert lo - 0.01 <= eff <= j["hours_max"] + 0.01, (
            f"{j['id']}: effective {eff:.2f} h outside "
            f"[{lo},{j['hours_max']}]")
    print(f"hours fix: {rota} rota, {broke} break-added, "
          f"{shortened} shortened, {lowered} hours-lowered")


def main():
    new_ids = {j["id"] for j in JOBS}
    new_emp_ids = {e[0] for e in EMPLOYERS}
    assert len(new_ids) == len(JOBS), "duplicate id in JOBS"

    jobs = [j for j in _load("jobs.json") if j["id"] not in new_ids]
    employers = [e for e in _load("employers.json") if e["id"] not in new_emp_ids]
    unlisted = _load("employers_unlisted.json")
    catalog = _load("catalog.json")

    clash = new_emp_ids & {e["id"] for e in unlisted}
    assert not clash, f"employer ids clash with employers_unlisted: {clash}"

    for f in NEW_FIELDS:
        if f["id"] not in {x["id"] for x in catalog["fields"]}:
            catalog["fields"].append(f)

    for i, (eid, name, about, contact) in enumerate(EMPLOYERS):
        employers.append({
            "id": eid, "name": name, "about": about, "contact_name": contact,
            "contact_email": f"info@{eid.split('emp-', 1)[1]}.example.com",
            "contact_phone": f"+358 40 000 {101 + i:04d}",
            "booth": None,
        })
    used = {j["employer_id"] for j in JOBS}
    assert used == new_emp_ids, f"employers without jobs: {new_emp_ids - used}"

    base_count = len(jobs)
    jobs.extend(JOBS)
    validate(jobs, employers + unlisted, catalog)
    _assign_commitments(jobs)
    _assign_contracts(jobs, catalog)
    _fix_hours(jobs)

    _dump("jobs.json", jobs)
    _dump("employers.json", employers)
    _dump("catalog.json", catalog)

    from collections import Counter
    counts = Counter(c for j in jobs for c in j["commitments"])
    print(f"commitments: {dict(counts)}")
    stale = sum(1 for j in jobs if j["confirmed_days_ago"] > 14)
    print(f"kept {base_count} base jobs, added {len(JOBS)} -> {len(jobs)} jobs")
    print(f"employers: {len(employers)} listed ({len(EMPLOYERS)} new), "
          f"{len(unlisted)} unlisted")
    print(f"stale (>14 days): {stale}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
