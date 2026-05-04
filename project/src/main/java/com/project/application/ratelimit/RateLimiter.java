package com.project.application.ratelimit;

import java.time.Duration;

/**
 * Port for request rate limiting.
 */
public interface RateLimiter {

    boolean allow(String key, int limit, Duration window);
}
