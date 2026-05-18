package com.project.api.conversation.dto;

/**
 * 返回给前端的已上传聊天图片描述符。
 */
public record UploadedImageResponse(
    String imageUrl,
    String fileName,
    long sizeBytes,
    String contentType
) {
}
