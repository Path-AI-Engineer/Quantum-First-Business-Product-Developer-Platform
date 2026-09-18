# Distribution routing formulation

- Route decision: ordered customer visits per vehicle from and back to the depot.
- Hard constraints: each customer exactly once and vehicle capacity.
- Objective unit: Manhattan distance over synthetic coordinates.
- Native baseline: OR-Tools routing with capacity dimension and guided local search.
- Heuristic: descending-demand capacity-first allocation.
- Independent checker recomputes coverage, duplicates, and route load.

Time-window and lateness terms are contract-ready but the fixture gate evaluates capacity and coverage. A production pilot must add client-specific travel-time provenance and service windows.
