import { useCallback, useEffect, useMemo, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  BookOpenCheck,
  CheckCircle2,
  Clock3,
  Filter,
  LoaderCircle,
  RotateCcw,
  Save,
  Search,
  Sparkles,
  Target,
  TriangleAlert,
  XCircle,
} from 'lucide-react';
import { getErrorMessage } from '../api/request';
import {
  mistakesApi,
  type MistakeListResponse,
  type MistakeRecordResponse,
  type MistakeReviewSessionResponse,
  type MistakeStatus,
  type MistakeUpdateRequest,
} from '../api/mistakes';
import type { LayoutOutletContext } from '../components/Layout';

const STATUS_OPTIONS: Array<{ value: MistakeStatus; label: string }> = [
  { value: 'active', label: '未掌握' },
  { value: 'due', label: '今日复习' },
  { value: 'mastered', label: '已掌握' },
  { value: 'all', label: '全部' },
];

const DIFFICULTY_OPTIONS = [
  { value: '', label: '全部难度' },
  { value: 'BASIC', label: '基础' },
  { value: 'INTERMEDIATE', label: '中等' },
  { value: 'ADVANCED', label: '进阶' },
  { value: 'MIXED', label: '综合' },
];

const MISTAKE_TYPE_OPTIONS = [
  { value: '', label: '未分类' },
  { value: 'conceptual', label: '概念理解' },
  { value: 'procedural', label: '步骤方法' },
  { value: 'careless', label: '粗心失误' },
];

const QUALITY_OPTIONS = [
  { value: 0, label: '完全不会' },
  { value: 1, label: '很吃力' },
  { value: 2, label: '仍不稳' },
  { value: 3, label: '基本会' },
  { value: 4, label: '较熟练' },
  { value: 5, label: '完全掌握' },
];

