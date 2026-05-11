package com.project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.SimpleAsyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Virtual-thread-backed executor for smart-engine and conversation task dispatch.
 *
 * <p>Each task runs on a virtual thread so blocking I/O (Python SSE, DB writes)
 * does not consume a platform thread. A concurrency limit protects the Python
 * agent and PostgreSQL connection pool from unbounded fan-out.</p>
 */
@Configuration
@EnableScheduling
public class TaskExecutionConfiguration {

    @Bean
    public TaskExecutor smartEngineTaskExecutor() {
        return buildExecutor("smart-engine-", 16);
    }

    @Bean
    public TaskExecutor conversationTaskExecutor() {
        // Reserve dedicated capacity for tutoring streams so they do not queue
        // behind long-running smart-engine tasks.
        return buildExecutor("conversation-", 8);
    }

    private TaskExecutor buildExecutor(String threadNamePrefix, int concurrencyLimit) {
        SimpleAsyncTaskExecutor executor = new SimpleAsyncTaskExecutor();
        executor.setVirtualThreads(true);
        executor.setConcurrencyLimit(concurrencyLimit);
        executor.setThreadNamePrefix(threadNamePrefix);
        return executor;
    }
}
