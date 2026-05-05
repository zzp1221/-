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
        SimpleAsyncTaskExecutor executor = new SimpleAsyncTaskExecutor();
        executor.setVirtualThreads(true);
        executor.setConcurrencyLimit(16);
        executor.setThreadNamePrefix("smart-engine-");
        return executor;
    }
}
