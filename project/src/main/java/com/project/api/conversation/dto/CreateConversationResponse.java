package com.project.api.conversation.dto;

import java.util.UUID;

/**
 * 创建新会话后返回的响应。
 */
public record CreateConversationResponse(
    UUID conversationId,
    String title
) {
}
