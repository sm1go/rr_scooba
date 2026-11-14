"""Deterministic 'what are you looking for' parser (spec v3 §2 fallback).

English + Finnish keywords -> the same filter shape as FILTERS_SYSTEM.
Anything recognised goes to `filters`; recognised-but-unsettable and
unknown fragments go to `not_understood`.
"""

from __future__ import annotations

import re

DAYS = {"mon": ["monday", "mon", "maanantai", "maanantaina"],
        "tue": ["tuesday", "tue", "tiistai", "tiistaina"],
        "wed": ["wednesday", "wed", "keskiviikko", "keskiviikkona"],
        "thu": ["thursday", "thu", "torstai", "torstaina"],
        "fri": ["friday", "fri", "perjantai", "perjantaina"],
        "sat": ["saturday", "sat", "lauantai", "lauantaina"],
        "sun": ["sunday", "sun", "sunnuntai", "sunnuntaina"]}
PARTS = {"morning": ["morning", "mornings", "aamu", "aamulla", "aamuisin"],
         "afternoon": ["afternoon", "afternoons", "iltapäivä", "iltapaiva",
                       "iltapäivällä"],
         "evening": ["evening", "evenings", "ilta", "illalla", "iltaisin",
                     "night"]}
LABEL_WORDS = {
    "students": ["student", "students", "opiskelija", "opiskelijalle"],
    "retirement": ["retired", "retirement", "pension", "pensioner", "eläke",
                   "eläkkeellä", "eläkeläinen", "vanhus"],
    "first_job": ["first job", "no experience", "ensimmäinen työ",
                  "ei kokemusta"],
    "side_job": ["side job", "extra work", "lisätyö", "sivutyö"],
    "part_time": ["part-time", "part time", "osa-aikainen", "osa-aika",
                  "osaaika"],
    "near_station": ["near metro", "near a metro", "near the metro",
                     "near train", "near a train", "near station",
                     "near a station", "metroasema", "lähellä metro",
                     "lähellä asemaa", "aseman lähellä", "juna-asema",
                     "metro station"],
}
FIELD_WORDS = {
    "cleaning": ["cleaning", "cleaner", "siivous", "siivooja"],
    "retail": ["retail", "shop", "store", "kauppa", "myymälä", "kassa"],
    "restaurant": ["restaurant", "café", "cafe", "kitchen", "ravintola",
                   "kahvila", "keittiö"],
    "care": ["care", "care work", "nursing", "hoiva", "hoitotyö", "elderly"],
    "logistics": ["logistics", "driver", "driving", "warehouse", "kuljetus",
                  "kuljettaja", "varasto"],
    "office": ["office", "toimisto", "toimistotyö"],
    "customer_service": ["customer service", "customer", "asiakaspalvelu"],
    "education": ["education", "library", "school", "teaching", "kirjasto",
                  "koulu", "opetus", "päiväkoti", "daycare", "children",
                  "lapset", "lapsi"],
    "construction": ["construction", "rakennus", "maalari", "painter"],
    "tech": ["tech", "ict", "it ", "ohjelmisto", "tietotekniikka"],
    "seasonal": ["seasonal", "summer", "kesätyö", "kesätöitä", "summer job"],
}
DISTRICT_WORDS = {
    "leppavaara": ["leppävaara", "leppavaara"],
    "tapiola": ["tapiola"],
    "otaniemi": ["otaniemi"],
    "matinkyla": ["matinkylä", "matinkyla"],
    "olari": ["olari"],
    "niittykumpu": ["niittykumpu"],
    "espoon_keskus": ["espoon keskus", "espoo centre", "espoo center"],
    "espoonlahti": ["espoonlahti"],
    "kauklahti": ["kauklahti"],
    "kalajarvi": ["kalajärvi", "kalajarvi"],
}
NEED_WORDS = {
    "step_free_entrance": ["step-free", "step free", "wheelchair",
                           "esteetön sisäänkäynti", "pyörätuoli", "ramppi"],
    "lift": ["lift", "elevator", "hissi"],
    "accessible_toilet": ["accessible toilet", "esteetön wc"],
    "seated_work": ["seated", "sitting", "istuen", "istumatyö"],
    "flexible_breaks": ["breaks", "flexible breaks", "tauot", "tauko"],
    "quiet_environment": ["quiet", "hiljainen"],
    "written_instructions": ["written instructions", "kirjalliset ohjeet"],
    "sign_language_ok": ["sign language", "viittomakieli"],
    "assistive_tech_ok": ["assistive technology", "apuväline", "apuvälineet"],
    "adjustments_negotiable": ["adjustments", "mukautukset", "järjestelyt"],
}
REMOTE_WORDS = ["remote", "from home", "etätyö", "etänä", "kotoa"]
LIFTING_PAT = re.compile(
    r"(lift|lifting|heavy|nosta|nostaminen|raskas|raskaat)", re.I)


