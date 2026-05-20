package com.project.domain.task;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * 智学引擎事件持久化仓库。
 */
public interface SmartEngineTaskEventRepository extends JpaRepository<SmartEngineTaskEvent, Long> {

    List<SmartEngineTaskEvent> findByTaskIdOrderByEventSeqAsc(UUID taskId);

    Optional<SmartEngineTaskEvent> findByTaskIdAndEventSeq(UUID taskId, Integer eventSeq);

    int countByTaskId(UUID taskId);
}
