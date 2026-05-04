package com.project.application.conversation;

import com.project.api.conversation.dto.ConversationMessageItemResponse;

import java.util.List;
import java.util.UUID;

/**
 * Reads and writes persisted conversation transcript messages from the Python runtime.
 */
public interface PythonConversationMessageClient {

    void appendMessage(UUID conversationId, UUID userId, String role, String content);

    List<ConversationMessageItemResponse> listMessages(UUID conversationId, UUID userId);
}
