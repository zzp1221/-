package com.project.application.ratelimit;

import java.time.Duration;

/**
 * 请求限流端口。
 */
public interface RateLimiter {

    boolean allow(String key, int limit, Duration window);
}
