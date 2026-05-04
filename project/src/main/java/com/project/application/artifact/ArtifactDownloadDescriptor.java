package com.project.application.artifact;

import java.time.OffsetDateTime;

/**
 * Public download metadata exposed after signing a sandbox artifact.
 */
public record ArtifactDownloadDescriptor(
    String downloadUrl,
    long expiresInSec,
    OffsetDateTime expiresAt
) {
}
