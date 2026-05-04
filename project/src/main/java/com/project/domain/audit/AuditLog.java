package com.project.domain.audit;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Audit trail entry for control-plane security and business actions.
 */
@Entity
@Table(name = "audit_log", schema = "app")
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private UUID userId;

    @Column(name = "task_id")
    private UUID taskId;

    @Column(name = "event_category", nullable = false)
    private String eventCategory;

    @Column(name = "risk_level", nullable = false)
    private String riskLevel;

    @Column(nullable = false)
    private String message;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "payload_json", nullable = false)
    private Map<String, Object> payloadJson = new LinkedHashMap<>();

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public void setTaskId(UUID taskId) {
        this.taskId = taskId;
    }

    public void setEventCategory(String eventCategory) {
        this.eventCategory = eventCategory;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public void setPayloadJson(Map<String, Object> payloadJson) {
        this.payloadJson = payloadJson;
    }

    public Long getId() {
        return id;
    }

    public UUID getUserId() {
        return userId;
    }

    public UUID getTaskId() {
        return taskId;
    }

    public String getEventCategory() {
        return eventCategory;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public String getMessage() {
        return message;
    }

    public Map<String, Object> getPayloadJson() {
        return payloadJson;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    @PrePersist
    void onCreate() {
        this.createdAt = OffsetDateTime.now();
    }
}
