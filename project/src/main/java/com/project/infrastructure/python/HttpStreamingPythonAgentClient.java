package com.project.infrastructure.python;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.application.smartengine.PythonAgentClient;
import com.project.application.smartengine.PythonStreamEvent;
import com.project.application.smartengine.SmartEngineInvocation;
import com.project.application.smartengine.StreamEventType;
import com.project.config.AppProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;

/**
 * JDK {@link HttpClient}-based implementation for the Python streaming endpoint.
 *
 * <p>The implementation intentionally uses the JDK client to keep the control
 * plane lightweight and independent from reactive server infrastructure while
 * still supporting incremental SSE-style reads from the Python runtime.</p>
 */
@Component
public class HttpStreamingPythonAgentClient implements PythonAgentClient {

    private static final TypeReference<Map<String, Object>> MAP_TYPE = new TypeReference<>() {
    };
    private static final Logger LOGGER = LoggerFactory.getLogger(HttpStreamingPythonAgentClient.class);

    private final ObjectMapper objectMapper;
    private final AppProperties appProperties;
    private final HttpClient httpClient;

    public HttpStreamingPythonAgentClient(ObjectMapper objectMapper, AppProperties appProperties) {
        this.objectMapper = objectMapper;
        this.appProperties = appProperties;
        this.httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(appProperties.getPythonAgent().getConnectTimeout())
            .build();
    }

    @Override
    public void stream(SmartEngineInvocation invocation, Consumer<PythonStreamEvent> eventConsumer) {
        try {
            String requestBody = buildRequestBody(invocation);
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(appProperties.getPythonAgent().getBaseUrl() + "/internal/smart-engine/stream"))
                .header("Content-Type", "application/json")
                .header("Accept", "text/event-stream")
                .timeout(appProperties.getPythonAgent().getReadTimeout())
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();

            HttpResponse<java.io.InputStream> response = httpClient.send(request, HttpResponse.BodyHandlers.ofInputStream());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                String responseBody = new String(response.body().readAllBytes(), StandardCharsets.UTF_8);
                LOGGER.warn(
                    "Python agent rejected request status={} traceId={} taskId={} body={} response={}",
                    response.statusCode(),
                    invocation.traceId(),
                    invocation.taskId(),
                    requestBody,
                    responseBody
                );
                throw new IllegalStateException(
                    responseBody == null || responseBody.isBlank()
                        ? "Python agent returned status " + response.statusCode()
                        : "Python agent returned status " + response.statusCode() + ": " + responseBody
                );
            }

            readEventStream(response, eventConsumer);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Failed to call Python agent stream", ex);
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to call Python agent stream", ex);
        }
    }

    private String buildRequestBody(SmartEngineInvocation invocation) throws IOException {
        Map<String, Object> requestBody = new LinkedHashMap<>();
        requestBody.put("userId", invocation.userId());
        requestBody.put("taskId", invocation.taskId());
        requestBody.put("traceId", invocation.traceId());
        requestBody.put("conversationId", invocation.conversationId());
        requestBody.put("serviceType", invocation.serviceType().value());
        requestBody.put("params", invocation.params());
        return objectMapper.writeValueAsString(requestBody);
    }

    private void readEventStream(
        HttpResponse<java.io.InputStream> response,
        Consumer<PythonStreamEvent> eventConsumer
    ) throws IOException {
        try (BufferedReader reader = new BufferedReader(
            new InputStreamReader(response.body(), StandardCharsets.UTF_8)
        )) {
            String eventType = null;
            String currentStage = null;
            StringBuilder dataBuffer = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                if (line.startsWith("event:")) {
                    eventType = line.substring(6).trim();
                    continue;
                }
                if (line.startsWith("data:")) {
                    dataBuffer.append(line.substring(5).trim());
                    continue;
                }
                if (line.isBlank()) {
                    currentStage = dispatch(eventType, dataBuffer.toString(), currentStage, eventConsumer);
                    eventType = null;
                    dataBuffer.setLength(0);
                }
            }

            if (!dataBuffer.isEmpty() || eventType != null) {
                dispatch(eventType, dataBuffer.toString(), currentStage, eventConsumer);
            }
        }
    }

    private String dispatch(
        String eventType,
        String rawData,
        String currentStage,
        Consumer<PythonStreamEvent> eventConsumer
    ) throws IOException {
        if ((eventType == null || eventType.isBlank()) && (rawData == null || rawData.isBlank())) {
            return currentStage;
        }

        Map<String, Object> envelope = rawData == null || rawData.isBlank()
            ? new LinkedHashMap<>()
            : objectMapper.readValue(rawData, MAP_TYPE);
        Object payloadCandidate = envelope.get("payload");
        @SuppressWarnings("unchecked")
        Map<String, Object> payload = payloadCandidate instanceof Map<?, ?>
            ? new LinkedHashMap<>((Map<String, Object>) payloadCandidate)
            : envelope;

        String resolvedEventType = eventType;
        if ((resolvedEventType == null || resolvedEventType.isBlank()) && envelope.get("event") instanceof String envelopeEventType) {
            resolvedEventType = envelopeEventType;
        }
        String stage = payload.get("stage") instanceof String stageValue ? stageValue : currentStage;
        eventConsumer.accept(new PythonStreamEvent(
            StreamEventType.resolve(resolvedEventType).wireValue(),
            stage,
            payload
        ));
        return stage;
    }
}
