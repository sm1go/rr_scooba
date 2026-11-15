"""Espoo Work Map API (spec section 3). Synthetic data only."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import ensure_db
from .routers import (advisor, ai, auth, catalog, commute, demo, employer, event,
                      events,
                      jobs, resident)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_db()
    yield


app = FastAPI(title="Espoo Work Map API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(catalog.router)
app.include_router(jobs.router)
app.include_router(auth.router)
app.include_router(resident.router)
app.include_router(employer.router)
app.include_router(advisor.router)
app.include_router(ai.router)
app.include_router(commute.router)
app.include_router(event.router)
app.include_router(events.router)
app.include_router(demo.router)
