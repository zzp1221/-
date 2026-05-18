package com.project.api.mistake.dto;

import java.util.List;

/**
 * 复习提交请求体。
 */
public record SubmitReviewSessionRequest(
    List<MistakeReviewSubmitItem> items
) {
}
