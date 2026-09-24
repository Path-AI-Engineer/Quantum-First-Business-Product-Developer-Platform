import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from venture_evidence.economics import EconomicsInput, economics
from venture_evidence.models import Interval
from venture_evidence.repository import load_corpus, load_protocol
from venture_evidence.scoring import compare, score, sensitivity


@given(
    st.floats(min_value=0, max_value=5, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0, max_value=5, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_score_bounds_and_cost_direction(a, b):
    opportunity, protocol = load_corpus().opportunities[0], load_protocol()
    low, high = sorted([a, b])
    opportunity.dimensions = {d.id: Interval(low=low, high=high) for d in protocol.dimensions}
    rows = [score(opportunity, protocol, s) for s in ("conservative", "base", "aggressive")]
    assert 0 <= rows[0].low <= rows[0].high <= 100
    assert rows[0].estimate <= rows[1].estimate <= rows[2].estimate
    cost = next(d for d in protocol.dimensions if d.direction == "cost")
    part = next(c for c in rows[1].contributions if c.dimension == cost.id)
    assert part.low == pytest.approx((5 - high) * 20 * part.weight)


def test_missing_is_full_uncertainty_not_zero():
    opportunity, protocol = load_corpus().opportunities[0], load_protocol()
    opportunity.dimensions = {d.id: None for d in protocol.dimensions}
    result = score(opportunity, protocol)
    assert (result.low, result.high, result.estimate) == (0, 100, 50)
    assert result.known_weight_fraction == 0
    assert len(result.unknown_dimensions) == 14


@given(st.floats(min_value=0.1, max_value=5, allow_nan=False, allow_infinity=False))
def test_uniform_weight_scale_invariance(multiplier):
    corpus, protocol = load_corpus(), load_protocol()
    reference = compare(corpus, protocol)
    changed = compare(corpus, protocol, multipliers={d.id: multiplier for d in protocol.dimensions})
    assert [s.id for s in changed] == [s.id for s in reference]
    assert [s.estimate for s in changed] == pytest.approx([s.estimate for s in reference])


@pytest.mark.parametrize("multiplier", [0, -1, 6, math.inf, math.nan])
def test_invalid_weights(multiplier):
    with pytest.raises(ValueError):
        compare(load_corpus(), load_protocol(), multipliers={"severity": multiplier})


def test_interval_sensitivity_is_explicit_and_reproducible():
    corpus, protocol = load_corpus(), load_protocol()
    result = sensitivity(corpus, protocol)
    assert len(result["stress_cases"]) == 8
    assert result["one_at_a_time_cases"] == 28
    assert result["intervals_overlap"] is True
    assert result == sensitivity(corpus, protocol)
    with pytest.raises(ValueError):
        compare(corpus, protocol, multipliers={"imaginary": 1})


@pytest.mark.parametrize("low,high", [(4, 1), (-1, 1), (0, 6), (0, math.inf), (math.nan, 1)])
def test_invalid_intervals(low, high):
    with pytest.raises(ValidationError):
        Interval(low=low, high=high)


@given(st.integers(0, 1000000), st.floats(1, 1000000, allow_nan=False, allow_infinity=False))
def test_economics_capacity_and_subset_invariants(organizations, price):
    inputs = EconomicsInput(organizations=organizations, annual_price=price)
    result = economics(inputs)
    assert 0 <= result["som"] <= result["sam"] <= result["tam"]
    assert result["som"] <= inputs.customer_capacity * price
    assert result["classification"] == "illustrative_hypothesis"
    assert result["gross_margin"] == pytest.approx((price - 5300) / price)


def test_negative_margin_is_not_clipped_into_success():
    result = economics(EconomicsInput(annual_price=100))
    assert result["gross_margin"] < 0
    with pytest.raises(ValidationError):
        EconomicsInput(annual_price=math.nan)
