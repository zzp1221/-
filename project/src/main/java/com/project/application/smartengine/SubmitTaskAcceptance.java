package com.project.application.smartengine;

import com.project.api.smartengine.dto.SubmitTaskResponse;

/**
 * Result of a task submission attempt, including idempotent replay information.
 */
public record SubmitTaskAcceptance(
    SubmitTaskResponse response,
    boolean replayed
) {
}
