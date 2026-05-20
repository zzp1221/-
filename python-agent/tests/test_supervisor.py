import asyncio

import pytest

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.models import (
    DialogState,
    EngineStreamRequest,
    JudgeResultPayload,
    JudgeResultSSEEvent,
    ProgressPayload,
    ProgressSSEEvent,
    QuestionBatchPayload,
    QuestionBatchSSEEvent,
    ResourceFilePayload,
    ResourceFileSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    VideoProgressSSEEvent,
)
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
    ]
    assert route.retrieval_strategy == "LOCAL_HYBRID"


def test_supervisor_routes_small_talk_to_tutor_only() -> None:
    supervisor = PythonAgentSupervisor()

    route = supervisor.resolve_route("TUTORING", {"query": "你好"})

    assert route.agent_names == ["tutor"]
    assert route.query_type == "SMALL_TALK"
    assert route.retrieval_strategy == "NONE"


def test_supervisor_routes_deep_reasoning_to_deep_agent() -> None:
    supervisor = PythonAgentSupervisor()

    route = supervisor.resolve_route(
        "TUTORING",
        {"query": "完整分析联合索引失效的所有边界", "reasoningMode": "DEEP"},
    )

    assert route.agent_names == [
        "query_rewrite",
        "retrieval",
        "image_analysis",
        "deep_reasoning",
    ]
    assert route.retrieval_strategy == "DEEP_EVIDENCE"


class _RecordingRewriteAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("rewrite", "query_rewrite")

    async def run(self, *, params, **kwargs):
        params["rewrittenQuery"] = "Java 程序设计 并发编程"
        params["keywords"] = ["Java", "程序设计", "并发编程"]
        if False:
            yield


class _RecordingRetrievalAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("retrieval", "retrieval")
        self.seen_rewritten_query = None
        self.seen_keywords = None

    async def run(self, *, params, **kwargs):
        self.seen_rewritten_query = params.get("rewrittenQuery")
        self.seen_keywords = list(params.get("keywords", []))
        if False:
            yield


class _StubRewriteAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub rewrite", "query_rewrite")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["rewrittenQuery"] = "数据库原理 联合索引"
        params["keywords"] = ["数据库原理", "联合索引"]
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="query_rewrite", percent=15, message="已完成问题改写"),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text="改写后：数据库原理 联合索引"),
        )


class _StubRetrievalAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub retrieval", "retrieval")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["retrievalResult"] = {
            "documents": [{"title": "联合索引导学", "channel": "hybrid"}],
            "sourcesSummary": "来源摘要：优先参考联合索引导学。",
        }
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="retrieval", percent=35, message="已完成资料检索"),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text="来源摘要：优先参考联合索引导学。"),
        )


class _StubTutorAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub tutor", "tutoring")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["structuredConversationSummary"] = {"lastUserMessage": "好"}
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="tutoring", percent=45, message="开始辅导"),
            dialogState=DialogState(
                conversationId=str(params.get("conversationId") or "conv"),
                turnId=f"{task_id}-turn",
                pedagogyStrategy="diagnostic_scaffold",
                nextAction="ask_follow_up",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text="联合索引需要先理解最左匹配规则。"),
        )


class _StubProfileAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub profile", "profiling")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["profileUpdate"] = {"summaryText": "画像更新完成"}
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="profiling", percent=90, message="已完成画像分析并写入快照"),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text="画像更新完成"),
        )


class _FailingBackgroundProfileAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("failing profile", "profiling")
        self.started = asyncio.Event()

    async def run(self, *, params, **kwargs):
        del params, kwargs
        self.started.set()
        raise RuntimeError("画像构建失败")
        if False:
            yield


class _StubDocumentGeneratorAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub document", "document_generation")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["generatedAsset"] = {"title": "联合索引导学文档", "summary": "结构化导学"}
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ResultChunkPayload(text="文档生成完成"),
        )
        yield ResourceFileSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResourceFilePayload(
                assetType="DOCUMENT",
                title="联合索引导学文档",
                summary="结构化导学",
                displayMode="download",
                fileName="document.md",
                localPath="sandbox/document.md",
                mimeType="text/markdown",
            ),
        )


