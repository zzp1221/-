package com.project.api.conversation.dto;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * 暴露给前端外壳的侧边栏会话历史项。
 */
public record ConversationHistoryItemResponse(
    UUID conversationId,
    String title,
    String lastMessagePreview,
    Integer messageCount,
    OffsetDateTime lastMessageAt,
    OffsetDateTime updatedAt
) {
}
