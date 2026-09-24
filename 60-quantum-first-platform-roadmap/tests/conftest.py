from __future__ import annotations

import pytest

from strategy_control_tower.models import StrategyRepository
from strategy_control_tower.repository import build_repository


@pytest.fixture(scope="session")
def repository() -> StrategyRepository:
    return build_repository()
