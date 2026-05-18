package com.project.api.smartengine.dto;

import com.project.domain.task.ServiceType;
import jakarta.validation.constraints.NotNull;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 提交智学引擎任务的请求体。
 */
public record SubmitTaskRequest(
    @NotNull UUID conversationId,
    @NotNull ServiceType serviceType,
    @NotNull
    Map<String, Object> params
) {
    public Map<String, Object> safeParams() {
        return params == null ? new LinkedHashMap<>() : new LinkedHashMap<>(params);
    }
}
