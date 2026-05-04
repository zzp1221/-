package com.project.api.conversation.dto;

import java.time.OffsetDateTime;

/**
 * Full message item exposed for conversation history replay.
 */
public record ConversationMessageItemResponse(
    String messageId,
    String role,
    String content,
    OffsetDateTime createdAt
) {
}
