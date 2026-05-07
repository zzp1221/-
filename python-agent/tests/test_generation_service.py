from pathlib import Path

import pytest

from src.ai_modules.config import get_settings
from src.ai_modules.generation import (
    ContentGenerationChain,
    GeneratedCodeAsset,
    GeneratedMindMap,
    GeneratedSection,
    GeneratedSectionBundle,
    GeneratedSlideDeck,
    GeneratedTextAsset,
    OpenAICompatibleStructuredGenerator,
    ResourceGenerationService,
)
from src.ai_modules.runtime import SystemSnapshot
from src.ai_modules.models.video import VideoScriptPayload


class FakePrimaryGenerator:
    def generate_document_sections(self, **kwargs) -> GeneratedSectionBundle:
        del kwargs
        return GeneratedSectionBundle(
            sections=[
                GeneratedSection(
                    title="一、核心概念与学习目标",
                    body="这里是百炼生成的正文。",
                    tips=["- 用自己的话复述核心概念。"],
                    citations=["- [来源1] 数据库索引导学"],
                ),
                GeneratedSection(
                    title="二、关键原理与判断方法",
                    body="这里是百炼生成的原理分析。",
                    tips=["- 先判断条件，再套用结论。"],
                    citations=["- [来源1] B+树原理"],
                ),
                GeneratedSection(
                    title="三、典型误区与辨析",
                    body="这里是百炼生成的误区辨析。",
                    tips=["- 对比相近概念的适用边界。"],
                    citations=["- [来源1] 数据库索引导学"],
                ),
                GeneratedSection(
                    title="四、练习建议与复习路径",
                    body="这里是百炼生成的练习建议。",
                    tips=["- 先做基础题，再做综合题。"],
                    citations=["- [来源1] B+树原理"],
                ),
            ]
        )

    def generate_reading_asset(self, **kwargs) -> GeneratedTextAsset:
        del kwargs
        return GeneratedTextAsset(
            title="联合索引延伸阅读",
            summary="百炼生成的延伸阅读",
            body="这里是百炼生成的阅读正文。",
        )

    def generate_slides_asset(self, **kwargs) -> GeneratedSlideDeck:
        del kwargs
        return GeneratedSlideDeck.model_validate(
            {
                "title": "联合索引PPT大纲",
                "summary": "百炼生成的PPT大纲",
                "slides": [
                    {
                        "title": "联合索引概念",
                        "bullets": ["定义", "场景"],
                        "speakerNotes": "先讲概念。",
                    }
                ],
            }
        )

    def generate_mindmap_asset(self, **kwargs) -> GeneratedMindMap:
        del kwargs
        return GeneratedMindMap.model_validate(
            {
                "title": "联合索引思维导图",
                "summary": "百炼生成的导图",
                "root": "联合索引",
                "children": [{"name": "定义", "children": [{"name": "概念"}]}],
            }
        )

    def generate_code_asset(self, **kwargs) -> GeneratedCodeAsset:
        del kwargs
        return GeneratedCodeAsset(
            title="联合索引代码案例",
            summary="百炼生成的代码案例",
            code="def explain_topic() -> str:\n    return '百炼代码案例'",
            explanation="这里是百炼生成的代码解释。",
        )

    def generate_video_script(self, **kwargs) -> VideoScriptPayload:
        del kwargs
        return VideoScriptPayload.model_validate(
            {
                "title": "联合索引教学视频",
                "totalDuration": 60,
                "segments": [
                    {
                        "id": 1,
                        "type": "intro",
                        "text": "今天我们用联合索引来理解最左前缀原则。",
                        "duration": 12,
                        "visualHint": "show_title_card",
                    },
                    {
                        "id": 2,
                        "type": "concept",
                        "text": "联合索引指把多个字段按顺序组织在一棵索引结构中，查询能否命中和字段顺序直接相关。",
                        "duration": 18,
                        "visualHint": "show_concept_explanation",
                    },
                    {
                        "id": 3,
                        "type": "case",
                        "text": "例如先按班级再按学号建立索引，按班级查询能走索引，直接只按学号过滤通常不能完整利用它。",
                        "duration": 18,
                        "visualHint": "show_case_demo",
                    },
                    {
                        "id": 4,
                        "type": "summary",
                        "text": "最后记住：设计联合索引时，先放筛选度高且常出现在条件最左侧的字段。",
                        "duration": 12,
                        "visualHint": "show_summary_card",
                    },
                ],
                "fullText": "今天我们用联合索引来理解最左前缀原则。联合索引指把多个字段按顺序组织在一棵索引结构中，查询能否命中和字段顺序直接相关。例如先按班级再按学号建立索引，按班级查询能走索引，直接只按学号过滤通常不能完整利用它。最后记住：设计联合索引时，先放筛选度高且常出现在条件最左侧的字段。",
                "videoStyle": "talking_head",
            }
        )


