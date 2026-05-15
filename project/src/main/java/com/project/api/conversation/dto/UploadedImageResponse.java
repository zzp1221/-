package com.project.api.conversation.dto;

/**
 * Uploaded chat image descriptor returned to the frontend.
 */
public record UploadedImageResponse(
    String imageUrl,
    String fileName,
    long sizeBytes,
    String contentType
) {
}
