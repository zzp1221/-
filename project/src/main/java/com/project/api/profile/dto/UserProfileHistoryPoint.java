package com.project.api.profile.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.Map;

/**
 * 供前端时间线面板使用的历史画像数据点。
 */
public record UserProfileHistoryPoint(
    Integer version,
    Map<String, Object> profile,
    String summary,
    BigDecimal confidence,
    OffsetDateTime updatedAt
) {
}
