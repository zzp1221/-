package com.project.application.smartengine;

import com.project.domain.task.ServiceType;

import java.util.Map;
import java.util.UUID;

/**
 * Immutable command object sent from the control plane to the Python runtime.
 */
public record SmartEngineInvocation(
    UUID userId,
    UUID taskId,
    String traceId,
    UUID conversationId,
    ServiceType serviceType,
    Map<String, Object> params
) {
}
