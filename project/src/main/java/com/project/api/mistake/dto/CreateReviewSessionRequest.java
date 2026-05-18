package com.project.api.mistake.dto;

import java.util.List;
import java.util.UUID;

/**
 * 可选的复习会话选择。mistakeIds 为空表示选择到期的错题。
 */
public record CreateReviewSessionRequest(
    List<UUID> mistakeIds,
    Integer limit
) {
}
