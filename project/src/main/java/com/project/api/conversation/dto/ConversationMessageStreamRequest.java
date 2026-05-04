package com.project.api.conversation.dto;

import com.project.domain.task.ServiceType;
import jakarta.validation.constraints.NotBlank;

/**
 * Request payload for sending a message into a conversation stream.
 */
public record ConversationMessageStreamRequest(
    @NotBlank String message,
    ServiceType serviceType
) {
    public ServiceType resolvedServiceType() {
        return serviceType == null ? ServiceType.TUTORING : serviceType;
    }
}
