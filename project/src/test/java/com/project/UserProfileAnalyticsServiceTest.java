package com.project;

import com.project.api.profile.dto.ProfileBehaviorTrendPoint;
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
        stubQueries(List.of(), List.of(), List.of(), List.of(), List.of());
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
    }

    @Test
    void derivesSystemAnalysisFromProfileOnly() {
        stubQueries(List.of(), List.of(), List.of(), List.of(), List.of());
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
            List.of(Map.of("day", today, "value", 5))
        );
        when(profileRepository.findById(userId)).thenReturn(Optional.empty());

        UserProfileAnalyticsResponse response = service.getAnalytics(currentUser, userId, 30);

        ProfileBehaviorTrendPoint point = findPoint(response, today);
        assertThat(point.newMistakeCount()).isEqualTo(2);
        assertThat(point.reviewCount()).isEqualTo(5);
        assertThat(response.systemAnalysis().coverage().newMistakeCount()).isEqualTo(2);
        assertThat(response.systemAnalysis().coverage().reviewCount()).isEqualTo(5);
    }

    @SafeVarargs
    private void stubQueries(List<Map<String, Object>>... queryResults) {
        when(jdbcTemplate.queryForList(anyString(), any(SqlParameterSource.class)))
            .thenReturn(queryResults[0], queryResults[1], queryResults[2], queryResults[3], queryResults[4]);
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
}
