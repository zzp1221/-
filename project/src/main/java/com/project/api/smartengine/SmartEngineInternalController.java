package com.project.api.smartengine;

import com.project.api.smartengine.dto.SmartEngineWorkerEventRequest;
import com.project.api.smartengine.dto.SmartEngineWorkerFailureRequest;
import com.project.application.smartengine.PythonStreamEvent;
import com.project.application.smartengine.SmartEngineOrchestratorService;
import com.project.application.smartengine.TaskEventRecordResult;
import com.project.security.InternalTokenVerifier;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/internal/smart-engine/tasks/{taskId}")
public class SmartEngineInternalController {

    private final SmartEngineOrchestratorService orchestratorService;
    private final InternalTokenVerifier internalTokenVerifier;

    public SmartEngineInternalController(
        SmartEngineOrchestratorService orchestratorService,
        InternalTokenVerifier internalTokenVerifier
    ) {
        this.orchestratorService = orchestratorService;
        this.internalTokenVerifier = internalTokenVerifier;
    }

    @PostMapping("/started")
    public ResponseEntity<Map<String, String>> started(
        @PathVariable UUID taskId,
        @RequestHeader(name = InternalTokenVerifier.INTERNAL_TOKEN_HEADER, required = false) String internalToken
    ) {
        internalTokenVerifier.requireValid(internalToken);
        orchestratorService.markWorkerStarted(taskId);
        return ResponseEntity.ok(Map.of("status", "started"));
    }

    @PostMapping("/events")
    public ResponseEntity<Map<String, String>> events(
        @PathVariable UUID taskId,
        @RequestHeader(name = InternalTokenVerifier.INTERNAL_TOKEN_HEADER, required = false) String internalToken,
        @Valid @RequestBody SmartEngineWorkerEventRequest request
    ) {
        internalTokenVerifier.requireValid(internalToken);
        TaskEventRecordResult result = orchestratorService.recordWorkerEvent(
            taskId,
            new PythonStreamEvent(request.eventType(), request.stage(), request.safePayload()),
            request.seq()
        );
        if (result.created()) {
            return ResponseEntity.ok(Map.of("status", "recorded"));
        }
        return ResponseEntity.ok(Map.of("status", result.payload() == null ? "ignored" : "duplicate"));
    }

    @PostMapping("/worker-failed")
    public ResponseEntity<Map<String, String>> workerFailed(
        @PathVariable UUID taskId,
        @RequestHeader(name = InternalTokenVerifier.INTERNAL_TOKEN_HEADER, required = false) String internalToken,
        @RequestBody(required = false) SmartEngineWorkerFailureRequest request
    ) {
        internalTokenVerifier.requireValid(internalToken);
        orchestratorService.markWorkerFailed(
            taskId,
            request == null ? null : request.errorCode(),
            request == null ? null : request.message()
        );
        return ResponseEntity.ok(Map.of("status", "recorded"));
    }
}
