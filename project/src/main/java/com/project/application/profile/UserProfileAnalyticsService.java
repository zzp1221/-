package com.project.application.profile;

import com.project.api.profile.dto.ProfileBehaviorTrendPoint;
import com.project.api.profile.dto.ProfileDataCoverageResponse;
import com.project.api.profile.dto.ProfileSystemAnalysisResponse;
import com.project.api.profile.dto.UserProfileAnalyticsResponse;
import com.project.application.common.ApplicationException;
import com.project.domain.profile.UserProfileCurrentRepository;
import com.project.security.JwtAuthenticatedUser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Date;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

/**
 * Read-only analytics assembled from real persisted learning records.
 */
@Service
public class UserProfileAnalyticsService {

    private static final Logger log = LoggerFactory.getLogger(UserProfileAnalyticsService.class);
    private static final int DEFAULT_DAYS = 30;
    private static final int MIN_DAYS = 7;
    private static final int MAX_DAYS = 90;
    private static final int STRONG_SKILL_THRESHOLD = 70;

    private static final String CONVERSATION_SQL = """
        SELECT CAST(COALESCE(last_message_at, updated_at, created_at) AS date) AS day,
               COUNT(*) AS value
        FROM app.qna_session
        WHERE user_id = :userId
          AND COALESCE(last_message_at, updated_at, created_at) >= :fromAt
          AND COALESCE(last_message_at, updated_at, created_at) < :toAt
        GROUP BY CAST(COALESCE(last_message_at, updated_at, created_at) AS date)
        """;

    private static final String SERVICE_TASK_SQL = """
        SELECT CAST(created_at AS date) AS day,
               COUNT(*) AS value
        FROM app.smart_engine_task
        WHERE user_id = :userId
          AND created_at >= :fromAt
          AND created_at < :toAt
        GROUP BY CAST(created_at AS date)
        """;

    private static final String PRACTICE_SQL = """
        SELECT CAST(submitted_at AS date) AS day,
               COUNT(*) AS submission_count,
               SUM(CASE WHEN is_correct IS TRUE THEN 1 ELSE 0 END) AS correct_count
        FROM app.practice_submission
        WHERE user_id = :userId
          AND submitted_at >= :fromAt
          AND submitted_at < :toAt
        GROUP BY CAST(submitted_at AS date)
        """;

    private static final String MISTAKE_SQL = """
        SELECT CAST(created_at AS date) AS day,
               COUNT(*) AS value
        FROM app.mistake_record
        WHERE user_id = :userId
          AND created_at >= :fromAt
          AND created_at < :toAt
        GROUP BY CAST(created_at AS date)
        """;

    private static final String REVIEW_SQL = """
        SELECT CAST(reviewed_at AS date) AS day,
               COUNT(*) AS value
        FROM app.mistake_review_result
        WHERE user_id = :userId
          AND reviewed_at >= :fromAt
          AND reviewed_at < :toAt
        GROUP BY CAST(reviewed_at AS date)
        """;

    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final UserProfileCurrentRepository userProfileCurrentRepository;

    public UserProfileAnalyticsService(
        NamedParameterJdbcTemplate jdbcTemplate,
        UserProfileCurrentRepository userProfileCurrentRepository
    ) {
        this.jdbcTemplate = jdbcTemplate;
        this.userProfileCurrentRepository = userProfileCurrentRepository;
    }

