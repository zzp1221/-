package com.project.domain.profile;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

/**
 * 当前用户画像仓库。
 */
public interface UserProfileCurrentRepository extends JpaRepository<UserProfileCurrent, UUID> {
}
