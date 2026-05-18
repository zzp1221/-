package com.project.application.conversation;

import java.time.OffsetDateTime;
import java.util.Map;

/**
 * 会话流式传输的 SSE 载荷。
 */
public record ConversationStreamEventPayload(
    String event,
    int seq,
    OffsetDateTime timestamp,
    ConversationDialogState dialogState,
    Map<String, Object> payload
) {
}
