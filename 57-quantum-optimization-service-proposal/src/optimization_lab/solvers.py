from __future__ import annotations

import math
import time
from collections.abc import Callable
from itertools import pairwise
from typing import Any

from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore[import-untyped]
from ortools.sat.python import cp_model

from optimization_lab.models import Domain, Feasibility, ProblemInstance, SolutionResult


def _result(
    instance: ProblemInstance,
    solver: str,
    started: float,
    assignments: dict[str, Any] | None,
    objective: float | None,
    violations: list[str],
    notes: list[str] | None = None,
) -> SolutionResult:
    feasible = not violations and assignments is not None
    return SolutionResult(
        instance_id=instance.instance_id,
        solver=solver,
        status=Feasibility.FEASIBLE if feasible else Feasibility.INFEASIBLE,
        feasible=feasible,
        objective=objective if feasible else None,
        normalized_objective=(1 / (1 + max(objective or 0, 0))) if feasible else None,
        wall_time_ms=(time.perf_counter() - started) * 1000,
        assignments=assignments or {},
        violations=violations,
        best_so_far=[{"elapsed_ms": (time.perf_counter() - started) * 1000, "objective": objective or 0.0}]
        if feasible
        else [],
        notes=notes or [],
    )


def check_feasibility(instance: ProblemInstance, assignments: dict[str, Any]) -> list[str]:
    if instance.domain is Domain.SCHEDULING:
        workers = len(instance.entities["workers"])
        shifts = len(instance.entities["shifts"])
        demand = instance.parameters["demand"]
        maximum = int(instance.parameters["max_shifts_per_worker"])
        unavailable = {tuple(pair) for pair in instance.parameters["unavailable"]}
        pairs = {tuple(pair) for pair in assignments.get("worker_shift", [])}
        violations = []
        for shift in range(shifts):
            if sum((worker, shift) in pairs for worker in range(workers)) < demand[shift]:
                violations.append(f"coverage:{shift}")
        for worker in range(workers):
            if sum((worker, shift) in pairs for shift in range(shifts)) > maximum:
                violations.append(f"max_shifts:{worker}")
        if pairs & unavailable:
            violations.append("availability")
        return violations
    if instance.domain is Domain.ROUTING:
        customers = set(instance.entities["customers"])
        routes = assignments.get("routes", [])
        visited = [customer for route in routes for customer in route if customer != 0]
        violations = []
        if len(visited) != len(set(visited)) or set(visited) != customers:
            violations.append("customer_coverage")
        demands = instance.parameters["demands"]
        capacity = int(instance.parameters["vehicle_capacity"])
        for route_index, route in enumerate(routes):
            load = sum(demands[customer - 1] for customer in route if customer != 0)
            if load > capacity:
                violations.append(f"capacity:{route_index}")
        return violations
    selected = [int(value) for value in assignments.get("selected_assets", [])]
    returns = instance.parameters["returns"]
    sectors = instance.parameters["sectors"]
    violations = []
    if len(selected) > int(instance.parameters["max_assets"]):
        violations.append("cardinality")
    if sum(returns[index] for index in selected) < int(instance.parameters["minimum_return"]):
        violations.append("minimum_return")
    for sector in set(sectors):
        if sum(sectors[index] == sector for index in selected) > int(instance.parameters["max_per_sector"]):
            violations.append(f"sector:{sector}")
    return violations


