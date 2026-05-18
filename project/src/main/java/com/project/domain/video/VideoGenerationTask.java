package com.project.domain.video;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 教学视频生成任务的持久化快照。
 */
@Entity
@Table(name = "video_generation_task", schema = "rag")
public class VideoGenerationTask {

    @Id
    @Column(nullable = false, updatable = false)
    private UUID id;

    @Column(name = "task_id", unique = true)
    private UUID taskId;

    @Column(name = "resource_document_id")
    private UUID resourceDocumentId;

    @Column(name = "student_id", nullable = false)
    private UUID studentId;

    @Column(name = "trace_id", unique = true)
    private String traceId;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String topic;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "script_json", nullable = false)
    private Map<String, Object> scriptJson = new LinkedHashMap<>();

    @Column(name = "script_text", nullable = false)
    private String scriptText = "";

    @Column(nullable = false)
    private String status = "pending";

    @Column(name = "audio_path")
    private String audioPath;

    @Column(name = "avatar_video_path")
    private String avatarVideoPath;

    @Column(name = "animation_video_path")
    private String animationVideoPath;

    @Column(name = "final_video_path")
    private String finalVideoPath;

    @Column(name = "thumbnail_path")
    private String thumbnailPath;

    @Column(name = "active_provider")
    private String activeProvider;

    @Column(name = "fallback_provider")
    private String fallbackProvider;

    @Column(name = "tts_provider")
    private String ttsProvider;

    @Column(name = "avatar_provider")
    private String avatarProvider;

    @Column(name = "duration_seconds")
    private Integer durationSeconds;

    @Column(name = "video_style")
    private String videoStyle;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "generation_params", nullable = false)
    private Map<String, Object> generationParams = new LinkedHashMap<>();

    @Column(name = "critic_score", precision = 3, scale = 2)
    private BigDecimal criticScore;

    @Column(name = "safety_passed", nullable = false)
    private Boolean safetyPassed = Boolean.FALSE;

    @Column(name = "error_message")
    private String errorMessage;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;

    public UUID getId() {
        return id;
    }

    public UUID getTaskId() {
        return taskId;
    }

    public void setTaskId(UUID taskId) {
        this.taskId = taskId;
    }

    public UUID getResourceDocumentId() {
        return resourceDocumentId;
    }

    public void setResourceDocumentId(UUID resourceDocumentId) {
        this.resourceDocumentId = resourceDocumentId;
    }

    public UUID getStudentId() {
        return studentId;
    }

    public void setStudentId(UUID studentId) {
        this.studentId = studentId;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }

    public Map<String, Object> getScriptJson() {
        return scriptJson;
    }

    public void setScriptJson(Map<String, Object> scriptJson) {
        this.scriptJson = scriptJson;
    }

    public String getScriptText() {
        return scriptText;
    }

    public void setScriptText(String scriptText) {
        this.scriptText = scriptText;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getAudioPath() {
        return audioPath;
    }

    public void setAudioPath(String audioPath) {
        this.audioPath = audioPath;
    }

    public String getAvatarVideoPath() {
        return avatarVideoPath;
    }

    public void setAvatarVideoPath(String avatarVideoPath) {
        this.avatarVideoPath = avatarVideoPath;
    }

    public String getAnimationVideoPath() {
        return animationVideoPath;
    }

    public void setAnimationVideoPath(String animationVideoPath) {
        this.animationVideoPath = animationVideoPath;
    }

    public String getFinalVideoPath() {
        return finalVideoPath;
    }

    public void setFinalVideoPath(String finalVideoPath) {
        this.finalVideoPath = finalVideoPath;
    }

    public String getThumbnailPath() {
        return thumbnailPath;
    }

    public void setThumbnailPath(String thumbnailPath) {
        this.thumbnailPath = thumbnailPath;
    }

    public String getActiveProvider() {
        return activeProvider;
    }

    public void setActiveProvider(String activeProvider) {
        this.activeProvider = activeProvider;
    }

    public String getFallbackProvider() {
        return fallbackProvider;
    }

    public void setFallbackProvider(String fallbackProvider) {
        this.fallbackProvider = fallbackProvider;
    }

    public String getTtsProvider() {
        return ttsProvider;
    }

    public void setTtsProvider(String ttsProvider) {
        this.ttsProvider = ttsProvider;
    }

    public String getAvatarProvider() {
        return avatarProvider;
    }

    public void setAvatarProvider(String avatarProvider) {
        this.avatarProvider = avatarProvider;
    }

    public Integer getDurationSeconds() {
        return durationSeconds;
    }

    public void setDurationSeconds(Integer durationSeconds) {
        this.durationSeconds = durationSeconds;
    }

    public String getVideoStyle() {
        return videoStyle;
    }

    public void setVideoStyle(String videoStyle) {
        this.videoStyle = videoStyle;
    }

    public Map<String, Object> getGenerationParams() {
        return generationParams;
    }

    public void setGenerationParams(Map<String, Object> generationParams) {
        this.generationParams = generationParams;
    }

    public BigDecimal getCriticScore() {
        return criticScore;
    }

    public void setCriticScore(BigDecimal criticScore) {
        this.criticScore = criticScore;
    }

    public Boolean getSafetyPassed() {
        return safetyPassed;
    }

    public void setSafetyPassed(Boolean safetyPassed) {
        this.safetyPassed = safetyPassed;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public OffsetDateTime getUpdatedAt() {
        return updatedAt;
    }

    @PrePersist
    void onCreate() {
        OffsetDateTime now = OffsetDateTime.now();
        this.id = this.id == null ? UUID.randomUUID() : this.id;
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    void onUpdate() {
        this.updatedAt = OffsetDateTime.now();
    }
}
