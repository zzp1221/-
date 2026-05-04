"""Models for learner profile extraction and persistence."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LearnerProfileDimensions(BaseModel):
    """Structured learner profile dimensions extracted from dialogue or practice."""

    knowledge_foundation: str = Field(alias="knowledgeFoundation")
    learning_goal: str = Field(alias="learningGoal")
    professional_background: str = Field(alias="professionalBackground")
    learning_preference: str = Field(alias="learningPreference")
    cognitive_style: str = Field(alias="cognitiveStyle")
    weak_points: list[str] = Field(default_factory=list, alias="weakPoints")
    learning_pace: str = Field(alias="learningPace")
    confidence_level: str = Field(alias="confidenceLevel")
    source: str
    summary_text: str = Field(alias="summaryText")

    model_config = ConfigDict(populate_by_name=True)


class LearnerProfileSnapshot(BaseModel):
    """Current learner profile snapshot."""

    user_id: str = Field(alias="userId")
    version: int
    profile: LearnerProfileDimensions

    model_config = ConfigDict(populate_by_name=True)
