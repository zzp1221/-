package com.project.api.auth.dto;

/**
 * Authentication response returned after successful registration or login.
 */
public record AuthResponse(
    String token,
    UserView user
) {
}
