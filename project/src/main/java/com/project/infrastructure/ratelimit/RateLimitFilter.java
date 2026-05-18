package com.project.infrastructure.ratelimit;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.api.common.dto.ApiMessageResponse;
import com.project.application.audit.AuditService;
import com.project.application.ratelimit.RateLimiter;
import com.project.config.AppProperties;
import com.project.security.JwtAuthenticatedUser;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Map;

/**
 * 对 API 请求应用 IP 级和用户级限流。
 */
@Component
public class RateLimitFilter extends OncePerRequestFilter {

    private final AppProperties appProperties;
    private final RateLimiter rateLimiter;
    private final ObjectMapper objectMapper;
    private final AuditService auditService;

    public RateLimitFilter(
        AppProperties appProperties,
        RateLimiter rateLimiter,
        ObjectMapper objectMapper,
        AuditService auditService
    ) {
        this.appProperties = appProperties;
        this.rateLimiter = rateLimiter;
        this.objectMapper = objectMapper;
        this.auditService = auditService;
    }

    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain
    ) throws ServletException, IOException {
        if (!appProperties.getRateLimit().isEnabled() || !request.getRequestURI().startsWith("/api/")) {
            filterChain.doFilter(request, response);
            return;
        }

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof JwtAuthenticatedUser principal) {
            if (!rateLimiter.allow("user:" + principal.userId(), appProperties.getRateLimit().getUserRequestsPerMinute(), IpRateLimitFilter.WINDOW)) {
                auditService.log("SAFETY", "MEDIUM", "用户限流命中", principal.userId(), null, Map.of("path", request.getRequestURI()));
                writeTooManyRequests(response);
                return;
            }
        }

        filterChain.doFilter(request, response);
    }

    private void writeTooManyRequests(HttpServletResponse response) throws IOException {
        response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
        response.setCharacterEncoding("UTF-8");
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        objectMapper.writeValue(response.getWriter(), new ApiMessageResponse("TOO_MANY_REQUESTS", "请求过于频繁，请稍后重试"));
    }
}
