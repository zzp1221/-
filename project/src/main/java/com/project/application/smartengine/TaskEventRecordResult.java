package com.project.application.smartengine;

/**
 * Result of persisting an externally sequenced SmartEngine worker event.
 */
public record TaskEventRecordResult(
    TaskStreamEventPayload payload,
    boolean created
) {
    public static TaskEventRecordResult ignored() {
        return new TaskEventRecordResult(null, false);
    }
}
