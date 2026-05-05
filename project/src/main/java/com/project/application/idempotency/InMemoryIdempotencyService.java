package com.project.application.idempotency;

import com.project.config.AppProperties;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lightweight idempotency registry used by the control plane.
 *
 * <p>The implementation is intentionally interface-friendly and can be replaced
 * by Redis without affecting controllers or orchestrator services.</p>
 */
@Service
@ConditionalOnMissingBean(name = "stringRedisTemplate")
public class InMemoryIdempotencyService implements IdempotencyService {

    private final Duration ttl;
    private final ConcurrentHashMap<String, Entry> taskIdsByKey = new ConcurrentHashMap<>();

    public InMemoryIdempotencyService(AppProperties appProperties) {
        this.ttl = appProperties.getIdempotency().getTtl();
    }

    @Override
    public Optional<UUID> findExisting(UUID userId, String operation, String idempotencyKey) {
        evictExpired();
        String key = composeKey(userId, operation, idempotencyKey);
        Entry entry = taskIdsByKey.get(key);
        if (entry == null) {
            return Optional.empty();
        }
        if (entry.isExpired()) {
            taskIdsByKey.remove(key);
            return Optional.empty();
        }
        return Optional.of(entry.taskId());
    }

    @Override
    public boolean reserve(UUID userId, String operation, String idempotencyKey, UUID taskId) {
        evictExpired();
        String key = composeKey(userId, operation, idempotencyKey);
        return taskIdsByKey.putIfAbsent(key, new Entry(taskId, Instant.now().plus(ttl))) == null;
    }

    private void evictExpired() {
        taskIdsByKey.entrySet().removeIf(e -> e.getValue().isExpired());
    }

    private String composeKey(UUID userId, String operation, String idempotencyKey) {
        return userId + "|" + operation + "|" + idempotencyKey;
    }

    private record Entry(UUID taskId, Instant expiresAt) {
        boolean isExpired() {
            return Instant.now().isAfter(expiresAt);
        }
    }
}
