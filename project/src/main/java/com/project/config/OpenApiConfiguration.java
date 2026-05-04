package com.project.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI bootstrap configuration.
 *
 * <p>The control plane owns all external HTTP contracts, so documenting those
 * contracts from day one reduces front-end/back-end drift during the competition
 * integration phase.</p>
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
