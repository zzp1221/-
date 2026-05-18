package com.project.application.artifact;

import java.time.OffsetDateTime;

/**
 * 签名沙箱制品后暴露的公开下载元数据。
 */
public record ArtifactDownloadDescriptor(
    String downloadUrl,
    long expiresInSec,
    OffsetDateTime expiresAt
) {
}
