package com.project.application.smartengine;

import com.project.api.smartengine.dto.SubmitTaskResponse;

/**
 * 任务提交尝试的结果，包含幂等重放信息。
 */
public record SubmitTaskAcceptance(
    SubmitTaskResponse response,
    boolean replayed
) {
}
