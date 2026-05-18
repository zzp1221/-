package com.project.application.smartengine;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 由 Java 控制平面生成的外部 SSE 事件契约。
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
