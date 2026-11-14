"""Runtime configuration: optional API keys + feature flags (spec v3 §0).

Reads a repo-root `.env` with a tiny parser (KEY=VALUE, no quoting) and the
process environment. Nothing here may log or return a secret — only flags.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> dict[str, str]:
    env: dict[str, str] = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


_ENV = {**_load_dotenv(), **os.environ}


def get(name: str, default: str = "") -> str:
    return _ENV.get(name, default)


def nvidia_api_key() -> str:
    return get("NVIDIA_API_KEY")


def nvidia_model() -> str:
    return get("NVIDIA_MODEL",
               "nvidia/nemotron-3.5-super-vl-120b-a12b")


def digitransit_api_key() -> str:
    return get("DIGITRANSIT_API_KEY")


def public_base_url() -> str:
    return get("PUBLIC_BASE_URL")


def ai_enabled() -> bool:
    return bool(nvidia_api_key())


def commute_enabled() -> bool:
    return bool(digitransit_api_key())


def demo_mode() -> bool:
    """Demo strip with one-click sign-in (env DEMO_MODE, default on)."""
    return get("DEMO_MODE") not in ("0", "false", "no")
