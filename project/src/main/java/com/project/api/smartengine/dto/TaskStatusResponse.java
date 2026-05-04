package com.project.api.smartengine.dto;

import com.project.domain.task.ServiceType;
import com.project.domain.task.TaskStatus;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

/**
 * Snapshot view of a submitted task.
 */
public record TaskStatusResponse(
    UUID taskId,
    String traceId,
    ServiceType serviceType,
    TaskStatus status,
    String currentStage,
    BigDecimal progressPercent,
    String errorCode,
    String errorMessage,
    Map<String, Object> responseSummary
) {
}
