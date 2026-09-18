from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

from optimization_lab.corpus import build_corpus, corpus_summary
from optimization_lab.models import Domain, Feasibility, Size, Split
from optimization_lab.qaoa import run_qaoa_candidate
from optimization_lab.solvers import objective_gap, solve_heuristic, solve_strong


def run_benchmark(*, include_locked_test: bool = True) -> dict[str, Any]:
    corpus = build_corpus()
    selected = [item for item in corpus if include_locked_test or item.split is Split.DEVELOPMENT]
    runs: list[dict[str, Any]] = []
    oracle_by_id: dict[str, Any] = {}
    for instance in selected:
        strong = solve_strong(instance)
        heuristic = solve_heuristic(instance)
        exact = solve_strong(instance, exact=True) if instance.size is Size.SMALL else None
        if exact is not None:
            oracle_by_id[instance.instance_id] = exact
        for result in (strong, heuristic, exact):
            if result is None:
                continue
            payload = result.model_dump(mode="json")
            payload["split"] = instance.split.value
            payload["domain"] = instance.domain.value
            payload["size"] = instance.size.value
            payload["expected_feasibility"] = instance.expected_feasibility.value
            payload["oracle_gap"] = objective_gap(result, exact) if exact is not None else None
            payload["reproducibility_sha256"] = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode("utf-8")
            ).hexdigest()
            runs.append(payload)
    false_feasible = [
        run for run in runs if run["feasible"] and run["expected_feasibility"] == Feasibility.INFEASIBLE.value
    ]
    exact_disagreements = [
        run
        for run in runs
        if run["solver"] == "classical_strong"
        and run["size"] == Size.SMALL.value
        and (
            run["feasible"] != oracle_by_id[run["instance_id"]].feasible
            or (run["oracle_gap"] is not None and run["oracle_gap"] > 1e-9)
        )
    ]
    qaoa_runs = [
        run_qaoa_candidate(
            [-3.0, -2.0, -4.0, -1.0],
            {(0, 1): 2.0, (1, 2): 2.5, (2, 3): 1.5, (0, 3): 1.0},
            seed=seed,
        )
        for seed in (5701, 5702, 5703)
    ]
    return {
        "schema_version": "optimization.benchmark.v1",
        "protocol": {
            "classical_first": True,
            "per_instance_time_budget_seconds": 0.08,
            "exact_small_time_budget_seconds": 0.25,
            "same_input_and_objective": True,
            "test_locked_until_final": True,
            "hardware": "local CPU",
            "cloud_jobs": False,
        },
        "corpus": corpus_summary(corpus),
        "run_count": len(runs),
        "solver_counts": dict(Counter(run["solver"] for run in runs)),
        "false_feasible_count": len(false_feasible),
        "exact_disagreement_count": len(exact_disagreements),
        "all_reported_solutions_feasible": all(not run["feasible"] or not run["violations"] for run in runs),
        "qaoa_experiment": qaoa_runs,
        "qaoa_advantage_claim": False,
        "runs": runs,
    }


def robustness_report() -> dict[str, Any]:
    corpus = build_corpus()
    summaries: list[dict[str, Any]] = []
    for domain in Domain:
        fixtures = [item for item in corpus if item.domain is domain and item.split is Split.DEVELOPMENT][:6]
        baseline = [solve_strong(item) for item in fixtures]
        feasible_rate = sum(result.feasible for result in baseline) / len(baseline)
        summaries.append(
            {
                "domain": domain.value,
                "scenarios": len(fixtures),
                "feasibility_rate": feasible_rate,
                "guardrail": (
                    "re-solve and require independent feasibility check after every material input change"
                ),
            }
        )
    return {"schema_version": "optimization.robustness.v1", "domains": summaries}
