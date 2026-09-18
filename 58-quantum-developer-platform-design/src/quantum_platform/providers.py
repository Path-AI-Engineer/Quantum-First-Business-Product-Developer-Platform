"""Provider contracts and deterministic local implementations."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Protocol

from quantum_platform.models import JobRequest, Operation


@dataclass(frozen=True)
class ProviderResult:
    submission_id: str
    result: dict[str, object]
    usage: float
    usage_unit: str


class Provider(Protocol):
    name: str

    def submit(self, request: JobRequest, idempotency_key: str) -> ProviderResult: ...


class DeterministicFakeProvider:
    name = "fake"

    def submit(self, request: JobRequest, idempotency_key: str) -> ProviderResult:
        submission_id = "sub_" + hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]
        if request.payload.get("mode") == "permanent_failure":
            raise ValueError("PROVIDER_REQUEST_REJECTED")
        score = int(hashlib.sha256(str(sorted(request.payload.items())).encode()).hexdigest()[:6], 16)
        return ProviderResult(
            submission_id=submission_id,
            result={"normalized": True, "score": score % 10_000, "provider": self.name},
            usage=float(request.payload.get("shots", 1)),
            usage_unit="shots" if "shots" in request.payload else "job",
        )


class LocalQuantumProvider:
    """Bounded local sampler with Aer-compatible count semantics and deterministic seeds."""

    name = "local"

    def submit(self, request: JobRequest, idempotency_key: str) -> ProviderResult:
        if request.operation not in {Operation.CIRCUIT_SAMPLE, Operation.OBSERVABLE_ESTIMATE}:
            raise ValueError("CAPABILITY_UNSUPPORTED")
        shots = int(request.payload.get("shots", 256))
        qubits = int(request.payload.get("qubits", 2))
        if shots < 1 or shots > 4096 or qubits < 1 or qubits > 8:
            raise ValueError("WORKLOAD_LIMIT_EXCEEDED")
        seed = int(hashlib.sha256(idempotency_key.encode()).hexdigest()[:8], 16)
        randomizer = random.Random(seed)
        width = 2**qubits
        counts = {format(i, f"0{qubits}b"): 0 for i in range(width)}
        for _ in range(shots):
            counts[format(randomizer.randrange(width), f"0{qubits}b")] += 1
        submission_id = f"local_{seed:08x}"
        return ProviderResult(
            submission_id=submission_id,
            result={"counts": counts, "seed": seed, "engine": "bounded-local-sampler"},
            usage=float(shots),
            usage_unit="shots",
        )


class ContractStubProvider:
    def __init__(self, name: str) -> None:
        self.name = name

    def submit(self, request: JobRequest, idempotency_key: str) -> ProviderResult:
        del request, idempotency_key
        raise ValueError("PROVIDER_UNAVAILABLE_NO_CREDENTIALS")
