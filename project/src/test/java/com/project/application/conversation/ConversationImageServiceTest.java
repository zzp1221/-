package com.project.application.conversation;

import com.project.config.AppProperties;
import com.project.security.JwtProvider;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.time.Instant;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

class ConversationImageServiceTest {

    private static final Instant NOW = Instant.parse("2026-05-20T04:00:00Z");

    @TempDir
    Path tempDir;

    @Test
    void cleanupExpiredImagesDeletesImageFilesOlderThanTokenTtl() throws Exception {
        ConversationImageService service = service();
        Path userDir = createUserDir();
        Path image = writeFile(userDir.resolve("old.png"), NOW.minusSeconds(1_801));

        service.cleanupExpiredImages(NOW);

        assertThat(image).doesNotExist();
        assertThat(userDir).doesNotExist();
    }

    @Test
    void cleanupExpiredImagesKeepsImagesInsideTokenTtl() throws Exception {
        ConversationImageService service = service();
        Path userDir = createUserDir();
        Path image = writeFile(userDir.resolve("fresh.jpg"), NOW.minusSeconds(1_799));

        service.cleanupExpiredImages(NOW);

        assertThat(image).exists();
        assertThat(userDir).exists();
    }

    @Test
    void cleanupExpiredImagesKeepsNonImageFiles() throws Exception {
        ConversationImageService service = service();
        Path userDir = createUserDir();
        Path note = writeFile(userDir.resolve("note.txt"), NOW.minusSeconds(3_600));

        service.cleanupExpiredImages(NOW);

        assertThat(note).exists();
        assertThat(userDir).exists();
    }

    @Test
    void cleanupExpiredImagesRemovesEmptyUserDirectoriesOnly() throws Exception {
        ConversationImageService service = service();
        Path emptyDir = createUserDir();
        Path nonEmptyDir = createUserDir();
        Path retained = writeFile(nonEmptyDir.resolve("fresh.webp"), NOW.minusSeconds(60));

        service.cleanupExpiredImages(NOW);

        assertThat(emptyDir).doesNotExist();
        assertThat(nonEmptyDir).exists();
        assertThat(retained).exists();
    }

    private ConversationImageService service() {
        AppProperties properties = new AppProperties();
        properties.getUpload().setImageStorageDir(tempDir.toString());
        properties.getUpload().setImageTokenTtlSeconds(1_800);
        return new ConversationImageService(properties, mock(JwtProvider.class));
    }

    private Path createUserDir() throws Exception {
        Path userDir = tempDir.resolve(UUID.randomUUID().toString());
        Files.createDirectories(userDir);
        return userDir;
    }

    private Path writeFile(Path path, Instant modifiedAt) throws Exception {
        Files.writeString(path, "test");
        Files.setLastModifiedTime(path, FileTime.from(modifiedAt));
        return path;
    }
}
