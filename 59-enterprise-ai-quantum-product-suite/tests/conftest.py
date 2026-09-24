from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from enterprise_suite.api import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
