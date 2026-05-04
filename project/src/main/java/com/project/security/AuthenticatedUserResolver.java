package com.project.security;

import com.project.application.common.ApplicationException;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;

/**
 * Resolves the authenticated JWT principal with a stable 401 response when unavailable.
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
