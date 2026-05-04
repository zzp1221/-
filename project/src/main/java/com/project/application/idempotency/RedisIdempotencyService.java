package com.project.application.idempotency;

import com.project.config.AppProperties;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Optional;
import java.util.UUID;

/**
 * Redis-backed idempotency store using {@code SETNX + TTL}.
 */
@Service
@ConditionalOnBean(StringRedisTemplate.class)
public class RedisIdempotencyService implements IdempotencyService {

    private final StringRedisTemplate redisTemplate;
    private final Duration ttl;

    public RedisIdempotencyService(StringRedisTemplate redisTemplate, AppProperties appProperties) {
        this.redisTemplate = redisTemplate;
        this.ttl = appProperties.getIdempotency().getTtl();
    }

    @Override
    public Optional<UUID> findExisting(UUID userId, String operation, String idempotencyKey) {
        String value = redisTemplate.opsForValue().get(composeKey(userId, operation, idempotencyKey));
        if (value == null || value.isBlank()) {
            return Optional.empty();
        }
        return Optional.of(UUID.fromString(value));
    }

    @Override
    public boolean reserve(UUID userId, String operation, String idempotencyKey, UUID taskId) {
        Boolean success = redisTemplate.opsForValue().setIfAbsent(
            composeKey(userId, operation, idempotencyKey),
            taskId.toString(),
            ttl
        );
        return Boolean.TRUE.equals(success);
    }

    private String composeKey(UUID userId, String operation, String idempotencyKey) {
        return "idempotency:%s:%s:%s".formatted(userId, operation, idempotencyKey);
    }
}
