package com.project.application.conversation;

import java.util.UUID;

/**
 * Lightweight teaching-state metadata emitted alongside conversation SSE events.
 */
public record ConversationDialogState(
    UUID conversationId,
    String turnId,
    String pedagogyStrategy,
    String nextAction
) {
}
