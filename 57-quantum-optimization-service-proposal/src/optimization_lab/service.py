from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any

import duckdb

from optimization_lab.benchmark import run_benchmark
from optimization_lab.corpus import build_corpus
from optimization_lab.eligibility import assess
from optimization_lab.models import (
    EligibilityAssessment,
    Opportunity,
    OpportunityCreate,
    PilotCreate,
    PilotPlan,
    ProblemInstance,
    Proposal,
    ValueModelInput,
    ValueModelOutput,
)
from optimization_lab.value import calculate_value


class LabService:
    def __init__(self, database_path: str = ":memory:") -> None:
        self._lock = threading.RLock()
        self._connection = duckdb.connect(database_path)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS records "
            "(kind VARCHAR, record_id VARCHAR, payload JSON, PRIMARY KEY (kind, record_id))"
        )
        self.instances = {item.instance_id: item for item in build_corpus()}
        self._sequence = 0

    def _next_id(self, prefix: str) -> str:
        with self._lock:
            self._sequence += 1
            return f"{prefix}-{self._sequence:05d}"

    def _put(self, kind: str, record_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._connection.execute(
                "INSERT OR REPLACE INTO records VALUES (?, ?, ?)",
                [kind, record_id, json.dumps(payload, sort_keys=True)],
            )

    def _get(self, kind: str, record_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT payload FROM records WHERE kind = ? AND record_id = ?", [kind, record_id]
            ).fetchone()
        return json.loads(str(row[0])) if row else None

    def create_opportunity(self, request: OpportunityCreate) -> Opportunity:
        item = Opportunity(opportunity_id=self._next_id("opp"), **request.model_dump())
        self._put("opportunity", item.opportunity_id, item.model_dump(mode="json"))
        return item

    def get_opportunity(self, opportunity_id: str) -> Opportunity | None:
        payload = self._get("opportunity", opportunity_id)
        return Opportunity.model_validate(payload) if payload else None

    def assess_opportunity(self, opportunity_id: str) -> EligibilityAssessment | None:
        item = self.get_opportunity(opportunity_id)
        if item is None:
            return None
        result = assess(item)
        self._put("assessment", opportunity_id, result.model_dump(mode="json"))
        return result

    def create_instance(self, instance: ProblemInstance) -> ProblemInstance:
        if instance.test_locked:
            raise ValueError("external creation cannot mark an instance as locked test evidence")
        self.instances[instance.instance_id] = instance
        return instance

    def create_benchmark(self) -> dict[str, Any]:
        report = run_benchmark(include_locked_test=False)
        benchmark_id = self._next_id("bench")
        report["benchmark_id"] = benchmark_id
        report["lifecycle"] = "COMPLETED_LOCAL"
        self._put("benchmark", benchmark_id, report)
        return report

    def get_benchmark(self, benchmark_id: str) -> dict[str, Any] | None:
        return self._get("benchmark", benchmark_id)

    def create_value_model(self, request: ValueModelInput) -> ValueModelOutput:
        result = calculate_value(request)
        self._put("value", self._next_id("value"), result.model_dump(mode="json"))
        return result

    def create_pilot(self, request: PilotCreate) -> PilotPlan:
        if self.get_opportunity(request.opportunity_id) is None:
            raise KeyError(request.opportunity_id)
        result = PilotPlan(
            pilot_id=self._next_id("pilot"),
            **request.model_dump(),
            termination_criteria=[
                "feasibility rate below the agreed threshold",
                "data error rate exceeds the agreed threshold",
                "integration effort exceeds the approved range",
                "human owner requests rollback",
            ],
        )
        self._put("pilot", result.pilot_id, result.model_dump(mode="json"))
        return result

    def create_proposal(self, opportunity_id: str) -> Proposal:
        assessment_payload = self._get("assessment", opportunity_id)
        if assessment_payload is None:
            assessment = self.assess_opportunity(opportunity_id)
            if assessment is None:
                raise KeyError(opportunity_id)
        else:
            assessment = EligibilityAssessment.model_validate(assessment_payload)
        result = Proposal(
            proposal_id=self._next_id("proposal"),
            opportunity_id=opportunity_id,
            recommendation=assessment.outcome,
            evidence=["synthetic corpus", "local classical benchmark", "parametric value model"],
            hypotheses=["client data can satisfy the canonical contract", "shadow-mode KPI is measurable"],
            client_responsibilities=[
                "provide lawful data",
                "validate constraints",
                "own operational decisions",
            ],
            provider_responsibilities=["reproduce benchmarks", "expose uncertainty", "support rollback"],
        )
        self._put("proposal", result.proposal_id, result.model_dump(mode="json"))
        return result

    def evidence(self, record_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT kind, payload FROM records WHERE record_id = ?", [record_id]
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(str(row[1]))
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return {
            "record_id": record_id,
            "kind": str(row[0]),
            "sha256": hashlib.sha256(canonical).hexdigest(),
            "payload": payload,
        }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            rows = self._connection.execute("SELECT kind, COUNT(*) FROM records GROUP BY kind").fetchall()
        return {
            "product": "Optimization Value Validation Lab",
            "instance_count": len(self.instances),
            "test_locked_count": sum(item.test_locked for item in self.instances.values()),
            "records": {str(kind): int(count) for kind, count in rows},
            "views": [
                "Opportunity Intake",
                "Eligibility Scorecard",
                "Problem Formulation",
                "Constraint & Feasibility Inspector",
                "Benchmark Arena",
                "Solution Comparison",
                "Value & Sensitivity Studio",
                "Quantum-Readiness Gate",
                "Pilot Builder",
                "Proposal & Evidence Export",
            ],
            "boundary": "synthetic local evidence; no operational or financial advice",
        }

    def export_records(self, output: Path) -> None:
        with self._lock:
            rows = self._connection.execute(
                "SELECT kind, record_id, payload FROM records ORDER BY record_id"
            ).fetchall()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                [
                    {"kind": str(kind), "record_id": str(record_id), "payload": json.loads(str(payload))}
                    for kind, record_id, payload in rows
                ],
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
