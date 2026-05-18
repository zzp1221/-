package com.project.application.smartengine;

import com.project.domain.artifact.ResourceType;
import com.project.domain.task.SmartEngineTask;
import com.project.domain.task.ServiceType;
import com.project.domain.video.VideoGenerationTask;
import com.project.domain.video.VideoGenerationTaskRepository;
import org.springframework.stereotype.Service;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 在关系数据库中维护视频生成进度的投影。
 */
@Service
public class VideoGenerationTaskService {

    private final VideoGenerationTaskRepository videoGenerationTaskRepository;

    public VideoGenerationTaskService(VideoGenerationTaskRepository videoGenerationTaskRepository) {
        this.videoGenerationTaskRepository = videoGenerationTaskRepository;
    }

    @Transactional
    public void syncFromPythonEvent(SmartEngineTask task, PythonStreamEvent pythonEvent, Map<String, Object> payload) {
        if (!isVideoTask(task, payload)) {
            return;
        }

        VideoGenerationTask entity = loadOrCreate(task);
        hydrateFromRequest(entity, task);
        hydrateFromPayload(entity, payload);

        switch (pythonEvent.resolvedEventType()) {
            case VIDEO_GEN_START -> entity.setStatus("pending");
            case VIDEO_GEN_SCRIPT -> entity.setStatus("script_generated");
            case VIDEO_GEN_SPEECH -> entity.setStatus("speech_synthesized");
            case VIDEO_GEN_AVATAR -> entity.setStatus("video_rendering");
            case VIDEO_GEN_COMPLETE -> entity.setStatus("completed");
            case DONE -> entity.setStatus(
                "FAILED".equalsIgnoreCase(stringValue(payload.get("status"))) ? "failed" : "completed"
            );
            case ERROR -> entity.setStatus("failed");
            default -> {
                return;
            }
        }

        if (pythonEvent.resolvedEventType() == StreamEventType.ERROR) {
            entity.setErrorMessage(stringValue(payload.get("message")));
        } else if (pythonEvent.resolvedEventType() == StreamEventType.DONE
            && "FAILED".equalsIgnoreCase(stringValue(payload.get("status")))) {
            entity.setErrorMessage(stringValue(payload.get("summary")));
        }

        videoGenerationTaskRepository.save(entity);
    }

    @Transactional
    public void syncFromResourceFile(SmartEngineTask task, Map<String, Object> payload) {
        if (!isVideoTask(task, payload)) {
            return;
        }

        VideoGenerationTask entity = loadOrCreate(task);
        hydrateFromRequest(entity, task);
        hydrateFromPayload(entity, payload);
        if (entity.getFinalVideoPath() == null) {
            entity.setFinalVideoPath(stringValue(payload.get("localPath")));
        }
        if (entity.getThumbnailPath() == null) {
            entity.setThumbnailPath(stringValue(payload.get("thumbnailPath")));
        }
        videoGenerationTaskRepository.save(entity);
    }

    @Transactional
    public void markFailed(SmartEngineTask task, String message) {
        if (!isVideoTask(task, Map.of())) {
            return;
        }

        VideoGenerationTask entity = loadOrCreate(task);
        hydrateFromRequest(entity, task);
        entity.setStatus("failed");
        entity.setErrorMessage(message);
        videoGenerationTaskRepository.save(entity);
    }

    private VideoGenerationTask loadOrCreate(SmartEngineTask task) {
        return videoGenerationTaskRepository.findByTaskId(task.getId())
            .orElseGet(() -> {
                VideoGenerationTask entity = new VideoGenerationTask();
                entity.setTaskId(task.getId());
                entity.setStudentId(task.getUserId());
                entity.setTraceId(task.getTraceId());
                entity.setTitle("教学视频");
                entity.setTopic("教学主题");
                entity.setStatus("pending");
                try {
                    return videoGenerationTaskRepository.saveAndFlush(entity);
                } catch (DataIntegrityViolationException ex) {
                    return videoGenerationTaskRepository.findByTaskId(task.getId())
                        .orElseThrow(() -> ex);
                }
            });
    }

