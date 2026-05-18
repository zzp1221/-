package com.project.api.auth.dto;

/**
 * 注册或登录成功后返回的认证响应。
 */
public record AuthResponse(
    String token,
    UserView user
) {
}
