package com.project.api.common.dto;

/**
 * Lightweight response structure for message-only API replies.
 */
public record ApiMessageResponse(
    String code,
    String message
) {
}
