package com.project.application.smartengine;

import com.project.domain.task.SmartEngineTask;
import com.project.domain.task.SmartEngineTaskEvent;
import com.project.domain.task.SmartEngineTaskEventRepository;
import com.project.domain.task.SmartEngineTaskRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Manages live SSE subscribers and replays persisted events for reconnect scenarios.
 */
@Service
public class SseEmitterService {

    private static final long DEFAULT_TIMEOUT_MS = 0L;

    private final SmartEngineTaskEventRepository taskEventRepository;
    private final SmartEngineTaskRepository taskRepository;
    private final ConcurrentHashMap<UUID, CopyOnWriteArrayList<SseEmitter>> emitters = new ConcurrentHashMap<>();

    public SseEmitterService(
        SmartEngineTaskEventRepository taskEventRepository,
        SmartEngineTaskRepository taskRepository
    ) {
        this.taskEventRepository = taskEventRepository;
        this.taskRepository = taskRepository;
    }

    public SseEmitter subscribe(SmartEngineTask task) {
        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT_MS);
        emitter.onCompletion(() -> removeEmitter(task.getId(), emitter));
        emitter.onTimeout(() -> removeEmitter(task.getId(), emitter));
        emitter.onError(ex -> removeEmitter(task.getId(), emitter));

        replayEvents(task, emitter);
        SmartEngineTask latestTask = taskRepository.findById(task.getId()).orElse(task);

        if (!latestTask.isTerminal()) {
            emitters.computeIfAbsent(task.getId(), ignored -> new CopyOnWriteArrayList<>()).add(emitter);
        } else {
            emitter.complete();
        }

        return emitter;
    }

    public void publish(TaskStreamEventPayload payload, boolean terminal) {
        CopyOnWriteArrayList<SseEmitter> taskEmitters = emitters.get(payload.taskId());
        if (taskEmitters == null || taskEmitters.isEmpty()) {
            return;
        }

        for (SseEmitter emitter : taskEmitters) {
            try {
                send(emitter, payload);
                if (terminal) {
                    emitter.complete();
                }
            } catch (IOException ex) {
                emitter.completeWithError(ex);
                removeEmitter(payload.taskId(), emitter);
            }
        }

        if (terminal) {
            emitters.remove(payload.taskId());
        }
    }

    private void replayEvents(SmartEngineTask task, SseEmitter emitter) {
        List<SmartEngineTaskEvent> events = taskEventRepository.findByTaskIdOrderByEventSeqAsc(task.getId());
        for (SmartEngineTaskEvent event : events) {
            try {
                send(emitter, new TaskStreamEventPayload(
                    event.getEventType(),
                    task.getId(),
                    task.getTraceId(),
                    event.getEventSeq(),
                    event.getCreatedAt() == null ? OffsetDateTime.now() : event.getCreatedAt(),
                    event.getEventPayload()
                ));
            } catch (IOException ex) {
                emitter.completeWithError(ex);
                return;
            }
        }
    }

    private void send(SseEmitter emitter, TaskStreamEventPayload payload) throws IOException {
        emitter.send(SseEmitter.event()
            .name(payload.event())
            .id(String.valueOf(payload.seq()))
            .data(payload));
    }

    private void removeEmitter(UUID taskId, SseEmitter emitter) {
        CopyOnWriteArrayList<SseEmitter> taskEmitters = emitters.get(taskId);
        if (taskEmitters == null) {
            return;
        }
        taskEmitters.remove(emitter);
        if (taskEmitters.isEmpty()) {
            emitters.remove(taskId);
        }
    }
}
