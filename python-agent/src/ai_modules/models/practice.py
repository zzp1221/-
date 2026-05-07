"""Models for practice generation, judging, and result exchange."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PracticeQuestion(BaseModel):
    """A normalized practice question."""

    question_id: str = Field(alias="questionId")
    question_type: str = Field(alias="questionType")
    stem: str
    options: list[str] = Field(default_factory=list)
    answer: str
    knowledge_tags: list[str] = Field(default_factory=list, alias="knowledgeTags")
    difficulty_level: str = Field(alias="difficultyLevel")
    explanation: str = ""

    model_config = ConfigDict(populate_by_name=True)


class QuestionBatchPayload(BaseModel):
    """Payload for a batch of generated practice questions."""

    title: str
    topic: str
    difficulty: str
    description: str = ""
    assessment_dimension: str | None = Field(default=None, alias="assessmentDimension")
    submit_label: str | None = Field(default=None, alias="submitLabel")
    questions: list[PracticeQuestion]

    model_config = ConfigDict(populate_by_name=True)


class JudgeItemResult(BaseModel):
    """Judge result for a single practice question."""

    question_id: str = Field(alias="questionId")
    question_type: str = Field(alias="questionType")
    learner_answer: str = Field(alias="learnerAnswer")
    correct_answer: str = Field(alias="correctAnswer")
    is_correct: bool = Field(alias="isCorrect")
    score: float
    knowledge_tags: list[str] = Field(default_factory=list, alias="knowledgeTags")
    reason: str
    feedback: str
    profile_delta: dict[str, str | list[str]] = Field(default_factory=dict, alias="profileDelta")

    model_config = ConfigDict(populate_by_name=True)


class SubjectiveJudgeEvaluation(BaseModel):
    """Structured evaluation output for a subjective answer."""

    score: float
    is_correct: bool = Field(alias="isCorrect")
    reason: str
    feedback: str
    confidence_level: str = Field(alias="confidenceLevel")

    model_config = ConfigDict(populate_by_name=True)


class JudgeResultPayload(BaseModel):
    """Payload for aggregated judging output."""

    title: str
    summary: str
    total_score: float = Field(alias="totalScore")
    accuracy: float
    items: list[JudgeItemResult]

    model_config = ConfigDict(populate_by_name=True)
