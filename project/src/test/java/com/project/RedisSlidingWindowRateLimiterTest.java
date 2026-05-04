package com.project;

import com.project.application.ratelimit.RedisSlidingWindowRateLimiter;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentMatchers;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;

import java.time.Duration;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

/**
 * Unit tests for the Redis sliding window limiter.
 */
@ExtendWith(MockitoExtension.class)
class RedisSlidingWindowRateLimiterTest {

    @Mock
    private StringRedisTemplate redisTemplate;

    @Test
    void allowReturnsTrueWhenLuaScriptApprovesRequest() {
        when(redisTemplate.execute(
            ArgumentMatchers.<RedisScript<Long>>any(),
            ArgumentMatchers.eq(List.of("rate_limit:user:123")),
            ArgumentMatchers.anyString(),
            ArgumentMatchers.eq("5"),
            ArgumentMatchers.anyString(),
            ArgumentMatchers.anyString()
        )).thenReturn(1L);

        RedisSlidingWindowRateLimiter limiter = new RedisSlidingWindowRateLimiter(redisTemplate);

        boolean allowed = limiter.allow("user:123", 5, Duration.ofMinutes(1));

        assertThat(allowed).isTrue();
    }

    @Test
    void allowReturnsFalseWhenLuaScriptRejectsRequest() {
        when(redisTemplate.execute(
            ArgumentMatchers.<RedisScript<Long>>any(),
            ArgumentMatchers.eq(List.of("rate_limit:ip:127.0.0.1")),
            ArgumentMatchers.anyString(),
            ArgumentMatchers.eq("1"),
            ArgumentMatchers.anyString(),
            ArgumentMatchers.anyString()
        )).thenReturn(0L);

        RedisSlidingWindowRateLimiter limiter = new RedisSlidingWindowRateLimiter(redisTemplate);

        boolean allowed = limiter.allow("ip:127.0.0.1", 1, Duration.ofMinutes(1));

        assertThat(allowed).isFalse();
    }
}
