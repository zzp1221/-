"""Models for learner profile extraction and persistence."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WeakPointDetail(BaseModel):
    """A ranked weak-point item with severity and evidence."""

    topic: str
    severity: float = 0.6
    last_error: str = Field(default="", alias="lastError")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class ErrorPattern(BaseModel):
    """A recurring learner error pattern."""

    pattern: str
    frequency: float = 0.5
    examples: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class LearningHabitsProfile(BaseModel):
    """Learning-habit signals extracted from conversation and behavior."""

    study_frequency: str = Field(default="", alias="studyFrequency")
    preferred_time: str = Field(default="", alias="preferredTime")
    avg_session_duration: int = Field(default=0, alias="avgSessionDuration")
    note_taking: bool = Field(default=False, alias="noteTaking")
    self_testing: bool = Field(default=False, alias="selfTesting")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class CurrentGoalProfile(BaseModel):
    """Current short/mid-term learner goals."""

    short_term: str = Field(default="", alias="shortTerm")
    mid_term: str = Field(default="", alias="midTerm")
    context: str = ""
    urgency: str = "MEDIUM"

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class LearnerProfileDimensions(BaseModel):
    """Structured learner profile dimensions extracted from dialogue or practice."""

    knowledge_foundation: str = Field(default="UNKNOWN", alias="knowledgeFoundation")
    learning_goal: str = Field(default="", alias="learningGoal")
    professional_background: str = Field(default="", alias="professionalBackground")
    learning_preference: str = Field(default="", alias="learningPreference")
    cognitive_style: str = Field(default="mixed", alias="cognitiveStyle")
    weak_points: list[str] = Field(default_factory=list, alias="weakPoints")
    learning_pace: str = Field(default="normal", alias="learningPace")
    confidence_level: str = Field(default="UNKNOWN", alias="confidenceLevel")
    confidence_score: float = Field(default=0.65, alias="confidenceScore")
    skill_mastery: dict[str, float] = Field(default_factory=dict, alias="skillMastery")
    weak_point_details: list[WeakPointDetail] = Field(default_factory=list, alias="weakPointDetails")
    learning_habits: LearningHabitsProfile = Field(
        default_factory=LearningHabitsProfile,
        alias="learningHabits",
    )
    error_patterns: list[ErrorPattern] = Field(default_factory=list, alias="errorPatterns")
    current_goal: CurrentGoalProfile = Field(default_factory=CurrentGoalProfile, alias="currentGoal")
    preferred_resource_types: list[str] = Field(default_factory=list, alias="preferredResourceTypes")
    explanation_preference: str = Field(default="", alias="explanationPreference")
    inferred_recommendations: list[str] = Field(default_factory=list, alias="inferredRecommendations")
    evidence: list[str] = Field(default_factory=list)
    source: str = "CONVERSATION"
    summary_text: str = Field(default="", alias="summaryText")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class LearnerProfileSnapshot(BaseModel):
    """Current learner profile snapshot."""

    user_id: str = Field(alias="userId")
    version: int
    profile: LearnerProfileDimensions

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
