package com.project.application.conversation;

import java.time.OffsetDateTime;
import java.util.Map;

/**
 * SSE payload exposed for conversation streaming.
 */
public record ConversationStreamEventPayload(
    String event,
    int seq,
    OffsetDateTime timestamp,
    ConversationDialogState dialogState,
    Map<String, Object> payload
) {
}
