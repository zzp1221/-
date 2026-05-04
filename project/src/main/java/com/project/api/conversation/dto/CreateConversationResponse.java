package com.project.api.conversation.dto;

import java.util.UUID;

/**
 * Response returned after creating a new conversation.
 */
public record CreateConversationResponse(
    UUID conversationId,
    String title
) {
}
