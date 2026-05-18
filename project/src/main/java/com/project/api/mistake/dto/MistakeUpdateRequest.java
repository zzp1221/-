package com.project.api.mistake.dto;

/**
 * 错题记录中用户可编辑的字段。
 */
public record MistakeUpdateRequest(
    String userNote,
    String mistakeType,
    Boolean mastered
) {
}
