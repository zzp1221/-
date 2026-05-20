package com.project.application.conversation;

import com.project.api.conversation.dto.UploadedImageResponse;
import com.project.application.common.ApplicationException;
import com.project.config.AppProperties;
import com.project.security.JwtAuthenticatedUser;
import com.project.security.JwtProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;

/**
 * 处理聊天图片上传及用于多模态分析的签名公开读取 URL。
 */
@Service
public class ConversationImageService {

    private static final Logger LOGGER = LoggerFactory.getLogger(ConversationImageService.class);

    private static final Set<String> ALLOWED_CONTENT_TYPES = Set.of(
        "image/jpeg",
        "image/png",
        "image/webp"
    );
    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(".jpg", ".jpeg", ".png", ".webp");

    private final AppProperties appProperties;
    private final JwtProvider jwtProvider;

    public ConversationImageService(
        AppProperties appProperties,
        JwtProvider jwtProvider
    ) {
        this.appProperties = appProperties;
        this.jwtProvider = jwtProvider;
    }

    public UploadedImageResponse uploadChatImage(JwtAuthenticatedUser currentUser, MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new ApplicationException("IMAGE_EMPTY", "请先选择要上传的图片", HttpStatus.BAD_REQUEST);
        }
        long size = file.getSize();
        if (size <= 0) {
            throw new ApplicationException("IMAGE_EMPTY", "图片内容为空，请重新选择", HttpStatus.BAD_REQUEST);
        }
        if (size > appProperties.getUpload().getImageMaxBytes()) {
            throw new ApplicationException("IMAGE_TOO_LARGE", "图片不能超过 10MB", HttpStatus.BAD_REQUEST);
        }

