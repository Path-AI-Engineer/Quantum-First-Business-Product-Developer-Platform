from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from strategy_control_tower.api import app

client = TestClient(app)
CASES = (
    ("GET", "/health"),
    ("GET", "/v1/roadmap"),
    ("GET", "/v1/scenarios"),
    ("POST", "/v1/scenarios/base/runs"),
    ("GET", "/v1/initiatives"),
    ("GET", "/v1/capabilities"),
    ("GET", "/v1/portfolio"),
    ("GET", "/v1/costs"),
    ("GET", "/v1/risks"),
    ("GET", "/v1/gates"),
    ("POST", "/v1/reports"),
    ("GET", "/openapi.json"),
)


@pytest.mark.parametrize(("method", "path"), CASES)
def test_fresh_review_usability_tasks(method: str, path: str) -> None:
    response = client.request(method, path, json={} if method == "POST" else None)
    assert response.status_code == 200
    assert response.json()
