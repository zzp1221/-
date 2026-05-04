package com.project.api.auth;

import com.project.api.auth.dto.AuthResponse;
import com.project.api.auth.dto.LoginRequest;
import com.project.api.auth.dto.RegisterRequest;
import com.project.api.auth.dto.UserView;
import com.project.api.common.dto.ApiMessageResponse;
import com.project.application.audit.AuditService;
import com.project.application.auth.AuthService;
import com.project.security.AuthenticatedUserResolver;
import com.project.security.JwtAuthenticatedUser;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Authentication API exposed by the Java control plane.
 */
@RestController
@RequestMapping("/api/auth")
@Tag(name = "Authentication")
public class AuthController {

    private final AuthService authService;
    private final AuditService auditService;

    public AuthController(AuthService authService, AuditService auditService) {
        this.authService = authService;
        this.auditService = auditService;
    }

    @PostMapping("/register")
    @Operation(summary = "Register a new user")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(authService.register(request));
    }

    @PostMapping("/login")
    @Operation(summary = "Login with loginId and password")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/logout")
    @Operation(summary = "Logout current user")
    public ResponseEntity<ApiMessageResponse> logout(Authentication authentication) {
        // Logout is stateless in the current JWT design, but the action is still audited.
        // Token invalidation/refresh rotation can be added later without changing the API contract.
        JwtAuthenticatedUser principal = AuthenticatedUserResolver.require(authentication);
        auditService.log("AUTH", "INFO", "用户退出登录", principal.userId(), null, java.util.Map.of());
        return ResponseEntity.ok(new ApiMessageResponse("SUCCESS", "退出成功"));
    }

    @GetMapping("/me")
    @Operation(summary = "Get current authenticated user")
    public ResponseEntity<UserView> me(Authentication authentication) {
        JwtAuthenticatedUser principal = AuthenticatedUserResolver.require(authentication);
        return ResponseEntity.ok(authService.getCurrentUser(principal));
    }
}
