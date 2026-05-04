package com.project.application.ratelimit;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Sliding-window rate limiter with an in-memory store.
 *
 * <p>This service is a drop-in placeholder for a future Redis-backed
 * implementation while keeping the calling contract stable.</p>
 */
@Service
@ConditionalOnMissingBean(name = "stringRedisTemplate")
public class InMemorySlidingWindowRateLimiter implements RateLimiter {

    private final ConcurrentHashMap<String, Deque<Instant>> buckets = new ConcurrentHashMap<>();

    @Override
    public boolean allow(String key, int limit, Duration window) {
        Instant now = Instant.now();
        Deque<Instant> bucket = buckets.computeIfAbsent(key, ignored -> new ArrayDeque<>());
        synchronized (bucket) {
            Instant cutoff = now.minus(window);
            while (!bucket.isEmpty() && bucket.peekFirst().isBefore(cutoff)) {
                bucket.removeFirst();
            }
            if (bucket.size() >= limit) {
                return false;
            }
            bucket.addLast(now);
            return true;
        }
    }

    /** Remove buckets that have been idle for longer than the window. */
    public void evictExpired(Duration window) {
        Instant cutoff = Instant.now().minus(window).minus(window);
        buckets.entrySet().removeIf(entry -> {
            Deque<Instant> bucket = entry.getValue();
            synchronized (bucket) {
                return bucket.isEmpty() || bucket.peekLast().isBefore(cutoff);
            }
        });
    }
}
