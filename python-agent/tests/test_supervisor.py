import pytest

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.models import EngineStreamRequest
from src.ai_modules.supervisor import PythonAgentSupervisor


def test_supervisor_resolves_resource_generation_route() -> None:
    supervisor = PythonAgentSupervisor()

    route = supervisor.resolve_route(
        "RESOURCE_GENERATION",
        {"resourceType": "DOCUMENT"},
    )

    assert route.agent_names == [
        "query_rewrite",
        "retrieval",
        "document_generator",
    ]


def test_supervisor_prefers_video_generator_when_resource_types_include_video() -> None:
    supervisor = PythonAgentSupervisor()

    route = supervisor.resolve_route(
        "RESOURCE_GENERATION",
        {"resourceTypes": ["EXPLANATION", "VIDEO"]},
    )

    assert route.agent_names == [
        "query_rewrite",
        "retrieval",
        "video_generator",
    ]


def test_supervisor_resolves_video_generation_route() -> None:
    supervisor = PythonAgentSupervisor()

    route = supervisor.resolve_route(
        "RESOURCE_GENERATION",
        {"resourceType": "VIDEO"},
    )

    assert route.agent_names == [
        "query_rewrite",
        "retrieval",
        "video_generator",
    ]


def test_supervisor_routes_tutoring_through_profile_update() -> None:
    supervisor = PythonAgentSupervisor()

    route = supervisor.resolve_route(
        "TUTORING",
        {"query": "联合索引"},
    )

    assert route.agent_names == [
        "query_rewrite",
        "retrieval",
        "tutor",
        "profile",
    ]


@pytest.mark.asyncio
async def test_supervisor_streams_profile_build_route() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="PROFILE_BUILD",
        params={
            "messages": [
                {"role": "user", "content": "老师，我刚学数据库，想一步步理解联合索引。"},
                {"role": "assistant", "content": "我们先从定义开始。"},
                {"role": "user", "content": "我做题时总是分不清什么时候会失效。"},
            ],
            "profile": {
                "studentLevel": "BASIC",
                "professionalBackground": "计算机本科生",
            },
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
        },
        taskId="task-profile",
        traceId="trace-profile",
    )

    events = [event async for event in supervisor.stream(request)]

    assert events[0].event == "progress"
    assert events[-1].event == "done"
    assert events[0].dialog_state is not None
    profile_progress = next((e for e in events if e.event == "progress" and "画像" in (e.payload.message or "")), None)
    assert profile_progress is not None
    assert "PROFILE_BUILD" in events[-1].payload.summary


def test_supervisor_rejects_unknown_service_type() -> None:
    supervisor = PythonAgentSupervisor()

    with pytest.raises(ValueError):
        supervisor.resolve_route("UNKNOWN", {})


@pytest.mark.asyncio
async def test_supervisor_streams_resource_generation_with_retrieval_chain() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="RESOURCE_GENERATION",
        params={
            "resourceType": "DOCUMENT",
            "query": "联合索引",
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
        },
        taskId="task-resource",
        traceId="trace-resource",
    )

    events = [event async for event in supervisor.stream(request)]

    assert events[0].event == "progress"
    assert events[1].event == "result_chunk"
    assert events[-1].event == "done"
    assert any(e.event == "resource_file" for e in events)
    assert "改写后" in events[1].payload.text
    assert "来源摘要" in events[3].payload.text


@pytest.mark.asyncio
async def test_supervisor_streams_video_generation_events() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="RESOURCE_GENERATION",
        params={
            "resourceType": "VIDEO",
            "query": "联合索引",
            "topic": "联合索引",
            "style": "hybrid",
            "duration": 60,
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
        },
        taskId="task-video",
        traceId="trace-video",
    )

    events = [event async for event in supervisor.stream(request)]

    assert [event.event for event in events] == [
        "progress",
        "result_chunk",
        "progress",
        "result_chunk",
        "progress",
        "progress",
        "progress",
        "progress",
        "result_chunk",
        "resource_file",
        "result_chunk",
        "done",
    ]
    assert events[9].payload.asset_type == "VIDEO"
    assert events[9].payload.thumbnail_path is not None
    assert "视频生成完成" in events[10].payload.text
    assert "教学视频" in events[11].payload.summary


