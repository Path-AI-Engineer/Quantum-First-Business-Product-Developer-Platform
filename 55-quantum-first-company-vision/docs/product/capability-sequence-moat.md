# Capability Sequence Moat

Generated from data/evidence/corpus.v1.json. Human approval pending. Planned work is not completed validation. Regenerate with scripts/build_documents.py.

## PQC inventory and migration planning

ID: capability-pqc | State: inference

Capability classification is an analyst assessment.

- classical baseline: "Classical inventory and vendor coordination"
- kill gate: "Pause if inventory cannot be obtained with consent"
- maturity: "available-now"
- maturity gate: "Approved scope, tested compatibility, cryptographic expert review"
- trl: null
- trl note: "No formal TRL assessment performed"
- vendor risk: "Recheck support and interoperability before any adoption"

- claim-nist-3 (C3, fact): NIST recommends identifying vulnerable cryptography and beginning migration planning. [NIST](https://csrc.nist.gov/projects/post-quantum-cryptography)

## Quantum-ready optimization assessment

ID: capability-optimization | State: inference

Capability classification is an analyst assessment.

- classical baseline: "OR-Tools / commercial solver baseline"
- kill gate: "Do not sell quantum uplift when classical baseline wins"
- maturity: "available-now"
- maturity gate: "Repeated feasible improvement after equal-budget comparison"
- trl: null
- trl note: "No formal TRL assessment performed"
- vendor risk: "Recheck support and interoperability before any adoption"

- claim-ortools-1 (C3, fact): OR-Tools supplies open-source classical optimization for routing, flows and constrained scheduling. [Google](https://developers.google.com/optimization)

## Hybrid execution abstraction

ID: capability-platform | State: inference

Capability classification is an analyst assessment.

- classical baseline: "Classical jobs and provider-native tools"
- kill gate: "Stop if native tools cover the entire job at lower cost"
- maturity: "experimental"
- maturity gate: "Paid repeat workflow and portable contracts"
- trl: null
- trl note: "No formal TRL assessment performed"
- vendor risk: "Recheck support and interoperability before any adoption"

- claim-braket-1 (C3, fact): Braket offers a common service for simulators and different quantum hardware providers. [AWS](https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html)

## Broad fault-tolerant quantum advantage

ID: capability-advantage | State: inference

Capability classification is an analyst assessment.

- classical baseline: "Use best available classical implementation"
- kill gate: "No roadmap date or revenue dependency before evidence"
- maturity: "speculative"
- maturity gate: "Independent reproducible advantage at total workload cost"
- trl: null
- trl note: "No formal TRL assessment performed"
- vendor risk: "Recheck support and interoperability before any adoption"

- claim-braket-2 (C3, fact): AWS describes hardware noise and hybrid algorithm limitations in its introductory guide. [AWS](https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html)

## Assisted evidence service

ID: stage-0 | State: planned

Conditional sequence, not a promised release date.

- build: "Templates and validation"
- buy partner: "Existing inventory tooling"
- gate: "Consented paid pilot and measured scope"
- months: [0, 6]
- quantum gate: "Independent reproducible workload advantage and affordable total cost; classical fallback remains"

- claim-finops-1 (C3, fact): FinOps connects engineering, finance and business around technology value and financial accountability. [FinOps Foundation](https://www.finops.org/framework/)
- claim-braket-2 (C3, fact): AWS describes hardware noise and hybrid algorithm limitations in its introductory guide. [AWS](https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html)

## Repeatable readiness product

ID: stage-6 | State: planned

Conditional sequence, not a promised release date.

- build: "Change tracking and evidence workflow"
- buy partner: "Maintained crypto libraries"
- gate: "Repeated paid delivery with sustainable margins"
- months: [6, 18]
- quantum gate: "Independent reproducible workload advantage and affordable total cost; classical fallback remains"

- claim-finops-1 (C3, fact): FinOps connects engineering, finance and business around technology value and financial accountability. [FinOps Foundation](https://www.finops.org/framework/)
- claim-braket-2 (C3, fact): AWS describes hardware noise and hybrid algorithm limitations in its introductory guide. [AWS](https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html)

## Shared platform and suite

ID: stage-18 | State: planned

Conditional sequence, not a promised release date.

- build: "Contract adapters and permissioned benchmark corpus"
- buy partner: "Cloud execution only when budgeted"
- gate: "Multiple repeatable workflows, portability and support economics"
- months: [18, 36]
- quantum gate: "Independent reproducible workload advantage and affordable total cost; classical fallback remains"

- claim-finops-1 (C3, fact): FinOps connects engineering, finance and business around technology value and financial accountability. [FinOps Foundation](https://www.finops.org/framework/)
- claim-braket-2 (C3, fact): AWS describes hardware noise and hybrid algorithm limitations in its introductory guide. [AWS](https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html)

## Permissioned migration compatibility data

ID: moat-01 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Domain models and transparent benchmarks

ID: moat-02 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Integration with critical review workflows

ID: moat-03 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Portable provider contracts and developer experience

ID: moat-04 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Audit trail with decision provenance

ID: moat-05 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Trusted partner distribution

ID: moat-06 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Maintained regulatory mapping

ID: moat-07 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

## Legitimate switching costs from useful workflow history

ID: moat-08 | State: hypothesis

Candidate accumulating asset; none is claimed defensible today.

- commoditization test: "Can an incumbent reproduce the outcome within a quarter?"
- data rights: "Only permissioned or public evidence; no client reuse without contract"
- exit: "Open formats and export; no artificial lock-in"

- claim-cisa-3 (C3, fact): Migration planning should account for vendor upgrade paths and associated costs. [CISA / NSA / NIST](https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF)
- claim-qiskit-2 (C3, fact): Qiskit documents plugins connecting classical and quantum execution resources. [IBM](https://www.ibm.com/quantum/qiskit)