class _StubVideoGeneratorAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub video", "video_generation")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["generatedAsset"] = {"title": "联合索引教学视频", "summary": "视频讲解"}
        yield VideoProgressSSEEvent(
            event="video_gen:start",
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="video_started", percent=10, message="视频生成开始"),
        )
        yield VideoProgressSSEEvent(
            event="video_gen:script",
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ProgressPayload(stage="script_generated", percent=25, message="脚本生成完成"),
        )
        yield VideoProgressSSEEvent(
            event="video_gen:speech",
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 2,
            payload=ProgressPayload(
                stage="speech_synthesized",
                percent=50,
                message="语音合成完成",
                audioBase64="ZmFrZS1hdWRpby1iYXNlNjQ=",
                format="mp3",
                avatarDataUrl="/dh_live/assets/combined_data.json.gz",
                durationSeconds=60,
                title="联合索引教学视频",
                topic="联合索引",
                videoStyle="hybrid",
            ),
        )
        yield VideoProgressSSEEvent(
            event="video_gen:avatar",
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 3,
            payload=ProgressPayload(stage="video_rendering", percent=75, message="视频渲染中"),
        )
        yield ResourceFileSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 4,
            payload=ResourceFilePayload(
                assetType="VIDEO",
                title="联合索引教学视频",
                summary="视频讲解",
                displayMode="download",
                fileName="browser-rendered.webm",
                localPath=None,
                mimeType="video/webm",
                thumbnailPath="sandbox/video.png",
                thumbnailFileName="video.png",
                thumbnailMimeType="image/png",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 5,
            payload=ResultChunkPayload(text="视频生成完成"),
        )


class _StubPracticeAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub practice", "practice")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="practice", percent=30, message="练习题生成完成"),
        )
        payload = QuestionBatchPayload.model_validate(
            {
                "title": "联合索引练习",
                "topic": "联合索引",
                "difficulty": "BASIC",
                "questions": [
                    {
                        "questionId": "q1",
                        "questionType": "SINGLE_CHOICE",
                        "stem": "最左匹配规则是什么？",
                        "options": ["A", "B", "C", "D"],
                        "answer": "A",
                        "knowledgeTags": ["最左匹配"],
                        "difficultyLevel": "BASIC",
                        "explanation": "解释",
                    }
                ],
            }
        )
        params["practiceQuestionBatch"] = payload.model_dump(by_alias=True)
        yield QuestionBatchSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=payload,
        )


class _StubJudgeAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub judge", "judge")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        payload = JudgeResultPayload.model_validate(
            {
                "title": "联合索引判题结果",
                "summary": "最左匹配理解仍需加强",
                "totalScore": 60,
                "accuracy": 0.6,
                "items": [
                    {
                        "questionId": "q1",
                        "questionType": "SINGLE_CHOICE",
                        "learnerAnswer": "B",
                        "correctAnswer": "A",
                        "isCorrect": False,
                        "score": 0,
                        "knowledgeTags": ["最左匹配"],
                        "reason": "判断错误",
                        "feedback": "复习最左匹配",
                        "profileDelta": {"weakPoints": ["最左匹配"]},
                    }
                ],
            }
        )
        params["judgeResult"] = payload.model_dump(by_alias=True)
        yield JudgeResultSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=payload,
        )


class _StubEvaluationAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub evaluation", "evaluation")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["evaluationResult"] = {
            "overallLevel": "BASIC",
            "strengths": ["愿意学习"],
            "weaknesses": ["最左匹配"],
            "nextFocus": ["最左匹配"],
            "dimensions": [],
            "summaryText": "已完成能力评估",
        }
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="evaluation", percent=45, message="已完成能力评估"),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text="已完成能力评估"),
        )


class _StubPathPlanningAgent(PlaceholderAgent):
    def __init__(self) -> None:
        super().__init__("stub planning", "path_planning")

    async def run(self, *, task_id, trace_id, seq, params, **kwargs):
        params["learningPath"] = {
            "goal": "掌握最左匹配",
            "duration": "4天",
            "milestones": ["理解规则"],
            "steps": [],
            "summaryText": "学习路径：先理解最左匹配，再做题巩固。",
        }
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(stage="path_planning", percent=75, message="已生成学习路径"),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text="学习路径：先理解最左匹配，再做题巩固。"),
        )


