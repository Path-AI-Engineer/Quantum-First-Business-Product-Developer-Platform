"""Illustrative assumptions, NOT market size or observed unit economics."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from venture_evidence.models import Contract


class EconomicsInput(Contract):
    classification: Literal["illustrative_hypothesis"] = "illustrative_hypothesis"
    organizations: int = Field(default=250, ge=0, le=1_000_000)
    serviceable_fraction: float = Field(default=0.2, ge=0, le=1)
    obtainable_fraction: float = Field(default=0.1, ge=0, le=1)
    annual_price: float = Field(default=12000, gt=0, le=1_000_000)
    hours_per_customer: float = Field(default=80, ge=0, le=10000)
    hourly_cost: float = Field(default=60, ge=0, le=10000)
    tooling_per_customer: float = Field(default=500, ge=0, le=1_000_000)
    customer_capacity: int = Field(default=6, ge=0, le=10000)


def economics(inputs: EconomicsInput) -> dict[str, object]:
    tam = inputs.organizations * inputs.annual_price
    sam = tam * inputs.serviceable_fraction
    demand_customers = inputs.organizations * inputs.serviceable_fraction * inputs.obtainable_fraction
    customers = min(demand_customers, inputs.customer_capacity)
    delivery = inputs.hours_per_customer * inputs.hourly_cost + inputs.tooling_per_customer
    return {
        "classification": inputs.classification,
        "currency": "USD",
        "period": "illustrative annual",
        "inputs": inputs.model_dump(),
        "tam": tam,
        "sam": sam,
        "som": customers * inputs.annual_price,
        "capacity_capped_customers": customers,
        "delivery_cost_per_customer": delivery,
        "gross_margin": (inputs.annual_price - delivery) / inputs.annual_price,
        "exclusions": "Tax, acquisition, founder salary outside delivery, financing and churn not modeled",
        "formulas": {
            "tam": "organizations * annual_price",
            "sam": "tam * serviceable_fraction",
            "som": "min(organizations * serviceable_fraction * obtainable_fraction, capacity) * annual_price",
            "delivery": "hours_per_customer * hourly_cost + tooling_per_customer",
            "margin": "(annual_price - delivery) / annual_price",
        },
        "assumption_ids": ["assumption-market", "assumption-price", "assumption-delivery"],
    }
