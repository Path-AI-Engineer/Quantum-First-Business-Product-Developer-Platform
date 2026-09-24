from __future__ import annotations

import pytest

from strategy_control_tower.engine import allocate
from strategy_control_tower.models import StrategicClass, StrategyRepository


@pytest.mark.parametrize("case", range(48))
def test_portfolio_constraints(repository: StrategyRepository, case: int) -> None:
    budget = 320_000 + case * 20_000
    people = 5 + case % 10
    result = allocate(repository.initiatives, budget, people, 0.8 + (case % 5) * 0.15)
    assert result["within_constraints"]
    assert result["spent"] <= budget and result["headcount_used"] <= people
    selected = [item for item in repository.initiatives if item.id in result["selected"]]
    if any(item.strategic_class is StrategicClass.GROWTH for item in selected):
        assert any(item.strategic_class is StrategicClass.REGULATORY for item in selected)
