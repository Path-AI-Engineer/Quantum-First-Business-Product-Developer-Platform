from __future__ import annotations

import pytest

from strategy_control_tower.engine import build_reports
from strategy_control_tower.models import StrategyRepository


@pytest.mark.parametrize("case", range(24))
def test_report_reconciliation(repository: StrategyRepository, case: int) -> None:
    reports = build_reports(repository, repository.scenarios[case % 3].id)
    assert reports["reconciled"]
    keys = ("revision", "scenario", "approval_status", "selected", "held", "cost_total", "side_effects")
    assert all(reports["board"][key] == reports["technical"][key] == reports["operating"][key] for key in keys)
