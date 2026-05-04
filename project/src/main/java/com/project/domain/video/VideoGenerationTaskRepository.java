package com.project.domain.video;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

/**
 * Repository for persisted video-generation task snapshots.
 */
public interface VideoGenerationTaskRepository extends JpaRepository<VideoGenerationTask, UUID> {

    Optional<VideoGenerationTask> findByTaskId(UUID taskId);
}