    @Transactional(readOnly = true)
    public UserProfileAnalyticsResponse getAnalytics(
        JwtAuthenticatedUser currentUser,
        UUID requestedUserId,
        Integer requestedDays
    ) {
        if (!currentUser.userId().equals(requestedUserId)) {
            throw new ApplicationException("FORBIDDEN", "无权访问该用户画像分析", HttpStatus.FORBIDDEN);
        }

        int days = normalizeDays(requestedDays);
        LocalDate toDate = LocalDate.now();
        LocalDate fromDate = toDate.minusDays(days - 1L);
        ZoneId zoneId = ZoneId.systemDefault();
        OffsetDateTime fromAt = fromDate.atStartOfDay(zoneId).toOffsetDateTime();
        OffsetDateTime toAt = toDate.plusDays(1).atStartOfDay(zoneId).toOffsetDateTime();
        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("userId", requestedUserId)
            .addValue("fromAt", fromAt)
            .addValue("toAt", toAt);

        Map<LocalDate, TrendBuilder> trendByDay = initializeTrend(fromDate, toDate);
        mergeCount(trendByDay, queryCountByDay("qna_session", CONVERSATION_SQL, params), TrendBuilder::addConversations);
        mergeCount(trendByDay, queryCountByDay("smart_engine_task", SERVICE_TASK_SQL, params), TrendBuilder::addServiceTasks);
        mergePractice(trendByDay, queryPracticeByDay(params));
        mergeCount(trendByDay, queryCountByDay("mistake_record", MISTAKE_SQL, params), TrendBuilder::addNewMistakes);
        mergeCount(trendByDay, queryCountByDay("mistake_review_result", REVIEW_SQL, params), TrendBuilder::addReviews);

        List<ProfileBehaviorTrendPoint> trend = trendByDay.values()
            .stream()
            .map(TrendBuilder::toResponse)
            .toList();
        Map<String, Object> profile = userProfileCurrentRepository.findById(requestedUserId)
            .map(current -> current.getProfileJson() == null ? Map.<String, Object>of() : current.getProfileJson())
            .orElseGet(Map::of);
        ProfileSystemAnalysisResponse systemAnalysis = buildSystemAnalysis(profile, trend, days);

        return new UserProfileAnalyticsResponse(requestedUserId, days, fromDate, toDate, trend, systemAnalysis);
    }

    private int normalizeDays(Integer requestedDays) {
        if (requestedDays == null) {
            return DEFAULT_DAYS;
        }
        return Math.max(MIN_DAYS, Math.min(MAX_DAYS, requestedDays));
    }

    private Map<LocalDate, TrendBuilder> initializeTrend(LocalDate fromDate, LocalDate toDate) {
        Map<LocalDate, TrendBuilder> trendByDay = new LinkedHashMap<>();
        for (LocalDate day = fromDate; !day.isAfter(toDate); day = day.plusDays(1)) {
            trendByDay.put(day, new TrendBuilder(day));
        }
        return trendByDay;
    }

    private Map<LocalDate, Integer> queryCountByDay(String sourceName, String sql, MapSqlParameterSource params) {
        Map<LocalDate, Integer> counts = new LinkedHashMap<>();
        for (Map<String, Object> row : safeQuery(sourceName, sql, params)) {
            LocalDate day = readDay(row.get("day"));
            if (day != null) {
                counts.put(day, readInt(row.get("value")));
            }
        }
        return counts;
    }

    private Map<LocalDate, PracticeAggregate> queryPracticeByDay(MapSqlParameterSource params) {
        Map<LocalDate, PracticeAggregate> aggregates = new LinkedHashMap<>();
        for (Map<String, Object> row : safeQuery("practice_submission", PRACTICE_SQL, params)) {
            LocalDate day = readDay(row.get("day"));
            if (day != null) {
                aggregates.put(day, new PracticeAggregate(
                    readInt(row.get("submission_count")),
                    readInt(row.get("correct_count"))
                ));
            }
        }
        return aggregates;
    }

    private List<Map<String, Object>> safeQuery(String sourceName, String sql, MapSqlParameterSource params) {
        try {
            return jdbcTemplate.queryForList(sql, params);
        } catch (DataAccessException ex) {
            log.warn("Profile analytics source {} is unavailable: {}", sourceName, ex.getMessage());
            return List.of();
        }
    }

    private void mergeCount(
        Map<LocalDate, TrendBuilder> trendByDay,
        Map<LocalDate, Integer> counts,
        TrendCounterApplier applier
    ) {
        counts.forEach((day, count) -> {
            TrendBuilder builder = trendByDay.get(day);
            if (builder != null) {
                applier.apply(builder, count);
            }
        });
    }

    private void mergePractice(Map<LocalDate, TrendBuilder> trendByDay, Map<LocalDate, PracticeAggregate> aggregates) {
        aggregates.forEach((day, aggregate) -> {
            TrendBuilder builder = trendByDay.get(day);
            if (builder != null) {
                builder.addPractice(aggregate.submissionCount(), aggregate.correctCount());
            }
        });
    }

