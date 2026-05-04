package com.project.domain.task;

/**
 * Lifecycle states for smart-engine tasks managed by the Java control plane.
 */
public enum TaskStatus {
    PENDING,
    RUNNING,
    COMPLETED,
    FAILED,
    CANCELLED,
    TIMEOUT
}
