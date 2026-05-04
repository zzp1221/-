package com.project.application.smartengine;

import java.util.function.Consumer;

/**
 * Abstraction over the Python runtime streaming protocol.
 */
public interface PythonAgentClient {

    void stream(SmartEngineInvocation invocation, Consumer<PythonStreamEvent> eventConsumer);
}
