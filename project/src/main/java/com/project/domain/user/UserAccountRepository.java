package com.project.domain.user;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

/**
 * 用户认证查询的仓库抽象。
 */
public interface UserAccountRepository extends JpaRepository<UserAccount, UUID> {

    boolean existsByLoginId(String loginId);

    Optional<UserAccount> findByLoginId(String loginId);
}
