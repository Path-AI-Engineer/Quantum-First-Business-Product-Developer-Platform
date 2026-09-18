from __future__ import annotations

import copy

import pytest

from optimization_lab.corpus import build_corpus
from optimization_lab.models import Domain, Feasibility, Size
from optimization_lab.solvers import check_feasibility, objective_gap, solve_heuristic, solve_strong


@pytest.mark.parametrize("domain", list(Domain))
def test_strong_baseline_matches_small_exact_oracle(domain: Domain) -> None:
    fixtures = [item for item in build_corpus() if item.domain is domain and item.size is Size.SMALL]
    for instance in fixtures:
        oracle = solve_strong(instance, exact=True)
        baseline = solve_strong(instance)
        assert baseline.feasible == oracle.feasible == (instance.expected_feasibility is Feasibility.FEASIBLE)
        if baseline.feasible:
            assert objective_gap(baseline, oracle) == 0
            assert check_feasibility(instance, baseline.assignments) == []


@pytest.mark.parametrize("mutation", range(30))
def test_constraint_mutations_never_pass_as_feasible(mutation: int) -> None:
    instance = copy.deepcopy(build_corpus()[mutation * 3])
    if instance.domain is Domain.SCHEDULING:
        instance.parameters["demand"][-1] = len(instance.entities["workers"]) + 1
    elif instance.domain is Domain.ROUTING:
        instance.parameters["demands"][-1] = int(instance.parameters["vehicle_capacity"]) * len(
            instance.entities["vehicles"]
        )
    else:
        instance.parameters["minimum_return"] = sum(instance.parameters["returns"]) + 1
    result = solve_strong(instance)
    assert not result.feasible
    assert result.status is Feasibility.INFEASIBLE


@pytest.mark.parametrize("domain", list(Domain))
def test_heuristic_is_only_reported_when_independently_feasible(domain: Domain) -> None:
    fixtures = [item for item in build_corpus() if item.domain is domain][:5]
    for instance in fixtures:
        result = solve_heuristic(instance)
        if result.feasible:
            assert check_feasibility(instance, result.assignments) == []
        else:
            assert result.assignments == {}


def test_gap_is_none_without_two_feasible_results() -> None:
    instance = next(item for item in build_corpus() if item.expected_feasibility is Feasibility.INFEASIBLE)
    assert objective_gap(solve_strong(instance), solve_strong(instance, exact=True)) is None
