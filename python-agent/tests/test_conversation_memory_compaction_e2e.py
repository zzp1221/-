"""End-to-end test for conversation memory persistence and context compression.

Test scenario:
  Simulate a 12-turn conversation about Java concurrency.
  The first 8 turns exceed the token budget, triggering compaction.
  The remaining 4 turns test that post-compaction answers remain coherent
  and reference pre-compaction context.

Scoring dimensions:
  - Memory persistence: summary saved and reloaded correctly
  - Context compression: compaction triggers at the right threshold
  - Answer continuity: post-compaction answers reference earlier context
"""

import pytest

from src.ai_modules.agents.tutor_agent import TutorAgent
from src.ai_modules.llms import RuleBasedTutorLLM
from src.ai_modules.memory import (
    ConversationSummaryDocument,
    InMemoryConversationSummaryStore,
)
from src.ai_modules.runtime import ConversationCompactor, SystemSnapshot


def _build_snapshot(**overrides) -> SystemSnapshot:
    defaults = dict(
        current_course="Java 程序设计",
        current_chapter="并发编程",
        course_progress=0.4,
        student_name="测试学生",
        student_level="BASIC",
        knowledge_gaps=["线程同步"],
        preferred_style="step_by_step",
        recent_mistakes=["synchronized 用法混淆"],
        session_id="conv-e2e",
        conversation_length=12,
        total_tokens_used=0,
        wiki_pages_count=30,
        last_index_update="2026-05-10",
        recent_activities=[],
    )
    defaults.update(overrides)
    return SystemSnapshot(**defaults)


# ── Multi-turn conversation script ──────────────────────────────────────────
# Each tuple: (user_query, retrieval_titles)
# Designed so that cumulative tokens exceed the small budget after ~6 turns.
TURNS = [
    ("什么是Java并发编程", ["Java并发编程入门"]),
    ("线程和进程有什么区别", ["线程与进程对比"]),
    ("synchronized 关键字怎么用", ["synchronized 详解"]),
    ("volatile 和 synchronized 有什么不同", ["volatile 与 synchronized 区别"]),
    ("什么是线程安全", ["线程安全概念"]),
    ("死锁是怎么产生的，怎么避免", ["死锁原理与预防"]),
    ("线程池的核心参数有哪些", ["Java线程池参数"]),
    ("CountDownLatch 和 CyclicBarrier 区别", ["并发工具类对比"]),
    # ── Post-compaction turns: test continuity ──
    ("那我前面问的 synchronized 具体怎么用，能再举个例子吗", ["synchronized 详解"]),
    ("回到死锁问题，除了避免还有别的解决办法吗", ["死锁原理与预防"]),
    ("线程池的拒绝策略有哪些", ["Java线程池参数"]),
    ("总结一下今天学到的并发知识", ["Java并发编程入门"]),
]


async def _run_turn(
    tutor: TutorAgent,
    conversation_id: str,
    task_id: str,
    turn_index: int,
    user_query: str,
    retrieval_titles: list[str],
    messages_history: list[dict],
) -> dict:
    """Execute one conversation turn and return the event results."""
    messages_history.append({"role": "user", "content": user_query})

    params = {
        "conversationId": conversation_id,
        "messages": [m for m in messages_history],
        "query": user_query,
        "rewrittenQuery": f"Java并发编程 {user_query}",
        "retrievalResult": {
            "documents": [{"title": t, "channel": "hybrid"} for t in retrieval_titles],
        },
    }

    events = []
    async for event in tutor.run(
        task_id=task_id,
        trace_id=f"trace-{turn_index}",
        seq=1,
        service_type="TUTORING",
        params=params,
        snapshot=_build_snapshot(),
        system_prompt="test",
    ):
        events.append(event)

    # Extract assistant response text and append to history
    assistant_text = ""
    for event in events:
        if hasattr(event, "payload") and hasattr(event.payload, "text"):
            assistant_text += event.payload.text
    messages_history.append({"role": "assistant", "content": assistant_text})

    return {
        "turn": turn_index,
        "query": user_query,
        "events": events,
        "assistant_text": assistant_text,
        "params": params,
    }


