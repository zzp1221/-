package com.project.api.mistake.dto;

import java.util.List;

/**
 * 分页的错题列表响应。
 */
public record MistakeListResponse(
    List<MistakeRecordResponse> items,
    long total,
    int page,
    int size,
    MistakeStatsResponse stats
) {
}
