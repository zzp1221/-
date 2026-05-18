package com.project.application.profile;

import com.project.api.profile.dto.UserProfileResponse;
import com.project.application.common.ApplicationException;
import com.project.domain.profile.UserProfileCurrentRepository;
import com.project.domain.profile.UserProfileSnapshotRepository;
import com.project.security.JwtAuthenticatedUser;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Comparator;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.UUID;

/**
 * 当前用户画像投影的只读服务。
 */
@Service
public class UserProfileQueryService {

    private final UserProfileCurrentRepository userProfileCurrentRepository;
    private final UserProfileSnapshotRepository userProfileSnapshotRepository;

    public UserProfileQueryService(
        UserProfileCurrentRepository userProfileCurrentRepository,
        UserProfileSnapshotRepository userProfileSnapshotRepository
    ) {
        this.userProfileCurrentRepository = userProfileCurrentRepository;
        this.userProfileSnapshotRepository = userProfileSnapshotRepository;
    }

    @Transactional(readOnly = true)
    public UserProfileResponse getCurrentProfile(JwtAuthenticatedUser currentUser, UUID requestedUserId) {
        if (!currentUser.userId().equals(requestedUserId)) {
            throw new ApplicationException("FORBIDDEN", "无权访问该用户画像", HttpStatus.FORBIDDEN);
        }

        List<com.project.api.profile.dto.UserProfileHistoryPoint> history = userProfileSnapshotRepository
            .findTop8ByUserIdOrderByVersionDesc(requestedUserId)
            .stream()
            .sorted(Comparator.comparing(snapshot -> snapshot.getVersion() == null ? 0 : snapshot.getVersion()))
            .map(snapshot -> new com.project.api.profile.dto.UserProfileHistoryPoint(
                snapshot.getVersion(),
                snapshot.getProfileJson(),
                snapshot.getSummaryText(),
                snapshot.getConfidence(),
                snapshot.getCreatedAt()
            ))
            .toList();

        return userProfileCurrentRepository.findById(requestedUserId)
            .map(profile -> new UserProfileResponse(
                profile.getUserId(),
                profile.getProfileJson(),
                profile.getSummaryText(),
                profile.getUpdatedAt(),
                history
            ))
            .orElseGet(() -> new UserProfileResponse(
                requestedUserId,
                new LinkedHashMap<>(),
                "",
                OffsetDateTime.now(),
                history
            ));
    }
}
