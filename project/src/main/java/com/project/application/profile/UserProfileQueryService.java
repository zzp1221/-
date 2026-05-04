package com.project.application.profile;

import com.project.api.profile.dto.UserProfileResponse;
import com.project.application.common.ApplicationException;
import com.project.domain.profile.UserProfileCurrentRepository;
import com.project.security.JwtAuthenticatedUser;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.UUID;

/**
 * Read-only service for the current user profile projection.
 */
@Service
public class UserProfileQueryService {

    private final UserProfileCurrentRepository userProfileCurrentRepository;

    public UserProfileQueryService(UserProfileCurrentRepository userProfileCurrentRepository) {
        this.userProfileCurrentRepository = userProfileCurrentRepository;
    }

    @Transactional(readOnly = true)
    public UserProfileResponse getCurrentProfile(JwtAuthenticatedUser currentUser, UUID requestedUserId) {
        if (!currentUser.userId().equals(requestedUserId)) {
            throw new ApplicationException("FORBIDDEN", "无权访问该用户画像", HttpStatus.FORBIDDEN);
        }

        return userProfileCurrentRepository.findById(requestedUserId)
            .map(profile -> new UserProfileResponse(
                profile.getUserId(),
                profile.getProfileJson(),
                profile.getSummaryText(),
                profile.getUpdatedAt()
            ))
            .orElseGet(() -> new UserProfileResponse(
                requestedUserId,
                new LinkedHashMap<>(),
                "",
                OffsetDateTime.now()
            ));
    }
}
