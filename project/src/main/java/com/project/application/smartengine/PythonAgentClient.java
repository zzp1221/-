package com.project.application.smartengine;

import java.util.function.Consumer;

/**
 * 对 Python 运行时流式协议的抽象。
 */
public interface PythonAgentClient {

    void stream(SmartEngineInvocation invocation, Consumer<PythonStreamEvent> eventConsumer);

    /**
     * 根据任务 ID 取消正在进行的流。实现应关闭底层连接，并可选地通知 Python 运行时。
     */
    default void cancel(String taskId) {
    }
}
