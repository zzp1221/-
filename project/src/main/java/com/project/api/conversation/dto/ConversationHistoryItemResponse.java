package com.project.api.conversation.dto;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Sidebar conversation history item exposed to the frontend shell.
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
