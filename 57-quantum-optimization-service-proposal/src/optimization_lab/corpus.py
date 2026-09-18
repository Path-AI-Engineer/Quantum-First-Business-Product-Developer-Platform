from __future__ import annotations

from typing import Any

from optimization_lab.models import Domain, Feasibility, ProblemInstance, Size, Split

TEST_INDICES = frozenset({6, 7, 8, 9, 16, 17, 26, 27})


def _size(index: int) -> Size:
    return Size.SMALL if index < 10 else Size.MEDIUM if index < 20 else Size.LARGE


def _scenario(index: int) -> tuple[str, Feasibility]:
    if index % 5 == 4:
        return "infeasible", Feasibility.INFEASIBLE
    if index % 5 in {2, 3}:
        return "tight", Feasibility.FEASIBLE
    return "nominal", Feasibility.FEASIBLE


def _scheduling(index: int, size: Size, infeasible: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    workers = {Size.SMALL: 5, Size.MEDIUM: 8, Size.LARGE: 12}[size]
    shifts = {Size.SMALL: 4, Size.MEDIUM: 7, Size.LARGE: 10}[size]
    demand = [2 + ((index + shift) % 2) for shift in range(shifts)]
    max_shifts = max(2, (sum(demand) + workers - 1) // workers)
    if infeasible:
        demand[-1] = workers + 1
    return (
        {"workers": [f"worker-{i:02d}" for i in range(workers)], "shifts": list(range(shifts))},
        {
            "demand": demand,
            "max_shifts_per_worker": max_shifts,
            "unavailable": [[worker, (worker + index) % shifts] for worker in range(min(2, workers))],
            "costs": [10 + ((worker * 3 + index) % 7) for worker in range(workers)],
            "preferences": [
                [(worker + shift + index) % 4 for shift in range(shifts)] for worker in range(workers)
            ],
        },
    )


def _routing(index: int, size: Size, infeasible: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    customers = {Size.SMALL: 4, Size.MEDIUM: 7, Size.LARGE: 10}[size]
    vehicles = {Size.SMALL: 2, Size.MEDIUM: 3, Size.LARGE: 4}[size]
    demands = [1 + ((index + customer) % 3) for customer in range(customers)]
    capacity = max(3, (sum(demands) + vehicles - 1) // vehicles + 1)
    if infeasible:
        demands[-1] = capacity * vehicles
    coordinates = [[0, 0]] + [
        [(customer * 3 + index) % 13, (customer * 5 + index * 2) % 11] for customer in range(1, customers + 1)
    ]
    return (
        {"depot": 0, "customers": list(range(1, customers + 1)), "vehicles": list(range(vehicles))},
        {"demands": demands, "vehicle_capacity": capacity, "coordinates": coordinates, "late_penalty": 20},
    )


def _portfolio(index: int, size: Size, infeasible: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    assets = {Size.SMALL: 5, Size.MEDIUM: 8, Size.LARGE: 12}[size]
    returns = [4 + ((asset * 5 + index) % 12) for asset in range(assets)]
    risks = [2 + ((asset * 7 + index) % 9) for asset in range(assets)]
    sectors = [asset % 3 for asset in range(assets)]
    cardinality = {Size.SMALL: 3, Size.MEDIUM: 4, Size.LARGE: 5}[size]
    minimum_return = sum(sorted(returns, reverse=True)[:cardinality]) - (2 if index % 5 in {2, 3} else 8)
    if infeasible:
        minimum_return = sum(sorted(returns, reverse=True)[:cardinality]) + 10
    return (
        {"assets": [f"asset-{asset:02d}" for asset in range(assets)]},
        {
            "returns": returns,
            "risks": risks,
            "sectors": sectors,
            "max_assets": cardinality,
            "max_per_sector": 2,
            "minimum_return": minimum_return,
            "risk_weight": 1,
            "return_weight": 2,
        },
    )


def build_corpus() -> list[ProblemInstance]:
    corpus: list[ProblemInstance] = []
    builders = {Domain.SCHEDULING: _scheduling, Domain.ROUTING: _routing, Domain.PORTFOLIO: _portfolio}
    for domain in Domain:
        for index in range(30):
            size = _size(index)
            scenario, expected = _scenario(index)
            entities, parameters = builders[domain](index, size, expected is Feasibility.INFEASIBLE)
            split = Split.TEST if index in TEST_INDICES else Split.DEVELOPMENT
            corpus.append(
                ProblemInstance(
                    instance_id=f"{domain.value}-{index:02d}",
                    domain=domain,
                    size=size,
                    split=split,
                    scenario_id=f"{scenario}-{index:02d}",
                    entities=entities,
                    parameters=parameters,
                    hard_constraints=[
                        "capacity_or_coverage",
                        "availability_or_exposure",
                        "declared_domain_limits",
                    ],
                    soft_constraints=["preference_or_stability"],
                    objective_terms=[
                        {"name": "primary_operational_cost", "unit": "synthetic_score", "weight": 1.0},
                        {"name": "soft_constraint_penalty", "unit": "synthetic_score", "weight": 1.0},
                    ],
                    provenance={
                        "generator": "optimization_lab.corpus",
                        "seed": 5700 + index,
                        "synthetic": True,
                    },
                    expected_feasibility=expected,
                    test_locked=split is Split.TEST,
                )
            )
    return corpus


def corpus_summary(corpus: list[ProblemInstance] | None = None) -> dict[str, Any]:
    values = corpus or build_corpus()
    return {
        "schema_version": "optimization.corpus.v1",
        "total": len(values),
        "domains": {domain.value: sum(item.domain is domain for item in values) for domain in Domain},
        "splits": {split.value: sum(item.split is split for item in values) for split in Split},
        "sizes": {size.value: sum(item.size is size for item in values) for size in Size},
        "expected_infeasible": sum(item.expected_feasibility is Feasibility.INFEASIBLE for item in values),
        "test_locked": True,
    }
