package com.project.api.smartengine;

import com.project.api.smartengine.dto.IdempotentReplayResponse;
import com.project.api.smartengine.dto.SubmitTaskRequest;
import com.project.api.smartengine.dto.SubmitTaskResponse;
import com.project.api.smartengine.dto.TaskStatusResponse;
import com.project.application.smartengine.SmartEngineOrchestratorService;
import com.project.application.smartengine.SubmitTaskAcceptance;
import com.project.security.AuthenticatedUserResolver;
import com.project.security.JwtAuthenticatedUser;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.UUID;

/**
 * External task submission and streaming APIs for the smart-engine workflow.
 */
@RestController
@RequestMapping("/api/smart-engine")
@Tag(name = "Smart Engine")
public class SmartEngineController {

    private final SmartEngineOrchestratorService orchestratorService;

    public SmartEngineController(SmartEngineOrchestratorService orchestratorService) {
        this.orchestratorService = orchestratorService;
    }

    @PostMapping("/submit")
    @Operation(summary = "Submit a smart-engine task")
    public ResponseEntity<?> submit(
        Authentication authentication,
        @RequestHeader(name = "Idempotency-Key", required = false) String idempotencyKey,
        @Valid @RequestBody SubmitTaskRequest request
    ) {
        JwtAuthenticatedUser principal = AuthenticatedUserResolver.require(authentication);
        SubmitTaskAcceptance acceptance = orchestratorService.submit(
            principal,
            request,
            idempotencyKey
        );
        SubmitTaskResponse response = acceptance.response();

        if (acceptance.replayed()) {
            return ResponseEntity.status(409).body(
                new IdempotentReplayResponse("IDEMPOTENT_REPLAY", "重复提交，返回已存在任务", response.taskId())
            );
        }

        return ResponseEntity.ok(response);
    }

    @GetMapping("/tasks/{taskId}")
    @Operation(summary = "Query task status")
    public ResponseEntity<TaskStatusResponse> getTaskStatus(
        Authentication authentication,
        @PathVariable UUID taskId
    ) {
        return ResponseEntity.ok(orchestratorService.getStatus(AuthenticatedUserResolver.require(authentication), taskId));
    }

    @GetMapping(path = "/tasks/{taskId}/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @Operation(summary = "Subscribe to task SSE stream")
    public SseEmitter streamTask(
        Authentication authentication,
        @PathVariable UUID taskId
    ) {
        return orchestratorService.subscribe(AuthenticatedUserResolver.require(authentication), taskId);
    }

    @PostMapping("/tasks/{taskId}/cancel")
    @Operation(summary = "Cancel a running task")
    public ResponseEntity<Void> cancelTask(
        Authentication authentication,
        @PathVariable UUID taskId
    ) {
        orchestratorService.cancel(AuthenticatedUserResolver.require(authentication), taskId);
        return ResponseEntity.noContent().build();
    }
}
