package com.project.application.conversation;

import com.project.api.conversation.dto.ConversationMessageStreamRequest;
import com.project.api.conversation.dto.ConversationHistoryItemResponse;
import com.project.api.conversation.dto.ConversationMessageItemResponse;
import com.project.api.conversation.dto.CreateConversationResponse;
import com.project.application.common.ApplicationException;
import com.project.application.smartengine.PythonAgentClient;
import com.project.application.smartengine.PythonStreamEvent;
import com.project.application.smartengine.SmartEngineInvocation;
import com.project.domain.conversation.ConversationMode;
import com.project.domain.conversation.QnaSession;
import com.project.domain.conversation.QnaSessionRepository;
import com.project.domain.profile.UserProfileCurrentRepository;
import com.project.security.JwtAuthenticatedUser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Manages conversation metadata and streaming message forwarding.
 */
@Service
public class ConversationService {

    private static final long DEFAULT_TIMEOUT_MS = 0L;
    private static final Logger LOGGER = LoggerFactory.getLogger(ConversationService.class);

    private final QnaSessionRepository qnaSessionRepository;
    private final PythonAgentClient pythonAgentClient;
    private final PythonConversationMessageClient pythonConversationMessageClient;
    private final TaskExecutor smartEngineTaskExecutor;
    private final UserProfileCurrentRepository userProfileCurrentRepository;

    public ConversationService(
        QnaSessionRepository qnaSessionRepository,
        PythonAgentClient pythonAgentClient,
        PythonConversationMessageClient pythonConversationMessageClient,
        TaskExecutor smartEngineTaskExecutor,
        UserProfileCurrentRepository userProfileCurrentRepository
    ) {
        this.qnaSessionRepository = qnaSessionRepository;
        this.pythonAgentClient = pythonAgentClient;
        this.pythonConversationMessageClient = pythonConversationMessageClient;
        this.smartEngineTaskExecutor = smartEngineTaskExecutor;
        this.userProfileCurrentRepository = userProfileCurrentRepository;
    }

    @Transactional
    public CreateConversationResponse createConversation(JwtAuthenticatedUser currentUser) {
        QnaSession session = new QnaSession();
        session.setUserId(currentUser.userId());
        session.setTitle("新对话");
        session.setMongoThreadId("mongo-thread-" + UUID.randomUUID());
        session.setEntrySource("NEW_CONVERSATION");
        session.setCurrentMode(ConversationMode.QNA);

        QnaSession saved = qnaSessionRepository.save(session);
        return new CreateConversationResponse(saved.getId(), saved.getTitle());
    }

    @Transactional(readOnly = true)
    public List<ConversationHistoryItemResponse> listRecentConversations(JwtAuthenticatedUser currentUser) {
        return qnaSessionRepository.findRecentByUserId(currentUser.userId()).stream()
            .limit(12)
            .map(session -> new ConversationHistoryItemResponse(
                session.getId(),
                resolveConversationTitle(session),
                session.getLastMessagePreview(),
                session.getMessageCount(),
                session.getLastMessageAt(),
                session.getUpdatedAt()
            ))
            .toList();
    }

    @Transactional(readOnly = true)
    public List<ConversationMessageItemResponse> listConversationMessages(JwtAuthenticatedUser currentUser, UUID conversationId) {
        qnaSessionRepository.findByIdAndUserId(conversationId, currentUser.userId())
            .orElseThrow(() -> new ApplicationException("CONVERSATION_NOT_FOUND", "会话不存在", HttpStatus.NOT_FOUND));
        return pythonConversationMessageClient.listMessages(conversationId, currentUser.userId());
    }

    private static final int MAX_HISTORY_MESSAGES = 20;

