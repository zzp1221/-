import { API_BASE_URL, getAuthHeaders, request } from './request';
import type { AxiosRequestConfig } from 'axios';
import { streamSse } from './sse';

export interface CreateConversationResponse {
  conversationId: string;
  title?: string;
}

export interface ConversationMessageStreamRequest {
  message: string;
  serviceType?: string;
}

export interface ConversationHistoryItem {
  conversationId: string;
  title: string;
  lastMessagePreview?: string;
  messageCount?: number;
  lastMessageAt?: string;
  updatedAt?: string;
}

export interface ConversationDialogState {
  conversationId: string;
  turnId: string;
  pedagogyStrategy?: string;
  nextAction?: string;
}

export interface ConversationMessageItem {
  messageId: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt?: string;
}

export interface ConversationStreamEventPayload {
  eventType?: string;
  sequence?: number;
  occurredAt?: string;
  event?: string;
  seq?: number;
  timestamp?: string;
  dialogState?: ConversationDialogState;
  payload?: Record<string, unknown>;
}

export interface ConversationStreamEvent {
  event: string;
  data: ConversationStreamEventPayload;
}

export const conversationApi = {
  async listRecentConversations(): Promise<ConversationHistoryItem[]> {
    return request.get<ConversationHistoryItem[]>('/api/conversations', {
      dedupe: true,
      dedupeKey: 'recent-conversations',
    });
  },

  async createConversation(): Promise<CreateConversationResponse> {
    return request.post<CreateConversationResponse>('/api/conversations');
  },

  async getConversationMessages(
    conversationId: string,
    config?: AxiosRequestConfig & { dedupe?: boolean; retry?: number },
  ): Promise<ConversationMessageItem[]> {
    return request.get<ConversationMessageItem[]>(`/api/conversations/${conversationId}/messages`, {
      ...config,
      dedupe: config?.dedupe ?? true,
      dedupeKey: `conversation-messages:${conversationId}`,
    });
  },

  async streamMessage(
    conversationId: string,
    request: ConversationMessageStreamRequest,
    handlers: {
      onOpen?: () => void;
      onEvent: (event: ConversationStreamEvent) => void;
      onDone: () => void;
      onError: (error: Error) => void;
    },
    signal?: AbortSignal,
  ): Promise<void> {
    await streamSse(`${API_BASE_URL}/api/conversations/${conversationId}/messages/stream`, {
      init: {
        method: 'POST',
        headers: {
          Accept: 'text/event-stream',
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(request),
        signal,
      },
      missingBodyMessage: '无法读取会话流',
      requestFailedMessage: (status) => status === 429
        ? '请求过于频繁 (429)，请稍后重试'
        : `会话请求失败 (${status})`,
      maxRetries: 2,
      onRetry: (_attempt, maxRetries) => {
        handlers.onEvent({
          event: 'retry',
          data: { payload: { text: `连接中断，正在重连 (${_attempt}/${maxRetries})...` } },
        });
      },
      onOpen: handlers.onOpen,
      onEvent: (rawEvent) => {
        const parsed: ConversationStreamEvent = {
          event: rawEvent.event,
          data: parsePayload(rawEvent.data),
        };
        handlers.onEvent(parsed);
        if (parsed.event === 'done') {
          handlers.onDone();
          return true;
        }
        if (parsed.event === 'error') {
          const message = readConversationMessage(parsed.data) || '会话流执行失败';
          handlers.onError(new Error(message));
          return true;
        }
        return false;
      },
      onDone: handlers.onDone,
      onError: handlers.onError,
    });
  },
};

function parsePayload(rawData: string): ConversationStreamEventPayload {
  try {
    const parsed = JSON.parse(rawData) as ConversationStreamEventPayload;
    return {
      ...parsed,
      eventType: parsed.eventType ?? parsed.event,
      sequence: parsed.sequence ?? parsed.seq,
      occurredAt: parsed.occurredAt ?? parsed.timestamp,
    };
  } catch {
    return {
      payload: {
        text: rawData,
      },
    };
  }
}

function readConversationMessage(data: ConversationStreamEventPayload): string {
  const payload = data.payload;
  const text = payload?.text;
  if (typeof text === 'string' && text.trim()) {
    return text.trim();
  }
  const message = payload?.message;
  if (typeof message === 'string' && message.trim()) {
    return message.trim();
  }
  return '';
}
