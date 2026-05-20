package com.project.api.profile.dto;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

/**
 * 画像页面的真实数据分析。
 */
public record UserProfileAnalyticsResponse(
    UUID userId,
    int days,
    LocalDate fromDate,
    LocalDate toDate,
    List<ProfileBehaviorTrendPoint> behaviorTrend,
    ProfileSystemAnalysisResponse systemAnalysis,
    ProfilePreferenceAnalyticsResponse preferenceAnalytics
) {
}
