from __future__ import annotations

from collections import Counter

import pytest
from hypothesis import given
from hypothesis import strategies as st

from optimization_lab.corpus import build_corpus, corpus_summary
from optimization_lab.models import Domain, Feasibility, Size, Split


def test_corpus_contract_is_exact_and_locked() -> None:
    corpus = build_corpus()
    summary = corpus_summary(corpus)
    assert len(corpus) == 90
    assert summary["splits"] == {"development": 66, "test": 24}
    assert summary["domains"] == {domain.value: 30 for domain in Domain}
    assert summary["sizes"] == {size.value: 30 for size in Size}
    assert sum(item.test_locked for item in corpus) == 24
    assert all(item.sensitive_data_classification == "SYNTHETIC_PUBLIC" for item in corpus)
    assert len({item.instance_id for item in corpus}) == 90


@pytest.mark.parametrize("domain", list(Domain))
def test_each_domain_has_balanced_scenarios(domain: Domain) -> None:
    selected = [item for item in build_corpus() if item.domain is domain]
    assert Counter(item.size for item in selected) == {Size.SMALL: 10, Size.MEDIUM: 10, Size.LARGE: 10}
    assert Counter(item.split for item in selected) == {Split.DEVELOPMENT: 22, Split.TEST: 8}
    assert sum(item.expected_feasibility is Feasibility.INFEASIBLE for item in selected) == 6


@given(st.integers(min_value=0, max_value=89))
def test_generated_instances_round_trip(index: int) -> None:
    item = build_corpus()[index]
    assert item.model_validate_json(item.model_dump_json()) == item
