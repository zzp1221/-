package com.project.api.conversation.dto;

import com.project.domain.conversation.ConversationReasoningMode;
import com.project.domain.task.ServiceType;

import java.util.List;

/**
 * 向会话流发送消息的请求体。
 */
public record ConversationMessageStreamRequest(
    String message,
    List<String> imageUrls,
    ServiceType serviceType,
    Boolean webSearchEnabled,
    ConversationReasoningMode reasoningMode
) {
    public ServiceType resolvedServiceType() {
        return serviceType == null ? ServiceType.TUTORING : serviceType;
    }

    public ConversationReasoningMode resolvedReasoningMode() {
        return reasoningMode == null ? ConversationReasoningMode.NORMAL : reasoningMode;
    }

    public String normalizedMessage() {
        return message == null ? "" : message.trim();
    }

    public List<String> normalizedImageUrls() {
        return imageUrls == null ? List.of() : imageUrls.stream()
            .filter(item -> item != null && !item.isBlank())
            .map(String::trim)
            .distinct()
            .toList();
    }

    public boolean isWebSearchEnabled() {
        return Boolean.TRUE.equals(webSearchEnabled);
    }

    public boolean hasUsableInput() {
        return !normalizedMessage().isBlank() || !normalizedImageUrls().isEmpty();
    }
}
