from __future__ import annotations

from optimization_lab.models import EligibilityAssessment, EligibilityOutcome, Opportunity

DIMENSIONS = (
    "decision_value",
    "outcome_controllability",
    "data_quality",
    "data_latency",
    "constraint_stability",
    "combinatorial_structure",
    "baseline_maturity",
    "integration_readiness",
    "error_tolerance",
    "human_validation",
    "current_solution_cost",
    "qubo_fit",
    "organizational_maturity",
)

WEIGHTS = {
    "decision_value": 0.12,
    "outcome_controllability": 0.09,
    "data_quality": 0.12,
    "data_latency": 0.05,
    "constraint_stability": 0.10,
    "combinatorial_structure": 0.09,
    "baseline_maturity": 0.08,
    "integration_readiness": 0.08,
    "error_tolerance": 0.05,
    "human_validation": 0.08,
    "current_solution_cost": 0.05,
    "qubo_fit": 0.04,
    "organizational_maturity": 0.05,
}


def assess(opportunity: Opportunity) -> EligibilityAssessment:
    known = {name: opportunity.dimensions.get(name) for name in DIMENSIONS}
    invalid = [name for name, value in known.items() if value is not None and not 0 <= value <= 1]
    if invalid:
        raise ValueError(f"dimension scores must be in [0, 1]: {', '.join(invalid)}")
    available = {name: float(value) for name, value in known.items() if value is not None}
    confidence = len(available) / len(DIMENSIONS)
    weighted_total = sum(WEIGHTS[name] * value for name, value in available.items())
    available_weight = sum(WEIGHTS[name] for name in available)
    score = weighted_total / available_weight if available_weight else 0.0
    gaps = [name for name, value in known.items() if value is None]
    explanation: list[str] = [
        f"weighted eligibility score={score:.3f}",
        f"evidence coverage={confidence:.3f}",
    ]

    def value(name: str) -> float:
        item = known[name]
        return float(item) if item is not None else 0.0

    explicit_stop = (known["human_validation"] is not None and value("human_validation") < 0.25) or (
        known["outcome_controllability"] is not None and value("outcome_controllability") < 0.25
    )
    if explicit_stop:
        outcome = EligibilityOutcome.DO_NOT_PILOT
        next_experiment = "Prove outcome control and a human validation path before modeling a pilot."
        explanation.append("minimum controllability or human-validation gate failed")
    elif value("data_quality") < 0.5 or value("constraint_stability") < 0.45 or confidence < 0.65:
        outcome = EligibilityOutcome.DATA_OR_PROCESS_FIRST
        next_experiment = "Run a data-readiness and constraint-definition sprint with sampled decisions."
        explanation.append("data, constraint, or evidence coverage gate failed")
    elif score >= 0.70 and value("qubo_fit") >= 0.65 and value("baseline_maturity") >= 0.60:
        outcome = EligibilityOutcome.EXPERIMENT_QUANTUM_READY
        next_experiment = "Benchmark a bounded QUBO subproblem after freezing the strong classical baseline."
        explanation.append("quantum-ready experiment gate passed; no advantage is implied")
    elif score >= 0.55:
        outcome = EligibilityOutcome.OPTIMIZE_NOW_CLASSICAL
        next_experiment = "Run a shadow-mode classical benchmark against the current decision process."
        explanation.append("classical optimization readiness gate passed")
    else:
        outcome = EligibilityOutcome.DATA_OR_PROCESS_FIRST
        next_experiment = "Resolve the lowest-scoring readiness dimensions before a solver pilot."
        explanation.append("aggregate readiness is below the pilot threshold")

    return EligibilityAssessment(
        opportunity_id=opportunity.opportunity_id,
        outcome=outcome,
        score=round(score, 4),
        confidence=round(confidence, 4),
        explanation=explanation,
        evidence_gaps=gaps,
        next_experiment=next_experiment,
    )
