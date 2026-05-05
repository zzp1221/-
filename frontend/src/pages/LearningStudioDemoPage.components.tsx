import { useEffect, useRef, useState, type ReactNode } from 'react';
import { BookOpen, LoaderCircle, SendHorizontal } from 'lucide-react';
import VideoCard from '../components/VideoCard';
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
    return <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">请先选择服务，再填写参数。</div>;
  }

  if (props.service === 'resource') {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div className="mb-3 text-sm font-medium text-slate-700">资源生成参数</div>
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
                className={`rounded-full border px-3 py-1 text-xs ${
                  active ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-slate-200 bg-white text-slate-600'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
        <div className="grid gap-2 md:grid-cols-2">
          <input
            value={props.resourceForm.course}
            onChange={(e) => props.onResourceChange({ ...props.resourceForm, course: e.target.value })}
            placeholder="课程"
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
          />
          <select
            value={props.resourceForm.difficulty}
            onChange={(e) =>
              props.onResourceChange({
                ...props.resourceForm,
                difficulty: e.target.value as ResourceForm['difficulty'],
              })
            }
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
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
          placeholder="重点知识点"
          className="mt-2 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
        />
        {props.resourceForm.resourceTypes.includes('VIDEO') ? (
          <div className="mt-3 rounded-xl border border-blue-100 bg-white p-3">
            <div className="mb-3 text-sm font-medium text-slate-700">教学视频参数</div>
            <div className="grid gap-2 md:grid-cols-2">
              <select
                value={props.resourceForm.videoStyle}
                onChange={(e) =>
                  props.onResourceChange({
                    ...props.resourceForm,
                    videoStyle: e.target.value as ResourceForm['videoStyle'],
                  })
                }
                className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
              >
                <option value="talking_head">数字人讲解</option>
                <option value="animation">动画演示</option>
                <option value="hybrid">混合模式</option>
              </select>
              <input
                value={props.resourceForm.durationSeconds}
                onChange={(e) => props.onResourceChange({ ...props.resourceForm, durationSeconds: e.target.value })}
                placeholder="目标时长（秒）"
                className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
              />
            </div>
            <div className="mt-2 text-xs text-slate-500">选择“教学视频/动画”时，会把知识点、课程、难度、风格偏好和目标时长一起提交给后端。</div>
          </div>
        ) : null}
      </div>
    );
  }

  if (props.service === 'path') {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div className="mb-3 text-sm font-medium text-slate-700">学习路径规划参数</div>
        <div className="grid gap-2 md:grid-cols-2">
          <input
            value={props.pathForm.targetPeriod}
            onChange={(e) => props.onPathChange({ ...props.pathForm, targetPeriod: e.target.value })}
            placeholder="目标周期"
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
          />
          <input
            value={props.pathForm.weeklyHours}
            onChange={(e) => props.onPathChange({ ...props.pathForm, weeklyHours: e.target.value })}
            placeholder="可投入时间（小时/周）"
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
          />
        </div>
        <textarea
          value={props.pathForm.currentProgress}
          onChange={(e) => props.onPathChange({ ...props.pathForm, currentProgress: e.target.value })}
          rows={2}
          placeholder="当前进度"
          className="mt-2 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
        />
      </div>
    );
  }

  if (props.service === 'push') {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div className="mb-3 text-sm font-medium text-slate-700">资源推送参数</div>
        <div className="grid gap-2 md:grid-cols-2">
          <input
            value={props.pushForm.keyword}
            onChange={(e) => props.onPushChange({ ...props.pushForm, keyword: e.target.value })}
            placeholder="关键词"
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
          />
          <select
            value={props.pushForm.preferredType}
            onChange={(e) => props.onPushChange({ ...props.pushForm, preferredType: e.target.value as ResourceType })}
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
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
          className="mt-2 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
        />
      </div>
    );
  }

  const nextDimensions = props.assessmentForm.dimensions;
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="mb-3 text-sm font-medium text-slate-700">学习效果评估参数</div>
      <select
        value={props.assessmentForm.range}
        onChange={(e) => props.onAssessmentChange({ ...props.assessmentForm, range: e.target.value as AssessmentForm['range'] })}
        className="mb-3 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
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
              className={`rounded-full border px-3 py-1 text-xs ${
                checked ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-slate-200 bg-white text-slate-600'
              }`}
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
  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex gap-3">
        <button
          type="button"
          onClick={props.onSubmit}
          disabled={props.disabled}
          className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          提交
        </button>
        <button
          type="button"
          onClick={props.onStop}
          disabled={!props.canStop}
          className="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          停止生成
        </button>
      </div>
      <div className="mt-3 grid gap-2 text-xs text-slate-500 md:grid-cols-4">
        <div>taskId：{props.taskId || '--'}</div>
        <div>进度：{props.progress}%</div>
        <div>状态：{props.status}</div>
        <div>状态机：{props.uiState}</div>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-blue-500 transition-all" style={{ width: `${Math.max(0, Math.min(100, props.progress))}%` }} />
      </div>
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
        <Card title="视频结果">
          <VideoCard
            title={props.videoResult.title}
            videoUrl={props.videoResult.videoUrl}
            thumbnailUrl={props.videoResult.thumbnailUrl}
            duration={props.videoResult.duration}
            style={props.videoResult.style}
            knowledgePoint={props.videoResult.knowledgePoint}
            expiresHint={props.videoResult.expiresHint}
          />
        </Card>
      ) : null}
      <Card title="任务结果">
        {props.taskSummary ? <div className="text-sm text-slate-700">{props.taskSummary}</div> : null}
        {props.serviceResultLines.length > 0 ? (
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            {props.serviceResultLines.map((line, index) => (
              <li key={`${index}-${line}`}>{line}</li>
            ))}
          </ul>
        ) : null}
      </Card>
      {props.downloadLinks.length > 0 ? (
        <Card title="产物下载">
          <div className="space-y-2 text-sm text-slate-700">
            {props.downloadLinks.map((item) => (
              <div key={`${item.title}-${item.url}`} className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
                <div>
                  <div className="font-medium text-slate-700">{item.title}</div>
                  <div className="text-xs text-slate-500">{item.expiresHint}</div>
                  {item.resourceType ? <div className="text-xs text-slate-400">类型：{item.resourceType}</div> : null}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    void handleDownload(item);
                  }}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  下载
                </button>
              </div>
            ))}
          </div>
        </Card>
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

  return (
    <div className="rounded-2xl border border-blue-100 bg-white px-5 py-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-800">画像快照</h2>
        <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs text-blue-700">{props.source}</span>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <ProfileCell label="课程方向" value={props.profile?.major || EMPTY_VALUE} />
        <ProfileCell label="学习目标" value={props.profile?.goal || EMPTY_VALUE} />
        <ProfileCell label="知识基础" value={props.profile?.knowledgeBase || EMPTY_VALUE} />
        <ProfileCell
          label="薄弱知识点"
          value={
            weakPoints.length > 0 ? (
              <div className="space-y-1.5">
                {weakPoints.map((item) => (
                  <div key={item}>{item}</div>
                ))}
                {allWeakPoints.length > 3 ? (
                  <button type="button" onClick={props.onToggleWeakPoints} className="text-xs text-blue-600 hover:text-blue-700">
                    {props.showAllWeakPoints ? '收起' : '展开全部'}
                  </button>
                ) : null}
              </div>
            ) : (
              EMPTY_VALUE
            )
          }
        />
        <ProfileCell label="偏好学习方式" value={props.profile?.preference?.join('、') || EMPTY_VALUE} />
        <ProfileCell label="认知风格" value={props.profile?.cognitiveStyle || EMPTY_VALUE} />
        <ProfileCell label="置信等级" value={props.profile?.confidenceLevel || EMPTY_VALUE} />
        <ProfileCell label="画像摘要" value={props.summary || EMPTY_VALUE} />
      </div>
      <div className="mt-3 grid gap-2 border-t border-slate-200 pt-3 text-xs text-slate-500 md:grid-cols-2">
        <div>更新时间：{props.updatedAt ? new Date(props.updatedAt).toLocaleString('zh-CN') : EMPTY_VALUE}</div>
        <div>来源：{props.source}</div>
      </div>
    </div>
  );
}

export function ChatPanel({ messages }: { messages: ChatMessage[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);

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
      <div ref={containerRef} onScroll={handleScroll} className="h-full space-y-8 overflow-y-auto px-8 py-4">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className="max-w-[82%] text-sm leading-8">
            <div className={`whitespace-pre-wrap break-words ${msg.role === 'user' ? 'rounded-2xl bg-blue-600 px-4 py-2.5 text-white' : 'px-1 py-1 text-slate-700'}`}>
              {msg.content || (msg.role === 'assistant' ? '思考中...' : '')}
            </div>
            <div className={`mt-1.5 text-xs ${msg.role === 'user' ? 'text-right text-blue-200' : 'text-slate-400'}`}>
              <button
                type="button"
                onClick={() => handleCopy(msg)}
                className="rounded px-1.5 py-0.5 hover:bg-slate-100 hover:text-slate-500"
              >
                {copiedMessageId === msg.id ? '已复制' : '复制'}
              </button>
            </div>
          </div>
        </div>
      ))}
      </div>
      {!autoFollow ? (
        <button
          type="button"
          onClick={() => {
            const container = containerRef.current;
            if (!container) {
              return;
            }
            container.scrollTop = container.scrollHeight;
            setAutoFollow(true);
          }}
          className="absolute bottom-4 right-8 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 shadow-sm hover:bg-slate-50"
        >
          回到底部
        </button>
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
    <div className="mt-4 rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
      <textarea
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            props.onSend();
          }
        }}
        rows={2}
        placeholder={props.placeholder}
        className="w-full resize-none border-none bg-transparent text-[15px] leading-7 text-slate-800 outline-none placeholder:text-slate-400"
      />
      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          {!isLanding ? <span className="text-xs text-slate-400">Enter 发送，Shift + Enter 换行</span> : null}
        </div>
        <button
          type="button"
          onClick={props.onSend}
          disabled={props.busy || !props.value.trim()}
          className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {props.busy ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}

function ProfileCell({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-sm text-slate-700">{value}</div>
    </div>
  );
}

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
        <BookOpen className="h-4 w-4 text-blue-600" />
        {title}
      </div>
      {children}
    </div>
  );
}
