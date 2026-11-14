"""Small OpenAI-compatible chat client for the optional AI helpers (spec §0).

`NVIDIA_API_KEY` missing -> `LLMUnavailable`; callers use their rules-based
fallback. Tests inject a fake client via `set_client()` — no test may call
the network. Every AI call writes an audit row through `audit_cb`.
"""

from __future__ import annotations

import json
import re
import time

import requests

from . import settings

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
TIMEOUT = 60
TEMPERATURE = 0.1


class LLMUnavailable(Exception):
    """No key configured, or the service could not be reached."""


class LLMBadReply(Exception):
    """The service answered but the content was not usable JSON."""


def _extract_json(text: str) -> dict:
    """Lenient: accept a bare object, a fenced block, or the first {...}."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        text = m.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    raise LLMBadReply("The assistant did not return a JSON object.")


class NvidiaClient:
    """OpenAI-compatible chat completions against NVIDIA Build."""

    def __init__(self, base_url: str = NVIDIA_BASE,
                 api_key: str | None = None,
                 model: str | None = None):
        self.base_url = base_url
        self.api_key = api_key if api_key is not None else settings.nvidia_api_key()
        self.model = model or settings.nvidia_model()

    def chat(self, messages: list[dict]) -> dict:
        """messages: OpenAI chat message dicts (text and/or image_url parts).
        Returns the parsed JSON object from the assistant's reply."""
        if not self.api_key:
            raise LLMUnavailable("No NVIDIA_API_KEY configured.")
        payload = {"model": self.model, "temperature": TEMPERATURE,
                   "messages": messages,
                   "chat_template_kwargs": {"enable_thinking": False}}
        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        url = f"{self.base_url}/chat/completions"
        last_err: Exception | None = None
        for attempt in range(2):                     # one retry on 429/5xx
            try:
                r = requests.post(url, json=payload, headers=headers,
                                  timeout=TIMEOUT)
            except requests.RequestException as e:
                raise LLMUnavailable(f"AI service unreachable: {e}") from e
            if r.status_code in (429,) or r.status_code >= 500:
                last_err = LLMUnavailable(f"AI service error {r.status_code}")
                if attempt == 0:
                    time.sleep(1.5)
                    continue
                raise last_err
            if r.status_code >= 400:
                raise LLMUnavailable(f"AI service error {r.status_code}")
            try:
                content = r.json()["choices"][0]["message"]["content"]
            except (KeyError, IndexError, ValueError) as e:
                raise LLMBadReply("Unexpected AI service response shape.") from e
            return _extract_json(content or "")
        raise LLMUnavailable(str(last_err))


_client = None


def set_client(client) -> None:
    """Tests inject a fake here (must provide .chat(messages)->dict)."""
    global _client
    _client = client


def get_client():
    global _client
    if _client is None:
        _client = NvidiaClient()
    return _client


def chat(messages: list[dict], conn=None, action: str = "ai_call") -> dict:
    """One AI call + optional audit row (actor='ai'; never log personal text
    or images — detail is the action name + coarse metadata only)."""
    out = get_client().chat(messages)
    if conn is not None:
        from .db import audit
        audit(conn, "ai", action, "")
    return out
