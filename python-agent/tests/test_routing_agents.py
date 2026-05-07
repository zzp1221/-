import pytest

from src.ai_modules.agents.evaluation_agent import EvaluationAgent
from src.ai_modules.agents.path_planning_agent import PathPlanningAgent
from src.ai_modules.agents.query_rewrite_agent import QueryRewriteAgent
from src.ai_modules.agents.retrieval_agent import RetrievalAgent
from src.ai_modules.llms import (
    RuleBasedPlanningLLM,
    RuleBasedQueryRewriteLLM,
    RuleBasedRetrievalLLM,
)
from src.ai_modules.memory import InMemoryLearningPlanStore
from src.ai_modules.models import EvaluationPayload, LearningPlanPayload, QueryRewriteResult
from src.ai_modules.retrieval import HybridRetrievalService
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
        session_id="conv-routing",
        conversation_length=3,
        total_tokens_used=256,
        wiki_pages_count=10,
        last_index_update="2026-05-03",
        recent_activities=["完成索引复习"],
    )


@pytest.mark.asyncio
async def test_query_rewrite_agent_accepts_llm_rewrite_result() -> None:
    class FakeRewriteGenerator:
        async def rewrite(self, *, system_prompt, original_query, learning_context):
            del system_prompt, original_query, learning_context
            return QueryRewriteResult(
                originalQuery="联合索引",
                rewrittenQuery="数据库原理 联合索引 最左匹配",
                keywords=["数据库原理", "联合索引", "最左匹配"],
            )

    agent = QueryRewriteAgent(
        llm_client=RuleBasedQueryRewriteLLM(),
        llm_generator=FakeRewriteGenerator(),
    )
    params = {
        "query": "联合索引",
        "learningContext": {"course": "数据库原理", "chapter": "索引"},
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-query",
            trace_id="trace-query",
            seq=1,
            service_type="RESOURCE_GENERATION",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    assert [event.event for event in events] == ["progress", "result_chunk"]
    assert params["rewrittenQuery"] == "数据库原理 联合索引 最左匹配"
    assert params["queryRewriteContext"]["originalQuery"] == "联合索引"


@pytest.mark.asyncio
async def test_retrieval_agent_uses_summary_generator_when_available() -> None:
    class FakeSummaryGenerator:
        async def summarize(self, *, system_prompt, retrieval_response):
            del system_prompt, retrieval_response
            return "优先参考联合索引与索引导学两类来源。"

    class FakeRetriever:
        def retrieve(self, query: str) -> dict:
            return {
                "query": query,
                "channels": {
                    "grep": {"priority": [("composite-index", "联合索引", 1.0, ["联合索引"])]},
                    "vector": [("db-index", "数据库索引导学", 0.91)],
                    "graph": [],
                },
                "top": [
                    ("db-index", "数据库索引导学", 0.91),
                    ("composite-index", "联合索引", 0.8),
                ],
            }

    agent = RetrievalAgent(
        service=HybridRetrievalService(retriever=FakeRetriever()),
        llm_client=RuleBasedRetrievalLLM(),
        summary_generator=FakeSummaryGenerator(),
    )
    params = {
        "query": "联合索引",
        "rewrittenQuery": "数据库原理 联合索引",
        "keywords": ["数据库原理", "联合索引"],
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-retrieval",
            trace_id="trace-retrieval",
            seq=1,
            service_type="RESOURCE_GENERATION",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    assert [event.event for event in events] == ["progress", "result_chunk"]
    assert "优先参考联合索引与索引导学两类来源" in events[1].payload.text
    assert params["grepRetrievalResult"]["priority"][0][0] == "composite-index"
    assert params["vectorRetrievalResult"]["results"][0][0] == "db-index"
    assert params["mergedRetrievalResult"].documents[0].slug in {"db-index", "composite-index"}


@pytest.mark.asyncio
async def test_evaluation_and_path_planning_agents_raise_when_llm_fails() -> None:
    class FailingEvaluationGenerator:
        async def evaluate(self, *, system_prompt, context_payload):
            del system_prompt, context_payload
            raise RuntimeError("eval llm down")

    class FailingPathGenerator:
        async def plan(self, *, system_prompt, context_payload):
            del system_prompt, context_payload
            raise RuntimeError("plan llm down")

    evaluation_agent = EvaluationAgent(generator=FailingEvaluationGenerator())
    planning_agent = PathPlanningAgent(generator=FailingPathGenerator())
    params = {
        "profile": {"studentLevel": "BASIC", "knowledgeGaps": ["最左匹配", "使用条件"]},
        "learningContext": {"course": "数据库原理", "chapter": "联合索引"},
    }

    with pytest.raises(RuntimeError, match="Evaluation LLM failed"):
        _ = [
            event
            async for event in evaluation_agent.run(
                task_id="task-eval",
                trace_id="trace-eval",
                seq=1,
                service_type="EVALUATION",
                params=params,
                snapshot=_build_snapshot(),
                system_prompt="test",
            )
        ]

    with pytest.raises(RuntimeError, match="Path planning LLM failed"):
        _ = [
            event
            async for event in planning_agent.run(
                task_id="task-plan",
                trace_id="trace-plan",
                seq=3,
                service_type="PATH_PLANNING",
                params=params,
                snapshot=_build_snapshot(),
                system_prompt="test",
            )
        ]


@pytest.mark.asyncio
async def test_evaluation_agent_uses_llm_generated_report_via_agent_core_loop() -> None:
    class FakeEvaluationGenerator:
        async def evaluate(self, *, system_prompt, context_payload):
            del system_prompt
            assert context_payload["aggregatedBehavior"]["behaviorSignals"]["practiceAccuracy"] == 0.5
            return EvaluationPayload.model_validate(
                {
                    "overallLevel": "INTERMEDIATE",
                    "strengths": ["LLM 识别出学生愿意练习"],
                    "weaknesses": ["最左匹配", "使用条件"],
                    "nextFocus": ["最左匹配", "条件判断"],
                    "dimensions": [
                        {
                            "name": "knowledge_foundation",
                            "level": "INTERMEDIATE",
                            "evidence": "LLM 综合画像与练习结果后认为基础可继续提升。",
                            "recommendation": "围绕最左匹配补例题训练。",
                        }
                    ],
                    "summaryText": "LLM 评估：学生基础接近中等，但条件判断仍不稳定。",
                }
            )

    agent = EvaluationAgent(
        llm_client=RuleBasedPlanningLLM(),
        generator=FakeEvaluationGenerator(),
    )
    params = {
        "profile": {"studentLevel": "BASIC", "knowledgeGaps": ["最左匹配", "使用条件"]},
        "judgeResult": {"accuracy": 0.5, "weakKnowledgeTags": ["条件判断"]},
        "messages": [{"role": "user", "content": "我总是搞不清最左匹配什么时候失效。"}],
        "learningContext": {"course": "数据库原理", "chapter": "联合索引"},
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-eval-llm",
            trace_id="trace-eval-llm",
            seq=1,
            service_type="EVALUATION",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    assert [event.event for event in events] == ["progress", "result_chunk"]
    assert params["aggregatedEvaluationContext"]["candidateWeaknesses"][0] == "最左匹配"
    assert params["evaluationResult"]["overallLevel"] == "INTERMEDIATE"
    assert events[1].payload.text.startswith("LLM 评估：")


@pytest.mark.asyncio
async def test_path_planning_agent_generates_and_persists_learning_path_via_agent_core_loop() -> None:
    class FakePathGenerator:
        async def plan(self, *, system_prompt, context_payload):
            del system_prompt
            assert context_payload["planningContext"]["triggerSource"] == "EVALUATION"
            return LearningPlanPayload.model_validate(
                {
                    "goal": "掌握联合索引的最左匹配规则",
                    "duration": "4天",
                    "milestones": ["理解规则", "判断条件", "解释场景"],
                    "steps": [
                        {
                            "title": "规则回顾",
                            "objective": "LLM 先带你回顾最左匹配。",
                            "activities": ["复述定义", "对照反例"],
                            "successCriteria": "能说清失效条件",
                        },
                        {
                            "title": "场景练习",
                            "objective": "用题目判断联合索引是否命中。",
                            "activities": ["先判条件", "再解释理由"],
                            "successCriteria": "连续 3 题判断正确",
                        },
                    ],
                    "summaryText": "LLM 路径：先掌握最左匹配，再做条件判断训练。",
                }
            )

    store = InMemoryLearningPlanStore()
    agent = PathPlanningAgent(
        llm_client=RuleBasedPlanningLLM(),
        learning_plan_store=store,
        generator=FakePathGenerator(),
    )
    params = {
        "userId": "00000000-0000-0000-0000-000000000777",
        "profile": {"studentLevel": "BASIC", "knowledgeGaps": ["最左匹配", "使用条件"]},
        "evaluationResult": {
            "overallLevel": "BASIC",
            "weaknesses": ["最左匹配", "使用条件"],
            "nextFocus": ["最左匹配"],
            "strengths": ["愿意练习"],
            "dimensions": [],
            "summaryText": "待规划",
        },
        "learningContext": {"course": "数据库原理", "chapter": "联合索引"},
    }

    events = [
        event
        async for event in agent.run(
            task_id="task-plan-llm",
            trace_id="trace-plan-llm",
            seq=3,
            service_type="PATH_PLANNING",
            params=params,
            snapshot=_build_snapshot(),
            system_prompt="test",
        )
    ]

    stored_record = store.active_plans_by_user["00000000-0000-0000-0000-000000000777"]

    assert [event.event for event in events] == ["progress", "result_chunk"]
    assert params["learningPath"]["goal"] == "掌握联合索引的最左匹配规则"
    assert params["learningPlanPersistence"]["version"] == 1
    assert stored_record["summaryText"].startswith("LLM 路径：")
    assert events[1].payload.text.startswith("LLM 路径：")


@pytest.mark.asyncio
async def test_in_memory_learning_plan_store_versions_snapshots() -> None:
    store = InMemoryLearningPlanStore()
    user_id = "00000000-0000-0000-0000-000000000888"
    first_plan = LearningPlanPayload.model_validate(
        {
            "goal": "先掌握定义",
            "duration": "2天",
            "milestones": ["理解概念"],
            "steps": [
                {
                    "title": "看定义",
                    "objective": "理解联合索引的定义。",
                    "activities": ["看讲义"],
                    "successCriteria": "能复述定义",
                }
            ],
            "summaryText": "第一版学习路径",
        }
    )
    second_plan = first_plan.model_copy(
        update={
            "summary_text": "第二版学习路径",
            "milestones": ["理解概念", "补充练习"],
        }
    )

    first_metadata = await store.save_plan(
        user_id=user_id,
        plan=first_plan,
        trigger_source="INITIAL",
    )
    second_metadata = await store.save_plan(
        user_id=user_id,
        plan=second_plan,
        trigger_source="EVALUATION",
    )

    assert first_metadata["version"] == 1
    assert second_metadata["version"] == 2
    assert first_metadata["planId"] == second_metadata["planId"]
    assert len(store.snapshots_by_plan[first_metadata["planId"]]) == 2
