package com.project.api.profile.dto;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

/**
 * Real-data analytics for the full profile page.
 */
public record UserProfileAnalyticsResponse(
    UUID userId,
    int days,
    LocalDate fromDate,
    LocalDate toDate,
    List<ProfileBehaviorTrendPoint> behaviorTrend,
    ProfileSystemAnalysisResponse systemAnalysis
) {
}
