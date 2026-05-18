package com.project.application.idempotency;

import java.util.Optional;
import java.util.UUID;

/**
 * 幂等存储与预留端口。
 *
 * <p>该接口将编排层与底层存储引擎隔离，
 * 使得实现可在内存、Redis 或其他分布式协调后端之间切换，
 * 而无需更改业务工作流。</p>
 */
public interface IdempotencyService {

    Optional<UUID> findExisting(UUID userId, String operation, String idempotencyKey);

    boolean reserve(UUID userId, String operation, String idempotencyKey, UUID taskId);
}
