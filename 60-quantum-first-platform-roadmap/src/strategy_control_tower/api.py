"""Read-mostly Control Tower API. Decision writes remain local simulations."""

from __future__ import annotations

from typing import Annotated, Any, cast

from fastapi import Body, FastAPI, HTTPException

from .engine import build_reports, capability_graph, reconcile_costs, scenario_run
from .repository import build_repository

app = FastAPI(title="Quantum-First Strategy Control Tower", version="1.0.0", openapi_version="3.1.0")
repository = build_repository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "revision": repository.revision}


@app.get("/v1/roadmap")
def roadmap() -> dict[str, Any]:
    return {
        "revision": repository.revision,
        "approval_status": repository.approval_status,
        "as_of": repository.as_of,
        "initiatives": [item.model_dump(mode="json") for item in repository.initiatives],
        "capability_graph": capability_graph(repository),
    }


@app.get("/v1/scenarios")
def scenarios() -> list[dict[str, Any]]:
    return [item.model_dump(mode="json") for item in repository.scenarios]


@app.post("/v1/scenarios/{scenario_id}/runs")
def run_scenario(scenario_id: str, shock_id: str | None = None) -> dict[str, Any]:
    try:
        return scenario_run(repository, scenario_id, shock_id)
    except StopIteration as error:
        raise HTTPException(status_code=404, detail="scenario or shock not found") from error


@app.get("/v1/initiatives")
def initiatives() -> list[dict[str, Any]]:
    return [item.model_dump(mode="json") for item in repository.initiatives]


@app.post("/v1/initiatives/{initiative_id}/decisions")
def decision(initiative_id: str, payload: Annotated[dict[str, str], Body()]) -> dict[str, Any]:
    if initiative_id not in {item.id for item in repository.initiatives}:
        raise HTTPException(status_code=404, detail="initiative not found")
    if payload.get("approval") != "authorized-reviewer":
        raise HTTPException(status_code=403, detail="authorized approval required")
    return {"initiative_id": initiative_id, "requested_state": payload.get("state", "HOLD"), "mode": "local_simulation", "executed": False}


@app.get("/v1/capabilities")
def capabilities() -> dict[str, Any]:
    return {"items": [item.model_dump(mode="json") for item in repository.capabilities], "graph": capability_graph(repository)}


@app.get("/v1/portfolio")
def portfolio(scenario: str = "base") -> dict[str, Any]:
    try:
        return cast(dict[str, Any], scenario_run(repository, scenario)["allocation"])
    except StopIteration as error:
        raise HTTPException(status_code=404, detail="scenario not found") from error


@app.get("/v1/costs")
def costs(scenario: str = "base") -> dict[str, Any]:
    try:
        return reconcile_costs(repository, scenario)
    except StopIteration as error:
        raise HTTPException(status_code=404, detail="scenario not found") from error


@app.get("/v1/risks")
def risks() -> list[dict[str, str]]:
    return [{"id": item.id, "risk": item.name, "response": item.expected_action} for item in repository.shocks]


@app.get("/v1/gates")
def gates() -> list[dict[str, Any]]:
    return [item.model_dump(mode="json") for item in repository.gates]


@app.post("/v1/reports")
def reports(payload: Annotated[dict[str, str], Body()]) -> dict[str, Any]:
    return build_reports(repository, payload.get("scenario", "base"))
