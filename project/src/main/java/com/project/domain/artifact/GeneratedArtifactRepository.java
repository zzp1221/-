package com.project.domain.artifact;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

/**
 * 生成产物令牌仓库。
 */
public interface GeneratedArtifactRepository extends JpaRepository<GeneratedArtifact, UUID> {

    Optional<GeneratedArtifact> findByDownloadToken(String downloadToken);
}
