package com.project.api.smartengine.dto;

import java.util.UUID;

/**
 * 幂等键重放已有任务时返回的响应。
 */
public record IdempotentReplayResponse(
    String code,
    String message,
    UUID taskId
) {
}
