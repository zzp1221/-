package com.project.domain.audit;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Repository for persisted audit logs.
 */
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {
}
