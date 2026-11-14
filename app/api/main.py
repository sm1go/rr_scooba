"""TalentMatch Signal MVP — FastAPI entry point.

Run:  uvicorn app.api.main:app --reload   (port 8000, API under /api)

On startup (or first request) the SQLite file db/talentmatch.sqlite is rebuilt
from db/schema.sql + db/seed/*.json if missing. Set TM_DB_PATH to override the
database location (tests use a temp file).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db as db_mod
from . import llm as llm_mod
from .routers import company, organiser, sparks, talent


@asynccontextmanager
async def lifespan(app: FastAPI):
    llm_mod.load_env()
    db_mod.ensure_db()
    yield


app = FastAPI(title="TalentMatch Signal", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(company.router, prefix="/api", tags=["company"])
app.include_router(talent.router, prefix="/api", tags=["talent"])
app.include_router(sparks.router, prefix="/api", tags=["sparks"])
app.include_router(organiser.router, prefix="/api", tags=["organiser"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
