package com.project.api.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

/**
 * Request payload for user registration.
 */
public record RegisterRequest(
    @NotBlank @Size(max = 64) String loginId,
    @NotBlank
    @Size(min = 8, max = 128)
    @Pattern(
        regexp = "^(?=.*[A-Za-z])(?=.*\\d).+$",
        message = "密码至少 8 位，且需同时包含字母和数字"
    )
    String password,
    @NotBlank @Size(max = 64) String fullName,
    @Size(max = 32) String majorCode
) {
}
