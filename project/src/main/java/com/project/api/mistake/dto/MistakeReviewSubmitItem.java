package com.project.api.mistake.dto;

import java.util.Map;
import java.util.UUID;

/**
 * 学习者提交的单题复习评分。
 */
public record MistakeReviewSubmitItem(
    UUID mistakeRecordId,
    Integer quality,
    Boolean isCorrect,
    Map<String, Object> answer
) {
}
