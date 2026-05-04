package com.project.application.ratelimit;

import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * Redis sorted-set based sliding window rate limiter.
 *
 * <p>A Lua script keeps cleanup, counting, and insertion in a single atomic
 * roundtrip, which avoids race conditions under concurrent requests.</p>
 */
@Service
@ConditionalOnBean(StringRedisTemplate.class)
public class RedisSlidingWindowRateLimiter implements RateLimiter {

    private static final DefaultRedisScript<Long> SLIDING_WINDOW_SCRIPT = new DefaultRedisScript<>(
        """
            local key = KEYS[1]
            local window = tonumber(ARGV[1])
            local limit = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local member = ARGV[4]

            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
            local count = redis.call('ZCARD', key)

            if count >= limit then
                redis.call('EXPIRE', key, math.ceil(window / 1000) + 1)
                return 0
            end

            redis.call('ZADD', key, now, member)
            redis.call('EXPIRE', key, math.ceil(window / 1000) + 1)
            return 1
            """,
        Long.class
    );

    private final StringRedisTemplate redisTemplate;

    public RedisSlidingWindowRateLimiter(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public boolean allow(String key, int limit, Duration window) {
        Long result = redisTemplate.execute(
            SLIDING_WINDOW_SCRIPT,
            List.of(composeKey(key)),
            String.valueOf(window.toMillis()),
            String.valueOf(limit),
            String.valueOf(Instant.now().toEpochMilli()),
            UUID.randomUUID().toString()
        );
        return Long.valueOf(1L).equals(result);
    }

    private String composeKey(String key) {
        return "rate_limit:%s".formatted(key);
    }
}
