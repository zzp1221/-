package com.project.domain.artifact;

/**
 * 生成产物下载令牌的生命周期状态。
 */
public enum ArtifactStatus {
    READY,
    DOWNLOADED,
    EXPIRED,
    DELETED
}
