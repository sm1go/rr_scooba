"""Authentication and authorisation helpers (spec section 3).

Passwords: hashlib.scrypt with a random 16-byte salt, stored as
`scrypt$<salt_hex>$<hash_hex>`, compared with hmac.compare_digest.
Sessions: `secrets.token_urlsafe(32)` bearer tokens in the `session` table.
Login never reveals whether an account exists — unknown login and wrong
password return the same 401 message.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from typing import Callable

from fastapi import Depends, Header, HTTPException

from .db import get_conn

SCRYPT_N = 2 ** 14
MIN_PASSWORD_LEN = 8


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N,
                            r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt_hex, hash_hex = stored.split("$", 2)
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex),
                                n=SCRYPT_N, r=8, p=1, dklen=32)
        return hmac.compare_digest(digest.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


def new_token() -> str:
    return secrets.token_urlsafe(32)


def find_user_by_login(conn: sqlite3.Connection, login: str):
    login = (login or "").strip()
    return conn.execute(
        "SELECT * FROM user WHERE lower(email)=lower(?) OR phone=?",
        (login, login)).fetchone()


def user_payload(row: sqlite3.Row, conn: sqlite3.Connection) -> dict:
    out = {"id": row["id"], "email": row["email"], "phone": row["phone"],
           "role": row["role"], "name": row["name"]}
    if row["role"] == "employer" and row["employer_id"]:
        emp = conn.execute("SELECT name FROM employer WHERE id=?",
                           (row["employer_id"],)).fetchone()
        out["employer_id"] = row["employer_id"]
        out["employer_name"] = emp["name"] if emp else ""
    return out


# --- FastAPI dependencies ------------------------------------------------------

def current_user(authorization: str | None = Header(default=None),
                 conn: sqlite3.Connection = Depends(get_conn)):
    """Resolve the bearer token to a user row or 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in to continue.")
    token = authorization.removeprefix("Bearer ").strip()
    row = conn.execute(
        "SELECT u.* FROM session s JOIN user u ON u.id = s.user_id"
        " WHERE s.token=?", (token,)).fetchone()
    if not row:
        raise HTTPException(401, "Sign in to continue.")
    return row


def optional_user(authorization: str | None = Header(default=None),
                  conn: sqlite3.Connection = Depends(get_conn)):
    """Same lookup, but returns None instead of 401 for anonymous callers."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    return conn.execute(
        "SELECT u.* FROM session s JOIN user u ON u.id = s.user_id"
        " WHERE s.token=?", (token,)).fetchone()


def require_role(role: str) -> Callable:
    def dep(user=Depends(current_user)):
        if user["role"] != role:
            raise HTTPException(403, "This is not available for your account.")
        return user
    return dep
