package com.project.api.mistake.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 错题记录，关联了原始练习项和最近一次错误提交。
 */
public record MistakeRecordResponse(
    UUID id,
    UUID practiceItemId,
    UUID lastSubmissionId,
    String questionType,
    String stem,
    List<String> options,
    Map<String, Object> standardAnswer,
    String learnerAnswer,
    Map<String, Object> judgeResult,
    BigDecimal score,
    OffsetDateTime submittedAt,
    List<String> knowledgeTags,
    String difficultyLevel,
    String mistakeType,
    String userNote,
    int wrongCount,
    int reviewCount,
    OffsetDateTime nextReviewAt,
    BigDecimal easeFactor,
    int intervalDays,
    boolean mastered,
    OffsetDateTime firstWrongAt,
    OffsetDateTime lastWrongAt,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {
}
