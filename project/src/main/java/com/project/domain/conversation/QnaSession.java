package com.project.domain.conversation;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcType;
import org.hibernate.dialect.PostgreSQLEnumJdbcType;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Conversation metadata owned by the Java control plane.
 *
 * <p>Only lightweight session metadata is stored here. Full message bodies and
 * compaction summaries remain in the Python runtime per the architecture
 * boundary defined in the project documents.</p>
 */
@Entity
@Table(name = "qna_session", schema = "app")
public class QnaSession {

    @Id
    @Column(nullable = false, updatable = false)
    private UUID id;

    @Column(name = "user_id", nullable = false, updatable = false)
    private UUID userId;

    @Column(nullable = false)
    private String title = "新对话";

    @Column(name = "mongo_thread_id", nullable = false, unique = true)
    private String mongoThreadId;

    @Column(name = "entry_source", nullable = false)
    private String entrySource = "NEW_CONVERSATION";

    @Enumerated(EnumType.STRING)
    @JdbcType(PostgreSQLEnumJdbcType.class)
    @Column(name = "current_mode", nullable = false, columnDefinition = "app.conversation_mode")
    private ConversationMode currentMode = ConversationMode.QNA;

    @Column(name = "last_message_at")
    private OffsetDateTime lastMessageAt;

    @Column(name = "last_message_preview")
    private String lastMessagePreview;

    @Column(name = "message_count", nullable = false)
    private Integer messageCount = 0;

    @Column(name = "active_profile_version", nullable = false)
    private Integer activeProfileVersion = 0;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;

    public UUID getId() {
        return id;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getMongoThreadId() {
        return mongoThreadId;
    }

    public void setMongoThreadId(String mongoThreadId) {
        this.mongoThreadId = mongoThreadId;
    }

    public String getEntrySource() {
        return entrySource;
    }

    public void setEntrySource(String entrySource) {
        this.entrySource = entrySource;
    }

    public ConversationMode getCurrentMode() {
        return currentMode;
    }

    public void setCurrentMode(ConversationMode currentMode) {
        this.currentMode = currentMode;
    }

    public OffsetDateTime getLastMessageAt() {
        return lastMessageAt;
    }

    public void setLastMessageAt(OffsetDateTime lastMessageAt) {
        this.lastMessageAt = lastMessageAt;
    }

    public String getLastMessagePreview() {
        return lastMessagePreview;
    }

    public void setLastMessagePreview(String lastMessagePreview) {
        this.lastMessagePreview = lastMessagePreview;
    }

    public Integer getMessageCount() {
        return messageCount;
    }

    public void setMessageCount(Integer messageCount) {
        this.messageCount = messageCount;
    }

    public Integer getActiveProfileVersion() {
        return activeProfileVersion;
    }

    public void setActiveProfileVersion(Integer activeProfileVersion) {
        this.activeProfileVersion = activeProfileVersion;
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
