# Workforce scheduling formulation

- Binary variable: worker assigned to shift.
- Hard constraints: shift coverage, worker maximum shifts, declared unavailability.
- Soft term: preference and assignment stability.
- Objective unit: synthetic labor-plus-preference score.
- Native baseline: OR-Tools CP-SAT with integer coefficients.
- Heuristic: cheapest eligible worker with load balancing.
- Independent checker recomputes coverage, load, and availability from decoded assignments.

An infeasible result is preserved when demand exceeds available capacity; no repair silently relaxes a hard constraint.