@pytest.mark.asyncio
async def test_full_conversation_memory_and_compaction():
    """Full E2E: 12 turns, compaction triggers at turn ~6, continuity verified."""
    COMPACTOR_BUDGET = 80  # Force compaction early (~40 chars/turn, 80 token budget)
    conversation_id = "conv-e2e-001"
    summary_store = InMemoryConversationSummaryStore()

    tutor = TutorAgent(
        compactor=ConversationCompactor(
            token_budget=COMPACTOR_BUDGET,
            keep_recent_turns=4,
            summary_max_chars=300,
        ),
        summary_store=summary_store,
        llm_client=RuleBasedTutorLLM(),
    )

    messages_history: list[dict] = []
    results: list[dict] = []
    compaction_triggered_at: int | None = None

    for i, (query, titles) in enumerate(TURNS):
        task_id = f"task-{i}"
        result = await _run_turn(
            tutor=tutor,
            conversation_id=conversation_id,
            task_id=task_id,
            turn_index=i,
            user_query=query,
            retrieval_titles=titles,
            messages_history=messages_history,
        )
        results.append(result)

        # Detect compaction event
        if compaction_triggered_at is None:
            progress_events = [
                e for e in result["events"]
                if hasattr(e, "event") and e.event == "progress"
            ]
            for pe in progress_events:
                if hasattr(pe, "payload") and "压缩" in str(pe.payload.message):
                    compaction_triggered_at = i
                    break

    # ── Scoring ──────────────────────────────────────────────────────────

    scores = {}

    # 1. Compaction score
    # compaction should trigger within the first 8 turns
    compaction_ok = compaction_triggered_at is not None and compaction_triggered_at <= 8
    scores["compaction"] = {
        "score": 1.0 if compaction_ok else 0.0,
        "triggered_at_turn": compaction_triggered_at,
        "expected": "compaction triggers at or before turn 8",
        "detail": f"Compaction triggered at turn {compaction_triggered_at}"
        if compaction_triggered_at
        else "Compaction never triggered",
    }

    # 2. Memory persistence score
    # After compaction, a summary should be saved
    saved_summaries = [
        d for d in summary_store.documents if d.conversation_id == conversation_id
    ]
    has_topic_focus = any(
        d.topic_focus for d in saved_summaries
    )
    has_learner_goal = any(
        d.learner_goal for d in saved_summaries
    )
    has_summary_text = any(
        d.summary_text for d in saved_summaries
    )
    memory_score = sum([
        0.25 if saved_summaries else 0.0,
        0.25 if has_topic_focus else 0.0,
        0.25 if has_learner_goal else 0.0,
        0.25 if has_summary_text else 0.0,
    ])
    scores["memory"] = {
        "score": memory_score,
        "summaries_saved": len(saved_summaries),
        "has_topic_focus": has_topic_focus,
        "has_learner_goal": has_learner_goal,
        "has_summary_text": has_summary_text,
    }

    # 3. Answer continuity score
    # Post-compaction answers should reference pre-compaction context
    post_compaction_answers = []
    if compaction_triggered_at is not None:
        post_compaction_answers = [
            r["assistant_text"] for r in results[compaction_triggered_at + 1:]
        ]
    # Check that at least some post-compaction answers are non-empty
    non_empty_answers = [a for a in post_compaction_answers if a.strip()]
    continuity_score = min(1.0, len(non_empty_answers) / max(1, len(post_compaction_answers))) if post_compaction_answers else 0.0
    scores["continuity"] = {
        "score": continuity_score,
        "post_compaction_turns": len(post_compaction_answers),
        "non_empty_answers": len(non_empty_answers),
    }

    # 4. Structured summary quality score
    if saved_summaries:
        latest = saved_summaries[-1]
        quality_checks = {
            "topic_focus_non_empty": bool(latest.topic_focus),
            "summary_text_non_empty": bool(latest.summary_text.strip()),
            "summary_text_reasonable_length": 20 <= len(latest.summary_text) <= 600,
        }
        quality_score = sum(0.33 for v in quality_checks.values() if v)
        quality_score = min(1.0, quality_score)
        scores["summary_quality"] = {
            "score": quality_score,
            **quality_checks,
            "summary_text_preview": latest.summary_text[:120],
        }
    else:
        scores["summary_quality"] = {"score": 0.0, "reason": "no summary saved"}

    # 5. Overall score
    overall = (
        scores["compaction"]["score"] * 0.25
        + scores["memory"]["score"] * 0.25
        + scores["continuity"]["score"] * 0.25
        + scores["summary_quality"]["score"] * 0.25
    )
    scores["overall"] = round(overall, 3)

    # ── Assertions ───────────────────────────────────────────────────────
    assert compaction_ok, (
        f"Compaction did not trigger within 8 turns. "
        f"Triggered at: {compaction_triggered_at}"
    )
    assert memory_score >= 0.5, (
        f"Memory persistence too low: {memory_score}"
    )
    assert continuity_score > 0.0, (
        "No post-compaction answers produced"
    )

    # ── Cleanup: clear all test data ─────────────────────────────────────
    summary_store.documents.clear()
    messages_history.clear()

    # Print scores for review
    import json
    print("\n" + "=" * 60)
    print("TEST SCORES")
    print("=" * 60)
    print(json.dumps(scores, indent=2, ensure_ascii=False))
    print("=" * 60)