class FailingPrimaryGenerator:
    def generate_document_sections(self, **kwargs) -> GeneratedSectionBundle:
        del kwargs
        raise RuntimeError("simulated bailian failure")

    def generate_reading_asset(self, **kwargs) -> GeneratedTextAsset:
        del kwargs
        raise RuntimeError("simulated bailian failure")

    def generate_slides_asset(self, **kwargs) -> GeneratedSlideDeck:
        del kwargs
        raise RuntimeError("simulated bailian failure")

    def generate_mindmap_asset(self, **kwargs) -> GeneratedMindMap:
        del kwargs
        raise RuntimeError("simulated bailian failure")

    def generate_code_asset(self, **kwargs) -> GeneratedCodeAsset:
        del kwargs
        raise RuntimeError("simulated bailian failure")

    def generate_video_script(self, **kwargs) -> VideoScriptPayload:
        del kwargs
        raise RuntimeError("simulated bailian failure")


def test_generation_service_writes_document_asset(tmp_path: Path) -> None:
    service = ResourceGenerationService(
        sandbox_root=tmp_path,
        content_chain=ContentGenerationChain(primary_generator=FakePrimaryGenerator()),
    )
    snapshot = SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["B+树"],
        preferred_style="step_by_step",
        recent_mistakes=[],
        session_id="task-1",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )

    asset = service.build_asset(
        asset_type="DOCUMENT",
        params={
            "taskId": "task-doc",
            "query": "联合索引",
            "rewrittenQuery": "数据库原理 联合索引",
            "retrievalResult": {
                "documents": [
                    {"title": "数据库索引导学", "channel": "hybrid"},
                    {"title": "B+树原理", "channel": "hybrid"},
                ]
            },
        },
        snapshot=snapshot,
    )

    assert asset.asset_type == "DOCUMENT"
    assert asset.file_name == "document_guide_task-doc.md"
    assert Path(asset.local_path).exists()
    content = Path(asset.local_path).read_text(encoding="utf-8")
    assert content.startswith("# ")
    assert "## 生成大纲" in content
    assert "## 一、核心概念与学习目标" in content
    assert "### 引用依据" in content
    assert "[来源1]" in content
    assert "这里是百炼生成的正文。" in content


def test_generation_service_raises_when_primary_generator_fails(tmp_path: Path) -> None:
    service = ResourceGenerationService(
        sandbox_root=tmp_path,
        content_chain=ContentGenerationChain(primary_generator=FailingPrimaryGenerator()),
    )
    snapshot = SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["B+树"],
        preferred_style="step_by_step",
        recent_mistakes=[],
        session_id="task-1",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )

    with pytest.raises(RuntimeError):
        service.build_asset(
            asset_type="DOCUMENT",
            params={
                "taskId": "task-fallback",
                "query": "联合索引",
                "rewrittenQuery": "数据库原理 联合索引",
                "retrievalResult": {
                    "documents": [
                        {"title": "数据库索引导学", "channel": "hybrid"},
                        {"title": "B+树原理", "channel": "hybrid"},
                    ]
                },
            },
            snapshot=snapshot,
        )


