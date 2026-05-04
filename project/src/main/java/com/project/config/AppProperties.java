package com.project.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Centralized application properties for the Java control plane.
 *
 * <p>This object groups infrastructure-facing settings so later modules can inject a
 * single configuration aggregate instead of scattering raw {@code @Value} lookups.
 * Nested classes are designed as extension points for future modules such as JWT
 * issuance, Python streaming clients, and cross-origin access control.</p>
 */
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private final PythonAgent pythonAgent = new PythonAgent();
    private final Cors cors = new Cors();
    private final Security security = new Security();
    private final Idempotency idempotency = new Idempotency();
    private final RateLimit rateLimit = new RateLimit();
    private final Download download = new Download();

    public PythonAgent getPythonAgent() {
        return pythonAgent;
    }

    public Cors getCors() {
        return cors;
    }

    public Security getSecurity() {
        return security;
    }

    public Idempotency getIdempotency() {
        return idempotency;
    }

    public RateLimit getRateLimit() {
        return rateLimit;
    }

    public Download getDownload() {
        return download;
    }

    public static class PythonAgent {
        private String baseUrl = "http://localhost:8000";
        private Duration connectTimeout = Duration.ofSeconds(5);
        private Duration readTimeout = Duration.ofMinutes(10);

        public String getBaseUrl() {
            return baseUrl;
        }

        public void setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
        }

        public Duration getConnectTimeout() {
            return connectTimeout;
        }

        public void setConnectTimeout(Duration connectTimeout) {
            this.connectTimeout = connectTimeout;
        }

        public Duration getReadTimeout() {
            return readTimeout;
        }

        public void setReadTimeout(Duration readTimeout) {
            this.readTimeout = readTimeout;
        }
    }

    public static class Cors {
        private List<String> allowedOrigins = new ArrayList<>(List.of(
            "http://localhost",
            "http://localhost:80",
            "http://localhost:5173",
            "http://localhost:5174"
        ));

        public List<String> getAllowedOrigins() {
            return allowedOrigins;
        }

        public void setAllowedOrigins(List<String> allowedOrigins) {
            this.allowedOrigins = allowedOrigins;
        }
    }

    public static class Security {
        private final Jwt jwt = new Jwt();

        public Jwt getJwt() {
            return jwt;
        }
    }

    public static class Jwt {
        private String issuer = "zhixue-control-plane";
        private String secret = "";
        private Duration accessTokenTtl = Duration.ofHours(2);
        private Duration refreshTokenTtl = Duration.ofDays(7);

        public String getIssuer() {
            return issuer;
        }

        public void setIssuer(String issuer) {
            this.issuer = issuer;
        }

        public Duration getAccessTokenTtl() {
            return accessTokenTtl;
        }

        public String getSecret() {
            return secret;
        }

        public void setSecret(String secret) {
            this.secret = secret;
        }

        public void setAccessTokenTtl(Duration accessTokenTtl) {
            this.accessTokenTtl = accessTokenTtl;
        }

        public Duration getRefreshTokenTtl() {
            return refreshTokenTtl;
        }

        public void setRefreshTokenTtl(Duration refreshTokenTtl) {
            this.refreshTokenTtl = refreshTokenTtl;
        }
    }

    public static class RateLimit {
        private boolean enabled = true;
        private int userRequestsPerMinute = 60;
        private int ipRequestsPerMinute = 100;

        public boolean isEnabled() {
            return enabled;
        }

        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }

        public int getUserRequestsPerMinute() {
            return userRequestsPerMinute;
        }

        public void setUserRequestsPerMinute(int userRequestsPerMinute) {
            this.userRequestsPerMinute = userRequestsPerMinute;
        }

        public int getIpRequestsPerMinute() {
            return ipRequestsPerMinute;
        }

        public void setIpRequestsPerMinute(int ipRequestsPerMinute) {
            this.ipRequestsPerMinute = ipRequestsPerMinute;
        }
    }

    public static class Idempotency {
        private Duration ttl = Duration.ofHours(24);

        public Duration getTtl() {
            return ttl;
        }

        public void setTtl(Duration ttl) {
            this.ttl = ttl;
        }
    }

    public static class Download {
        private long artifactTtlSeconds = 1800;

        public long getArtifactTtlSeconds() {
            return artifactTtlSeconds;
        }

        public void setArtifactTtlSeconds(long artifactTtlSeconds) {
            this.artifactTtlSeconds = artifactTtlSeconds;
        }
    }
}
