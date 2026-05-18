package com.project.api.auth.dto;

import java.util.UUID;

/**
 * 暴露给客户端的最小用户视图。
 */
public record UserView(
    UUID userId,
    String loginId,
    String fullName,
    String majorCode
) {
}
