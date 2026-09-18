from __future__ import annotations

import pytest

from optimization_lab.eligibility import DIMENSIONS, assess
from optimization_lab.models import Domain, EligibilityOutcome, Opportunity


def opportunity(case: int, **overrides: float | None) -> Opportunity:
    dimensions = {name: 0.72 for name in DIMENSIONS}
    dimensions.update(overrides)
    return Opportunity(
        opportunity_id=f"opp-red-{case:02d}",
        name=f"Synthetic opportunity {case}",
        domain=Domain.SCHEDULING,
        decision_frequency_per_year=250,
        current_cost_per_decision=120,
        dimensions=dimensions,
    )


@pytest.mark.parametrize(
    ("case", "overrides", "expected"),
    [
        (1, {"human_validation": 0.1}, EligibilityOutcome.DO_NOT_PILOT),
        (2, {"outcome_controllability": 0.1}, EligibilityOutcome.DO_NOT_PILOT),
        (3, {"data_quality": 0.2}, EligibilityOutcome.DATA_OR_PROCESS_FIRST),
        (4, {"constraint_stability": 0.2}, EligibilityOutcome.DATA_OR_PROCESS_FIRST),
        (5, {name: None for name in list(DIMENSIONS)[:7]}, EligibilityOutcome.DATA_OR_PROCESS_FIRST),
        (6, {"qubo_fit": 0.1}, EligibilityOutcome.OPTIMIZE_NOW_CLASSICAL),
        (7, {"qubo_fit": 0.8}, EligibilityOutcome.EXPERIMENT_QUANTUM_READY),
        (8, {"baseline_maturity": 0.2}, EligibilityOutcome.OPTIMIZE_NOW_CLASSICAL),
        (9, {name: 0.4 for name in DIMENSIONS}, EligibilityOutcome.DATA_OR_PROCESS_FIRST),
        (10, {"organizational_maturity": 0.0}, EligibilityOutcome.OPTIMIZE_NOW_CLASSICAL),
        (11, {"decision_value": 0.0}, EligibilityOutcome.OPTIMIZE_NOW_CLASSICAL),
        (12, {"error_tolerance": 0.0}, EligibilityOutcome.OPTIMIZE_NOW_CLASSICAL),
    ],
)
def test_twelve_red_team_cases(
    case: int, overrides: dict[str, float | None], expected: EligibilityOutcome
) -> None:
    result = assess(opportunity(case, **overrides))
    assert result.outcome is expected
    assert result.explanation
    assert result.next_experiment


def test_invalid_dimension_is_rejected() -> None:
    with pytest.raises(ValueError, match="dimension scores"):
        assess(opportunity(99, decision_value=1.1))


def test_empty_evidence_is_low_confidence() -> None:
    result = assess(opportunity(98, **dict.fromkeys(DIMENSIONS)))
    assert result.confidence == 0
    assert result.outcome is EligibilityOutcome.DATA_OR_PROCESS_FIRST
