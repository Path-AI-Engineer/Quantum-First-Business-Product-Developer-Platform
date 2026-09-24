from __future__ import annotations

import pytest

from strategy_control_tower.models import CostRange, StrategyRepository


@pytest.mark.parametrize("case", range(120))
def test_schema_and_invariants(repository: StrategyRepository, case: int) -> None:
    initiative = repository.initiatives[case % len(repository.initiatives)]
    assert initiative.outcome and initiative.owner and initiative.dependencies and initiative.gate_ids
    assert initiative.cost.minimum <= initiative.cost.expected <= initiative.cost.maximum
    assert initiative.kill_condition and initiative.exit_plan
    if "quantum" in initiative.name.lower():
        assert initiative.classical_baseline
    if case == 119:
        with pytest.raises(ValueError):
            CostRange(minimum=3, expected=2, maximum=1)
