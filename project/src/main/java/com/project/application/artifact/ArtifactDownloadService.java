package com.project.application.artifact;

import com.project.application.audit.AuditService;
import com.project.application.common.ApplicationException;
import com.project.config.AppProperties;
import com.project.domain.artifact.ArtifactStatus;
import com.project.domain.artifact.GeneratedArtifact;
import com.project.domain.artifact.GeneratedArtifactRepository;
import com.project.domain.artifact.ResourceType;
import com.project.domain.task.SmartEngineTask;
import com.project.security.JwtAuthenticatedUser;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.ContentDisposition;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.UUID;

/**
 * Signs, resolves, and serves sandbox-generated artifacts.
 */
@Service
public class ArtifactDownloadService {

    private final GeneratedArtifactRepository generatedArtifactRepository;
    private final AppProperties appProperties;
    private final AuditService auditService;

    public ArtifactDownloadService(
        GeneratedArtifactRepository generatedArtifactRepository,
        AppProperties appProperties,
        AuditService auditService
    ) {
        this.generatedArtifactRepository = generatedArtifactRepository;
        this.appProperties = appProperties;
        this.auditService = auditService;
    }

    @Transactional
    public ArtifactDownloadDescriptor issueDownload(
        SmartEngineTask task,
        ResourceType resourceType,
        String title,
        String fileName,
        String sandboxPath,
        String mimeType
    ) {
        Path path = Path.of(sandboxPath);
        if (!Files.exists(path)) {
            throw new ApplicationException("ARTIFACT_NOT_FOUND", "生成文件不存在", HttpStatus.NOT_FOUND);
        }

        GeneratedArtifact artifact = new GeneratedArtifact();
        artifact.setTaskId(task.getId());
        artifact.setUserId(task.getUserId());
        artifact.setResourceType(resourceType);
        artifact.setTitle(title);
        artifact.setFileName(fileName);
        artifact.setMimeType(mimeType);
        artifact.setSandboxPath(sandboxPath);
        try {
            artifact.setSizeBytes(Files.size(path));
        } catch (Exception ignored) {
            artifact.setSizeBytes(null);
        }
        artifact.setDownloadToken(UUID.randomUUID().toString().replace("-", ""));
        artifact.setExpiresAt(OffsetDateTime.now().plusSeconds(appProperties.getDownload().getArtifactTtlSeconds()));

        GeneratedArtifact savedArtifact = generatedArtifactRepository.save(artifact);
        String url = "/api/assets/download/" + savedArtifact.getDownloadToken();

        auditService.log(
            "DOWNLOAD",
            "INFO",
            "签发下载链接",
            task.getUserId(),
            task.getId(),
            Map.of("fileName", fileName, "downloadUrl", url)
        );

        return new ArtifactDownloadDescriptor(url, appProperties.getDownload().getArtifactTtlSeconds(), savedArtifact.getExpiresAt());
    }

    @Transactional
    public ResponseEntity<Resource> download(JwtAuthenticatedUser currentUser, String token) {
        GeneratedArtifact artifact = generatedArtifactRepository.findByDownloadToken(token)
            .orElseThrow(() -> new ApplicationException("ARTIFACT_NOT_FOUND", "下载资源不存在", HttpStatus.NOT_FOUND));

        if (!artifact.getUserId().equals(currentUser.userId())) {
            throw new ApplicationException("FORBIDDEN", "无权下载该资源", HttpStatus.FORBIDDEN);
        }

        if (artifact.getExpiresAt().isBefore(OffsetDateTime.now())) {
            artifact.setArtifactStatus(ArtifactStatus.EXPIRED);
            generatedArtifactRepository.save(artifact);
            throw new ApplicationException("ARTIFACT_EXPIRED", "下载链接已过期", HttpStatus.FORBIDDEN);
        }

        Path path = Path.of(artifact.getSandboxPath());
        if (!Files.exists(path)) {
            throw new ApplicationException("ARTIFACT_NOT_FOUND", "下载资源不存在", HttpStatus.NOT_FOUND);
        }

        artifact.setDownloadCount(artifact.getDownloadCount() + 1);
        artifact.setArtifactStatus(ArtifactStatus.DOWNLOADED);
        auditService.log("DOWNLOAD", "INFO", "下载资源", currentUser.userId(), artifact.getTaskId(), Map.of("fileName", artifact.getFileName()));

        FileSystemResource resource = new FileSystemResource(path);
        MediaType mediaType = artifact.getMimeType() == null || artifact.getMimeType().isBlank()
            ? MediaType.APPLICATION_OCTET_STREAM
            : MediaType.parseMediaType(artifact.getMimeType());

        return ResponseEntity.ok()
            .contentType(mediaType)
            .header(
                "Content-Disposition",
                ContentDisposition.attachment().filename(artifact.getFileName()).build().toString()
            )
            .contentLength(resolveContentLength(resource))
            .body(resource);
    }

    private long resolveContentLength(FileSystemResource resource) {
        try {
            return resource.contentLength();
        } catch (Exception ex) {
            return -1;
        }
    }
}
