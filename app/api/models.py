"""Pydantic models mirroring docs/03-product/api-contract.md shared types."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Band = Literal["fewer than 10", "10–19", "20–49", "50+"]
Cefr = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
Provider = Literal["mock", "nvidia", "gemma"]


class LanguageNeed(BaseModel):
    language: str
    level: Cefr
    task: str = ""
    from_when: str = ""


class Requirement(BaseModel):
    id: str
    text: str
    how_we_check: str = ""
    esco_uri: Optional[str] = None
    esco_label: Optional[str] = None


class ChallengeCard(BaseModel):
    id: str
    company_id: str
    title: str
    problem_90d: str
    must_haves: list[Requirement] = []
    nice_to_haves: list[str] = []
    languages: list[LanguageNeed] = []
    work_mode: str = ""
    status: Literal["draft", "approved"] = "draft"
    company_minutes_spent: int = 0


class LintHint(BaseModel):
    id: str
    rule: str
    trigger: str
    requirement_id: Optional[str] = None
    why: str
    law: Optional[str] = None
    suggestion: str
    pool_before: Band
    pool_after: Band


class Elasticity(BaseModel):
    requirement_id: str
    text: str
    band_without: Band


class Pool(BaseModel):
    band: Band
    elasticity: list[Elasticity] = []


class TraceStep(BaseModel):
    tool: str
    input: Any
    output_summary: str
    ms: int


EvidenceLevel = Literal["own words", "artefact", "witnessed live"]


class Claim(BaseModel):
    id: str
    text: str
    quote: str
    esco_uri: Optional[str] = None
    esco_label: Optional[str] = None
    evidence_level: EvidenceLevel = "own words"
    confirmed: bool
    original_language: str = "en"
    translated: bool = False


class RefusedClaim(BaseModel):
    text: str
    reason: str


class Language(BaseModel):
    language: str
    level: Cefr


class EvidenceCard(BaseModel):
    talent_id: str
    pseudonym: str
    headline: str
    claims: list[Claim] = []
    languages: list[Language] = []
    availability: str = ""


class Spark(BaseModel):
    id: str
    talent_id: str
    card_id: str
    claim_id: str
    requirement_id: str
    note: Optional[str] = None
    status: Literal["sent", "accepted", "declined", "refunded"] = "sent"
    deadline: str
    revealed_name: Optional[str] = None
    slot: Optional[str] = None


# --- request bodies -----------------------------------------------------------


class DraftRequest(BaseModel):
    company_id: str
    text: Optional[str] = None
    image_base64: Optional[str] = Field(default=None, max_length=12_000_000)


class LintRequest(BaseModel):
    card: ChallengeCard


class PoolRequest(BaseModel):
    card: ChallengeCard


class ApproveCardRequest(BaseModel):
    card: ChallengeCard


class FollowupsRequest(BaseModel):
    talent_id: str
    transcript: str
    language: str = "en"


class ExtractRequest(BaseModel):
    talent_id: str
    transcript: str
    language: str = "en"


class EvidenceRequest(BaseModel):
    claims: list[Claim]


class SparkRequest(BaseModel):
    talent_id: str
    card_id: str
    claim_id: str
    requirement_id: str
    note: Optional[str] = Field(default=None, max_length=140)


class RespondRequest(BaseModel):
    decision: Literal["accept", "decline"]
    reason_chip: Optional[str] = None


class Tick(BaseModel):
    requirement_id: str
    seen: bool
    note: Optional[str] = None


class TicksRequest(BaseModel):
    ticks: list[Tick]


class ClosureRequest(BaseModel):
    outcome: Literal["next_step", "not_now"]
    reason_chips: list[str] = []
    next_step: Optional[str] = None
    redirect_company_id: Optional[str] = None