@pytest.mark.asyncio
async def test_supervisor_runs_retrieval_after_query_rewrite() -> None:
    supervisor = PythonAgentSupervisor()
    rewrite_agent = _RecordingRewriteAgent()
    retrieval_agent = _RecordingRetrievalAgent()
    supervisor.agent_registry["query_rewrite"] = rewrite_agent
    supervisor.agent_registry["retrieval"] = retrieval_agent
    supervisor.agent_registry["document_generator"] = PlaceholderAgent("doc", "document_generator")

    request = EngineStreamRequest(
        serviceType="RESOURCE_GENERATION",
        params={"resourceType": "DOCUMENT", "query": "并发编程"},
        taskId="task-seq",
        traceId="trace-seq",
    )

    _ = [event async for event in supervisor.stream(request)]

    assert retrieval_agent.seen_rewritten_query == "Java 程序设计 并发编程"
    assert retrieval_agent.seen_keywords == ["Java", "程序设计", "并发编程"]


@pytest.mark.asyncio
async def test_supervisor_streams_profile_build_route() -> None:
    supervisor = PythonAgentSupervisor()
    supervisor.agent_registry["tutor"] = _StubTutorAgent()
    supervisor.agent_registry["profile"] = _StubProfileAgent()
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
    supervisor.agent_registry["query_rewrite"] = _StubRewriteAgent()
    supervisor.agent_registry["retrieval"] = _StubRetrievalAgent()
    supervisor.agent_registry["document_generator"] = _StubDocumentGeneratorAgent()
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
    supervisor.agent_registry["query_rewrite"] = _StubRewriteAgent()
    supervisor.agent_registry["retrieval"] = _StubRetrievalAgent()
    supervisor.agent_registry["video_generator"] = _StubVideoGeneratorAgent()
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

    assert events[0].event == "progress"
    assert any(event.event == "video_gen:start" for event in events)
    assert any(event.event == "video_gen:speech" for event in events)
    resource_event = next(event for event in events if event.event == "resource_file")
    assert resource_event.payload.asset_type == "VIDEO"
    assert resource_event.payload.thumbnail_path is not None
    speech_event = next(event for event in events if event.event == "video_gen:speech")
    assert speech_event.payload.audio_base64 is not None
    assert any(event.event == "done" and "教学视频" in event.payload.summary for event in events)


@pytest.mark.asyncio
async def test_supervisor_streams_video_generation_route() -> None:
    supervisor = PythonAgentSupervisor()
    supervisor.agent_registry["query_rewrite"] = _StubRewriteAgent()
    supervisor.agent_registry["retrieval"] = _StubRetrievalAgent()
    supervisor.agent_registry["video_generator"] = _StubVideoGeneratorAgent()
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

    assert events[0].event == "progress"
    assert any(event.event == "video_gen:avatar" for event in events)
    assert any(event.event == "resource_file" and event.payload.asset_type == "VIDEO" for event in events)


@pytest.mark.asyncio
async def test_supervisor_streams_practice_judge_route_with_profile_feedback() -> None:
    supervisor = PythonAgentSupervisor()
    supervisor.agent_registry["practice"] = _StubPracticeAgent()
    supervisor.agent_registry["judge"] = _StubJudgeAgent()
    supervisor.agent_registry["profile"] = _StubProfileAgent()
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
async def test_supervisor_injects_top_level_user_and_conversation_into_agent_params() -> None:
    class RecordingAgent(PlaceholderAgent):
        def __init__(self) -> None:
            super().__init__("recording profile", "profiling")
            self.seen_user_id = None
            self.seen_conversation_id = None

        async def run(self, *, params, **kwargs):
            self.seen_user_id = params.get("userId")
            self.seen_conversation_id = params.get("conversationId")
            if False:
                yield

    supervisor = PythonAgentSupervisor()
    recording_agent = RecordingAgent()
    supervisor.agent_registry["practice"] = _StubPracticeAgent()
    supervisor.agent_registry["judge"] = _StubJudgeAgent()
    supervisor.agent_registry["profile"] = recording_agent
    request = EngineStreamRequest(
        serviceType="PRACTICE_JUDGE",
        userId="user-top-level",
        conversationId="conv-top-level",
        params={
            "topic": "联合索引",
            "answers": {"q1": "A"},
        },
        taskId="task-param-injection",
        traceId="trace-param-injection",
    )

    events = [event async for event in supervisor.stream(request)]

    assert events[-1].event == "done"
    assert recording_agent.seen_user_id == "user-top-level"
    assert recording_agent.seen_conversation_id == "conv-top-level"
    assert request.params == {
        "topic": "联合索引",
        "answers": {"q1": "A"},
    }


