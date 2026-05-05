"""Supervisor that resolves routes and streams agent execution results."""

from __future__ import annotations

import asyncio
import copy
from collections.abc import AsyncIterator

from pydantic import BaseModel, ConfigDict, Field

from src.ai_modules.agents import (
    CodeGeneratorAgent,
    DocumentGeneratorAgent,
    EvaluationAgent,
    JudgeAgent,
    MindMapGeneratorAgent,
    PathPlanningAgent,
    PracticeAgent,
    ProfileAgent,
    QueryRewriteAgent,
    ReadingGeneratorAgent,
    ResourcePushAgent,
    RetrievalAgent,
    SlideGeneratorAgent,
    TutorAgent,
    VideoGenerationAgent,
)
from src.ai_modules.models import DonePayload, DoneSSEEvent, EngineStreamRequest, ErrorPayload, ErrorSSEEvent, SSEEvent
from src.ai_modules.runtime import SnapshotBuilder, SystemSnapshot


class RoutePlan(BaseModel):
    """Resolved service route plan."""

    service_type: str = Field(alias="serviceType")
    agent_names: list[str] = Field(alias="agentNames")

    model_config = ConfigDict(populate_by_name=True)


class PythonAgentSupervisor:
    """Resolve service routes and execute agents sequentially."""

    def __init__(self) -> None:
        self.snapshot_builder = SnapshotBuilder()
        self.agent_registry = {
            "query_rewrite": QueryRewriteAgent(),
            "retrieval": RetrievalAgent(),
            "document_generator": DocumentGeneratorAgent(),
            "slide_generator": SlideGeneratorAgent(),
            "reading_generator": ReadingGeneratorAgent(),
            "mindmap_generator": MindMapGeneratorAgent(),
            "code_generator": CodeGeneratorAgent(),
            "video_generator": VideoGenerationAgent(),
            "tutor": TutorAgent(),
            "profile": ProfileAgent(),
            "practice": PracticeAgent(),
            "judge": JudgeAgent(),
            "path_planning": PathPlanningAgent(),
            "evaluation": EvaluationAgent(),
            "resource_push": ResourcePushAgent(),
        }

    def resolve_route(self, service_type: str, params: dict) -> RoutePlan:
        requested_resource_type = self._resolve_resource_type(params)
        generation_agent = {
            "DOCUMENT": "document_generator",
            "SLIDES": "slide_generator",
            "READING": "reading_generator",
            "MINDMAP": "mindmap_generator",
            "CODE": "code_generator",
            "VIDEO": "video_generator",
        }.get(requested_resource_type, "document_generator")

        route_map = {
            "PROFILE_BUILD": ["tutor", "profile"],
            "RESOURCE_GENERATION": ["query_rewrite", "retrieval", generation_agent],
            "RESOURCE_PUSH": ["resource_push"],
            "VIDEO_GENERATION": ["query_rewrite", "retrieval", "video_generator"],
            "PRACTICE_JUDGE": ["practice", "judge", "profile"],
            "PATH_PLANNING": ["path_planning"],
            "EVALUATION": ["evaluation", "path_planning"],
            "LEARNING_EVALUATION": ["evaluation", "path_planning"],
            "TUTORING": ["query_rewrite", "retrieval", "tutor", "profile"],
        }
        if service_type not in route_map:
            raise ValueError(f"Unsupported serviceType: {service_type}")

        return RoutePlan(
            serviceType=service_type,
            agentNames=route_map[service_type],
        )

    def _resolve_resource_type(self, params: dict) -> str:
        resource_type = params.get("resourceType")
        if isinstance(resource_type, str) and resource_type.strip():
            return self._normalize_resource_type(resource_type)
        resource_types = params.get("resourceTypes")
        if isinstance(resource_types, list):
            normalized = [self._normalize_resource_type(str(item)) for item in resource_types if str(item).strip()]
            if "VIDEO" in normalized:
                return "VIDEO"
            if normalized:
                return normalized[0]
        return "DOCUMENT"

    def _normalize_resource_type(self, resource_type: str) -> str:
        normalized = resource_type.strip().upper()
        return {
            "EXPLANATION": "DOCUMENT",
            "CODE_CASE": "CODE",
            "QUIZ": "DOCUMENT",
        }.get(normalized, normalized)

    async def build_snapshot(self, request: EngineStreamRequest) -> SystemSnapshot:
        return await self.snapshot_builder.build(
            user_id=request.user_id,
            task_id=request.task_id,
            conversation_id=request.conversation_id,
            params=request.params,
        )

    def build_agent_system_prompt(
        self,
        *,
        agent_name: str,
        snapshot: SystemSnapshot,
    ) -> str:
        return self.agent_registry[agent_name].system_prompt(snapshot)

    async def stream(self, request: EngineStreamRequest, cancelled: set[str] | None = None) -> AsyncIterator[SSEEvent]:
        route_plan = self.resolve_route(request.service_type, request.params)
        snapshot = await self.build_snapshot(request)
        current_params = copy.deepcopy(request.params)
        seq = 1
        agent_names = list(route_plan.agent_names)
        i = 0
        while i < len(agent_names):
            if cancelled and request.task_id in cancelled:
                yield ErrorSSEEvent(
                    taskId=request.task_id,
                    traceId=request.trace_id,
                    seq=seq,
                    payload=ErrorPayload(
                        code="TASK_CANCELLED",
                        message="任务已被取消",
                    ),
                )
                yield DoneSSEEvent(
                    taskId=request.task_id,
                    traceId=request.trace_id,
                    seq=seq + 1,
                    payload=DonePayload(
                        status="FAILED",
                        summary="任务已被取消",
                    ),
                )
                return

            agent_name = agent_names[i]

            # P0-2: Run query_rewrite and retrieval in parallel
            if (
                agent_name == "query_rewrite"
                and i + 1 < len(agent_names)
                and agent_names[i + 1] == "retrieval"
            ):
                rewrite_params = copy.deepcopy(current_params)
                retrieval_params = copy.deepcopy(current_params)
                retrieval_params["rewrittenQuery"] = str(
                    retrieval_params.get("query")
                    or retrieval_params.get("message", "")
                )
                retrieval_params["keywords"] = []

                async def _run_agent(_agent_name: str, _agent_params: dict):
                    agent = self.agent_registry[_agent_name]
                    sp = self.build_agent_system_prompt(agent_name=_agent_name, snapshot=snapshot)
                    events: list[SSEEvent] = []
                    async for event in agent.run(
                        task_id=request.task_id,
                        trace_id=request.trace_id,
                        seq=0,
                        service_type=request.service_type,
                        params=_agent_params,
                        snapshot=snapshot,
                        system_prompt=sp,
                    ):
                        events.append(event)
                    return events, _agent_params

                rewrite_task = asyncio.create_task(_run_agent("query_rewrite", rewrite_params))
                retrieval_task = asyncio.create_task(_run_agent("retrieval", retrieval_params))

                rewrite_events, _rw_params = await rewrite_task
                retrieval_events, _ret_params = await retrieval_task

                for event in rewrite_events:
                    yield event.model_copy(update={"seq": seq})
                    seq += 1
                for event in retrieval_events:
                    yield event.model_copy(update={"seq": seq})
                    seq += 1

                current_params.update(_ret_params)
                current_params["rewrittenQuery"] = _rw_params.get(
                    "rewrittenQuery", current_params.get("rewrittenQuery")
                )
                current_params["keywords"] = _rw_params.get(
                    "keywords", current_params.get("keywords", [])
                )

                i += 2
                snapshot = await self.snapshot_builder.build(
                    user_id=request.user_id,
                    task_id=request.task_id,
                    conversation_id=request.conversation_id,
                    params=current_params,
                )
                continue

            # P1-1: ProfileAgent runs in background for TUTORING
            if agent_name == "profile" and request.service_type == "TUTORING":
                agent_params = copy.deepcopy(current_params)
                sp = self.build_agent_system_prompt(agent_name="profile", snapshot=snapshot)
                agent = self.agent_registry["profile"]

                async def _run_background():
                    try:
                        async for _ in agent.run(
                            task_id=request.task_id,
                            trace_id=request.trace_id,
                            seq=0,
                            service_type=request.service_type,
                            params=agent_params,
                            snapshot=snapshot,
                            system_prompt=sp,
                        ):
                            pass
                    except Exception:
                        pass

                asyncio.create_task(_run_background())
                i += 1
                continue

            agent = self.agent_registry[agent_name]
            agent_params = copy.deepcopy(current_params)
            system_prompt = self.build_agent_system_prompt(
                agent_name=agent_name,
                snapshot=snapshot,
            )
            async for event in agent.run(
                task_id=request.task_id,
                trace_id=request.trace_id,
                seq=seq,
                service_type=request.service_type,
                params=agent_params,
                snapshot=snapshot,
                system_prompt=system_prompt,
            ):
                yield event
                seq += 1
            current_params = agent_params
            snapshot = await self.snapshot_builder.build(
                user_id=request.user_id,
                task_id=request.task_id,
                conversation_id=request.conversation_id,
                params=current_params,
            )
            i += 1

        yield DoneSSEEvent(
            taskId=request.task_id,
            traceId=request.trace_id,
            seq=seq,
            payload=self._build_done_payload(
                service_type=route_plan.service_type,
                agent_names=route_plan.agent_names,
                params=current_params,
            ),
        )

    def _build_done_payload(self, *, service_type: str, agent_names: list[str], params: dict) -> DonePayload:
        generated_asset = params.get("generatedAsset")
        if service_type in {"RESOURCE_GENERATION", "VIDEO_GENERATION"} and isinstance(generated_asset, dict):
            title = str(generated_asset.get("title") or "资源")
            summary = str(generated_asset.get("summary") or "").strip()
            return DonePayload(status="SUCCESS", summary=f"{title} 生成完成：{summary}" if summary else f"{title} 生成完成")
        pushed_resources = params.get("pushedResources")
        if service_type == "RESOURCE_PUSH" and isinstance(pushed_resources, list):
            if not pushed_resources:
                return DonePayload(status="SUCCESS", summary="资源推送未命中可直接分发的现成资源")
            titles = "、".join(
                str(item.get("title") or "资源")
                for item in pushed_resources[:3]
                if isinstance(item, dict)
            )
            return DonePayload(status="SUCCESS", summary=f"资源推送完成，已匹配 {len(pushed_resources)} 个现成资源：{titles}")
        learning_path = params.get("learningPath")
        if service_type == "PATH_PLANNING" and isinstance(learning_path, dict):
            summary = str(learning_path.get("summaryText") or "").strip()
            if not summary:
                summary = f"{service_type} 路由完成，执行链路: {' -> '.join(agent_names)}"
            return DonePayload(
                status="SUCCESS",
                summary=summary,
                learningPath=learning_path,
            )
        return DonePayload(
            status="SUCCESS",
            summary=f"{service_type} 路由完成，执行链路: {' -> '.join(agent_names)}",
        )
