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
    private final ConcurrentHashMap<UUID, CopyOnWriteArrayList<Subscriber>> emitters = new ConcurrentHashMap<>();

    public SseEmitterService(
        SmartEngineTaskEventRepository taskEventRepository,
        SmartEngineTaskRepository taskRepository
    ) {
        this.taskEventRepository = taskEventRepository;
        this.taskRepository = taskRepository;
    }

    public synchronized SseEmitter subscribe(SmartEngineTask task) {
        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT_MS);
        Subscriber subscriber = new Subscriber(emitter);
        emitter.onCompletion(() -> removeEmitter(task.getId(), subscriber));
        emitter.onTimeout(() -> removeEmitter(task.getId(), subscriber));
        emitter.onError(ex -> removeEmitter(task.getId(), subscriber));

        replayEvents(task, subscriber);
        SmartEngineTask latestTask = taskRepository.findById(task.getId()).orElse(task);

        if (!latestTask.isTerminal()) {
            emitters.computeIfAbsent(task.getId(), ignored -> new CopyOnWriteArrayList<>()).add(subscriber);
        } else {
            emitter.complete();
        }

        return emitter;
    }

    public synchronized void publish(TaskStreamEventPayload payload, boolean terminal) {
        CopyOnWriteArrayList<Subscriber> taskEmitters = emitters.get(payload.taskId());
        if (taskEmitters == null || taskEmitters.isEmpty()) {
            return;
        }

        for (Subscriber subscriber : taskEmitters) {
            try {
                if (payload.seq() > subscriber.lastSentSeq) {
                    send(subscriber, payload);
                }
                if (terminal) {
                    subscriber.emitter.complete();
                }
            } catch (IOException ex) {
                subscriber.emitter.completeWithError(ex);
                removeEmitter(payload.taskId(), subscriber);
            }
        }

        if (terminal) {
            emitters.remove(payload.taskId());
        }
    }

    private void replayEvents(SmartEngineTask task, Subscriber subscriber) {
        List<SmartEngineTaskEvent> events = taskEventRepository.findByTaskIdOrderByEventSeqAsc(task.getId());
        for (SmartEngineTaskEvent event : events) {
            try {
                send(subscriber, new TaskStreamEventPayload(
                    event.getEventType(),
                    task.getId(),
                    task.getTraceId(),
                    event.getEventSeq(),
                    event.getCreatedAt() == null ? OffsetDateTime.now() : event.getCreatedAt(),
                    event.getEventPayload()
                ));
            } catch (IOException ex) {
                subscriber.emitter.completeWithError(ex);
                return;
            }
        }
    }

    private void send(Subscriber subscriber, TaskStreamEventPayload payload) throws IOException {
        subscriber.emitter.send(SseEmitter.event()
            .name(payload.event())
            .id(String.valueOf(payload.seq()))
            .data(payload));
        subscriber.lastSentSeq = Math.max(subscriber.lastSentSeq, payload.seq());
    }

    /**
     * Force-complete all emitters for a cancelled task and publish the final event.
     */
    public synchronized void cancelTask(UUID taskId, TaskStreamEventPayload cancelPayload) {
        CopyOnWriteArrayList<Subscriber> taskEmitters = emitters.remove(taskId);
        if (taskEmitters == null || taskEmitters.isEmpty()) {
            return;
        }
        for (Subscriber subscriber : taskEmitters) {
            try {
                send(subscriber, cancelPayload);
                subscriber.emitter.complete();
            } catch (IOException ex) {
                subscriber.emitter.completeWithError(ex);
            }
        }
    }

    private void removeEmitter(UUID taskId, Subscriber subscriber) {
        CopyOnWriteArrayList<Subscriber> taskEmitters = emitters.get(taskId);
        if (taskEmitters == null) {
            return;
        }
        taskEmitters.remove(subscriber);
        if (taskEmitters.isEmpty()) {
            emitters.remove(taskId);
        }
    }

    private static final class Subscriber {
        private final SseEmitter emitter;
        private int lastSentSeq;

        private Subscriber(SseEmitter emitter) {
            this.emitter = emitter;
        }
    }
}
