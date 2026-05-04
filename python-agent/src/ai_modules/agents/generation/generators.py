"""Generation agents that write deterministic assets into sandbox storage."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
import logging
from pathlib import Path
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.agents.common_agents import CriticAgent, SafetyAgent
from src.ai_modules.config import get_settings
from src.ai_modules.generation import ResourceGenerationService
from src.ai_modules.llms import GenerationToolLLMClientFactory
from src.ai_modules.models import (
    DonePayload,
    DoneSSEEvent,
    ResourceFilePayload,
    ResourceFileSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
    ProgressPayload,
    ProgressSSEEvent,
)
from src.ai_modules.runtime import (
    AgentCoreLoop,
    PermissionLevel,
    RecoveryEngine,
    RecoveryFailureType,
    SystemSnapshot,
    ToolRegistry,
)

LOGGER = logging.getLogger(__name__)


class _BaseGenerationAgent(PlaceholderAgent):
    def __init__(
        self,
        agent_name: str,
        stage_name: str,
        asset_type: str,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
        heartbeat_interval_seconds: float = 15.0,
    ) -> None:
        super().__init__(agent_name, stage_name, emits_result_chunk=True)
        self.asset_type = asset_type
        self.generation_service = generation_service or ResourceGenerationService()
        self.llm_client = llm_client or GenerationToolLLMClientFactory.create()
        self.critic_agent = critic_agent or CriticAgent()
        self.safety_agent = safety_agent or SafetyAgent()
        self.recovery_engine = RecoveryEngine()
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    async def run(
        self,
        *,
        task_id: str,
        trace_id: str,
        seq: int,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> AsyncIterator[SSEEvent]:
        del service_type
        next_seq = seq
        final_output_task = asyncio.create_task(
            self._run_agent_core_loop(
                task_id=task_id,
                params=params,
                snapshot=snapshot,
                system_prompt=system_prompt,
            )
        )
        while not final_output_task.done():
            try:
                final_output = await asyncio.wait_for(
                    asyncio.shield(final_output_task),
                    timeout=self.heartbeat_interval_seconds,
                )
                break
            except TimeoutError:
                yield ProgressSSEEvent(
                    taskId=task_id,
                    traceId=trace_id,
                    seq=next_seq,
                    payload=ProgressPayload(
                        stage=self.stage_name,
                        percent=70,
                        message="资源生成仍在执行中，请稍候",
                    ),
                )
                next_seq += 1
        else:
            final_output = await final_output_task

        final_output = final_output if "final_output" in locals() else await final_output_task
        asset = final_output["asset"]
        critic_review = final_output["criticReview"]
        safety_review = final_output["safetyReview"]

        if not safety_review.allowed:
            yield ResultChunkSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=next_seq,
                payload=ResultChunkPayload(text=safety_review.summary_text),
            )
            yield DoneSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=next_seq + 1,
                payload=DonePayload(status="FAILED", summary=safety_review.summary_text),
            )
            return

        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq,
            payload=ResultChunkPayload(
                text=(
                    f"{self.agent_name} 已生成 {asset.asset_type} 资源；"
                    f"预览: {asset.preview_text}；"
                    f"Critic: {critic_review.summary_text}；"
                    f"Safety: {safety_review.summary_text}"
                )
            ),
        )
        yield ResourceFileSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq + 1,
            payload=ResourceFilePayload(
                assetType=asset.asset_type,
                title=asset.title,
                summary=asset.summary,
                displayMode=asset.display_mode,
                fileName=asset.file_name,
                localPath=asset.local_path,
                mimeType=asset.mime_type,
                thumbnailPath=asset.thumbnail_path,
                thumbnailFileName=asset.thumbnail_file_name,
                thumbnailMimeType=asset.thumbnail_mime_type,
                durationSeconds=asset.duration_seconds,
                videoStyle=asset.video_style,
                knowledgePoint=asset.knowledge_point,
            ),
        )

    async def _run_agent_core_loop(
        self,
        *,
        task_id: str,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> dict[str, Any]:
        tool_registry = ToolRegistry()
        tool_registry.register(
            name="generate_outline",
            fn=lambda tool_input: self._tool_generate_outline(
                tool_input=tool_input,
                params=params,
                snapshot=snapshot,
            ),
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Plan the generation outline before expanding content.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="expand_content",
            fn=lambda tool_input: self._tool_expand_content(
                tool_input=tool_input,
                task_id=task_id,
                params=params,
                snapshot=snapshot,
            ),
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Expand the planned outline into a draft asset.",
            parameters={"type": "object", "properties": {}, "additionalProperties": True},
        )
        tool_registry.register(
            name="review_content",
            fn=lambda tool_input: self._tool_review_content(
                tool_input=tool_input,
                params=params,
                snapshot=snapshot,
            ),
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Review the draft content and collect critic feedback.",
            parameters={"type": "object", "properties": {}, "additionalProperties": True},
        )
        tool_registry.register(
            name="format_output",
            fn=lambda tool_input: self._tool_format_output(
                tool_input=tool_input,
                params=params,
                snapshot=snapshot,
            ),
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Finalize the generated asset after safety review.",
            parameters={"type": "object", "properties": {}, "additionalProperties": True},
        )
        try:
            result = await AgentCoreLoop(
                llm_client=self.llm_client,
                tool_registry=tool_registry,
                recovery_engine=self.recovery_engine,
                max_iterations=6,
                agent_level=PermissionLevel.CONTENT_GENERATE,
            ).run(
                system_prompt=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "请按大纲规划、内容扩展、内容复核、格式输出的顺序完成资源生成。",
                    }
                ],
            )
            final_output = result.tool_results[-1].output if result.tool_results else {}
            if isinstance(final_output, dict) and final_output.get("asset"):
                return self._normalize_final_output(final_output)
        except Exception:
            LOGGER.warning(
                "Tool-driven generation failed, falling back to deterministic pipeline.",
                exc_info=True,
            )

        outline = self._tool_generate_outline(tool_input={}, params=params, snapshot=snapshot)
        draft = await self._tool_expand_content(
            tool_input=outline,
            task_id=task_id,
            params=params,
            snapshot=snapshot,
        )
        reviewed = await self._tool_review_content(
            tool_input=draft,
            params=params,
            snapshot=snapshot,
        )
        return self._normalize_final_output(
            await self._tool_format_output(
                tool_input=reviewed,
                params=params,
                snapshot=snapshot,
            )
        )

    def _tool_generate_outline(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        del tool_input
        topic = str(params.get("rewrittenQuery") or params.get("query") or "主题")
        sources = (params.get("retrievalResult") or {}).get("documents", [])
        if self.asset_type == "DOCUMENT":
            outline = {
                "assetType": self.asset_type,
                "topic": topic,
                "sections": [
                    section.model_dump(by_alias=True)
                    for section in self.generation_service._plan_document_sections(
                        params=params,
                        snapshot=snapshot,
                        sources=sources,
                    )
                ],
            }
        else:
            outline = {
                "assetType": self.asset_type,
                "topic": topic,
                "sections": [
                    {"title": "学习目标", "objective": f"围绕 {topic} 建立概念框架"},
                    {"title": "核心内容", "objective": "扩展关键原理和例子"},
                    {"title": "复盘建议", "objective": "输出练习与复习建议"},
                ],
            }
        params["generationOutline"] = outline
        return outline

    async def _tool_expand_content(
        self,
        *,
        tool_input: dict[str, Any],
        task_id: str,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        del tool_input
        build_params = dict(params)
        build_params.setdefault("taskId", task_id)

        async def operation() -> dict[str, Any]:
            asset = await asyncio.to_thread(
                self.generation_service.build_asset,
                asset_type=self.asset_type,
                params=build_params,
                snapshot=snapshot,
            )
            generated_content = (
                asset.preview_text
                if asset.asset_type == "VIDEO"
                else Path(asset.local_path).read_text(encoding="utf-8")
            )
            return {
                "asset": asset.model_dump(by_alias=True),
                "generatedContent": generated_content,
            }

        async def fallback_operation() -> dict[str, Any]:
            asset = await self._build_minimal_asset(task_id=task_id, params=params)
            generated_content = Path(asset.local_path).read_text(encoding="utf-8")
            payload = {
                "asset": asset.model_dump(by_alias=True),
                "generatedContent": generated_content,
                "degraded": True,
            }
            await self.recovery_engine.recover_content_generation_failed(
                asset_type=self.asset_type,
                fallback_payload=payload,
            )
            return payload

        draft = await self.recovery_engine.call_with_recovery(
            failure_type=RecoveryFailureType.CONTENT_GENERATION_FAILED,
            operation=operation,
            fallback_operation=fallback_operation,
        )
        params["generatedAsset"] = draft["asset"]
        params["generatedContent"] = draft["generatedContent"]
        return draft

    async def _tool_review_content(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        if isinstance(tool_input, dict):
            params["generatedAsset"] = tool_input.get("asset", params.get("generatedAsset", {}))
            params["generatedContent"] = tool_input.get(
                "generatedContent",
                params.get("generatedContent", ""),
            )
        critic_review = await self.critic_agent.review_content(
            params=params,
            snapshot=snapshot,
            system_prompt=self.critic_agent.system_prompt(snapshot),
        )
        params["criticReview"] = critic_review.model_dump(by_alias=True)
        return {
            "asset": params["generatedAsset"],
            "generatedContent": params["generatedContent"],
            "criticReview": params["criticReview"],
        }

    async def _tool_format_output(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        if isinstance(tool_input, dict):
            params["generatedAsset"] = tool_input.get("asset", params.get("generatedAsset", {}))
            params["generatedContent"] = tool_input.get(
                "generatedContent",
                params.get("generatedContent", ""),
            )
            if tool_input.get("criticReview"):
                params["criticReview"] = tool_input["criticReview"]
        safety_review = await self.safety_agent.review_content(
            params=params,
            snapshot=snapshot,
            system_prompt=self.safety_agent.system_prompt(snapshot),
        )
        params["safetyReview"] = safety_review.model_dump(by_alias=True)
        return {
            "asset": params["generatedAsset"],
            "criticReview": params["criticReview"],
            "safetyReview": params["safetyReview"],
        }

    def _normalize_final_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        from src.ai_modules.generation import GeneratedAsset
        from src.ai_modules.models import CriticReviewPayload, SafetyReviewPayload

        return {
            "asset": GeneratedAsset.model_validate(payload["asset"]),
            "criticReview": CriticReviewPayload.model_validate(payload["criticReview"]),
            "safetyReview": SafetyReviewPayload.model_validate(payload["safetyReview"]),
        }

    async def _build_minimal_asset(
        self,
        *,
        task_id: str,
        params: dict[str, Any],
    ):
        from src.ai_modules.generation import GeneratedAsset

        title = f"{params.get('query', '学习主题')}{self.asset_type}回退资源"
        file_name = self.generation_service._scoped_file_name(
            f"{self.asset_type.lower()}_fallback",
            "md",
            {"taskId": task_id},
        )
        content = f"# {title}\n\n当前进入简化生成模式，请稍后重试。\n"
        path = await asyncio.to_thread(self.generation_service._write_text, file_name, content)
        return GeneratedAsset(
            assetType=self.asset_type,
            title=title,
            summary="回退生成资源",
            displayMode="MARKDOWN_CARD",
            fileName=file_name,
            localPath=str(path),
            previewText=title,
        )


class DocumentGeneratorAgent(_BaseGenerationAgent):
    def __init__(
        self,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
    ) -> None:
        super().__init__(
            "Document Generator Agent",
            "document_generation",
            "DOCUMENT",
            generation_service=generation_service,
            llm_client=llm_client,
            critic_agent=critic_agent,
            safety_agent=safety_agent,
        )


class MindMapGeneratorAgent(_BaseGenerationAgent):
    def __init__(
        self,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
    ) -> None:
        super().__init__(
            "MindMap Generator Agent",
            "mindmap_generation",
            "MINDMAP",
            generation_service=generation_service,
            llm_client=llm_client,
            critic_agent=critic_agent,
            safety_agent=safety_agent,
        )


class SlideGeneratorAgent(_BaseGenerationAgent):
    def __init__(
        self,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
    ) -> None:
        super().__init__(
            "Slide Generator Agent",
            "slide_generation",
            "SLIDES",
            generation_service=generation_service,
            llm_client=llm_client,
            critic_agent=critic_agent,
            safety_agent=safety_agent,
        )


class ReadingGeneratorAgent(_BaseGenerationAgent):
    def __init__(
        self,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
    ) -> None:
        super().__init__(
            "Reading Generator Agent",
            "reading_generation",
            "READING",
            generation_service=generation_service,
            llm_client=llm_client,
            critic_agent=critic_agent,
            safety_agent=safety_agent,
        )


class CodeGeneratorAgent(_BaseGenerationAgent):
    def __init__(
        self,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
    ) -> None:
        super().__init__(
            "Code Generator Agent",
            "code_generation",
            "CODE",
            generation_service=generation_service,
            llm_client=llm_client,
            critic_agent=critic_agent,
            safety_agent=safety_agent,
        )


class VideoGenerationAgent(_BaseGenerationAgent):
    def __init__(
        self,
        generation_service: ResourceGenerationService | None = None,
        llm_client: Any | None = None,
        critic_agent: CriticAgent | None = None,
        safety_agent: SafetyAgent | None = None,
    ) -> None:
        super().__init__(
            "Video Generator Agent",
            "video_generation",
            "VIDEO",
            generation_service=generation_service,
            llm_client=llm_client,
            critic_agent=critic_agent,
            safety_agent=safety_agent,
        )

    async def run(
        self,
        *,
        task_id: str,
        trace_id: str,
        seq: int,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> AsyncIterator[SSEEvent]:
        topic = str(params.get("topic") or params.get("query") or "教学主题")
        stage_events = [
            ("video_started", 10, f"{topic} 视频生成任务已启动"),
            ("script_generated", 25, "脚本生成完成"),
            ("speech_synthesized", 50, "语音合成完成"),
            ("video_rendering", 75, "视频渲染中..."),
        ]
        current_seq = seq
        for stage_name, percent, message in stage_events:
            yield ProgressSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=current_seq,
                payload=ProgressPayload(stage=stage_name, percent=percent, message=message),
            )
            current_seq += 1

        final_output_task = asyncio.create_task(
            self._run_agent_core_loop(
                task_id=task_id,
                params=params,
                snapshot=snapshot,
                system_prompt=system_prompt,
            )
        )
        while not final_output_task.done():
            try:
                final_output = await asyncio.wait_for(
                    asyncio.shield(final_output_task),
                    timeout=self.heartbeat_interval_seconds,
                )
                break
            except TimeoutError:
                yield ProgressSSEEvent(
                    taskId=task_id,
                    traceId=trace_id,
                    seq=current_seq,
                    payload=ProgressPayload(
                        stage=self.stage_name,
                        percent=85,
                        message="视频资源仍在生成中，请稍候",
                    ),
                )
                current_seq += 1
        else:
            final_output = await final_output_task

        final_output = final_output if "final_output" in locals() else await final_output_task
        asset = final_output["asset"]
        critic_review = final_output["criticReview"]
        safety_review = final_output["safetyReview"]

        if not safety_review.allowed:
            yield ResultChunkSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=current_seq,
                payload=ResultChunkPayload(text=safety_review.summary_text),
            )
            yield DoneSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=current_seq + 1,
                payload=DonePayload(status="FAILED", summary=safety_review.summary_text),
            )
            return

        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=current_seq,
            payload=ResultChunkPayload(
                text=(
                    f"{self.agent_name} 已生成教学视频；"
                    f"预览: {asset.preview_text}；"
                    f"Critic: {critic_review.summary_text}；"
                    f"Safety: {safety_review.summary_text}"
                )
            ),
        )
        current_seq += 1
        yield ResourceFileSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=current_seq,
            payload=ResourceFilePayload(
                assetType=asset.asset_type,
                title=asset.title,
                summary=asset.summary,
                displayMode=asset.display_mode,
                fileName=asset.file_name,
                localPath=asset.local_path,
                mimeType=asset.mime_type,
                thumbnailPath=asset.thumbnail_path,
                thumbnailFileName=asset.thumbnail_file_name,
                thumbnailMimeType=asset.thumbnail_mime_type,
                durationSeconds=asset.duration_seconds,
                videoStyle=asset.video_style,
                knowledgePoint=asset.knowledge_point,
            ),
        )
        current_seq += 1
        settings = get_settings()
        video_task_payload = params.get("videoGenerationTask")
        video_artifact_payload = params.get("videoSandboxArtifact")
        complete_payload: dict[str, Any] = {
            "topic": topic,
            "stage": "completed",
            "progress": 100,
            "message": "视频生成完成",
            "title": asset.title,
            "duration": asset.duration_seconds,
            "durationSeconds": asset.duration_seconds,
            "style": asset.video_style,
            "videoStyle": asset.video_style,
            "knowledgePoint": asset.knowledge_point,
            "activeProvider": settings.runtime_provider_name(),
            "fallbackProvider": settings.selected_fallback_provider_name(),
            "finalVideoPath": asset.local_path,
            "thumbnailPath": asset.thumbnail_path,
            "criticScore": 1.0 if critic_review.verdict == "PASS" else 0.5,
            "safetyPassed": safety_review.allowed,
        }
        if isinstance(video_task_payload, dict):
            complete_payload["videoGenerationTask"] = video_task_payload
            complete_payload["ttsProvider"] = video_task_payload.get("ttsProvider")
            complete_payload["avatarProvider"] = video_task_payload.get("avatarProvider")
            complete_payload["generationParams"] = video_task_payload.get("generationParams")
            script_payload = video_task_payload.get("script")
            if isinstance(script_payload, dict):
                complete_payload["scriptJson"] = script_payload
                complete_payload["scriptText"] = script_payload.get("fullText")
        if isinstance(video_artifact_payload, dict):
            complete_payload["videoSandboxArtifact"] = video_artifact_payload
            complete_payload["audioPath"] = video_artifact_payload.get("audioPath")
            complete_payload["finalVideoPath"] = video_artifact_payload.get("finalVideoPath", asset.local_path)
            complete_payload["thumbnailPath"] = video_artifact_payload.get("thumbnailPath", asset.thumbnail_path)
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=current_seq,
            payload=ResultChunkPayload(
                text=(
                    f"视频生成完成：主题={complete_payload['topic']}，"
                    f"时长={complete_payload.get('durationSeconds') or '未知'}秒，"
                    f"风格={complete_payload.get('videoStyle') or '默认'}。"
                )
            ),
        )
