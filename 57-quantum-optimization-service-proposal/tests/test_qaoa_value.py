from __future__ import annotations

import pytest

from optimization_lab.models import ValueModelInput
from optimization_lab.qaoa import qubo_resource_report, run_qaoa_candidate
from optimization_lab.value import calculate_value


def base_value(**overrides: float | int) -> ValueModelInput:
    values: dict[str, float | int] = {
        "baseline_cost_per_decision": 100,
        "decisions_per_year": 500,
        "improvement_low": 0.05,
        "improvement_high": 0.15,
        "adoption_low": 0.4,
        "adoption_high": 0.8,
        "integration_cost": 10_000,
        "annual_operating_cost": 2_000,
        "risk_adjustment": 0.7,
        "horizon_years": 3,
    }
    values.update(overrides)
    return ValueModelInput(**values)


@pytest.mark.parametrize("case", range(18))
def test_value_sensitivity_cases_are_ranges_not_promises(case: int) -> None:
    result = calculate_value(
        base_value(
            improvement_low=0.01 + case * 0.002,
            improvement_high=0.10 + case * 0.005,
            risk_adjustment=0.5 + case * 0.02,
        )
    )
    assert result.annualized_value_range[0] <= result.annualized_value_range[1]
    assert len(result.sensitivity) == 3
    assert "not realized savings" in result.disclaimer
    assert result.assumptions


def test_invalid_value_ranges_fail_closed() -> None:
    with pytest.raises(ValueError, match="improvement_low"):
        base_value(improvement_low=0.8, improvement_high=0.2)


@pytest.mark.parametrize("seed", [5701, 5702, 5703])
def test_qaoa_is_reproducible_and_never_claims_advantage(seed: int) -> None:
    args = ([-3.0, -2.0, -4.0, -1.0], {(0, 1): 2.0, (1, 2): 2.5, (2, 3): 1.5})
    first = run_qaoa_candidate(*args, seed=seed, shots=256)
    second = run_qaoa_candidate(*args, seed=seed, shots=256)
    assert first == second
    assert first["advantage_claim"] is False
    assert first["sampled_objective"] >= first["exact_objective"]


def test_qaoa_bounds_and_empty_qubo_resources() -> None:
    assert qubo_resource_report([], {})["coefficient_dynamic_range"] == 0
    with pytest.raises(ValueError, match="1..8"):
        run_qaoa_candidate([], {}, seed=1)
