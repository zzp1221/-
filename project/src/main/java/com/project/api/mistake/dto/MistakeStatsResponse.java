package com.project.api.mistake.dto;

/**
 * 错题本顶部展示的汇总计数器。
 */
public record MistakeStatsResponse(
    long dueCount,
    long activeCount,
    long masteredCount
) {
}
