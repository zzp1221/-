package com.project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

/**
 * Configures cross-origin access for the browser-facing control plane.
 *
 * <p>The configuration is property-driven so the runtime can extend the allowed
 * origins list through environment variables without code changes.</p>
 */
@Configuration
public class CorsConfiguration {

    @Bean
    public CorsConfigurationSource corsConfigurationSource(AppProperties appProperties) {
        org.springframework.web.cors.CorsConfiguration configuration =
            new org.springframework.web.cors.CorsConfiguration();

        configuration.setAllowedOrigins(normalizeOrigins(appProperties.getCors().getAllowedOrigins()));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of(
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "Cache-Control",
            "Last-Event-ID",
            "Idempotency-Key"
        ));
        configuration.setExposedHeaders(List.of("Authorization", "Content-Disposition"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    private List<String> normalizeOrigins(List<String> rawOrigins) {
        return rawOrigins.stream()
            .flatMap(value -> List.of(value.split(",")).stream())
            .map(String::trim)
            .filter(origin -> !origin.isBlank())
            .distinct()
            .toList();
    }
}
