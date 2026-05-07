import { API_BASE_URL, getAuthHeaders, request } from './request';
import type { AxiosRequestConfig } from 'axios';
import { streamSse } from './sse';

export type SmartEngineServiceType =
  | 'RESOURCE_GENERATION'
  | 'PATH_PLANNING'
  | 'RESOURCE_PUSH'
  | 'LEARNING_EVALUATION'
  | 'EVALUATION'
  | 'VIDEO_GENERATION'
  | 'TUTORING'
  | 'PROFILE_BUILD'
  | 'PRACTICE_JUDGE';

export interface SmartEngineSubmitRequest {
  conversationId: string;
  serviceType: SmartEngineServiceType;
  params: Record<string, unknown>;
}

export interface SmartEngineSubmitResponse {
  taskId: string;
  status?: string;
}

export interface SmartEngineTaskResponse {
  taskId: string;
  traceId?: string;
  serviceType?: string;
  status?: string;
  currentStage?: string;
  progress?: number;
  progressPercent?: number;
  errorCode?: string;
  errorMessage?: string;
  result?: unknown;
  responseSummary?: Record<string, unknown>;
}

export type SmartEngineStreamEventType =
  | 'progress'
  | 'result_chunk'
  | 'resource_file'
  | 'question_batch'
  | 'judge_result'
  | 'done'
  | 'error'
  | 'video_gen:start'
  | 'video_gen:script'
  | 'video_gen:speech'
  | 'video_gen:avatar'
  | 'video_gen:complete';

export interface SmartEngineStreamEvent {
  event: SmartEngineStreamEventType;
  data: string;
}

export interface UserProfileResponse {
  userId: string;
  profile?: Record<string, unknown>;
  summary?: string;
  updatedAt?: string;
  history?: Array<{
    version?: number;
    profile?: Record<string, unknown>;
    summary?: string;
    confidence?: number;
    updatedAt?: string;
  }>;
}

export const smartEngineApi = {
  submit(payload: SmartEngineSubmitRequest): Promise<SmartEngineSubmitResponse> {
    return request.post<SmartEngineSubmitResponse>('/api/smart-engine/submit', payload);
  },

  getTask(taskId: string, config?: AxiosRequestConfig & { dedupe?: boolean; retry?: number }): Promise<SmartEngineTaskResponse> {
    return request.get<SmartEngineTaskResponse>(`/api/smart-engine/tasks/${taskId}`, config);
  },

  getTaskStreamUrl(taskId: string): string {
    return `/api/smart-engine/tasks/${taskId}/stream`;
  },

  async streamTask(
    taskId: string,
    handlers: {
      onEvent: (event: SmartEngineStreamEvent) => void;
      onDone: () => void;
      onError: (error: Error) => void;
    },
    signal?: AbortSignal,
  ): Promise<void> {
    await streamSse(`${API_BASE_URL}${this.getTaskStreamUrl(taskId)}`, {
      init: {
        method: 'GET',
        headers: {
          Accept: 'text/event-stream',
          ...getAuthHeaders(),
        },
        signal,
      },
      missingBodyMessage: '无法读取任务流',
      requestFailedMessage: (status) => `任务流请求失败 (${status})`,
      defaultEvent: 'result_chunk',
      onEvent: (rawEvent) => {
        const parsed: SmartEngineStreamEvent = {
          event: rawEvent.event as SmartEngineStreamEventType,
          data: rawEvent.data,
        };
        handlers.onEvent(parsed);
        if (parsed.event === 'done') {
          handlers.onDone();
          return true;
        }
        if (parsed.event === 'error') {
          handlers.onError(new Error(parsed.data || '任务流执行失败'));
          return true;
        }
        return false;
      },
      onDone: handlers.onDone,
      onError: handlers.onError,
    });
  },

  getCurrentProfile(userId: string): Promise<UserProfileResponse> {
    return request.get<UserProfileResponse>(`/api/users/${userId}/profile/current`);
  },
};