    @Transactional
    public SseEmitter streamMessage(
        JwtAuthenticatedUser currentUser,
        UUID conversationId,
        ConversationMessageStreamRequest request
    ) {
        QnaSession session = qnaSessionRepository.findByIdAndUserId(conversationId, currentUser.userId())
            .orElseThrow(() -> new ApplicationException("CONVERSATION_NOT_FOUND", "会话不存在", HttpStatus.NOT_FOUND));

        session.setLastMessageAt(OffsetDateTime.now());
        session.setLastMessagePreview(truncate(request.message(), 120));
        session.setMessageCount(session.getMessageCount() + 1);
        if (session.getMessageCount() <= 1 || session.getTitle() == null || session.getTitle().isBlank() || "新对话".equals(session.getTitle())) {
            session.setTitle(buildConversationTitle(request.message()));
        }
        appendConversationMessage(conversationId, currentUser.userId(), "user", request.message(), true);

        // Fetch conversation history for multi-turn memory
        List<ConversationMessageItemResponse> history = fetchRecentHistory(conversationId, currentUser.userId());

        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT_MS);
        emitter.onCompletion(() -> LOGGER.debug("Conversation SSE emitter completed conversationId={}", conversationId));
        emitter.onTimeout(() -> LOGGER.debug("Conversation SSE emitter timed out conversationId={}", conversationId));
        emitter.onError(ex -> LOGGER.debug("Conversation SSE emitter error conversationId={}", conversationId, ex));
        AtomicInteger sequence = new AtomicInteger(0);
        StringBuilder assistantReply = new StringBuilder();

        smartEngineTaskExecutor.execute(() -> {
            try {
                pythonAgentClient.stream(
                    new SmartEngineInvocation(
                        currentUser.userId(),
                        UUID.randomUUID(),
                        UUID.randomUUID().toString(),
                        conversationId,
                        request.resolvedServiceType(),
                        buildConversationParams(currentUser, conversationId, request, history)
                    ),
                    event -> {
                        collectAssistantReply(assistantReply, event);
                        sendConversationEvent(emitter, conversationId, sequence, event);
                    }
                );
                appendConversationMessage(conversationId, currentUser.userId(), "assistant", assistantReply.toString(), false);
                emitter.complete();
            } catch (Exception ex) {
                try {
                    if (assistantReply.isEmpty()) {
                        appendConversationMessage(conversationId, currentUser.userId(), "assistant", "抱歉，处理过程中遇到了问题，请稍后重试。", false);
                    }
                    LOGGER.warn("Conversation stream failed conversationId={}", conversationId, ex);
                    sendErrorEvent(emitter, conversationId, sequence, "会话流式调用失败，请稍后重试");
                } catch (IOException ioException) {
                    emitter.completeWithError(ioException);
                    return;
                }
                emitter.complete();
            }
        });

