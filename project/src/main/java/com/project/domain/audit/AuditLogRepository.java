package com.project.domain.audit;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 审计日志持久化仓库。
 */
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {
}
