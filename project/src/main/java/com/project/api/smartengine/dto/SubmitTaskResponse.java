package com.project.api.smartengine.dto;

import com.project.domain.task.TaskStatus;

import java.util.UUID;

/**
 * 控制平面接受任务后返回的响应。
 */
public record SubmitTaskResponse(
    UUID taskId,
    String traceId,
    TaskStatus status
) {
}
