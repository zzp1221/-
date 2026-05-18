package com.project.domain.task;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 智学引擎任务执行过程中发出的持久化事件。
 */
@Entity
@Table(name = "smart_engine_task_event", schema = "app")
public class SmartEngineTaskEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "task_id", nullable = false)
    private SmartEngineTask task;

    @Column(name = "event_seq", nullable = false)
    private Integer eventSeq;

    @Column(name = "event_type", nullable = false)
    private String eventType;

    @Column(name = "stage_name")
    private String stageName;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "event_payload", nullable = false)
    private Map<String, Object> eventPayload = new LinkedHashMap<>();

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    public Long getId() {
        return id;
    }

    public SmartEngineTask getTask() {
        return task;
    }

    public void setTask(SmartEngineTask task) {
        this.task = task;
    }

    public Integer getEventSeq() {
        return eventSeq;
    }

    public void setEventSeq(Integer eventSeq) {
        this.eventSeq = eventSeq;
    }

    public String getEventType() {
        return eventType;
    }

    public void setEventType(String eventType) {
        this.eventType = eventType;
    }

    public String getStageName() {
        return stageName;
    }

    public void setStageName(String stageName) {
        this.stageName = stageName;
    }

    public Map<String, Object> getEventPayload() {
        return eventPayload;
    }

    public void setEventPayload(Map<String, Object> eventPayload) {
        this.eventPayload = eventPayload;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    @PrePersist
    void onCreate() {
        this.createdAt = OffsetDateTime.now();
    }
}
