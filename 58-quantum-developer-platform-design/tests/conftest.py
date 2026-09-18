from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from quantum_platform.api import app, plane
from quantum_platform.control_plane import ControlPlane
from quantum_platform.models import Environment


@pytest.fixture
def seeded() -> tuple[ControlPlane, str, str]:
    control = ControlPlane()
    organization = control.create_organization("Northstar Research")
    project = control.create_project(organization.id, "sandbox-a", Environment.SANDBOX)
    other = control.create_project(organization.id, "sandbox-b", Environment.SANDBOX)
    return control, project.id, other.id


@pytest.fixture
def client() -> Iterator[TestClient]:
    plane.__init__()
    with TestClient(app) as value:
        yield value
