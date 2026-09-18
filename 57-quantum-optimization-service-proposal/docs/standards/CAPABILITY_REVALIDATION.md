# Capability revalidation — 2026-09-18

Primary documentation checked for the protocol:

- Google OR-Tools CP-SAT documents integer modeling and explicit `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `MODEL_INVALID`, and `UNKNOWN` statuses: <https://developers.google.com/optimization/cp/cp_solver>
- OR-Tools recommends its routing library for typical routing problems and exposes MIP/CP alternatives: <https://developers.google.com/optimization/cp>
- IBM's current Qiskit reference exposes `StatevectorSampler`; the project nevertheless uses a small dependency-free local statevector diagnostic and makes no provider claim: <https://qiskit.qotlabs.org/docs/api/qiskit/qiskit.primitives.StatevectorSampler>
- Amazon Braket Hybrid Jobs provisions billable classical and quantum resources; this project does not submit a job: <https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs.html>
- Azure Quantum is a cloud service requiring an account/workspace for submitted jobs, while the QDK can be used without an Azure account; this project creates no workspace or job: <https://learn.microsoft.com/en-us/azure/quantum/overview-azure-quantum>
- Microsoft's resource estimator models future fault-tolerant resource requirements and is not evidence of runtime advantage: <https://learn.microsoft.com/en-us/azure/quantum/overview-resources-estimator>

Capabilities, availability, and pricing are time-sensitive. Revalidate them before any external proposal or paid execution.
