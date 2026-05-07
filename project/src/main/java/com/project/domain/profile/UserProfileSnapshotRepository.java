package com.project.domain.profile;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

/**
 * Repository for historical user profile snapshots.
 */
public interface UserProfileSnapshotRepository extends JpaRepository<UserProfileSnapshot, UUID> {

    List<UserProfileSnapshot> findTop8ByUserIdOrderByVersionDesc(UUID userId);
}
