package com.project.api.profile.dto;

import java.time.LocalDate;

/**
 * Daily real behavior counters used by the profile analytics page.
 */
public record ProfileBehaviorTrendPoint(
    LocalDate date,
    int conversationCount,
    int serviceTaskCount,
    int practiceSubmissionCount,
    Double practiceAccuracy,
    int newMistakeCount,
    int reviewCount
) {
}
