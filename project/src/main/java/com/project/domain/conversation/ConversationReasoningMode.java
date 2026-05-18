package com.project.domain.conversation;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

import java.util.Arrays;

/**
 * 对话轮次请求的推理深度。
 */
public enum ConversationReasoningMode {
    NORMAL,
    DEEP;

    @JsonCreator
    public static ConversationReasoningMode fromValue(String rawValue) {
        if (rawValue == null || rawValue.isBlank()) {
            return NORMAL;
        }
        return Arrays.stream(values())
            .filter(candidate -> candidate.name().equalsIgnoreCase(rawValue.trim()))
            .findFirst()
            .orElse(NORMAL);
    }

    @JsonValue
    public String value() {
        return name();
    }
}
