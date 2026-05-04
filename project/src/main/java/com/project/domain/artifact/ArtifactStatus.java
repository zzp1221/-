package com.project.domain.artifact;

/**
 * Lifecycle status of a generated artifact download token.
 */
public enum ArtifactStatus {
    READY,
    DOWNLOADED,
    EXPIRED,
    DELETED
}
