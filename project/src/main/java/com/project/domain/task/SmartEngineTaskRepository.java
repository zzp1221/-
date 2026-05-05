package com.project.domain.task;

import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;
import java.util.UUID;

/**
 * Repository for task lifecycle persistence.
 */
public interface SmartEngineTaskRepository extends JpaRepository<SmartEngineTask, UUID> {

    Optional<SmartEngineTask> findByIdAndUserId(UUID id, UUID userId);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT t FROM SmartEngineTask t WHERE t.id = :id")
    Optional<SmartEngineTask> findWithLockById(@Param("id") UUID id);
}
