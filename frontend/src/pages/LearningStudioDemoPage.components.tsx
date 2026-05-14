import { useEffect, useRef, useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ArrowDown, Brain, BookOpen, CheckCircle2, Clock3, ExternalLink, FileText, LoaderCircle, SendHorizontal, Sparkles, Target, TrendingUp, TriangleAlert, XCircle } from 'lucide-react';
import CodeBlock from '../components/CodeBlock';
import RadarChart from '../components/RadarChart';
import ScoreProgressBar from '../components/ScoreProgressBar';
import VideoCard from '../components/VideoCard';
import MarkdownRenderer from '../components/MarkdownRenderer';
import MermaidDiagram from '../components/MermaidDiagram';
import {
  EMPTY_VALUE,
  assessmentDimensionOptions,
  pushResourceTypeOptions,
  resourceTypeButtons,
  type AssessmentForm,
  type ChatMessage,
  type EngineService,
  type EngineState,
  type InlineResourceView,
  type ProfileDimensionScore,
  type PathForm,
  type ProfileSnapshot,
  type ProfileTimelinePoint,
  type ProfileUpdateSource,
  type PracticeJudgeResult,
  type PracticeQuestionBatch,
  type PushForm,
  type ResourceForm,
  type TempDownloadLink,
  type VideoResult,
  type WeakPointRank,
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

  const baseInputClass = "w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all duration-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:focus:border-primary-500";
  const baseSelectClass = "w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all duration-200 focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:focus:border-primary-500";
  const chipButton = (active: boolean) => `rounded-full border px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
    active
      ? 'border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-500/10 dark:text-primary-400'
      : 'border-slate-200 bg-white text-slate-600 hover:border-primary-200 hover:text-primary-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:border-primary-600'
  }`;

  if (props.service === 'resource') {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-900/50 md:p-5">
        <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">资源生成参数</div>
        <div className="mb-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {resourceTypeButtons.map((item) => {
            const active = props.resourceForm.resourceType === item.type;
            return (
              <button
                key={item.type}
                type="button"
                onClick={() => props.onResourceChange({ ...props.resourceForm, resourceType: item.type })}
                className={`${chipButton(active)} w-full justify-center py-2 text-sm`}
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
        {props.resourceForm.resourceType === 'VIDEO' ? (
          <div className="mt-4 rounded-2xl border border-primary-200 bg-primary-50/70 px-4 py-3 text-sm text-primary-700 dark:border-primary-700 dark:bg-primary-500/10 dark:text-primary-200">
            已固定为数字人视频生成，系统将按默认时长自动完成脚本、TTS，并在当前浏览器本地渲染视频。
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
        <select
          value={props.pushForm.preferredType}
          onChange={(e) => props.onPushChange({ ...props.pushForm, preferredType: e.target.value as typeof props.pushForm.preferredType })}
          className={baseSelectClass}
        >
          {pushResourceTypeOptions.map((item) => (
            <option key={item.type} value={item.type}>
              {item.label}
            </option>
          ))}
        </select>
        <div className="mt-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
          具体推送内容将结合当前画像、薄弱点和学习方向自动筛选，不再手动输入关键词和课程范围。
        </div>
      </div>
    );
  }

  const nextDimensions = props.assessmentForm.dimensions;
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-900/50 md:p-5">
      <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">学习效果评估参数</div>
      <div className="flex flex-wrap gap-2">
        {assessmentDimensionOptions.map((item) => {
          const checked = nextDimensions.includes(item);
          return (
            <button
              key={item}
              type="button"
              onClick={() => {
                props.onAssessmentChange({ ...props.assessmentForm, dimensions: [item] });
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
          className="flex-1 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary-500/25 transition-all hover:shadow-md hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none active:scale-[0.98]"
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
              isRunning ? 'text-primary-600 dark:text-primary-400' :
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
                  : 'bg-primary-500'
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

function InlineResourcePanel(props: { resource: InlineResourceView }) {
  if (props.resource.kind === 'code') {
    return (
      <div className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 dark:border-slate-800 dark:bg-slate-900/50">
        <div className="mb-3">
          <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">{props.resource.title}</div>
          {props.resource.summary ? (
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">{props.resource.summary}</div>
          ) : null}
        </div>
        <CodeBlock language={props.resource.language || 'text'}>{props.resource.content}</CodeBlock>
        {props.resource.explanation ? (
          <div className="mt-4 rounded-xl border border-primary-100 bg-white p-4 dark:border-primary-900 dark:bg-slate-950">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-primary-600 dark:text-primary-400">讲解</div>
            <MarkdownRenderer content={props.resource.explanation} />
          </div>
        ) : null}
      </div>
    );
  }

  if (props.resource.kind === 'mermaid') {
    return (
      <div className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 dark:border-slate-800 dark:bg-slate-900/50">
        <div className="mb-3">
          <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">{props.resource.title}</div>
          {props.resource.summary ? (
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">{props.resource.summary}</div>
          ) : null}
        </div>
        <MermaidDiagram chart={props.resource.content} />
      </div>
    );
  }

  return (
    <div className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-sm leading-7 text-slate-700 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-300">
      <MarkdownRenderer content={props.resource.content} />
    </div>
  );
}

function PracticeQuestionPanel(props: {
  batch: PracticeQuestionBatch;
  judgeResult: PracticeJudgeResult | null;
  canSubmit: boolean;
  onSubmitAnswers: (batch: PracticeQuestionBatch, answers: Record<string, string>) => void;
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  return (
    <div className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 dark:border-slate-800 dark:bg-slate-900/50">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">{props.batch.title}</div>
          <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            主题：{props.batch.topic || '未指定'} · 难度：{props.batch.difficulty || '未指定'}
          </div>
          {props.batch.description ? (
            <div className="mt-3 rounded-xl border border-primary-100 bg-primary-50/70 px-3 py-2 text-sm leading-6 text-primary-700 dark:border-primary-900 dark:bg-primary-500/10 dark:text-primary-200">
              {props.batch.description}
            </div>
          ) : null}
        </div>
        <button
          type="button"
          disabled={!props.canSubmit}
          onClick={() => props.onSubmitAnswers(props.batch, answers)}
          className="shrink-0 rounded-lg bg-primary-600 px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {props.batch.submitLabel || '提交答案并判题'}
        </button>
      </div>

      <div className="space-y-4">
        {props.batch.questions.map((question, index) => (
          <div key={question.questionId} className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-950">
            <div className="text-sm font-medium text-slate-700 dark:text-slate-300">
              {index + 1}. {question.stem}
            </div>
            {question.options && question.options.length > 0 ? (
              <div className="mt-3 space-y-2">
                {question.options.map((option, optionIndex) => {
                  const optionLabel = String.fromCharCode(65 + optionIndex);
                  const checked = answers[question.questionId] === optionLabel;
                  return (
                    <label
                      key={`${question.questionId}-${optionLabel}`}
                      className="flex cursor-pointer items-start gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 transition-colors hover:border-primary-300 dark:border-slate-700 dark:text-slate-400 dark:hover:border-primary-700"
                    >
                      <input
                        type="radio"
                        name={question.questionId}
                        checked={checked}
                        onChange={() => setAnswers((prev) => ({ ...prev, [question.questionId]: optionLabel }))}
                        className="mt-1"
                      />
                      <span>{optionLabel}. {option}</span>
                    </label>
                  );
                })}
              </div>
            ) : (
              <textarea
                value={answers[question.questionId] || ''}
                onChange={(event) => setAnswers((prev) => ({ ...prev, [question.questionId]: event.target.value }))}
                rows={4}
                className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
                placeholder="请输入你的答案"
              />
            )}
          </div>
        ))}
      </div>

      {props.judgeResult ? (
        <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50/60 p-4 dark:border-emerald-900 dark:bg-emerald-500/10">
          <div className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">{props.judgeResult.title}</div>
          <div className="mt-1 text-sm text-emerald-700/90 dark:text-emerald-200">{props.judgeResult.summary}</div>
          {props.judgeResult.specializedAnalysis ? (
            <div className="mt-4 rounded-xl border border-white/70 bg-white/80 p-4 dark:border-slate-800 dark:bg-slate-950">
              <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                {props.judgeResult.specializedAnalysis.title}
              </div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {props.judgeResult.specializedAnalysis.summary}
              </div>
              {props.judgeResult.specializedAnalysis.markdown ? (
                <div className="mt-3 text-sm leading-7 text-slate-700 dark:text-slate-300">
                  <MarkdownRenderer content={props.judgeResult.specializedAnalysis.markdown} />
                </div>
              ) : null}
            </div>
          ) : null}
          <div className="mt-3 text-xs text-emerald-700/80 dark:text-emerald-300">
            总分：{props.judgeResult.totalScore} · 正确率：{Math.round((props.judgeResult.accuracy || 0) * 100)}%
          </div>
          <div className="mt-4 space-y-3">
            {props.judgeResult.items.map((item) => (
              <div key={item.questionId} className="rounded-lg border border-emerald-200 bg-white px-3 py-3 dark:border-emerald-900 dark:bg-slate-950">
                <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
                  {item.isCorrect ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <XCircle className="h-4 w-4 text-rose-500" />}
                  {item.questionId} · 得分 {item.score}
                </div>
                <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">你的答案：{item.learnerAnswer || '未作答'}</div>
                {item.correctAnswer ? (
                  <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">参考答案：{item.correctAnswer}</div>
                ) : null}
                {item.reason ? <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">判定依据：{item.reason}</div> : null}
                {item.feedback ? <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">反馈建议：{item.feedback}</div> : null}
              </div>
            ))}
          </div>
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
  inlineResource: InlineResourceView | null;
  practiceBatch: PracticeQuestionBatch | null;
  judgeResult: PracticeJudgeResult | null;
  canSubmitPractice: boolean;
  onSubmitPracticeAnswers: (batch: PracticeQuestionBatch, answers: Record<string, string>) => void;
}) {
  const externalRecommendations = props.service === 'push'
    ? props.downloadLinks.filter(isExternalRecommendation)
    : [];
  const fileDownloads = props.service === 'push'
    ? []
    : props.downloadLinks.filter((item) => !isExternalRecommendation(item));

  const handleDownload = async (item: TempDownloadLink) => {
    const absoluteUrl = /^https?:\/\//i.test(item.url) ? item.url : `${window.location.origin}${item.url.startsWith('/') ? item.url : `/${item.url}`}`;
    const sameOrigin = absoluteUrl.startsWith(window.location.origin);
    const fallbackOpen = () => {
      const anchor = document.createElement('a');
      anchor.href = absoluteUrl;
      anchor.target = '_blank';
      anchor.rel = 'noopener noreferrer';
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
    };

    if (!sameOrigin) {
      fallbackOpen();
      return;
    }

    try {
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
    } catch {
      fallbackOpen();
    }
  };

  if (!props.service) {
    return null;
  }

  const hasContent = Boolean(props.taskSummary)
    || props.serviceResultLines.length > 0
    || props.downloadLinks.length > 0
    || Boolean(props.videoResult)
    || Boolean(props.inlineResource)
    || Boolean(props.practiceBatch)
    || Boolean(props.judgeResult);
  if (!hasContent) {
    return null;
  }

  return (
    <div className="space-y-4">
      {props.videoResult ? (
        <div className="modern-card overflow-hidden">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <Sparkles className="h-4 w-4 text-primary-500" />
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
              fileName={props.videoResult.fileName}
            />
          </div>
        </div>
      ) : null}

      {externalRecommendations.length > 0 ? (
        <div className="modern-card overflow-hidden">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <Sparkles className="h-4 w-4 text-primary-500" />
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">推荐资源</span>
          </div>
          <div className="grid gap-3 p-4 md:grid-cols-2">
            {externalRecommendations.map((item) => (
              <ExternalResourceRecommendationCard key={`${item.title}-${item.url}`} item={item} />
            ))}
          </div>
        </div>
      ) : null}

      <div className="modern-card overflow-hidden">
        <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
          <BookOpen className="h-4 w-4 text-primary-500" />
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">任务结果</span>
        </div>
        <div className="p-4">
          {props.service === 'assessment' && props.practiceBatch ? (
            <PracticeQuestionPanel
              batch={props.practiceBatch}
              judgeResult={props.judgeResult}
              canSubmit={props.canSubmitPractice}
              onSubmitAnswers={props.onSubmitPracticeAnswers}
            />
          ) : null}
          {props.inlineResource ? (
            <InlineResourcePanel resource={props.inlineResource} />
          ) : null}
          {props.service !== 'assessment' && props.practiceBatch ? (
            <PracticeQuestionPanel
              batch={props.practiceBatch}
              judgeResult={props.judgeResult}
              canSubmit={props.canSubmitPractice}
              onSubmitAnswers={props.onSubmitPracticeAnswers}
            />
          ) : null}
          {props.taskSummary ? (
            <div className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-sm leading-7 text-slate-700 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-300">
              <MarkdownRenderer content={props.taskSummary} />
            </div>
          ) : null}
          {props.serviceResultLines.length > 0 ? (
            <ul className="space-y-2">
              {props.serviceResultLines.map((line, index) => (
                <li key={`${index}-${line}`} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <span className="mt-1.5 block h-1.5 w-1.5 shrink-0 rounded-full bg-primary-400" />
                  {line}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </div>

      {fileDownloads.length > 0 ? (
        <div className="modern-card overflow-hidden">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <FileText className="h-4 w-4 text-primary-500" />
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">产物下载</span>
          </div>
          <div className="p-4">
            <div className="grid gap-2 md:grid-cols-2">
              {fileDownloads.map((item) => (
                <div
                  key={`${item.title}-${item.url}`}
                  className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-3 transition-all hover:border-primary-200 hover:bg-white dark:border-slate-700 dark:bg-slate-900/50 dark:hover:border-primary-700"
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
                    className="shrink-0 rounded-lg bg-primary-50 px-3 py-1.5 text-xs font-medium text-primary-600 transition-colors hover:bg-primary-100 dark:bg-primary-500/10 dark:text-primary-400 dark:hover:bg-primary-500/20"
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

function ExternalResourceRecommendationCard(props: { item: TempDownloadLink }) {
  const actionLabel = recommendationActionLabel(props.item.resourceType);
  const typeLabel = recommendationTypeLabel(props.item.resourceType);
  const isVideo = props.item.resourceType === 'VIDEO';
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className={`relative ${isVideo ? 'aspect-video' : 'aspect-[16/10]'} bg-slate-100 dark:bg-slate-800`}>
        {props.item.thumbnailUrl ? (
          <img
            src={props.item.thumbnailUrl}
            alt={props.item.title}
            className="h-full w-full object-cover"
            loading="lazy"
            referrerPolicy="no-referrer"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-slate-100 to-primary-100 text-sm text-slate-500 dark:from-slate-800 dark:to-slate-900 dark:text-slate-400">
            {typeLabel}
          </div>
        )}
      </div>
      <div className="space-y-3 p-4">
        <div>
          <div className="text-base font-semibold text-slate-800 dark:text-slate-100">{props.item.title}</div>
          {props.item.knowledgePoint ? (
            <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">知识点：{props.item.knowledgePoint}</div>
          ) : null}
          {props.item.summary ? (
            <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{props.item.summary}</p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
          {props.item.sourceName ? (
            <span className="rounded-full bg-slate-100 px-2.5 py-1 dark:bg-slate-800">{props.item.sourceName}</span>
          ) : null}
          <span className="rounded-full bg-primary-50 px-2.5 py-1 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300">{typeLabel}</span>
        </div>
        <div className="flex items-center justify-between gap-3 border-t border-slate-100 pt-3 dark:border-slate-800">
          <span className="text-xs text-slate-400 dark:text-slate-500">{props.item.expiresHint || '点击后将在新窗口打开资源'}</span>
          <a
            href={props.item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 transition-colors hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            {actionLabel}
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}

function isExternalRecommendation(item: TempDownloadLink): boolean {
  return /^https?:\/\//i.test(item.url);
}

function recommendationActionLabel(resourceType?: string): string {
  switch (resourceType) {
    case 'VIDEO':
      return '打开视频';
    case 'CODE_CASE':
      return '查看案例';
    case 'PRACTICAL_CASE':
      return '开始实操';
    default:
      return '打开资源';
  }
}

function recommendationTypeLabel(resourceType?: string): string {
  switch (resourceType) {
    case 'VIDEO':
      return '外部视频';
    case 'CODE_CASE':
      return '代码案例';
    case 'PRACTICAL_CASE':
      return '实操案例';
    case 'READING':
      return '拓展阅读';
    default:
      return '讲解文档';
  }
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
            ? 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400'
            : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400'
        }`}>
          {props.source === 'BACKEND' ? '系统分析' : '实时更新'}
        </span>
      </div>
      <div className="space-y-5 p-5">
        <div className="grid gap-3 xl:grid-cols-4">
          <ProfileStatCard icon={<Target className="h-4 w-4" />} label="学习目标" value={props.profile.goal || EMPTY_VALUE} accent="primary" />
          <ProfileStatCard icon={<Brain className="h-4 w-4" />} label="知识基础" value={props.profile.knowledgeBase || EMPTY_VALUE} accent="primary" />
          <ProfileStatCard icon={<Activity className="h-4 w-4" />} label="置信分" value={`${props.profile.confidenceScore}/100`} accent="emerald" />
          <ProfileStatCard icon={<Sparkles className="h-4 w-4" />} label="认知偏好" value={props.profile.explanationPreference || props.profile.cognitiveStyle || EMPTY_VALUE} accent="amber" />
        </div>

        <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
          <section className="rounded-2xl border border-slate-100 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-900/40">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">7维画像可视化</h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">从当前画像自动计算 7 个核心学习维度</p>
              </div>
              <span className="rounded-full bg-primary-50 px-2.5 py-1 text-[11px] font-medium text-primary-600 dark:bg-primary-500/10 dark:text-primary-400">
                实时画像
              </span>
            </div>
            <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
              <RadarChart
                data={props.profile.dimensionScores.map((item) => ({
                  subject: item.subject,
                  score: item.score,
                  fullMark: item.fullMark,
                }))}
                height={320}
                className="min-h-[320px]"
              />
              <div className="space-y-2.5">
                {props.profile.dimensionScores.map((item, index) => (
                  <DimensionProgressRow key={item.key} item={item} delay={index * 0.06} />
                ))}
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-100 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-900/40">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">薄弱点排序</h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">按当前薄弱强度由高到低排序，优先展示最该补的内容</p>
              </div>
              <TriangleAlert className="h-4 w-4 text-amber-500" />
            </div>
            <div className="space-y-3">
              {props.profile.weakPointRanks.length > 0 ? (
                props.profile.weakPointRanks
                  .slice(0, props.showAllWeakPoints ? props.profile.weakPointRanks.length : 5)
                  .map((item, index) => (
                    <WeakPointRankCard key={`${item.topic}-${index}`} item={item} rank={index + 1} />
                  ))
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-400 dark:border-slate-700 dark:text-slate-500">
                  暂无可排序的薄弱点，继续对话、练习或评估后会自动补齐。
                </div>
              )}
              {props.profile.weakPointRanks.length > 5 || allWeakPoints.length > 3 ? (
                <button
                  type="button"
                  onClick={props.onToggleWeakPoints}
                  className="text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
                >
                  {props.showAllWeakPoints ? '收起薄弱点列表' : `展开全部 (${props.profile.weakPointRanks.length || allWeakPoints.length}项)`}
                </button>
              ) : null}
            </div>
          </section>
        </div>

        <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
          <section className="rounded-2xl border border-slate-100 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-900/40">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">画像摘要</h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">当前学习阶段、重点弱项与推荐方向</p>
              </div>
              <TrendingUp className="h-4 w-4 text-emerald-500" />
            </div>
            <div className="space-y-3">
              <div className="rounded-2xl bg-white/90 px-4 py-3 text-sm leading-7 text-slate-600 dark:bg-slate-950/40 dark:text-slate-300">
                {props.summary || props.profile.summaryText || EMPTY_VALUE}
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <ProfileCell label="课程方向" value={props.profile.major || EMPTY_VALUE} />
                <ProfileCell label="偏好学习方式" value={props.profile.preference?.join('、') || EMPTY_VALUE} />
                <ProfileCell label="认知风格" value={props.profile.cognitiveStyle || EMPTY_VALUE} />
                <ProfileCell label="当前薄弱点" value={weakPoints.length > 0 ? weakPoints.join('、') : EMPTY_VALUE} />
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-100 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-900/40">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">时间线演化</h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">展示最近几次画像快照的目标、基础和关键弱点变化</p>
              </div>
              <Clock3 className="h-4 w-4 text-slate-500" />
            </div>
            <ProfileTimeline timeline={props.profile.timeline} />
          </section>
        </div>

        <div className="flex items-center gap-4 border-t border-slate-100 pt-4 text-[11px] text-slate-400 dark:border-slate-800 dark:text-slate-500">
          <span>更新于 {props.updatedAt ? new Date(props.updatedAt).toLocaleString('zh-CN') : EMPTY_VALUE}</span>
        </div>
      </div>
    </div>
  );
}

function ProfileStatCard(props: {
  icon: ReactNode;
  label: string;
  value: string;
  accent: 'primary' | 'emerald' | 'amber';
}) {
  const accentMap: Record<typeof props.accent, string> = {
    primary: 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400',
    emerald: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400',
    amber: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400',
  };
  return (
    <div className="rounded-2xl border border-slate-100 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-900/40">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">{props.label}</div>
          <div className="mt-2 text-sm font-semibold leading-6 text-slate-700 dark:text-slate-200">{props.value || EMPTY_VALUE}</div>
        </div>
        <div className={`rounded-xl p-2 ${accentMap[props.accent]}`}>{props.icon}</div>
      </div>
    </div>
  );
}

function DimensionProgressRow(props: { item: ProfileDimensionScore; delay: number }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white/90 p-3 dark:border-slate-800 dark:bg-slate-950/40">
      <ScoreProgressBar
        label={`${props.item.subject} · ${props.item.hint}`}
        score={props.item.score}
        maxScore={props.item.fullMark}
        color="bg-primary-500"
        delay={props.delay}
      />
    </div>
  );
}

function WeakPointRankCard(props: { item: WeakPointRank; rank: number }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white/90 p-3 dark:border-slate-800 dark:bg-slate-950/40">
      <div className="mb-2 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-50 text-xs font-semibold text-amber-600 dark:bg-amber-500/10 dark:text-amber-400">
            {props.rank}
          </div>
          <div>
            <div className="text-sm font-medium text-slate-700 dark:text-slate-200">{props.item.topic}</div>
            <div className="text-xs text-slate-400 dark:text-slate-500">
              {props.item.lastError || '等待更多练习或评估错误样本'}
            </div>
          </div>
        </div>
        <div className="text-sm font-semibold text-amber-600 dark:text-amber-400">{props.item.severity}/100</div>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-amber-400 to-rose-500"
          style={{ width: `${Math.max(8, Math.min(100, props.item.severity))}%` }}
        />
      </div>
    </div>
  );
}

function ProfileTimeline(props: { timeline: ProfileTimelinePoint[] }) {
  if (props.timeline.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-400 dark:border-slate-700 dark:text-slate-500">
        暂无历史画像快照，继续学习后会自动累积演化记录。
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {props.timeline.map((item, index) => (
        <div key={`${item.version}-${item.updatedAt}-${index}`} className="relative rounded-2xl border border-slate-100 bg-white/90 p-4 dark:border-slate-800 dark:bg-slate-950/40">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                V{item.version}
              </span>
              <span className="text-xs text-slate-400 dark:text-slate-500">
                {item.updatedAt ? new Date(item.updatedAt).toLocaleString('zh-CN') : '时间未知'}
              </span>
            </div>
            <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">置信 {item.confidenceScore}/100</span>
          </div>
          <div className="grid gap-2 text-sm text-slate-600 dark:text-slate-300 md:grid-cols-3">
            <div><span className="text-slate-400 dark:text-slate-500">知识基础：</span>{item.knowledgeBase || EMPTY_VALUE}</div>
            <div><span className="text-slate-400 dark:text-slate-500">目标：</span>{item.goal || EMPTY_VALUE}</div>
            <div><span className="text-slate-400 dark:text-slate-500">首要薄弱点：</span>{item.leadWeakPoint || EMPTY_VALUE}</div>
          </div>
          <div className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{item.summary || '该版本暂无摘要'}</div>
        </div>
      ))}
    </div>
  );
}

export function ChatPanel({ messages }: { messages: ChatMessage[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);

  const isStreaming = messages.length > 0 && messages[messages.length - 1]?.role === 'assistant' && !messages[messages.length - 1]?.content;

  // Scroll to bottom on mount
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
  }, []);

  // Scroll to bottom when messages change (new message / streaming)
  useEffect(() => {
    const container = containerRef.current;
    if (!container || !autoFollow) return;
    requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
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
                <div className="rounded-2xl rounded-br-md bg-primary-600 px-4 py-2.5 text-[15px] leading-7 text-white shadow-sm">
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
          className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-600 shadow-lg transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
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
          : 'rounded-3xl border border-slate-200 bg-white shadow-sm focus-within:shadow-md focus-within:ring-2 focus-within:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:focus-within:ring-primary-500/10'
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
            className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg shadow-primary-500/25 transition-all hover:shadow-md hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none active:scale-95"
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
