"""Analyze uploaded learning images with MiMo-V2-Omni and summarize key content."""

from __future__ import annotations

import base64
import os
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms.mimo_client import MiMoClient
from src.ai_modules.models import ProgressPayload, ProgressSSEEvent, SSEEvent
from src.ai_modules.runtime import SystemSnapshot


class ImageAnalysisAgent(PlaceholderAgent):
    """Extract learning-relevant information from uploaded images."""

    MAX_IMAGE_BYTES = 10 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

    def __init__(self, mimo_client: MiMoClient | None = None) -> None:
        super().__init__("Image Analysis Agent", "image_analysis")
        self.mimo_client = mimo_client or MiMoClient(timeout_seconds=20.0)
        self.control_plane_base_url = os.getenv("CONTROL_PLANE_BASE_URL", "http://app:8081").rstrip("/")

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
        del service_type, snapshot, system_prompt
        image_urls = self._normalize_image_urls(params.get("imageUrls"))
        if not image_urls:
            return

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=15,
                message=f"已接收 {len(image_urls)} 张图片，开始解析图片内容",
            ),
        )

        analysis_result = await self._analyze_images(
            user_query=str(params.get("query") or params.get("message") or "").strip(),
            image_urls=image_urls,
        )
        params["imageAnalysisResult"] = analysis_result
        params["imageAnalysisSummary"] = str(analysis_result.get("summary") or "").strip()

    def _normalize_image_urls(self, raw_value: Any) -> list[str]:
        if not isinstance(raw_value, list):
            return []
        return [str(item).strip() for item in raw_value if str(item).strip()]

    async def _analyze_images(self, *, user_query: str, image_urls: list[str]) -> dict[str, Any]:
        prompt = (
            "你是学习场景图片理解助手。请提取图片中的题目文字、代码报错、教材知识点、公式、图表含义，"
            "识别关键信息后给出结构化结论。若图中信息不足，请明确指出缺失点。"
        )
        if user_query:
            prompt += f"\n学生补充问题：{user_query}"
        try:
            model_image_urls = await self._prepare_image_inputs(image_urls)
        except Exception as exc:
            return {
                "summary": self._friendly_error_message(exc),
                "imageUrls": image_urls,
                "status": "FAILED",
            }
        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请分析这些学习相关图片，并总结可用于答疑的有效信息。"},
                    *[
                        {"type": "image_url", "image_url": {"url": image_url}}
                        for image_url in model_image_urls
                    ],
                ],
            },
        ]
        try:
            response = await self.mimo_client.omni_chat(messages=messages, temperature=0.1, max_tokens=1600)
            content = self.mimo_client.extract_content(response).strip()
            if not content:
                raise RuntimeError("模型未返回可用的图片识别结果")
            return {
                "summary": content,
                "imageUrls": image_urls,
                "status": "SUCCESS",
            }
        except Exception as exc:
            return {
                "summary": self._friendly_error_message(exc),
                "imageUrls": image_urls,
                "status": "FAILED",
            }

    async def _prepare_image_inputs(self, image_urls: list[str]) -> list[str]:
        prepared: list[str] = []
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for image_url in image_urls:
                absolute_url = self._resolve_image_url(image_url)
                response = await client.get(absolute_url)
                response.raise_for_status()
                content_type = self._normalize_content_type(response.headers.get("content-type"), absolute_url)
                if content_type not in self.ALLOWED_CONTENT_TYPES:
                    raise RuntimeError("仅支持 jpg、png、webp 图片提问")
                content = response.content
                if len(content) > self.MAX_IMAGE_BYTES:
                    raise RuntimeError("图片不能超过 10MB，请压缩后再试")
                encoded = base64.b64encode(content).decode("ascii")
                prepared.append(f"data:{content_type};base64,{encoded}")
        return prepared

    def _resolve_image_url(self, image_url: str) -> str:
        parsed = urlparse(image_url)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            return image_url
        if image_url.startswith("/"):
            return urljoin(self.control_plane_base_url + "/", image_url.lstrip("/"))
        raise RuntimeError("图片链接无效，请重新上传后再试")

    def _normalize_content_type(self, raw_content_type: str | None, image_url: str) -> str:
        normalized = (raw_content_type or "").split(";", 1)[0].strip().lower()
        if normalized in self.ALLOWED_CONTENT_TYPES:
            return normalized
        lower_path = urlparse(image_url).path.lower()
        if lower_path.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        if lower_path.endswith(".png"):
            return "image/png"
        if lower_path.endswith(".webp"):
            return "image/webp"
        return normalized

    def _friendly_error_message(self, exc: Exception) -> str:
        message = str(exc).lower()
        if "timeout" in message:
            return "图片分析超时了，请稍后重试，或减少单次上传图片数量。"
        if "404" in message or "not found" in message:
            return "图片加载失败，请重新上传清晰图片后再试。"
        if "10mb" in message:
            return "图片不能超过 10MB，请压缩后再试。"
        if "链接无效" in str(exc):
            return "图片链接无效，请重新上传后再试。"
        return "图片内容识别失败，请确认图片清晰、格式正确后重试。"
