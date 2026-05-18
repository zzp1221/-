package com.project.application.conversation;

import java.util.UUID;

/**
 * 与会话 SSE 事件一起发出的轻量级教学状态元数据。
 */
public record ConversationDialogState(
    UUID conversationId,
    String turnId,
    String pedagogyStrategy,
    String nextAction
) {
}
