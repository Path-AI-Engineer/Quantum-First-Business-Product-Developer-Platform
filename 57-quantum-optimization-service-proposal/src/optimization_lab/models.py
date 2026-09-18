from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Domain(StrEnum):
    SCHEDULING = "workforce_scheduling"
    ROUTING = "distribution_routing"
    PORTFOLIO = "portfolio_allocation"


class Size(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Split(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"


class Feasibility(StrEnum):
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNKNOWN = "UNKNOWN"


class EligibilityOutcome(StrEnum):
    OPTIMIZE_NOW_CLASSICAL = "OPTIMIZE_NOW_CLASSICAL"
    EXPERIMENT_QUANTUM_READY = "EXPERIMENT_QUANTUM_READY"
    DATA_OR_PROCESS_FIRST = "DATA_OR_PROCESS_FIRST"
    DO_NOT_PILOT = "DO_NOT_PILOT"


class ProblemInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "optimization.instance.v1alpha1"
    instance_id: str
    domain: Domain
    size: Size
    split: Split
    scenario_id: str
    business_unit: str = "Fictional Operations"
    currency: str = "USD"
    time_zone: str = "UTC"
    entities: dict[str, Any]
    parameters: dict[str, Any]
    hard_constraints: list[str]
    soft_constraints: list[str]
    objective_terms: list[dict[str, Any]]
    provenance: dict[str, Any]
    expected_feasibility: Feasibility
    sensitive_data_classification: str = "SYNTHETIC_PUBLIC"
    test_locked: bool = False


class SolutionResult(BaseModel):
    instance_id: str
    solver: str
    status: Feasibility
    feasible: bool
    objective: float | None = None
    normalized_objective: float | None = None
    wall_time_ms: float = Field(ge=0)
    compute_profile: str = "local-cpu-single-process"
    estimated_compute_cost_usd: float = 0.0
    seed: int | None = None
    assignments: dict[str, Any] = Field(default_factory=dict)
    violations: list[str] = Field(default_factory=list)
    best_so_far: list[dict[str, float]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class OpportunityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=3, max_length=100)
    domain: Domain
    decision_frequency_per_year: int = Field(ge=1, le=100_000)
    current_cost_per_decision: float = Field(ge=0, le=1_000_000)
    dimensions: dict[str, float | None]


class Opportunity(OpportunityCreate):
    opportunity_id: str


class EligibilityAssessment(BaseModel):
    opportunity_id: str
    outcome: EligibilityOutcome
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    explanation: list[str]
    evidence_gaps: list[str]
    next_experiment: str


class ValueModelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baseline_cost_per_decision: float = Field(gt=0)
    decisions_per_year: int = Field(gt=0)
    improvement_low: float = Field(ge=0, le=1)
    improvement_high: float = Field(ge=0, le=1)
    adoption_low: float = Field(ge=0, le=1)
    adoption_high: float = Field(ge=0, le=1)
    integration_cost: float = Field(ge=0)
    annual_operating_cost: float = Field(ge=0)
    risk_adjustment: float = Field(ge=0, le=1)
    horizon_years: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def ranges_are_ordered(self) -> ValueModelInput:
        if self.improvement_low > self.improvement_high:
            raise ValueError("improvement_low must not exceed improvement_high")
        if self.adoption_low > self.adoption_high:
            raise ValueError("adoption_low must not exceed adoption_high")
        return self


class ValueModelOutput(BaseModel):
    annualized_value_range: tuple[float, float]
    payback_years_range: tuple[float | None, float | None]
    break_even_adoption: float | None
    cost_per_decision: float
    assumptions: dict[str, float | int]
    sensitivity: list[dict[str, float | str]]
    evidence_required: list[str]
    no_go: bool
    disclaimer: str


class PilotCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str
    domain: Domain
    owner: str = Field(min_length=3, max_length=100)
    acceptance_metrics: list[str] = Field(min_length=3)
    rollback_trigger: str = Field(min_length=10)


class PilotPlan(PilotCreate):
    pilot_id: str
    weeks: int = 8
    mode: str = "shadow"
    human_review_required: bool = True
    auto_actuation: bool = False
    termination_criteria: list[str]


class Proposal(BaseModel):
    proposal_id: str
    opportunity_id: str
    recommendation: EligibilityOutcome
    evidence: list[str]
    hypotheses: list[str]
    client_responsibilities: list[str]
    provider_responsibilities: list[str]
    approval: str | None = None
    status: str = "technical_candidate_unapproved"
