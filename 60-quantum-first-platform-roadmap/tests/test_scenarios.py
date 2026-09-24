from __future__ import annotations

import pytest

from strategy_control_tower.engine import scenario_run
from strategy_control_tower.models import StrategyRepository


@pytest.mark.parametrize("case", range(72))
def test_scenario_and_shock_cases(repository: StrategyRepository, case: int) -> None:
    scenario = repository.scenarios[case % 3]
    shock = repository.shocks[case % 10] if case >= 3 else None
    result = scenario_run(repository, scenario.id, shock.id if shock else None)
    assert result["external_side_effects"] is False
    assert result["allocation"]["within_constraints"]
    assert result["budget"] > 0 and result["decision"]