export default function MistakeBookPage() {
  const { isAuthenticated, openAuthModal } = useOutletContext<LayoutOutletContext>();
  const [status, setStatus] = useState<MistakeStatus>('active');
  const [difficulty, setDifficulty] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [knowledgeTag, setKnowledgeTag] = useState('');
  const [page, setPage] = useState(0);
  const [data, setData] = useState<MistakeListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [noteDrafts, setNoteDrafts] = useState<Record<string, string>>({});
  const [typeDrafts, setTypeDrafts] = useState<Record<string, string>>({});
  const [savingId, setSavingId] = useState('');
  const [reviewSession, setReviewSession] = useState<MistakeReviewSessionResponse | null>(null);
  const [reviewQualities, setReviewQualities] = useState<Record<string, number>>({});
  const [reviewBusy, setReviewBusy] = useState(false);
  const [reviewMessage, setReviewMessage] = useState('');

  const loadMistakes = useCallback(async () => {
    if (!isAuthenticated) {
      return;
    }
    setLoading(true);
    setError('');
    try {
      const nextData = await mistakesApi.list({
        status,
        knowledgeTag: knowledgeTag || undefined,
        difficulty: difficulty || undefined,
        page,
        size: 12,
      });
      setData(nextData);
      setNoteDrafts(Object.fromEntries(nextData.items.map((item) => [item.id, item.userNote || ''])));
      setTypeDrafts(Object.fromEntries(nextData.items.map((item) => [item.id, item.mistakeType || ''])));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }, [difficulty, isAuthenticated, knowledgeTag, page, status]);

  useEffect(() => {
    void loadMistakes();
  }, [loadMistakes]);

  const totalPages = useMemo(() => {
    if (!data || data.size <= 0) {
      return 1;
    }
    return Math.max(1, Math.ceil(data.total / data.size));
  }, [data]);

  const handleApplyFilters = () => {
    setPage(0);
    setKnowledgeTag(tagInput.trim());
  };

  const handleSave = async (item: MistakeRecordResponse) => {
    setSavingId(item.id);
    setError('');
    try {
      const payload: MistakeUpdateRequest = {
        userNote: noteDrafts[item.id] ?? '',
      };
      const selectedType = typeDrafts[item.id] as MistakeUpdateRequest['mistakeType'] | '';
      if (selectedType) {
        payload.mistakeType = selectedType;
      }
      await mistakesApi.update(item.id, payload);
      await loadMistakes();
    } catch (saveError) {
      setError(getErrorMessage(saveError));
    } finally {
      setSavingId('');
    }
  };

  const handleToggleMastered = async (item: MistakeRecordResponse) => {
    setSavingId(item.id);
    setError('');
    try {
      await mistakesApi.update(item.id, { mastered: !item.mastered });
      await loadMistakes();
    } catch (saveError) {
      setError(getErrorMessage(saveError));
    } finally {
      setSavingId('');
    }
  };

  const handleStartReview = async () => {
    setReviewBusy(true);
    setReviewMessage('');
    try {
      const session = await mistakesApi.createReviewSession({ limit: 10 });
      setReviewSession(session);
      setReviewQualities({});
    } catch (reviewError) {
      setReviewMessage(getErrorMessage(reviewError));
    } finally {
      setReviewBusy(false);
    }
  };

  const handleSubmitReview = async () => {
    if (!reviewSession) {
      return;
    }
    const missing = reviewSession.items.some((item) => reviewQualities[item.id] === undefined);
    if (missing) {
      setReviewMessage('请先为每道错题选择掌握评分');
      return;
    }
    setReviewBusy(true);
    setReviewMessage('');
    try {
      const nextSession = await mistakesApi.submitReviewSession(reviewSession.sessionId, {
        items: reviewSession.items.map((item) => ({
          mistakeRecordId: item.id,
          quality: reviewQualities[item.id],
          isCorrect: reviewQualities[item.id] >= 3,
          answer: { quality: reviewQualities[item.id] },
        })),
      });
      setReviewSession(nextSession);
      setReviewMessage('复习结果已保存，下次复习时间已更新');
      await loadMistakes();
    } catch (reviewError) {
      setReviewMessage(getErrorMessage(reviewError));
    } finally {
      setReviewBusy(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-[980px] px-1 pb-10 md:px-0">
        <div className="modern-card p-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300">
            <BookOpenCheck className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-800 dark:text-white">错题本</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">登录后可以查看自动沉淀的错题和复习计划。</p>
          <button
            type="button"
            onClick={() => openAuthModal('login', '登录后查看错题本')}
            className="mt-6 rounded-xl bg-primary-600 px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary-500/20 transition-colors hover:bg-primary-700"
          >
            登录查看
          </button>
        </div>
      </div>
    );
  }

  const stats = data?.stats ?? { dueCount: 0, activeCount: 0, masteredCount: 0 };

  return (
    <div className="mx-auto max-w-[1180px] space-y-5 px-1 pb-10 md:px-0">
      <div className="modern-card overflow-hidden">
        <div className="flex flex-col gap-5 p-5 md:flex-row md:items-center md:justify-between md:p-6">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-primary-100 bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700 dark:border-primary-800 dark:bg-primary-500/10 dark:text-primary-300">
              <BookOpenCheck className="h-3.5 w-3.5" />
              自动沉淀
            </div>
            <h1 className="mt-3 text-2xl font-semibold tracking-tight text-slate-800 dark:text-white md:text-[32px]">错题本</h1>
            <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">判错后的练习会自动进入这里，按下次复习时间排队。</p>
          </div>
          <button
            type="button"
            onClick={handleStartReview}
            disabled={reviewBusy}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary-500/20 transition-all hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {reviewBusy ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <RotateCcw className="h-4 w-4" />}
            开始今日复习
          </button>
        </div>
        <div className="grid border-t border-slate-100 dark:border-slate-800 md:grid-cols-3">
          <StatTile icon={Clock3} label="今日待复习" value={stats.dueCount} />
          <StatTile icon={Target} label="未掌握错题" value={stats.activeCount} />
          <StatTile icon={CheckCircle2} label="已掌握" value={stats.masteredCount} />
        </div>
      </div>

      <div className="modern-card p-4 md:p-5">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
          <Filter className="h-4 w-4 text-primary-500" />
          筛选错题
        </div>
        <div className="grid gap-3 lg:grid-cols-[1fr_180px_150px_auto]">
          <label className="flex items-center rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 transition-all focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900">
            <Search className="mr-2 h-4 w-4 text-slate-400" />
            <input
              value={tagInput}
              onChange={(event) => setTagInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  handleApplyFilters();
                }
              }}
              placeholder="按知识点筛选"
              className="w-full bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400 dark:text-slate-200"
            />
          </label>
          <select
            value={status}
            onChange={(event) => {
              setPage(0);
              setStatus(event.target.value as MistakeStatus);
            }}
            className="rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
          >
            {STATUS_OPTIONS.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>
          <select
            value={difficulty}
            onChange={(event) => {
              setPage(0);
              setDifficulty(event.target.value);
            }}
            className="rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
          >
            {DIFFICULTY_OPTIONS.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={handleApplyFilters}
            className="rounded-xl border border-primary-200 bg-primary-50 px-4 py-2.5 text-sm font-medium text-primary-700 transition-colors hover:bg-primary-100 dark:border-primary-800 dark:bg-primary-500/10 dark:text-primary-300"
          >
            应用筛选
          </button>
        </div>
      </div>

      {error ? <Notice tone="error" message={error} /> : null}
      {reviewMessage ? <Notice tone={reviewSession?.status === 'DONE' ? 'success' : 'warning'} message={reviewMessage} /> : null}

      {reviewSession ? (
        <ReviewPanel
          session={reviewSession}
          qualities={reviewQualities}
          busy={reviewBusy}
          onQualityChange={(id, quality) => setReviewQualities((prev) => ({ ...prev, [id]: quality }))}
          onSubmit={handleSubmitReview}
          onClose={() => {
            setReviewSession(null);
            setReviewQualities({});
          }}
        />
      ) : null}

      <div className="space-y-3">
        {loading ? (
          <div className="modern-card flex items-center justify-center gap-2 p-8 text-sm text-slate-500 dark:text-slate-400">
            <LoaderCircle className="h-4 w-4 animate-spin text-primary-500" />
            正在加载错题
          </div>
        ) : data && data.items.length > 0 ? (
          data.items.map((item) => (
            <MistakeCard
              key={item.id}
              item={item}
              noteDraft={noteDrafts[item.id] ?? ''}
              typeDraft={typeDrafts[item.id] ?? ''}
              saving={savingId === item.id}
              onNoteChange={(value) => setNoteDrafts((prev) => ({ ...prev, [item.id]: value }))}
              onTypeChange={(value) => setTypeDrafts((prev) => ({ ...prev, [item.id]: value }))}
              onSave={() => void handleSave(item)}
              onToggleMastered={() => void handleToggleMastered(item)}
            />
          ))
        ) : (
          <div className="modern-card p-8 text-center">
            <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 dark:bg-slate-800">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">暂无匹配错题</div>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">练习判错后会自动进入错题本。</p>
          </div>
        )}
      </div>

      {data && data.total > data.size ? (
        <div className="flex items-center justify-center gap-2 sm:justify-end">
          <button
            type="button"
            disabled={page <= 0}
            onClick={() => setPage((prev) => Math.max(0, prev - 1))}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
          >
            上一页
          </button>
          <span className="text-xs text-slate-500 dark:text-slate-400">{page + 1} / {totalPages}</span>
          <button
            type="button"
            disabled={page + 1 >= totalPages}
            onClick={() => setPage((prev) => Math.min(totalPages - 1, prev + 1))}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
          >
            下一页
          </button>
        </div>
      ) : null}
    </div>
  );
}

function MistakeCard(props: {
  item: MistakeRecordResponse;
  noteDraft: string;
  typeDraft: string;
  saving: boolean;
  onNoteChange: (value: string) => void;
  onTypeChange: (value: string) => void;
  onSave: () => void;
  onToggleMastered: () => void;
}) {
  const { item } = props;
  const feedback = asText(item.judgeResult.feedback) || asText(item.judgeResult.reason);

  return (
    <article className="modern-card overflow-hidden">
      <div className="border-b border-slate-100 px-4 py-3 dark:border-slate-800 md:px-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${
                item.mastered
                  ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
                  : isDue(item.nextReviewAt)
                    ? 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
                    : 'bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-300'
              }`}>
                {item.mastered ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Clock3 className="h-3.5 w-3.5" />}
                {item.mastered ? '已掌握' : isDue(item.nextReviewAt) ? '今日复习' : '待复习'}
              </span>
              <span className="text-xs text-slate-400 dark:text-slate-500">错 {item.wrongCount} 次 · 复习 {item.reviewCount} 次 · {difficultyLabel(item.difficultyLevel)}</span>
            </div>
            <h2 className="mt-3 text-base font-semibold leading-7 text-slate-800 dark:text-slate-100">{item.stem}</h2>
          </div>
          <button
            type="button"
            onClick={props.onToggleMastered}
            disabled={props.saving}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {item.mastered ? <RotateCcw className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
            {item.mastered ? '移回复习' : '标记掌握'}
          </button>
        </div>
      </div>
      <div className="grid gap-4 p-4 md:grid-cols-[1.1fr_0.9fr] md:p-5">
        <div className="space-y-4">
          {item.options.length > 0 ? (
            <div className="space-y-2">
              {item.options.map((option, index) => (
                <div key={`${item.id}-${index}`} className="rounded-xl border border-slate-200 bg-slate-50/60 px-3 py-2 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-300">
                  {String.fromCharCode(65 + index)}. {option}
                </div>
              ))}
            </div>
          ) : null}

          <div className="grid gap-3 md:grid-cols-2">
            <AnswerBlock label="你的答案" value={item.learnerAnswer || '未作答'} tone="danger" />
            <AnswerBlock label="参考答案" value={formatAnswer(item.standardAnswer)} tone="success" />
          </div>

          {feedback ? (
            <div className="rounded-xl border border-primary-100 bg-primary-50/60 px-3.5 py-3 text-sm leading-6 text-primary-800 dark:border-primary-900 dark:bg-primary-500/10 dark:text-primary-200">
              {feedback}
            </div>
          ) : null}
        </div>

        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {item.knowledgeTags.length > 0 ? item.knowledgeTags.map((tag) => (
              <span key={tag} className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
                {tag}
              </span>
            )) : (
              <span className="rounded-full border border-slate-200 px-2.5 py-1 text-xs text-slate-400 dark:border-slate-700">未标注知识点</span>
            )}
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <select
              value={props.typeDraft}
              onChange={(event) => props.onTypeChange(event.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition-all focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
            >
              {MISTAKE_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 px-3 py-2 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-400">
              下次：{formatDate(item.nextReviewAt)}
            </div>
          </div>
          <textarea
            value={props.noteDraft}
            onChange={(event) => props.onNoteChange(event.target.value)}
            rows={4}
            placeholder="记录这道题为什么错、下次怎么检查"
            className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-sm leading-6 outline-none transition-all focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
          />
          <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span className="text-xs text-slate-400 dark:text-slate-500">错因：{mistakeTypeLabel(item.mistakeType)}</span>
            <button
              type="button"
              onClick={props.onSave}
              disabled={props.saving}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary-600 px-3.5 py-2 text-xs font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {props.saving ? <LoaderCircle className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              保存
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}

function ReviewPanel(props: {
  session: MistakeReviewSessionResponse;
  qualities: Record<string, number>;
  busy: boolean;
  onQualityChange: (id: string, quality: number) => void;
  onSubmit: () => void;
  onClose: () => void;
}) {
  const done = props.session.status === 'DONE';
  return (
    <section className="modern-card overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-100 px-4 py-3 dark:border-slate-800 md:flex-row md:items-center md:justify-between md:px-5">
        <div>
          <div className="text-sm font-semibold text-slate-800 dark:text-slate-100">今日复习</div>
          <div className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            {done ? `本次得分 ${props.session.score ?? 0}` : `共 ${props.session.items.length} 道错题，按掌握程度评分`}
          </div>
        </div>
        <button
          type="button"
          onClick={props.onClose}
          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <XCircle className="h-3.5 w-3.5" />
          关闭
        </button>
      </div>
      <div className="space-y-4 p-4 md:p-5">
        {props.session.items.map((item, index) => (
          <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 dark:border-slate-700 dark:bg-slate-900/50">
            <div className="text-sm font-semibold leading-6 text-slate-800 dark:text-slate-100">{index + 1}. {item.stem}</div>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              <AnswerBlock label="你的错答" value={item.learnerAnswer || '未作答'} tone="danger" />
              <AnswerBlock label="参考答案" value={formatAnswer(item.standardAnswer)} tone="success" />
            </div>
            {!done ? (
              <div className="mt-4 flex flex-wrap gap-2">
                {QUALITY_OPTIONS.map((quality) => {
                  const active = props.qualities[item.id] === quality.value;
                  return (
                    <button
                      key={quality.value}
                      type="button"
                      onClick={() => props.onQualityChange(item.id, quality.value)}
                      className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                        active
                          ? 'border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-500/10 dark:text-primary-300'
                          : 'border-slate-200 bg-white text-slate-500 hover:border-primary-200 hover:text-primary-600 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-400'
                      }`}
                    >
                      {quality.value} · {quality.label}
                    </button>
                  );
                })}
              </div>
            ) : null}
          </div>
        ))}
        {!done ? (
          <button
            type="button"
            onClick={props.onSubmit}
            disabled={props.busy}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {props.busy ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
            提交复习结果
          </button>
        ) : null}
      </div>
    </section>
  );
}

