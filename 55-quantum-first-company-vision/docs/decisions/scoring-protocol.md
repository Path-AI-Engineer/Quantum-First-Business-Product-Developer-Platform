# Scoring protocol v1

Authority: `data/opportunities/protocol.v1.json`. It declares fourteen 0–5
dimensions and positive raw weights. Normalize each weight by the total.
Benefit dimensions keep [low,high]; cost dimensions become [5-high,5-low].
For an unknown dimension, retain the full [0,5] interval, not zero.

Score endpoints = sum(adjusted endpoint / 5 × normalized weight × 100).
Conservative/base/aggressive use 0/0.5/1 interpolation of those endpoints.
These are decision-assumption bounds, not statistical confidence intervals or
probabilistic forecasts. Decimal output aids reconstruction, not market precision.

Every score exposes per-dimension contributions, explicit unknowns, explanation
and supporting/opposing claim references. Positive multipliers change weights
and then renormalize. Out-of-range, NaN and unknown dimension inputs are rejected.

Eight named weight stresses and 28 one-at-a-time perturbations (×0.5, ×1.5)
are reproducible. An unchanged winner does not establish robustness to all
possible assumptions. The intervals overlap: selection remains provisional.
Ties use stable identifiers for display, not a claim of superiority.

This specification and the analyst intervals were authored in one implementation
session, before the first generated comparison. There is no independently
timestamped preregistration or human approval. Do not describe it as such.
A revised protocol needs a reviewed diff and regenerated candidate.

## Current decision

The current base estimate prefers postquantum readiness. Its value does not
require a quantum computer. Baseline alternatives include internal inventory,
existing vendors and consulting. Access and budget are unmeasured.
Optimization remains a plausible pivot but needs a customer's real instance and
a fair classical solver comparison. A hybrid platform must first demonstrate
paid workflow demand beyond existing cloud and SDK tools.

If selection changes, update the explicit decision and dissent, not just the
chart. The exporter fails when the computed winner contradicts the recorded
wedge. The present decision authorizes a discovery recommendation only.
