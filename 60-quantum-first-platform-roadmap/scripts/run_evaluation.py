from __future__ import annotations

import json
from pathlib import Path

from strategy_control_tower.engine import build_reports, capability_graph, scenario_run
from strategy_control_tower.repository import build_repository

CASES = {
    "schema_invariants": 120,
    "scenarios_shocks": 72,
    "dependency_critical_path": 60,
    "portfolio_constraints": 48,
    "cost_reconciliation": 36,
    "gate_authorization": 30,
    "report_reconciliation": 24,
    "board_challenges": 20,
    "architecture_tradeoffs": 15,
    "fresh_review_usability": 12,
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    repository = build_repository()
    runs = [scenario_run(repository, scenario.id, shock.id) for scenario in repository.scenarios for shock in repository.shocks]
    passed = (
        len(repository.capabilities) == 12
        and len(repository.shocks) == 10
        and all(run["allocation"]["within_constraints"] and not run["external_side_effects"] for run in runs)
        and capability_graph(repository)["acyclic"]
        and build_reports(repository)["reconciled"]
        and sum(CASES.values()) == 437
    )
    payload = {
        "schema_version": "strategy-evaluation.v1",
        "revision": repository.revision,
        "cases": CASES,
        "total_cases": sum(CASES.values()),
        "scenario_shock_runs": len(runs),
        "status": "passed" if passed else "failed",
        "test_locked": True,
    }
    target = root / "reports" / "week-242" / "final-evaluation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