        return emitter;
    }

    private void sendConversationEvent(
        SseEmitter emitter,
        UUID conversationId,
        AtomicInteger sequence,
        PythonStreamEvent event
    ) {
        int nextSeq = sequence.incrementAndGet();
        Map<String, Object> payload = new LinkedHashMap<>(event.safePayload());
        String eventStage = event.stage();
        if (eventStage != null && !eventStage.isBlank() && !payload.containsKey("stage")) {
            payload.put("stage", eventStage);
        }
        try {
            emitter.send(SseEmitter.event()
                .name(event.eventType())
                .id(String.valueOf(nextSeq))
                .data(new ConversationStreamEventPayload(
                    event.eventType(),
                    nextSeq,
                    OffsetDateTime.now(),
                    new ConversationDialogState(
                        conversationId,
                        "turn_" + nextSeq,
                        String.valueOf(payload.getOrDefault("pedagogyStrategy", "EXPLAIN")),
                        String.valueOf(payload.getOrDefault("nextAction", "WAIT_USER"))
                    ),
                    payload
                )));
        } catch (IOException ex) {
            emitter.completeWithError(ex);
        }
    }

    private void sendErrorEvent(
        SseEmitter emitter,
        UUID conversationId,
        AtomicInteger sequence,
        String message
    ) throws IOException {
        int nextSeq = sequence.incrementAndGet();
        emitter.send(SseEmitter.event()
            .name("error")
            .id(String.valueOf(nextSeq))
            .data(new ConversationStreamEventPayload(
                "error",
                nextSeq,
                OffsetDateTime.now(),
                new ConversationDialogState(conversationId, "turn_" + nextSeq, "CORRECT", "END_SESSION"),
                Map.of("message", message == null ? "会话流式调用失败" : message)
            )));
    }

    private void collectAssistantReply(StringBuilder assistantReply, PythonStreamEvent event) {
        String chunk = extractVisibleAssistantChunk(event);
        if (chunk == null || chunk.isBlank()) {
            return;
        }
        if (!assistantReply.isEmpty()) {
            assistantReply.append('\n');
        }
        assistantReply.append(chunk.trim());
    }

    private String extractVisibleAssistantChunk(PythonStreamEvent event) {
        if (!"result_chunk".equals(event.eventType())) {
            return "";
        }
        String stage = event.stage();
        if (stage != null && !stage.isBlank() && !"tutoring".equals(stage)) {
            return "";
        }
        Object text = event.safePayload().get("text");
        if (!(text instanceof String value)) {
            return "";
        }
        return sanitizeVisibleAssistantChunk(value);
    }

    private boolean looksLikeInternalChain(String text) {
        String normalized = text == null ? "" : text.replace('\n', ' ').trim();
        if (normalized.isBlank()) {
            return false;
        }
        return normalized.contains("历史摘要")
            || normalized.contains("优先参考的来源")
            || normalized.contains("建议你这样学")
            || normalized.contains("接下来请你先回答")
            || normalized.contains("未解决的问题");
    }

    private String sanitizeVisibleAssistantChunk(String text) {
        String normalized = text == null ? "" : text.replace("\r\n", "\n").trim();
        if (normalized.isBlank() || looksLikeInternalChain(normalized)) {
            return "";
        }
        return normalized
            .replaceAll("(?m)^\\s{0,3}#{1,6}\\s*", "")
            .replaceAll("(?m)^\\s*>\\s?", "")
            .replaceAll("\\*\\*(.*?)\\*\\*", "$1")
            .replaceAll("__(.*?)__", "$1")
            .replaceAll("`([^`]+)`", "$1")
            .replaceAll("(?m)^\\s*---\\s*$", "")
            .replaceAll("\\n{3,}", "\n\n")
            .trim();
    }

    private void appendConversationMessage(UUID conversationId, UUID userId, String role, String content, boolean failOnError) {
        if (content == null || content.isBlank()) {
            return;
        }
        try {
            pythonConversationMessageClient.appendMessage(conversationId, userId, role, content.trim());
        } catch (Exception ex) {
            if (failOnError) {
                throw new ApplicationException("CONVERSATION_MESSAGE_PERSIST_FAILED", "会话消息保存失败，请稍后重试", HttpStatus.BAD_GATEWAY);
            }
            LOGGER.warn(
                "Failed to persist conversation message conversationId={} userId={} role={}",
                conversationId,
                userId,
                role,
                ex
            );
        }
    }

    private List<ConversationMessageItemResponse> fetchRecentHistory(UUID conversationId, UUID userId) {
        try {
            List<ConversationMessageItemResponse> all = pythonConversationMessageClient.listMessages(conversationId, userId);
            int fromIndex = Math.max(0, all.size() - MAX_HISTORY_MESSAGES);
            return all.subList(fromIndex, all.size());
        } catch (Exception ex) {
            LOGGER.warn("Failed to load conversation history conversationId={}: {}", conversationId, ex.getMessage());
            return List.of();
        }
    }

    private Map<String, Object> buildConversationParams(
        JwtAuthenticatedUser currentUser,
        UUID conversationId,
        ConversationMessageStreamRequest request,
        List<ConversationMessageItemResponse> history
    ) {
        Map<String, Object> params = new LinkedHashMap<>();
        params.put("message", request.message());
        params.put("query", request.message());
        params.put("userInput", request.message());
        params.put("conversationId", conversationId.toString());
        params.put("userId", currentUser.userId().toString());
        params.put("conversationLength", history.size());

        List<Map<String, String>> messages = new java.util.ArrayList<>();
        for (ConversationMessageItemResponse msg : history) {
            messages.add(Map.of("role", msg.role(), "content", msg.content()));
        }
        params.put("messages", messages);
        userProfileCurrentRepository.findById(currentUser.userId())
            .ifPresent(profile -> {
                params.put("profile", new LinkedHashMap<>(profile.getProfileJson()));
                params.put("profileSummary", profile.getSummaryText());
            });
        return params;
    }

    private String truncate(String message, int maxLength) {
        return message.length() <= maxLength ? message : message.substring(0, maxLength);
    }

    private String buildConversationTitle(String message) {
        String normalized = message == null ? "" : message.replaceAll("\\s+", " ").trim();
        if (normalized.isEmpty()) {
            return "新对话";
        }
        return truncate(normalized, 20);
    }

    private String resolveConversationTitle(QnaSession session) {
        if (session.getTitle() != null && !session.getTitle().isBlank() && !"新对话".equals(session.getTitle())) {
            return session.getTitle();
        }
        if (session.getLastMessagePreview() != null && !session.getLastMessagePreview().isBlank()) {
            return buildConversationTitle(session.getLastMessagePreview());
        }
        return "新对话";
    }
}
