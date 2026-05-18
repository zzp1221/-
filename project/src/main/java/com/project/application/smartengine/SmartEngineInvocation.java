package com.project.application.smartengine;

import com.project.domain.task.ServiceType;

import java.util.Map;
import java.util.UUID;

/**
 * 从控制平面发送到 Python 运行时的不可变命令对象。
 */
public record SmartEngineInvocation(
    UUID userId,
    UUID taskId,
    String traceId,
    UUID conversationId,
    ServiceType serviceType,
    Map<String, Object> params
) {
}
