package com.project.security;

import java.util.UUID;

/**
 * 从已验证的 JWT 中提取的不可变认证主体。
 */
public record JwtAuthenticatedUser(
    UUID userId,
    String loginId,
    String role
) {
}
