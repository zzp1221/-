from src.ai_modules.llms import BailianSubjectiveJudgeEvaluator, HeuristicSubjectiveJudgeEvaluator
from src.ai_modules.models import PracticeQuestion


def _build_question() -> PracticeQuestion:
    return PracticeQuestion(
        questionId="q3",
        questionType="SHORT_ANSWER",
        stem="请说明联合索引的使用条件。",
        options=[],
        answer="先判断使用前提，再结合具体查询场景说明容易误判的位置。",
        knowledgeTags=["联合索引", "使用条件"],
        difficultyLevel="BASIC",
        explanation="回答应覆盖条件和场景。",
    )


import pytest


@pytest.mark.asyncio
async def test_heuristic_subjective_evaluator_handles_empty_answer() -> None:
    evaluator = HeuristicSubjectiveJudgeEvaluator()

    result = await evaluator.evaluate(question=_build_question(), learner_answer="")

    assert result.score == 0.0
    assert result.is_correct is False
    assert result.confidence_level == "LOW"


def test_bailian_subjective_evaluator_extracts_json_payload() -> None:
    evaluator = BailianSubjectiveJudgeEvaluator(api_key="test-key")

    payload = evaluator._extract_json(
        """```json
        {"score": 16, "isCorrect": true, "reason": "回答基本完整", "feedback": "建议补充例子", "confidenceLevel": "MEDIUM"}
        ```"""
    )

    assert payload["score"] == 16
    assert payload["isCorrect"] is True
