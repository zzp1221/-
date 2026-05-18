package com.project.application.ratelimit;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 基于内存存储的滑动窗口限流器。
 *
 * <p>此服务是未来 Redis 实现的即插即用占位符，
 * 同时保持调用契约不变。</p>
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

    @Scheduled(fixedDelay = 300_000)
    public void evictExpired() {
        evictExpired(Duration.ofMinutes(5));
    }

    /** 移除空闲时间超过窗口期的桶。 */
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
