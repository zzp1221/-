package com.project.application.smartengine;

import com.project.api.smartengine.dto.SubmitTaskRequest;
import com.project.api.smartengine.dto.SubmitTaskResponse;
import com.project.api.smartengine.dto.TaskStatusResponse;
import com.project.application.audit.AuditService;
import com.project.application.common.ApplicationException;
import com.project.application.idempotency.IdempotencyService;
import com.project.domain.task.SmartEngineTask;
import com.project.security.JwtAuthenticatedUser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Coordinates task submission, background execution, cancellation, and external SSE exposure.
 */
@Service
public class SmartEngineOrchestratorService {

    private static final Logger LOGGER = LoggerFactory.getLogger(SmartEngineOrchestratorService.class);

    private final TaskStateMachineService taskStateMachineService;
    private final PythonAgentClient pythonAgentClient;
    private final SseEmitterService sseEmitterService;
    private final TaskExecutor smartEngineTaskExecutor;
    private final IdempotencyService idempotencyService;
    private final AuditService auditService;
    private final ConcurrentHashMap<UUID, Thread> runningThreads = new ConcurrentHashMap<>();

    public SmartEngineOrchestratorService(
        TaskStateMachineService taskStateMachineService,
        PythonAgentClient pythonAgentClient,
        SseEmitterService sseEmitterService,
        TaskExecutor smartEngineTaskExecutor,
        IdempotencyService idempotencyService,
        AuditService auditService
    ) {
        this.taskStateMachineService = taskStateMachineService;
        this.pythonAgentClient = pythonAgentClient;
        this.sseEmitterService = sseEmitterService;
        this.smartEngineTaskExecutor = smartEngineTaskExecutor;
        this.idempotencyService = idempotencyService;
        this.auditService = auditService;
    }

    public SubmitTaskAcceptance submit(JwtAuthenticatedUser currentUser, SubmitTaskRequest request) {
        return submit(currentUser, request, null);
    }

    public SubmitTaskAcceptance submit(JwtAuthenticatedUser currentUser, SubmitTaskRequest request, String idempotencyKey) {
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            return idempotencyService.findExisting(currentUser.userId(), "SMART_ENGINE_SUBMIT", idempotencyKey)
                .map(existingTaskId -> {
                    SmartEngineTask existingTask = taskStateMachineService.getOwnedTask(existingTaskId, currentUser.userId());
                    auditService.log("TASK", "LOW", "命中幂等重放", currentUser.userId(), existingTaskId, Map.of("serviceType", request.serviceType()));
                    return new SubmitTaskAcceptance(
                        new SubmitTaskResponse(existingTask.getId(), existingTask.getTraceId(), existingTask.getTaskStatus()),
                        true
                    );
                })
                .orElseGet(() -> createAndDispatchTask(currentUser, request, idempotencyKey));
        }

