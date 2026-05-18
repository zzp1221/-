package com.project.api.artifact;

import com.project.application.artifact.ArtifactDownloadService;
import com.project.security.AuthenticatedUserResolver;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 沙箱生成产物的下载端点。
 */
@RestController
@RequestMapping("/api/assets")
@Tag(name = "Artifacts")
public class ArtifactController {

    private final ArtifactDownloadService artifactDownloadService;

    public ArtifactController(ArtifactDownloadService artifactDownloadService) {
        this.artifactDownloadService = artifactDownloadService;
    }

    @GetMapping("/download/{token}")
    @Operation(summary = "Download a signed sandbox artifact")
    public ResponseEntity<Resource> download(Authentication authentication, @PathVariable String token) {
        return artifactDownloadService.download(AuthenticatedUserResolver.require(authentication), token);
    }
}
