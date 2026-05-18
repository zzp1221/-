package com.project.api.profile.dto;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 用于前端渲染的当前用户画像视图。
 */
public record UserProfileResponse(
    UUID userId,
    Map<String, Object> profile,
    String summary,
    OffsetDateTime updatedAt,
    List<UserProfileHistoryPoint> history
) {
}
