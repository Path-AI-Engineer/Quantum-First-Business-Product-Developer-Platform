# Pricing Assumptions

Generated from data/evidence/corpus.v1.json. Human approval pending. Planned work is not completed validation. Regenerate with scripts/build_documents.py.

## Reachable market is unknown

ID: assumption-market | State: hypothesis

Organization counts are illustrative planning inputs, not an observed TAM.

- confidence: "C0"
- owner: "founder"
- review on: "2026-12-11"
- validation: "Future interviews and measured pilot"

- claim-cisa-1 (C3, fact): The joint guidance calls for roadmaps, inventories, risk assessment and vendor engagement. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

## Willingness to pay is unmeasured

ID: assumption-price | State: hypothesis

All price intervals need buyer and procurement validation.

- confidence: "C0"
- owner: "founder"
- review on: "2026-12-11"
- validation: "Future interviews and measured pilot"

- claim-cisa-1 (C3, fact): The joint guidance calls for roadmaps, inventories, risk assessment and vendor engagement. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

## Delivery effort is unmeasured

ID: assumption-delivery | State: hypothesis

Hours and unit costs need a time-tracked assisted pilot.

- confidence: "C0"
- owner: "founder"
- review on: "2026-12-11"
- validation: "Future interviews and measured pilot"

- claim-cisa-1 (C3, fact): The joint guidance calls for roadmaps, inventories, risk assessment and vendor engagement. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

## Buyer access is unknown

ID: assumption-access | State: hypothesis

Founder has not demonstrated access to a qualified buying committee.

- confidence: "C0"
- owner: "founder"
- review on: "2026-12-11"
- validation: "Future interviews and measured pilot"

- claim-cisa-1 (C3, fact): The joint guidance calls for roadmaps, inventories, risk assessment and vendor engagement. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

## Evidence workflow may differentiate

ID: assumption-moat | State: hypothesis

Defensibility depends on repeat use and permissioned operational learning.

- confidence: "C0"
- owner: "founder"
- review on: "2026-12-11"
- validation: "Future interviews and measured pilot"

- claim-cisa-1 (C3, fact): The joint guidance calls for roadmaps, inventories, risk assessment and vendor engagement. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

## Fixed-price assessment

ID: pricing-assessment | State: hypothesis

Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.

- anchor: "Existing consultant or internal team"
- buyer: "CISO with procurement approval"
- delivery hours range: [40, 120]
- formula: "margin = (price - hours * hourly_cost - tooling) / price"
- hourly cost range usd: [40, 100]
- human dependency: "Expert scoping, validation and change approval remain necessary"
- margin target range: [0.4, 0.65]
- price range usd: [6000, 18000]
- tooling cost range usd: [100, 1000]
- validation: "Obtain opt-in pilot procurement feedback and time-track delivery"
- value unit: "Scoped service inventory and roadmap"
- volume sensitivity: "Delivery hours and capacity must be remeasured before volume discounts"

- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

Related: assumption-price, assumption-delivery

## Pilot fee with acceptance criteria

ID: pricing-pilot | State: hypothesis

Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.

- anchor: "Existing integrator"
- buyer: "CISO with procurement approval"
- delivery hours range: [80, 240]
- formula: "margin = (price - hours * hourly_cost - tooling) / price"
- hourly cost range usd: [40, 100]
- human dependency: "Expert scoping, validation and change approval remain necessary"
- margin target range: [0.4, 0.65]
- price range usd: [12000, 30000]
- tooling cost range usd: [100, 1000]
- validation: "Obtain opt-in pilot procurement feedback and time-track delivery"
- value unit: "Two services with reviewed acceptance evidence"
- volume sensitivity: "Delivery hours and capacity must be remeasured before volume discounts"

- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

Related: assumption-price, assumption-delivery

## Organization subscription / year

ID: pricing-subscription | State: hypothesis

Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.

- anchor: "Asset management workflow"
- buyer: "CISO with procurement approval"
- delivery hours range: [20, 80]
- formula: "margin = (price - hours * hourly_cost - tooling) / price"
- hourly cost range usd: [40, 100]
- human dependency: "Expert scoping, validation and change approval remain necessary"
- margin target range: [0.4, 0.65]
- price range usd: [6000, 24000]
- tooling cost range usd: [100, 1000]
- validation: "Obtain opt-in pilot procurement feedback and time-track delivery"
- value unit: "Recurring change and inventory review"
- volume sensitivity: "Delivery hours and capacity must be remeasured before volume discounts"

- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

Related: assumption-price, assumption-delivery

## Managed service / year

ID: pricing-managed | State: hypothesis

Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.

- anchor: "Security managed service provider"
- buyer: "CISO with procurement approval"
- delivery hours range: [200, 600]
- formula: "margin = (price - hours * hourly_cost - tooling) / price"
- hourly cost range usd: [40, 100]
- human dependency: "Expert scoping, validation and change approval remain necessary"
- margin target range: [0.4, 0.65]
- price range usd: [24000, 72000]
- tooling cost range usd: [100, 1000]
- validation: "Obtain opt-in pilot procurement feedback and time-track delivery"
- value unit: "Owned review cadence with agreed service levels"
- volume sensitivity: "Delivery hours and capacity must be remeasured before volume discounts"

- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

Related: assumption-price, assumption-delivery

## Platform consumption / reviewed job

ID: pricing-consumption | State: hypothesis

Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.

- anchor: "Provider-native metering"
- buyer: "CISO with procurement approval"
- delivery hours range: [0.5, 5]
- formula: "margin = (price - hours * hourly_cost - tooling) / price"
- hourly cost range usd: [40, 100]
- human dependency: "Expert scoping, validation and change approval remain necessary"
- margin target range: [0.4, 0.65]
- price range usd: [50, 500]
- tooling cost range usd: [100, 1000]
- validation: "Obtain opt-in pilot procurement feedback and time-track delivery"
- value unit: "Metered, bounded evidence job"
- volume sensitivity: "Delivery hours and capacity must be remeasured before volume discounts"

- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

Related: assumption-price, assumption-delivery

## Enterprise license / year

ID: pricing-enterprise | State: hypothesis

Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.

- anchor: "Internal platform / incumbent bundle"
- buyer: "CISO with procurement approval"
- delivery hours range: [100, 400]
- formula: "margin = (price - hours * hourly_cost - tooling) / price"
- hourly cost range usd: [40, 100]
- human dependency: "Expert scoping, validation and change approval remain necessary"
- margin target range: [0.4, 0.65]
- price range usd: [30000, 120000]
- tooling cost range usd: [100, 1000]
- validation: "Obtain opt-in pilot procurement feedback and time-track delivery"
- value unit: "Contracted deployment and support"
- volume sensitivity: "Delivery hours and capacity must be remeasured before volume discounts"

- claim-finops-2 (C3, fact): The framework includes cost allocation, forecasting and unit economics capabilities. [FinOps Foundation](https://www.finops.org/framework/)

Related: assumption-price, assumption-delivery

