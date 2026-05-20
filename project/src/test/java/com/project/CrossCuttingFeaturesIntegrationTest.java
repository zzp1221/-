package com.project;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.application.smartengine.PythonAgentClient;
import com.project.application.smartengine.PythonStreamEvent;
import com.project.domain.audit.AuditLogRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doAnswer;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.request;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Integration tests for idempotency, audit logging, and artifact download signing.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class CrossCuttingFeaturesIntegrationTest {

    private static final Pattern DOWNLOAD_URL_PATTERN = Pattern.compile("\"downloadUrl\":\"([^\"]+)\"");

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AuditLogRepository auditLogRepository;

    @MockBean
    private PythonAgentClient pythonAgentClient;

    @Test
    void submitSupportsIdempotencyAndSignedArtifactDownload() throws Exception {
        Path tempFile = Files.createTempFile("zhixue-artifact-", ".md");
        Files.writeString(tempFile, "# 数据库索引讲义", StandardCharsets.UTF_8);

        doAnswer(invocation -> {
            @SuppressWarnings("unchecked")
            Consumer<PythonStreamEvent> consumer = invocation.getArgument(1, Consumer.class);
            consumer.accept(new PythonStreamEvent(
                "resource_file",
                "generating",
                Map.ofEntries(
                    Map.entry("assetType", "DOCUMENT"),
                    Map.entry("title", "数据库索引讲义"),
                    Map.entry("fileName", tempFile.getFileName().toString()),
                    Map.entry("localPath", tempFile.toString()),
                    Map.entry("mimeType", "text/markdown"),
                    Map.entry("generatedBy", "LLM"),
                    Map.entry("contentOrigin", "LLM"),
                    Map.entry("provider", "test-provider"),
                    Map.entry("model", "test-model"),
                    Map.entry("agentName", "document_generation"),
                    Map.entry("evidenceIds", List.of("doc-1")),
                    Map.entry("fallback", false),
                    Map.entry("fromCache", false)
                )
            ));
            consumer.accept(new PythonStreamEvent("done", "completed", Map.of("summary", "资源生成完成")));
            return null;
        }).when(pythonAgentClient).stream(any(), any());

        AuthContext auth = register("cross_" + System.nanoTime());
        String idempotencyKey = "idem-" + UUID.randomUUID();

        MvcResult firstSubmit = mockMvc.perform(post("/api/smart-engine/submit")
                .header("Authorization", "Bearer " + auth.token())
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "conversationId": "%s",
                      "serviceType": "RESOURCE_GENERATION",
                      "params": {
                        "resourceType": "DOCUMENT"
                      }
                    }
                    """.formatted(UUID.randomUUID())))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.taskId").isNotEmpty())
            .andReturn();

        String taskId = readField(firstSubmit, "taskId");

        mockMvc.perform(post("/api/smart-engine/submit")
                .header("Authorization", "Bearer " + auth.token())
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "conversationId": "%s",
                      "serviceType": "RESOURCE_GENERATION",
                      "params": {
                        "resourceType": "DOCUMENT"
                      }
                    }
                    """.formatted(UUID.randomUUID())))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.code").value("IDEMPOTENT_REPLAY"))
            .andExpect(jsonPath("$.taskId").value(taskId));

        awaitTaskCompletion(auth.token(), taskId);

        MvcResult streamResult = mockMvc.perform(get("/api/smart-engine/tasks/" + taskId + "/stream")
                .header("Authorization", "Bearer " + auth.token()))
            .andExpect(request().asyncStarted())
            .andReturn();

        String streamBody = streamResult.getResponse().getContentAsString(StandardCharsets.UTF_8);
        Matcher matcher = DOWNLOAD_URL_PATTERN.matcher(streamBody);
        assertThat(matcher.find()).isTrue();
        String downloadUrl = matcher.group(1);

        MvcResult downloadResult = mockMvc.perform(get(downloadUrl)
                .header("Authorization", "Bearer " + auth.token()))
            .andExpect(status().isOk())
            .andReturn();

        assertThat(downloadResult.getResponse().getContentAsString(StandardCharsets.UTF_8)).contains("数据库索引讲义");
        assertThat(auditLogRepository.findAll()).extracting("eventCategory")
            .contains("AUTH", "TASK", "DOWNLOAD");
    }

    private void awaitTaskCompletion(String token, String taskId) throws Exception {
        for (int attempt = 0; attempt < 20; attempt++) {
            MvcResult statusResult = mockMvc.perform(get("/api/smart-engine/tasks/" + taskId)
                    .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andReturn();
            if ("COMPLETED".equals(readField(statusResult, "status"))) {
                return;
            }
            Thread.sleep(100);
        }
        throw new AssertionError("Task did not complete in time");
    }

    private AuthContext register(String loginId) throws Exception {
        MvcResult registerResult = mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "loginId": "%s",
                      "password": "Password123",
                      "fullName": "测试用户",
                      "majorCode": "CS"
                    }
                    """.formatted(loginId)))
            .andExpect(status().isOk())
            .andReturn();

        JsonNode jsonNode = objectMapper.readTree(registerResult.getResponse().getContentAsString());
        return new AuthContext(jsonNode.path("token").asText());
    }

    private String readField(MvcResult result, String fieldName) throws Exception {
        return objectMapper.readTree(result.getResponse().getContentAsString()).path(fieldName).asText();
    }

    private record AuthContext(String token) {
    }
}
