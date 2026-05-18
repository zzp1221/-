package com.project.domain.video;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

/**
 * 视频生成任务快照持久化仓库。
 */
public interface VideoGenerationTaskRepository extends JpaRepository<VideoGenerationTask, UUID> {

    Optional<VideoGenerationTask> findByTaskId(UUID taskId);
}
