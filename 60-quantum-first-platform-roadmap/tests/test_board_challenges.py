from __future__ import annotations

import pytest

from strategy_control_tower.models import StrategyRepository


@pytest.mark.parametrize("case", range(20))
def test_board_challenge_questions(repository: StrategyRepository, case: int) -> None:
    question = repository.board_questions[case]
    assert question.startswith("Board challenge") and "reverse" in question
    assert repository.approval_status == "technical_candidate_unapproved"
