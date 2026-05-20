package com.project.api.profile.dto;

import java.time.OffsetDateTime;

/**
 * 单类资源偏好的真实证据聚合。
 */
public record ProfileResourcePreferenceResponse(
    String type,
    String label,
    boolean identified,
    boolean profileMentioned,
    int requestCount,
    int generatedCount,
    int downloadCount,
    OffsetDateTime lastUsedAt,
    String evidenceLabel
) {
}
