package com.project.api.auth.dto;

import java.util.UUID;

/**
 * Minimal user view exposed to clients.
 */
public record UserView(
    UUID userId,
    String loginId,
    String fullName,
    String majorCode
) {
}
