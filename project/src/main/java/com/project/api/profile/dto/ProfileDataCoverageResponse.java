package com.project.api.profile.dto;

/**
 * Counts of real data sources used for profile analytics.
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
