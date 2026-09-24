from __future__ import annotations

import json
from pathlib import Path

from strategy_control_tower.engine import build_reports
from strategy_control_tower.repository import build_repository


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    repository = build_repository()
    write_json(root / "data" / "canonical" / "strategy.v1.json", repository.model_dump(mode="json"))
    reports = build_reports(repository)
    for audience in ("board", "technical", "operating"):
        write_json(root / "reports" / "week-242" / f"{audience}.json", reports[audience])
    print({"revision": repository.revision, "initiatives": len(repository.initiatives), "capabilities": len(repository.capabilities)})


if __name__ == "__main__":
    main()
