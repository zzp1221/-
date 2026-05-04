"""Structured models for video-generation requests and artifacts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VideoScriptSegment(BaseModel):
    """A single narration/visual segment in a teaching video script."""

    segment_id: int = Field(alias="id")
    segment_type: str = Field(alias="type")
    text: str
    duration_seconds: int = Field(alias="duration")
    visual_hint: str = Field(alias="visualHint")
    code_snippet: str | None = Field(default=None, alias="codeSnippet")

    model_config = ConfigDict(populate_by_name=True)


class VideoScriptPayload(BaseModel):
    """Structured output of the `generate_script` step."""

    title: str
    total_duration: int = Field(alias="totalDuration")
    segments: list[VideoScriptSegment]
    full_text: str = Field(alias="fullText")
    video_style: str = Field(alias="videoStyle")

    model_config = ConfigDict(populate_by_name=True)


class VideoSandboxArtifact(BaseModel):
    """Paths and metadata written to sandbox for a generated video asset."""

    task_dir: str = Field(alias="taskDir")
    script_json_path: str = Field(alias="scriptJsonPath")
    script_text_path: str = Field(alias="scriptTextPath")
    audio_path: str = Field(alias="audioPath")
    final_video_path: str = Field(alias="finalVideoPath")
    thumbnail_path: str = Field(alias="thumbnailPath")
    duration_seconds: int = Field(alias="durationSeconds")
    video_style: str = Field(alias="videoStyle")
    preview_text: str = Field(alias="previewText")
    summary_text: str = Field(alias="summaryText")

    model_config = ConfigDict(populate_by_name=True)


class VideoGenerationTaskPayload(BaseModel):
    """Serialized video-generation task metadata for DB persistence."""

    status: str
    title: str
    topic: str
    script: VideoScriptPayload
    duration_seconds: int = Field(alias="durationSeconds")
    video_style: str = Field(alias="videoStyle")
    tts_provider: str = Field(alias="ttsProvider")
    avatar_provider: str = Field(alias="avatarProvider")
    generation_params: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict,
        alias="generationParams",
    )

    model_config = ConfigDict(populate_by_name=True)