@pytest.mark.asyncio
async def test_supervisor_streams_video_generation_route() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="RESOURCE_GENERATION",
        params={
            "resourceType": "VIDEO",
            "query": "快速排序",
            "topic": "快速排序算法",
            "style": "hybrid",
            "learningContext": {"course": "数据结构", "chapter": "排序"},
        },
        taskId="task-video",
        traceId="trace-video",
    )

    events = [event async for event in supervisor.stream(request)]

    assert [event.event for event in events] == [
        "progress",
        "result_chunk",
        "progress",
        "result_chunk",
        "progress",
        "progress",
        "progress",
        "progress",
        "result_chunk",
        "resource_file",
        "result_chunk",
        "done",
    ]
    assert events[9].payload.asset_type == "VIDEO"


@pytest.mark.asyncio
async def test_supervisor_streams_practice_judge_route_with_profile_feedback() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="PRACTICE_JUDGE",
        params={
            "topic": "联合索引",
            "difficulty": "BASIC",
            "count": 5,
            "profile": {
                "studentLevel": "BASIC",
                "professionalBackground": "计算机本科生",
            },
            "learningContext": {"course": "数据库原理", "chapter": "联合索引"},
            "answers": {
                "q1": "C",
                "q2": "B",
                "q3": "我知道要判断条件，但还不会举出误判场景。",
                "q4": "A",
                "q5": "",
            },
        },
        taskId="task-practice-judge",
        traceId="trace-practice-judge",
    )

    events = [event async for event in supervisor.stream(request)]

    assert events[0].event == "progress"
    assert any(e.event == "question_batch" for e in events)
    assert any(e.event == "judge_result" for e in events)
    assert events[-1].event == "done"
    question_batch = next(e for e in events if e.event == "question_batch")
    assert question_batch.payload.topic == "联合索引"
    judge_result = next(e for e in events if e.event == "judge_result")
    assert judge_result.payload.accuracy < 1.0


@pytest.mark.asyncio
async def test_supervisor_streams_tutoring_route_with_retrieval_then_tutor() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="TUTORING",
        params={
            "query": "联合索引",
            "messages": [
                {"role": "user", "content": "老师我不太懂联合索引"},
                {"role": "assistant", "content": "我们先从定义开始"},
                {"role": "user", "content": "我还是容易做错"},
                {"role": "assistant", "content": "那我们结合题目来分析"},
                {"role": "user", "content": "好"},
            ],
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
            "profile": {"knowledgeGaps": ["联合索引"], "studentLevel": "BASIC"},
            "conversationLength": 32,
            "totalTokensUsed": 2048,
            "conversationId": "conv-tutor",
        },
        taskId="task-tutor",
        traceId="trace-tutor",
    )

    events = [event async for event in supervisor.stream(request)]

    assert [event.event for event in events] == [
        "progress",
        "result_chunk",
        "progress",
        "result_chunk",
        "progress",
        "result_chunk",
        "done",
    ]
    assert events[4].dialog_state is not None
    assert events[4].dialog_state.next_action == "ask_follow_up"
    assert "联合索引" in events[5].payload.text


@pytest.mark.asyncio
async def test_supervisor_streams_evaluation_route() -> None:
    supervisor = PythonAgentSupervisor()
    request = EngineStreamRequest(
        serviceType="EVALUATION",
        params={
            "profile": {
                "studentLevel": "BASIC",
                "knowledgeGaps": ["最左匹配", "使用条件"],
            },
            "learningContext": {"course": "数据库原理", "chapter": "联合索引"},
        },
        taskId="task-evaluation",
        traceId="trace-evaluation",
    )

    events = [event async for event in supervisor.stream(request)]

    assert [event.event for event in events] == ["progress", "result_chunk", "progress", "result_chunk", "done"]
    assert events[0].payload.message == "已完成能力评估"
    assert "学习路径" in events[3].payload.text


@pytest.mark.asyncio
async def test_supervisor_does_not_commit_partial_param_mutations_when_agent_fails() -> None:
    class MutatingFailingAgent(PlaceholderAgent):
        def __init__(self) -> None:
            super().__init__("Failing Agent", "failing")

        async def run(self, **kwargs):
            params = kwargs["params"]
            params["rewrittenQuery"] = "should-not-leak"
            raise RuntimeError("simulated failure")
            yield  # pragma: no cover

    supervisor = PythonAgentSupervisor()
    supervisor.agent_registry["query_rewrite"] = MutatingFailingAgent()
    request = EngineStreamRequest(
        serviceType="RESOURCE_GENERATION",
        params={
            "resourceType": "DOCUMENT",
            "query": "联合索引",
        },
        taskId="task-failure",
        traceId="trace-failure",
    )

    with pytest.raises(RuntimeError, match="simulated failure"):
        _ = [event async for event in supervisor.stream(request)]

    assert request.params == {
        "resourceType": "DOCUMENT",
        "query": "联合索引",
    }
