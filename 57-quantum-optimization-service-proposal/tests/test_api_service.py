from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import optimization_lab.api as api_module
from optimization_lab.eligibility import DIMENSIONS
from optimization_lab.models import Domain, OpportunityCreate, PilotCreate, ValueModelInput
from optimization_lab.service import LabService


@pytest.fixture
def client() -> TestClient:
    api_module.service = LabService()
    return TestClient(api_module.app)


def headers(identity: str = "operations-owner") -> dict[str, str]:
    return {"X-Demo-Identity": identity}


def opportunity_payload() -> dict[str, Any]:
    return {
        "name": "Fictional workforce planning",
        "domain": "workforce_scheduling",
        "decision_frequency_per_year": 250,
        "current_cost_per_decision": 120,
        "dimensions": {name: 0.72 for name in DIMENSIONS},
    }


@pytest.mark.parametrize(
    ("method", "path", "payload", "identity", "expected"),
    [
        ("get", "/v1/snapshot", None, None, 401),
        ("get", "/v1/snapshot", None, "unknown", 401),
        ("post", "/v1/opportunities", {}, "operations-owner", 422),
        ("post", "/v1/opportunities", opportunity_payload(), "risk-reviewer", 403),
        ("get", "/v1/opportunities/missing", None, "operations-owner", 404),
        ("post", "/v1/opportunities/missing/assess", None, "operations-owner", 404),
        ("post", "/v1/instances", {"unexpected": True}, "operations-owner", 422),
        ("get", "/v1/benchmarks/missing", None, "operations-owner", 404),
        ("get", "/v1/benchmarks/missing/runs", None, "operations-owner", 404),
        ("get", "/v1/benchmarks/missing/comparison", None, "operations-owner", 404),
        ("post", "/v1/pilots", {}, "operations-owner", 422),
        ("get", "/v1/evidence/missing", None, "operations-owner", 404),
    ],
)
def test_twelve_api_auth_and_input_abuse_cases(
    client: TestClient,
    method: str,
    path: str,
    payload: dict[str, Any] | None,
    identity: str | None,
    expected: int,
) -> None:
    response = client.request(method, path, json=payload, headers=headers(identity) if identity else {})
    assert response.status_code == expected


def test_full_api_journey(client: TestClient) -> None:
    created = client.post("/v1/opportunities", json=opportunity_payload(), headers=headers())
    assert created.status_code == 201
    opportunity_id = created.json()["opportunity_id"]
    assert client.get(f"/v1/opportunities/{opportunity_id}", headers=headers()).status_code == 200
    assessed = client.post(f"/v1/opportunities/{opportunity_id}/assess", headers=headers())
    assert assessed.status_code == 200
    assert assessed.json()["outcome"] == "EXPERIMENT_QUANTUM_READY"
    value = client.post(
        "/v1/value-models",
        json={
            "baseline_cost_per_decision": 100,
            "decisions_per_year": 500,
            "improvement_low": 0.05,
            "improvement_high": 0.15,
            "adoption_low": 0.4,
            "adoption_high": 0.8,
            "integration_cost": 10_000,
            "annual_operating_cost": 2_000,
            "risk_adjustment": 0.7,
            "horizon_years": 3,
        },
        headers=headers(),
    )
    assert value.status_code == 201
    pilot = client.post(
        "/v1/pilots",
        json={
            "opportunity_id": opportunity_id,
            "domain": "workforce_scheduling",
            "owner": "Fictional operations owner",
            "acceptance_metrics": ["feasibility_rate", "objective_improvement", "override_rate"],
            "rollback_trigger": "Any breach of the agreed feasibility threshold",
        },
        headers=headers(),
    )
    assert pilot.status_code == 201
    assert pilot.json()["auto_actuation"] is False
    proposal = client.post(f"/v1/proposals?opportunity_id={opportunity_id}", headers=headers())
    assert proposal.status_code == 201
    assert proposal.json()["status"] == "technical_candidate_unapproved"


def test_benchmark_lifecycle_and_evidence(client: TestClient) -> None:
    benchmark = client.post("/v1/benchmarks", headers=headers())
    assert benchmark.status_code == 201
    benchmark_id = benchmark.json()["benchmark_id"]
    summary = client.get(f"/v1/benchmarks/{benchmark_id}", headers=headers())
    runs = client.get(f"/v1/benchmarks/{benchmark_id}/runs", headers=headers())
    comparison = client.get(f"/v1/benchmarks/{benchmark_id}/comparison", headers=headers())
    evidence = client.get(f"/v1/evidence/{benchmark_id}", headers=headers())
    assert summary.status_code == runs.status_code == comparison.status_code == evidence.status_code == 200
    assert summary.json()["exact_disagreement_count"] == 0
    assert comparison.json()["qaoa_advantage_claim"] is False
    assert len(evidence.json()["sha256"]) == 64


def test_service_storage_export_and_missing_pilot(tmp_path: Path) -> None:
    service = LabService(str(tmp_path / "metadata.duckdb"))
    created = service.create_opportunity(OpportunityCreate.model_validate(opportunity_payload()))
    assert service.get_opportunity(created.opportunity_id) == created
    assert service.assess_opportunity(created.opportunity_id) is not None
    output = tmp_path / "records.json"
    service.export_records(output)
    assert output.is_file()
    with pytest.raises(KeyError):
        service.create_pilot(
            PilotCreate(
                opportunity_id="missing",
                domain=Domain.ROUTING,
                owner="Owner",
                acceptance_metrics=["feasibility", "latency", "cost"],
                rollback_trigger="Terminate when feasibility drops below threshold",
            )
        )


@pytest.mark.parametrize("case", range(10))
def test_ten_pilot_acceptance_scenarios(case: int) -> None:
    service = LabService()
    opportunity = service.create_opportunity(OpportunityCreate.model_validate(opportunity_payload()))
    plan = service.create_pilot(
        PilotCreate(
            opportunity_id=opportunity.opportunity_id,
            domain=Domain.SCHEDULING,
            owner=f"Synthetic owner {case}",
            acceptance_metrics=["feasibility_rate", "solve_time_p95", "human_override_rate"],
            rollback_trigger=f"Scenario {case}: terminate on threshold breach",
        )
    )
    assert plan.weeks == 8
    assert plan.mode == "shadow"
    assert plan.human_review_required
    assert not plan.auto_actuation
    assert len(plan.termination_criteria) == 4


def test_value_model_service() -> None:
    service = LabService()
    result = service.create_value_model(
        ValueModelInput(
            baseline_cost_per_decision=100,
            decisions_per_year=100,
            improvement_low=0.02,
            improvement_high=0.10,
            adoption_low=0.3,
            adoption_high=0.8,
            integration_cost=5_000,
            annual_operating_cost=1_000,
            risk_adjustment=0.6,
            horizon_years=2,
        )
    )
    assert result.annualized_value_range
