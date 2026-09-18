from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, status

from optimization_lab.corpus import corpus_summary
from optimization_lab.models import (
    Opportunity,
    OpportunityCreate,
    PilotCreate,
    ProblemInstance,
    ValueModelInput,
)
from optimization_lab.service import LabService

app = FastAPI(
    title="Optimization Value Validation Lab",
    version="1.0.0-alpha.1",
    description=(
        "Classical-first local prototype. Outputs are evidence, not automated "
        "operational or financial advice."
    ),
)
service = LabService()

IDENTITIES = {
    "operations-owner": {"write": True},
    "optimization-scientist": {"write": True},
    "risk-reviewer": {"write": False},
}


def identity(x_demo_identity: Annotated[str | None, Header()] = None) -> str:
    if x_demo_identity not in IDENTITIES:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "known X-Demo-Identity is required")
    return x_demo_identity


def writer(subject: Annotated[str, Depends(identity)]) -> str:
    if not IDENTITIES[subject]["write"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "identity is read-only")
    return subject


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "mode": "local-synthetic"}


@app.get("/v1/snapshot")
def snapshot(_: Annotated[str, Depends(identity)]) -> dict[str, Any]:
    return service.snapshot()


@app.post("/v1/opportunities", response_model=Opportunity, status_code=status.HTTP_201_CREATED)
def create_opportunity(request: OpportunityCreate, _: Annotated[str, Depends(writer)]) -> Opportunity:
    return service.create_opportunity(request)


@app.get("/v1/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: str, _: Annotated[str, Depends(identity)]) -> Opportunity:
    item = service.get_opportunity(opportunity_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "opportunity not found")
    return item


@app.post("/v1/opportunities/{opportunity_id}/assess")
def assess_opportunity(opportunity_id: str, _: Annotated[str, Depends(writer)]) -> Any:
    result = service.assess_opportunity(opportunity_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "opportunity not found")
    return result


@app.post("/v1/instances", status_code=status.HTTP_201_CREATED)
def create_instance(request: ProblemInstance, _: Annotated[str, Depends(writer)]) -> ProblemInstance:
    try:
        return service.create_instance(request)
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error


@app.get("/v1/formulations")
def formulations(_: Annotated[str, Depends(identity)]) -> dict[str, Any]:
    return {
        "formulations": [
            {
                "domain": "workforce_scheduling",
                "native": "CP-SAT",
                "heuristic": "cost-priority assignment",
                "qubo": "bounded diagnostic only",
            },
            {
                "domain": "distribution_routing",
                "native": "OR-Tools routing",
                "heuristic": "capacity-first greedy",
                "qubo": "bounded diagnostic only",
            },
            {
                "domain": "portfolio_allocation",
                "native": "CP-SAT integer selection",
                "heuristic": "risk-return ranking",
                "qubo": "small binary selection",
            },
        ],
        "corpus": corpus_summary(),
    }


@app.post("/v1/benchmarks", status_code=status.HTTP_201_CREATED)
def create_benchmark(_: Annotated[str, Depends(writer)]) -> dict[str, Any]:
    return service.create_benchmark()


@app.get("/v1/benchmarks/{benchmark_id}")
def get_benchmark(benchmark_id: str, _: Annotated[str, Depends(identity)]) -> dict[str, Any]:
    item = service.get_benchmark(benchmark_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "benchmark not found")
    return {key: value for key, value in item.items() if key != "runs"}


@app.get("/v1/benchmarks/{benchmark_id}/runs")
def benchmark_runs(benchmark_id: str, _: Annotated[str, Depends(identity)]) -> dict[str, Any]:
    item = service.get_benchmark(benchmark_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "benchmark not found")
    return {"runs": item["runs"]}


@app.get("/v1/benchmarks/{benchmark_id}/comparison")
def benchmark_comparison(benchmark_id: str, _: Annotated[str, Depends(identity)]) -> dict[str, Any]:
    item = service.get_benchmark(benchmark_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "benchmark not found")
    return {
        "solver_counts": item["solver_counts"],
        "all_reported_solutions_feasible": item["all_reported_solutions_feasible"],
        "exact_disagreement_count": item["exact_disagreement_count"],
        "qaoa_advantage_claim": False,
    }


@app.post("/v1/value-models", status_code=status.HTTP_201_CREATED)
def create_value_model(request: ValueModelInput, _: Annotated[str, Depends(writer)]) -> Any:
    return service.create_value_model(request)


@app.post("/v1/pilots", status_code=status.HTTP_201_CREATED)
def create_pilot(request: PilotCreate, _: Annotated[str, Depends(writer)]) -> Any:
    try:
        return service.create_pilot(request)
    except KeyError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "opportunity not found") from error


@app.post("/v1/proposals", status_code=status.HTTP_201_CREATED)
def create_proposal(opportunity_id: str, _: Annotated[str, Depends(writer)]) -> Any:
    try:
        return service.create_proposal(opportunity_id)
    except KeyError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "opportunity not found") from error


@app.get("/v1/evidence/{record_id}")
def evidence(record_id: str, _: Annotated[str, Depends(identity)]) -> dict[str, Any]:
    item = service.evidence(record_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "evidence record not found")
    return item
