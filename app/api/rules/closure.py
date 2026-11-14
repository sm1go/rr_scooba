"""72-hour closure (F13) + incentives banner at the moment of intent (F14).

Reason chips must come from the meeting card's own requirements — never free
text. When the company moves to a next step, the support banner is shown so
nobody signs before the decision.
"""

from __future__ import annotations

SUPPORT_BANNER = ("Pay subsidy or other support may apply — "
                  "don't sign before the decision.")


class ChipError(ValueError):
    def __init__(self, invalid: list[str], allowed: list[str]):
        self.invalid = invalid
        self.allowed = allowed
        super().__init__(f"unknown reason chips: {invalid}")


def allowed_chips(card: dict) -> list[str]:
    chips: list[str] = []
    for r in card.get("must_haves", []):
        chips.extend([r["id"], r["text"]])
    return chips


def validate_chips(card: dict, chips: list[str]) -> None:
    allowed = allowed_chips(card)
    bad = [c for c in chips if c not in allowed]
    if bad:
        raise ChipError(bad, allowed)


def _chip_texts(card: dict, chips: list[str]) -> list[str]:
    """Resolve chip ids back to their requirement text for the message."""
    by_id = {r["id"]: r["text"] for r in card.get("must_haves", [])}
    return [by_id.get(c, c) for c in chips]


def build_message(company_name: str, talent_name: str | None, card: dict,
                  outcome: str, chips: list[str], next_step: str | None,
                  redirect_name: str | None) -> str:
    greet = f"Thank you for meeting {company_name}."
    if outcome == "next_step":
        msg = f"{greet} We'd like to move forward"
        if next_step:
            msg += f" — next step: {next_step}"
        return msg + "."
    reasons = _chip_texts(card, chips)
    msg = f"{greet} This time we are not moving forward."
    if reasons:
        joined = "; ".join(r.rstrip(".") for r in reasons)
        msg += f" The deciding requirement{'s were' if len(reasons) > 1 else ' was'}: {joined}."
    if redirect_name:
        msg += f" {redirect_name} is looking for adjacent skills — worth a visit."
    return msg


def support_banner_for(outcome: str) -> str | None:
    return SUPPORT_BANNER if outcome == "next_step" else None