def parse(text: str) -> dict:
    """Free text -> {filters, explanation, not_understood}."""
    t = text.lower()
    filters: dict = {}
    expl: list[str] = []
    not_understood: list[str] = []
    slots: set[str] = set()

    days_hit = {d for d, words in DAYS.items()
                if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words)}
    parts_hit = {p for p, words in PARTS.items()
                 if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words)}
    weekend = re.search(r"\b(weekend|weekends|viikonloppu|viikonloppuisin)\b", t)
    weekdays = re.search(r"\b(weekday|weekdays|arkisin|arkipäivisin)\b", t)
    if weekend:
        days_hit |= {"sat", "sun"}
    a_week = re.search(r"\ba week\b|\bweekly\b|\bviikossa\b|\bviikossa\b",
                       t)
    if (weekdays or a_week) and not days_hit:
        days_hit |= {"mon", "tue", "wed", "thu", "fri"}
    if days_hit and parts_hit:
        slots = {f"{d}-{p}" for d in days_hit for p in parts_hit}
    elif days_hit:
        slots = {f"{d}-{p}" for d in days_hit
                 for p in ("morning", "afternoon", "evening")}
    elif parts_hit:
        # every day at those parts
        slots = {f"{d}-{p}" for d in DAYS for p in parts_hit}
    if weekend and not parts_hit:
        pass                                       # all weekend parts set
    if slots:
        filters["slots"] = sorted(slots)
        expl.append("Work times that match the days and times of day "
                    "you named.")

    labels = [lid for lid, words in LABEL_WORDS.items()
              if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words)]
    if "near_station" in labels:
        labels.remove("near_station")
        filters["near_station"] = True
        expl.append("Only jobs near a metro or train station.")
    if labels:
        filters["labels"] = labels
        expl.append("Job labels that match what you said.")

    for fid, words in FIELD_WORDS.items():
        if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words):
            filters["field"] = fid
            expl.append("The kind of work you named.")
            break
    for did, words in DISTRICT_WORDS.items():
        if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words):
            filters["district"] = did
            expl.append("The area you named.")
            break
    needs = [k for k, words in NEED_WORDS.items()
             if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words)]
    if needs:
        filters["needs"] = needs
        filters["needs_mode"] = "yes"
        expl.append("Working conditions you said you need.")
    if any(re.search(rf"\b{re.escape(w)}\b", t) for w in REMOTE_WORDS):
        filters["work_mode"] = "remote"
        expl.append("Remote work.")

    m = re.search(r"\b(\d{1,2})\s*(hours|h|tuntia|t)\b", t)
    if m:
        filters["hours_max"] = int(m.group(1))
        expl.append(f"At most {m.group(1)} hours a week.")
    if re.search(r"\bno experience\b|\bei kokemusta\b", t):
        filters["experience"] = "none"
        expl.append("Jobs that do not ask for experience.")

    if LIFTING_PAT.search(t):
        not_understood.append(
            "lifting: please check each job's lifting information")

    return {"filters": filters, "explanation": expl,
            "not_understood": not_understood}
