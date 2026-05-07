import pytest

from src.ai_modules.agents.profile_agent import ProfileAgent
from src.ai_modules.llms import RuleBasedProfileLLM
from src.ai_modules.memory import InMemoryProfileStore, PostgresProfileStore
from src.ai_modules.models import LearnerProfileDimensions
from src.ai_modules.runtime import SystemSnapshot


def _build_snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.4,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["联合索引"],
        preferred_style="step_by_step",
        recent_mistakes=["最左匹配判断错误"],
        session_id="conv-profile",
        conversation_length=6,
        total_tokens_used=512,
        wiki_pages_count=12,
        last_index_update="2026-05-02",
        recent_activities=["完成索引练习"],
    )


@pytest.mark.asyncio
async def test_profile_agent_updates_profile_and_caches_dimensions() -> None:
    class FakeProfileAnalyzer:
        async def analyze(self, *, context_payload):
            del context_payload
            return LearnerProfileDimensions(
                knowledgeFoundation="BASIC",
                learningGoal="掌握联合索引的使用条件",
                professionalBackground="计算机本科生",
                learningPreference="step_by_step",
                cognitiveStyle="procedural_oriented",
                weakPoints=["不会判断最左匹配"],
                learningPace="steady",
                confidenceLevel="LOW",
                source="CONVERSATION",
                summaryText="画像更新完成：学生需要一步步理解联合索引使用条件。",
            )

    store = InMemoryProfileStore()
    agent = ProfileAgent(
        profile_store=store,
        llm_client=RuleBasedProfileLLM(),
        profile_analyzer=FakeProfileAnalyzer(),
    )
    params = {
        "userId": "00000000-0000-0000-0000-000000000111",
        "conversationId": "00000000-0000-0000-0000-000000000222",
        "messages": [
            {"role": "user", "content": "老师，我刚学数据库，想一步步理解联合索引。"},
            {"role": "assistant", "content": "我们先从定义开始。"},
            {"role": "user", "content": "我做题时总是分不清什么时候会失效。"},
        ],
        "structuredConversationSummary": {
            "learnerGoal": "掌握联合索引的使用条件",
            "knownGaps": ["不会判断最左匹配"],
            "preferredHelpStyle": "step_by_step",
        },
        "profile": {
            "studentLevel": "BASIC",
            "professionalBackground": "计算机本科生",
        },
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-profile",
            trace_id="trace-profile",
            seq=1,
            service_type="PROFILE_BUILD",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    snapshot = await store.read_profile("00000000-0000-0000-0000-000000000111")

    assert [event.event for event in events] == ["progress", "result_chunk"]
    assert params["analyzedProfileDimensions"]["knowledgeFoundation"] == "BASIC"
    assert params["analyzedProfileDimensions"]["learningPreference"] == "step_by_step"
    assert "一步步理解联合索引使用条件" in params["profileUpdate"]["summaryText"]
    assert snapshot is not None
    assert snapshot.version == 1
    assert snapshot.profile.professional_background == "计算机本科生"
    assert snapshot.profile.weak_points == ["不会判断最左匹配"]
    assert "一步步理解联合索引使用条件" in events[1].payload.text


@pytest.mark.asyncio
async def test_profile_agent_falls_back_to_in_memory_store_when_primary_store_fails() -> None:
    class BrokenProfileStore:
        async def read_profile(self, user_id: str):
            del user_id
            raise RuntimeError("db unavailable")

        async def update_profile(
            self,
            *,
            user_id: str,
            dimensions: LearnerProfileDimensions,
            source_session_id: str | None = None,
        ):
            del user_id, dimensions, source_session_id
            raise RuntimeError("db unavailable")

    class FakeProfileAnalyzer:
        async def analyze(self, *, context_payload):
            del context_payload
            return LearnerProfileDimensions(
                knowledgeFoundation="BASIC",
                learningGoal="掌握联合索引",
                professionalBackground="计算机本科生",
                learningPreference="step_by_step",
                cognitiveStyle="procedural_oriented",
                weakPoints=["最左匹配"],
                learningPace="steady",
                confidenceLevel="LOW",
                source="CONVERSATION",
                summaryText="画像更新完成：联合索引理解仍需强化。",
            )

    agent = ProfileAgent(
        profile_store=BrokenProfileStore(),
        llm_client=RuleBasedProfileLLM(),
        profile_analyzer=FakeProfileAnalyzer(),
    )
    params = {
        "userId": "00000000-0000-0000-0000-000000000333",
        "messages": [{"role": "user", "content": "我不太懂联合索引，能慢一点吗？"}],
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-profile-fallback",
            trace_id="trace-profile-fallback",
            seq=1,
            service_type="PROFILE_BUILD",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    fallback_snapshot = await agent.fallback_profile_store.read_profile(
        "00000000-0000-0000-0000-000000000333"
    )

    assert events[0].event == "progress"
    assert events[-1].event == "result_chunk"
    assert fallback_snapshot is not None
    assert fallback_snapshot.version == 1
    assert fallback_snapshot.profile.learning_pace == "steady"


@pytest.mark.asyncio
async def test_postgres_profile_store_rolls_back_only_vector_write() -> None:
    executed_sql: list[str] = []

    class FakeCursor:
        def __init__(self) -> None:
            self._last_fetchone = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type, exc, tb

        def execute(self, sql: str, params=None) -> None:
            del params
            compact_sql = " ".join(sql.split())
            executed_sql.append(compact_sql)
            if "SELECT COALESCE(MAX(version), 0) + 1" in compact_sql:
                self._last_fetchone = (1,)
            elif "RETURNING id" in compact_sql:
                self._last_fetchone = ("snapshot-001",)
            elif "INSERT INTO rag.user_profile_vector" in compact_sql:
                raise RuntimeError("vector extension unavailable")
            else:
                self._last_fetchone = None

        def fetchone(self):
            return self._last_fetchone

    class FakeConnection:
        def __init__(self) -> None:
            self.commit_count = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type, exc, tb

        def cursor(self) -> FakeCursor:
            return FakeCursor()

        def commit(self) -> None:
            self.commit_count += 1

    connection = FakeConnection()
    store = PostgresProfileStore(connect_fn=lambda **_: connection)

    snapshot = await store.update_profile(
        user_id="00000000-0000-0000-0000-000000000444",
        source_session_id="00000000-0000-0000-0000-000000000555",
        dimensions=LearnerProfileDimensions(
            knowledgeFoundation="BASIC",
            learningGoal="掌握联合索引",
            professionalBackground="计算机本科生",
            learningPreference="step_by_step",
            cognitiveStyle="procedural_oriented",
            weakPoints=["不会判断最左匹配"],
            learningPace="steady",
            confidenceLevel="LOW",
            source="CONVERSATION",
            summaryText="画像更新完成",
        ),
    )

    assert snapshot.version == 1
    assert connection.commit_count == 1
    assert any("SAVEPOINT profile_vector_insert" in sql for sql in executed_sql)
    assert any("ROLLBACK TO SAVEPOINT profile_vector_insert" in sql for sql in executed_sql)
    assert any("RELEASE SAVEPOINT profile_vector_insert" in sql for sql in executed_sql)
