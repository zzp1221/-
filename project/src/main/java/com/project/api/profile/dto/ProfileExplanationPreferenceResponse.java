package com.project.api.profile.dto;

/**
 * 讲解方式偏好的真实画像字段来源。
 */
public record ProfileExplanationPreferenceResponse(
    String value,
    String source,
    boolean identified
) {
}