@pytest.mark.asyncio
async def test_supervisor_streams_tutoring_route_with_retrieval_then_tutor() -> None:
    supervisor = PythonAgentSupervisor()
    supervisor.agent_registry["query_rewrite"] = _StubRewriteAgent()
    supervisor.agent_registry["retrieval"] = _StubRetrievalAgent()
    supervisor.agent_registry["tutor"] = _StubTutorAgent()
    supervisor.agent_registry["profile"] = _StubProfileAgent()
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

    assert events[-1].event == "done"
    tutor_progress = next(event for event in events if event.event == "progress" and event.dialog_state is not None)
    assert tutor_progress.dialog_state.next_action == "ask_follow_up"
    tutor_result = next(event for event in events if event.event == "result_chunk" and "联合索引" in event.payload.text)
    assert "联合索引" in tutor_result.payload.text


@pytest.mark.asyncio
async def test_supervisor_runs_tutoring_profile_in_background() -> None:
    supervisor = PythonAgentSupervisor()
    profile_agent = _FailingBackgroundProfileAgent()
    supervisor.agent_registry["query_rewrite"] = _StubRewriteAgent()
    supervisor.agent_registry["retrieval"] = _StubRetrievalAgent()
    supervisor.agent_registry["tutor"] = _StubTutorAgent()
    supervisor.agent_registry["profile"] = profile_agent
    request = EngineStreamRequest(
        serviceType="TUTORING",
        params={
            "query": "好",
            "messages": [
                {"role": "user", "content": "老师，我不太懂联合索引"},
                {"role": "assistant", "content": "我们先从定义开始"},
                {"role": "user", "content": "我还是容易做错"},
                {"role": "assistant", "content": "那我们结合题目来分析"},
                {"role": "user", "content": "好"},
            ],
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
            "profile": {"studentLevel": "BASIC"},
            "conversationId": "conv-tutor-background-profile",
        },
        taskId="task-tutor-background-profile",
        traceId="trace-tutor-background-profile",
    )

    events = [event async for event in supervisor.stream(request)]
    await asyncio.wait_for(profile_agent.started.wait(), timeout=1)

    assert events[-1].event == "done"
    assert any(event.event == "result_chunk" for event in events)
    assert not any(
        event.event == "progress" and getattr(event.payload, "stage", "") == "profiling"
        for event in events
    )


@pytest.mark.asyncio
async def test_supervisor_skips_tutoring_profile_before_third_turn() -> None:
    supervisor = PythonAgentSupervisor()
    profile_agent = _FailingBackgroundProfileAgent()
    supervisor.agent_registry["query_rewrite"] = _StubRewriteAgent()
    supervisor.agent_registry["retrieval"] = _StubRetrievalAgent()
    supervisor.agent_registry["tutor"] = _StubTutorAgent()
    supervisor.agent_registry["profile"] = profile_agent
    request = EngineStreamRequest(
        serviceType="TUTORING",
        params={
            "query": "我还是容易做错",
            "messages": [
                {"role": "user", "content": "老师，我不太懂联合索引"},
                {"role": "assistant", "content": "我们先从定义开始"},
                {"role": "user", "content": "我还是容易做错"},
            ],
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
            "profile": {"studentLevel": "BASIC"},
            "conversationId": "conv-tutor-background-profile-skip",
        },
        taskId="task-tutor-background-profile-skip",
        traceId="trace-tutor-background-profile-skip",
    )

    events = [event async for event in supervisor.stream(request)]

    assert events[-1].event == "done"
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(profile_agent.started.wait(), timeout=0.2)


@pytest.mark.asyncio
async def test_supervisor_streams_evaluation_route() -> None:
    supervisor = PythonAgentSupervisor()
    supervisor.agent_registry["evaluation"] = _StubEvaluationAgent()
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

    assert events[-1].event == "done"
    assert events[0].payload.message == "已完成能力评估"
    assert any(event.event == "result_chunk" and "已完成能力评估" in event.payload.text for event in events)
    assert events[-1].payload.summary == "EVALUATION 路由完成，执行链路: evaluation"


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
