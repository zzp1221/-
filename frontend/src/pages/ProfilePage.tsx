import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  BookOpen,
  Brain,
  CalendarClock,
  Clock3,
  Gauge,
  LineChart,
  LoaderCircle,
  Lock,
  Sparkles,
  Target,
  TriangleAlert,
  UserRoundSearch,
} from 'lucide-react';
import RadarChart from '../components/RadarChart';
import { getErrorMessage } from '../api/request';
import {
  smartEngineApi,
  type ProfileBehaviorTrendPoint,
  type UserProfileAnalyticsResponse,
} from '../api/smartEngine';
import type { LayoutOutletContext } from '../components/Layout';
import {
  EMPTY_VALUE,
  type ProfileLearningHabits,
  type ProfileSnapshot,
  type WeakPointRank,
} from './LearningStudioDemoPage.types';
import { mapProfileResponse } from './LearningStudioDemoPage.utils';

const navItems = [
  { id: 'overview', label: '概览' },
  { id: 'goals', label: '学习目标' },
  { id: 'knowledge', label: '知识基础' },
  { id: 'behavior', label: '学习行为' },
  { id: 'preference', label: '讲解偏好' },
  { id: 'analysis', label: '系统分析' },
];

export default function ProfilePage() {
  const { isAuthenticated, currentUser, openAuthModal } = useOutletContext<LayoutOutletContext>();
  const [profile, setProfile] = useState<ProfileSnapshot | null>(null);
  const [updatedAt, setUpdatedAt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analytics, setAnalytics] = useState<UserProfileAnalyticsResponse | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState('');
  const [showAllWeakPoints, setShowAllWeakPoints] = useState(false);

  const loadProfile = useCallback(async () => {
    if (!isAuthenticated || !currentUser) {
      setProfile(null);
      setUpdatedAt('');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await smartEngineApi.getCurrentProfile(String(currentUser.id));
      const hasProfilePayload = Boolean(response.profile && Object.keys(response.profile).length > 0);
      setProfile(hasProfilePayload ? mapProfileResponse(response) : null);
      setUpdatedAt(response.updatedAt ?? '');
    } catch (loadError) {
      setProfile(null);
      setUpdatedAt('');
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }, [currentUser, isAuthenticated]);

  const loadAnalytics = useCallback(async () => {
    if (!isAuthenticated || !currentUser) {
      setAnalytics(null);
      setAnalyticsError('');
      return;
    }
    setAnalyticsLoading(true);
    setAnalyticsError('');
    try {
      const response = await smartEngineApi.getProfileAnalytics(String(currentUser.id), 30);
      setAnalytics(response);
    } catch (loadError) {
      setAnalytics(null);
      setAnalyticsError(getErrorMessage(loadError));
    } finally {
      setAnalyticsLoading(false);
    }
  }, [currentUser, isAuthenticated]);

  useEffect(() => {
    void loadProfile();
    void loadAnalytics();
  }, [loadAnalytics, loadProfile]);

  const displayName = currentUser?.fullName || currentUser?.loginId || currentUser?.username || '同学';

  const metrics = useMemo(() => {
    if (!profile) {
      return null;
    }
    const masteryAverage = profile.skillMastery.length > 0
      ? Math.round(profile.skillMastery.reduce((sum, item) => sum + item.score, 0) / profile.skillMastery.length)
      : null;
    const weakPointCount = profile.weakPointRanks.length || profile.weakPoints.length;
    const behaviorSignals = countBehaviorSignals(profile.learningHabits);
    const goalCount = [
      profile.currentGoal.shortTerm || profile.goal,
      profile.currentGoal.midTerm,
      profile.currentGoal.context,
    ].filter(Boolean).length;
    const preferenceCount = profile.preference.length + (profile.explanationPreference ? 1 : 0);
    return {
      masteryAverage,
      weakPointCount,
      behaviorSignals,
      goalCount,
      preferenceCount,
    };
  }, [profile]);

  if (!isAuthenticated) {
    return (
      <ProfileShell>
        <ProfileAccessState
          icon={<Lock className="h-6 w-6" />}
          title="登录后查看个人画像"
          description="个人画像只读取你的真实学习记录和画像快照。"
          actionLabel="去登录"
          onAction={() => openAuthModal('login', '登录后查看个人画像')}
        />
      </ProfileShell>
    );
  }

  if (loading && !profile) {
    return (
      <ProfileShell>
        <div className="flex min-h-[420px] items-center justify-center rounded-2xl border border-blue-100 bg-white/80 text-sm text-slate-500 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/70 dark:text-slate-400">
          <LoaderCircle className="mr-2 h-4 w-4 animate-spin text-primary-500" />
          正在读取真实画像数据
        </div>
      </ProfileShell>
    );
  }

  if (error) {
    return (
      <ProfileShell>
        <ProfileAccessState
          icon={<TriangleAlert className="h-6 w-6" />}
          title="画像读取失败"
          description={error}
          actionLabel="重新加载"
          onAction={() => void loadProfile()}
        />
      </ProfileShell>
    );
  }

  if (!profile || !metrics) {
    return (
      <ProfileShell>
        <ProfileAccessState
          icon={<UserRoundSearch className="h-6 w-6" />}
          title="暂无个人画像"
          description="完成对话、练习或学习服务后，系统会基于真实记录生成画像。"
          actionLabel="刷新画像"
          onAction={() => void loadProfile()}
        />
      </ProfileShell>
    );
  }

  const visibleWeakPoints = showAllWeakPoints ? profile.weakPointRanks : profile.weakPointRanks.slice(0, 5);
  const recommendations = profile.inferredRecommendations.slice(0, 3);

  return (
    <ProfileShell>
      <div className="grid gap-5 xl:grid-cols-[176px_minmax(0,1fr)]">
        <ProfileSubnav updatedAt={updatedAt} />

        <div className="min-w-0 space-y-5">
          <header className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-slate-900 dark:text-white md:text-3xl">
                你好，{displayName}
              </h1>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                这是基于真实学习记录生成的个人画像，用来辅助你了解当前状态。
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                void loadProfile();
                void loadAnalytics();
              }}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-blue-100 bg-white px-4 text-sm font-medium text-primary-600 shadow-sm shadow-blue-100/60 transition-colors hover:bg-primary-50 dark:border-slate-700 dark:bg-slate-900 dark:text-primary-300 dark:hover:bg-slate-800"
            >
              <CalendarClock className="h-4 w-4" />
              刷新画像
            </button>
          </header>

          <section id="overview" className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
            <MetricCard
              icon={<Target className="h-5 w-5" />}
              label="学习阶段"
              value={profile.knowledgeBase || EMPTY_VALUE}
              description={profile.goal || profile.currentGoal.shortTerm || '暂无明确学习目标'}
              accent="blue"
            />
            <MetricCard
              icon={<Clock3 className="h-5 w-5" />}
              label="学习节奏"
              value={profile.learningPace || profile.learningHabits.studyFrequency || EMPTY_VALUE}
              description={profile.learningHabits.studyFrequency || analyticsTrendSummary(analytics) || '暂无节奏信号'}
              accent="cyan"
              mutedHint={analyticsLoading ? '正在读取近 30 天行为趋势' : analyticsError ? '行为趋势读取失败，画像主体不受影响' : undefined}
            />
            <MetricCard
              icon={<Gauge className="h-5 w-5" />}
              label="知识掌握度"
              value={metrics.masteryAverage === null ? EMPTY_VALUE : `${metrics.masteryAverage}%`}
              description={profile.skillMastery.length > 0 ? `来自 ${profile.skillMastery.length} 个知识点掌握度` : '暂无真实掌握度数据'}
              accent="indigo"
              progress={metrics.masteryAverage}
            />
            <MetricCard
              icon={<TriangleAlert className="h-5 w-5" />}
              label="薄弱点数量"
              value={`${metrics.weakPointCount}个`}
              description={metrics.weakPointCount > 0 ? '待重点提升知识点' : '暂无明确薄弱点'}
              accent="orange"
            />
          </section>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
            <div className="space-y-5">
              <section id="goals" className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
                <SectionTitle title="学习维度总览" subtitle="所有数量均来自当前画像字段" />
                <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <DimensionCard icon={<Target className="h-5 w-5" />} title="学习目标" value={`${metrics.goalCount}项`} detail={profile.currentGoal.shortTerm || profile.goal || '暂无短期目标'} href="#goals-detail" />
                  <DimensionCard icon={<Brain className="h-5 w-5" />} title="知识基础" value={`${profile.skillMastery.length}项维度`} detail={profile.knowledgeBase || '待分析'} href="#knowledge" />
                  <DimensionCard
                    icon={<LineChart className="h-5 w-5" />}
                    title="学习行为"
                    value={analyticsLoading ? '读取中' : analytics ? `${analytics.systemAnalysis.coverage.activeDays}天记录` : `${metrics.behaviorSignals}项信号`}
                    detail={analytics ? `近 ${analytics.days} 天真实行为聚合` : metrics.behaviorSignals > 0 ? '来自 learningHabits' : '暂无真实行为记录'}
                    href="#behavior"
                  />
                  <DimensionCard icon={<BookOpen className="h-5 w-5" />} title="讲解偏好" value={`${metrics.preferenceCount}项偏好`} detail={profile.explanationPreference || profile.preference.join('、') || '暂无偏好'} href="#preference" />
                </div>
              </section>

              <section id="knowledge" className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
                <SectionTitle title="画像维度可视化" subtitle="分数由前端根据真实画像字段推断，仅供参考" />
                <div className="mt-4 grid gap-5 lg:grid-cols-[minmax(0,0.95fr)_minmax(280px,0.75fr)]">
                  <RadarChart
                    data={profile.dimensionScores.map((item) => ({
                      subject: item.subject,
                      score: item.score,
                      fullMark: item.fullMark,
                      description: item.description,
                    }))}
                    height={320}
                    className="min-h-[320px]"
                  />
                  <div className="space-y-3">
                    {profile.dimensionScores.map((item) => (
                      <ScoreLine key={item.key} label={item.subject} detail={item.hint} score={item.score} />
                    ))}
                  </div>
                </div>
              </section>

              <section className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
                <SectionTitle title="学习建议" subtitle="来自 inferredRecommendations" />
                {recommendations.length > 0 ? (
                  <div className="mt-4 grid gap-3 md:grid-cols-3">
                    {recommendations.map((item, index) => (
                      <RecommendationCard key={`${item}-${index}`} index={index + 1} text={item} />
                    ))}
                  </div>
                ) : (
                  <EmptyInline text="当前画像暂无学习建议。" />
                )}
              </section>

              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <InfoCard title="偏好学习方式" value={profile.preference.join('、') || EMPTY_VALUE} detail="来自 preferredResourceTypes" />
                <InfoCard title="认知风格" value={profile.cognitiveStyle || EMPTY_VALUE} detail="来自 cognitiveStyle" />
                <InfoCard title="当前薄弱点" value={`${metrics.weakPointCount}个知识点`} detail="来自 weakPointDetails/weakPoints" />
                <InfoCard
                  title="擅长领域"
                  value={analytics?.systemAnalysis.strongestSkill || EMPTY_VALUE}
                  detail={analyticsLoading
                    ? '正在读取系统分析'
                    : analyticsError
                      ? '分析接口读取失败'
                      : analytics?.systemAnalysis.strongestSkillScore
                        ? `来自 analytics，掌握度 ${analytics.systemAnalysis.strongestSkillScore}%`
                        : '真实证据不足，暂不判断'}
                  muted={!analytics?.systemAnalysis.strongestSkill}
                />
              </section>

              <section id="preference" className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
                <SectionTitle title="讲解偏好详情" subtitle="不展示未接入的偏好百分比" />
                <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {profile.preference.length > 0 ? profile.preference.map((item) => (
                    <PreferenceCard key={item} title={item} detail="已识别资源偏好" />
                  )) : (
                    <EmptyInline text="暂无资源类型偏好。" />
                  )}
                  {profile.explanationPreference ? (
                    <PreferenceCard title="讲解方式" detail={profile.explanationPreference} />
                  ) : null}
                </div>
              </section>

              <section className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(300px,0.8fr)]">
                <BehaviorTrendPanel
                  analytics={analytics}
                  loading={analyticsLoading}
                  error={analyticsError}
                  onRetry={() => void loadAnalytics()}
                />
                <SystemAnalysisPanel
                  analytics={analytics}
                  loading={analyticsLoading}
                  error={analyticsError}
                  onRetry={() => void loadAnalytics()}
                />
              </section>
            </div>

            <aside className="space-y-5">
              <section className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
                <SectionTitle title="薄弱点排序" subtitle="优先展示最需要补强的内容" />
                <div className="mt-4 space-y-3">
                  {visibleWeakPoints.length > 0 ? visibleWeakPoints.map((item, index) => (
                    <WeakPointCard key={`${item.topic}-${index}`} item={item} rank={index + 1} />
                  )) : (
                    <EmptyInline text="暂无薄弱点排序。" />
                  )}
                  {profile.weakPointRanks.length > 5 ? (
                    <button
                      type="button"
                      onClick={() => setShowAllWeakPoints((prev) => !prev)}
                      className="w-full rounded-xl border border-blue-100 px-3 py-2 text-sm font-medium text-primary-600 transition-colors hover:bg-primary-50 dark:border-slate-700 dark:text-primary-300 dark:hover:bg-slate-800"
                    >
                      {showAllWeakPoints ? '收起薄弱点' : `查看全部薄弱点 (${profile.weakPointRanks.length})`}
                    </button>
                  ) : null}
                </div>
              </section>

              <section id="goals-detail" className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
                <SectionTitle title="目标与节奏" subtitle="来自 currentGoal 与 learningHabits" />
                <div className="mt-4 space-y-3 text-sm">
                  <FactRow label="短期目标" value={profile.currentGoal.shortTerm || profile.goal || EMPTY_VALUE} />
                  <FactRow label="中期目标" value={profile.currentGoal.midTerm || EMPTY_VALUE} />
                  <FactRow label="学习频率" value={profile.learningHabits.studyFrequency || EMPTY_VALUE} />
                  <FactRow label="平均时长" value={profile.learningHabits.avgSessionDuration > 0 ? `${profile.learningHabits.avgSessionDuration} 分钟` : EMPTY_VALUE} />
                  <FactRow label="画像历史" value={`${profile.history.length} 次快照`} />
                </div>
              </section>
            </aside>
          </div>

          <footer className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 pb-2 text-xs text-slate-400 dark:text-slate-500">
            <span>数据基于你的学习行为分析，仅供参考</span>
            <span>更新时间：{updatedAt ? new Date(updatedAt).toLocaleString('zh-CN') : EMPTY_VALUE}</span>
            <span>画像可靠度：{profile.confidenceScore}%</span>
          </footer>
        </div>
      </div>
    </ProfileShell>
  );
}

function ProfileShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto max-w-[1440px] px-1 pb-10">
      {children}
    </div>
  );
}

function ProfileSubnav({ updatedAt }: { updatedAt: string }) {
  return (
    <aside className="hidden xl:block">
      <div className="sticky top-24 rounded-2xl border border-blue-100/80 bg-white/85 p-3 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
        <div className="mb-3 flex items-center gap-2 px-2 py-2 text-base font-semibold text-slate-900 dark:text-white">
          <UserRoundSearch className="h-5 w-5 text-primary-500" />
          学习画像
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className="flex items-center rounded-xl px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-primary-50 hover:text-primary-700 dark:text-slate-400 dark:hover:bg-primary-500/10 dark:hover:text-primary-300"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="mt-6 rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-500 dark:bg-slate-800/70 dark:text-slate-400">
          <div className="mb-1 flex items-center gap-1.5">
            <Clock3 className="h-3.5 w-3.5" />
            更新时间
          </div>
          {updatedAt ? new Date(updatedAt).toLocaleString('zh-CN') : EMPTY_VALUE}
        </div>
      </div>
    </aside>
  );
}

function MetricCard(props: {
  icon: ReactNode;
  label: string;
  value: string;
  description: string;
  accent: 'blue' | 'cyan' | 'indigo' | 'orange';
  progress?: number | null;
  mutedHint?: string;
}) {
  const accentMap: Record<typeof props.accent, string> = {
    blue: 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300',
    cyan: 'bg-cyan-50 text-cyan-600 dark:bg-cyan-500/10 dark:text-cyan-300',
    indigo: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-300',
    orange: 'bg-orange-50 text-orange-600 dark:bg-orange-500/10 dark:text-orange-300',
  };
  return (
    <article className="min-h-[156px] rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-medium text-slate-500 dark:text-slate-400">{props.label}</div>
          <div className="mt-4 text-xl font-semibold text-slate-900 dark:text-white">{props.value}</div>
          <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{props.description}</p>
        </div>
        <div className={`rounded-xl p-2 ${accentMap[props.accent]}`}>{props.icon}</div>
      </div>
      {typeof props.progress === 'number' ? (
        <div className="mt-4 flex items-center gap-3">
          <div
            className="grid h-14 w-14 place-items-center rounded-full"
            style={{ background: `conic-gradient(#2563eb ${props.progress * 3.6}deg, #e2e8f0 0deg)` }}
          >
            <div className="grid h-10 w-10 place-items-center rounded-full bg-white text-xs font-semibold text-slate-800 dark:bg-slate-900 dark:text-slate-100">
              {props.progress}%
            </div>
          </div>
          <span className="text-xs text-slate-400 dark:text-slate-500">真实知识点均值</span>
        </div>
      ) : null}
      {props.mutedHint ? (
        <div className="mt-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-400 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-500">
          {props.mutedHint}
        </div>
      ) : null}
    </article>
  );
}

function SectionTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div>
      <h2 className="text-base font-semibold text-slate-900 dark:text-white">{title}</h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
    </div>
  );
}

function DimensionCard(props: {
  icon: ReactNode;
  title: string;
  value: string;
  detail: string;
  href?: string;
}) {
  return (
    <article className="rounded-2xl border border-blue-100 bg-white px-4 py-4 shadow-sm shadow-blue-100/50 dark:border-slate-800 dark:bg-slate-950/40">
      <div className="mb-3 inline-flex rounded-xl bg-primary-50 p-2 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300">
        {props.icon}
      </div>
      <div className="text-sm font-medium text-slate-500 dark:text-slate-400">{props.title}</div>
      <div className="mt-2 text-lg font-semibold text-slate-900 dark:text-white">{props.value}</div>
      <div className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">{props.detail}</div>
      {props.href ? (
        <a href={props.href} className="mt-3 inline-flex text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-300">
          查看详情
        </a>
      ) : null}
    </article>
  );
}

function ScoreLine({ label, detail, score }: { label: string; detail: string; score: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-3 text-sm">
        <span className="font-medium text-slate-700 dark:text-slate-300">{label}</span>
        <span className="text-slate-500 dark:text-slate-400">{score}/100</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div className="h-full rounded-full bg-primary-500" style={{ width: `${Math.max(0, Math.min(100, score))}%` }} />
      </div>
      <div className="mt-1 line-clamp-1 text-xs text-slate-400 dark:text-slate-500">{detail}</div>
    </div>
  );
}

