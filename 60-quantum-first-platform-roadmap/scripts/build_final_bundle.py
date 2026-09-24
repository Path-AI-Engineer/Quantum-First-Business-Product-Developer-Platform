from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from strategy_control_tower.engine import build_reports, material_figures, scenario_run
from strategy_control_tower.repository import build_repository


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    repository = build_repository()
    evaluation = root / "reports" / "week-242" / "final-evaluation.json"
    if not evaluation.exists():
        raise ValueError("locked evaluation is missing")
    reports = build_reports(repository)
    artifacts: dict[str, Any] = {}
    for relative in (
        "data/canonical/strategy.v1.json",
        "reports/week-242/final-evaluation.json",
        "reports/week-242/board.json",
        "reports/week-242/technical.json",
        "reports/week-242/operating.json",
    ):
        path = root / relative
        artifacts[relative] = {"sha256": digest(path), "bytes": path.stat().st_size}
    payload = {
        "schema_version": "quantum-first-roadmap-bundle.v1",
        "version": "quantum-first-roadmap-v1",
        "revision": repository.revision,
        "status": repository.approval_status,
        "approval": None,
        "claim_boundary": "synthetic scenarios; no external board, financial, staffing, product, or cloud action",
        "roadmap_horizons": ["year_1", "year_3", "year_10"],
        "scenarios": [scenario_run(repository, item.id) for item in repository.scenarios],
        "reports_reconciled": reports["reconciled"],
        "material_figures": material_figures(repository),
        "artifacts": artifacts,
        "transition": {"next_plan": "Plan 11 — Embodied AI + Autonomous Systems", "blocked_until_external_approval": True},
    }
    target = root / "reports" / "week-242" / "final" / "quantum-first-roadmap-v1.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"file": str(target.relative_to(root)), "sha256": digest(target), "status": payload["status"], "reports_reconciled": True},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
