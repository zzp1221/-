import pytest

from src.ai_modules.agents.tutor_agent import TutorAgent
from src.ai_modules.llms import RuleBasedTutorLLM
from src.ai_modules.memory import (
    ConversationSummaryDocument,
    InMemoryConversationSummaryStore,
    MongoConversationSummaryStore,
)
from src.ai_modules.runtime import ConversationCompactor, SystemSnapshot


def _build_snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["联合索引"],
        preferred_style="step_by_step",
        recent_mistakes=["范围查询条件判断错误"],
        session_id="conv-001",
        conversation_length=10,
        total_tokens_used=1500,
        wiki_pages_count=20,
        last_index_update="2026-05-02",
        recent_activities=["完成索引练习"],
    )


@pytest.mark.asyncio
async def test_tutor_agent_compacts_long_conversation_and_emits_dialog_state() -> None:
    tutor = TutorAgent(
        compactor=ConversationCompactor(token_budget=30, keep_recent_turns=2),
        summary_store=InMemoryConversationSummaryStore(),
        llm_client=RuleBasedTutorLLM(),
    )
    snapshot = _build_snapshot()
    params = {
        "conversationId": "conv-001",
        "messages": [
            {"role": "user", "content": "老师我不太懂什么是索引"},
            {"role": "assistant", "content": "索引可以帮助快速定位数据"},
            {"role": "user", "content": "联合索引和普通索引有什么区别"},
            {"role": "assistant", "content": "它们的适用场景不同"},
            {"role": "user", "content": "那我做题时总是分不清"},
        ],
        "query": "联合索引",
        "rewrittenQuery": "数据库原理 联合索引",
        "retrievalResult": {
            "documents": [
                {"title": "联合索引", "channel": "phrase"},
                {"title": "数据库索引导学", "channel": "hybrid"},
            ]
        },
    }

    events = [
        event
        async for event in tutor.run(
            task_id="task-001",
            trace_id="trace-001",
            seq=1,
            service_type="TUTORING",
            params=params,
            snapshot=snapshot,
            system_prompt="test",
        )
    ]

    assert [event.event for event in events] == ["progress", "result_chunk"]
    assert params["conversationSummary"]
    assert params["structuredConversationSummary"]["summaryText"]
    assert params["structuredConversationSummary"]["lastUserMessage"] == "联合索引和普通索引有什么区别"
    assert events[0].dialog_state is not None
    assert events[0].dialog_state.pedagogy_strategy == "retrieval_grounded_scaffold"
    assert "我先回顾一下历史摘要" in events[1].payload.text
    assert "接下来请你先回答" in events[1].payload.text


def test_conversation_compactor_keeps_recent_messages() -> None:
    compactor = ConversationCompactor(token_budget=20, keep_recent_turns=2)
    messages = [
        {"role": "user", "content": "a" * 20},
        {"role": "assistant", "content": "b" * 20},
        {"role": "user", "content": "c" * 20},
        {"role": "assistant", "content": "d" * 20},
    ]

    result = compactor.compact(messages)

    assert result.was_compacted is True
    assert len(result.compacted_messages) == 3
    assert result.structured_summary.summary_text
    assert result.compacted_messages[-2]["content"] == "c" * 20
    assert result.compacted_messages[-1]["content"] == "d" * 20


@pytest.mark.asyncio
async def test_tutor_agent_loads_and_persists_structured_summary() -> None:
    store = InMemoryConversationSummaryStore()
    await store.save_summary(
        ConversationSummaryDocument(
            conversationId="conv-001",
            userId=None,
            taskId="task-old",
            topicFocus=["索引"],
            learnerGoal="掌握联合索引",
            knownGaps=["总是分不清使用条件"],
            unresolvedQuestions=["联合索引和普通索引有什么区别？"],
            preferredHelpStyle="step_by_step",
            lastUserMessage="老师我还是不懂",
            recentProgress=["前面已经讲过概念定义"],
            summaryText="主题: 索引 ; 目标: 掌握联合索引 ; 薄弱点: 总是分不清使用条件 ; 未解决问题: 联合索引和普通索引有什么区别？",
        )
    )
    tutor = TutorAgent(
        compactor=ConversationCompactor(token_budget=30, keep_recent_turns=2),
        summary_store=store,
        llm_client=RuleBasedTutorLLM(),
    )

    params = {
        "conversationId": "conv-001",
        "messages": [
            {"role": "user", "content": "老师我不太懂什么是索引"},
            {"role": "assistant", "content": "索引可以帮助快速定位数据"},
            {"role": "user", "content": "联合索引和普通索引有什么区别"},
            {"role": "assistant", "content": "它们的适用场景不同"},
            {"role": "user", "content": "那我做题时总是分不清"},
        ],
        "query": "联合索引",
        "rewrittenQuery": "数据库原理 联合索引",
        "retrievalResult": {"documents": [{"title": "联合索引", "channel": "phrase"}]},
    }
    events = [
        event
        async for event in tutor.run(
            task_id="task-001",
            trace_id="trace-001",
            seq=1,
            service_type="TUTORING",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    assert "我先回顾一下历史摘要" in events[1].payload.text
    assert len(store.documents) >= 2


@pytest.mark.asyncio
async def test_mongo_summary_store_maps_save_and_load() -> None:
    class FakeCollection:
        def __init__(self) -> None:
            self.saved: list[dict] = []

        def insert_one(self, payload: dict) -> None:
            self.saved.append(payload)

        def find_one(self, criteria: dict, sort: list[tuple[str, int]]):
            del sort
            for item in reversed(self.saved):
                if item.get("conversationId") == criteria.get("conversationId"):
                    return {**item, "_id": "fake"}
            return None

    collection = FakeCollection()
    store = MongoConversationSummaryStore(collection=collection)
    document = ConversationSummaryDocument(
        conversationId="conv-002",
        userId="user-001",
        taskId="task-002",
        topicFocus=["联合索引"],
        learnerGoal="理解使用条件",
        knownGaps=["不会判断最左匹配"],
        unresolvedQuestions=["为什么会失效？"],
        preferredHelpStyle="example_first",
        lastUserMessage="为什么联合索引会失效？",
        recentProgress=["已区分普通索引与联合索引"],
        summaryText="主题: 联合索引 ; 目标: 理解使用条件 ; 薄弱点: 不会判断最左匹配 ; 未解决问题: 为什么会失效？",
    )

    await store.save_summary(document)
    loaded = await store.get_latest_summary(conversation_id="conv-002", user_id="user-001")

    assert collection.saved
    assert loaded is not None
    assert loaded.topic_focus == ["联合索引"]
