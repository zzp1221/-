package com.project.api.profile.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.Map;

/**
 * Historical profile point used by the front-end timeline panel.
 */
public record UserProfileHistoryPoint(
    Integer version,
    Map<String, Object> profile,
    String summary,
    BigDecimal confidence,
    OffsetDateTime updatedAt
) {
}
