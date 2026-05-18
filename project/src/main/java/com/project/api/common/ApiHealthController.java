package com.project.api.common;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * 轻量级 API 健康探测端点，供本地 Docker 冒烟检查使用。
 */
@RestController
@RequestMapping("/api/health")
public class ApiHealthController {

    @GetMapping
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }
}
