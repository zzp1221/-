"""Supervisor that resolves routes and streams agent execution results."""

from __future__ import annotations

import asyncio
import copy
import json
import logging
from collections.abc import AsyncIterator, Container
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.ai_modules.agents import (
    CodeGeneratorAgent,
    DeepReasoningAgent,
    DocumentGeneratorAgent,
    EvaluationAgent,
    ImageAnalysisAgent,
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

LOGGER = logging.getLogger(__name__)


class RoutePlan(BaseModel):
    """Resolved service route plan."""

    service_type: str = Field(alias="serviceType")
    agent_names: list[str] = Field(alias="agentNames")

    model_config = ConfigDict(populate_by_name=True)


class PythonAgentSupervisor:
    """Resolve service routes and execute agents sequentially."""

    def __init__(self) -> None:
        self.snapshot_builder = SnapshotBuilder()
        self._background_tasks: set[asyncio.Task[None]] = set()
        self.agent_registry = {
            "query_rewrite": QueryRewriteAgent(),
            "retrieval": RetrievalAgent(),
            "document_generator": DocumentGeneratorAgent(),
            "slide_generator": SlideGeneratorAgent(),
            "reading_generator": ReadingGeneratorAgent(),
            "mindmap_generator": MindMapGeneratorAgent(),
            "code_generator": CodeGeneratorAgent(),
            "video_generator": VideoGenerationAgent(),
            "deep_reasoning": DeepReasoningAgent(),
            "tutor": TutorAgent(),
            "profile": ProfileAgent(),
            "practice": PracticeAgent(),
            "judge": JudgeAgent(),
            "path_planning": PathPlanningAgent(),
            "evaluation": EvaluationAgent(),
            "image_analysis": ImageAnalysisAgent(),
            "resource_push": ResourcePushAgent(),
        }
        self.route_templates = self._load_route_templates()

    def resolve_route(self, service_type: str, params: dict) -> RoutePlan:
        requested_resource_type = self._resolve_resource_type(params)
        generation_agent = {
            "DOCUMENT": "document_generator",
            "SLIDES": "slide_generator",
            "READING": "reading_generator",
            "MINDMAP": "mindmap_generator",
            "CODE": "code_generator",
            "QUIZ": "practice",
            "VIDEO": "video_generator",
        }.get(requested_resource_type, "document_generator")

        route_template = self.route_templates.get(service_type)
        if route_template is None:
            raise ValueError(f"Unsupported serviceType: {service_type}")
        if service_type == "TUTORING" and self._is_deep_reasoning(params):
            route_template = [
                "query_rewrite",
                "retrieval",
                "image_analysis",
                "deep_reasoning",
                "profile",
            ]
        resolved_route = [
            generation_agent if agent_name == "{generation_agent}" else agent_name
            for agent_name in route_template
        ]

        return RoutePlan(
            serviceType=service_type,
            agentNames=resolved_route,
        )

    def _load_route_templates(self) -> dict[str, list[str]]:
        config_path = Path(__file__).with_name("supervisor_routes.json")
        with config_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        route_templates: dict[str, list[str]] = {}
        for service_type, agent_names in loaded.items():
            if not isinstance(service_type, str) or not isinstance(agent_names, list):
                continue
            route_templates[service_type.strip().upper()] = [str(agent_name) for agent_name in agent_names]
        return route_templates

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
            "QUIZ": "QUIZ",
        }.get(normalized, normalized)

    def _is_deep_reasoning(self, params: dict) -> bool:
        reasoning_mode = params.get("reasoningMode")
        if isinstance(reasoning_mode, str) and reasoning_mode.strip().upper() == "DEEP":
            return True
        return bool(params.get("deepReasoning"))

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

    async def stream(self, request: EngineStreamRequest, cancelled: Container[str] | None = None) -> AsyncIterator[SSEEvent]:
        route_plan = self.resolve_route(request.service_type, request.params)
        snapshot = await self.build_snapshot(request)
        current_params = self._seed_request_params(request)
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

            # Retrieval must consume rewritten query/keywords, otherwise high-precision wiki matches are lost.
            if (
                agent_name == "query_rewrite"
                and i + 1 < len(agent_names)
                and agent_names[i + 1] == "retrieval"
            ):
                rewrite_agent = self.agent_registry["query_rewrite"]
                rewrite_prompt = self.build_agent_system_prompt(agent_name="query_rewrite", snapshot=snapshot)
                rewrite_params = copy.deepcopy(current_params)

                async for event in rewrite_agent.run(
                    task_id=request.task_id,
                    trace_id=request.trace_id,
                    seq=0,
                    service_type=request.service_type,
                    params=rewrite_params,
                    snapshot=snapshot,
                    system_prompt=rewrite_prompt,
                ):
                    yield event.model_copy(update={"seq": seq})
                    seq += 1

                current_params.update(rewrite_params)
                snapshot = await self.snapshot_builder.build(
                    user_id=request.user_id,
                    task_id=request.task_id,
                    conversation_id=request.conversation_id,
                    params=current_params,
                )

                retrieval_agent = self.agent_registry["retrieval"]
                retrieval_prompt = self.build_agent_system_prompt(agent_name="retrieval", snapshot=snapshot)
                retrieval_params = copy.deepcopy(current_params)

                async for event in retrieval_agent.run(
                    task_id=request.task_id,
                    trace_id=request.trace_id,
                    seq=0,
                    service_type=request.service_type,
                    params=retrieval_params,
                    snapshot=snapshot,
                    system_prompt=retrieval_prompt,
                ):
                    yield event.model_copy(update={"seq": seq})
                    seq += 1

                current_params.update(retrieval_params)

                i += 2
                snapshot = await self.snapshot_builder.build(
                    user_id=request.user_id,
                    task_id=request.task_id,
                    conversation_id=request.conversation_id,
                    params=current_params,
                )
                continue

            agent = self.agent_registry[agent_name]
            agent_params = copy.deepcopy(current_params)
            system_prompt = self.build_agent_system_prompt(
                agent_name=agent_name,
                snapshot=snapshot,
            )
            if self._should_run_profile_in_background(
                service_type=route_plan.service_type,
                agent_name=agent_name,
            ):
                self._schedule_background_agent(
                    agent=agent,
                    agent_name=agent_name,
                    task_id=request.task_id,
                    trace_id=request.trace_id,
                    service_type=request.service_type,
                    params=agent_params,
                    snapshot=snapshot,
                    system_prompt=system_prompt,
                )
                i += 1
                continue
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

    def _seed_request_params(self, request: EngineStreamRequest) -> dict:
        seeded_params = copy.deepcopy(request.params)
        if request.user_id and not seeded_params.get("userId"):
            seeded_params["userId"] = request.user_id
        if request.conversation_id and not seeded_params.get("conversationId"):
            seeded_params["conversationId"] = request.conversation_id
        return seeded_params

    def _should_run_profile_in_background(self, *, service_type: str, agent_name: str) -> bool:
        return service_type == "TUTORING" and agent_name == "profile"

    def _schedule_background_agent(
        self,
        *,
        agent: Any,
        agent_name: str,
        task_id: str,
        trace_id: str,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> None:
        task = asyncio.create_task(
            self._drain_background_agent(
                agent=agent,
                agent_name=agent_name,
                task_id=task_id,
                trace_id=trace_id,
                service_type=service_type,
                params=params,
                snapshot=snapshot,
                system_prompt=system_prompt,
            ),
            name=f"background-{agent_name}:{task_id}",
        )
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _drain_background_agent(
        self,
        *,
        agent: Any,
        agent_name: str,
        task_id: str,
        trace_id: str,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> None:
        try:
            async for _ in agent.run(
                task_id=task_id,
                trace_id=trace_id,
                seq=1,
                service_type=service_type,
                params=params,
                snapshot=snapshot,
                system_prompt=system_prompt,
            ):
                pass
        except asyncio.CancelledError:
            raise
        except Exception:
            LOGGER.exception("后台画像构建失败，已与 Tutor 主链路隔离: task_id=%s agent=%s", task_id, agent_name)
