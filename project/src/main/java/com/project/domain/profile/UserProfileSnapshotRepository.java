package com.project.domain.profile;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

/**
 * 用户画像历史快照仓库。
 */
public interface UserProfileSnapshotRepository extends JpaRepository<UserProfileSnapshot, UUID> {

    List<UserProfileSnapshot> findTop8ByUserIdOrderByVersionDesc(UUID userId);
}
