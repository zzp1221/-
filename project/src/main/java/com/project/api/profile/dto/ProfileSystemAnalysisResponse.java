package com.project.api.profile.dto;

import java.util.List;

/**
 * 基于画像字段与行为聚合数据的只读分析。
 */
public record ProfileSystemAnalysisResponse(
    String strongestSkill,
    Integer strongestSkillScore,
    List<String> focusAreas,
    ProfileDataCoverageResponse coverage,
    String summary,
    boolean dataAvailable
) {
}