def _solve_scheduling(instance: ProblemInstance, time_limit: float, solver_name: str) -> SolutionResult:
    started = time.perf_counter()
    workers = len(instance.entities["workers"])
    shifts = len(instance.entities["shifts"])
    model = cp_model.CpModel()
    variables = {
        (worker, shift): model.new_bool_var(f"x_{worker}_{shift}")
        for worker in range(workers)
        for shift in range(shifts)
    }
    for shift, required in enumerate(instance.parameters["demand"]):
        model.add(sum(variables[worker, shift] for worker in range(workers)) >= required)
    maximum = int(instance.parameters["max_shifts_per_worker"])
    for worker in range(workers):
        model.add(sum(variables[worker, shift] for shift in range(shifts)) <= maximum)
    for worker, shift in instance.parameters["unavailable"]:
        model.add(variables[worker, shift] == 0)
    costs = instance.parameters["costs"]
    preferences = instance.parameters["preferences"]
    model.minimize(
        sum(
            (costs[worker] + preferences[worker][shift]) * variables[worker, shift]
            for worker in range(workers)
            for shift in range(shifts)
        )
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    if solver.status_name(status) not in {"OPTIMAL", "FEASIBLE"}:
        return _result(instance, solver_name, started, None, None, ["proven_or_budgeted_infeasible"])
    pairs = [
        [worker, shift]
        for worker in range(workers)
        for shift in range(shifts)
        if solver.value(variables[worker, shift])
    ]
    assignments = {"worker_shift": pairs}
    return _result(
        instance,
        solver_name,
        started,
        assignments,
        float(solver.objective_value),
        check_feasibility(instance, assignments),
    )


def _distance_matrix(coordinates: list[list[int]]) -> list[list[int]]:
    return [[abs(ax - bx) + abs(ay - by) for bx, by in coordinates] for ax, ay in coordinates]


def _solve_routing(instance: ProblemInstance, time_limit: float, solver_name: str) -> SolutionResult:
    started = time.perf_counter()
    customers = len(instance.entities["customers"])
    vehicles = len(instance.entities["vehicles"])
    demands = [0, *instance.parameters["demands"]]
    capacity = int(instance.parameters["vehicle_capacity"])
    if sum(demands) > vehicles * capacity:
        return _result(instance, solver_name, started, None, None, ["aggregate_capacity"])
    distances = _distance_matrix(instance.parameters["coordinates"])
    manager = pywrapcp.RoutingIndexManager(customers + 1, vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        return int(distances[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)])

    distance_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_index)

    def demand_callback(index: int) -> int:
        return int(demands[manager.IndexToNode(index)])

    demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_index, 0, [capacity] * vehicles, True, "Capacity")
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromMilliseconds(max(10, int(time_limit * 1000)))
    solution = routing.SolveWithParameters(params)
    if solution is None:
        return _result(instance, solver_name, started, None, None, ["no_route_within_budget"])
    routes: list[list[int]] = []
    objective = 0
    for vehicle in range(vehicles):
        index = routing.Start(vehicle)
        route = [0]
        while not routing.IsEnd(index):
            next_index = solution.Value(routing.NextVar(index))
            objective += routing.GetArcCostForVehicle(index, next_index, vehicle)
            index = next_index
            route.append(manager.IndexToNode(index))
        routes.append(route)
    assignments = {"routes": routes}
    return _result(
        instance,
        solver_name,
        started,
        assignments,
        float(objective),
        check_feasibility(instance, assignments),
    )


