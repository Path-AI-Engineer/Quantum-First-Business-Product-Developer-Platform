from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from strategy_control_tower.api import app
from strategy_control_tower.engine import evaluate_gate

client = TestClient(app)


@pytest.mark.parametrize("case", range(30))
def test_gate_and_decision_authorization(case: int) -> None:
    value = (case % 10) / 10
    assert evaluate_gate(value, 0.5) in {"PASS", "HOLD"}
    if case == 0:
        response = client.post("/v1/initiatives/pqc-readiness/decisions", json={"state": "COMMITTED"})
        assert response.status_code == 403
    elif case == 1:
        response = client.post("/v1/initiatives/pqc-readiness/decisions", json={"state": "HOLD", "approval": "authorized-reviewer"})
        assert response.status_code == 200 and response.json()["executed"] is False
    elif case == 2:
        assert client.post("/v1/initiatives/missing/decisions", json={"approval": "authorized-reviewer"}).status_code == 404
