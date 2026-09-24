"""Interval arithmetic, scenario interpolation and explicit weight perturbations."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from venture_evidence.models import Contract, Corpus, Opportunity, Protocol

Scenario = Literal["conservative", "base", "aggressive"]


class Contribution(Contract):
    dimension: str
    weight: float
    known: bool
    low: float
    high: float
    explanation: str


class Score(Contract):
    id: str
    name: str
    scenario: str
    low: float
    high: float
    estimate: float
    known_weight_fraction: float = Field(ge=0, le=1)
    unknown_dimensions: list[str]
    contributions: list[Contribution]


class StressResult(Contract):
    id: str
    title: str
    winner: str
    scores: list[Score]


class SensitivityResult(Contract):
    reference_winner: str
    intervals_overlap: bool
    interpretation: str
    one_at_a_time_cases: int = Field(ge=0)
    rank_flips: list[str]
    stress_cases: list[StressResult]


def score(
    opportunity: Opportunity,
    protocol: Protocol,
    scenario: Scenario = "base",
    multipliers: dict[str, float] | None = None,
) -> Score:
    multipliers = multipliers or {}
    if set(multipliers) - {d.id for d in protocol.dimensions}:
        raise ValueError("Unknown scoring dimension")
    if any(not 0 < x <= 5 for x in multipliers.values()):
        raise ValueError("Weight multipliers must be in (0, 5]")
    weights = {d.id: d.weight * multipliers.get(d.id, 1.0) for d in protocol.dimensions}
    total = sum(weights.values())
    parts: list[Contribution] = []
    for dimension in protocol.dimensions:
        value = opportunity.dimensions[dimension.id]
        low, high = (value.low, value.high) if value is not None else (0.0, 5.0)
        if dimension.direction == "cost":
            low, high = 5 - high, 5 - low
        weight = weights[dimension.id] / total
        parts.append(
            Contribution(
                dimension=dimension.id,
                weight=weight,
                known=value is not None,
                low=low * 20 * weight,
                high=high * 20 * weight,
                explanation=opportunity.rationale[dimension.id],
            )
        )
    low, high = sum(p.low for p in parts), sum(p.high for p in parts)
    alpha = protocol.scenarios[scenario]
    return Score(
        id=opportunity.id,
        name=opportunity.name,
        scenario=scenario,
        low=round(low, 4),
        high=round(high, 4),
        estimate=round(low + alpha * (high - low), 4),
        known_weight_fraction=min(1.0, sum(p.weight for p in parts if p.known)),
        unknown_dimensions=[p.dimension for p in parts if not p.known],
        contributions=parts,
    )


def compare(
    corpus: Corpus, protocol: Protocol, scenario: Scenario = "base", multipliers: dict[str, float] | None = None
) -> list[Score]:
    return sorted(
        [score(o, protocol, scenario, multipliers) for o in corpus.opportunities],
        key=lambda item: (-item.estimate, item.id),
    )


def sensitivity(corpus: Corpus, protocol: Protocol) -> dict[str, object]:
    reference = compare(corpus, protocol)
    rows: list[dict[str, object]] = []
    for case in protocol.stress_cases:
        ranking = compare(corpus, protocol, multipliers=case.multipliers)
        rows.append(
            {"id": case.id, "title": case.title, "winner": ranking[0].id, "scores": [s.model_dump() for s in ranking]}
        )
    flips: list[str] = []
    for dimension in protocol.dimensions:
        for multiplier in (0.5, 1.5):
            if compare(corpus, protocol, multipliers={dimension.id: multiplier})[0].id != reference[0].id:
                flips.append(f"{dimension.id}:{multiplier}")
    overlap = any(reference[0].low <= other.high for other in reference[1:])
    return {
        "reference_winner": reference[0].id,
        "intervals_overlap": overlap,
        "interpretation": "provisional; overlapping intervals are not proof of market superiority",
        "one_at_a_time_cases": len(protocol.dimensions) * 2,
        "rank_flips": flips,
        "stress_cases": rows,
    }
