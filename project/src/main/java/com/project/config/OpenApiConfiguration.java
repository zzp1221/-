package com.project.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI 引导配置。
 *
 * <p>控制平面拥有所有外部 HTTP 契约，从第一天起就记录这些契约
 * 可以减少比赛集成阶段的前后端偏差。</p>
 */
@Configuration
public class OpenApiConfiguration {

    @Bean
    public OpenAPI zhixueOpenApi() {
        return new OpenAPI().info(new Info()
            .title("Zhixue Control Plane API")
            .description("External Java control-plane API for the intelligent education competition system.")
            .version("v0.1.0")
            .contact(new Contact()
                .name("Zhixue Backend Team")
                .email("backend@example.local")));
    }
}
