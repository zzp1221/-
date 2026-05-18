package com.project.application.audit;

import com.project.domain.audit.AuditLog;
import com.project.domain.audit.AuditLogRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 面向安全敏感与可追溯操作的集中式审计服务。
 */
@Service
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    public AuditService(AuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    @Transactional
    public void log(String category, String riskLevel, String message, UUID userId, UUID taskId, Map<String, Object> payload) {
        AuditLog auditLog = new AuditLog();
        auditLog.setEventCategory(category);
        auditLog.setRiskLevel(riskLevel);
        auditLog.setMessage(message);
        auditLog.setUserId(userId);
        auditLog.setTaskId(taskId);
        auditLog.setPayloadJson(payload == null ? new LinkedHashMap<>() : new LinkedHashMap<>(payload));
        auditLogRepository.save(auditLog);
    }
}