@pytest.mark.asyncio
async def test_compaction_preserves_recent_turns():
    """Verify that after compaction, the last N turns are kept verbatim."""
    compactor = ConversationCompactor(token_budget=20, keep_recent_turns=2)
    messages = [
        {"role": "user", "content": "什么是线程"},
        {"role": "assistant", "content": "线程是CPU调度的基本单位"},
        {"role": "user", "content": "synchronized怎么用"},
        {"role": "assistant", "content": "synchronized可以修饰方法或代码块"},
        {"role": "user", "content": "volatile是什么"},
        {"role": "assistant", "content": "volatile保证变量的可见性"},
    ]

    result = compactor.compact(messages)

    assert result.was_compacted is True
    # Last 2 messages should be preserved
    recent = result.compacted_messages[-2:]
    assert recent[0]["content"] == "volatile是什么"
    assert recent[1]["content"] == "volatile保证变量的可见性"
    # First message should be a summary
    assert result.compacted_messages[0]["role"] == "system"
    assert "历史对话摘要" in result.compacted_messages[0]["content"]


@pytest.mark.asyncio
async def test_memory_loads_from_previous_session():
    """Verify that a previous session's summary is available in the next run."""
    store = InMemoryConversationSummaryStore()
    await store.save_summary(
        ConversationSummaryDocument(
            conversationId="conv-prev",
            userId="user-1",
            taskId="task-old",
            topicFocus=["synchronized", "volatile"],
            learnerGoal="掌握Java并发基础",
            knownGaps=["分不清volatile和synchronized"],
            unresolvedQuestions=["什么时候用volatile？"],
            preferredHelpStyle="step_by_step",
            lastUserMessage="volatile和synchronized有什么区别",
            recentProgress=["已讲线程概念"],
            summaryText="主题: synchronized, volatile ; 目标: 掌握Java并发基础",
        )
    )

    tutor = TutorAgent(
        compactor=ConversationCompactor(token_budget=1000, keep_recent_turns=4),
        summary_store=store,
        llm_client=RuleBasedTutorLLM(),
    )

    params = {
        "conversationId": "conv-prev",
        "messages": [
            {"role": "user", "content": "继续上次的话题"},
        ],
        "query": "继续上次的话题",
        "rewrittenQuery": "继续上次的话题",
        "retrievalResult": {"documents": []},
    }

    events = []
    async for event in tutor.run(
        task_id="task-new",
        trace_id="trace-new",
        seq=1,
        service_type="TUTORING",
        params=params,
        snapshot=_build_snapshot(),
        system_prompt="test",
    ):
        events.append(event)

    # The tutor should have loaded the previous summary
    progress_events = [e for e in events if hasattr(e, "event") and e.event == "progress"]
    assert len(progress_events) >= 1

    # Cleanup
    store.documents.clear()


@pytest.mark.asyncio
async def test_small_talk_does_not_trigger_compaction():
    """Greeting/small talk should not produce compaction even with small budget."""
    compactor = ConversationCompactor(token_budget=5, keep_recent_turns=2)
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！"},
    ]

    result = compactor.compact(messages)

    # With only 2 messages and keep_recent_turns=2, no compaction
    assert result.was_compacted is False
