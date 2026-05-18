package com.project.application.smartengine;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 由 Python 运行时发出、Java 控制平面消费的规范事件。
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
