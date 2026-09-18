"""Minimal local CLI for the documented golden paths."""

from __future__ import annotations

import argparse
import json

from quantum_platform.control_plane import ControlPlane
from quantum_platform.models import Environment, JobRequest


def main() -> None:
    parser = argparse.ArgumentParser(prog="qdp")
    parser.add_argument("command", choices=["capabilities", "demo"])
    args = parser.parse_args()
    plane = ControlPlane()
    if args.command == "capabilities":
        print(json.dumps([item.model_dump(mode="json") for item in plane.capabilities()], indent=2))
        return
    organization = plane.create_organization("CLI Demo")
    project = plane.create_project(organization.id, "sandbox", Environment.SANDBOX)
    job = plane.submit_job(
        project.id,
        JobRequest(operation="circuit.sample", provider="local", payload={"qubits": 2, "shots": 64}),
        "cli-demo-1",
    )
    print(job.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
