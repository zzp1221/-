package com.project.api.profile.dto;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Current user profile view for front-end rendering.
 */
public record UserProfileResponse(
    UUID userId,
    Map<String, Object> profile,
    String summary,
    OffsetDateTime updatedAt,
    List<UserProfileHistoryPoint> history
) {
}