def _solve_portfolio(instance: ProblemInstance, time_limit: float, solver_name: str) -> SolutionResult:
    started = time.perf_counter()
    assets = len(instance.entities["assets"])
    model = cp_model.CpModel()
    selected = [model.new_bool_var(f"asset_{index}") for index in range(assets)]
    model.add(sum(selected) <= int(instance.parameters["max_assets"]))
    model.add(
        sum(instance.parameters["returns"][index] * selected[index] for index in range(assets))
        >= int(instance.parameters["minimum_return"])
    )
    for sector in set(instance.parameters["sectors"]):
        model.add(
            sum(selected[index] for index in range(assets) if instance.parameters["sectors"][index] == sector)
            <= int(instance.parameters["max_per_sector"])
        )
    risks = instance.parameters["risks"]
    returns = instance.parameters["returns"]
    model.minimize(sum((risks[index] - 2 * returns[index]) * selected[index] for index in range(assets)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    if solver.status_name(status) not in {"OPTIMAL", "FEASIBLE"}:
        return _result(instance, solver_name, started, None, None, ["return_or_exposure_infeasible"])
    chosen = [index for index in range(assets) if solver.value(selected[index])]
    assignments = {"selected_assets": chosen}
    objective = sum(risks[index] - 2 * returns[index] for index in chosen)
    return _result(
        instance,
        solver_name,
        started,
        assignments,
        float(objective),
        check_feasibility(instance, assignments),
        ["synthetic laboratory; not financial advice"],
    )


SOLVERS: dict[Domain, Callable[[ProblemInstance, float, str], SolutionResult]] = {
    Domain.SCHEDULING: _solve_scheduling,
    Domain.ROUTING: _solve_routing,
    Domain.PORTFOLIO: _solve_portfolio,
}


def solve_strong(instance: ProblemInstance, *, exact: bool = False) -> SolutionResult:
    return SOLVERS[instance.domain](
        instance, 0.25 if exact else 0.08, "exact_oracle" if exact else "classical_strong"
    )


def solve_heuristic(instance: ProblemInstance) -> SolutionResult:
    started = time.perf_counter()
    assignments: dict[str, Any]
    if instance.domain is Domain.SCHEDULING:
        workers = len(instance.entities["workers"])
        maximum = int(instance.parameters["max_shifts_per_worker"])
        unavailable = {tuple(pair) for pair in instance.parameters["unavailable"]}
        loads = [0] * workers
        pairs: list[list[int]] = []
        for shift, required in enumerate(instance.parameters["demand"]):
            choices = [
                worker
                for worker in range(workers)
                if loads[worker] < maximum and (worker, shift) not in unavailable
            ]
            choices.sort(
                key=lambda worker: (
                    instance.parameters["costs"][worker] + instance.parameters["preferences"][worker][shift],
                    loads[worker],
                )
            )
            for worker in choices[:required]:
                pairs.append([worker, shift])
                loads[worker] += 1
        assignments = {"worker_shift": pairs}
        violations = check_feasibility(instance, assignments)
        objective = float(
            sum(
                instance.parameters["costs"][worker] + instance.parameters["preferences"][worker][shift]
                for worker, shift in pairs
            )
        )
    elif instance.domain is Domain.ROUTING:
        demands = instance.parameters["demands"]
        capacity = int(instance.parameters["vehicle_capacity"])
        routes = [[0] for _ in instance.entities["vehicles"]]
        loads = [0] * len(routes)
        for customer, demand in sorted(enumerate(demands, start=1), key=lambda pair: pair[1], reverse=True):
            candidates = [index for index, load in enumerate(loads) if load + demand <= capacity]
            if not candidates:
                continue
            vehicle = min(candidates, key=lambda index: loads[index])
            routes[vehicle].append(customer)
            loads[vehicle] += demand
        for route in routes:
            route.append(0)
        assignments = {"routes": routes}
        violations = check_feasibility(instance, assignments)
        distances = _distance_matrix(instance.parameters["coordinates"])
        objective = float(sum(distances[a][b] for route in routes for a, b in pairwise(route)))
    else:
        returns = instance.parameters["returns"]
        risks = instance.parameters["risks"]
        sectors = instance.parameters["sectors"]
        limit = int(instance.parameters["max_assets"])
        selected: list[int] = []
        for index in sorted(
            range(len(returns)), key=lambda item: (2 * returns[item] - risks[item]), reverse=True
        ):
            if len(selected) >= limit or sum(sectors[item] == sectors[index] for item in selected) >= int(
                instance.parameters["max_per_sector"]
            ):
                continue
            selected.append(index)
        assignments = {"selected_assets": selected}
        violations = check_feasibility(instance, assignments)
        objective = float(sum(risks[index] - 2 * returns[index] for index in selected))
    return _result(
        instance, "domain_heuristic", started, assignments if not violations else None, objective, violations
    )


def objective_gap(candidate: SolutionResult, oracle: SolutionResult) -> float | None:
    if (
        not candidate.feasible
        or not oracle.feasible
        or candidate.objective is None
        or oracle.objective is None
    ):
        return None
    denominator = max(abs(oracle.objective), 1.0)
    return (
        max(0.0, (candidate.objective - oracle.objective) / denominator)
        if math.isfinite(denominator)
        else None
    )
