# Frozen benchmark protocol v1

The corpus contains exactly 90 synthetic instances: 30 workforce scheduling, 30 distribution routing, and 30 portfolio allocation. Each domain has ten small, ten medium, and ten large cases. Sixty-six instances are development evidence; 24 are locked test evidence.

## Comparison rules

- Feasibility is checked independently before objective quality.
- Small instances use the exact solver as oracle.
- Strong classical and heuristic methods receive the same canonical input and objective semantics.
- Strong runs have a declared 80 ms local budget; exact-small runs have 250 ms.
- Runtime, compute profile, status, objective, violations, and reproducibility hash are preserved.
- The QAOA experiment is a four-variable, p=1 local statevector diagnostic with three fixed seeds. It cannot gate service value and carries no advantage claim.
- Test cases remain excluded from interactive benchmark creation and are opened only by the final evidence materialization script.

Any tuning after viewing final test output requires a new protocol version and a new locked test set.
