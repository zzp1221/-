package com.project;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.application.smartengine.PythonAgentClient;
import com.project.application.smartengine.PythonStreamEvent;
import com.project.domain.video.VideoGenerationTaskRepository;
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
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doAnswer;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.request;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Integration tests for the task submission and SSE orchestration flow.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class SmartEngineControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private VideoGenerationTaskRepository videoGenerationTaskRepository;

    @MockBean
    private PythonAgentClient pythonAgentClient;

    @Test
    void submitTaskCompletesAndCanReplayStream() throws Exception {
        doAnswer(invocation -> {
            @SuppressWarnings("unchecked")
            Consumer<PythonStreamEvent> consumer = invocation.getArgument(1, Consumer.class);
            consumer.accept(new PythonStreamEvent(
                "progress",
                "retrieving",
                Map.of("stage", "retrieving", "percent", 35)
            ));
            consumer.accept(new PythonStreamEvent(
                "result_chunk",
                "generating",
                Map.of("text", "数据库索引讲解")
            ));
            consumer.accept(new PythonStreamEvent(
                "done",
                "completed",
                Map.of("summary", "生成完成")
            ));
            return null;
        }).when(pythonAgentClient).stream(any(), any());

        String token = registerAndGetToken("engine_" + System.nanoTime());
        MvcResult submitResult = mockMvc.perform(post("/api/smart-engine/submit")
                .header("Authorization", "Bearer " + token)
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
            .andExpect(jsonPath("$.traceId").isNotEmpty())
            .andReturn();

        String taskId = readField(submitResult, "taskId");
        awaitTaskCompletion(token, taskId);

        mockMvc.perform(get("/api/smart-engine/tasks/" + taskId)
                .header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("COMPLETED"))
            .andExpect(jsonPath("$.currentStage").value("completed"))
            .andExpect(jsonPath("$.responseSummary.summary").value("生成完成"));

        MvcResult streamResult = mockMvc.perform(get("/api/smart-engine/tasks/" + taskId + "/stream")
                .header("Authorization", "Bearer " + token))
            .andExpect(request().asyncStarted())
            .andReturn();

        String responseBody = streamResult.getResponse().getContentAsString(StandardCharsets.UTF_8);
        assertThat(responseBody).contains("event:progress");
        assertThat(responseBody).contains("event:result_chunk");
        assertThat(responseBody).contains("event:done");
        assertThat(responseBody).contains("生成完成");
    }

    @Test
    void submitWithoutTokenReturnsAuthRequired() throws Exception {
        mockMvc.perform(post("/api/smart-engine/submit")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "serviceType": "RESOURCE_GENERATION",
                      "params": {}
                    }
                    """))
            .andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.code").value("AUTH_REQUIRED"));
    }

    @Test
    void submitVideoTaskPersistsVideoGenerationProjection() throws Exception {
        Path videoFile = Files.createTempFile("zhixue-video-", ".mp4");
        Path thumbnailFile = Files.createTempFile("zhixue-video-thumb-", ".svg");
        Files.writeString(videoFile, "placeholder-video", StandardCharsets.UTF_8);
        Files.writeString(thumbnailFile, "<svg/>", StandardCharsets.UTF_8);

        doAnswer(invocation -> {
            @SuppressWarnings("unchecked")
            Consumer<PythonStreamEvent> consumer = invocation.getArgument(1, Consumer.class);
            consumer.accept(new PythonStreamEvent(
                "video_gen:start",
                "video_started",
                Map.of("topic", "联合索引", "progress", 10)
            ));
            consumer.accept(new PythonStreamEvent(
                "video_gen:script",
                "script_generated",
                Map.of("topic", "联合索引", "progress", 25)
            ));
            consumer.accept(new PythonStreamEvent(
                "video_gen:speech",
                "speech_synthesized",
                Map.of("topic", "联合索引", "progress", 50)
            ));
            consumer.accept(new PythonStreamEvent(
                "video_gen:avatar",
                "video_rendering",
                Map.of("topic", "联合索引", "progress", 75)
            ));
            consumer.accept(new PythonStreamEvent(
                "resource_file",
                "video_generation",
                Map.ofEntries(
                    Map.entry("assetType", "VIDEO"),
                    Map.entry("title", "联合索引教学视频"),
                    Map.entry("fileName", videoFile.getFileName().toString()),
                    Map.entry("localPath", videoFile.toString()),
                    Map.entry("mimeType", "video/mp4"),
                    Map.entry("thumbnailPath", thumbnailFile.toString()),
                    Map.entry("thumbnailFileName", thumbnailFile.getFileName().toString()),
                    Map.entry("thumbnailMimeType", "image/svg+xml"),
                    Map.entry("videoStyle", "hybrid"),
                    Map.entry("durationSeconds", 60),
                    Map.entry("knowledgePoint", "联合索引")
                )
            ));
            consumer.accept(new PythonStreamEvent(
                "video_gen:complete",
                "completed",
                Map.ofEntries(
                    Map.entry("topic", "联合索引"),
                    Map.entry("title", "联合索引教学视频"),
                    Map.entry("progress", 100),
                    Map.entry("durationSeconds", 60),
                    Map.entry("videoStyle", "hybrid"),
                    Map.entry("ttsProvider", "edge_tts"),
                    Map.entry("avatarProvider", "sadtalker"),
                    Map.entry("activeProvider", "openai_compatible"),
                    Map.entry("fallbackProvider", "spark"),
                    Map.entry("scriptText", "今天我们来学习联合索引。"),
                    Map.entry("scriptJson", Map.of(
                        "title", "联合索引教学视频",
                        "fullText", "今天我们来学习联合索引。"
                    )),
                    Map.entry("generationParams", Map.of("style", "hybrid", "durationTarget", 60)),
                    Map.entry("audioPath", "D:/sandbox/video/speech.mp3"),
                    Map.entry("finalVideoPath", videoFile.toString()),
                    Map.entry("thumbnailPath", thumbnailFile.toString()),
                    Map.entry("safetyPassed", true),
                    Map.entry("criticScore", 0.96)
                )
            ));
            consumer.accept(new PythonStreamEvent(
                "done",
                "completed",
                Map.of("summary", "教学视频生成完成")
            ));
            return null;
        }).when(pythonAgentClient).stream(any(), any());

        String token = registerAndGetToken("video_" + System.nanoTime());
        MvcResult submitResult = mockMvc.perform(post("/api/smart-engine/submit")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                      "conversationId": "%s",
                      "serviceType": "RESOURCE_GENERATION",
                      "params": {
                        "resourceType": "VIDEO",
                        "topic": "联合索引",
                        "query": "联合索引",
                        "style": "hybrid",
                        "duration": 60
                      }
                    }
                    """.formatted(UUID.randomUUID())))
            .andExpect(status().isOk())
            .andReturn();

        String taskId = readField(submitResult, "taskId");
        awaitTaskCompletion(token, taskId);

        var savedProjection = videoGenerationTaskRepository.findByTaskId(UUID.fromString(taskId));
        assertThat(savedProjection).isPresent();
        assertThat(savedProjection.get().getStatus()).isEqualTo("completed");
        assertThat(savedProjection.get().getTopic()).isEqualTo("联合索引");
        assertThat(savedProjection.get().getTitle()).isEqualTo("联合索引教学视频");
        assertThat(savedProjection.get().getVideoStyle()).isEqualTo("hybrid");
        assertThat(savedProjection.get().getTtsProvider()).isEqualTo("edge_tts");
        assertThat(savedProjection.get().getAvatarProvider()).isEqualTo("sadtalker");
        assertThat(savedProjection.get().getFinalVideoPath()).isEqualTo(videoFile.toString());
        assertThat(savedProjection.get().getThumbnailPath()).isEqualTo(thumbnailFile.toString());
        assertThat(savedProjection.get().getScriptText()).contains("联合索引");
        assertThat(savedProjection.get().getGenerationParams()).containsEntry("durationTarget", 60);
        assertThat(savedProjection.get().getSafetyPassed()).isTrue();
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

    private String registerAndGetToken(String loginId) throws Exception {
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

        return readField(registerResult, "token");
    }

    private String readField(MvcResult result, String fieldName) throws Exception {
        JsonNode jsonNode = objectMapper.readTree(result.getResponse().getContentAsString());
        return jsonNode.path(fieldName).asText();
    }
}
