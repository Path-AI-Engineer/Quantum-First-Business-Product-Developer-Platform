from __future__ import annotations

import pytest

from strategy_control_tower.models import StrategyRepository

DIMENSIONS = (
    "demand",
    "latency",
    "job duration",
    "state",
    "isolation",
    "compliance",
    "residency",
    "skills",
    "on-call",
    "cost",
    "portability",
    "exit",
)


@pytest.mark.parametrize("case", range(15))
def test_architecture_tradeoffs(repository: StrategyRepository, case: int) -> None:
    dimension = DIMENSIONS[case % len(DIMENSIONS)]
    assert dimension and all(provider["exit"] for provider in repository.providers)
    if case >= 12:
        assert {provider["strategy"] for provider in repository.providers} == {"buy", "partner", "option"}
