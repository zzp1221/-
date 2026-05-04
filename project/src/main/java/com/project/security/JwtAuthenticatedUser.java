package com.project.security;

import java.util.UUID;

/**
 * Immutable authenticated principal extracted from a validated JWT.
 */
public record JwtAuthenticatedUser(
    UUID userId,
    String loginId,
    String role
) {
}
