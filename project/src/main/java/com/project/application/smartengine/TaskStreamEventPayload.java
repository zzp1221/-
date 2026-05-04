package com.project.application.smartengine;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * External SSE event contract produced by the Java control plane.
 */
public record TaskStreamEventPayload(
    String event,
    UUID taskId,
    String traceId,
    int seq,
    OffsetDateTime timestamp,
    Map<String, Object> payload
) {
    public Map<String, Object> safePayload() {
        return payload == null ? new LinkedHashMap<>() : new LinkedHashMap<>(payload);
    }
}
