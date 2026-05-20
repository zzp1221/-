package com.project.api.smartengine.dto;

public record SmartEngineWorkerFailureRequest(
    String errorCode,
    String message
) {
}
