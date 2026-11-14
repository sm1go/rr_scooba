"""Requirement Reality Check (F02): a deterministic, non-blocking rulebook.

At most five hints. Each hint carries the legal reason (Non-Discrimination Act
1325/2014, Equality Act 609/1986) where relevant, a suggested rewrite, and the
pool band before/after applying that rewrite.
"""

from __future__ import annotations

import copy
import re
import sqlite3
from typing import Callable

from . import pool as pool_mod

NONDECR = "Non-Discrimination Act 1325/2014"
EQUALITY = "Equality Act 609/1986"


def _text_fields(card: dict):
    """Yield (field, requirement_id_or_None, text) for every wording surface."""
    yield "title", None, card.get("title", "")
    yield "problem_90d", None, card.get("problem_90d", "")
    for r in card.get("must_haves", []):
        yield "must_have", r["id"], r.get("text", "")
        yield "must_have", r["id"], r.get("how_we_check", "")
    for s in card.get("nice_to_haves", []):
        yield "nice_to_have", None, s


def _find(pattern: str, card: dict):
    rx = re.compile(pattern, re.I)
    for field, req_id, text in _text_fields(card):
        m = rx.search(text or "")
        if m:
            return m.group(0), req_id
    return None


def _fluent_language_need(card: dict) -> dict | None:
    """A language need set at near-native level with no stated task is the
    structured equivalent of writing 'fluent <language>'."""
    for need in card.get("languages", []):
        if need.get("level") in ("C1", "C2") and not need.get("task", "").strip():
            return need
    return None


def _language_rewrite(need_language: str) -> Callable[[dict], dict]:
    def apply(card: dict) -> dict:
        c = copy.deepcopy(card)
        for n in c.get("languages", []):
            if n["language"].lower() == need_language.lower():
                n["level"] = "B1"
                if not n.get("task", "").strip():
                    n["task"] = "customer calls"
                n["from_when"] = "by month 6"
        return c
    return apply


def _identity_rewrite(card: dict) -> dict:
    return card


# rule order is stable; the first five hits become the hints
RULES = [
    {
        "rule": "language_proxy",
        "why": "Asking for native-level language without naming the task screens "
               "out capable international talent and can mask origin-based "
               "discrimination.",
        "law": NONDECR,
        "suggestion": "Keep the team English-speaking; set Finnish at B1 for "
                      "customer calls by month 6 (course paid).",
    },
    {
        "rule": "nationality",
        "pattern": r"\b(citizenship|citizens?|nationality|nationals?)\b",
        "why": "Nationality or citizenship requirements discriminate on origin "
               "unless a law specifically demands them.",
        "law": NONDECR,
        "suggestion": "Remove it — ask only about the right to work in Finland.",
    },
    {
        "rule": "age_words",
        "pattern": r"\b(young|digital native|recent graduate|junior spirit|energetic team)\b",
        "why": "Age-coded words signal preference for a certain age group, which "
               "the law treats as discrimination.",
        "law": NONDECR,
        "suggestion": "Describe the team by what it does, not its age — e.g. "
                      "'a small team that ships weekly'.",
    },
    {
        "rule": "gendered_words",
        "pattern": r"\b(salesman|chairman|foreman|manpower|he will|she will|"
                   r"guys\b|ninja|rockstar)\b",
        "why": "Gendered or stereotype-coded words deter whole groups from "
               "applying.",
        "law": EQUALITY,
        "suggestion": "Use the neutral form — 'sales representative', 'the team', "
                      "'you'.",
    },
    {
        "rule": "photo",
        "pattern": r"\b(photo|picture|headshot)\b",
        "why": "Requesting a photo invites appearance- and origin-based bias "
               "before any evidence is seen.",
        "law": NONDECR,
        "suggestion": "Drop the photo request; evaluate evidence of skill instead.",
    },
    {
        "rule": "degree_without_reason",
        "pattern": r"\b(master'?s|bachelor'?s|degree|diploma|phd)\b",
        "why": "A degree requirement without a stated reason shrinks the pool "
               "and can indirectly discriminate where the degree is not needed "
               "for the task.",
        "law": NONDECR,
        "suggestion": "Name the skill the degree was meant to prove — e.g. "
                      "'can design a database schema' — and check that instead.",
    },
    {
        "rule": "no_gaps",
        "pattern": r"\bno (unexplained )?gaps|gap[- ]free|uninterrupted (career|cv|employment)\b",
        "why": "Demanding gap-free histories penalises parental leave, illness "
               "and migration — protected grounds.",
        "law": NONDECR,
        "suggestion": "Remove it; ask what the person can do now.",
    },
    {
        "rule": "cultural_fit",
        "pattern": r"\bcultural fit|fit(s|ting)? our culture|company culture fit|"
                   r"fit(s)? right in\b",
        "why": "'Culture fit' is an undefined proxy that replicates the existing "
               "team and hides bias.",
        "law": NONDECR,
        "suggestion": "Name the observable behaviour instead — e.g. 'writes "
                      "things down for the team'.",
    },
]


def lint_card(conn: sqlite3.Connection, card: dict, max_hints: int = 5) -> list[dict]:
    hints: list[dict] = []
    pool_before = pool_mod.band_for(pool_mod.count_pool(conn, card))

    def emit(rule, trigger, req_id, rewrite):
        after = pool_mod.band_for(pool_mod.count_pool(conn, rewrite(card)))
        hints.append({
            "id": f"hint-{len(hints) + 1:02d}-{rule['rule']}",
            "rule": rule["rule"], "trigger": trigger, "requirement_id": req_id,
            "why": rule["why"], "law": rule["law"],
            "suggestion": rule["suggestion"],
            "pool_before": pool_before, "pool_after": after,
        })

    for rule in RULES:
        if len(hints) >= max_hints:
            break
        if rule["rule"] == "language_proxy":
            # literal wording first, then the structured C1/C2-without-task check
            hit = _find(r"\b(native speaker|native[- ]level|mother[- ]?tongue|"
                        r"fluent\s+\w+)\b", card)
            if hit:
                trigger, req_id = hit
                lang = "Finnish"
                m = re.search(r"(finnish|swedish|english)", trigger, re.I)
                if m:
                    lang = m.group(1).capitalize()
                elif _fluent_language_need(card):
                    lang = _fluent_language_need(card)["language"]
                emit(rule, trigger, req_id, _language_rewrite(lang))
                continue
            need = _fluent_language_need(card)
            if need:
                emit(rule, f"{need['language']} {need['level']} with no stated task",
                     None, _language_rewrite(need["language"]))
            continue
        hit = _find(rule["pattern"], card)
        if hit:
            emit(rule, hit[0], hit[1], _identity_rewrite)
    return hints
