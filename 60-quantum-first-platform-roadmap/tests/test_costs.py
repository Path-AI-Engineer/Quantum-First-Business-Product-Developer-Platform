from __future__ import annotations

import pytest

from strategy_control_tower.engine import material_figures, reconcile_costs
from strategy_control_tower.models import StrategyRepository


@pytest.mark.parametrize("case", range(36))
def test_cost_reconciliation(repository: StrategyRepository, case: int) -> None:
    scenario = repository.scenarios[case % 3]
    result = reconcile_costs(repository, scenario.id)
    assert result["reconciled"] and sum(result["pools"].values()) == result["total"]
    assert set(result["pools"]) == set(repository.cost_pools)
    assert len(material_figures(repository)) == 4
