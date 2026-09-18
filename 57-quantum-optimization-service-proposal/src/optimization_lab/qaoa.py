from __future__ import annotations

import math
from typing import Any

import numpy as np


def qubo_resource_report(linear: list[float], quadratic: dict[tuple[int, int], float]) -> dict[str, Any]:
    coefficients = [*linear, *quadratic.values()]
    nonzero = [abs(value) for value in coefficients if value]
    return {
        "variables": len(linear),
        "couplers": len([value for value in quadratic.values() if value]),
        "coefficient_min_abs": min(nonzero) if nonzero else 0.0,
        "coefficient_max_abs": max(nonzero) if nonzero else 0.0,
        "coefficient_dynamic_range": (max(nonzero) / min(nonzero)) if nonzero else 0.0,
        "mapping": "binary QUBO diagnostic subproblem",
    }


def _costs(linear: list[float], quadratic: dict[tuple[int, int], float]) -> np.ndarray:
    count = len(linear)
    result = np.zeros(2**count, dtype=np.float64)
    for state in range(2**count):
        bits = [(state >> index) & 1 for index in range(count)]
        result[state] = sum(weight * bits[index] for index, weight in enumerate(linear)) + sum(
            weight * bits[left] * bits[right] for (left, right), weight in quadratic.items()
        )
    return result


def _apply_mixer(state: np.ndarray, qubits: int, beta: float) -> np.ndarray:
    mixed = state.copy()
    cosine = math.cos(beta)
    sine = -1j * math.sin(beta)
    for qubit in range(qubits):
        stride = 1 << qubit
        for block in range(0, len(mixed), stride * 2):
            for offset in range(stride):
                zero = block + offset
                one = zero + stride
                a, b = mixed[zero], mixed[one]
                mixed[zero] = cosine * a + sine * b
                mixed[one] = sine * a + cosine * b
    return mixed


def run_qaoa_candidate(
    linear: list[float],
    quadratic: dict[tuple[int, int], float],
    *,
    seed: int,
    shots: int = 512,
) -> dict[str, Any]:
    """Run a bounded p=1 statevector QAOA diagnostic; no hardware or advantage claim."""
    if not 1 <= len(linear) <= 8:
        raise ValueError("local diagnostic is limited to 1..8 QUBO variables")
    costs = _costs(linear, quadratic)
    initial = np.ones(len(costs), dtype=np.complex128) / math.sqrt(len(costs))
    best_expectation = math.inf
    best_probabilities: np.ndarray | None = None
    best_angles = (0.0, 0.0)
    for gamma in np.linspace(0.0, math.pi * 2, 9, endpoint=False):
        phased = initial * np.exp(-1j * gamma * costs)
        for beta in np.linspace(0.0, math.pi, 9, endpoint=False):
            state = _apply_mixer(phased, len(linear), float(beta))
            probabilities = np.abs(state) ** 2
            expectation = float(np.dot(probabilities, costs))
            if expectation < best_expectation:
                best_expectation = expectation
                best_probabilities = probabilities
                best_angles = (float(gamma), float(beta))
    if best_probabilities is None:
        raise RuntimeError("QAOA grid search produced no state")
    rng = np.random.default_rng(seed)
    samples = rng.choice(len(costs), size=shots, p=best_probabilities / best_probabilities.sum())
    sampled_state = int(min(samples, key=lambda state: costs[int(state)]))
    exact_state = int(np.argmin(costs))
    return {
        "candidate": "qaoa_p1_local_statevector",
        "seed": seed,
        "shots": shots,
        "gamma": best_angles[0],
        "beta": best_angles[1],
        "sampled_state": format(sampled_state, f"0{len(linear)}b")[::-1],
        "sampled_objective": float(costs[sampled_state]),
        "exact_objective": float(costs[exact_state]),
        "expectation": best_expectation,
        "advantage_claim": False,
        "conclusion": "diagnostic only; strong classical methods remain the service baseline",
        "resources": qubo_resource_report(linear, quadratic),
    }
