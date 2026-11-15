"""Espoo Work Map API (spec section 3). Synthetic data only."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

# Single-origin deploy: serve the built frontend from app/web/dist when it
# exists (Docker image). Dev runs Vite separately, so this stays inactive.
DIST = Path(__file__).resolve().parents[1] / "web" / "dist"
if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"),
              name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        if path.startswith("api/") or path == "api":
            raise HTTPException(404, "Not found")
        file = (DIST / path).resolve()
        if path and file.is_relative_to(DIST) and file.is_file():
            return FileResponse(file)          # favicon.svg, robots.txt, …
        return FileResponse(DIST / "index.html")
