package com.project.api.mistake.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

/**
 * 包含待复习错题项的复习会话。
 */
public record MistakeReviewSessionResponse(
    UUID sessionId,
    String status,
    BigDecimal score,
    List<MistakeRecordResponse> items,
    OffsetDateTime createdAt,
    OffsetDateTime completedAt
) {
}
