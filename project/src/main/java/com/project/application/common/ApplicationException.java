package com.project.application.common;

import org.springframework.http.HttpStatus;

/**
 * 面向领域的应用异常，携带稳定的 API 错误码和状态。
 */
public class ApplicationException extends RuntimeException {

    private final String code;
    private final HttpStatus status;

    public ApplicationException(String code, String message, HttpStatus status) {
        super(message);
        this.code = code;
        this.status = status;
    }

    public String getCode() {
        return code;
    }

    public HttpStatus getStatus() {
        return status;
    }
}
