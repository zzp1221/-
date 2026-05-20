package com.project.security;

import com.project.application.common.ApplicationException;
import com.project.config.AppProperties;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;

/**
 * Validates internal callbacks from the Python Agent.
 */
@Component
public class InternalTokenVerifier {

    public static final String INTERNAL_TOKEN_HEADER = "X-Zhixue-Internal-Token";
    private static final Path INTERNAL_TOKEN_FILE = Path.of("/run/secrets/zhixue-python-agent-internal-token");

    private final AppProperties appProperties;

    public InternalTokenVerifier(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    public void requireValid(String suppliedToken) {
        String expectedToken = internalToken();
        if (expectedToken.isBlank()) {
            throw new ApplicationException("INTERNAL_TOKEN_NOT_CONFIGURED", "Internal token is not configured", HttpStatus.SERVICE_UNAVAILABLE);
        }
        String normalizedSuppliedToken = suppliedToken == null ? "" : suppliedToken.trim();
        if (
            normalizedSuppliedToken.isBlank()
                || !MessageDigest.isEqual(
                    normalizedSuppliedToken.getBytes(StandardCharsets.UTF_8),
                    expectedToken.getBytes(StandardCharsets.UTF_8)
                )
        ) {
            throw new ApplicationException("INVALID_INTERNAL_TOKEN", "Invalid internal token", HttpStatus.UNAUTHORIZED);
        }
    }

    private String internalToken() {
        String configuredToken = appProperties.getPythonAgent().getInternalToken();
        if (configuredToken != null && !configuredToken.isBlank()) {
            return configuredToken.trim();
        }
        try {
            return Files.exists(INTERNAL_TOKEN_FILE) ? Files.readString(INTERNAL_TOKEN_FILE, StandardCharsets.UTF_8).trim() : "";
        } catch (IOException ex) {
            throw new ApplicationException("INTERNAL_TOKEN_UNAVAILABLE", "Internal token is unavailable", HttpStatus.SERVICE_UNAVAILABLE);
        }
    }
}
