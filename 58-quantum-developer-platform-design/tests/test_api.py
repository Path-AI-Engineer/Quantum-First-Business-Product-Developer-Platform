import pytest


def bootstrap(client):
    organization = client.post("/v1/organizations", json={"name": "API Test Org"}).json()
    project = client.post(
        "/v1/projects",
        json={"organization_id": organization["id"], "name": "sandbox", "environment": "sandbox"},
    ).json()
    return organization, project


def test_health_security_headers_and_catalog(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["x-frame-options"] == "DENY"
    assert client.get("/v1/health/live").json()["status"] == "ok"
    assert client.get("/v1/health/ready").json()["cloud_live"] is False
    capabilities = client.get("/v1/capabilities").json()
    assert len(capabilities) == 25
    assert any(item["availability"] == "credentials_required" for item in capabilities)


def test_api_golden_path(client) -> None:
    _organization, project = bootstrap(client)
    key = client.post("/v1/api-keys", json={"project_id": project["id"], "scopes": ["jobs:write"]})
    assert key.status_code == 201
    key_body = key.json()
    assert key_body["secret"].startswith("qdp_sandbox")
    estimate = client.post(
        f"/v1/jobs/estimate?project_id={project['id']}",
        json={"operation": "circuit.sample", "provider": "local", "payload": {"shots": 32}},
    )
    assert estimate.json()["classification"] == "estimate"
    response = client.post(
        f"/v1/jobs?project_id={project['id']}",
        headers={"Idempotency-Key": "api-golden"},
        json={"operation": "circuit.sample", "provider": "local", "payload": {"shots": 32}},
    )
    assert response.status_code == 202
    job = response.json()
    assert job["state"] == "SUCCEEDED"
    assert client.get(f"/v1/jobs?project_id={project['id']}").json()[0]["id"] == job["id"]
    assert client.get(f"/v1/jobs/{job['id']}?project_id={project['id']}").status_code == 200
    artifacts = client.get(f"/v1/jobs/{job['id']}/artifacts?project_id={project['id']}").json()
    downloaded = client.get(f"/v1/artifacts/{artifacts[0]['id']}/download?project_id={project['id']}")
    assert downloaded.status_code == 200
    assert downloaded.headers["digest"].startswith("sha-256=")
    assert client.get(f"/v1/usage?project_id={project['id']}").json()[0]["classification"] == "actual"
    assert client.get(f"/v1/quotas?project_id={project['id']}").json()["allowed"] is True
    assert client.get(f"/v1/audit?project_id={project['id']}").json()


def test_api_problem_details_and_idempotency_conflict(client) -> None:
    response = client.post(
        "/v1/projects",
        headers={"X-Request-Id": "req-test"},
        json={"organization_id": "missing", "name": "sandbox"},
    )
    body = response.json()
    assert response.status_code == 404
    assert body["code"] == "ORGANIZATION_NOT_FOUND"
    assert body["correlation_id"] == "req-test"
    _organization, project = bootstrap(client)
    first = client.post(
        f"/v1/jobs?project_id={project['id']}",
        headers={"Idempotency-Key": "conflict"},
        json={"operation": "workflow.run", "provider": "fake"},
    )
    assert first.status_code == 202
    conflict = client.post(
        f"/v1/jobs?project_id={project['id']}",
        headers={"Idempotency-Key": "conflict"},
        json={"operation": "resource.estimate", "provider": "fake"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "IDEMPOTENCY_CONFLICT"
    missing = client.post(
        f"/v1/jobs?project_id={project['id']}",
        json={"operation": "workflow.run", "provider": "fake"},
    )
    assert missing.status_code == 422
    assert missing.json()["remediation_hint"]


def test_api_key_lifecycle_and_webhook_workbench(client) -> None:
    _organization, project = bootstrap(client)
    key = client.post("/v1/api-keys", json={"project_id": project["id"]}).json()
    rotated = client.post(f"/v1/api-keys/{key['id']}/rotate?project_id={project['id']}")
    assert rotated.status_code == 201
    fresh = rotated.json()
    assert fresh["id"] != key["id"]
    assert client.delete(f"/v1/api-keys/{fresh['id']}?project_id={project['id']}").status_code == 200
    webhook = client.post(
        "/v1/webhook-endpoints",
        json={"project_id": project["id"], "url": "https://receiver.example/hook"},
    ).json()
    assert webhook["secret"].startswith("whsec")
    rotated_secret = client.post(f"/v1/webhook-endpoints/{webhook['id']}/rotate-secret").json()
    assert rotated_secret["secret"] != webhook["secret"]
    assert client.get(f"/v1/webhook-deliveries?project_id={project['id']}").json() == []


@pytest.mark.parametrize("path", ["/docs", "/openapi.json", "/v1/capabilities", "/v1/health/ready"])
def test_public_reference_surfaces(client, path: str) -> None:
    assert client.get(path).status_code == 200
