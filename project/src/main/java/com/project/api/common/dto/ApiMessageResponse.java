package com.project.api.common.dto;

/**
 * 仅包含消息的轻量级 API 响应结构。
 */
public record ApiMessageResponse(
    String code,
    String message
) {
}
