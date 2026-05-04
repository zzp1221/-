package com.project.config;

import com.project.infrastructure.ratelimit.IpRateLimitFilter;
import com.project.infrastructure.ratelimit.RateLimitFilter;
import com.project.security.JwtAuthenticationFilter;
import com.project.security.RestAuthenticationEntryPoint;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * Security configuration for the Java control plane.
 *
 * <p>The design keeps the application stateless and centered around JWT bearer
 * tokens. Public endpoints stay narrowly scoped to health checks, API docs, and
 * authentication entry points; every business API is protected by default.</p>
 */
@Configuration
public class SecurityConfiguration {

    @Bean
    public SecurityFilterChain securityFilterChain(
        HttpSecurity http,
        IpRateLimitFilter ipRateLimitFilter,
        JwtAuthenticationFilter jwtAuthenticationFilter,
        RestAuthenticationEntryPoint authenticationEntryPoint,
        RateLimitFilter rateLimitFilter
    ) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .cors(Customizer.withDefaults())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .exceptionHandling(exceptions -> exceptions.authenticationEntryPoint(authenticationEntryPoint))
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers(
                    "/actuator/health",
                    "/actuator/info",
                    "/error",
                    "/api-docs/**",
                    "/swagger-ui.html",
                    "/swagger-ui/**",
                    "/api/auth/register",
                    "/api/auth/login"
                )
                .permitAll()
                .anyRequest()
                .authenticated()
            )
            .addFilterBefore(ipRateLimitFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterAfter(jwtAuthenticationFilter, IpRateLimitFilter.class)
            .addFilterAfter(rateLimitFilter, JwtAuthenticationFilter.class)
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
