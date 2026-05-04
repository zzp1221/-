import pytest

from src.ai_modules.agents.judge_agent import JudgeAgent
from src.ai_modules.agents.practice_agent import PracticeAgent
from src.ai_modules.models import QuestionBatchPayload, SubjectiveJudgeEvaluation
from src.ai_modules.runtime import SystemSnapshot


def _build_snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        current_course="数据库原理",
        current_chapter="联合索引",
        course_progress=0.5,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["最左匹配", "使用条件"],
        preferred_style="step_by_step",
        recent_mistakes=["条件判断错误"],
        session_id="conv-practice",
        conversation_length=3,
        total_tokens_used=256,
        wiki_pages_count=10,
        last_index_update="2026-05-03",
        recent_activities=["完成索引复习"],
    )


@pytest.mark.asyncio
async def test_practice_agent_generates_question_batch() -> None:
    class FakeQuestionGenerator:
        async def generate_batch(self, *, topic, difficulty, count, learning_context):
            del learning_context
            return QuestionBatchPayload.model_validate(
                {
                    "title": f"{topic} 练习题",
                    "topic": topic,
                    "difficulty": difficulty,
                    "questions": [
                        {
                            "questionId": f"q{index}",
                            "questionType": "SINGLE_CHOICE" if index < count else "SHORT_ANSWER",
                            "stem": f"LLM 生成题目 {index}",
                            "options": ["A", "B", "C", "D"] if index < count else [],
                            "answer": "C" if index < count else "说明理由",
                            "knowledgeTags": [topic, f"标签{index}"],
                            "difficultyLevel": difficulty,
                            "explanation": f"LLM 生成解析 {index}",
                        }
                        for index in range(1, count + 1)
                    ],
                }
            )

    agent = PracticeAgent(question_generator=FakeQuestionGenerator())
    params = {
        "topic": "联合索引",
        "difficulty": "BASIC",
        "count": 5,
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-practice",
            trace_id="trace-practice",
            seq=1,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    assert [event.event for event in events] == ["progress", "question_batch"]
    assert params["practiceQuestionBatch"]["topic"] == "联合索引"
    assert len(params["practiceQuestionBatch"]["questions"]) == 5
    assert "practiceSetId" in params["practicePersistence"]
    assert events[1].payload.questions[0].stem == "LLM 生成题目 1"


@pytest.mark.asyncio
async def test_judge_agent_scores_answers_and_marks_profile_source() -> None:
    class FakeQuestionGenerator:
        async def generate_batch(self, *, topic, difficulty, count, learning_context):
            del learning_context
            return QuestionBatchPayload.model_validate(
                {
                    "title": f"{topic} 练习题",
                    "topic": topic,
                    "difficulty": difficulty,
                    "questions": [
                        {
                            "questionId": "q1",
                            "questionType": "SINGLE_CHOICE",
                            "stem": "LLM 生成客观题 1",
                            "options": ["A", "B", "C", "D"],
                            "answer": "C",
                            "knowledgeTags": [topic, "核心概念"],
                            "difficultyLevel": difficulty,
                            "explanation": "LLM 解析 1",
                        },
                        {
                            "questionId": "q2",
                            "questionType": "SINGLE_CHOICE",
                            "stem": "LLM 生成客观题 2",
                            "options": ["A", "B", "C", "D"],
                            "answer": "A",
                            "knowledgeTags": [topic, "易错点"],
                            "difficultyLevel": difficulty,
                            "explanation": "LLM 解析 2",
                        },
                        {
                            "questionId": "q3",
                            "questionType": "SHORT_ANSWER",
                            "stem": "LLM 生成主观题 3",
                            "options": [],
                            "answer": "需要先判断条件",
                            "knowledgeTags": [topic, "使用条件"],
                            "difficultyLevel": difficulty,
                            "explanation": "LLM 解析 3",
                        },
                    ],
                }
            )

    class FakeObjectiveJudgeGenerator:
        async def judge(self, *, questions, answers):
            del questions
            return {
                "items": [
                    {
                        "questionId": "q1",
                        "questionType": "SINGLE_CHOICE",
                        "learnerAnswer": answers["q1"],
                        "correctAnswer": "C",
                        "isCorrect": True,
                        "score": 20.0,
                        "knowledgeTags": ["联合索引", "核心概念"],
                        "reason": "LLM 判断答案正确。",
                        "feedback": "继续保持。",
                        "profileDelta": {"confidenceLevel": "MEDIUM"},
                    },
                    {
                        "questionId": "q2",
                        "questionType": "SINGLE_CHOICE",
                        "learnerAnswer": answers["q2"],
                        "correctAnswer": "A",
                        "isCorrect": False,
                        "score": 0.0,
                        "knowledgeTags": ["联合索引", "易错点"],
                        "reason": "LLM 判断答案遗漏了条件。",
                        "feedback": "先判断条件再作答。",
                        "profileDelta": {"confidenceLevel": "LOW", "weakPoints": ["易错点"]},
                    },
                ],
                "pendingSubjective": [
                    {
                        "questionId": "q3",
                        "questionType": "SHORT_ANSWER",
                        "stem": "LLM 生成主观题 3",
                        "options": [],
                        "answer": "需要先判断条件",
                        "knowledgeTags": ["联合索引", "使用条件"],
                        "difficultyLevel": "BASIC",
                        "explanation": "LLM 解析 3",
                    }
                ],
            }

    class FakeFeedbackGenerator:
        async def summarize(self, *, items, topic):
            return {
                "summary": f"LLM 汇总：{topic} 还需加强条件判断。",
                "totalScore": 20.0,
                "accuracy": 1 / 3,
                "items": [
                    item.model_dump(by_alias=True) for item in items
                ],
                "weakKnowledgeTags": ["易错点", "使用条件"],
            }

    practice_agent = PracticeAgent(question_generator=FakeQuestionGenerator())
    params = {
        "topic": "联合索引",
        "difficulty": "BASIC",
        "count": 5,
    }
    practice_events = [
        event
        async for event in practice_agent.run(
            task_id="task-practice",
            trace_id="trace-practice",
            seq=1,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]
    assert practice_events[1].event == "question_batch"

    params["answers"] = {
        "q1": "C",
        "q2": "B",
        "q3": "需要先判断条件，但是我还不会分析错因。",
        "q4": "B",
        "q5": "",
    }
    judge_agent = JudgeAgent(
        objective_judge_generator=FakeObjectiveJudgeGenerator(),
        feedback_generator=FakeFeedbackGenerator(),
    )
    judge_events = [
        event
        async for event in judge_agent.run(
            task_id="task-judge",
            trace_id="trace-judge",
            seq=3,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    assert [event.event for event in judge_events] == ["progress", "judge_result"]
    assert params["profileSource"] == "PRACTICE"
    assert params["judgeResult"]["accuracy"] < 1.0
    assert params["judgeResult"]["items"][1]["isCorrect"] is False
    assert "submissionMappings" in params["practiceJudgePersistence"]
    assert "weakKnowledgeTags" in params["judgeResult"]
    assert params["judgeResult"]["summary"].startswith("LLM 汇总：")


@pytest.mark.asyncio
async def test_judge_agent_uses_subjective_evaluator_result_when_available() -> None:
    class FakeSubjectiveEvaluator:
        async def evaluate(self, *, question, learner_answer):
            del question, learner_answer
            return SubjectiveJudgeEvaluation(
                score=18.0,
                isCorrect=True,
                reason="百炼评估认为答案基本完整。",
                feedback="补一个更具体的例子会更好。",
                confidenceLevel="MEDIUM",
            )

    practice_agent = PracticeAgent()
    params = {
        "topic": "联合索引",
        "difficulty": "BASIC",
        "count": 5,
    }
    _ = [
        event
        async for event in practice_agent.run(
            task_id="task-practice",
            trace_id="trace-practice",
            seq=1,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]
    params["answers"] = {
        "q1": "C",
        "q2": "A",
        "q3": "我会先判断条件，再结合场景解释。",
        "q4": "B",
        "q5": "先看定义。",
    }

    judge_agent = JudgeAgent(subjective_evaluator=FakeSubjectiveEvaluator())
    events = [
        event
        async for event in judge_agent.run(
            task_id="task-judge-llm",
            trace_id="trace-judge-llm",
            seq=3,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    subjective_items = [
        item for item in events[1].payload.items if item.question_type == "SHORT_ANSWER"
    ]
    assert subjective_items
    assert subjective_items[0].score == 18.0
    assert subjective_items[0].reason == "百炼评估认为答案基本完整。"


@pytest.mark.asyncio
async def test_judge_agent_falls_back_when_subjective_evaluator_fails() -> None:
    class BrokenSubjectiveEvaluator:
        async def evaluate(self, *, question, learner_answer):
            del question, learner_answer
            raise RuntimeError("rate limit")

    practice_agent = PracticeAgent()
    params = {
        "topic": "联合索引",
        "difficulty": "BASIC",
        "count": 5,
    }
    _ = [
        event
        async for event in practice_agent.run(
            task_id="task-practice",
            trace_id="trace-practice",
            seq=1,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]
    params["answers"] = {
        "q1": "C",
        "q2": "B",
        "q3": "",
        "q4": "B",
        "q5": "",
    }

    judge_agent = JudgeAgent(subjective_evaluator=BrokenSubjectiveEvaluator())
    events = [
        event
        async for event in judge_agent.run(
            task_id="task-judge-fallback",
            trace_id="trace-judge-fallback",
            seq=3,
            service_type="PRACTICE_JUDGE",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    subjective_items = [
        item for item in events[1].payload.items if item.question_type == "SHORT_ANSWER"
    ]
    assert subjective_items
    assert subjective_items[0].score == 0.0
    assert "未作答或答案为空" in subjective_items[0].reason
