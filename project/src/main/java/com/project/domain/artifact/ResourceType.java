package com.project.domain.artifact;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

import java.util.Arrays;

/**
 * Artifact/resource types emitted by the generation pipeline.
 */
public enum ResourceType {
    DOCUMENT,
    EXPLANATION,
    CODE_CASE,
    QUIZ,
    MINDMAP,
    READING,
    VIDEO,
    SLIDES,
    CODE;

    @JsonCreator
    public static ResourceType fromValue(String rawValue) {
        if (rawValue == null || rawValue.isBlank()) {
            throw new IllegalArgumentException("resourceType must not be blank");
        }
        return Arrays.stream(values())
            .filter(candidate -> candidate.name().equalsIgnoreCase(rawValue.trim()))
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException("Unsupported resourceType: " + rawValue));
    }

    @JsonValue
    public String value() {
        return name();
    }
}
