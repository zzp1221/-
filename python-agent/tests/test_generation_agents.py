from pathlib import Path
from types import SimpleNamespace

import pytest

from src.ai_modules.agents.generation.generators import SlideGeneratorAgent
from src.ai_modules.generation.content_chain import OpenAICompatibleStructuredGenerator
from src.ai_modules.generation.resource_builder import GeneratedAsset
from src.ai_modules.runtime import SystemSnapshot


def _build_snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        current_course="Java 程序设计",
        current_chapter="并发编程",
        course_progress=0.3,
        student_name="张三",
        student_level="INTERMEDIATE",
        knowledge_gaps=["线程同步"],
        preferred_style="visual_first",
        recent_mistakes=[],
        session_id="task-generation",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )


def test_structured_generator_uses_generation_component_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_settings = SimpleNamespace(
        normalize_provider_name=lambda provider_name: provider_name,
        resolve_component_provider=lambda component_name: "mimo",
        provider_endpoint_config=lambda provider_name: SimpleNamespace(
            name=provider_name,
            base_url="https://api.xiaomimimo.com/v1",
        ),
        provider_api_key=lambda provider_name: "fake-mimo-key",
        resolve_component_model=lambda component_name, default_logical_model, provider_name: "mimo-v2.5-pro",
    )
    monkeypatch.setattr("src.ai_modules.generation.content_chain.get_settings", lambda: fake_settings)

    generator = OpenAICompatibleStructuredGenerator()

    assert generator.provider_name == "mimo"
    assert generator.base_url == "https://api.xiaomimimo.com/v1"
    assert generator.api_key == "fake-mimo-key"
    assert generator.model_name == "mimo-v2.5-pro"


@pytest.mark.asyncio
async def test_expand_content_uses_preview_text_for_binary_assets(tmp_path: Path) -> None:
    pptx_path = tmp_path / "slides.pptx"
    pptx_path.write_bytes(b"PK\x03\x04binary-pptx")

    class FakeGenerationService:
        def build_asset(self, *, asset_type, params, snapshot):
            del asset_type, params, snapshot
            return GeneratedAsset(
                assetType="SLIDES",
                title="并发编程PPT大纲",
                summary="PPT 生成成功",
                displayMode="DOWNLOAD_CARD",
                fileName="slides.pptx",
                localPath=str(pptx_path),
                previewText="PPT 演示文稿 · 6 页 · 并发编程",
                mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )

    agent = SlideGeneratorAgent(generation_service=FakeGenerationService())

    result = await agent._tool_expand_content(
        tool_input={},
        task_id="task-slides",
        params={"query": "并发编程"},
        snapshot=_build_snapshot(),
    )

    assert result["generatedContent"] == "PPT 演示文稿 · 6 页 · 并发编程"
    assert result["asset"]["assetType"] == "SLIDES"
