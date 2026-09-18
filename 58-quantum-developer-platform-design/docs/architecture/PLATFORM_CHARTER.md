# Platform charter

## Promise

The reference lab demonstrates stable, versioned developer contracts around tenant-bound credentials, asynchronous jobs, artifacts, signed events, quotas, usage, and audit evidence. A deterministic fake provider and a bounded local quantum sampler make the golden paths reproducible without a cloud account.

## No-promises

- No claim of perfect provider portability, exactly-once external execution, enterprise SLA, production hardening, or commercial billing.
- IBM Quantum, Amazon Braket, and Azure Quantum are explicit contract stubs until separately configured and validated.
- The control plane accepts allowlisted workload schemas only. It never executes arbitrary Python, shells, containers, or remote commands.

## Users

Organization owners, project administrators, developers, operators/support, usage viewers, and security auditors receive distinct conceptual surfaces. The prototype enforces tenant ownership at every object lookup; production identity federation remains a productization gap.