    private ProfileSystemAnalysisResponse buildSystemAnalysis(
        Map<String, Object> profile,
        List<ProfileBehaviorTrendPoint> trend,
        int days
    ) {
        List<SkillScore> skills = readSkillScores(profile);
        List<String> focusAreas = readFocusAreas(profile, skills);
        ProfileDataCoverageResponse coverage = buildCoverage(trend, skills.size(), focusAreas.size());
        SkillScore strongest = skills.stream().max(Comparator.comparingInt(SkillScore::score)).orElse(null);
        String strongestSkill = strongest != null && strongest.score() >= STRONG_SKILL_THRESHOLD ? strongest.topic() : null;
        Integer strongestSkillScore = strongestSkill == null ? null : strongest.score();
        boolean dataAvailable = coverage.activeDays() > 0 || coverage.profileSkillCount() > 0 || coverage.weakPointCount() > 0;

        return new ProfileSystemAnalysisResponse(
            strongestSkill,
            strongestSkillScore,
            focusAreas,
            coverage,
            buildSummary(coverage, days, dataAvailable),
            dataAvailable
        );
    }

    private ProfileDataCoverageResponse buildCoverage(
        List<ProfileBehaviorTrendPoint> trend,
        int profileSkillCount,
        int weakPointCount
    ) {
        int activeDays = 0;
        int conversationCount = 0;
        int serviceTaskCount = 0;
        int practiceSubmissionCount = 0;
        int newMistakeCount = 0;
        int reviewCount = 0;
        for (ProfileBehaviorTrendPoint point : trend) {
            int dayActivity = point.conversationCount()
                + point.serviceTaskCount()
                + point.practiceSubmissionCount()
                + point.newMistakeCount()
                + point.reviewCount();
            if (dayActivity > 0) {
                activeDays += 1;
            }
            conversationCount += point.conversationCount();
            serviceTaskCount += point.serviceTaskCount();
            practiceSubmissionCount += point.practiceSubmissionCount();
            newMistakeCount += point.newMistakeCount();
            reviewCount += point.reviewCount();
        }
        return new ProfileDataCoverageResponse(
            activeDays,
            conversationCount,
            serviceTaskCount,
            practiceSubmissionCount,
            newMistakeCount,
            reviewCount,
            profileSkillCount,
            weakPointCount
        );
    }

    private String buildSummary(ProfileDataCoverageResponse coverage, int days, boolean dataAvailable) {
        if (!dataAvailable) {
            return "近 %d 天暂无可聚合学习行为，系统尚未形成可分析证据。".formatted(days);
        }
        if (coverage.activeDays() == 0) {
            return "当前分析主要来自画像字段，近 %d 天暂无可聚合学习行为。".formatted(days);
        }
        return "近 %d 天聚合了 %d 次对话、%d 个学习服务任务、%d 次练习提交、%d 次错题复习。".formatted(
            days,
            coverage.conversationCount(),
            coverage.serviceTaskCount(),
            coverage.practiceSubmissionCount(),
            coverage.reviewCount()
        );
    }

    private List<SkillScore> readSkillScores(Map<String, Object> profile) {
        Map<String, Object> skillMastery = readRecord(firstValue(profile, "skillMastery", "skill_mastery"));
        if (skillMastery.isEmpty()) {
            return List.of();
        }
        return skillMastery.entrySet()
            .stream()
            .map(entry -> {
                Integer score = readScoreValue(entry.getValue());
                if (score == null) {
                    return null;
                }
                return new SkillScore(readString(entry.getKey()), score);
            })
            .filter(Objects::nonNull)
            .filter(item -> !item.topic().isBlank())
            .sorted(Comparator.comparingInt(SkillScore::score).reversed())
            .toList();
    }

    private List<String> readFocusAreas(Map<String, Object> profile, List<SkillScore> skills) {
        Set<String> focusAreas = new LinkedHashSet<>();
        Object weakPointDetails = firstValue(profile, "weakPointDetails", "weak_point_details");
        if (weakPointDetails instanceof List<?> items) {
            for (Object item : items) {
                Map<String, Object> record = readRecord(item);
                String topic = readString(firstValue(record, "topic", "knowledgeTag", "knowledge_tag"));
                if (!topic.isBlank()) {
                    focusAreas.add(topic);
                }
            }
        }

        for (String topic : readStringList(firstValue(profile, "weakPoints", "weak_points", "knowledgeGaps", "knowledge_gaps"))) {
            if (!topic.isBlank()) {
                focusAreas.add(topic);
            }
        }

        if (focusAreas.isEmpty()) {
            skills.stream()
                .filter(skill -> skill.score() < 60)
                .map(SkillScore::topic)
                .forEach(focusAreas::add);
        }

        return focusAreas.stream().limit(3).toList();
    }