def test_generation_service_writes_non_document_assets_from_llm_output(tmp_path: Path) -> None:
    service = ResourceGenerationService(
        sandbox_root=tmp_path,
        content_chain=ContentGenerationChain(primary_generator=FakePrimaryGenerator()),
    )
    snapshot = SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["B+树"],
        preferred_style="step_by_step",
        recent_mistakes=[],
        session_id="task-1",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )
    params = {
        "taskId": "task-multi",
        "query": "联合索引",
        "rewrittenQuery": "数据库原理 联合索引",
        "retrievalResult": {"documents": [{"title": "数据库索引导学", "channel": "hybrid"}]},
    }

    reading_asset = service.build_asset(asset_type="READING", params=params, snapshot=snapshot)
    slides_asset = service.build_asset(asset_type="SLIDES", params=params, snapshot=snapshot)
    mindmap_asset = service.build_asset(asset_type="MINDMAP", params=params, snapshot=snapshot)
    code_asset = service.build_asset(asset_type="CODE", params=params, snapshot=snapshot)

    assert "这里是百炼生成的阅读正文。" in Path(reading_asset.local_path).read_text(encoding="utf-8")
    assert "讲解备注: 先讲概念。" in Path(slides_asset.local_path).read_text(encoding="utf-8")
    assert mindmap_asset.display_mode == "INLINE_MERMAID"
    assert mindmap_asset.local_path is None
    assert "mindmap" in mindmap_asset.inline_content
    assert "root((联合索引))" in mindmap_asset.inline_content
    assert code_asset.display_mode == "INLINE_CODE"
    assert code_asset.local_path is None
    assert "百炼代码案例" in code_asset.inline_content


def test_generation_service_requires_tts_audio_for_video_asset(tmp_path: Path) -> None:
    class FailingMimoClient:
        def synthesize_speech_sync(self, **kwargs) -> bytes:
            raise RuntimeError("tts unavailable")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("src.ai_modules.llms.mimo_client.MiMoClient", FailingMimoClient)

    service = ResourceGenerationService(
        sandbox_root=tmp_path,
        content_chain=ContentGenerationChain(primary_generator=FakePrimaryGenerator()),
    )
    snapshot = SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["B+树"],
        preferred_style="visual",
        recent_mistakes=[],
        session_id="task-video",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )

    with pytest.raises(RuntimeError, match="Video TTS generation failed"):
        service.build_asset(
            asset_type="VIDEO",
            params={
                "taskId": "task-video",
                "query": "联合索引",
                "topic": "联合索引",
                "style": "hybrid",
                "duration": 60,
            },
            snapshot=snapshot,
        )
    monkeypatch.undo()


