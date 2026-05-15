package com.project.api.conversation.dto;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Full message item exposed for conversation history replay.
 */
public record ConversationMessageItemResponse(
    String messageId,
    String role,
    String content,
    List<String> imageUrls,
    OffsetDateTime createdAt
) {
}
