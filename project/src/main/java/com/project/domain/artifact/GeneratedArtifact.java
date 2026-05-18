package com.project.domain.artifact;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcType;
import org.hibernate.dialect.PostgreSQLEnumJdbcType;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * 控制平面签发的可下载沙箱产物。
 */
@Entity
@Table(name = "generated_artifact", schema = "app")
public class GeneratedArtifact {

    @Id
    @Column(nullable = false, updatable = false)
    private UUID id;

    @Column(name = "task_id", nullable = false)
    private UUID taskId;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Enumerated(EnumType.STRING)
    @JdbcType(PostgreSQLEnumJdbcType.class)
    @Column(name = "resource_type", nullable = false, columnDefinition = "app.resource_type")
    private ResourceType resourceType;

    @Column(nullable = false)
    private String title;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Column(name = "mime_type")
    private String mimeType;

    @Column(name = "sandbox_path", nullable = false)
    private String sandboxPath;

    @Column(name = "size_bytes")
    private Long sizeBytes;

    @Column(name = "download_token", nullable = false, unique = true)
    private String downloadToken;

    @Column(name = "expires_at", nullable = false)
    private OffsetDateTime expiresAt;

    @Column(name = "download_count", nullable = false)
    private Integer downloadCount = 0;

    @Enumerated(EnumType.STRING)
    @Column(name = "artifact_status", nullable = false)
    private ArtifactStatus artifactStatus = ArtifactStatus.READY;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    public UUID getId() {
        return id;
    }

    public UUID getTaskId() {
        return taskId;
    }

    public void setTaskId(UUID taskId) {
        this.taskId = taskId;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public ResourceType getResourceType() {
        return resourceType;
    }

    public void setResourceType(ResourceType resourceType) {
        this.resourceType = resourceType;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getMimeType() {
        return mimeType;
    }

    public void setMimeType(String mimeType) {
        this.mimeType = mimeType;
    }

    public String getSandboxPath() {
        return sandboxPath;
    }

    public void setSandboxPath(String sandboxPath) {
        this.sandboxPath = sandboxPath;
    }

    public Long getSizeBytes() {
        return sizeBytes;
    }

    public void setSizeBytes(Long sizeBytes) {
        this.sizeBytes = sizeBytes;
    }

    public String getDownloadToken() {
        return downloadToken;
    }

    public void setDownloadToken(String downloadToken) {
        this.downloadToken = downloadToken;
    }

    public OffsetDateTime getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(OffsetDateTime expiresAt) {
        this.expiresAt = expiresAt;
    }

    public Integer getDownloadCount() {
        return downloadCount;
    }

    public void setDownloadCount(Integer downloadCount) {
        this.downloadCount = downloadCount;
    }

    public ArtifactStatus getArtifactStatus() {
        return artifactStatus;
    }

    public void setArtifactStatus(ArtifactStatus artifactStatus) {
        this.artifactStatus = artifactStatus;
    }

    @PrePersist
    void onCreate() {
        this.id = this.id == null ? UUID.randomUUID() : this.id;
        this.createdAt = OffsetDateTime.now();
    }
}