function RecommendationCard({ index, text }: { index: number; text: string }) {
  return (
    <article className="rounded-2xl border border-blue-100 bg-primary-50/50 px-4 py-4 dark:border-primary-900/60 dark:bg-primary-500/10">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-primary-700 dark:text-primary-200">
        <Sparkles className="h-4 w-4" />
        建议 {index}
      </div>
      <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{text}</p>
    </article>
  );
}

function InfoCard({ title, value, detail, muted = false }: { title: string; value: string; detail: string; muted?: boolean }) {
  return (
    <article className={`rounded-2xl border px-4 py-4 shadow-sm ${muted ? 'border-slate-200 bg-slate-50 text-slate-400 shadow-none dark:border-slate-800 dark:bg-slate-800/50 dark:text-slate-500' : 'border-blue-100 bg-white/85 shadow-blue-100/50 dark:border-slate-800 dark:bg-slate-900/80'}`}>
      <div className="text-sm text-slate-500 dark:text-slate-400">{title}</div>
      <div className="mt-3 text-base font-semibold text-slate-900 dark:text-white">{value}</div>
      <div className="mt-2 text-xs text-slate-400 dark:text-slate-500">{detail}</div>
    </article>
  );
}

function PreferenceCard({ title, detail }: { title: string; detail: string }) {
  return (
    <article className="rounded-2xl border border-blue-100 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950/40">
      <div className="mb-3 inline-flex rounded-xl bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300">
        <BookOpen className="h-4 w-4" />
      </div>
      <div className="text-sm font-semibold text-slate-900 dark:text-white">{title}</div>
      <div className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{detail}</div>
    </article>
  );
}

