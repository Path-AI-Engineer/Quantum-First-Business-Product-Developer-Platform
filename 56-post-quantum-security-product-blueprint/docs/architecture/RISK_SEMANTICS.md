# Falsifiable priority semantics — prototype v1

The engine does not estimate a probability of compromise. It emits a planning
band only for observed legacy public-key mechanisms or unresolved evidence.
No observation means no finding, **not** an assertion that the asset is safe.

First, conflicting algorithms, unidentified mechanisms, stale observations or
only low-confidence evidence are assigned `verify`. This branch takes
precedence over numerical ordering. `unknown` and `conflicting` never produce
an affirmative safety label.

For sufficiently supported legacy observations, the integer planning weight
is: +2 long-lived protected data (10+ years); +2 external exposure; +2 high
business criticality (4–5); +1 vendor dependency; +1 long migration lead time
(12+ months); +1 blast radius 4–5. `urgent` means weight 6+, `high` means 2–5,
and `planned` means 0–1. The report exposes contributing factors and
conservative evidence confidence. The weights are **design hypotheses**,
not calibrated economic loss or NIST thresholds. Compensating controls are
not encoded as an automatic score reduction; a crypto architect must review
their evidence and scope.

The 24 pairwise cases test declared ordering and a separate regression proves
vendor dependency plus lead time can move an otherwise planned item to high.
These are development tests. A blinded gold set and preapproved acceptance
threshold are still needed before calling the model calibrated.
