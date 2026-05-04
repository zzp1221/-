import pytest

from src.ai_modules.memory import InMemoryPracticeStore, PostgresPracticeStore
from src.ai_modules.models import JudgeItemResult, JudgeResultPayload, PracticeQuestion, QuestionBatchPayload


def _build_question_batch() -> QuestionBatchPayload:
    return QuestionBatchPayload(
        title="联合索引练习题",
        topic="联合索引",
        difficulty="BASIC",
        questions=[
            PracticeQuestion(
                questionId="q1",
                questionType="SINGLE_CHOICE",
                stem="关于联合索引，下列哪项正确？",
                options=["A", "B", "C", "D"],
                answer="C",
                knowledgeTags=["联合索引", "核心概念"],
                difficultyLevel="BASIC",
                explanation="测试解释",
            ),
            PracticeQuestion(
                questionId="q2",
                questionType="SHORT_ANSWER",
                stem="说明联合索引的使用条件。",
                options=[],
                answer="先判断使用前提，再分析具体场景。",
                knowledgeTags=["联合索引", "使用条件"],
                difficultyLevel="BASIC",
                explanation="测试解释",
            ),
        ],
    )


def _build_judge_result() -> JudgeResultPayload:
    return JudgeResultPayload(
        title="联合索引判题结果",
        summary="本次共判定 2 题。",
        totalScore=26.0,
        accuracy=0.5,
        items=[
            JudgeItemResult(
                questionId="q1",
                questionType="SINGLE_CHOICE",
                learnerAnswer="C",
                correctAnswer="C",
                isCorrect=True,
                score=20.0,
                knowledgeTags=["联合索引", "核心概念"],
                reason="答案匹配标准答案",
                feedback="回答正确。",
                profileDelta={"confidenceLevel": "MEDIUM"},
            ),
            JudgeItemResult(
                questionId="q2",
                questionType="SHORT_ANSWER",
                learnerAnswer="我只知道一点定义。",
                correctAnswer="先判断使用前提，再分析具体场景。",
                isCorrect=False,
                score=6.0,
                knowledgeTags=["联合索引", "使用条件"],
                reason="回答不完整",
                feedback="需要补充使用前提。",
                profileDelta={"confidenceLevel": "LOW", "weakPoints": ["使用条件"]},
            ),
        ],
    )


@pytest.mark.asyncio
async def test_in_memory_practice_store_saves_batch_and_judge_result() -> None:
    store = InMemoryPracticeStore()
    batch_metadata = await store.save_question_batch(
        user_id="00000000-0000-0000-0000-000000000111",
        batch=_build_question_batch(),
        task_id="task-practice",
    )
    judge_metadata = await store.save_judge_result(
        user_id="00000000-0000-0000-0000-000000000111",
        answers={"q1": "C", "q2": "我只知道一点定义。"},
        judge_result=_build_judge_result(),
        persistence_metadata=batch_metadata,
    )

    assert batch_metadata["practiceSetId"] in store.question_batches
    assert len(batch_metadata["itemMappings"]) == 2
    assert judge_metadata["practiceSetId"] == batch_metadata["practiceSetId"]
    assert len(judge_metadata["submissionMappings"]) == 2


@pytest.mark.asyncio
async def test_postgres_practice_store_maps_batch_and_submission_sql() -> None:
    executed_sql: list[str] = []

    class FakeCursor:
        def __init__(self) -> None:
            self._last_fetchone = None
            self._item_counter = 0
            self._submission_counter = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type, exc, tb

        def execute(self, sql: str, params=None) -> None:
            compact_sql = " ".join(sql.split())
            executed_sql.append(compact_sql)
            if "INSERT INTO app.practice_set" in compact_sql:
                self._last_fetchone = ("practice-set-001",)
            elif "INSERT INTO app.practice_item" in compact_sql:
                self._item_counter += 1
                self._last_fetchone = (f"practice-item-00{self._item_counter}",)
            elif "INSERT INTO app.practice_submission" in compact_sql:
                self._submission_counter += 1
                self._last_fetchone = (f"practice-submission-00{self._submission_counter}",)
            else:
                self._last_fetchone = None
            del params

        def fetchone(self):
            return self._last_fetchone

    class FakeConnection:
        def __init__(self) -> None:
            self.commit_count = 0
            self.cursor_instance = FakeCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type, exc, tb

        def cursor(self) -> FakeCursor:
            return self.cursor_instance

        def commit(self) -> None:
            self.commit_count += 1

    connection = FakeConnection()
    store = PostgresPracticeStore(connect_fn=lambda **_: connection)

    batch_metadata = await store.save_question_batch(
        user_id="00000000-0000-0000-0000-000000000111",
        batch=_build_question_batch(),
        task_id="task-practice",
    )
    judge_metadata = await store.save_judge_result(
        user_id="00000000-0000-0000-0000-000000000111",
        answers={"q1": "C", "q2": "我只知道一点定义。"},
        judge_result=_build_judge_result(),
        persistence_metadata=batch_metadata,
    )

    assert batch_metadata["practiceSetId"] == "practice-set-001"
    assert len(batch_metadata["itemMappings"]) == 2
    assert len(judge_metadata["submissionMappings"]) == 2
    assert connection.commit_count == 2
    assert any("INSERT INTO app.practice_set" in sql for sql in executed_sql)
    assert any("INSERT INTO app.practice_item" in sql for sql in executed_sql)
    assert any("INSERT INTO app.practice_submission" in sql for sql in executed_sql)
    assert any("UPDATE app.practice_set" in sql for sql in executed_sql)