    private void hydrateFromRequest(VideoGenerationTask entity, SmartEngineTask task) {
        Map<String, Object> params = requestParams(task);
        String topic = firstNonBlank(
            stringValue(params.get("topic")),
            stringValue(params.get("query")),
            entity.getTopic(),
            "教学主题"
        );
        entity.setTopic(topic);
        entity.setTitle(firstNonBlank(stringValue(params.get("title")), entity.getTitle(), topic + "教学视频"));
        if (entity.getVideoStyle() == null) {
            entity.setVideoStyle(stringValue(params.get("style")));
        }
        if (entity.getDurationSeconds() == null) {
            entity.setDurationSeconds(intValue(params.get("duration")));
        }
        if (entity.getGenerationParams().isEmpty()) {
            entity.setGenerationParams(new LinkedHashMap<>(params));
        }
    }

    private void hydrateFromPayload(VideoGenerationTask entity, Map<String, Object> payload) {
        entity.setTitle(firstNonBlank(stringValue(payload.get("title")), entity.getTitle()));
        entity.setTopic(firstNonBlank(
            stringValue(payload.get("topic")),
            stringValue(payload.get("knowledgePoint")),
            entity.getTopic()
        ));
        entity.setVideoStyle(firstNonBlank(
            stringValue(payload.get("videoStyle")),
            stringValue(payload.get("style")),
            entity.getVideoStyle()
        ));
        Integer durationSeconds = firstNonNullInt(
            intValue(payload.get("durationSeconds")),
            intValue(payload.get("duration")),
            entity.getDurationSeconds()
        );
        entity.setDurationSeconds(durationSeconds);
        entity.setFinalVideoPath(firstNonBlank(
            stringValue(payload.get("finalVideoPath")),
            stringValue(payload.get("localPath")),
            entity.getFinalVideoPath()
        ));
        entity.setThumbnailPath(firstNonBlank(stringValue(payload.get("thumbnailPath")), entity.getThumbnailPath()));
        entity.setAudioPath(firstNonBlank(stringValue(payload.get("audioPath")), entity.getAudioPath()));
        entity.setAvatarVideoPath(firstNonBlank(stringValue(payload.get("avatarVideoPath")), entity.getAvatarVideoPath()));
        entity.setAnimationVideoPath(firstNonBlank(
            stringValue(payload.get("animationVideoPath")),
            entity.getAnimationVideoPath()
        ));
        entity.setActiveProvider(firstNonBlank(stringValue(payload.get("activeProvider")), entity.getActiveProvider()));
        entity.setFallbackProvider(firstNonBlank(stringValue(payload.get("fallbackProvider")), entity.getFallbackProvider()));
        entity.setTtsProvider(firstNonBlank(stringValue(payload.get("ttsProvider")), entity.getTtsProvider()));
        entity.setAvatarProvider(firstNonBlank(stringValue(payload.get("avatarProvider")), entity.getAvatarProvider()));

        if (payload.get("criticScore") instanceof Number number) {
            entity.setCriticScore(BigDecimal.valueOf(number.doubleValue()));
        }
        if (payload.get("safetyPassed") instanceof Boolean safetyPassed) {
            entity.setSafetyPassed(safetyPassed);
        }

        Map<String, Object> scriptJson = mapValue(payload.get("scriptJson"));
        if (!scriptJson.isEmpty()) {
            entity.setScriptJson(scriptJson);
        }
        String scriptText = firstNonBlank(stringValue(payload.get("scriptText")), entity.getScriptText());
        entity.setScriptText(scriptText == null ? "" : scriptText);

        Map<String, Object> generationParams = mapValue(payload.get("generationParams"));
        if (!generationParams.isEmpty()) {
            entity.setGenerationParams(generationParams);
        }

        Map<String, Object> videoTaskPayload = mapValue(payload.get("videoGenerationTask"));
        if (!videoTaskPayload.isEmpty()) {
            hydrateFromVideoTask(entity, videoTaskPayload);
        }

        Map<String, Object> artifactPayload = mapValue(payload.get("videoSandboxArtifact"));
        if (!artifactPayload.isEmpty()) {
            hydrateFromArtifact(entity, artifactPayload);
        }
    }

