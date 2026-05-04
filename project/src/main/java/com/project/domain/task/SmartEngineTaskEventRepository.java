package com.project.domain.task;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

/**
 * Repository for persisted smart-engine events.
 */
public interface SmartEngineTaskEventRepository extends JpaRepository<SmartEngineTaskEvent, Long> {

    List<SmartEngineTaskEvent> findByTaskIdOrderByEventSeqAsc(UUID taskId);

    int countByTaskId(UUID taskId);
}
