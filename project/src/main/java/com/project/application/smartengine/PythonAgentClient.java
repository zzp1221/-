package com.project.application.smartengine;

import java.util.function.Consumer;

/**
 * Abstraction over the Python runtime streaming protocol.
 */
public interface PythonAgentClient {

    void stream(SmartEngineInvocation invocation, Consumer<PythonStreamEvent> eventConsumer);

    /**
     * Cancel an in-flight stream by task id. Implementations should close the
     * underlying connection and optionally notify the Python runtime.
     */
    default void cancel(String taskId) {
    }
}