    private void hydrateFromVideoTask(VideoGenerationTask entity, Map<String, Object> videoTaskPayload) {
        entity.setTitle(firstNonBlank(stringValue(videoTaskPayload.get("title")), entity.getTitle()));
        entity.setTopic(firstNonBlank(stringValue(videoTaskPayload.get("topic")), entity.getTopic()));
        entity.setTtsProvider(firstNonBlank(stringValue(videoTaskPayload.get("ttsProvider")), entity.getTtsProvider()));
        entity.setAvatarProvider(firstNonBlank(stringValue(videoTaskPayload.get("avatarProvider")), entity.getAvatarProvider()));
        entity.setVideoStyle(firstNonBlank(stringValue(videoTaskPayload.get("videoStyle")), entity.getVideoStyle()));
        entity.setDurationSeconds(firstNonNullInt(intValue(videoTaskPayload.get("durationSeconds")), entity.getDurationSeconds()));
        Map<String, Object> scriptPayload = mapValue(videoTaskPayload.get("script"));
        if (!scriptPayload.isEmpty()) {
            entity.setScriptJson(scriptPayload);
            entity.setScriptText(firstNonBlank(stringValue(scriptPayload.get("fullText")), entity.getScriptText()));
        }
        Map<String, Object> generationParams = mapValue(videoTaskPayload.get("generationParams"));
        if (!generationParams.isEmpty()) {
            entity.setGenerationParams(generationParams);
        }
    }

    private void hydrateFromArtifact(VideoGenerationTask entity, Map<String, Object> artifactPayload) {
        entity.setAudioPath(firstNonBlank(stringValue(artifactPayload.get("audioPath")), entity.getAudioPath()));
        entity.setFinalVideoPath(firstNonBlank(
            stringValue(artifactPayload.get("finalVideoPath")),
            entity.getFinalVideoPath()
        ));
        entity.setThumbnailPath(firstNonBlank(stringValue(artifactPayload.get("thumbnailPath")), entity.getThumbnailPath()));
        entity.setDurationSeconds(firstNonNullInt(
            intValue(artifactPayload.get("durationSeconds")),
            entity.getDurationSeconds()
        ));
        entity.setVideoStyle(firstNonBlank(stringValue(artifactPayload.get("videoStyle")), entity.getVideoStyle()));
        entity.setScriptText(firstNonBlank(
            stringValue(artifactPayload.get("previewText")),
            entity.getScriptText()
        ));
    }

    private boolean isVideoTask(SmartEngineTask task, Map<String, Object> payload) {
        if (task.getServiceType() == ServiceType.VIDEO_GENERATION) {
            return true;
        }

        String assetType = stringValue(payload.get("assetType"));
        if (isVideoResourceType(assetType)) {
            return true;
        }

        Map<String, Object> params = requestParams(task);
        if (isVideoResourceType(stringValue(params.get("resourceType")))) {
            return true;
        }

        Object resourceTypes = params.get("resourceTypes");
        if (resourceTypes instanceof List<?> list) {
            return list.stream().map(String::valueOf).anyMatch(this::isVideoResourceType);
        }
        return false;
    }

    private boolean isVideoResourceType(String rawValue) {
        if (rawValue == null || rawValue.isBlank()) {
            return false;
        }
        try {
            return ResourceType.fromValue(rawValue) == ResourceType.VIDEO;
        } catch (IllegalArgumentException ignored) {
            return false;
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> requestParams(SmartEngineTask task) {
        Object params = task.getRequestPayload().get("params");
        if (params instanceof Map<?, ?> map) {
            return new LinkedHashMap<>((Map<String, Object>) map);
        }
        return Map.of();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> mapValue(Object value) {
        if (value instanceof Map<?, ?> map) {
            return new LinkedHashMap<>((Map<String, Object>) map);
        }
        return Map.of();
    }

    private String stringValue(Object value) {
        if (value == null) {
            return null;
        }
        String text = String.valueOf(value).trim();
        return text.isBlank() ? null : text;
    }

    private Integer intValue(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value instanceof String text && !text.isBlank()) {
            try {
                return Integer.parseInt(text.trim());
            } catch (NumberFormatException ignored) {
                return null;
            }
        }
        return null;
    }

    private String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }

    private Integer firstNonNullInt(Integer... values) {
        for (Integer value : values) {
            if (value != null) {
                return value;
            }
        }
        return null;
    }
}
