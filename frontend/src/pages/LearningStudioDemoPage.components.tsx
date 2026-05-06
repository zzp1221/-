import { useEffect, useRef, useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowDown, BookOpen, FileText, LoaderCircle, SendHorizontal, Sparkles } from 'lucide-react';
import VideoCard from '../components/VideoCard';
import MarkdownRenderer from '../components/MarkdownRenderer';
import {
  EMPTY_VALUE,
  assessmentDimensionOptions,
  resourceTypeButtons,
  type AssessmentForm,
  type ChatMessage,
  type EngineService,
  type EngineState,
  type PathForm,
  type ProfileSnapshot,
  type ProfileUpdateSource,
  type PushForm,
  type ResourceForm,
  type ResourceType,
  type TempDownloadLink,
  type VideoResult,
} from './LearningStudioDemoPage.types';
import { request } from '../api/request';
import { normalizeCopyText } from './LearningStudioDemoPage.utils';

export function ServiceDynamicForm(props: {
  service: EngineService | null;
  resourceForm: ResourceForm;
  pathForm: PathForm;
  pushForm: PushForm;
  assessmentForm: AssessmentForm;
  onResourceChange: (next: ResourceForm) => void;
  onPathChange: (next: PathForm) => void;
  onPushChange: (next: PushForm) => void;
  onAssessmentChange: (next: AssessmentForm) => void;
}) {
  if (!props.service) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/50 px-4 py-8 text-center dark:border-slate-700 dark:bg-slate-900/50">
        <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800">
          <Sparkles className="h-5 w-5 text-slate-400" />
        </div>
        <p className="text-sm text-slate-500 dark:text-slate-400">请先选择一项服务，再填写参数</p>
      </div>
    );
  }

  const baseInputClass = "w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all duration-200 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:focus:border-indigo-500";
  const baseSelectClass = "w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all duration-200 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:focus:border-indigo-500";
  const chipButton = (active: boolean) => `rounded-full border px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
    active
      ? 'border-indigo-300 bg-indigo-50 text-indigo-700 dark:border-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400'
      : 'border-slate-200 bg-white text-slate-600 hover:border-indigo-200 hover:text-indigo-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:border-indigo-600'
  }`;

  if (props.service === 'resource') {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-900/50 md:p-5">
        <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">资源生成参数</div>
        <div className="mb-3 flex flex-wrap gap-2">
          {resourceTypeButtons.map((item) => {
            const active = props.resourceForm.resourceTypes.includes(item.type);
            return (
              <button
                key={item.type}
                type="button"
                onClick={() => {
                  const nextTypes = active
                    ? props.resourceForm.resourceTypes.filter((x) => x !== item.type)
                    : [...props.resourceForm.resourceTypes, item.type];
                  props.onResourceChange({ ...props.resourceForm, resourceTypes: nextTypes });
                }}
                className={chipButton(active)}
              >
                {item.label}
              </button>
            );
          })}
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <input
            value={props.resourceForm.course}
            onChange={(e) => props.onResourceChange({ ...props.resourceForm, course: e.target.value })}
            placeholder="课程名称"
            className={baseInputClass}
          />
          <select
            value={props.resourceForm.difficulty}
            onChange={(e) =>
              props.onResourceChange({
                ...props.resourceForm,
                difficulty: e.target.value as ResourceForm['difficulty'],
              })
            }
            className={baseSelectClass}
          >
            <option value="basic">基础</option>
            <option value="intermediate">中等</option>
            <option value="advanced">进阶</option>
          </select>
        </div>
        <textarea
          value={props.resourceForm.keyPoints}
          onChange={(e) => props.onResourceChange({ ...props.resourceForm, keyPoints: e.target.value })}
          rows={2}
          placeholder="重点知识点（如：并发编程、线程池）"
          className={`${baseInputClass} mt-3`}
        />
        {props.resourceForm.resourceTypes.includes('VIDEO') ? (
          <div className="mt-4 rounded-2xl border border-indigo-200 bg-white p-4 dark:border-indigo-700 dark:bg-slate-900">
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
              <Sparkles className="h-4 w-4 text-indigo-500" />
              教学视频参数
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <select
                value={props.resourceForm.videoStyle}
                onChange={(e) =>
                  props.onResourceChange({
                    ...props.resourceForm,
                    videoStyle: e.target.value as ResourceForm['videoStyle'],
                  })
                }
                className={baseSelectClass}
              >
                <option value="talking_head">数字人讲解</option>
                <option value="animation">动画演示</option>
                <option value="hybrid">混合模式</option>
              </select>
              <input
                value={props.resourceForm.durationSeconds}
                onChange={(e) => props.onResourceChange({ ...props.resourceForm, durationSeconds: e.target.value })}
                placeholder="目标时长（秒）"
                className={baseInputClass}
              />
            </div>
          </div>
        ) : null}
      </div>
    );
  }

  if (props.service === 'path') {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-900/50 md:p-5">
        <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">学习路径规划参数</div>
        <div className="grid gap-3 md:grid-cols-2">
          <input
            value={props.pathForm.targetPeriod}
            onChange={(e) => props.onPathChange({ ...props.pathForm, targetPeriod: e.target.value })}
            placeholder="目标周期（如：14 天）"
            className={baseInputClass}
          />
          <input
            value={props.pathForm.weeklyHours}
            onChange={(e) => props.onPathChange({ ...props.pathForm, weeklyHours: e.target.value })}
            placeholder="每周可投入（小时）"
            className={baseInputClass}
          />
        </div>
        <textarea
          value={props.pathForm.currentProgress}
          onChange={(e) => props.onPathChange({ ...props.pathForm, currentProgress: e.target.value })}
          rows={2}
          placeholder="当前学习进度"
          className={`${baseInputClass} mt-3`}
        />
      </div>
    );
  }

  if (props.service === 'push') {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-900/50 md:p-5">
        <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">资源推送参数</div>
        <div className="grid gap-3 md:grid-cols-2">
          <input
            value={props.pushForm.keyword}
            onChange={(e) => props.onPushChange({ ...props.pushForm, keyword: e.target.value })}
            placeholder="关键词"
            className={baseInputClass}
          />
          <select
            value={props.pushForm.preferredType}
            onChange={(e) => props.onPushChange({ ...props.pushForm, preferredType: e.target.value as ResourceType })}
            className={baseSelectClass}
          >
            {resourceTypeButtons.map((item) => (
              <option key={item.type} value={item.type}>
                {item.label}
              </option>
            ))}
          </select>
        </div>
        <input
          value={props.pushForm.courseScope}
          onChange={(e) => props.onPushChange({ ...props.pushForm, courseScope: e.target.value })}
          placeholder="课程范围"
          className={`${baseInputClass} mt-3`}
        />
      </div>
    );
  }

  const nextDimensions = props.assessmentForm.dimensions;
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-900/50 md:p-5">
      <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">学习效果评估参数</div>
      <select
        value={props.assessmentForm.range}
        onChange={(e) => props.onAssessmentChange({ ...props.assessmentForm, range: e.target.value as AssessmentForm['range'] })}
        className={`${baseSelectClass} mb-3`}
      >
        <option value="7d">近 7 天</option>
        <option value="30d">近 30 天</option>
        <option value="60d">近 60 天</option>
      </select>
      <div className="flex flex-wrap gap-2">
        {assessmentDimensionOptions.map((item) => {
          const checked = nextDimensions.includes(item);
          return (
            <button
              key={item}
              type="button"
              onClick={() => {
                const merged = checked ? nextDimensions.filter((x) => x !== item) : [...nextDimensions, item];
                props.onAssessmentChange({ ...props.assessmentForm, dimensions: merged });
              }}
              className={chipButton(checked)}
            >
              {item}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function ServiceSubmitPanel(props: {
  disabled: boolean;
  onSubmit: () => void;
  onStop?: () => void;
  canStop?: boolean;
  taskId: string;
  progress: number;
  status: string;
  uiState: EngineState;
}) {
  const progress = Math.max(0, Math.min(100, props.progress));
  const isRunning = props.uiState === 'ENGINE_RUNNING' || props.uiState === 'ENGINE_SUBMITTING';

  return (
    <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900 md:p-5">
      <div className="flex gap-3">
        <button
          type="button"
          onClick={props.onSubmit}
          disabled={props.disabled}
          className="flex-1 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl hover:shadow-indigo-500/30 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none active:scale-[0.98]"
        >
          {isRunning ? '提交中...' : '提交任务'}
        </button>
        <button
          type="button"
          onClick={props.onStop}
          disabled={!props.canStop}
          className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800"
        >
          停止
        </button>
      </div>

      {props.taskId ? (
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-mono text-slate-400 dark:text-slate-500">任务 #{props.taskId.slice(0, 12)}...</span>
            <span className={`font-medium ${
              progress >= 100 ? 'text-emerald-600 dark:text-emerald-400' :
              isRunning ? 'text-indigo-600 dark:text-indigo-400' :
              'text-slate-500 dark:text-slate-400'
            }`}>
              {props.status}
            </span>
          </div>
          <div className="relative h-2.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <motion.div
              className={`absolute inset-y-0 left-0 rounded-full ${
                progress >= 100
                  ? 'bg-gradient-to-r from-emerald-400 to-emerald-500'
                  : 'bg-gradient-to-r from-indigo-500 to-violet-500'
              }`}
              initial={false}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
            {isRunning && progress < 100 ? (
              <div className="absolute inset-y-0 left-0 w-20 animate-shimmer rounded-full bg-gradient-to-r from-transparent via-white/30 to-transparent" />
            ) : null}
          </div>
          <div className="text-right text-[11px] text-slate-400 dark:text-slate-500">{progress}%</div>
        </div>
      ) : null}
    </div>
  );
}

export function TaskResultPanel(props: {
  service: EngineService | null;
  taskSummary: string;
  serviceResultLines: string[];
  downloadLinks: TempDownloadLink[];
  videoResult: VideoResult | null;
}) {
  const handleDownload = async (item: TempDownloadLink) => {
    const absoluteUrl = /^https?:\/\//i.test(item.url) ? item.url : `${window.location.origin}${item.url.startsWith('/') ? item.url : `/${item.url}`}`;
    const response = await request.getInstance().get(absoluteUrl, {
      responseType: 'blob',
    });
    const blobUrl = window.URL.createObjectURL(response.data as Blob);
    const anchor = document.createElement('a');
    anchor.href = blobUrl;
    anchor.download = item.fileName || extractFileName(item.url, item.title);
    anchor.target = '_blank';
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    window.URL.revokeObjectURL(blobUrl);
  };

  if (!props.service) {
    return null;
  }

  const hasContent = Boolean(props.taskSummary) || props.serviceResultLines.length > 0 || props.downloadLinks.length > 0 || Boolean(props.videoResult);
  if (!hasContent) {
    return null;
  }

  return (
    <div className="space-y-4">
      {props.videoResult ? (
        <div className="modern-card overflow-hidden">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <Sparkles className="h-4 w-4 text-indigo-500" />
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">视频结果</span>
          </div>
          <div className="p-4">
            <VideoCard
              title={props.videoResult.title}
              videoUrl={props.videoResult.videoUrl}
              thumbnailUrl={props.videoResult.thumbnailUrl}
              duration={props.videoResult.duration}
              style={props.videoResult.style}
              knowledgePoint={props.videoResult.knowledgePoint}
              expiresHint={props.videoResult.expiresHint}
            />
          </div>
        </div>
      ) : null}

      <div className="modern-card overflow-hidden">
        <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
          <BookOpen className="h-4 w-4 text-indigo-500" />
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">任务结果</span>
        </div>
        <div className="p-4">
          {props.taskSummary ? (
            <div className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-sm leading-7 text-slate-700 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-300">
              <MarkdownRenderer content={props.taskSummary} />
            </div>
          ) : null}
          {props.serviceResultLines.length > 0 ? (
            <ul className="space-y-2">
              {props.serviceResultLines.map((line, index) => (
                <li key={`${index}-${line}`} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <span className="mt-1.5 block h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" />
                  {line}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </div>

      {props.downloadLinks.length > 0 ? (
        <div className="modern-card overflow-hidden">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <FileText className="h-4 w-4 text-indigo-500" />
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">产物下载</span>
          </div>
          <div className="p-4">
            <div className="grid gap-2 md:grid-cols-2">
              {props.downloadLinks.map((item) => (
                <div
                  key={`${item.title}-${item.url}`}
                  className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-3 transition-all hover:border-indigo-200 hover:bg-white dark:border-slate-700 dark:bg-slate-900/50 dark:hover:border-indigo-700"
                >
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium text-slate-700 dark:text-slate-300">{item.title}</div>
                    <div className="mt-0.5 flex items-center gap-2 text-[11px] text-slate-400 dark:text-slate-500">
                      {item.resourceType ? <span>{item.resourceType}</span> : null}
                      <span>{item.expiresHint}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => { void handleDownload(item); }}
                    className="shrink-0 rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-600 transition-colors hover:bg-indigo-100 dark:bg-indigo-500/10 dark:text-indigo-400 dark:hover:bg-indigo-500/20"
                  >
                    下载
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function extractFileName(url: string, fallbackTitle: string): string {
  try {
    const normalizedUrl = /^https?:\/\//i.test(url) ? url : `${window.location.origin}${url.startsWith('/') ? url : `/${url}`}`;
    const pathname = new URL(normalizedUrl).pathname;
    const basename = pathname.split('/').filter(Boolean).pop();
    return basename || fallbackTitle;
  } catch {
    return fallbackTitle;
  }
}

export function RealtimeProfile(props: {
  profile: ProfileSnapshot | null;
  summary: string;
  updatedAt: string;
  source: ProfileUpdateSource;
  showAllWeakPoints: boolean;
  onToggleWeakPoints: () => void;
}) {
  const allWeakPoints = props.profile?.weakPoints ?? [];
  const weakPoints = props.showAllWeakPoints ? allWeakPoints : allWeakPoints.slice(0, 3);

  if (!props.profile) {
    return (
      <div className="modern-card px-5 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">学习画像</h2>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] text-slate-500 dark:bg-slate-800 dark:text-slate-400">暂无数据</span>
        </div>
        <p className="mt-4 text-sm text-slate-400 dark:text-slate-500">完成对话或提交任务后，AI 将自动生成你的学习画像。</p>
      </div>
    );
  }

  return (
    <div className="modern-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3 dark:border-slate-800">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">学习画像</h2>
        <span className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${
          props.source === 'BACKEND'
            ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400'
            : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400'
        }`}>
          {props.source === 'BACKEND' ? '系统分析' : '实时更新'}
        </span>
      </div>
      <div className="p-5">
        <div className="grid gap-3 md:grid-cols-2">
          <ProfileCell label="课程方向" value={props.profile.major || EMPTY_VALUE} />
          <ProfileCell label="学习目标" value={props.profile.goal || EMPTY_VALUE} />
          <ProfileCell label="知识基础" value={props.profile.knowledgeBase || EMPTY_VALUE} />
          <ProfileCell
            label="薄弱知识点"
            value={
              weakPoints.length > 0 ? (
                <div className="space-y-1.5">
                  {weakPoints.map((item) => (
                    <div key={item} className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
                      {item}
                    </div>
                  ))}
                  {allWeakPoints.length > 3 ? (
                    <button type="button" onClick={props.onToggleWeakPoints} className="text-xs font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">
                      {props.showAllWeakPoints ? '收起' : `展开全部 (${allWeakPoints.length}项)`}
                    </button>
                  ) : null}
                </div>
              ) : (
                EMPTY_VALUE
              )
            }
          />
          <ProfileCell label="偏好学习方式" value={props.profile.preference?.join('、') || EMPTY_VALUE} />
          <ProfileCell label="认知风格" value={props.profile.cognitiveStyle || EMPTY_VALUE} />
          <ProfileCell label="置信等级" value={props.profile.confidenceLevel || EMPTY_VALUE} />
          <ProfileCell label="画像摘要" value={props.summary || EMPTY_VALUE} />
        </div>
        <div className="mt-4 flex items-center gap-4 border-t border-slate-100 pt-4 text-[11px] text-slate-400 dark:border-slate-800 dark:text-slate-500">
          <span>更新于 {props.updatedAt ? new Date(props.updatedAt).toLocaleString('zh-CN') : EMPTY_VALUE}</span>
        </div>
      </div>
    </div>
  );
}

export function ChatPanel({ messages }: { messages: ChatMessage[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);

  const isStreaming = messages.length > 0 && messages[messages.length - 1]?.role === 'assistant' && !messages[messages.length - 1]?.content;

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !autoFollow) {
      return;
    }
    container.scrollTop = container.scrollHeight;
  }, [autoFollow, messages]);

  const handleScroll = () => {
    const container = containerRef.current;
    if (!container) {
      return;
    }
    const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    setAutoFollow(distanceToBottom < 64);
  };

  const handleCopy = async (message: ChatMessage) => {
    try {
      await navigator.clipboard.writeText(normalizeCopyText(message.content));
      setCopiedMessageId(message.id);
      window.setTimeout(() => {
        setCopiedMessageId((prev) => (prev === message.id ? null : prev));
      }, 1200);
    } catch {
      // ignore clipboard errors
    }
  };

  return (
    <div className="relative flex-1">
      <div ref={containerRef} onScroll={handleScroll} className="h-full space-y-6 overflow-y-auto px-2 py-4 scrollbar-thin md:space-y-8 md:px-8">
      <AnimatePresence>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[90%] md:max-w-[82%] ${msg.role === 'user' ? '' : 'w-full md:w-auto'}`}>
              {msg.role === 'user' ? (
                <div className="rounded-2xl rounded-br-md bg-indigo-600 px-4 py-2.5 text-[15px] leading-7 text-white shadow-sm">
                  {msg.content}
                </div>
              ) : (
                <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
                  {msg.content ? (
                    <MarkdownRenderer
                      content={msg.content}
                      isStreaming={msg.id === messages[messages.length - 1]?.id && isStreaming}
                    />
                  ) : (
                    <MarkdownRenderer content="" isStreaming={true} />
                  )}
                </div>
              )}
              {msg.content ? (
                <div className={`mt-1.5 flex items-center gap-2 text-xs ${msg.role === 'user' ? 'justify-end' : ''}`}>
                  {msg.role === 'assistant' ? (
                    <span className="text-slate-400 dark:text-slate-500">
                      <Sparkles className="inline h-3 w-3" /> 智学引擎
                    </span>
                  ) : null}
                  <button
                    type="button"
                    onClick={() => handleCopy(msg)}
                    className="rounded-md px-1.5 py-0.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:text-slate-500 dark:hover:bg-slate-800 dark:hover:text-slate-300"
                  >
                    {copiedMessageId === msg.id ? '已复制' : '复制'}
                  </button>
                </div>
              ) : null}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      </div>
      {!autoFollow ? (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          type="button"
          onClick={() => {
            const container = containerRef.current;
            if (!container) {
              return;
            }
            container.scrollTop = container.scrollHeight;
            setAutoFollow(true);
          }}
          className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-600 shadow-lg transition-all hover:shadow-xl dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
        >
          <ArrowDown className="mr-1.5 inline h-3.5 w-3.5" />
          回到底部
        </motion.button>
      ) : null}
    </div>
  );
}

export function InputPanel(props: {
  value: string;
  busy: boolean;
  placeholder: string;
  onChange: (value: string) => void;
  onSend: () => void;
  variant?: 'landing' | 'chat';
}) {
  const isLanding = props.variant === 'landing';

  return (
    <div className="shrink-0 px-2 pb-4 md:px-0">
      <div className={`mx-auto transition-all duration-300 ${
        isLanding
          ? 'rounded-3xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-900'
          : 'rounded-3xl border border-slate-200 bg-white shadow-sm focus-within:shadow-md focus-within:ring-2 focus-within:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-900 dark:focus-within:ring-indigo-500/10'
      }`}>
        <div className="px-4 pt-4 md:px-5 md:pt-5">
          <textarea
            value={props.value}
            onChange={(e) => props.onChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                props.onSend();
              }
            }}
            rows={isLanding ? 3 : 2}
            placeholder={props.placeholder}
            className="w-full resize-none border-none bg-transparent text-[15px] leading-7 text-slate-800 outline-none placeholder:text-slate-400 dark:text-slate-200 dark:placeholder:text-slate-500"
          />
        </div>
        <div className="flex items-center justify-between px-4 pb-3 md:px-5 md:pb-4">
          <div className="flex items-center gap-3 text-xs text-slate-400 dark:text-slate-500">
            {isLanding ? (
              <span>按 Enter 发送你的第一个问题</span>
            ) : (
              <>
                <kbd className="hidden rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-mono text-[10px] text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 sm:inline">Enter</kbd>
                <span className="hidden sm:inline">发送</span>
                <kbd className="hidden rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-mono text-[10px] text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 sm:inline">Shift + Enter</kbd>
                <span className="hidden sm:inline">换行</span>
              </>
            )}
          </div>
          <button
            type="button"
            onClick={props.onSend}
            disabled={props.busy || !props.value.trim()}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl hover:shadow-indigo-500/30 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none active:scale-95"
          >
            {props.busy ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}

function ProfileCell({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50/50 px-3.5 py-2.5 dark:border-slate-800 dark:bg-slate-900/50">
      <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500">{label}</div>
      <div className="mt-1 text-[13px] leading-relaxed text-slate-700 dark:text-slate-300">{value}</div>
    </div>
  );
}
