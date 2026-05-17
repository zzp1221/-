import { Suspense, lazy, useCallback, useEffect, useRef, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { conversationApi, type ConversationMessageItem } from '../api/conversation';
import { smartEngineApi } from '../api/smartEngine';
import { getErrorMessage } from '../api/request';
import type { LayoutOutletContext } from '../components/Layout';
import QnaChatView from './QnaChatView';
import {
  QNA_GREETING,
  defaultAssessmentDimensions,
  defaultResourceForm,
  serviceButtons,
  serviceTypeMap,
  type AssessmentForm,
  type ChatMessage,
  type EngineService,
  type EngineState,
  type EngineTaskSnapshot,
  type PathForm,
  type PendingChatImage,
  type ProfileSnapshot,
  type ProfileUpdateSource,
  type PracticeQuestionBatch,
  type PushForm,
  type QnaState,
  type ResourceForm,
} from './LearningStudioDemoPage.types';
import {
  buildServiceParams,
  cleanupStreamSchedulers,
  mapProfileResponse,
  readConversationChunk,
  runByApiTask,
  sanitizeConversationMessageContent,
  toUiTaskStatus,
} from './LearningStudioDemoPage.utils';

const RealtimeProfile = lazy(() =>
  import('./LearningStudioDemoPage.components').then((module) => ({ default: module.RealtimeProfile }))
);
const ServiceDynamicForm = lazy(() =>
  import('./LearningStudioDemoPage.components').then((module) => ({ default: module.ServiceDynamicForm }))
);
const ServiceSubmitPanel = lazy(() =>
  import('./LearningStudioDemoPage.components').then((module) => ({ default: module.ServiceSubmitPanel }))
);
const TaskResultPanel = lazy(() =>
  import('./LearningStudioDemoPage.components').then((module) => ({ default: module.TaskResultPanel }))
);

const ENGINE_TASK_STORAGE_KEY = 'learning_studio_engine_tasks';
const QNA_SNAPSHOT_STORAGE_KEY = 'learning_studio_qna_snapshot';
const QNA_CONVERSATION_CACHE_STORAGE_KEY = 'learning_studio_qna_cache';
const SELECTED_CONVERSATION_STORAGE_KEY = 'learning_studio_selected_conversation';
const ACTIVE_CONVERSATION_ID_STORAGE_KEY = 'learning_studio_active_conversation_id';

interface SelectedConversationSnapshot {
  conversationId: string;
  title?: string;
  lastMessagePreview?: string;
}

function mapConversationHistory(history: ConversationMessageItem[]): ChatMessage[] {
  const messages: ChatMessage[] = history
    .map((item, index) => ({
      id: item.messageId || `history-${index}`,
      role: (item.role === 'user' ? 'user' : 'assistant') as ChatMessage['role'],
      content: item.role === 'user'
        ? item.content?.trim() ?? ''
        : sanitizeConversationMessageContent(item.content ?? ''),
    }))
    .filter((item) => item.content);

  return messages.length > 0
    ? messages
    : [{ id: 'qna-greeting', role: 'assistant', content: QNA_GREETING }];
}

interface PersistedEngineTaskSnapshot {
  selectedService: EngineService | null;
  conversationId: string;
  snapshots: Record<EngineService, EngineTaskSnapshot>;
}

interface PersistedQnaSnapshot {
  conversationId: string;
  qnaInput: string;
  qnaState: QnaState;
  qnaMessages: ChatMessage[];
}

interface PersistedConversationViewSnapshot {
  qnaInput: string;
  qnaMessages: ChatMessage[];
  qnaState?: QnaState;
}

type QnaDrafts = Record<string, string>;
type PersistedQnaConversationCache = Record<string, PersistedConversationViewSnapshot>;

function conversationCacheKey(conversationId: string): string {
  const normalized = conversationId.trim();
  return normalized || '__new__';
}

function pickPreferredConversationMessages(
  cachedMessages: ChatMessage[] | undefined,
  fetchedMessages: ChatMessage[],
): ChatMessage[] {
  if (!cachedMessages || cachedMessages.length === 0) {
    return fetchedMessages;
  }
  const cachedTextLength = cachedMessages.reduce((sum, item) => sum + item.content.length, 0);
  const fetchedTextLength = fetchedMessages.reduce((sum, item) => sum + item.content.length, 0);
  if (cachedMessages.length > fetchedMessages.length || cachedTextLength > fetchedTextLength) {
    return cachedMessages;
  }
  return fetchedMessages;
}

function isProcessingOnlyAssistantContent(content: string): boolean {
  const lines = content
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
  return lines.length > 0 && lines.every((line) => line.startsWith('[处理中]'));
}

function hasPendingAssistantResponse(messages?: ChatMessage[]): boolean {
  const lastMessage = messages?.[messages.length - 1];
  if (!lastMessage || lastMessage.role !== 'assistant') {
    return false;
  }
  const content = lastMessage.content.trim();
  return !content || isProcessingOnlyAssistantContent(content);
}

function hasResolvedAssistantResponse(messages: ChatMessage[]): boolean {
  const lastMessage = messages[messages.length - 1];
  return Boolean(
    lastMessage
      && lastMessage.role === 'assistant'
      && lastMessage.content.trim()
      && !isProcessingOnlyAssistantContent(lastMessage.content),
  );
}

function createEmptyEngineTaskSnapshot(baseState: EngineState = 'ENGINE_IDLE'): EngineTaskSnapshot {
  return {
    engineState: baseState,
    taskId: '',
    taskProgress: 0,
    taskStatus: '未提交',
    taskSummary: '',
    serviceResultLines: [],
    downloadLinks: [],
    videoResult: null,
    inlineResource: null,
    practiceBatch: null,
    judgeResult: null,
  };
}

function createInitialEngineSnapshots(): Record<EngineService, EngineTaskSnapshot> {
  return {
    resource: createEmptyEngineTaskSnapshot(),
    path: createEmptyEngineTaskSnapshot(),
    push: createEmptyEngineTaskSnapshot(),
    assessment: createEmptyEngineTaskSnapshot(),
  };
}

function isTaskTerminal(snapshot: EngineTaskSnapshot): boolean {
  return snapshot.engineState === 'ENGINE_COMPLETED' || snapshot.engineState === 'ENGINE_FAILED';
}

function hasLockedTask(snapshot: EngineTaskSnapshot): boolean {
  return Boolean(snapshot.taskId) && !isTaskTerminal(snapshot);
}

function dedupeResultLines(lines: string[]): string[] {
  const seen = new Set<string>();
  const normalized: string[] = [];
  for (const raw of lines) {
    const line = String(raw).trim();
    if (!line || seen.has(line)) {
      continue;
    }
    seen.add(line);
    normalized.push(line);
  }
  return normalized;
}

function sanitizeEngineSnapshot(snapshot: EngineTaskSnapshot): EngineTaskSnapshot {
  const normalized: EngineTaskSnapshot = {
    ...snapshot,
    serviceResultLines: dedupeResultLines(snapshot.serviceResultLines),
  };
  if (normalized.engineState === 'ENGINE_SUBMITTING' && !normalized.taskId) {
    return createEmptyEngineTaskSnapshot('ENGINE_FORM_EDITING');
  }
  return normalized;
}

function buildPersistedEngineSnapshots(
  selectedService: EngineService | null,
  snapshots: Record<EngineService, EngineTaskSnapshot>,
): Record<EngineService, EngineTaskSnapshot> {
  const next = createInitialEngineSnapshots();
  (Object.entries(snapshots) as Array<[EngineService, EngineTaskSnapshot]>).forEach(([service, snapshot]) => {
    const normalized = sanitizeEngineSnapshot(snapshot);
    const shouldPersist = service === selectedService || hasLockedTask(normalized);
    next[service] = shouldPersist ? normalized : createEmptyEngineTaskSnapshot();
  });
  return next;
}

function normalizeRestoredQnaMessages(snapshot: PersistedQnaSnapshot): ChatMessage[] {
  if (!Array.isArray(snapshot.qnaMessages) || snapshot.qnaMessages.length === 0) {
    return [{ id: 'qna-greeting', role: 'assistant', content: QNA_GREETING }];
  }
  if (snapshot.qnaState !== 'QNA_STREAMING') {
    return snapshot.qnaMessages;
  }

  const normalized = [...snapshot.qnaMessages];
  const lastAssistantIndex = [...normalized]
    .map((item, index) => ({ item, index }))
    .reverse()
    .find(({ item }) => item.role === 'assistant' && !item.content.trim())?.index;

  if (lastAssistantIndex === undefined) {
    return normalized;
  }

  normalized[lastAssistantIndex] = {
    ...normalized[lastAssistantIndex],
    content: '上一条回复未完整加载，你可以继续提问，或重新发送上一条问题。',
  };
  return normalized;
}

function buildConversationSyncSignature(messages: ChatMessage[]): string {
  return messages.map((item) => `${item.role}:${item.content}`).join('\u0001');
}

export default function LearningStudioDemoPage({ mode }: { mode: 'qna' | 'engine' }) {
  const { isAuthenticated, currentUser, openAuthModal } = useOutletContext<LayoutOutletContext>();
  const pendingActionRef = useRef<null | (() => void)>(null);
  const qnaAbortRef = useRef<AbortController | null>(null);
  const taskMonitorRefsRef = useRef<Record<EngineService, {
    taskStreamAbortRef: { current: AbortController | null };
    streamQueueRef: { current: string[] };
    streamFlushTimerRef: { current: number | null };
    streamRafRef: { current: number | null };
  }>>({
    resource: {
      taskStreamAbortRef: { current: null },
      streamQueueRef: { current: [] },
      streamFlushTimerRef: { current: null },
      streamRafRef: { current: null },
    },
    path: {
      taskStreamAbortRef: { current: null },
      streamQueueRef: { current: [] },
      streamFlushTimerRef: { current: null },
      streamRafRef: { current: null },
    },
    push: {
      taskStreamAbortRef: { current: null },
      streamQueueRef: { current: [] },
      streamFlushTimerRef: { current: null },
      streamRafRef: { current: null },
    },
    assessment: {
      taskStreamAbortRef: { current: null },
      streamQueueRef: { current: [] },
      streamFlushTimerRef: { current: null },
      streamRafRef: { current: null },
    },
  });
  const activeTaskMonitorsRef = useRef<Partial<Record<EngineService, string>>>({});
  const qnaMessagesRef = useRef<ChatMessage[]>([{ id: 'qna-greeting', role: 'assistant', content: QNA_GREETING }]);
  const qnaInputRef = useRef('');
  const qnaStateRef = useRef<QnaState>('QNA_IDLE');
  const conversationIdRef = useRef('');
  const mountedRef = useRef(true);
  const engineSnapshotHydratedRef = useRef(false);
  const qnaSnapshotHydratedRef = useRef(false);
  const loadingConversationIdRef = useRef('');
  const qnaDraftsRef = useRef<QnaDrafts>({});
  const qnaConversationCacheRef = useRef<PersistedQnaConversationCache>({});
  const qnaStreamTokensRef = useRef<Record<string, string>>({});
  const qnaRequestVersionRef = useRef(0);
  const engineSubmitVersionRef = useRef(0);
  const previousModeRef = useRef(mode);

  const [profile, setProfile] = useState<ProfileSnapshot | null>(null);
  const [profileSummary, setProfileSummary] = useState('');
  const [profileUpdatedAt, setProfileUpdatedAt] = useState('');
  const [profileSource, setProfileSource] = useState<ProfileUpdateSource>('BACKEND');
  const [showAllWeakPoints, setShowAllWeakPoints] = useState(false);

  const [qnaState, setQnaState] = useState<QnaState>('QNA_IDLE');
  const [qnaMessages, setQnaMessages] = useState<ChatMessage[]>([{ id: 'qna-greeting', role: 'assistant', content: QNA_GREETING }]);
  const [qnaInput, setQnaInput] = useState('');
  const [pendingQnaImages, setPendingQnaImages] = useState<PendingChatImage[]>([]);
  const [qnaImageError, setQnaImageError] = useState('');
  const [qnaWebSearchEnabled, setQnaWebSearchEnabled] = useState(false);
  const [deepReasoningEnabled, setDeepReasoningEnabled] = useState(false);
  const [conversationId, setConversationId] = useState('');

  const [selectedService, setSelectedService] = useState<EngineService | null>(null);
  const [serviceSnapshots, setServiceSnapshots] = useState<Record<EngineService, EngineTaskSnapshot>>(createInitialEngineSnapshots);
  const [resourceForm, setResourceForm] = useState<ResourceForm>(defaultResourceForm);
  const [pathForm, setPathForm] = useState<PathForm>({
    targetPeriod: '14 天',
    weeklyHours: '8',
    currentProgress: '已完成基础概念，准备进入案例训练',
  });
  const [pushForm, setPushForm] = useState<PushForm>({
    preferredType: 'CODE_CASE',
  });
  const [assessmentForm, setAssessmentForm] = useState<AssessmentForm>({
    dimensions: defaultAssessmentDimensions,
  });

  const qnaBusy = qnaState === 'QNA_STREAMING';
  const hasStartedConversation = Boolean(conversationId) || qnaMessages.length > 1 || qnaMessages.some((item) => item.role === 'user');
  const activeEngineSnapshot = selectedService ? serviceSnapshots[selectedService] : createEmptyEngineTaskSnapshot();
  const engineBusy = selectedService ? hasLockedTask(activeEngineSnapshot) : false;
  const taskId = activeEngineSnapshot.taskId;
  const taskProgress = activeEngineSnapshot.taskProgress;
  const taskStatus = activeEngineSnapshot.taskStatus;
  const taskSummary = activeEngineSnapshot.taskSummary;
  const serviceResultLines = activeEngineSnapshot.serviceResultLines;
  const downloadLinks = activeEngineSnapshot.downloadLinks;
  const videoResult = activeEngineSnapshot.videoResult;
  const engineStateView = selectedService ? activeEngineSnapshot.engineState : 'ENGINE_IDLE';

  const clearPersistedEngineSnapshot = useCallback(() => {
    if (typeof window === 'undefined') {
      return;
    }
    window.sessionStorage.removeItem(ENGINE_TASK_STORAGE_KEY);
  }, []);

  const clearPersistedQnaSnapshot = useCallback(() => {
    if (typeof window === 'undefined') {
      return;
    }
    window.sessionStorage.removeItem(QNA_SNAPSHOT_STORAGE_KEY);
  }, []);

  const persistQnaConversationCache = useCallback(() => {
    if (typeof window === 'undefined') {
      return;
    }
    window.sessionStorage.setItem(
      QNA_CONVERSATION_CACHE_STORAGE_KEY,
      JSON.stringify(qnaConversationCacheRef.current),
    );
  }, []);

  const cacheConversationView = useCallback((
    targetConversationId: string,
    snapshot: PersistedConversationViewSnapshot,
  ) => {
    qnaConversationCacheRef.current[conversationCacheKey(targetConversationId)] = snapshot;
    persistQnaConversationCache();
  }, [persistQnaConversationCache]);

  const setQnaStateView = useCallback((nextState: QnaState) => {
    qnaStateRef.current = nextState;
    setQnaState(nextState);
  }, []);

  const updateQnaConversationMessages = useCallback((
    targetConversationId: string,
    updater: (messages: ChatMessage[]) => ChatMessage[],
    options: { qnaInput?: string; qnaState?: QnaState } = {},
  ) => {
    const normalizedConversationId = targetConversationId.trim();
    const cacheKey = conversationCacheKey(normalizedConversationId);
    const cachedSnapshot = qnaConversationCacheRef.current[cacheKey];
    const isVisibleConversation = conversationIdRef.current === normalizedConversationId;
    const sourceMessages = isVisibleConversation
      ? qnaMessagesRef.current
      : cachedSnapshot?.qnaMessages ?? [];
    const nextMessages = updater(sourceMessages);
    const nextSnapshot: PersistedConversationViewSnapshot = {
      qnaInput: options.qnaInput ?? cachedSnapshot?.qnaInput ?? (isVisibleConversation ? qnaInputRef.current : ''),
      qnaMessages: nextMessages,
      qnaState: options.qnaState ?? cachedSnapshot?.qnaState ?? (isVisibleConversation ? qnaStateRef.current : 'QNA_IDLE'),
    };

    cacheConversationView(normalizedConversationId, nextSnapshot);

    if (!isVisibleConversation || !mountedRef.current) {
      return;
    }
    qnaMessagesRef.current = nextMessages;
    setQnaMessages(nextMessages);
    if (options.qnaInput !== undefined) {
      qnaInputRef.current = options.qnaInput;
      setQnaInput(options.qnaInput);
    }
    if (options.qnaState !== undefined) {
      setQnaStateView(options.qnaState);
    }
  }, [cacheConversationView, setQnaStateView]);

  const updateServiceSnapshot = useCallback(
    (
      service: EngineService,
      updater: EngineTaskSnapshot | ((current: EngineTaskSnapshot) => EngineTaskSnapshot),
    ) => {
      setServiceSnapshots((prev) => {
        const current = prev[service];
        const next = typeof updater === 'function' ? updater(current) : updater;
        return {
          ...prev,
          [service]: next,
        };
      });
    },
    [],
  );

  const resetQnaConversation = useCallback(() => {
    qnaRequestVersionRef.current += 1;
    qnaAbortRef.current = null;
    cacheConversationView(conversationIdRef.current, {
      qnaInput: qnaInputRef.current,
      qnaMessages: qnaMessagesRef.current,
      qnaState: qnaStateRef.current,
    });
    const nextMessages: ChatMessage[] = [{ id: 'qna-greeting', role: 'assistant', content: QNA_GREETING }];
    const nextInput = qnaDraftsRef.current.__new__ ?? '';
    conversationIdRef.current = '';
    qnaMessagesRef.current = nextMessages;
    qnaInputRef.current = nextInput;
    setConversationId('');
    setQnaMessages(nextMessages);
    setQnaInput(nextInput);
    setQnaWebSearchEnabled(false);
    setQnaStateView('QNA_IDLE');
    clearPersistedQnaSnapshot();
    if (typeof window !== 'undefined') {
      window.sessionStorage.removeItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY);
    }
    window.dispatchEvent(new CustomEvent('app:active-conversation-changed', { detail: { conversationId: '' } }));
  }, [cacheConversationView, clearPersistedQnaSnapshot]);

  const resetEngineView = useCallback(() => {
    engineSubmitVersionRef.current += 1;
    Object.values(taskMonitorRefsRef.current).forEach((refs) => {
      refs.taskStreamAbortRef.current?.abort();
      refs.taskStreamAbortRef.current = null;
      refs.streamQueueRef.current = [];
      cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    });
    activeTaskMonitorsRef.current = {};
    setConversationId('');
    setSelectedService(null);
    setServiceSnapshots(createInitialEngineSnapshots());
    clearPersistedEngineSnapshot();
  }, [clearPersistedEngineSnapshot]);

  useEffect(() => {
    qnaMessagesRef.current = qnaMessages;
  }, [qnaMessages]);

  useEffect(() => {
    qnaInputRef.current = qnaInput;
    qnaDraftsRef.current[conversationIdRef.current || '__new__'] = qnaInput;
  }, [qnaInput]);

  useEffect(() => {
    qnaStateRef.current = qnaState;
  }, [qnaState]);

  useEffect(() => {
    if (mode !== 'qna' || typeof window === 'undefined') {
      return;
    }
    const raw = window.sessionStorage.getItem(QNA_CONVERSATION_CACHE_STORAGE_KEY);
    if (!raw) {
      return;
    }
    try {
      qnaConversationCacheRef.current = JSON.parse(raw) as PersistedQnaConversationCache;
    } catch {
      qnaConversationCacheRef.current = {};
      window.sessionStorage.removeItem(QNA_CONVERSATION_CACHE_STORAGE_KEY);
    }
  }, [mode]);

  useEffect(() => {
    conversationIdRef.current = conversationId;
    if (typeof window !== 'undefined') {
      if (conversationId) {
        window.sessionStorage.setItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY, conversationId);
      } else {
        window.sessionStorage.removeItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY);
      }
    }
    window.dispatchEvent(new CustomEvent('app:active-conversation-changed', { detail: { conversationId } }));
  }, [conversationId]);

  const syncConversationHistory = useCallback(async ({
    targetConversationId,
    requestVersion,
    cachedMessages,
    nextInput,
    expectStreaming = false,
  }: {
    targetConversationId: string;
    requestVersion?: number;
    cachedMessages?: ChatMessage[];
    nextInput?: string;
    expectStreaming?: boolean;
  }): Promise<boolean> => {
    const normalizedConversationId = targetConversationId.trim();
    if (!normalizedConversationId) {
      return false;
    }

    let latestMessages = cachedMessages;
    let previousSignature = latestMessages ? buildConversationSyncSignature(latestMessages) : '';
    let unchangedPolls = 0;
    const maxAttempts = expectStreaming ? 360 : 1;

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      const history = await conversationApi.getConversationMessages(normalizedConversationId, {
        dedupe: false,
        retry: 1,
      });
      if (!mountedRef.current || conversationIdRef.current !== normalizedConversationId) {
        return Boolean(latestMessages?.length);
      }
      if (requestVersion !== undefined && qnaRequestVersionRef.current !== requestVersion) {
        return Boolean(latestMessages?.length);
      }

      const mapped = mapConversationHistory(history);
      if (mapped.length > 0) {
        const mappedHasResolvedAssistant = hasResolvedAssistantResponse(mapped);
        const preferredMessages = mappedHasResolvedAssistant
          ? mapped
          : pickPreferredConversationMessages(latestMessages, mapped);
        const nextState: QnaState =
          expectStreaming && hasPendingAssistantResponse(preferredMessages) && !mappedHasResolvedAssistant
            ? 'QNA_STREAMING'
            : 'QNA_IDLE';
        latestMessages = preferredMessages;
        qnaMessagesRef.current = preferredMessages;
        setQnaMessages(preferredMessages);
        if (expectStreaming) {
          setQnaStateView(nextState);
        }
        cacheConversationView(normalizedConversationId, {
          qnaInput: nextInput ?? qnaInputRef.current,
          qnaMessages: preferredMessages,
          qnaState: nextState,
        });

        const currentSignature = buildConversationSyncSignature(preferredMessages);
        if (currentSignature === previousSignature) {
          unchangedPolls += 1;
        } else {
          previousSignature = currentSignature;
          unchangedPolls = 0;
        }

        if (
          !expectStreaming
          || mappedHasResolvedAssistant
          || (attempt >= 2 && unchangedPolls >= 2 && !hasPendingAssistantResponse(preferredMessages))
        ) {
          return true;
        }
      }

      if (attempt < maxAttempts - 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 2000));
      }
    }

    return Boolean(latestMessages?.length);
  }, [cacheConversationView, setQnaStateView]);

  const openExistingConversation = useCallback(async (payload: SelectedConversationSnapshot) => {
    const nextConversationId = payload.conversationId?.trim();
    if (!nextConversationId) {
      return;
    }
    if (loadingConversationIdRef.current === nextConversationId) {
      return;
    }
    qnaRequestVersionRef.current += 1;
    const requestVersion = qnaRequestVersionRef.current;
    loadingConversationIdRef.current = nextConversationId;
    qnaDraftsRef.current[conversationIdRef.current || '__new__'] = qnaInputRef.current;
    cacheConversationView(conversationIdRef.current, {
      qnaInput: qnaInputRef.current,
      qnaMessages: qnaMessagesRef.current,
      qnaState: qnaStateRef.current,
    });
    const cachedSnapshot = qnaConversationCacheRef.current[conversationCacheKey(nextConversationId)];
    const shouldResumeStreaming =
      cachedSnapshot?.qnaState === 'QNA_STREAMING'
      || Boolean(qnaStreamTokensRef.current[nextConversationId])
      || hasPendingAssistantResponse(cachedSnapshot?.qnaMessages);
    const nextInput = cachedSnapshot?.qnaInput ?? qnaDraftsRef.current[nextConversationId] ?? '';
    const nextMessages: ChatMessage[] = cachedSnapshot?.qnaMessages?.length
      ? cachedSnapshot.qnaMessages
      : [
        { id: 'qna-greeting', role: 'assistant', content: QNA_GREETING },
        { id: `qna-loading-${nextConversationId}`, role: 'assistant', content: '正在加载历史对话...' },
      ];

    qnaAbortRef.current = null;
    conversationIdRef.current = nextConversationId;
    qnaInputRef.current = nextInput;
    qnaMessagesRef.current = nextMessages;
    setConversationId(nextConversationId);
    setQnaInput(nextInput);
    setQnaStateView(shouldResumeStreaming ? 'QNA_STREAMING' : 'QNA_IDLE');
    setQnaMessages(cachedSnapshot?.qnaMessages?.length
      ? cachedSnapshot.qnaMessages
      : [
        { id: 'qna-greeting', role: 'assistant', content: QNA_GREETING },
        { id: `qna-loading-${nextConversationId}`, role: 'assistant', content: '正在加载历史对话...' },
      ]);

    try {
      const synced = await syncConversationHistory({
        targetConversationId: nextConversationId,
        requestVersion,
        cachedMessages: cachedSnapshot?.qnaMessages,
        nextInput: cachedSnapshot?.qnaInput ?? qnaDraftsRef.current[nextConversationId] ?? '',
        expectStreaming: shouldResumeStreaming,
      });
      if (synced) {
        return;
      }
      setQnaMessages([
        { id: 'qna-greeting', role: 'assistant', content: QNA_GREETING },
        {
          id: `qna-history-${nextConversationId}`,
          role: 'assistant',
          content: payload.lastMessagePreview?.trim()
            ? `已进入历史对话“${payload.title || '历史对话'}”。\n上次对话摘要：${payload.lastMessagePreview}\n你可以继续追问。`
            : `已进入历史对话“${payload.title || '历史对话'}”。你可以继续追问。`,
        },
      ]);
    } catch (error) {
      if (conversationIdRef.current !== nextConversationId || qnaRequestVersionRef.current !== requestVersion) {
        return;
      }
      const message = getErrorMessage(error);
      setQnaMessages([
        { id: 'qna-greeting', role: 'assistant', content: QNA_GREETING },
        {
          id: `qna-history-error-${nextConversationId}`,
          role: 'assistant',
          content:
            message.includes('(429)')
              ? '历史对话加载过于频繁，请稍等一两秒后重试。当前会话已选中，但消息列表还未重新拉取完成。'
              : `历史对话加载失败：${message}`,
        },
      ]);
    } finally {
      loadingConversationIdRef.current = '';
    }
  }, [cacheConversationView, setQnaStateView, syncConversationHistory]);

  const loadCurrentProfile = useCallback(
    async (source: ProfileUpdateSource) => {
      if (!currentUser) {
        setProfile(null);
        setProfileSummary('');
        setProfileUpdatedAt('');
        return;
      }

      try {
        const response = await smartEngineApi.getCurrentProfile(String(currentUser.id));
        setProfile(mapProfileResponse(response));
        setProfileSummary(response.summary ?? '');
        setProfileUpdatedAt(response.updatedAt ?? '');
        setProfileSource(source);
      } catch {
        setProfile(null);
        setProfileSummary('');
        setProfileUpdatedAt('');
      }
    },
    [currentUser],
  );

  useEffect(() => {
    return () => {
      mountedRef.current = false;
      Object.values(taskMonitorRefsRef.current).forEach((refs) => {
        refs.taskStreamAbortRef.current?.abort();
        cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
      });
    };
  }, []);

  useEffect(() => {
    mountedRef.current = true;
  }, []);

  useEffect(() => {
    if (mode !== 'qna' || qnaSnapshotHydratedRef.current || typeof window === 'undefined') {
      return;
    }

    qnaSnapshotHydratedRef.current = true;
    const raw = window.sessionStorage.getItem(QNA_SNAPSHOT_STORAGE_KEY);
    if (!raw) {
      return;
    }
    try {
      const snapshot = JSON.parse(raw) as PersistedQnaSnapshot;
      const restoredConversationId = snapshot.conversationId ?? '';
      const restoredInput = snapshot.qnaInput ?? '';
      const restoredMessages = normalizeRestoredQnaMessages(snapshot);
      cacheConversationView(snapshot.conversationId ?? '', {
        qnaInput: restoredInput,
        qnaMessages: restoredMessages,
        qnaState: snapshot.qnaState === 'QNA_STREAMING' ? 'QNA_STREAMING' : 'QNA_IDLE',
      });
      conversationIdRef.current = restoredConversationId;
      qnaInputRef.current = restoredInput;
      qnaMessagesRef.current = restoredMessages;
      setConversationId(restoredConversationId);
      setQnaInput(restoredInput);
      setQnaStateView(snapshot.qnaState === 'QNA_STREAMING' ? 'QNA_STREAMING' : 'QNA_IDLE');
      setQnaMessages(restoredMessages);
      if (snapshot.qnaState === 'QNA_STREAMING' && snapshot.conversationId?.trim()) {
        const restoredConversationId = snapshot.conversationId.trim();
        void syncConversationHistory({
          targetConversationId: restoredConversationId,
          cachedMessages: normalizeRestoredQnaMessages(snapshot),
          nextInput: snapshot.qnaInput ?? '',
          expectStreaming: true,
        }).catch(() => undefined);
      }
    } catch {
      clearPersistedQnaSnapshot();
    }
  }, [cacheConversationView, clearPersistedQnaSnapshot, mode, setQnaStateView, syncConversationHistory]);

  useEffect(() => {
    const previousMode = previousModeRef.current;
    previousModeRef.current = mode;
    if (mode !== 'qna' || previousMode === 'qna') {
      return;
    }
    const restoredConversationId = conversationIdRef.current.trim();
    if (!restoredConversationId) {
      return;
    }
    void syncConversationHistory({
      targetConversationId: restoredConversationId,
      cachedMessages: qnaMessagesRef.current,
      nextInput: qnaInputRef.current,
      expectStreaming: qnaStateRef.current === 'QNA_STREAMING',
    }).catch(() => undefined);
  }, [mode, syncConversationHistory]);

  useEffect(() => {
    if (mode !== 'qna' || !qnaSnapshotHydratedRef.current || typeof window === 'undefined') {
      return;
    }

    cacheConversationView(conversationId, {
      qnaInput,
      qnaMessages,
      qnaState,
    });

    const snapshot: PersistedQnaSnapshot = {
      conversationId,
      qnaInput,
      qnaState,
      qnaMessages,
    };
    const isEmpty =
      !snapshot.conversationId &&
      !snapshot.qnaInput &&
      snapshot.qnaState === 'QNA_IDLE' &&
      snapshot.qnaMessages.length === 1 &&
      snapshot.qnaMessages[0]?.id === 'qna-greeting';

    if (isEmpty) {
      clearPersistedQnaSnapshot();
      return;
    }
    window.sessionStorage.setItem(QNA_SNAPSHOT_STORAGE_KEY, JSON.stringify(snapshot));
  }, [cacheConversationView, clearPersistedQnaSnapshot, conversationId, mode, qnaInput, qnaMessages, qnaState]);

  useEffect(() => {
    const onNewChat = () => {
      if (mode === 'qna') {
        resetQnaConversation();
        return;
      }
      resetEngineView();
    };
    window.addEventListener('app:new-chat', onNewChat);
    return () => {
      window.removeEventListener('app:new-chat', onNewChat);
    };
  }, [mode, resetEngineView, resetQnaConversation]);

  useEffect(() => {
    const restoreSelectedConversation = (payload?: SelectedConversationSnapshot) => {
      if (mode !== 'qna') {
        return;
      }
      if (payload?.conversationId) {
        openExistingConversation(payload);
        return;
      }
      if (typeof window === 'undefined') {
        return;
      }
      const raw = window.sessionStorage.getItem(SELECTED_CONVERSATION_STORAGE_KEY);
      if (!raw) {
        return;
      }
      try {
        const parsed = JSON.parse(raw) as SelectedConversationSnapshot;
        openExistingConversation(parsed);
      } catch {
        window.sessionStorage.removeItem(SELECTED_CONVERSATION_STORAGE_KEY);
      }
    };

    const onOpenConversation = (event: Event) => {
      const customEvent = event as CustomEvent<SelectedConversationSnapshot>;
      restoreSelectedConversation(customEvent.detail);
    };

    restoreSelectedConversation();
    window.addEventListener('app:open-conversation', onOpenConversation as EventListener);
    return () => {
      window.removeEventListener('app:open-conversation', onOpenConversation as EventListener);
    };
  }, [mode, openExistingConversation]);

  useEffect(() => {
    if (mode !== 'engine' || conversationId || typeof window === 'undefined') {
      return;
    }
    const activeConversationId = window.sessionStorage.getItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY)?.trim() ?? '';
    if (activeConversationId) {
      setConversationId(activeConversationId);
    }
  }, [conversationId, mode]);

  useEffect(() => {
    if (isAuthenticated && currentUser) {
      void loadCurrentProfile('BACKEND');
    } else {
      setProfile(null);
      setProfileSummary('');
      setProfileUpdatedAt('');
    }
  }, [currentUser, isAuthenticated, loadCurrentProfile]);

  useEffect(() => {
    setShowAllWeakPoints(false);
  }, [profile]);

  useEffect(() => {
    if (isAuthenticated && pendingActionRef.current) {
      const action = pendingActionRef.current;
      pendingActionRef.current = null;
      action();
    }
  }, [isAuthenticated]);

  const withAuth = (action: () => void) => {
    if (isAuthenticated) {
      action();
      return;
    }
    pendingActionRef.current = action;
    openAuthModal('login', '请先登录');
  };

  const markFormEditing = () => {
    if (!selectedService) {
      return;
    }
    updateServiceSnapshot(selectedService, (current) => {
      if (hasLockedTask(current)) {
        return current;
      }
      return {
        ...current,
        engineState: 'ENGINE_FORM_EDITING',
      };
    });
  };

  const handleSelectService = (service: EngineService) => {
    setSelectedService(service);
    updateServiceSnapshot(service, (current) => {
      if (current.engineState !== 'ENGINE_IDLE' || current.taskId) {
        return current;
      }
      return {
        ...current,
        engineState: 'ENGINE_SERVICE_SELECTED',
      };
    });
  };

  const monitorTask = useCallback(
    async (service: EngineService, currentTaskId: string) => {
      if (activeTaskMonitorsRef.current[service] === currentTaskId) {
        return;
      }
      activeTaskMonitorsRef.current[service] = currentTaskId;
      const refs = taskMonitorRefsRef.current[service];
      const outcome = await runByApiTask({
        service,
        currentTaskId,
        streamQueueRef: refs.streamQueueRef,
        streamFlushTimerRef: refs.streamFlushTimerRef,
        streamRafRef: refs.streamRafRef,
        setServiceResultLines: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            serviceResultLines: typeof value === 'function' ? value(current.serviceResultLines) : value,
          }));
        },
        setTaskProgress: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            taskProgress: typeof value === 'function' ? value(current.taskProgress) : value,
          }));
        },
        setTaskStatus: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            taskStatus: typeof value === 'function' ? value(current.taskStatus) : value,
          }));
        },
        setTaskSummary: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            taskSummary: typeof value === 'function' ? value(current.taskSummary) : value,
          }));
        },
        setDownloadLinks: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            downloadLinks: typeof value === 'function' ? value(current.downloadLinks) : value,
          }));
        },
        setVideoResult: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            videoResult: typeof value === 'function' ? value(current.videoResult) : value,
          }));
        },
        setInlineResource: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            inlineResource: typeof value === 'function' ? value(current.inlineResource) : value,
          }));
        },
        setPracticeBatch: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            practiceBatch: typeof value === 'function' ? value(current.practiceBatch) : value,
          }));
        },
        setJudgeResult: (value) => {
          updateServiceSnapshot(service, (current) => ({
            ...current,
            judgeResult: typeof value === 'function' ? value(current.judgeResult) : value,
          }));
        },
        taskStreamAbortRef: refs.taskStreamAbortRef,
      });

      if (activeTaskMonitorsRef.current[service] === currentTaskId) {
        delete activeTaskMonitorsRef.current[service];
      }
      if (!mountedRef.current) {
        return;
      }

      if (outcome === 'completed') {
        updateServiceSnapshot(service, (current) => ({
          ...current,
          engineState: 'ENGINE_COMPLETED',
          taskStatus: '任务完成',
        }));
        await loadCurrentProfile('TASK_REFRESH');
        return;
      }

      if (outcome === 'failed') {
        updateServiceSnapshot(service, (current) => ({
          ...current,
          engineState: 'ENGINE_FAILED',
          taskStatus: '任务失败',
        }));
        return;
      }

      if (outcome === 'aborted') {
        updateServiceSnapshot(service, (current) => ({
          ...current,
          engineState: 'ENGINE_FAILED',
          taskStatus: '连接中断，请重试',
        }));
        return;
      }

      if (outcome === 'running') {
        updateServiceSnapshot(service, (current) => ({
          ...current,
          engineState: 'ENGINE_RUNNING',
          taskStatus: '后台运行中',
          serviceResultLines: current.serviceResultLines.includes('任务仍在后台执行，可切换页面，稍后返回继续查看结果。')
            ? current.serviceResultLines
            : [...current.serviceResultLines, '任务仍在后台执行，可切换页面，稍后返回继续查看结果。'],
        }));
        return;
      }

      if (outcome === 'unauthorized') {
        updateServiceSnapshot(service, (current) => ({
          ...current,
          engineState: 'ENGINE_RUNNING',
          taskStatus: '登录失效，待重新登录',
        }));
        openAuthModal('login', '登录状态已失效，重新登录后可继续查看任务结果');
      }
    },
    [loadCurrentProfile, openAuthModal, updateServiceSnapshot],
  );

  const handleQnaSend = async () => {
    const text = qnaInput.trim();
    const uploadedImageUrls = pendingQnaImages.filter((item) => item.uploadStatus === 'uploaded' && item.uploadedUrl).map((item) => item.uploadedUrl as string);
    if ((!text && uploadedImageUrls.length === 0) || qnaBusy) {
      return;
    }
    if (!isAuthenticated) {
      openAuthModal('login', '请先登录');
      return;
    }

    const assistantMessageId = `qna-assistant-${Date.now()}`;
    const userMessageId = `qna-user-${Date.now()}`;
    const pendingPreviewUrls = pendingQnaImages.map((item) => item.previewUrl);
    const useWebSearch = qnaWebSearchEnabled;
    const useDeepReasoning = deepReasoningEnabled;
    const pendingMessages: ChatMessage[] = [
      ...qnaMessagesRef.current,
      {
        id: userMessageId,
        role: 'user',
        content: text,
        imageUrls: uploadedImageUrls,
        localImagePreviews: pendingPreviewUrls,
        webSearchEnabled: useWebSearch,
        deepReasoningEnabled: useDeepReasoning,
      },
      { id: assistantMessageId, role: 'assistant', content: '' },
    ];
    qnaInputRef.current = '';
    qnaMessagesRef.current = pendingMessages;
    setQnaInput('');
    setQnaWebSearchEnabled(false);
    setQnaImageError('');
    setQnaMessages(pendingMessages);
    setPendingQnaImages([]);
    setQnaStateView('QNA_STREAMING');
    cacheConversationView(conversationIdRef.current, {
      qnaInput: '',
      qnaMessages: pendingMessages,
      qnaState: 'QNA_STREAMING',
    });

    qnaRequestVersionRef.current += 1;
    const requestVersion = qnaRequestVersionRef.current;
    const abortController = new AbortController();
    qnaAbortRef.current = abortController;
    const draftConversationId = conversationId;

    try {
      const currentConversationId = conversationId || (await conversationApi.createConversation()).conversationId;
      if (abortController.signal.aborted || qnaRequestVersionRef.current !== requestVersion) {
        setQnaStateView('QNA_IDLE');
        return;
      }
      if (!conversationId) {
        conversationIdRef.current = currentConversationId;
        setConversationId(currentConversationId);
        qnaDraftsRef.current.__new__ = '';
        window.dispatchEvent(new Event('app:conversation-updated'));
      }
      cacheConversationView(currentConversationId, {
        qnaInput: '',
        qnaMessages: pendingMessages,
        qnaState: 'QNA_STREAMING',
      });
      const streamToken = `${currentConversationId}:${assistantMessageId}`;
      qnaStreamTokensRef.current[currentConversationId] = streamToken;

      await conversationApi.streamMessage(
        currentConversationId,
        {
          message: text,
          imageUrls: uploadedImageUrls,
          serviceType: 'TUTORING',
          webSearchEnabled: useWebSearch,
          reasoningMode: useDeepReasoning ? 'DEEP' : 'NORMAL',
        },
        {
          onOpen: () => {
            if (qnaStreamTokensRef.current[currentConversationId] !== streamToken) {
              return;
            }
            window.dispatchEvent(new Event('app:conversation-updated'));
          },
          onEvent: (event) => {
            if (qnaStreamTokensRef.current[currentConversationId] !== streamToken) {
              return;
            }
            const chunk = readConversationChunk(event.data, event.event);
            if (!chunk) {
              return;
            }
            updateQnaConversationMessages(
              currentConversationId,
              (messages) => {
                let updatedAssistant = false;
                const nextMessagesForChunk = messages.map((item) => {
                  if (item.id !== assistantMessageId) {
                    return item;
                  }
                  updatedAssistant = true;
                  return { ...item, content: (item.content ?? '') + chunk };
                });
                return updatedAssistant
                  ? nextMessagesForChunk
                  : [...messages, { id: assistantMessageId, role: 'assistant', content: chunk }];
              },
              { qnaState: 'QNA_STREAMING' },
            );
          },
          onDone: () => {
            if (qnaStreamTokensRef.current[currentConversationId] !== streamToken) {
              return;
            }
            delete qnaStreamTokensRef.current[currentConversationId];
            updateQnaConversationMessages(currentConversationId, (messages) => messages, { qnaState: 'QNA_IDLE' });
            window.dispatchEvent(new Event('app:conversation-updated'));
            if (conversationIdRef.current === currentConversationId) {
              void loadCurrentProfile('TASK_REFRESH');
            }
          },
          onError: (error) => {
            if (qnaStreamTokensRef.current[currentConversationId] !== streamToken) {
              return;
            }
            delete qnaStreamTokensRef.current[currentConversationId];
            const message = getErrorMessage(error);
            updateQnaConversationMessages(
              currentConversationId,
              (messages) =>
                messages.map((item) =>
                  item.id === assistantMessageId
                    ? {
                      ...item,
                      content: item.content && !isProcessingOnlyAssistantContent(item.content)
                        ? item.content
                        : `会话失败：${message}`,
                    }
                    : item,
                ),
              { qnaState: 'QNA_IDLE' },
            );
            if (conversationIdRef.current !== currentConversationId) {
              window.dispatchEvent(new Event('app:conversation-updated'));
              return;
            }
            setQnaMessages((prev) =>
              prev.map((item) =>
                item.id === assistantMessageId ? { ...item, content: item.content || `会话失败：${message}` } : item,
              ),
            );
            setQnaStateView('QNA_IDLE');
            window.dispatchEvent(new Event('app:conversation-updated'));
          },
        },
        abortController.signal,
      );
    } catch (error) {
      if (qnaRequestVersionRef.current !== requestVersion) {
        return;
      }
      if (draftConversationId && conversationIdRef.current !== draftConversationId) {
        return;
      }
      const message = getErrorMessage(error);
      setQnaMessages((prev) =>
        prev.map((item) => (item.id === assistantMessageId ? { ...item, content: `会话失败：${message}` } : item)),
      );
      setQnaStateView('QNA_IDLE');
    }
  };

  const revokePendingImage = useCallback((image: PendingChatImage) => {
    if (image.previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(image.previewUrl);
    }
  }, []);

  const validateImageFile = useCallback((file: File): string => {
    const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp']);
    if (!allowedTypes.has(file.type)) {
      return '仅支持 jpg、png、webp 图片';
    }
    if (file.size > 10 * 1024 * 1024) {
      return '图片不能超过 10MB';
    }
    return '';
  }, []);

  const handlePickQnaImages = useCallback(async (files: File[]) => {
    if (!files.length) {
      return;
    }
    setQnaImageError('');
    for (const file of files) {
      const validationMessage = validateImageFile(file);
      if (validationMessage) {
        setQnaImageError(validationMessage);
        continue;
      }
      const imageId = `pending-image-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      const previewUrl = URL.createObjectURL(file);
      const pendingImage: PendingChatImage = {
        id: imageId,
        file,
        previewUrl,
        uploadStatus: 'uploading',
        uploadProgress: 0,
      };
      setPendingQnaImages((prev) => [...prev, pendingImage]);
      try {
        const uploaded = await conversationApi.uploadImage(file, (percent) => {
          setPendingQnaImages((prev) =>
            prev.map((item) => (item.id === imageId ? { ...item, uploadProgress: percent, uploadStatus: 'uploading' } : item)),
          );
        });
        setPendingQnaImages((prev) =>
          prev.map((item) =>
            item.id === imageId
              ? { ...item, uploadProgress: 100, uploadStatus: 'uploaded', uploadedUrl: uploaded.imageUrl }
              : item,
          ),
        );
      } catch (error) {
        const message = getErrorMessage(error);
        setPendingQnaImages((prev) =>
          prev.map((item) =>
            item.id === imageId
              ? { ...item, uploadStatus: 'failed', errorMessage: message }
              : item,
          ),
        );
        setQnaImageError(message);
      }
    }
  }, [validateImageFile]);

  const handleRemovePendingQnaImage = useCallback((id: string) => {
    setPendingQnaImages((prev) => {
      const target = prev.find((item) => item.id === id);
      if (target) {
        revokePendingImage(target);
      }
      return prev.filter((item) => item.id !== id);
    });
  }, [revokePendingImage]);

  useEffect(() => () => {
    pendingQnaImages.forEach(revokePendingImage);
  }, [pendingQnaImages, revokePendingImage]);

  const ensureEngineConversationId = useCallback(async () => {
    const currentConversationId = conversationIdRef.current.trim();
    if (currentConversationId) {
      return currentConversationId;
    }

    if (typeof window !== 'undefined') {
      const activeConversationId = window.sessionStorage.getItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY)?.trim() ?? '';
      if (activeConversationId) {
        setConversationId(activeConversationId);
        window.dispatchEvent(new Event('app:conversation-updated'));
        return activeConversationId;
      }
    }

    const recentConversations = await conversationApi.listRecentConversations();
    const latestConversationId = recentConversations[0]?.conversationId?.trim() ?? '';
    if (latestConversationId) {
      setConversationId(latestConversationId);
      window.dispatchEvent(new Event('app:conversation-updated'));
      return latestConversationId;
    }

    const createdConversationId = (await conversationApi.createConversation()).conversationId;
    setConversationId(createdConversationId);
    window.dispatchEvent(new Event('app:conversation-updated'));
    return createdConversationId;
  }, []);

  const handleSubmitService = async () => {
    if (!isAuthenticated) {
      openAuthModal('login', '请先登录');
      return;
    }
    if (!selectedService || engineBusy || hasLockedTask(serviceSnapshots[selectedService])) {
      return;
    }

    const refs = taskMonitorRefsRef.current[selectedService];
    refs.taskStreamAbortRef.current?.abort();
    refs.taskStreamAbortRef.current = null;
    refs.streamQueueRef.current = [];
    cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    updateServiceSnapshot(selectedService, {
      engineState: 'ENGINE_SUBMITTING',
      taskId: '',
      taskProgress: 8,
      taskStatus: '已提交，等待受理',
      taskSummary: '',
      serviceResultLines: [],
      downloadLinks: [],
      videoResult: null,
      inlineResource: null,
      practiceBatch: null,
      judgeResult: null,
    });

    const params = buildServiceParams(selectedService, { resourceForm, pathForm, pushForm, assessmentForm });

    try {
      engineSubmitVersionRef.current += 1;
      const submitVersion = engineSubmitVersionRef.current;
      const ensuredConversationId = await ensureEngineConversationId();
      if (engineSubmitVersionRef.current !== submitVersion) {
        return;
      }
      const submitResp = await smartEngineApi.submit({
        conversationId: ensuredConversationId,
        serviceType: serviceTypeMap[selectedService],
        params,
      });

      updateServiceSnapshot(selectedService, (current) => ({
        ...current,
        taskId: submitResp.taskId,
        engineState: 'ENGINE_RUNNING',
        taskStatus: toUiTaskStatus(submitResp.status),
      }));
      void monitorTask(selectedService, submitResp.taskId);
    } catch (error) {
      const message = getErrorMessage(error);
      updateServiceSnapshot(selectedService, (current) => ({
        ...current,
        engineState: 'ENGINE_FAILED',
        taskStatus: '任务失败',
        serviceResultLines: [...current.serviceResultLines, `接口失败：${message}`],
      }));
    }
  };

  const handleSubmitPracticeAnswers = async (batch: PracticeQuestionBatch, answers: Record<string, string>) => {
    if (!isAuthenticated) {
      openAuthModal('login', '请先登录');
      return;
    }
    const targetService: EngineService = selectedService === 'assessment' ? 'assessment' : 'resource';
    if (hasLockedTask(serviceSnapshots[targetService])) {
      return;
    }

    const refs = taskMonitorRefsRef.current[targetService];
    refs.taskStreamAbortRef.current?.abort();
    refs.taskStreamAbortRef.current = null;
    refs.streamQueueRef.current = [];
    cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    updateServiceSnapshot(targetService, (current) => ({
      ...current,
      engineState: 'ENGINE_SUBMITTING',
      taskId: '',
      taskProgress: 12,
      taskStatus: '已提交判题任务',
      taskSummary: '',
      serviceResultLines: [],
      downloadLinks: [],
      videoResult: null,
      inlineResource: null,
      judgeResult: null,
    }));

    try {
      const ensuredConversationId = await ensureEngineConversationId();
      const assessmentDimension = batch.assessmentDimension || (targetService === 'assessment' ? assessmentForm.dimensions[0] : '');
      const batchTopic = batch.topic || resourceForm.keyPoints || resourceForm.course;
      const judgeQuery = targetService === 'assessment'
        ? `${assessmentDimension || '专项评估'} ${batchTopic} 判题`
        : `${resourceForm.course} ${batchTopic} 练习题判题`;
      const submitResp = await smartEngineApi.submit({
        conversationId: ensuredConversationId,
        serviceType: 'PRACTICE_JUDGE',
        params: {
          topic: targetService === 'assessment' && assessmentDimension
            ? `${assessmentDimension}：${batchTopic}`
            : batchTopic,
          query: judgeQuery,
          practiceQuestionBatch: batch,
          practiceQuestions: batch.questions,
          answers,
          assessmentDimension,
          learningContext: {
            course: resourceForm.course,
            chapter: batchTopic,
          },
        },
      });
      updateServiceSnapshot(targetService, (current) => ({
        ...current,
        taskId: submitResp.taskId,
        engineState: 'ENGINE_RUNNING',
        taskStatus: toUiTaskStatus(submitResp.status),
      }));
      void monitorTask(targetService, submitResp.taskId);
    } catch (error) {
      const message = getErrorMessage(error);
      updateServiceSnapshot(targetService, (current) => ({
        ...current,
        engineState: 'ENGINE_FAILED',
        taskStatus: '判题失败',
        serviceResultLines: [...current.serviceResultLines, `判题失败：${message}`],
      }));
    }
  };

  const handleStopService = () => {
    if (!selectedService) {
      return;
    }
    const refs = taskMonitorRefsRef.current[selectedService];
    refs.taskStreamAbortRef.current?.abort();
    refs.taskStreamAbortRef.current = null;
    activeTaskMonitorsRef.current[selectedService] = '';
    cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    updateServiceSnapshot(selectedService, (current) => ({
      ...current,
      engineState: 'ENGINE_FAILED',
      taskStatus: '已停止实时接收',
      serviceResultLines: current.serviceResultLines.includes('已停止当前页面的实时接收，任务可能仍在后台继续执行。')
        ? current.serviceResultLines
        : [...current.serviceResultLines, '已停止当前页面的实时接收，任务可能仍在后台继续执行。'],
    }));
  };

  useEffect(() => {
    if (mode !== 'engine' || engineSnapshotHydratedRef.current) {
      return;
    }

    engineSnapshotHydratedRef.current = true;
    if (typeof window === 'undefined') {
      return;
    }

    const raw = window.sessionStorage.getItem(ENGINE_TASK_STORAGE_KEY);
    if (!raw) {
      return;
    }

    try {
      const snapshot = JSON.parse(raw) as PersistedEngineTaskSnapshot;
      const persistedSnapshots = buildPersistedEngineSnapshots(
        snapshot.selectedService ?? null,
        snapshot.snapshots ?? createInitialEngineSnapshots(),
      );
      setSelectedService(snapshot.selectedService ?? null);
      setConversationId(snapshot.conversationId ?? window.sessionStorage.getItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY) ?? '');
      setServiceSnapshots({
        ...createInitialEngineSnapshots(),
        ...persistedSnapshots,
      });

      (Object.entries(persistedSnapshots) as Array<[EngineService, EngineTaskSnapshot]>).forEach(([service, item]) => {
        if (item.taskId && (item.engineState === 'ENGINE_RUNNING' || item.engineState === 'ENGINE_SUBMITTING')) {
          void monitorTask(service, item.taskId);
        }
      });
    } catch {
      clearPersistedEngineSnapshot();
    }
  }, [clearPersistedEngineSnapshot, mode, monitorTask]);

  useEffect(() => {
    if (mode !== 'engine' || !engineSnapshotHydratedRef.current || typeof window === 'undefined') {
      return;
    }

    const snapshot: PersistedEngineTaskSnapshot = {
      selectedService,
      conversationId,
      snapshots: buildPersistedEngineSnapshots(selectedService, serviceSnapshots),
    };

    const isEmptySnapshot =
      !selectedService &&
      !conversationId &&
      Object.values(serviceSnapshots).every((item) => !item.taskId && item.engineState === 'ENGINE_IDLE');

    if (isEmptySnapshot) {
      clearPersistedEngineSnapshot();
      return;
    }

    window.sessionStorage.setItem(ENGINE_TASK_STORAGE_KEY, JSON.stringify(snapshot));
  }, [
    clearPersistedEngineSnapshot,
    conversationId,
    mode,
    selectedService,
    serviceSnapshots,
  ]);

  if (mode === 'qna') {
    return (
      <QnaChatView
        hasStartedConversation={hasStartedConversation}
        qnaInput={qnaInput}
        qnaBusy={qnaBusy}
        qnaMessages={qnaMessages}
        pendingImages={pendingQnaImages}
        imageErrorMessage={qnaImageError}
        deepReasoningEnabled={deepReasoningEnabled}
        webSearchEnabled={qnaWebSearchEnabled}
        onChange={setQnaInput}
        onSend={handleQnaSend}
        onToggleDeepReasoning={() => setDeepReasoningEnabled((prev) => !prev)}
        onToggleWebSearch={() => setQnaWebSearchEnabled((prev) => !prev)}
        onPickImages={handlePickQnaImages}
        onRemoveImage={handleRemovePendingQnaImage}
      />
    );
  }

  return (
    <Suspense fallback={<div className="mx-auto max-w-[1180px] rounded-3xl border border-slate-200 bg-white/80 px-6 py-10 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-400">正在加载智能服务界面...</div>}>
      <div className="mx-auto max-w-[1180px] space-y-6 pb-10 px-1 md:px-0">
        <RealtimeProfile
          profile={profile}
          summary={profileSummary}
          updatedAt={profileUpdatedAt}
          source={profileSource}
          showAllWeakPoints={showAllWeakPoints}
          onToggleWeakPoints={() => setShowAllWeakPoints((prev) => !prev)}
        />

        <div className="modern-card p-5 md:p-6">
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-semibold tracking-tight text-slate-800 dark:text-white md:text-[34px]">你好，我是智学引擎</h1>
            <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">选择一项智能服务，开始你的学习之旅</p>
          </div>

          <div className="mb-6 grid grid-cols-2 gap-2 md:flex md:flex-wrap md:justify-center md:gap-3">
            {serviceButtons.map((item) => {
              const active = selectedService === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => withAuth(() => handleSelectService(item.id))}
                  className={`group flex flex-col items-center gap-1.5 rounded-2xl border px-4 py-3 text-sm transition-all duration-200 md:flex-row md:gap-2 md:px-4 md:py-2 ${
                    active
                      ? 'border-primary-300 bg-primary-50 text-primary-700 shadow-sm dark:border-primary-700 dark:bg-primary-900/50 dark:text-primary-300'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-primary-200 hover:bg-primary-50/50 hover:text-primary-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:border-primary-700 dark:hover:bg-primary-900/20'
                  }`}
                >
                  <item.icon className={`h-5 w-5 md:h-4 md:w-4 ${active ? 'text-primary-600 dark:text-primary-400' : 'text-slate-400 group-hover:text-primary-500 dark:text-slate-500'}`} />
                  <span className="text-xs md:text-sm">{item.label}</span>
                </button>
              );
            })}
          </div>

          <ServiceDynamicForm
            service={selectedService}
            resourceForm={resourceForm}
            pathForm={pathForm}
            pushForm={pushForm}
            assessmentForm={assessmentForm}
            onResourceChange={(next) => {
              setResourceForm(next);
              markFormEditing();
            }}
            onPathChange={(next) => {
              setPathForm(next);
              markFormEditing();
            }}
            onPushChange={(next) => {
              setPushForm(next);
              markFormEditing();
            }}
            onAssessmentChange={(next) => {
              setAssessmentForm(next);
              markFormEditing();
            }}
          />

          <ServiceSubmitPanel
            disabled={!selectedService || engineBusy}
            onSubmit={handleSubmitService}
            onStop={handleStopService}
            canStop={engineBusy}
            taskId={taskId}
            progress={taskProgress}
            status={taskStatus}
            uiState={engineStateView}
          />
        </div>

        <TaskResultPanel
          service={selectedService}
          taskSummary={taskSummary}
          serviceResultLines={serviceResultLines}
          downloadLinks={downloadLinks}
          videoResult={videoResult}
          inlineResource={activeEngineSnapshot.inlineResource}
          practiceBatch={activeEngineSnapshot.practiceBatch}
          judgeResult={activeEngineSnapshot.judgeResult}
          canSubmitPractice={!hasLockedTask(activeEngineSnapshot)}
          onSubmitPracticeAnswers={handleSubmitPracticeAnswers}
        />
      </div>
    </Suspense>
  );
}
