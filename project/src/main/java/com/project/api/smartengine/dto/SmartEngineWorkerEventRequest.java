package com.project.api.smartengine.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;

import java.util.LinkedHashMap;
import java.util.Map;

public record SmartEngineWorkerEventRequest(
    @NotBlank String eventType,
    String stage,
    @Positive int seq,
    Map<String, Object> payload
) {
    public Map<String, Object> safePayload() {
        return payload == null ? new LinkedHashMap<>() : new LinkedHashMap<>(payload);
    }
}
