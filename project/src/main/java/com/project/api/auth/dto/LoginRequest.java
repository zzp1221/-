package com.project.api.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Request payload for password-based login.
 *
 * <p>Login only validates presence and an upper bound for credentials. The
 * endpoint intentionally does not enforce registration-time password policy so
 * callers always receive a stable authentication result instead of leaking
 * validation details about the submitted password.</p>
 */
public record LoginRequest(
    @NotBlank @Size(max = 64) String loginId,
    @NotBlank @Size(max = 128) String password
) {
}
