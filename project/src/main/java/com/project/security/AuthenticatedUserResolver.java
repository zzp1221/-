package com.project.security;

import com.project.application.common.ApplicationException;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;

/**
 * 解析已认证的 JWT 主体，未认证时返回稳定的 401 响应。
 */
public final class AuthenticatedUserResolver {

    private AuthenticatedUserResolver() {
    }

    public static JwtAuthenticatedUser require(Authentication authentication) {
        if (authentication != null && authentication.getPrincipal() instanceof JwtAuthenticatedUser principal) {
            return principal;
        }
        throw new ApplicationException("UNAUTHORIZED", "认证信息无效", HttpStatus.UNAUTHORIZED);
    }
}
