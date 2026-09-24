"""Deterministic scenario, graph, allocation, economics, and gate engines."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

from .models import Initiative, StrategicClass, StrategyRepository


def allocate(initiatives: tuple[Initiative, ...], budget: int, headcount: float, cost_multiplier: float = 1.0) -> dict[str, Any]:
    priority = {
        StrategicClass.REGULATORY: 0,
        StrategicClass.CORE: 1,
        StrategicClass.ENABLER: 2,
        StrategicClass.GROWTH: 3,
        StrategicClass.OPTION: 4,
        StrategicClass.WATCH: 5,
    }
    selected: list[str] = []
    held: list[str] = []
    spent, people = 0, 0.0
    for item in sorted(initiatives, key=lambda current: (priority[current.strategic_class], current.cost.expected, current.id)):
        cost = round(item.cost.expected * cost_multiplier)
        if spent + cost <= budget and people + item.headcount_min <= headcount:
            selected.append(item.id)
            spent += cost
            people += item.headcount_min
        else:
            held.append(item.id)
    return {
        "selected": selected,
        "held": held,
        "spent": spent,
        "budget": budget,
        "headcount_used": people,
        "headcount_limit": headcount,
        "within_constraints": spent <= budget and people <= headcount,
        "unmet_demand": len(held),
    }


def scenario_run(repository: StrategyRepository, scenario_id: str, shock_id: str | None = None) -> dict[str, Any]:
    scenario = next(item for item in repository.scenarios if item.id == scenario_id)
    shock = next((item for item in repository.shocks if item.id == shock_id), None)
    budget = round(scenario.budget * (shock.budget_multiplier if shock else 1.0))
    cost_multiplier = scenario.compute_multiplier * (shock.cost_multiplier if shock else 1.0)
    adoption = scenario.adoption_multiplier * (shock.adoption_multiplier if shock else 1.0)
    return {
        "scenario": scenario.id,
        "shock": shock.id if shock else None,
        "budget": budget,
        "cost_multiplier": round(cost_multiplier, 3),
        "adoption_index": round(adoption, 3),
        "allocation": allocate(repository.initiatives, budget, scenario.headcount, cost_multiplier),
        "decision": shock.expected_action if shock else "execute quarterly gates and preserve reversibility",
        "external_side_effects": False,
    }


def capability_graph(repository: StrategyRepository) -> dict[str, Any]:
    graph = nx.DiGraph()
    for capability in repository.capabilities:
        graph.add_node(capability.id, weight=capability.bottleneck_weight)
        for prerequisite in capability.prerequisites:
            graph.add_edge(prerequisite, capability.id)
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("capability graph must be acyclic")
    centrality = nx.betweenness_centrality(graph)
    critical = sorted(graph.nodes, key=lambda node: (centrality[node], graph.nodes[node]["weight"]), reverse=True)
    return {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "acyclic": True, "critical_path": critical[:5]}


def reconcile_costs(repository: StrategyRepository, scenario_id: str) -> dict[str, Any]:
    run = scenario_run(repository, scenario_id)
    total = int(run["allocation"]["spent"])
    weights = (0.34, 0.15, 0.08, 0.06, 0.10, 0.06, 0.05, 0.05, 0.05, 0.06)
    pools = {name: round(total * weight) for name, weight in zip(repository.cost_pools, weights, strict=True)}
    pools["contingency"] += total - sum(pools.values())
    return {
        "scenario": scenario_id,
        "total": total,
        "pools": pools,
        "reconciled": sum(pools.values()) == total,
        "confidence": "scenario_only",
    }


def evaluate_gate(metric_value: float, threshold: float, operator: str = ">=") -> str:
    passed = metric_value >= threshold if operator == ">=" else metric_value <= threshold
    return "PASS" if passed else "HOLD"


def build_reports(repository: StrategyRepository, scenario_id: str = "base") -> dict[str, Any]:
    run, economics = scenario_run(repository, scenario_id), reconcile_costs(repository, scenario_id)
    common = {
        "revision": repository.revision,
        "scenario": scenario_id,
        "approval_status": repository.approval_status,
        "selected": run["allocation"]["selected"],
        "held": run["allocation"]["held"],
        "cost_total": economics["total"],
        "side_effects": False,
    }
    return {
        "board": {**common, "focus": "capital, options, downside, and decision asks"},
        "technical": {**common, "focus": "dependencies, architecture, controls, and exit paths"},
        "operating": {**common, "focus": "owners, quarterly gates, costs, and review cadence"},
        "reconciled": True,
    }


def material_figures(repository: StrategyRepository) -> Mapping[str, str]:
    return {
        "budget": "scenario.budget × shock.budget_multiplier",
        "initiative_cost": "initiative.cost.expected × compute_multiplier × shock.cost_multiplier",
        "adoption": "scenario.adoption_multiplier × shock.adoption_multiplier",
        "source": repository.revision,
    }
