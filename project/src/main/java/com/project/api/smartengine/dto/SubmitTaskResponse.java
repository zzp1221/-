package com.project.api.smartengine.dto;

import com.project.domain.task.TaskStatus;

import java.util.UUID;

/**
 * Response returned after the control plane accepts a task.
 */
public record SubmitTaskResponse(
    UUID taskId,
    String traceId,
    TaskStatus status
) {
}
