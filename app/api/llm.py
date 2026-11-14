"""LLM adapter + AI suggestion flows.

Provider by env LLM_PROVIDER = mock | nvidia | gemma (default and fallback:
mock — recorded outputs from db/seed/recorded/*.json). Remote providers are
called through an OpenAI-compatible HTTP API via `requests`:

  nvidia: https://integrate.api.nvidia.com/v1, model nvidia/nemotron-3.5-super-vl-120b-a12b,
          key NVIDIA_API_KEY (from .env, parsed here — never in code)
  gemma:  GEMMA_BASE_URL + /chat/completions, model GEMMA_MODEL

Every flow: try the configured provider; on any failure fall back to mock and
report provider "mock". The compiler's tool-using trace
(esco_search -> lint_requirements -> pool_preview -> submit_card) is always
produced by really running our deterministic tools.
"""

from __future__ import annotations

import copy
import json
import os
import re
import time
from pathlib import Path

import requests

from . import db as db_mod
from .rules import lint as lint_mod
from .rules import pool as pool_mod
from .rules import quote_guard

ROOT = Path(__file__).resolve().parents[2]
RECORDED_DIR = ROOT / "db" / "seed" / "recorded"
ESCO_FILE = ROOT / "db" / "esco" / "skills.json"

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"

PROVIDERS = ("mock", "nvidia", "gemma")


# --- tiny .env parser (no secrets in code) ------------------------------------

def load_env(path: Path | None = None) -> None:
    path = path or ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def provider() -> str:
    p = os.environ.get("LLM_PROVIDER", "mock").strip().lower()
    return p if p in PROVIDERS else "mock"


class LLMError(Exception):
    pass


