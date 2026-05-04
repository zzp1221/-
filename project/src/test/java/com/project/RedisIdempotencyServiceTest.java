package com.project;

import com.project.application.idempotency.RedisIdempotencyService;
import com.project.config.AppProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.time.Duration;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

/**
 * Unit tests for the Redis-backed idempotency service.
 */
@ExtendWith(MockitoExtension.class)
class RedisIdempotencyServiceTest {

    @Mock
    private StringRedisTemplate redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    private RedisIdempotencyService service;

    @BeforeEach
    void setUp() {
        AppProperties properties = new AppProperties();
        properties.getIdempotency().setTtl(Duration.ofHours(24));

        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        service = new RedisIdempotencyService(redisTemplate, properties);
    }

    @Test
    void reserveReturnsTrueWhenKeyIsNew() {
        UUID userId = UUID.randomUUID();
        UUID taskId = UUID.randomUUID();
        when(valueOperations.setIfAbsent(
            "idempotency:%s:%s:%s".formatted(userId, "SMART_ENGINE_SUBMIT", "idem-1"),
            taskId.toString(),
            Duration.ofHours(24)
        )).thenReturn(true);

        boolean reserved = service.reserve(userId, "SMART_ENGINE_SUBMIT", "idem-1", taskId);

        assertThat(reserved).isTrue();
    }

    @Test
    void findExistingReturnsStoredTaskId() {
        UUID userId = UUID.randomUUID();
        UUID taskId = UUID.randomUUID();
        when(valueOperations.get("idempotency:%s:%s:%s".formatted(userId, "SMART_ENGINE_SUBMIT", "idem-2")))
            .thenReturn(taskId.toString());

        Optional<UUID> existing = service.findExisting(userId, "SMART_ENGINE_SUBMIT", "idem-2");

        assertThat(existing).contains(taskId);
    }
}
