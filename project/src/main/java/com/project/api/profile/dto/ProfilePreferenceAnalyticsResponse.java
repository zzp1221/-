package com.project.api.profile.dto;

import java.util.List;

/**
 * 个人画像中的讲解偏好证据详情。
 */
public record ProfilePreferenceAnalyticsResponse(
    List<ProfileResourcePreferenceResponse> resourcePreferences,
    ProfileExplanationPreferenceResponse explanationPreference
) {
}
