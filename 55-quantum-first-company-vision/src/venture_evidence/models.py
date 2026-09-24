"""Versioned evidence contracts; absent measurements stay explicitly unknown."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, JsonValue, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]+$")]
Confidence = Literal["C0", "C1", "C2", "C3", "C4"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Source(Contract):
    id: Identifier
    title: str
    publisher: str
    url: HttpUrl
    accessed_on: date
    published_on: date | None = None
    classification: Literal["primary", "secondary"]
    scope: str
    access_note: str


class Evidence(Contract):
    id: Identifier
    source_id: Identifier
    paraphrase: Annotated[str, Field(min_length=20)]
    locator: str
    stance: Literal["supports", "contradicts", "context"]
    confidence: Confidence
    limitations: str


class Claim(Contract):
    id: Identifier
    text: Annotated[str, Field(min_length=10)]
    kind: Literal["fact", "inference", "hypothesis"]
    external: bool
    confidence: Confidence
    source_ids: list[Identifier]
    supporting_evidence: list[Identifier]
    opposing_evidence: list[Identifier]
    accessed_on: date | None
    scope: str
    owner: str
    review_on: date
    validity: str

    @model_validator(mode="after")
    def grounded(self) -> Self:
        if self.confidence == "C4":
            raise ValueError("Direct buyer validation is outside this laboratory; C4 is forbidden")
        if self.external and (not self.source_ids or self.accessed_on is None):
            raise ValueError("External claims need sources and an access date")
        if self.kind == "fact" and (self.confidence not in ("C2", "C3") or not self.supporting_evidence):
            raise ValueError("Facts require qualifying evidence, never repeated C0/C1 hypotheses")
        return self


class Entity(Contract):
    id: Identifier
    entity_type: Literal[
        "assumption",
        "customer_profile",
        "job_to_be_done",
        "pain",
        "alternative",
        "competitor",
        "capability",
        "experiment",
        "risk",
        "decision",
        "handoff_contract",
        "buying_pattern",
        "workflow",
        "inaction",
        "discovery_question",
        "interview_plan",
        "pricing",
        "product_stage",
        "moat",
        "challenge",
        "objection",
        "trace",
    ]
    title: str
    description: str
    status: Literal["hypothesis", "inference", "planned", "candidate", "documented"]
    claim_ids: list[Identifier]
    related_ids: list[Identifier] = Field(default_factory=list)
    details: dict[str, JsonValue] = Field(default_factory=dict)


class Interval(Contract):
    low: Annotated[float, Field(ge=0, le=5)]
    high: Annotated[float, Field(ge=0, le=5)]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.low > self.high:
            raise ValueError("Interval bounds are reversed")
        return self


class Opportunity(Contract):
    id: Identifier
    name: str
    promise: str
    classical_alternative: str
    maturity_condition: str
    kill_gate: str
    primary_icp: Identifier
    secondary_icp: Identifier
    claim_ids: list[Identifier]
    opposing_claim_ids: list[Identifier]
    dimensions: dict[str, Interval | None]
    rationale: dict[str, str]


class Dimension(Contract):
    id: Identifier
    label: str
    weight: Annotated[float, Field(gt=0)]
    direction: Literal["benefit", "cost"]


class StressCase(Contract):
    id: Identifier
    title: str
    multipliers: dict[str, Annotated[float, Field(gt=0, le=5)]]


class Protocol(Contract):
    version: Literal["decision-protocol-v1"]
    status: Literal["analyst_specification_not_buyer_validation"]
    dimensions: list[Dimension]
    scenarios: dict[str, Annotated[float, Field(ge=0, le=1)]]
    stress_cases: list[StressCase]
    unknown_rule: str
    tie_rule: str


class Corpus(Contract):
    schema_version: Literal["venture.corpus.v1"]
    research_date: date
    scope: str
    buyer_interviews_completed: Literal[0]
    paying_customers_validated: Literal[0]
    approval: Literal["pending_human_review"]
    sources: list[Source]
    evidence: list[Evidence]
    claims: list[Claim]
    entities: list[Entity]
    opportunities: list[Opportunity]