        String originalName = file.getOriginalFilename() == null ? "" : file.getOriginalFilename().trim();
        String extension = resolveExtension(originalName);
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new ApplicationException("IMAGE_FORMAT_UNSUPPORTED", "仅支持 jpg、png、webp 图片", HttpStatus.BAD_REQUEST);
        }

        String contentType = normalizeContentType(file.getContentType(), extension);
        if (!ALLOWED_CONTENT_TYPES.contains(contentType)) {
            throw new ApplicationException("IMAGE_FORMAT_UNSUPPORTED", "仅支持 jpg、png、webp 图片", HttpStatus.BAD_REQUEST);
        }

        Path storageDir = Path.of(appProperties.getUpload().getImageStorageDir()).toAbsolutePath().normalize();
        Path userDir = storageDir.resolve(currentUser.userId().toString());
        UUID imageId = UUID.randomUUID();
        String fileName = imageId + extension;
        Path targetPath = userDir.resolve(fileName).normalize();
        if (!targetPath.startsWith(storageDir)) {
            throw new ApplicationException("IMAGE_PATH_INVALID", "图片存储路径无效", HttpStatus.BAD_REQUEST);
        }

        try {
            Files.createDirectories(userDir);
            try (InputStream inputStream = file.getInputStream()) {
                Files.copy(inputStream, targetPath, StandardCopyOption.REPLACE_EXISTING);
            }
        } catch (IOException ex) {
            throw new ApplicationException("IMAGE_UPLOAD_FAILED", "图片上传失败，请稍后重试", HttpStatus.INTERNAL_SERVER_ERROR);
        }

        return new UploadedImageResponse(
            buildImageUrl(currentUser.userId(), imageId, extension),
            originalName.isBlank() ? fileName : originalName,
            size,
            contentType
        );
    }

    public ResolvedImage resolvePublicImage(String token) {
        ParsedImageToken parsed = parseImageToken(token);
        Path path = resolveStoredPath(parsed.userId(), parsed.imageId(), parsed.extension());
        if (!Files.exists(path)) {
            throw new ApplicationException("IMAGE_NOT_FOUND", "图片不存在或已失效", HttpStatus.NOT_FOUND);
        }
        return new ResolvedImage(path, MediaType.parseMediaType(normalizeContentType(null, parsed.extension())));
    }

    @Scheduled(fixedDelay = 300_000, initialDelay = 300_000)
    public void cleanupExpiredImages() {
        cleanupExpiredImages(Instant.now());
    }

    void cleanupExpiredImages(Instant now) {
        Path storageDir = Path.of(appProperties.getUpload().getImageStorageDir()).toAbsolutePath().normalize();
        if (!Files.exists(storageDir)) {
            return;
        }
        if (!Files.isDirectory(storageDir, LinkOption.NOFOLLOW_LINKS)) {
            LOGGER.warn("Conversation image storage path is not a directory: {}", storageDir);
            return;
        }

        Instant cutoff = now.minusSeconds(appProperties.getUpload().getImageTokenTtlSeconds());
        try (Stream<Path> userDirs = Files.list(storageDir)) {
            userDirs
                .filter(path -> Files.isDirectory(path, LinkOption.NOFOLLOW_LINKS))
                .forEach(userDir -> cleanupUserImageDirectory(userDir, cutoff));
        } catch (IOException ex) {
            LOGGER.warn("Conversation image cleanup failed for {}", storageDir, ex);
        }
    }

    private void cleanupUserImageDirectory(Path userDir, Instant cutoff) {
        try (Stream<Path> entries = Files.list(userDir)) {
            entries
                .filter(path -> Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS))
                .filter(this::isAllowedImageFile)
                .forEach(file -> deleteIfExpired(file, cutoff));
        } catch (IOException ex) {
            LOGGER.warn("Conversation image cleanup failed for {}", userDir, ex);
            return;
        }

        try (Stream<Path> remaining = Files.list(userDir)) {
            if (remaining.findAny().isEmpty()) {
                Files.deleteIfExists(userDir);
            }
        } catch (IOException ex) {
            LOGGER.warn("Conversation image directory cleanup failed for {}", userDir, ex);
        }
    }

    private void deleteIfExpired(Path file, Instant cutoff) {
        try {
            if (Files.getLastModifiedTime(file, LinkOption.NOFOLLOW_LINKS).toInstant().isBefore(cutoff)) {
                Files.deleteIfExists(file);
            }
        } catch (IOException ex) {
            LOGGER.warn("Failed to delete expired conversation image {}", file, ex);
        }
    }

    private boolean isAllowedImageFile(Path file) {
        return ALLOWED_EXTENSIONS.contains(resolveExtension(file.getFileName().toString()));
    }

    private String buildImageUrl(UUID userId, UUID imageId, String extension) {
        Instant expiresAt = Instant.now().plusSeconds(appProperties.getUpload().getImageTokenTtlSeconds());
        String token = jwtProvider.issueToken(
            imageId.toString(),
            Map.of(
                "userId", userId.toString(),
                "kind", "conversation_image",
                "ext", extension
            ),
            expiresAt
        );
        return "/api/conversations/images/" + token;
    }

    private ParsedImageToken parseImageToken(String token) {
        try {
            var claims = jwtProvider.parseClaims(token);
            if (!"conversation_image".equals(claims.get("kind", String.class))) {
                throw new ApplicationException("IMAGE_TOKEN_INVALID", "图片链接无效", HttpStatus.FORBIDDEN);
            }
            return new ParsedImageToken(
                UUID.fromString(claims.get("userId", String.class)),
                UUID.fromString(claims.getSubject()),
                claims.get("ext", String.class)
            );
        } catch (ApplicationException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new ApplicationException("IMAGE_TOKEN_INVALID", "图片链接无效", HttpStatus.FORBIDDEN);
        }
    }

    private Path resolveStoredPath(UUID userId, UUID imageId, String extension) {
        Path storageDir = Path.of(appProperties.getUpload().getImageStorageDir()).toAbsolutePath().normalize();
        Path resolved = storageDir.resolve(userId.toString()).resolve(imageId + extension).normalize();
        if (!resolved.startsWith(storageDir)) {
            throw new ApplicationException("IMAGE_PATH_INVALID", "图片路径无效", HttpStatus.BAD_REQUEST);
        }
        return resolved;
    }

    private String resolveExtension(String fileName) {
        String lower = fileName.toLowerCase();
        for (String extension : ALLOWED_EXTENSIONS) {
            if (lower.endsWith(extension)) {
                return extension;
            }
        }
        return "";
    }

    private String normalizeContentType(String contentType, String extension) {
        if (contentType != null && ALLOWED_CONTENT_TYPES.contains(contentType.trim().toLowerCase())) {
            return contentType.trim().toLowerCase();
        }
        return switch (extension) {
            case ".jpg", ".jpeg" -> "image/jpeg";
            case ".png" -> "image/png";
            case ".webp" -> "image/webp";
            default -> "";
        };
    }

    public record ResolvedImage(Path path, MediaType mediaType) {
    }

    private record ParsedImageToken(UUID userId, UUID imageId, String extension) {
    }
}
