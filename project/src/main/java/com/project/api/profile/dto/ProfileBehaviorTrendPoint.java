package com.project.api.profile.dto;

import java.time.LocalDate;

/**
 * 画像分析页面使用的每日真实行为计数器。
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
