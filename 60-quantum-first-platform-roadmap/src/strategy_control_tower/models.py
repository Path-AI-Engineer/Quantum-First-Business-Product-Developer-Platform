"""Typed strategy contracts and invariants."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Horizon(StrEnum):
    YEAR_1 = "year_1"
    YEAR_3 = "year_3"
    YEAR_10 = "year_10"


class InitiativeState(StrEnum):
    CANDIDATE = "CANDIDATE"
    COMMITTED = "COMMITTED"
    HOLD = "HOLD"
    KILLED = "KILLED"


class StrategicClass(StrEnum):
    CORE = "core_commitment"
    GROWTH = "growth_bet"
    OPTION = "real_option"
    REGULATORY = "regulatory_obligation"
    ENABLER = "capability_enabler"
    WATCH = "watch_item"


class Maturity(StrEnum):
    ABSENT = "absent"
    EMERGING = "emerging"
    REPEATABLE = "repeatable"
    MANAGED = "managed"
    DIFFERENTIATING = "differentiating"


class CostRange(StrictModel):
    minimum: int = Field(ge=0)
    expected: int = Field(ge=0)
    maximum: int = Field(ge=0)
    currency: str = "USD"

    @model_validator(mode="after")
    def ordered(self) -> CostRange:
        if not self.minimum <= self.expected <= self.maximum:
            raise ValueError("cost range must be ordered")
        return self


class Gate(StrictModel):
    id: str
    name: str
    metric: str
    threshold: float
    owner: str
    cadence: str


class Initiative(StrictModel):
    id: str
    name: str
    horizon: Horizon
    state: InitiativeState
    strategic_class: StrategicClass
    outcome: str
    owner: str
    target_user: str
    metrics: tuple[str, ...]
    dependencies: tuple[str, ...]
    capability_ids: tuple[str, ...]
    cost: CostRange
    headcount_min: float = Field(ge=0)
    headcount_max: float = Field(ge=0)
    gate_ids: tuple[str, ...]
    reversible: bool
    classical_baseline: str | None = None
    kill_condition: str
    exit_plan: str

    @model_validator(mode="after")
    def decision_ready(self) -> Initiative:
        if "quantum" in self.name.lower() and not self.classical_baseline:
            raise ValueError("quantum initiatives require a classical baseline")
        if not self.dependencies or not self.gate_ids or not self.kill_condition:
            raise ValueError("initiative is missing decision evidence")
        return self


class Capability(StrictModel):
    id: str
    name: str
    current: Maturity
    target: Maturity
    prerequisites: tuple[str, ...]
    owner: str
    sourcing: str
    evidence: str
    bottleneck_weight: float = Field(ge=0, le=1)


class Scenario(StrictModel):
    id: str
    name: str
    budget: int = Field(gt=0)
    headcount: float = Field(gt=0)
    adoption_multiplier: float = Field(gt=0)
    compute_multiplier: float = Field(gt=0)
    confidence: str


class Shock(StrictModel):
    id: str
    name: str
    budget_multiplier: float = Field(gt=0)
    cost_multiplier: float = Field(gt=0)
    adoption_multiplier: float = Field(gt=0)
    expected_action: str


class Evidence(StrictModel):
    id: str
    title: str
    source_url: str
    observed_on: str
    confidence: str
    claim_boundary: str


class StrategyRepository(StrictModel):
    schema_version: str
    revision: str
    as_of: str
    approval_status: str
    scenarios: tuple[Scenario, ...]
    shocks: tuple[Shock, ...]
    gates: tuple[Gate, ...]
    capabilities: tuple[Capability, ...]
    initiatives: tuple[Initiative, ...]
    cost_pools: tuple[str, ...]
    providers: tuple[dict[str, str], ...]
    evidence: tuple[Evidence, ...]
    board_questions: tuple[str, ...]
