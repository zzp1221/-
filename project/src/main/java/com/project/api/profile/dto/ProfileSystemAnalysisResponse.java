package com.project.api.profile.dto;

import java.util.List;

/**
 * Read-only analysis derived from profile fields and behavior aggregates.
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