function WeakPointCard({ item, rank }: { item: WeakPointRank; rank: number }) {
  return (
    <article className="rounded-2xl border border-blue-100 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950/40">
      <div className="flex items-start gap-3">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-orange-50 text-sm font-semibold text-orange-600 dark:bg-orange-500/10 dark:text-orange-300">
          {rank}
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-semibold text-slate-900 dark:text-white">{item.topic}</div>
          {item.errorPattern ? (
            <div className="mt-1 inline-flex rounded-full bg-orange-50 px-2 py-0.5 text-[11px] font-medium text-orange-600 dark:bg-orange-500/10 dark:text-orange-300">
              {item.errorPattern}
            </div>
          ) : null}
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
            {item.lastError || '暂无错误样本说明'}
          </p>
          {item.severityInferred ? (
            <div className="mt-3 text-xs text-slate-400 dark:text-slate-500">强度待接入真实数据</div>
          ) : (
            <div className="mt-3">
              <div className="mb-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>薄弱强度</span>
                <span>{item.severity}/100</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                <div className="h-full rounded-full bg-gradient-to-r from-orange-400 to-rose-500" style={{ width: `${Math.max(0, Math.min(100, item.severity))}%` }} />
              </div>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}

function FactRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 px-3 py-2 dark:bg-slate-800/60">
      <div className="text-xs text-slate-400 dark:text-slate-500">{label}</div>
      <div className="mt-1 text-slate-700 dark:text-slate-300">{value}</div>
    </div>
  );
}

function BehaviorTrendPanel(props: {
  analytics: UserProfileAnalyticsResponse | null;
  loading: boolean;
  error: string;
  onRetry: () => void;
}) {
  const trend = props.analytics?.behaviorTrend ?? [];
  const hasData = trend.some((point) => sumTrendActivity(point) > 0);
  const visibleTrend = trend.slice(-14);
  const maxActivity = Math.max(1, ...visibleTrend.map(sumTrendActivity));
  const coverage = props.analytics?.systemAnalysis.coverage;
  const practiceAccuracy = trend.length > 0 && coverage && coverage.practiceSubmissionCount > 0
    ? trend.reduce((sum, point) => sum + ((point.practiceAccuracy ?? 0) * point.practiceSubmissionCount), 0) / coverage.practiceSubmissionCount
    : null;

  return (
    <section id="behavior" className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
      <SectionTitle title="学习行为趋势" subtitle="来自近 30 天真实行为表聚合，不包含学习时长推测" />
      {props.loading ? (
        <AnalyticsStateMessage kind="loading" text="正在读取行为趋势" />
      ) : props.error ? (
        <AnalyticsStateMessage kind="error" text={props.error} onRetry={props.onRetry} />
      ) : !props.analytics || !hasData ? (
        <EmptyInline text={props.analytics ? `近 ${props.analytics.days} 天暂无真实行为记录。` : '暂无行为趋势数据。'} />
      ) : (
        <>
          <div className="mt-4 overflow-x-auto pb-1">
            <div
              className="grid min-w-[560px] gap-2"
              style={{ gridTemplateColumns: `repeat(${visibleTrend.length}, minmax(0, 1fr))` }}
            >
              {visibleTrend.map((point) => {
                const activity = sumTrendActivity(point);
                const height = activity === 0 ? 0 : Math.max(8, Math.round((activity / maxActivity) * 100));
                return (
                  <div key={point.date} className="flex min-h-[144px] flex-col items-center justify-end gap-2">
                    <div
                      className="flex h-24 w-full items-end rounded-xl bg-slate-100 px-1.5 py-1.5 dark:bg-slate-800"
                      title={`${point.date}：${activity} 次真实行为`}
                    >
                      <div
                        className="w-full rounded-lg bg-primary-500 transition-[height]"
                        style={{ height: `${height}%` }}
                      />
                    </div>
                    <span className="text-[11px] text-slate-400 dark:text-slate-500">{formatTrendDate(point.date)}</span>
                  </div>
                );
              })}
            </div>
          </div>
          {coverage ? (
            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              <CoverageStat label="对话" value={`${coverage.conversationCount}次`} />
              <CoverageStat label="学习服务" value={`${coverage.serviceTaskCount}个`} />
              <CoverageStat label="练习提交" value={`${coverage.practiceSubmissionCount}次`} />
              <CoverageStat label="练习正确率" value={formatPercent(practiceAccuracy)} />
              <CoverageStat label="新增错题" value={`${coverage.newMistakeCount}条`} />
              <CoverageStat label="复习" value={`${coverage.reviewCount}次`} />
            </div>
          ) : null}
        </>
      )}
    </section>
  );
}

function SystemAnalysisPanel(props: {
  analytics: UserProfileAnalyticsResponse | null;
  loading: boolean;
  error: string;
  onRetry: () => void;
}) {
  const analysis = props.analytics?.systemAnalysis;
  return (
    <section id="analysis" className="rounded-2xl border border-blue-100/80 bg-white/85 p-5 shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
      <SectionTitle title="系统分析" subtitle="由画像字段与真实行为聚合生成" />
      {props.loading ? (
        <AnalyticsStateMessage kind="loading" text="正在读取系统分析" />
      ) : props.error ? (
        <AnalyticsStateMessage kind="error" text={props.error} onRetry={props.onRetry} />
      ) : !analysis ? (
        <EmptyInline text="暂无系统分析数据。" />
      ) : !analysis.dataAvailable ? (
        <EmptyInline text={analysis.summary || '暂无足够真实数据生成系统分析。'} />
      ) : (
        <div className="mt-4 space-y-4">
          <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
            {analysis.summary}
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <InfoCard
              title="强项领域"
              value={analysis.strongestSkill || EMPTY_VALUE}
              detail={analysis.strongestSkillScore ? `掌握度 ${analysis.strongestSkillScore}%` : '真实证据不足'}
              muted={!analysis.strongestSkill}
            />
            <InfoCard
              title="重点关注"
              value={analysis.focusAreas.length > 0 ? analysis.focusAreas.join('、') : EMPTY_VALUE}
              detail={analysis.focusAreas.length > 0 ? '来自薄弱点与低掌握度字段' : '暂无明确关注项'}
              muted={analysis.focusAreas.length === 0}
            />
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            <CoverageStat label="画像掌握度字段" value={`${analysis.coverage.profileSkillCount}项`} />
            <CoverageStat label="薄弱点字段" value={`${analysis.coverage.weakPointCount}项`} />
            <CoverageStat label="近 30 天活跃日" value={`${analysis.coverage.activeDays}天`} />
            <CoverageStat label="可聚合行为" value={`${sumCoverageActivity(analysis.coverage)}次`} />
          </div>
        </div>
      )}
    </section>
  );
}

function CoverageStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 px-3 py-2 dark:bg-slate-800/60">
      <div className="text-[11px] text-slate-400 dark:text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-slate-700 dark:text-slate-200">{value}</div>
    </div>
  );
}

