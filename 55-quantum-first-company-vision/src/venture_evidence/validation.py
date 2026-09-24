"""Semantic gates supplement the generated JSON Schema 2020-12 contracts."""

from __future__ import annotations

from collections import Counter
from datetime import date

from venture_evidence.models import Corpus, Protocol

MINIMUMS = {
    "customer_profile": 12,
    "job_to_be_done": 18,
    "buying_pattern": 10,
    "workflow": 3,
    "inaction": 3,
    "discovery_question": 24,
    "challenge": 24,
    "objection": 6,
    "trace": 6,
    "pricing": 6,
    "capability": 3,
    "experiment": 6,
    "risk": 6,
    "product_stage": 3,
}


def validate(corpus: Corpus, protocol: Protocol, *, today: date | None = None) -> dict[str, object]:
    today = today or date.today()
    groups = (corpus.sources, corpus.evidence, corpus.claims, corpus.entities, corpus.opportunities)
    ids = [item.id for group in groups for item in group]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate stable identifier")
    sources = {item.id: item for item in corpus.sources}
    evidence = {item.id: item for item in corpus.evidence}
    claims = {item.id: item for item in corpus.claims}
    entity_ids = {item.id for item in corpus.entities}
    dimensions = {item.id for item in protocol.dimensions}
    if len(dimensions) != 14 or len(protocol.dimensions) != 14:
        raise ValueError("Exactly 14 distinct scoring dimensions are required")
    if set(protocol.scenarios) != {"conservative", "base", "aggressive"}:
        raise ValueError("Three named scenarios are required")
    if len(protocol.stress_cases) != 8:
        raise ValueError("Eight assumption stress scenarios are required")
    for stress in protocol.stress_cases:
        if not set(stress.multipliers) <= dimensions:
            raise ValueError("Unknown stress dimension")
    for source in corpus.sources:
        if source.accessed_on > today:
            raise ValueError("Future source access date")
    for item in corpus.evidence:
        if item.source_id not in sources or item.confidence == "C4":
            raise ValueError(f"Unverifiable evidence: {item.id}")
    for claim in corpus.claims:
        if not set(claim.source_ids) <= sources.keys():
            raise ValueError(f"Dangling source on {claim.id}")
        if set(claim.supporting_evidence) & set(claim.opposing_evidence):
            raise ValueError("Evidence cannot simultaneously support and oppose the same claim")
        for eid in claim.supporting_evidence + claim.opposing_evidence:
            if eid not in evidence or evidence[eid].source_id not in claim.source_ids:
                raise ValueError(f"Broken evidence lineage on {claim.id}")
        if claim.kind == "fact":
            primary = any(
                sources[evidence[eid].source_id].classification == "primary" for eid in claim.supporting_evidence
            )
            independent = {sources[evidence[eid].source_id].publisher for eid in claim.supporting_evidence}
            if (claim.confidence == "C3" and not primary) or (claim.confidence == "C2" and len(independent) < 2):
                raise ValueError("Confidence is not supported by independent/primary provenance")
        if claim.accessed_on and claim.accessed_on > today:
            raise ValueError("Future claim access date")
    for entity in corpus.entities:
        if not set(entity.claim_ids) <= claims.keys() or not set(entity.related_ids) <= set(ids):
            raise ValueError(f"Dangling entity reference: {entity.id}")
    for opportunity in corpus.opportunities:
        if set(opportunity.dimensions) != dimensions or set(opportunity.rationale) != dimensions:
            raise ValueError("Every dimension needs a value or explicit unknown and an explanation")
        if not opportunity.classical_alternative or not opportunity.kill_gate or not opportunity.maturity_condition:
            raise ValueError("Every opportunity needs a classical alternative, maturity condition and kill gate")
        if not set(opportunity.claim_ids + opportunity.opposing_claim_ids) <= claims.keys():
            raise ValueError("Broken opportunity lineage")
        if not opportunity.opposing_claim_ids:
            raise ValueError("Every opportunity needs counterevidence")
        if opportunity.primary_icp not in entity_ids or opportunity.secondary_icp not in entity_ids:
            raise ValueError("Unknown ICP")
    entity_map = {item.id: item for item in corpus.entities}
    for trace in (e for e in corpus.entities if e.entity_type == "trace"):
        path = trace.details.get("path")
        if not isinstance(path, list) or len(path) != 4 or not all(isinstance(x, str) for x in path):
            raise ValueError("Trace requires decision, claim, evidence and source")
        decision_id, claim_id, evidence_id, source_id = [str(x) for x in path]
        decision = entity_map.get(decision_id)
        trace_claim = claims.get(claim_id)
        record = evidence.get(evidence_id)
        if (
            decision is None
            or decision.entity_type != "decision"
            or claim_id not in decision.claim_ids
            or trace_claim is None
            or evidence_id not in trace_claim.supporting_evidence + trace_claim.opposing_evidence
            or record is None
            or record.source_id != source_id
            or source_id not in sources
        ):
            raise ValueError(f"Broken decision-to-source trace: {trace.id}")
    verticals = {str(e.details.get("vertical")) for e in corpus.entities if e.entity_type == "customer_profile"}
    if len(verticals) != 4 or "None" in verticals:
        raise ValueError("Four explicit ICP verticals are required")
    plans = [e for e in corpus.entities if e.entity_type == "interview_plan"]
    if not plans or any(
        e.status != "planned" or e.details.get("target") != 15 or e.details.get("completed") != 0 for e in plans
    ):
        raise ValueError("Future interview plan must be explicitly planned")
    counts: Counter[str] = Counter(item.entity_type for item in corpus.entities)
    for key, minimum in MINIMUMS.items():
        if counts[key] < minimum:
            raise ValueError(f"Insufficient {key}: {counts[key]} < {minimum}")
    if counts["competitor"] + counts["alternative"] < 15 or len(evidence) < 30 or len(corpus.opportunities) < 3:
        raise ValueError("Incomplete research coverage")
    if not any(item.stance == "contradicts" for item in corpus.evidence):
        raise ValueError("Contradictory evidence is missing")
    return {
        "status": "verified",
        "sources": len(sources),
        "evidence": len(evidence),
        "claims": len(claims),
        "entities": dict(counts),
        "opportunities": len(corpus.opportunities),
        "overdue_claims": [c.id for c in corpus.claims if c.review_on < today],
        "approval": corpus.approval,
        "buyer_interviews_completed": 0,
    }