function StatTile(props: { icon: typeof Clock3; label: string; value: number }) {
  const Icon = props.icon;
  return (
    <div className="flex items-center gap-3 border-slate-100 px-5 py-4 dark:border-slate-800 md:border-r md:last:border-r-0">
      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <div className="text-xl font-semibold text-slate-800 dark:text-white">{props.value}</div>
        <div className="text-xs text-slate-500 dark:text-slate-400">{props.label}</div>
      </div>
    </div>
  );
}

function AnswerBlock(props: { label: string; value: string; tone: 'danger' | 'success' }) {
  const toneClass = props.tone === 'danger'
    ? 'border-rose-100 bg-rose-50/60 text-rose-800 dark:border-rose-900 dark:bg-rose-500/10 dark:text-rose-200'
    : 'border-emerald-100 bg-emerald-50/60 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-500/10 dark:text-emerald-200';
  return (
    <div className={`rounded-xl border px-3.5 py-3 ${toneClass}`}>
      <div className="mb-1 text-xs font-semibold opacity-75">{props.label}</div>
      <div className="whitespace-pre-wrap text-sm leading-6">{props.value}</div>
    </div>
  );
}

function Notice(props: { tone: 'error' | 'warning' | 'success'; message: string }) {
  const toneClass = props.tone === 'error'
    ? 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-500/10 dark:text-rose-200'
    : props.tone === 'success'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-500/10 dark:text-emerald-200'
      : 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-500/10 dark:text-amber-200';
  return (
    <div className={`flex items-start gap-2 rounded-xl border px-4 py-3 text-sm ${toneClass}`}>
      <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{props.message}</span>
    </div>
  );
}

function formatAnswer(value: Record<string, unknown>): string {
  const answer = value.answer ?? value.correctAnswer ?? value;
  if (typeof answer === 'string') {
    return answer;
  }
  return JSON.stringify(answer, null, 2);
}

function asText(value: unknown): string {
  return typeof value === 'string' ? value : '';
}

function difficultyLabel(value: string): string {
  return DIFFICULTY_OPTIONS.find((item) => item.value === value)?.label ?? value;
}

function mistakeTypeLabel(value?: string): string {
  return MISTAKE_TYPE_OPTIONS.find((item) => item.value === (value || ''))?.label ?? '未分类';
}

function formatDate(value?: string): string {
  if (!value) {
    return '--';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '--';
  }
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function isDue(value?: string): boolean {
  if (!value) {
    return false;
  }
  return new Date(value).getTime() <= Date.now();
}
