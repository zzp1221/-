package com.project.application.idempotency;

import java.util.Optional;
import java.util.UUID;

/**
 * Port for idempotency storage and reservation.
 *
 * <p>The interface isolates the orchestration layer from the underlying storage
 * engine so the implementation can move between in-memory, Redis, or other
 * distributed coordination backends without changing business workflows.</p>
 */
public interface IdempotencyService {

    Optional<UUID> findExisting(UUID userId, String operation, String idempotencyKey);

    boolean reserve(UUID userId, String operation, String idempotencyKey, UUID taskId);
}
