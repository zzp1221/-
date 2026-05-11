package com.project.domain.conversation;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for conversation metadata.
 */
public interface QnaSessionRepository extends JpaRepository<QnaSession, UUID> {

    Optional<QnaSession> findByIdAndUserId(UUID id, UUID userId);

    @Query("""
        select session from QnaSession session
        where session.userId = :userId
        order by
            case when session.lastMessageAt is null then 1 else 0 end,
            session.lastMessageAt desc,
            session.updatedAt desc
        """)
    List<QnaSession> findRecentByUserId(UUID userId, Pageable pageable);
}
