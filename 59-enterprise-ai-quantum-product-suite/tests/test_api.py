from __future__ import annotations

from fastapi.testclient import TestClient


def test_portfolio_catalog_evidence_and_domains(client: TestClient) -> None:
    headers = {"x-tenant-id": "meridian"}
    portfolio = client.get("/v1/portfolio/summary", headers=headers)
    assert portfolio.status_code == 200
    assert portfolio.json()["evidence"] == 60
    assert len(client.get("/v1/catalog").json()) == 4
    assert client.get("/v1/evidence/ev-meridian-000", headers=headers).status_code == 200
    assert client.get("/v1/evidence/ev-atlas-000", headers=headers).status_code == 404
    assert len(client.get("/v1/risks", headers=headers).json()) == 3
    assert len(client.get("/v1/crypto/findings", headers=headers).json()) == 3
    assert client.get("/v1/crypto/migration-waves", headers=headers).json()[0]["status"] == "proposed-not-authorized"
    assert len(client.get("/v1/optimization/opportunities", headers=headers).json()) == 4
    assert client.get("/v1/quantum/capabilities").json()[0]["external"] is False


def test_decision_benchmark_usage_report_and_assistant(client: TestClient) -> None:
    decision = client.post(
        "/v1/recommendations/rec-meridian-1/decisions",
        json={"tenant_id": "meridian", "owner_id": "id-meridian-00", "outcome": "hold", "assumptions": []},
    )
    assert decision.status_code == 200
    benchmark = client.post(
        "/v1/optimization/benchmarks",
        json={"tenant_id": "meridian", "opportunity_id": "opt-meridian-1"},
    )
    assert benchmark.status_code == 200
    assert client.get("/v1/usage", headers={"x-tenant-id": "meridian"}).json()["estimated_cost"] == 0
    report = client.post("/v1/reports", json={"tenant_id": "meridian", "report_type": "portfolio"})
    assert report.json()["limitations"]
    assistant = client.post(
        "/v1/assistant/brief",
        json={"tenant_id": "meridian", "question": "Summarize", "evidence_ids": ["ev-meridian-000"]},
    )
    assert assistant.json()["citations"] == ["ev-meridian-000"]


def test_approval_job_is_local_single_use_and_tenant_scoped(client: TestClient) -> None:
    approval = client.post(
        "/v1/approvals",
        json={"tenant_id": "meridian", "requester_id": "id-meridian-05", "resource_id": "local-simulator", "scope": "sandbox-job"},
    ).json()
    from enterprise_suite.api import suite

    suite.grant_approval(approval["approval_id"], "id-meridian-03")
    payload = {
        "tenant_id": "meridian",
        "capability_id": "local-simulator",
        "approval_id": approval["approval_id"],
        "idempotency_key": "job-key-1",
        "input_reference": "s3-local://synthetic/input-1",
    }
    first = client.post("/v1/quantum/jobs", json=payload)
    replay = client.post("/v1/quantum/jobs", json=payload)
    assert first.status_code == 200
    assert first.json()["provider_action"] is False
    assert replay.json()["job_id"] == first.json()["job_id"]
    assert len(client.get("/v1/approvals", headers={"x-tenant-id": "meridian"}).json()) >= 1
    assert client.get("/v1/approvals", headers={"x-tenant-id": "atlas"}).json() == []


def test_api_error_paths(client: TestClient) -> None:
    assert (
        client.post(
            "/v1/recommendations/missing/decisions",
            json={"tenant_id": "meridian", "owner_id": "x", "outcome": "hold"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/v1/optimization/benchmarks",
            json={"tenant_id": "meridian", "opportunity_id": "missing"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/v1/quantum/jobs",
            json={
                "tenant_id": "meridian",
                "capability_id": "local-simulator",
                "approval_id": "missing",
                "idempotency_key": "x",
                "input_reference": "local://x",
            },
        ).status_code
        == 403
    )
    assert client.get("/v1/audit", headers={"x-tenant-id": "meridian"}).status_code == 200
