import { getErrorMessage, isUnauthorizedError } from '../api/request';
import { smartEngineApi } from '../api/smartEngine';
import type {
  ConversationStreamEventPayload,
  EngineService,
  ProfileSnapshot,
  RunByApiTaskArgs,
  ServiceFormsPayload,
  SmartEngineStreamEvent,
  SmartEngineTaskResponse,
  TaskRunHandlers,
  TempDownloadLink,
  UserProfileResponse,
  VideoCardStyle,
  VideoResult,
} from './LearningStudioDemoPage.types';

export function normalizeCopyText(input: string): string {
  return input
    .replace(/\r\n/g, '\n')
    .replace(/\n{2,}/g, '\n')
    .trim();
}

export function sanitizeConversationMessageContent(input: string): string {
  const normalized = normalizeCopyText(input);
  if (!normalized || looksLikeTutorChain(normalized)) {
    return '';
  }

  return normalized
    .split('\n')
    .map((line) => line.trimEnd())
    .filter((line) => line.trim() !== '---')
    .map((line) =>
      line
        .replace(/^\s{0,3}#{1,6}\s*/g, '')
        .replace(/^\s*>\s?/g, '')
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/__(.*?)__/g, '$1')
        .replace(/`([^`]+)`/g, '$1'),
    )
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export async function runByApiTask({
  service,
  currentTaskId,
  streamQueueRef,
  streamFlushTimerRef,
  streamRafRef,
  setServiceResultLines,
  setTaskProgress,
  setTaskStatus,
  setTaskSummary,
  setDownloadLinks,
  setVideoResult,
  taskStreamAbortRef,
}: RunByApiTaskArgs): Promise<'completed' | 'running' | 'failed' | 'aborted' | 'unauthorized'> {
  const handlers: TaskRunHandlers = {
    onProgress: (value, statusHint) => {
      setTaskProgress((prev) => Math.max(prev, value));
      if (statusHint) {
        setTaskStatus(statusHint);
      }
    },
    onLine: (line) => {
      if (!line.trim()) {
        return;
      }
      streamQueueRef.current.push(line);
      scheduleStreamFlush(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);
    },
    onSummary: (summary) => {
      if (!summary.trim()) {
        return;
      }
      setTaskSummary(summary);
    },
    onDownload: (item) => {
      setDownloadLinks((prev) => (prev.some((existing) => existing.url === item.url) ? prev : [...prev, item]));
      if (isVideoLink(item)) {
        setVideoResult((prev) => prev ?? mapDownloadToVideoResult(item));
      }
    },
    onVideo: (item) => {
      setVideoResult((prev) => prev ?? item);
    },
  };

  const streamAbortController = new AbortController();
  taskStreamAbortRef.current = streamAbortController;
  let streamErrorMessage = '';
  let streamDone = false;

  await smartEngineApi.streamTask(
    currentTaskId,
    {
      onEvent: (event) => {
        consumeTaskStreamEvent(event, handlers);
      },
      onDone: () => {
        streamDone = true;
      },
      onError: (error) => {
        streamErrorMessage = error.message;
      },
    },
    streamAbortController.signal,
  );

  taskStreamAbortRef.current = null;
  flushStreamQueue(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);

  if (streamDone && !streamErrorMessage) {
    setTaskProgress(100);
    setTaskStatus('任务完成');
    return 'completed';
  }

  if (streamAbortController.signal.aborted && !streamErrorMessage) {
    return 'aborted';
  }

  if (streamErrorMessage) {
    if (isUnauthorizedError(new Error(streamErrorMessage))) {
      handlers.onLine('任务结果读取需要重新登录，任务本身可能仍在后台继续执行。');
      return 'unauthorized';
    }
    handlers.onLine(`任务流失败，尝试轮询兜底：${streamErrorMessage}`);
  }

  try {
    for (let i = 0; i < 45; i += 1) {
      if (streamAbortController.signal.aborted) {
        return 'aborted';
      }
      const task = await smartEngineApi.getTask(currentTaskId, { dedupe: false, retry: 2 });
      applyTaskSnapshot(task, service, handlers);

      if (task.status === 'COMPLETED') {
        flushStreamQueue(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);
        return 'completed';
      }

      if (task.status === 'FAILED' || task.status === 'CANCELLED' || task.status === 'TIMEOUT') {
        throw new Error(task.errorMessage || '任务失败');
      }

      await wait(2000);
    }

    flushStreamQueue(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);
    return 'running';
  } catch (error) {
    if (streamAbortController.signal.aborted) {
      return 'aborted';
    }
    if (isUnauthorizedError(error)) {
      handlers.onLine('任务结果读取需要重新登录，任务本身可能仍在后台继续执行。');
      flushStreamQueue(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);
      return 'unauthorized';
    }
    handlers.onLine(getErrorMessage(error));
    flushStreamQueue(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);
    return 'failed';
  }
}

function consumeTaskStreamEvent(event: SmartEngineStreamEvent, handlers: TaskRunHandlers): void {
  const envelope = parseTaskStreamEnvelope(event.data);

  if (event.event === 'progress') {
    const progress = readNumeric(envelope.payload?.percent) ?? readNumeric(envelope.payload?.progress) ?? 0;
    handlers.onProgress(progress, readStatusHint(envelope.payload));
    return;
  }

  if (isVideoProgressEvent(event.event)) {
    const stage = mapVideoProgressEvent(event.event);
    const progress = readNumeric(envelope.payload?.percent) ?? readNumeric(envelope.payload?.progress) ?? stage.progress;
    handlers.onProgress(progress, stage.status);
    const line = readSummary(envelope.payload) || stage.message;
    if (line) {
      handlers.onLine(line);
    }
    if (event.event === 'video_gen:complete') {
      const summary = readSummary(envelope.payload);
      if (summary) {
        handlers.onSummary(summary);
      }
      const videoResult = readVideoResult(envelope.payload);
      if (videoResult) {
        handlers.onVideo(videoResult);
      }
    }
    return;
  }

  if (event.event === 'resource_file') {
    const title = readString(envelope.payload?.title) || readString(envelope.payload?.fileName) || '资源文件';
    const downloadUrl = readString(envelope.payload?.downloadUrl);
    const resourceType = readString(envelope.payload?.assetType);
    if (downloadUrl) {
      handlers.onDownload({
        title,
        url: downloadUrl,
        expiresHint: formatExpiresHint(envelope.payload),
        resourceType,
        thumbnailUrl: readUrlField(envelope.payload, ['thumbnailUrl', 'thumbnail_url', 'posterUrl', 'coverUrl']),
        duration: readDuration(envelope.payload),
        style: readVideoStyle(envelope.payload),
        knowledgePoint: readString(envelope.payload?.knowledgePoint) || readString(envelope.payload?.topic),
      });
    }
    handlers.onLine(`${title} 已生成`);
    return;
  }

  if (event.event === 'done') {
    const summary = readSummary(envelope.payload);
    const status = readString(envelope.payload?.status).toUpperCase();
    const doneLabel = status === 'FAILED' || status === 'ERROR' ? '任务失败' : '任务完成';
    handlers.onProgress(100, doneLabel);
    if (summary) {
      handlers.onSummary(summary);
    }
    if (doneLabel === '任务失败') {
      handlers.onLine(summary || '任务执行失败');
    }
    return;
  }

  if (event.event === 'error') {
    handlers.onLine(`任务流错误：${readSummary(envelope.payload) || '任务流执行失败'}`);
    return;
  }

  const line = readSummary(envelope.payload) || stringifyCompact(envelope.payload);
  if (line) {
    handlers.onLine(line);
  }
}

function applyTaskSnapshot(
  task: SmartEngineTaskResponse,
  service: EngineService,
  handlers: TaskRunHandlers,
): void {
  const progress =
    readNumeric(task.progressPercent) ??
    readNumeric(task.progress);

  if (progress !== undefined) {
    handlers.onProgress(progress, toUiTaskStatus(task.status));
  }

  if (task.responseSummary) {
    const summary = readSummary(task.responseSummary);
    if (summary) {
      handlers.onSummary(summary);
    }
    const videoResult = readVideoResult(task.responseSummary);
    if (videoResult) {
      handlers.onVideo(videoResult);
    }
    responseSummaryToLines(task.responseSummary, service).forEach((line) => handlers.onLine(line));
  }
}

function parseTaskStreamEnvelope(raw: string): { payload?: Record<string, unknown> } {
  try {
    return JSON.parse(raw) as { payload?: Record<string, unknown> };
  } catch {
    return {
      payload: {
        text: raw,
      },
    };
  }
}

function responseSummaryToLines(summary: Record<string, unknown>, service: EngineService): string[] {
  if (service === 'path') {
    const learningPath = readRecord(summary.learningPath);
    if (learningPath) {
      return formatLearningPathLines(learningPath);
    }
  }
  return Object.entries(summary)
    .filter(([key]) => !['summary', 'summaryText', 'message'].includes(key))
    .map(([key, value]) => `${labelForSummaryKey(key, service)}：${stringifyCompact(value)}`)
    .filter((line) => !line.endsWith('：'));
}

export function readConversationChunk(data: ConversationStreamEventPayload, eventName: string): string {
  const payload = data.payload;
  if (!payload) {
    return '';
  }

  const stage = readString(payload.stage);
  if (eventName === 'progress') {
    return '';
  }
  if (eventName === 'result_chunk' && stage && stage !== 'tutoring') {
    return '';
  }

  const text = readString(payload.text) || readString(payload.message) || readString(payload.summaryText);
  if (text) {
    return sanitizeConversationMessageContent(text);
  }

  if (eventName === 'done') {
    return '';
  }

  return stringifyCompact(payload);
}

function looksLikeTutorChain(text: string): boolean {
  const normalized = text.replace(/\n/g, ' ').trim();
  return normalized.includes('历史摘要')
    || normalized.includes('优先参考的来源')
    || normalized.includes('建议你这样学')
    || normalized.includes('接下来请你先回答')
    || normalized.includes('未解决的问题');
}

export function mapProfileResponse(response: UserProfileResponse): ProfileSnapshot | null {
  const raw = response.profile;
  if (!raw) {
    return null;
  }

  return {
    major: readString(raw.major) || readString(raw.courseFocus) || readString(raw.courseDirection),
    goal: readString(raw.learningGoal) || readString(raw.goal),
    knowledgeBase: readString(raw.knowledgeBase) || readString(raw.foundationLevel),
    weakPoints: readStringArray(raw.weakPoints, raw.knownGaps),
    preference: readStringArray(raw.preference, raw.learningPreference, raw.preferredModes),
    cognitiveStyle: readString(raw.cognitiveStyle) || readString(raw.learningStyle),
    confidenceLevel: readString(raw.confidenceLevel) || readString(raw.confidence),
  };
}

export function buildServiceParams(service: EngineService, payload: ServiceFormsPayload): Record<string, unknown> {
  if (service === 'resource') {
    const resourceForm = payload.resourceForm;
    const includeVideo = payload.resourceForm.resourceTypes.includes('VIDEO');
    const normalizedResourceTypes = payload.resourceForm.resourceTypes.map(normalizeResourceType);
    const primaryResourceType = includeVideo ? 'VIDEO' : normalizedResourceTypes[0] ?? 'DOCUMENT';
    const resourceTypeLabels = payload.resourceForm.resourceTypes
      .map(resourceTypeLabel)
      .filter(Boolean);
    const difficultyLabel = resourceDifficultyLabel(resourceForm.difficulty);
    const query = [
      resourceForm.course,
      resourceForm.keyPoints,
      difficultyLabel,
      resourceTypeLabels.join('、'),
    ]
      .map((item) => item?.trim())
      .filter(Boolean)
      .join(' ');
    return {
      resourceType: primaryResourceType,
      resourceTypes: normalizedResourceTypes,
      course: resourceForm.course,
      difficulty: resourceForm.difficulty,
      keyPoints: resourceForm.keyPoints,
      query,
      topic: resourceForm.keyPoints || resourceForm.course,
      learningContext: {
        course: resourceForm.course,
        chapter: resourceForm.keyPoints,
      },
      style: includeVideo ? resourceForm.videoStyle : undefined,
      duration: includeVideo ? normalizeDurationSeconds(resourceForm.durationSeconds) : undefined,
    };
  }

  if (service === 'path') {
    return {
      targetPeriod: payload.pathForm.targetPeriod,
      weeklyHours: payload.pathForm.weeklyHours,
      currentProgress: payload.pathForm.currentProgress,
    };
  }

  if (service === 'push') {
    const preferredTypeLabelMap: Record<string, string> = {
      CODE_CASE: '代码案例',
      EXPLANATION: '讲解文档',
      QUIZ: '练习题',
      MINDMAP: '思维导图',
      READING: '拓展阅读',
      VIDEO: '教学视频',
    };
    const composedQuery = [
      payload.pushForm.keyword,
      payload.pushForm.courseScope,
      preferredTypeLabelMap[payload.pushForm.preferredType] ?? payload.pushForm.preferredType,
    ]
      .map((item) => item?.trim())
      .filter(Boolean)
      .join(' ');
    return {
      keyword: payload.pushForm.keyword,
      resourceType: normalizeResourceType(payload.pushForm.preferredType),
      courseScope: payload.pushForm.courseScope,
      query: composedQuery,
      topic: payload.pushForm.keyword,
    };
  }

  return {
    range: payload.assessmentForm.range,
    dimensions: payload.assessmentForm.dimensions,
  };
}

function scheduleStreamFlush(
  streamQueueRef: RunByApiTaskArgs['streamQueueRef'],
  streamFlushTimerRef: RunByApiTaskArgs['streamFlushTimerRef'],
  streamRafRef: RunByApiTaskArgs['streamRafRef'],
  setServiceResultLines: RunByApiTaskArgs['setServiceResultLines'],
): void {
  if (streamFlushTimerRef.current != null) {
    return;
  }

  streamFlushTimerRef.current = window.setTimeout(() => {
    streamFlushTimerRef.current = null;
    if (streamRafRef.current != null) {
      return;
    }
    streamRafRef.current = window.requestAnimationFrame(() => {
      streamRafRef.current = null;
      flushStreamQueue(streamQueueRef, streamFlushTimerRef, streamRafRef, setServiceResultLines);
    });
  }, 60);
}

function flushStreamQueue(
  streamQueueRef: RunByApiTaskArgs['streamQueueRef'],
  streamFlushTimerRef: RunByApiTaskArgs['streamFlushTimerRef'],
  streamRafRef: RunByApiTaskArgs['streamRafRef'],
  setServiceResultLines: RunByApiTaskArgs['setServiceResultLines'],
): void {
  cleanupStreamSchedulers(streamFlushTimerRef, streamRafRef);
  if (streamQueueRef.current.length === 0) {
    return;
  }
  const chunks = [...streamQueueRef.current];
  streamQueueRef.current = [];
  setServiceResultLines((prev) => [...prev, ...chunks]);
}

export function cleanupStreamSchedulers(
  streamFlushTimerRef: RunByApiTaskArgs['streamFlushTimerRef'],
  streamRafRef: RunByApiTaskArgs['streamRafRef'],
): void {
  if (streamFlushTimerRef.current != null) {
    window.clearTimeout(streamFlushTimerRef.current);
    streamFlushTimerRef.current = null;
  }
  if (streamRafRef.current != null) {
    window.cancelAnimationFrame(streamRafRef.current);
    streamRafRef.current = null;
  }
}

function readSummary(payload: Record<string, unknown> | undefined): string {
  if (!payload) {
    return '';
  }

  const nestedLearningPath = readRecord(payload.learningPath);
  if (nestedLearningPath) {
    const learningPathSummary = readString(nestedLearningPath.summaryText);
    if (learningPathSummary) {
      return learningPathSummary;
    }
  }

  return readString(payload.summaryText) || readString(payload.summary) || readString(payload.message) || readString(payload.text) || '';
}

function formatLearningPathLines(learningPath: Record<string, unknown>): string[] {
  const lines: string[] = [];
  const goal = readString(learningPath.goal);
  const duration = readString(learningPath.duration);
  const milestones = readStringArray(learningPath.milestones);
  const rawSteps = Array.isArray(learningPath.steps) ? learningPath.steps : [];

  if (goal) {
    lines.push(`学习目标：${goal}`);
  }
  if (duration) {
    lines.push(`规划周期：${duration}`);
  }
  if (milestones.length > 0) {
    lines.push(`阶段里程碑：${milestones.join(' -> ')}`);
  }

  rawSteps.forEach((step, index) => {
    const record = readRecord(step);
    if (!record) {
      return;
    }
    const title = readString(record.title) || `阶段 ${index + 1}`;
    const objective = readString(record.objective);
    const activities = readStringArray(record.activities);
    const successCriteria = readString(record.successCriteria);

    lines.push(`${index + 1}. ${title}${objective ? `：${objective}` : ''}`);
    if (activities.length > 0) {
      lines.push(`   关键活动：${activities.join('；')}`);
    }
    if (successCriteria) {
      lines.push(`   完成标准：${successCriteria}`);
    }
  });

  return lines;
}

function readStatusHint(payload: Record<string, unknown> | undefined): string | undefined {
  if (!payload) {
    return undefined;
  }
  return readString(payload.message) || readString(payload.stage) || readString(payload.status) || undefined;
}

function formatExpiresHint(payload: Record<string, unknown> | undefined): string {
  if (!payload) {
    return '下载链接已生成';
  }

  const expiresInSec = readNumeric(payload.expiresInSec);
  if (expiresInSec !== undefined) {
    return `${expiresInSec} 秒后过期`;
  }

  const expiresAt = readString(payload.expiresAt);
  if (expiresAt) {
    return `到期时间 ${new Date(expiresAt).toLocaleString('zh-CN')}`;
  }

  return '下载链接已生成';
}

function labelForSummaryKey(key: string, service: EngineService): string {
  const commonLabels: Record<string, string> = {
    goal: '目标',
    steps: '步骤',
    weakKnowledgeTags: '薄弱知识点',
    recommendations: '建议',
    score: '得分',
    accuracy: '正确率',
    currentStage: '阶段',
    duration: '视频时长',
    videoUrl: '视频地址',
    thumbnailUrl: '缩略图',
    style: '视频风格',
    topic: '知识点',
  };

  if (commonLabels[key]) {
    return commonLabels[key];
  }

  if (service === 'path' && key === 'plan') {
    return '学习路径';
  }
  if (service === 'assessment' && key === 'judgeResult') {
    return '评估结果';
  }
  if (service === 'push' && key === 'candidates') {
    return '候选资源';
  }
  if (service === 'resource' && key === 'segments') {
    return '视频脚本分段';
  }

  return key;
}

function normalizeDurationSeconds(value: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return 60;
  }
  return Math.max(15, Math.min(180, Math.round(parsed)));
}

function resourceDifficultyLabel(difficulty: string): string {
  switch (difficulty) {
    case 'basic':
      return '基础';
    case 'intermediate':
      return '中等';
    case 'advanced':
      return '进阶';
    default:
      return difficulty.trim();
  }
}

function resourceTypeLabel(resourceType: string): string {
  switch (resourceType) {
    case 'EXPLANATION':
      return '讲解文档';
    case 'CODE_CASE':
      return '代码案例';
    case 'QUIZ':
      return '练习题';
    case 'MINDMAP':
      return '思维导图';
    case 'READING':
      return '拓展阅读';
    case 'VIDEO':
      return '教学视频';
    default:
      return resourceType.trim();
  }
}

function normalizeResourceType(resourceType: string): string {
  switch (resourceType) {
    case 'EXPLANATION':
      return 'DOCUMENT';
    case 'CODE_CASE':
      return 'CODE';
    case 'QUIZ':
      return 'DOCUMENT';
    default:
      return resourceType;
  }
}

function isVideoProgressEvent(eventType: SmartEngineStreamEvent['event']): boolean {
  return eventType.startsWith('video_gen:');
}

function mapVideoProgressEvent(eventType: SmartEngineStreamEvent['event']): { progress: number; status: string; message: string } {
  switch (eventType) {
    case 'video_gen:start':
      return { progress: 10, status: '视频任务启动', message: '视频生成任务已启动' };
    case 'video_gen:script':
      return { progress: 25, status: '脚本生成完成', message: '脚本生成完成' };
    case 'video_gen:speech':
      return { progress: 50, status: '语音合成完成', message: '语音合成完成' };
    case 'video_gen:avatar':
      return { progress: 75, status: '视频渲染中', message: '视频渲染中...' };
    case 'video_gen:complete':
      return { progress: 100, status: '视频生成完成', message: '视频生成完成' };
    default:
      return { progress: 0, status: '执行中', message: '' };
  }
}

function readDuration(payload: Record<string, unknown> | undefined): number | undefined {
  if (!payload) {
    return undefined;
  }
  const duration = readNumericRaw(payload.duration) ?? readNumericRaw(payload.durationSeconds) ?? readNumericRaw(payload.totalDuration);
  if (duration === undefined) {
    return undefined;
  }
  return Math.max(0, duration);
}

function readVideoStyle(payload: Record<string, unknown> | undefined): VideoCardStyle | undefined {
  if (!payload) {
    return undefined;
  }
  const style = readString(payload.style) || readString(payload.videoStyle);
  if (style === 'talking_head' || style === 'animation' || style === 'hybrid') {
    return style;
  }
  return undefined;
}

function readUrlField(payload: Record<string, unknown> | undefined, keys: string[]): string {
  if (!payload) {
    return '';
  }
  for (const key of keys) {
    const value = readString(payload[key]);
    if (value) {
      return value;
    }
  }
  return '';
}

function isVideoLink(item: TempDownloadLink): boolean {
  return item.resourceType === 'VIDEO' || /\.mp4($|\?)/i.test(item.url);
}

function mapDownloadToVideoResult(item: TempDownloadLink): VideoResult {
  return {
    title: item.title,
    videoUrl: item.url,
    thumbnailUrl: item.thumbnailUrl,
    duration: item.duration,
    style: item.style,
    knowledgePoint: item.knowledgePoint,
    expiresHint: item.expiresHint,
  };
}

function readVideoResult(payload: Record<string, unknown> | undefined): VideoResult | null {
  if (!payload) {
    return null;
  }
  const videoUrl =
    readUrlField(payload, ['videoUrl', 'finalVideoUrl', 'final_video_url', 'downloadUrl', 'resourceUrl']) ||
    readNestedVideoUrl(payload.result);
  if (!videoUrl || !/\.mp4($|\?)/i.test(videoUrl)) {
    return null;
  }

  return {
    title: readString(payload.title) || readString(payload.topic) || '教学视频',
    videoUrl,
    thumbnailUrl: readUrlField(payload, ['thumbnailUrl', 'thumbnail_url', 'posterUrl', 'coverUrl']),
    duration: readDuration(payload),
    style: readVideoStyle(payload),
    knowledgePoint: readString(payload.knowledgePoint) || readString(payload.topic),
    expiresHint: formatExpiresHint(payload),
  };
}

function readNestedVideoUrl(value: unknown): string {
  if (!value || typeof value !== 'object') {
    return '';
  }
  const payload = value as Record<string, unknown>;
  return readUrlField(payload, ['videoUrl', 'finalVideoUrl', 'final_video_url', 'downloadUrl', 'resourceUrl']);
}

function readNumericRaw(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return undefined;
}

function readNumeric(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return Math.max(0, Math.min(100, value));
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return Math.max(0, Math.min(100, parsed));
    }
  }
  return undefined;
}

function readString(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function readRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

function readStringArray(...values: unknown[]): string[] {
  for (const value of values) {
    if (Array.isArray(value)) {
      return value.map((item) => readString(item)).filter(Boolean);
    }
    if (typeof value === 'string' && value.trim()) {
      return value
        .split(/[、,，]/)
        .map((item) => item.trim())
        .filter(Boolean);
    }
  }
  return [];
}

function stringifyCompact(value: unknown): string {
  if (value === null || value === undefined) {
    return '';
  }
  if (typeof value === 'string') {
    return value;
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function toUiTaskStatus(status?: string): string {
  if (!status) {
    return '执行中';
  }
  if (status === 'COMPLETED') {
    return '任务完成';
  }
  if (status === 'FAILED') {
    return '任务失败';
  }
  if (status === 'PENDING' || status === 'ACCEPTED') {
    return '等待受理';
  }
  return '执行中';
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
