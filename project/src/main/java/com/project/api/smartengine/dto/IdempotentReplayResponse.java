package com.project.api.smartengine.dto;

import java.util.UUID;

/**
 * Response returned when an idempotency key replays an existing task.
 */
public record IdempotentReplayResponse(
    String code,
    String message,
    UUID taskId
) {
}
