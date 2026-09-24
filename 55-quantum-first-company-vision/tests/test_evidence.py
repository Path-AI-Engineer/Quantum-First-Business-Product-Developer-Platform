from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from venture_evidence.models import Claim, Corpus
from venture_evidence.repository import load_corpus, load_protocol
from venture_evidence.validation import validate


def test_complete_public_corpus_and_real_decision_traces():
    corpus = load_corpus()
    result = validate(corpus, load_protocol())
    assert result["evidence"] >= 30
    assert result["entities"]["customer_profile"] == 12
    assert result["entities"]["trace"] == 6
    assert result["approval"] == "pending_human_review"
    assert corpus.buyer_interviews_completed == corpus.paying_customers_validated == 0
    plan = next(e for e in corpus.entities if e.entity_type == "interview_plan")
    assert plan.details["target"] == 15
    assert plan.details["completed"] == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_ids", []),
        ("accessed_on", None),
        ("confidence", "C4"),
        ("confidence", "C1"),
        ("supporting_evidence", []),
    ],
)
def test_external_fact_cannot_be_fabricated(field, value):
    record = load_corpus().claims[0].model_dump()
    record[field] = value
    with pytest.raises(ValidationError):
        Claim.model_validate(record)


def test_hypothesis_is_not_a_fact_by_repetition():
    record = load_corpus().claims[0].model_dump()
    record.update(
        kind="hypothesis", confidence="C0", external=False, source_ids=[], supporting_evidence=[], accessed_on=None
    )
    assert Claim.model_validate(record).kind == "hypothesis"
    record["kind"] = "fact"
    with pytest.raises(ValidationError):
        Claim.model_validate(record)


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate",
        "source",
        "support",
        "independence",
        "trace",
        "dimension",
        "counterevidence",
        "coverage",
        "vertical",
        "future",
        "icp",
    ],
)
def test_semantic_gate_rejects_invalid_research(mutation):
    corpus, protocol = load_corpus(), load_protocol()
    if mutation == "duplicate":
        corpus.evidence[1].id = corpus.evidence[0].id
    elif mutation == "source":
        corpus.evidence[0].source_id = "source-missing"
    elif mutation == "support":
        corpus.claims[0].supporting_evidence = ["evidence-missing"]
    elif mutation == "independence":
        corpus.claims[0].confidence = "C2"
    elif mutation == "trace":
        next(e for e in corpus.entities if e.entity_type == "trace").details["path"][-1] = "source-wrong"
    elif mutation == "dimension":
        protocol.dimensions.pop()
    elif mutation == "counterevidence":
        corpus.opportunities[0].opposing_claim_ids = []
    elif mutation == "coverage":
        corpus.entities = [e for e in corpus.entities if e.entity_type != "discovery_question"]
    elif mutation == "vertical":
        for entity in corpus.entities:
            if entity.entity_type == "customer_profile":
                entity.details["vertical"] = "one"
    elif mutation == "future":
        corpus.sources[0].accessed_on = date.today() + timedelta(days=1)
    elif mutation == "icp":
        corpus.opportunities[0].primary_icp = "icp-not-present"
    with pytest.raises(ValueError):
        validate(corpus, protocol)


@pytest.mark.parametrize(
    "field,value",
    [
        ("approval", "approved"),
        ("buyer_interviews_completed", 15),
        ("paying_customers_validated", 1),
    ],
)
def test_approval_and_customer_claims_are_outside_scope(field, value):
    corpus = load_corpus().model_dump()
    corpus[field] = value
    with pytest.raises(ValidationError):
        Corpus.model_validate(corpus)


def test_freshness_is_reported_not_silently_extended():
    corpus = load_corpus()
    result = validate(corpus, load_protocol(), today=date(2030, 1, 1))
    assert len(result["overdue_claims"]) == len(corpus.claims)
