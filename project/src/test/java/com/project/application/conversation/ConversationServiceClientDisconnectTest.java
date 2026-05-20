package com.project.application.conversation;

import org.apache.catalina.connector.ClientAbortException;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.context.request.async.AsyncRequestNotUsableException;

import java.io.IOException;

import static org.assertj.core.api.Assertions.assertThat;

class ConversationServiceClientDisconnectTest {

    private final ConversationService conversationService = new ConversationService(null, null, null, null, null);

    @Test
    void detectsSpringAsyncRequestNotUsableExceptionInCauseChain() {
        RuntimeException wrapped = new RuntimeException(new AsyncRequestNotUsableException("response unavailable"));

        assertThat(isClientDisconnect(wrapped)).isTrue();
    }

    @Test
    void detectsTomcatClientAbortExceptionInCauseChain() {
        RuntimeException wrapped = new RuntimeException(new ClientAbortException(new IOException("socket closed")));

        assertThat(isClientDisconnect(wrapped)).isTrue();
    }

    @Test
    void doesNotDetectClientDisconnectFromIOExceptionMessageText() {
        assertThat(isClientDisconnect(new IOException("broken pipe"))).isFalse();
        assertThat(isClientDisconnect(new IOException("AsyncRequestNotUsableException"))).isFalse();
    }

    private boolean isClientDisconnect(Throwable throwable) {
        Boolean result = ReflectionTestUtils.invokeMethod(
            conversationService,
            "isClientDisconnect",
            throwable
        );
        return Boolean.TRUE.equals(result);
    }
}
