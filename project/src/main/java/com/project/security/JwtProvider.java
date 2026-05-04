package com.project.security;

import com.project.config.AppProperties;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import java.util.Map;
import java.util.UUID;

/**
 * JWT issuing and parsing service for the control plane.
 *
 * <p>The provider keeps token creation isolated from controllers so future
 * changes such as refresh-token rotation or asymmetric signing can be added
 * without rewriting endpoint logic.</p>
 */
@Component
public class JwtProvider {

    private static final String INSECURE_DEFAULT_SECRET = "change-this-development-secret-to-a-strong-32-byte-key";

    private final AppProperties appProperties;
    private final SecretKey signingKey;

    public JwtProvider(AppProperties appProperties) {
        this.appProperties = appProperties;
        this.signingKey = buildSigningKey(appProperties.getSecurity().getJwt().getSecret());
    }

    public String generateAccessToken(UUID userId, String loginId, String role) {
        Instant now = Instant.now();
        Instant expiresAt = now.plus(appProperties.getSecurity().getJwt().getAccessTokenTtl());

        return Jwts.builder()
            .issuer(appProperties.getSecurity().getJwt().getIssuer())
            .subject(userId.toString())
            .claims(Map.of(
                "loginId", loginId,
                "role", role
            ))
            .issuedAt(Date.from(now))
            .expiration(Date.from(expiresAt))
            .signWith(signingKey)
            .compact();
    }

    public JwtAuthenticatedUser parse(String token) {
        Claims claims = Jwts.parser()
            .verifyWith(signingKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();

        return new JwtAuthenticatedUser(
            UUID.fromString(claims.getSubject()),
            claims.get("loginId", String.class),
            claims.get("role", String.class)
        );
    }

    private SecretKey buildSigningKey(String configuredSecret) {
        String secret = configuredSecret == null ? "" : configuredSecret.trim();
        if (secret.isEmpty() || INSECURE_DEFAULT_SECRET.equals(secret)) {
            throw new IllegalStateException("APP_JWT_SECRET must be configured with a strong secret");
        }

        if (secret.matches("^[A-Za-z0-9+/=]+$") && secret.length() >= 44) {
            try {
                byte[] decoded = Decoders.BASE64.decode(secret);
                if (decoded.length >= 32) {
                    return Keys.hmacShaKeyFor(decoded);
                }
            } catch (IllegalArgumentException ignored) {
                // Fall back to raw bytes for plain text development secrets.
            }
        }

        byte[] rawBytes = secret.getBytes(StandardCharsets.UTF_8);
        if (rawBytes.length < 32) {
            throw new IllegalStateException("APP_JWT_SECRET must be at least 32 bytes long");
        }
        return Keys.hmacShaKeyFor(rawBytes);
    }
}
