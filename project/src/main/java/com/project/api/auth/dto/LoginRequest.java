package com.project.api.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * 基于密码的登录请求体。
 *
 * <p>登录仅校验凭据的存在性和长度上限。该端点故意不强制执行注册时的密码策略，
 * 以便调用方始终获得稳定的认证结果，而不会泄露所提交密码的校验细节。</p>
 */
public record LoginRequest(
    @NotBlank @Size(max = 64) String loginId,
    @NotBlank @Size(max = 128) String password
) {
}
