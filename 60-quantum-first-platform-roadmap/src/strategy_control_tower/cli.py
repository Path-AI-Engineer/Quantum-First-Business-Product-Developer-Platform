"""Command-line contract for local strategy review."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .engine import build_reports, capability_graph, scenario_run
from .repository import build_repository


def main() -> None:
    parser = argparse.ArgumentParser(prog="roadmap")
    parser.add_argument("command", choices=("validate", "scenario", "critical-path", "report", "export"))
    parser.add_argument("--name", default="base")
    parser.add_argument("--audience", default="board")
    args = parser.parse_args()
    repository = build_repository()
    output: Any
    if args.command == "validate":
        output = {"status": "valid", "revision": repository.revision}
    elif args.command == "scenario":
        output = scenario_run(repository, args.name)
    elif args.command == "critical-path":
        output = capability_graph(repository)
    elif args.command == "report":
        output = build_reports(repository, args.name).get(args.audience)
    else:
        output = repository.model_dump(mode="json")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