        return createAndDispatchTask(currentUser, request, null);
    }

    private SubmitTaskAcceptance createAndDispatchTask(
        JwtAuthenticatedUser currentUser,
        SubmitTaskRequest request,
        String idempotencyKey
    ) {
        UUID taskId = UUID.randomUUID();
        String traceId = UUID.randomUUID().toString();
        Map<String, Object> requestPayload = new LinkedHashMap<>();
        requestPayload.put("conversationId", request.conversationId());
        requestPayload.put("params", request.safeParams());

        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            boolean reserved = idempotencyService.reserve(
                currentUser.userId(),
                "SMART_ENGINE_SUBMIT",
                idempotencyKey,
                taskId
            );
            if (!reserved) {
                return idempotencyService.findExisting(currentUser.userId(), "SMART_ENGINE_SUBMIT", idempotencyKey)
                    .map(existingTaskId -> {
                        SmartEngineTask existingTask = taskStateMachineService.getOwnedTask(existingTaskId, currentUser.userId());
                        auditService.log("TASK", "LOW", "命中幂等重放", currentUser.userId(), existingTaskId, Map.of("serviceType", request.serviceType()));
                        return new SubmitTaskAcceptance(
                            new SubmitTaskResponse(existingTask.getId(), existingTask.getTraceId(), existingTask.getTaskStatus()),
                            true
                        );
                    })
                    .orElseThrow(() -> new IllegalStateException("Idempotency reservation failed without an existing record"));
            }
        }

        SmartEngineTask task = taskStateMachineService.createTask(
            taskId,
            currentUser.userId(),
            traceId,
            request.serviceType(),
            requestPayload
        );

        auditService.log("TASK", "INFO", "创建智能任务", currentUser.userId(), task.getId(), Map.of("serviceType", request.serviceType()));

        SmartEngineInvocation invocation = new SmartEngineInvocation(
            currentUser.userId(),
            task.getId(),
            traceId,
            request.conversationId(),
            request.serviceType(),
            request.safeParams()
        );

        smartEngineTaskExecutor.execute(() -> {
            Thread currentThread = Thread.currentThread();
            runningThreads.put(taskId, currentThread);
            try {
                executeTask(taskId, invocation);
            } finally {
                runningThreads.remove(taskId);
            }
        });

        return new SubmitTaskAcceptance(
            new SubmitTaskResponse(task.getId(), traceId, task.getTaskStatus()),
            false
        );
    }

    public TaskStatusResponse getStatus(JwtAuthenticatedUser currentUser, UUID taskId) {
        return taskStateMachineService.getOwnedTaskStatus(taskId, currentUser.userId());
    }

    public SseEmitter subscribe(JwtAuthenticatedUser currentUser, UUID taskId) {
        SmartEngineTask task = taskStateMachineService.getOwnedTask(taskId, currentUser.userId());
        return sseEmitterService.subscribe(task);
    }

    /**
     * Cancel a running task. No-op if the task is already in a terminal state.
     */
    public void cancel(JwtAuthenticatedUser currentUser, UUID taskId) {
        SmartEngineTask task = taskStateMachineService.getOwnedTask(taskId, currentUser.userId());

        if (task.isTerminal()) {
            return;
        }

        auditService.log("TASK", "MEDIUM", "取消任务", currentUser.userId(), taskId, Map.of(
            "currentStatus", task.getTaskStatus().name(),
            "currentStage", task.getCurrentStage() == null ? "" : task.getCurrentStage()
        ));

        pythonAgentClient.cancel(taskId.toString());

        Thread thread = runningThreads.remove(taskId);
        if (thread != null) {
            thread.interrupt();
        }

        TaskStreamEventPayload cancelPayload = taskStateMachineService.markCancelled(taskId);
        sseEmitterService.cancelTask(taskId, cancelPayload);
    }

    private void executeTask(UUID taskId, SmartEngineInvocation invocation) {
        try {
            taskStateMachineService.markRunning(taskId);
            pythonAgentClient.stream(invocation, event -> {
                TaskStreamEventPayload payload = taskStateMachineService.recordPythonEvent(taskId, event);
                sseEmitterService.publish(payload, event.resolvedEventType().isTerminal());
            });

            if (!taskStateMachineService.isTerminal(taskId)) {
                TaskStreamEventPayload autoCompleted = taskStateMachineService.recordPythonEvent(
                    taskId,
                    new PythonStreamEvent(StreamEventType.DONE.wireValue(), "completed", Map.of("message", "Task completed"))
                );
                sseEmitterService.publish(autoCompleted, true);
            }
        } catch (Exception ex) {
            if (Thread.currentThread().isInterrupted() || taskStateMachineService.isCancelled(taskId)) {
                LOGGER.info("Task {} was cancelled, not marking as failed", taskId);
                return;
            }
            auditService.log("TASK", "MEDIUM", "任务执行失败", invocation.userId(), taskId, Map.of("message", ex.getMessage() == null ? "" : ex.getMessage()));
            TaskStreamEventPayload failurePayload = taskStateMachineService.failTask(
                taskId,
                "PYTHON_AGENT_ERROR",
                ex.getMessage() == null ? "Python Agent 调用失败" : ex.getMessage()
            );
            sseEmitterService.publish(failurePayload, true);
        }
    }
}
