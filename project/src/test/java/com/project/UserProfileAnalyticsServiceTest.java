package com.project;

import com.project.api.profile.dto.ProfileBehaviorTrendPoint;
import com.project.api.profile.dto.ProfileResourcePreferenceResponse;
import com.project.api.profile.dto.UserProfileAnalyticsResponse;
import com.project.application.profile.UserProfileAnalyticsService;
import com.project.domain.profile.UserProfileCurrent;
import com.project.domain.profile.UserProfileCurrentRepository;
import com.project.security.JwtAuthenticatedUser;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class UserProfileAnalyticsServiceTest {

    private final UUID userId = UUID.fromString("10000000-0000-0000-0000-000000000001");
    private final JwtAuthenticatedUser currentUser = new JwtAuthenticatedUser(userId, "learner", "STUDENT");
    private NamedParameterJdbcTemplate jdbcTemplate;
    private UserProfileCurrentRepository profileRepository;
    private UserProfileAnalyticsService service;

    @BeforeEach
    void setUp() {
        jdbcTemplate = mock(NamedParameterJdbcTemplate.class);
        profileRepository = mock(UserProfileCurrentRepository.class);
        service = new UserProfileAnalyticsService(jdbcTemplate, profileRepository);
    }

    @Test
    void returnsEmptyTrendWhenNoDataExists() {
        stubQueries(List.of(), List.of(), List.of(), List.of(), List.of(), List.of(), List.of());
        when(profileRepository.findById(userId)).thenReturn(Optional.empty());

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        assertThat(response.behaviorTrend()).hasSize(30);
        assertThat(response.behaviorTrend()).allSatisfy(point -> {
            assertThat(point.conversationCount()).isZero();
            assertThat(point.serviceTaskCount()).isZero();
            assertThat(point.practiceSubmissionCount()).isZero();
            assertThat(point.practiceAccuracy()).isNull();
            assertThat(point.newMistakeCount()).isZero();
            assertThat(point.reviewCount()).isZero();
        });
        assertThat(response.systemAnalysis().dataAvailable()).isFalse();
        assertThat(response.systemAnalysis().strongestSkill()).isNull();
        assertThat(response.preferenceAnalytics().resourcePreferences()).hasSize(6);
        assertThat(response.preferenceAnalytics().resourcePreferences())
            .allSatisfy(item -> assertThat(item.identified()).isFalse());
        assertThat(response.preferenceAnalytics().explanationPreference().identified()).isFalse();
    }

    @Test
    void derivesSystemAnalysisFromProfileOnly() {
        stubQueries(List.of(), List.of(), List.of(), List.of(), List.of(), List.of(), List.of());
        when(profileRepository.findById(userId)).thenReturn(Optional.of(profile(Map.of(
            "skillMastery", Map.of("数据库索引", 0.88, "事务隔离", 0.54),
            "weakPointDetails", List.of(Map.of("topic", "事务隔离"))
        ))));

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        assertThat(response.systemAnalysis().dataAvailable()).isTrue();
        assertThat(response.systemAnalysis().strongestSkill()).isEqualTo("数据库索引");
        assertThat(response.systemAnalysis().strongestSkillScore()).isEqualTo(88);
        assertThat(response.systemAnalysis().focusAreas()).containsExactly("事务隔离");
        assertThat(response.systemAnalysis().coverage().activeDays()).isZero();
        assertThat(response.systemAnalysis().coverage().profileSkillCount()).isEqualTo(2);
        assertThat(response.systemAnalysis().coverage().weakPointCount()).isEqualTo(1);
    }

    @Test
    void aggregatesPracticeSubmissionAccuracyByDay() {
        LocalDate today = LocalDate.now();
        stubQueries(
            List.of(),
            List.of(),
            List.of(Map.of("day", today, "submission_count", 4, "correct_count", 3)),
            List.of(),
            List.of(),
            List.of(),
            List.of()
        );
        when(profileRepository.findById(userId)).thenReturn(Optional.empty());

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        ProfileBehaviorTrendPoint point = findPoint(response, today);
        assertThat(point.practiceSubmissionCount()).isEqualTo(4);
        assertThat(point.practiceAccuracy()).isEqualTo(75.0);
        assertThat(response.systemAnalysis().coverage().activeDays()).isEqualTo(1);
        assertThat(response.systemAnalysis().coverage().practiceSubmissionCount()).isEqualTo(4);
    }

    @Test
    void aggregatesMistakeAndReviewCountsByDay() {
        LocalDate today = LocalDate.now();
        stubQueries(
            List.of(),
            List.of(),
            List.of(),
            List.of(Map.of("day", today, "value", 2)),
            List.of(Map.of("day", today, "value", 5)),
            List.of(),
            List.of()
        );
        when(profileRepository.findById(userId)).thenReturn(Optional.empty());

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        ProfileBehaviorTrendPoint point = findPoint(response, today);
        assertThat(point.newMistakeCount()).isEqualTo(2);
        assertThat(point.reviewCount()).isEqualTo(5);
        assertThat(response.systemAnalysis().coverage().newMistakeCount()).isEqualTo(2);
        assertThat(response.systemAnalysis().coverage().reviewCount()).isEqualTo(5);
    }

    @Test
    void derivesPreferenceEvidenceFromProfileOnly() {
        stubQueries(List.of(), List.of(), List.of(), List.of(), List.of(), List.of(), List.of());
        when(profileRepository.findById(userId)).thenReturn(Optional.of(profile(Map.of(
            "preferredResourceTypes", List.of("EXPLANATION", "VIDEO"),
            "explanationPreference", "循序渐进"
        ))));

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        ProfileResourcePreferenceResponse explanation = resourcePreference(response, "EXPLANATION");
        assertThat(explanation.identified()).isTrue();
        assertThat(explanation.profileMentioned()).isTrue();
        assertThat(explanation.requestCount()).isZero();
        assertThat(explanation.evidenceLabel()).isEqualTo("画像已识别，暂无近期行为证据");
        assertThat(resourcePreference(response, "VIDEO").profileMentioned()).isTrue();
        assertThat(response.preferenceAnalytics().explanationPreference().identified()).isTrue();
        assertThat(response.preferenceAnalytics().explanationPreference().value()).isEqualTo("循序渐进");
        assertThat(response.preferenceAnalytics().explanationPreference().source()).isEqualTo("profile_json.explanationPreference");
    }

    @Test
    void aggregatesPreferenceRequestEvidence() {
        OffsetDateTime now = OffsetDateTime.now();
        stubQueries(
            List.of(),
            List.of(),
            List.of(),
            List.of(),
            List.of(),
            List.of(
                Map.of("resource_type", "CODE_CASE", "request_count", 2, "last_used_at", now),
                Map.of("resource_type", "VIDEO", "request_count", 1, "last_used_at", now.minusHours(1))
            ),
            List.of()
        );
        when(profileRepository.findById(userId)).thenReturn(Optional.empty());

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        ProfileResourcePreferenceResponse codeCase = resourcePreference(response, "CODE_CASE");
        assertThat(codeCase.identified()).isTrue();
        assertThat(codeCase.profileMentioned()).isFalse();
        assertThat(codeCase.requestCount()).isEqualTo(2);
        assertThat(codeCase.generatedCount()).isZero();
        assertThat(codeCase.downloadCount()).isZero();
        assertThat(codeCase.lastUsedAt()).isEqualTo(now);
        assertThat(codeCase.evidenceLabel()).isEqualTo("已识别 · 近30天请求 2 次 / 生成 0 次 / 下载 0 次");
        assertThat(resourcePreference(response, "VIDEO").requestCount()).isEqualTo(1);
    }

    @Test
    void aggregatesPreferenceArtifactAndDownloadEvidence() {
        OffsetDateTime now = OffsetDateTime.now();
        stubQueries(
            List.of(),
            List.of(),
            List.of(),
            List.of(),
            List.of(),
            List.of(),
            List.of(Map.of(
                "resource_type", "MINDMAP",
                "generated_count", 2,
                "download_count", 3,
                "last_used_at", now
            ))
        );
        when(profileRepository.findById(userId)).thenReturn(Optional.empty());

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        ProfileResourcePreferenceResponse mindmap = resourcePreference(response, "MINDMAP");
        assertThat(mindmap.identified()).isTrue();
        assertThat(mindmap.generatedCount()).isEqualTo(2);
        assertThat(mindmap.downloadCount()).isEqualTo(3);
        assertThat(mindmap.lastUsedAt()).isEqualTo(now);
        assertThat(mindmap.evidenceLabel()).isEqualTo("已识别 · 近30天请求 0 次 / 生成 2 次 / 下载 3 次");
    }

    @SafeVarargs
    private void stubQueries(List<Map<String, Object>>... queryResults) {
        when(jdbcTemplate.queryForList(anyString(), any(SqlParameterSource.class)))
            .thenAnswer(invocation -> {
                String sql = invocation.getArgument(0);
                if (sql.contains("FROM app.qna_session")) {
                    return queryResults[0];
                }
                if (sql.contains("FROM app.smart_engine_task") && !sql.contains("preference_source")) {
                    return queryResults[1];
                }
                if (sql.contains("FROM app.practice_submission")) {
                    return queryResults[2];
                }
                if (sql.contains("FROM app.mistake_record")) {
                    return queryResults[3];
                }
                if (sql.contains("FROM app.mistake_review_result")) {
                    return queryResults[4];
                }
                if (sql.contains("preference_source")) {
                    return queryResults[5];
                }
                if (sql.contains("FROM app.generated_artifact")) {
                    return queryResults[6];
                }
                return List.of();
            });
    }

    private UserProfileCurrent profile(Map<String, Object> profileJson) {
        UserProfileCurrent current = new UserProfileCurrent();
        current.setUserId(userId);
        current.setProfileJson(profileJson);
        current.setSummaryText("");
        current.setUpdatedAt(OffsetDateTime.now());
        return current;
    }

    private ProfileBehaviorTrendPoint findPoint(UserProfileAnalyticsResponse response, LocalDate day) {
        return response.behaviorTrend()
            .stream()
            .filter(point -> point.date().equals(day))
            .findFirst()
            .orElseThrow();
    }

    private ProfileResourcePreferenceResponse resourcePreference(UserProfileAnalyticsResponse response, String type) {
        return response.preferenceAnalytics()
            .resourcePreferences()
            .stream()
            .filter(item -> item.type().equals(type))
            .findFirst()
            .orElseThrow();
    }
}
