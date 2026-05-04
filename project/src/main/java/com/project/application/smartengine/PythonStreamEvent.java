package com.project.application.smartengine;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Canonical event emitted by the Python runtime and consumed by the Java control plane.
 */
public record PythonStreamEvent(
    String eventType,
    String stage,
    Map<String, Object> payload
) {
    public String eventType() {
        return eventType == null || eventType.isBlank() ? StreamEventType.MESSAGE.wireValue() : eventType;
    }

    public StreamEventType resolvedEventType() {
        return StreamEventType.resolve(eventType());
    }

    public Map<String, Object> safePayload() {
        return payload == null ? new LinkedHashMap<>() : new LinkedHashMap<>(payload);
    }
}