    private Object firstValue(Map<String, Object> record, String... keys) {
        for (String key : keys) {
            if (record.containsKey(key)) {
                return record.get(key);
            }
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> readRecord(Object value) {
        if (value instanceof Map<?, ?> map) {
            Map<String, Object> record = new LinkedHashMap<>();
            map.forEach((key, item) -> {
                if (key != null) {
                    record.put(String.valueOf(key), item);
                }
            });
            return record;
        }
        return Map.of();
    }

    private List<String> readStringList(Object value) {
        if (value instanceof List<?> items) {
            List<String> result = new ArrayList<>();
            for (Object item : items) {
                String text = readString(item);
                if (!text.isBlank()) {
                    result.add(text);
                }
            }
            return result;
        }
        String text = readString(value);
        if (text.isBlank()) {
            return List.of();
        }
        return List.of(text.split("[、,，]"))
            .stream()
            .map(String::trim)
            .filter(item -> !item.isBlank())
            .toList();
    }

    private Integer readScoreValue(Object value) {
        Number number = readNumber(value);
        if (number == null) {
            Map<String, Object> record = readRecord(value);
            number = readNumber(firstValue(record, "score", "mastery", "value"));
        }
        if (number == null) {
            return null;
        }
        double raw = number.doubleValue();
        double percent = raw <= 1 ? raw * 100 : raw;
        return Math.max(0, Math.min(100, (int) Math.round(percent)));
    }

    private Number readNumber(Object value) {
        if (value instanceof Number number) {
            return number;
        }
        if (value instanceof String text && !text.isBlank()) {
            try {
                return Double.parseDouble(text);
            } catch (NumberFormatException ignored) {
                return null;
            }
        }
        return null;
    }

    private LocalDate readDay(Object value) {
        if (value instanceof LocalDate day) {
            return day;
        }
        if (value instanceof Date date) {
            return date.toLocalDate();
        }
        if (value instanceof Timestamp timestamp) {
            return timestamp.toLocalDateTime().toLocalDate();
        }
        if (value instanceof java.util.Date date) {
            return date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
        }
        if (value instanceof String text && !text.isBlank()) {
            return LocalDate.parse(text.substring(0, Math.min(10, text.length())));
        }
        return null;
    }

    private int readInt(Object value) {
        Number number = readNumber(value);
        return number == null ? 0 : Math.max(0, number.intValue());
    }

    private String readString(Object value) {
        return value == null ? "" : String.valueOf(value).trim();
    }

    private interface TrendCounterApplier {
        void apply(TrendBuilder builder, int count);
    }

    private record PracticeAggregate(int submissionCount, int correctCount) {
    }

    private record SkillScore(String topic, int score) {
    }

    private static final class TrendBuilder {
        private final LocalDate date;
        private int conversationCount;
        private int serviceTaskCount;
        private int practiceSubmissionCount;
        private int practiceCorrectCount;
        private int newMistakeCount;
        private int reviewCount;

        private TrendBuilder(LocalDate date) {
            this.date = date;
        }

        private void addConversations(int count) {
            conversationCount += count;
        }

        private void addServiceTasks(int count) {
            serviceTaskCount += count;
        }

        private void addPractice(int submissionCount, int correctCount) {
            this.practiceSubmissionCount += submissionCount;
            this.practiceCorrectCount += correctCount;
        }

        private void addNewMistakes(int count) {
            newMistakeCount += count;
        }

        private void addReviews(int count) {
            reviewCount += count;
        }

        private ProfileBehaviorTrendPoint toResponse() {
            Double practiceAccuracy = practiceSubmissionCount == 0
                ? null
                : Math.round((practiceCorrectCount * 1000.0) / practiceSubmissionCount) / 10.0;
            return new ProfileBehaviorTrendPoint(
                date,
                conversationCount,
                serviceTaskCount,
                practiceSubmissionCount,
                practiceAccuracy,
                newMistakeCount,
                reviewCount
            );
        }
    }
}