function AnalyticsStateMessage(props: {
  kind: 'loading' | 'error';
  text: string;
  onRetry?: () => void;
}) {
  return (
    <div className="mt-4 rounded-2xl border border-dashed border-slate-200 px-4 py-5 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
      <div className="flex items-center gap-2">
        {props.kind === 'loading' ? (
          <LoaderCircle className="h-4 w-4 animate-spin text-primary-500" />
        ) : (
          <TriangleAlert className="h-4 w-4 text-orange-500" />
        )}
        <span>{props.text}</span>
      </div>
      {props.kind === 'error' && props.onRetry ? (
        <button
          type="button"
          onClick={props.onRetry}
          className="mt-3 rounded-xl border border-blue-100 px-3 py-1.5 text-xs font-medium text-primary-600 transition-colors hover:bg-primary-50 dark:border-slate-700 dark:text-primary-300 dark:hover:bg-slate-800"
        >
          重试分析
        </button>
      ) : null}
    </div>
  );
}

function EmptyInline({ text }: { text: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-400 dark:border-slate-700 dark:text-slate-500">
      {text}
    </div>
  );
}

function ProfileAccessState(props: {
  icon: ReactNode;
  title: string;
  description: string;
  actionLabel: string;
  onAction: () => void;
}) {
  return (
    <div className="flex min-h-[420px] flex-col items-center justify-center rounded-2xl border border-blue-100 bg-white/85 px-6 text-center shadow-sm shadow-blue-100/60 dark:border-slate-800 dark:bg-slate-900/80">
      <div className="mb-4 rounded-2xl bg-primary-50 p-3 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300">
        {props.icon}
      </div>
      <h1 className="text-xl font-semibold text-slate-900 dark:text-white">{props.title}</h1>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500 dark:text-slate-400">{props.description}</p>
      <button
        type="button"
        onClick={props.onAction}
        className="mt-5 inline-flex h-10 items-center justify-center rounded-xl bg-primary-600 px-4 text-sm font-medium text-white shadow-lg shadow-primary-500/20 transition-colors hover:bg-primary-700"
      >
        {props.actionLabel}
      </button>
    </div>
  );
}