def test_generation_service_writes_video_asset(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeRenderer:
        def __init__(self, checkpoint_dir=None, avatar_data_dir=None) -> None:
            self.checkpoint_dir = checkpoint_dir
            self.avatar_data_dir = avatar_data_dir

        def render_talking_video(self, *, audio_path: Path, output_video_path: Path) -> None:
            assert audio_path.exists()
            output_video_path.write_bytes(b"\x00\x00\x00fake-video")

    monkeypatch.setattr("src.ai_modules.generation.video_renderer.VideoRendererService", FakeRenderer)

    service = ResourceGenerationService(sandbox_root=tmp_path)
    snapshot = SystemSnapshot(
        current_course="数据结构",
        current_chapter="快速排序",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["递归"],
        preferred_style="visual",
        recent_mistakes=[],
        session_id="task-video",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )

    params = {
        "taskId": "task-video",
        "query": "快速排序",
        "topic": "快速排序算法",
        "style": "hybrid",
        "tts_audio_bytes": b"x" * 256,
    }
    asset = service.build_asset(asset_type="VIDEO", params=params, snapshot=snapshot)

    assert asset.asset_type == "VIDEO"
    assert asset.file_name == "final.mp4"
    assert Path(asset.local_path).exists()
    assert Path(asset.local_path).read_bytes().startswith(b"\x00\x00\x00")
    assert Path(asset.thumbnail_path).exists()
    task_payload = params["videoGenerationTask"]
    assert task_payload["videoStyle"] == "hybrid"
    assert Path(params["videoSandboxArtifact"]["scriptJsonPath"]).exists()


def test_generation_service_synthesizes_video_audio_from_final_script(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeRenderer:
        def __init__(self, checkpoint_dir=None, avatar_data_dir=None) -> None:
            self.checkpoint_dir = checkpoint_dir
            self.avatar_data_dir = avatar_data_dir

        def render_talking_video(self, *, audio_path: Path, output_video_path: Path) -> None:
            assert audio_path.exists()
            output_video_path.write_bytes(b"\x00\x00\x00fake-video")

    class FakeMimoClient:
        def synthesize_speech_sync(self, **kwargs) -> bytes:
            captured["text"] = kwargs["text"]
            return b"y" * 512

    monkeypatch.setattr("src.ai_modules.generation.video_renderer.VideoRendererService", FakeRenderer)
    monkeypatch.setattr("src.ai_modules.llms.mimo_client.MiMoClient", FakeMimoClient)

    service = ResourceGenerationService(
        sandbox_root=tmp_path,
        content_chain=ContentGenerationChain(primary_generator=FakePrimaryGenerator()),
    )
    snapshot = SystemSnapshot(
        current_course="Java 程序设计",
        current_chapter="并发编程",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["线程同步"],
        preferred_style="visual",
        recent_mistakes=[],
        session_id="task-video",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )

    params = {
        "taskId": "task-video",
        "query": "并发编程",
        "topic": "并发编程",
        "style": "talking_head",
    }
    asset = service.build_asset(asset_type="VIDEO", params=params, snapshot=snapshot)

    assert asset.asset_type == "VIDEO"
    assert "回退候选" not in captured["text"]
    assert captured["text"].startswith("今天我们用联合索引来理解最左前缀原则")


def test_generation_service_rejects_unknown_asset_type(tmp_path: Path) -> None:
    service = ResourceGenerationService(sandbox_root=tmp_path)
    snapshot = SystemSnapshot(
        current_course="数据库原理",
        current_chapter="索引",
        course_progress=0.3,
        student_name="张三",
        student_level="BASIC",
        knowledge_gaps=["B+树"],
        preferred_style="step_by_step",
        recent_mistakes=[],
        session_id="task-1",
        conversation_length=1,
        total_tokens_used=0,
        wiki_pages_count=10,
        last_index_update="2026-05-02",
        recent_activities=[],
    )

    with pytest.raises(ValueError, match="Unsupported assetType"):
        service.build_asset(
            asset_type="UNKNOWN",
            params={"taskId": "task-unknown"},
            snapshot=snapshot,
        )


def test_structured_generator_uses_spark_openai_compatible_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MODEL_PROVIDER", "spark")
    monkeypatch.setenv("SPARK_API_KEY", "spark-test-key")
    monkeypatch.setenv("SPARK_BASE_URL", "https://spark-api-open.xf-yun.com/v1")
    monkeypatch.setenv("SPARK_MODEL_NAME", "generalv3.5")
    get_settings.cache_clear()

    captured: dict[str, object] = {}

    def fake_post_chat_completion(
        self,
        *,
        messages,
        temperature=0.3,
        max_tokens=None,
        response_format=None,
    ):
        captured["provider_name"] = self.provider_name
        captured["base_url"] = self.base_url
        captured["model_name"] = self.model_name
        captured["messages"] = messages
        captured["temperature"] = temperature
        captured["max_tokens"] = max_tokens
        captured["response_format"] = response_format
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"title":"星火阅读","summary":"星火摘要","body":"星火正文"}'
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 128, "completion_tokens": 32},
        }

    monkeypatch.setattr(
        OpenAICompatibleStructuredGenerator,
        "_post_chat_completion",
        fake_post_chat_completion,
    )

    generator = OpenAICompatibleStructuredGenerator()
    asset = generator.generate_reading_asset(
        title="联合索引延伸阅读",
        topic="联合索引",
        snapshot={"current_course": "数据库原理"},
        sources=[{"title": "数据库索引导学"}],
    )

    assert asset.title == "星火阅读"
    assert asset.summary == "星火摘要"
    assert asset.body == "星火正文"
    assert captured["provider_name"] == "spark"
    assert captured["base_url"] == "https://spark-api-open.xf-yun.com/v1"
    assert captured["model_name"] == "generalv3.5"
    assert captured["max_tokens"] == 1600
    assert captured["response_format"] == {"type": "json_object"}
    assert isinstance(captured["messages"], list)

    get_settings.cache_clear()
