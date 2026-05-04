package com.project.domain.profile;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

/**
 * Repository for current user profiles.
 */
public interface UserProfileCurrentRepository extends JpaRepository<UserProfileCurrent, UUID> {
}
