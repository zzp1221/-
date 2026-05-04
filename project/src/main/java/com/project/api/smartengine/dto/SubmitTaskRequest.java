package com.project.api.smartengine.dto;

import com.project.domain.task.ServiceType;
import jakarta.validation.constraints.NotNull;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Request payload for submitting a smart-engine task.
 */
public record SubmitTaskRequest(
    @NotNull UUID conversationId,
    @NotNull ServiceType serviceType,
    Map<String, Object> params
) {
    public Map<String, Object> safeParams() {
        return params == null ? new LinkedHashMap<>() : new LinkedHashMap<>(params);
    }
}