def chat(messages: list[dict], temperature: float = 0.2, timeout: int = 45) -> str:
    """One chat completion against the configured remote provider."""
    p = provider()
    if p == "nvidia":
        key = os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise LLMError("NVIDIA_API_KEY not set")
        resp = requests.post(
            f"{NVIDIA_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"model": NVIDIA_MODEL, "messages": messages,
                  "temperature": temperature},
            timeout=timeout)
    elif p == "gemma":
        base = os.environ.get("GEMMA_BASE_URL", "").rstrip("/")
        if not base:
            raise LLMError("GEMMA_BASE_URL not set")
        resp = requests.post(
            f"{base}/chat/completions",
            json={"model": os.environ.get("GEMMA_MODEL", "gemma-3-27b-it"),
                  "messages": messages, "temperature": temperature},
            timeout=timeout)
    else:
        raise LLMError("provider is mock")
    if resp.status_code != 200:
        raise LLMError(f"{p} HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError(f"unexpected {p} response shape: {e}")


def _parse_json(text: str) -> dict:
    """Lenient JSON extraction from model output."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def _recorded(name: str) -> dict:
    return json.loads((RECORDED_DIR / name).read_text(encoding="utf-8"))


def _matches(payload: dict, text: str) -> bool:
    hay = (text or "").lower()
    return any(s.lower() in hay for s in payload.get("match_substrings", []))


# --- deterministic tools the compiler "calls" (real work, measured) -----------

def _load_esco() -> list[dict]:
    if ESCO_FILE.exists():
        return json.loads(ESCO_FILE.read_text(encoding="utf-8"))["skills"]
    return []


def esco_search(query: str) -> list[dict]:
    q = (query or "").lower()
    hits = []
    for s in _load_esco():
        if any(k in q for k in s["keywords"]) or any(
                k in s["label"] for k in q.split() if len(k) > 3):
            hits.append({"uri": s["uri"], "label": s["label"]})
    return hits


def _traced(trace: list, tool: str, tool_input, run):
    t0 = time.perf_counter()
    out = run()
    ms = int((time.perf_counter() - t0) * 1000)
    trace.append({"tool": tool, "input": tool_input, "ms": ms, "_out": out})
    return out


def _finish_trace(trace: list) -> list[dict]:
    steps = []
    for t in trace:
        out = t.pop("_out")
        if isinstance(out, list):
            summary = f"{len(out)} result(s)"
            if out and isinstance(out[0], dict) and "label" in out[0]:
                summary = f"{len(out)} skill(s): " + ", ".join(o["label"] for o in out[:4])
        elif isinstance(out, dict):
            if "band" in out:
                summary = f"pool band: {out['band']}"
            elif "id" in out:
                summary = f"stored card {out['id']} (status {out.get('status')})"
            else:
                summary = "ok"
        else:
            summary = str(out)[:120]
        steps.append({"tool": t["tool"], "input": t["input"],
                      "output_summary": summary, "ms": t["ms"]})
    return steps


# --- compiler -----------------------------------------------------------------

_COMPILER_SYSTEM = (
    "You are the Need Compiler of a recruitment-matchmaking event. Turn the "
    "pasted job ad into a draft Challenge Card as strict JSON with keys: "
    "title, problem_90d, must_haves (exactly 3 objects {id,text,how_we_check,"
    "esco_uri,esco_label}), nice_to_haves (strings), languages (objects "
    "{language,level A1..C2,task,from_when}), work_mode, followups (<=3 "
    "questions for the hiring manager). Never infer protected attributes. "
    "Use these ESCO-like skills only: {skills}. Respond with JSON only."
)


def _generic_card(company: dict, text: str) -> dict:
    """Deterministic compile for any company/ad without a recording."""
    esco = esco_search(text or "")
    reqs = []
    for i, s in enumerate(esco[:3], start=1):
        reqs.append({"id": f"reqg-{company['id']}-{i}",
                     "text": f"Has hands-on experience with {s['label']}",
                     "how_we_check": "Walk us through a concrete example from your own work",
                     "esco_uri": s["uri"], "esco_label": s["label"]})
    if not reqs:
        reqs = [{"id": f"reqg-{company['id']}-1",
                 "text": "Can show evidence for the main skill this role needs",
                 "how_we_check": "Ask them to walk through a concrete work example",
                 "esco_uri": None, "esco_label": None}]
    first_line = next((l.strip() for l in (text or "").splitlines() if l.strip()),
                      f"Challenge card — {company['name']}")
    return {
        "id": f"card-{company['id']}-draft", "company_id": company["id"],
        "title": first_line[:80], "problem_90d": (text or "")[:300],
        "must_haves": reqs, "nice_to_haves": [], "languages": [],
        "work_mode": "to be decided", "status": "draft",
        "company_minutes_spent": 0,
    }


GENERIC_FOLLOWUPS = [
    "What does success look like after 90 days?",
    "Which tasks need which language level, and from when?",
    "How will you check each must-have in a conversation?",
]


def compiler_draft(conn, company: dict, text: str | None,
                   image_base64: str | None) -> dict:
    """POST /api/compiler/draft flow. Returns the contract response dict."""
    p = provider()
    card, followups = None, None
    used_provider = "mock"

    if p != "mock":
        try:
            skills = ", ".join(f"{s['label']} ({s['uri']})" for s in _load_esco())
            user_content = text or "[image of a job ad attached]"
            if image_base64:
                if image_base64.startswith("data:"):
                    image_url = image_base64
                else:
                    image_url = f"data:image/png;base64,{image_base64}"
                user_content = [
                    {"type": "text", "text": text or "Read this job ad image."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            raw = chat([
                {"role": "system",
                 "content": _COMPILER_SYSTEM.format(skills=skills)},
                {"role": "user", "content": user_content},
            ])
            data = _parse_json(raw)
            card = {k: data[k] for k in
                    ("title", "problem_90d", "must_haves", "nice_to_haves",
                     "languages", "work_mode") if k in data}
            card.setdefault("must_haves", [])
            for i, r in enumerate(card["must_haves"], start=1):
                r.setdefault("id", f"req-{company['id']}-{i}")
            card.update({"id": f"card-{company['id']}-draft",
                         "company_id": company["id"], "status": "draft",
                         "company_minutes_spent": 0})
            card.setdefault("nice_to_haves", [])
            card.setdefault("languages", [])
            card.setdefault("work_mode", "")
            followups = data.get("followups", [])[:3] or GENERIC_FOLLOWUPS
            used_provider = p
        except Exception:
            p = "mock"
            card, followups = None, None

    if card is None:
        rec = _recorded("ad_lumo.json")
        if _matches(rec, text or "") or company["id"] == rec["company_id"]:
            card = copy.deepcopy(rec["card"])
            card["company_id"] = company["id"]
            followups = list(rec["followups"])
        else:
            card = _generic_card(company, text)
            followups = list(GENERIC_FOLLOWUPS)
        used_provider = "mock"

    # The tool-using flow is real in every provider mode.
    trace: list[dict] = []
    _traced(trace, "esco_search", {"query": (text or card["title"])[:120]},
            lambda: esco_search(text or card["title"]))
    hints = _traced(trace, "lint_requirements", {"card_id": card["id"]},
                    lambda: lint_mod.lint_card(conn, card))
    pool = _traced(trace, "pool_preview", {"card_id": card["id"]},
                   lambda: pool_mod.pool_preview(conn, card))
    _traced(trace, "submit_card", {"card_id": card["id"], "status": "draft"},
            lambda: _submit_draft(conn, card))

    return {"card": card, "followups": followups, "lint": hints, "pool": pool,
            "trace": _finish_trace(trace), "provider": used_provider}


def _submit_draft(conn, card: dict) -> dict:
    db_mod.save_card(conn, card)
    conn.commit()
    return card


# --- story interview ----------------------------------------------------------

_FOLLOWUP_SYSTEM = (
    "You interview a talent about work episodes. Given the transcript, ask at "
    "most 3 short follow-up questions that draw out concrete detail (numbers, "
    "their own part, what could have gone wrong). JSON: {\"questions\": [...]}."
)

_EXTRACT_SYSTEM = (
    "From this story transcript extract claims for an evidence card. Every "
    "claim MUST quote the person's exact words (verbatim substring of the "
    "transcript). Never inflate what was said. JSON: {\"claims\": [{\"id\","
    "\"text\",\"quote\",\"esco_uri\",\"esco_label\",\"confirmed\":true,"
    "\"original_language\",\"translated\"}]}."
)


def _generic_followups(transcript: str) -> list[str]:
    questions = []
    if re.search(r"\d", transcript or ""):
        questions.append("You mentioned numbers — can you say exactly what you changed?")
    questions += ["What was your own part in this, versus the team's?",
                  "Can you remember a time this went wrong — what did you do?"]
    return questions[:3]


def story_followups(talent_id: str, transcript: str, language: str) -> dict:
    p = provider()
    if p != "mock":
        try:
            raw = chat([{"role": "system", "content": _FOLLOWUP_SYSTEM},
                        {"role": "user", "content": transcript}])
            questions = _parse_json(raw).get("questions", [])[:3]
            if not questions:
                raise LLMError("empty questions")
            return {"questions": questions, "provider": p}
        except Exception:
            pass
    rec = _recorded("amira_story.json")
    if _matches(rec, transcript):
        return {"questions": list(rec["followups"])[:3], "provider": "mock"}
    return {"questions": _generic_followups(transcript), "provider": "mock"}


def _generic_claims(talent_id: str, transcript: str) -> list[dict]:
    esco = _load_esco()
    out, i = [], 0
    for sent in re.split(r"(?<=[.!?])\s+", transcript or ""):
        sent = sent.strip()
        if len(sent) < 25 or not (re.search(r"\d", sent) or " I " in f" {sent} "):
            continue
        i += 1
        match = next((s for s in esco if any(k in sent.lower()
                                           for k in s["keywords"])), None)
        out.append({
            "id": f"cl-{talent_id}-gen{i}", "text": sent, "quote": sent,
            "esco_uri": match["uri"] if match else None,
            "esco_label": match["label"] if match else None,
            "evidence_level": "own words", "confirmed": False,
            "original_language": "en", "translated": False,
        })
        if i >= 4:
            break
    return out


def story_extract(talent_id: str, transcript: str, language: str) -> dict:
    p = provider()
    proposed = None
    if p != "mock":
        try:
            raw = chat([{"role": "system", "content": _EXTRACT_SYSTEM},
                        {"role": "user", "content": transcript}])
            data = _parse_json(raw)
            proposed = data.get("claims", [])
            if not isinstance(proposed, list):
                raise LLMError("claims must be a list")
            proposed = [claim for claim in proposed if isinstance(claim, dict)]
            used_provider = p
        except Exception:
            proposed = None

    refused_extra: list[dict] = []
    if proposed is None:
        rec = _recorded("amira_story.json")
        if _matches(rec, transcript):
            proposed = copy.deepcopy(rec["claims"])
            refused_extra = list(rec.get("refused", []))
        else:
            proposed = _generic_claims(talent_id, transcript)
        used_provider = "mock"

    if not isinstance(proposed, list):
        proposed = []
    proposed = [claim for claim in proposed if isinstance(claim, dict)][:4]
    esco_by_uri = {s["uri"]: s["label"] for s in _load_esco()}
    for i, c in enumerate(proposed, start=1):
        c.setdefault("id", f"cl-{talent_id}-x{i}")
        c.setdefault("evidence_level", "own words")
        # Extraction is a proposal only. The person must explicitly confirm it.
        c["confirmed"] = False
        c.setdefault("original_language", language or "en")
        c.setdefault("translated", (language or "en") != "en")
        c.setdefault("esco_uri", None)
        c.setdefault("esco_label", None)
        if c["esco_uri"] not in esco_by_uri:
            c["esco_uri"] = None
            c["esco_label"] = None
        else:
            c["esco_label"] = esco_by_uri[c["esco_uri"]]
        c["original_language"] = language or "en"
        c["translated"] = (language or "en").lower() not in ("en", "english")

    claims, refused = quote_guard.guarded_extract(proposed, transcript)
    refused.extend(refused_extra)
    return {"claims": claims, "refused": refused, "provider": used_provider}
