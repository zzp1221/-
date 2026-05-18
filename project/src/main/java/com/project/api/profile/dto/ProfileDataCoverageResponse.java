package com.project.api.profile.dto;

/**
 * 画像分析所用真实数据源的计数统计。
 */
public record ProfileDataCoverageResponse(
    int activeDays,
    int conversationCount,
    int serviceTaskCount,
    int practiceSubmissionCount,
    int newMistakeCount,
    int reviewCount,
    int profileSkillCount,
    int weakPointCount
) {
}
