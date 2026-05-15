package com.project.api.conversation.dto;

import com.project.domain.task.ServiceType;

import java.util.List;

/**
 * Request payload for sending a message into a conversation stream.
 */
public record ConversationMessageStreamRequest(
    String message,
    List<String> imageUrls,
    ServiceType serviceType
) {
    public ServiceType resolvedServiceType() {
        return serviceType == null ? ServiceType.TUTORING : serviceType;
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

    public boolean hasUsableInput() {
        return !normalizedMessage().isBlank() || !normalizedImageUrls().isEmpty();
    }
}
