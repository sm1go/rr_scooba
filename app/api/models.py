"""Pydantic request models for the Espoo Work Map API (spec section 3)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    role: Literal["resident", "employer"]
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str = Field(min_length=8)
    employer_name: Optional[str] = None


class LoginIn(BaseModel):
    login: str
    password: str


class ProfileIn(BaseModel):
    contact_method: Optional[Literal["phone", "sms", "email"]] = None
    district: Optional[str] = None
    fields: list[str] = []
    availability: list[str] = []
    max_hours_per_week: Optional[int] = None
    needs: list[str] = []
    languages: list[dict] = []
    about: str = ""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EmployerProfileIn(BaseModel):
    name: Optional[str] = None
    about: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""


class LanguageNeed(BaseModel):
    language: str
    level: str
    task: str = ""


class Shift(BaseModel):
    day: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    start: str
    end: str


class JobIn(BaseModel):
    title: str
    field: str = ""
    duties: list[str] = []
    address: str = ""
    district: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None
    work_mode: Literal["on_site", "hybrid", "remote"] = "on_site"
    pay_amount: Optional[float] = None
    pay_unit: Optional[Literal["hour", "month"]] = None
    pay_note: str = ""
    shifts: list[Shift] = []
    schedule_flexible: bool = False
    hours_min: Optional[int] = None
    hours_max: Optional[int] = None
    contract: Optional[Literal["permanent", "fixed_term", "seasonal", "gig",
                               "summer_job", "traineeship"]] = None
    experience: Optional[Literal["none", "some", "required"]] = None
    experience_note: str = ""
    qualifications: list[str] = []
    onboarding: str = ""
    languages: list[LanguageNeed] = []
    lifting: Optional[str] = None
    apply_question: str = ""
    cv_required: bool = False
    positions: int = 1
    status: Optional[Literal["draft", "open"]] = None   # None = keep / draft
    conditions: dict[str, Literal["yes", "no", "unknown"]] = {}
    employer_id: Optional[str] = None   # advisor posts for any employer


class WordingCheckIn(BaseModel):
    title: str = ""
    pay_note: str = ""
    experience_note: str = ""
    onboarding: str = ""
    apply_question: str = ""
    lifting: Optional[str] = ""
    duties: list[str] = []
    qualifications: list[str] = []
    languages: list[LanguageNeed] = []


class ApplicationIn(BaseModel):
    job_id: str
    contact_method: Literal["phone", "sms", "email"]
    contact_value: str
    availability_note: str = ""
    answer: str
    cv_text: Optional[str] = None
    shared_needs: list[str] = []
    meet_at_event: bool = False
    name: Optional[str] = None          # advisor applies for someone
    consent: Optional[bool] = None      # required true for advisor applies
    user_id: Optional[str] = None       # advisor may attach to an account


class StatusIn(BaseModel):
    status: Literal["interview", "offer", "not_selected"]
    status_note: str


class HelpRequestIn(BaseModel):
    job_id: Optional[str] = None
    kind: Literal["check_conditions", "prepare_application",
                  "arrange_contact", "other", "employer_support"]
    condition_keys: list[str] = []
    message: str = ""
    consent: bool
    name: Optional[str] = None
    contact_method: Optional[Literal["phone", "sms", "email"]] = None
    contact_value: Optional[str] = None


class HelpRequestUpdate(BaseModel):
    status: Literal["new", "in_progress", "done"]
    advisor_reply: str = ""


class ConditionCheckIn(BaseModel):
    key: str
    value: Literal["yes", "no"]
    note: str = ""


class EmployerNewIn(BaseModel):
    name: str
    about: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""


# --- v3 additions ------------------------------------------------------------

CONTENT_LANGUAGES = ["en", "fi", "sv", "ru", "ar", "et", "zh", "fa", "sq",
                     "uk"]


class JobDraftIn(BaseModel):
    image_base64: Optional[str] = None
    image_mime: Optional[Literal["image/jpeg", "image/png"]] = None
    text: Optional[str] = None


class FiltersIn(BaseModel):
    text: str = Field(max_length=600)
    ui_language: str = "en"


class SimplifyIn(BaseModel):
    job_id: str
    language: Literal["en", "fi", "sv", "ru", "ar", "et", "zh", "fa", "sq",
                      "uk"]


class AdvisorNoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class TalkIn(BaseModel):
    code: str = Field(pattern=r"^\d{4}$")


class TalkAnswerIn(BaseModel):
    outcome: Literal["next_step", "not_now"]
    employer_note: str = Field(min_length=1)