function countBehaviorSignals(habits: ProfileLearningHabits): number {
  return [
    habits.studyFrequency,
    habits.preferredTime,
    habits.avgSessionDuration > 0 ? habits.avgSessionDuration : '',
    habits.noteTaking ? 'noteTaking' : '',
    habits.selfTesting ? 'selfTesting' : '',
  ].filter(Boolean).length;
}

function sumTrendActivity(point: ProfileBehaviorTrendPoint): number {
  return point.conversationCount
    + point.serviceTaskCount
    + point.practiceSubmissionCount
    + point.newMistakeCount
    + point.reviewCount;
}

function sumCoverageActivity(coverage: UserProfileAnalyticsResponse['systemAnalysis']['coverage']): number {
  return coverage.conversationCount
    + coverage.serviceTaskCount
    + coverage.practiceSubmissionCount
    + coverage.newMistakeCount
    + coverage.reviewCount;
}

function analyticsTrendSummary(analytics: UserProfileAnalyticsResponse | null): string {
  if (!analytics) {
    return '';
  }
  const activeDays = analytics.systemAnalysis.coverage.activeDays;
  if (activeDays <= 0) {
    return `近 ${analytics.days} 天暂无真实行为记录`;
  }
  return `近 ${analytics.days} 天有 ${activeDays} 天学习行为记录`;
}

function formatTrendDate(date: string): string {
  const parsed = new Date(`${date}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) {
    return date.slice(5);
  }
  return parsed.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
  });
}

function formatPercent(value: number | null): string {
  if (value === null || !Number.isFinite(value)) {
    return EMPTY_VALUE;
  }
  return `${Math.round(value)}%`;
}
