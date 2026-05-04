package com.project.config;

import org.junit.jupiter.api.Test;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Verifies safe defaults for infrastructure-facing configuration.
 */
class AppPropertiesTest {

    @Test
    void pythonAgentReadTimeoutDefaultsToTenMinutes() {
        AppProperties properties = new AppProperties();

        assertThat(properties.getPythonAgent().getConnectTimeout()).isEqualTo(Duration.ofSeconds(5));
        assertThat(properties.getPythonAgent().getReadTimeout()).isEqualTo(Duration.ofMinutes(10));
    }
}
