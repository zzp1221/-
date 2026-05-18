package com.project.api.conversation;

import com.project.api.conversation.dto.ConversationMessageStreamRequest;
import com.project.api.conversation.dto.ConversationHistoryItemResponse;
import com.project.api.conversation.dto.ConversationMessageItemResponse;
import com.project.api.conversation.dto.CreateConversationResponse;
import com.project.api.conversation.dto.UploadedImageResponse;
import com.project.application.common.ApplicationException;
import com.project.application.conversation.ConversationImageService;
import com.project.application.conversation.ConversationService;
import com.project.security.AuthenticatedUserResolver;
import com.project.security.JwtAuthenticatedUser;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

/**
 * 辅导式对话流程的会话端点。
 */
@RestController
@RequestMapping("/api/conversations")
@Tag(name = "Conversations")
public class ConversationController {

    private final ConversationService conversationService;
    private final ConversationImageService conversationImageService;

    public ConversationController(
        ConversationService conversationService,
        ConversationImageService conversationImageService
    ) {
        this.conversationService = conversationService;
        this.conversationImageService = conversationImageService;
    }

    @PostMapping
    @Operation(summary = "Create a new conversation")
    public ResponseEntity<CreateConversationResponse> createConversation(Authentication authentication) {
        return ResponseEntity.ok(
            conversationService.createConversation(AuthenticatedUserResolver.require(authentication))
        );
    }

    @GetMapping
    @Operation(summary = "List recent conversations")
    public ResponseEntity<List<ConversationHistoryItemResponse>> listRecentConversations(
        Authentication authentication,
        @RequestParam(required = false) Integer page,
        @RequestParam(required = false) Integer size
    ) {
        return ResponseEntity.ok(
            conversationService.listRecentConversations(AuthenticatedUserResolver.require(authentication), page, size)
        );
    }

    @GetMapping("/{conversationId}/messages")
    @Operation(summary = "List persisted conversation messages")
    public ResponseEntity<List<ConversationMessageItemResponse>> listConversationMessages(
        Authentication authentication,
        @PathVariable UUID conversationId,
        @RequestParam(required = false) Integer page,
        @RequestParam(required = false) Integer size
    ) {
        JwtAuthenticatedUser principal = AuthenticatedUserResolver.require(authentication);
        return ResponseEntity.ok(conversationService.listConversationMessages(principal, conversationId, page, size));
    }

    @PostMapping(path = "/{conversationId}/messages/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @Operation(summary = "Send a message and receive streaming tutor replies")
    public SseEmitter streamMessage(
        Authentication authentication,
        @PathVariable UUID conversationId,
        @Valid @RequestBody ConversationMessageStreamRequest request
    ) {
        return conversationService.streamMessage(
            AuthenticatedUserResolver.require(authentication),
            conversationId,
            request
        );
    }

    @PostMapping(path = "/images/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload an image used in conversation Q&A")
    public ResponseEntity<UploadedImageResponse> uploadConversationImage(
        Authentication authentication,
        @RequestPart("file") MultipartFile file
    ) {
        return ResponseEntity.ok(
            conversationImageService.uploadChatImage(AuthenticatedUserResolver.require(authentication), file)
        );
    }

    @GetMapping("/images/{token}")
    @Operation(summary = "Resolve a signed public conversation image for multimodal analysis")
    public ResponseEntity<Resource> resolveConversationImage(@PathVariable String token) {
        ConversationImageService.ResolvedImage image = conversationImageService.resolvePublicImage(token);
        if (!image.path().toFile().exists()) {
            throw new ApplicationException("IMAGE_NOT_FOUND", "图片不存在或已失效", HttpStatus.NOT_FOUND);
        }
        return ResponseEntity.ok()
            .header(HttpHeaders.CACHE_CONTROL, "private, max-age=300")
            .contentType(image.mediaType())
            .body(new FileSystemResource(image.path()));
    }
}
