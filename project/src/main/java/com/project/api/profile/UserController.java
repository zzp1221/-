package com.project.api.profile;

import com.project.api.profile.dto.UserProfileResponse;
import com.project.application.profile.UserProfileQueryService;
import com.project.security.AuthenticatedUserResolver;
import com.project.security.JwtAuthenticatedUser;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

/**
 * User-related read endpoints owned by the control plane.
 */
@RestController
@RequestMapping("/api/users")
@Tag(name = "Users")
public class UserController {

    private final UserProfileQueryService userProfileQueryService;

    public UserController(UserProfileQueryService userProfileQueryService) {
        this.userProfileQueryService = userProfileQueryService;
    }

    @GetMapping("/{userId}/profile/current")
    @Operation(summary = "Get the current profile of a user")
    public ResponseEntity<UserProfileResponse> getCurrentProfile(
        Authentication authentication,
        @PathVariable UUID userId
    ) {
        return ResponseEntity.ok(
            userProfileQueryService.getCurrentProfile(AuthenticatedUserResolver.require(authentication), userId)
        );
    }
}
