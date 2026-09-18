from __future__ import annotations

from optimization_lab.models import ValueModelInput, ValueModelOutput


def calculate_value(inputs: ValueModelInput) -> ValueModelOutput:
    gross_low = (
        inputs.baseline_cost_per_decision
        * inputs.decisions_per_year
        * inputs.improvement_low
        * inputs.adoption_low
        * inputs.risk_adjustment
    )
    gross_high = (
        inputs.baseline_cost_per_decision
        * inputs.decisions_per_year
        * inputs.improvement_high
        * inputs.adoption_high
        * inputs.risk_adjustment
    )
    net_low = gross_low - inputs.annual_operating_cost
    net_high = gross_high - inputs.annual_operating_cost

    def payback(net: float) -> float | None:
        return round(inputs.integration_cost / net, 3) if net > 0 else None

    denominator = (
        inputs.baseline_cost_per_decision
        * inputs.decisions_per_year
        * max(inputs.improvement_high, 1e-9)
        * inputs.risk_adjustment
    )
    break_even = (inputs.integration_cost / inputs.horizon_years + inputs.annual_operating_cost) / denominator
    break_even_value = round(break_even, 4) if 0 <= break_even <= 1 else None
    cost_per_decision = (
        inputs.integration_cost / inputs.horizon_years + inputs.annual_operating_cost
    ) / inputs.decisions_per_year
    sensitivity: list[dict[str, float | str]] = [
        {"assumption": "adoption", "low_value": round(gross_low, 2), "high_value": round(gross_high, 2)},
        {
            "assumption": "integration_cost",
            "low_value": round(inputs.integration_cost * 0.8, 2),
            "high_value": round(inputs.integration_cost * 1.3, 2),
        },
        {
            "assumption": "risk_adjustment",
            "low_value": round(gross_low * 0.8, 2),
            "high_value": round(gross_high, 2),
        },
    ]
    return ValueModelOutput(
        annualized_value_range=(round(net_low, 2), round(net_high, 2)),
        payback_years_range=(payback(net_high), payback(net_low)),
        break_even_adoption=break_even_value,
        cost_per_decision=round(cost_per_decision, 2),
        assumptions=inputs.model_dump(),
        sensitivity=sensitivity,
        evidence_required=[
            "historical decision volume and current cost",
            "shadow-mode objective improvement",
            "measured adoption and override rate",
            "integration and operating invoices",
        ],
        no_go=net_high <= 0 or break_even_value is None,
        disclaimer="Parametric scenario, not realized savings, financial advice, or a guaranteed return.",
    )
