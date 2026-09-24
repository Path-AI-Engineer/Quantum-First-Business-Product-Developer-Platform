"""Loopback-only read API; query calculations never write the evidence corpus."""

import os
from functools import lru_cache
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, PlainTextResponse

from venture_evidence.economics import EconomicsInput, economics
from venture_evidence.reporting import overview, thesis, verify_handoff
from venture_evidence.repository import ROOT, load_corpus, load_protocol
from venture_evidence.scoring import Scenario, compare

app = FastAPI(
    title="Quantum-First Venture Evidence Room",
    version="1.0.0",
    description="Local read-only analyst evidence. Zero buyer validation; handoff approval pending.",
)
allowed_hosts = [
    host.strip()
    for host in os.getenv("VENTURE_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",")
    if host.strip()
]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


@lru_cache(maxsize=1)
def room_snapshot() -> dict[str, Any]:
    return overview()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-read-only"}


@app.get("/api/room")
def room() -> dict[str, Any]:
    return room_snapshot()


@app.get("/api/score")
def score(
    scenario: Scenario = "base", dimension: str | None = None, multiplier: Annotated[float, Query(gt=0, le=5)] = 1.0
) -> dict[str, Any]:
    corpus, protocol = load_corpus(), load_protocol()
    if dimension and dimension not in {d.id for d in protocol.dimensions}:
        raise HTTPException(422, "Unknown dimension")
    rows = compare(corpus, protocol, scenario, {dimension: multiplier} if dimension else None)
    return {
        "scenario": scenario,
        "scores": [r.model_dump() for r in rows],
        "interpretation": "Analyst assumption intervals, not statistical confidence or demand validation",
    }


@app.get("/api/economics")
def calculate(inputs: Annotated[EconomicsInput, Query()]) -> dict[str, object]:
    return economics(inputs)


@app.get("/api/thesis", response_class=PlainTextResponse)
def download_thesis() -> PlainTextResponse:
    return PlainTextResponse(
        thesis(room_snapshot()), headers={"Content-Disposition": 'attachment; filename="company-thesis.md"'}
    )


@app.get("/api/handoff", response_class=FileResponse)
def download_handoff() -> FileResponse:
    try:
        verify_handoff()
    except (ValueError, OSError) as exc:
        raise HTTPException(409, "Candidate bundle missing or stale; run venture handoff export") from exc
    return FileResponse(
        ROOT / "reports/handoff/company-vision-v1.zip",
        media_type="application/zip",
        filename="company-vision-v1.zip",
    )
