from __future__ import annotations

import pytest

from strategy_control_tower.engine import capability_graph
from strategy_control_tower.models import StrategyRepository


@pytest.mark.parametrize("case", range(60))
def test_dependency_and_critical_path(repository: StrategyRepository, case: int) -> None:
    graph = capability_graph(repository)
    assert graph["acyclic"] is True
    assert graph["nodes"] == 12
    assert graph["critical_path"]
    capability = repository.capabilities[case % 12]
    assert capability.owner and capability.evidence and capability.sourcing in {"build", "buy", "partner"}
