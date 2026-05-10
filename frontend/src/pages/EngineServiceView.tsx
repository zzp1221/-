import {
  RealtimeProfile,
  ServiceDynamicForm,
  ServiceSubmitPanel,
  TaskResultPanel,
} from './LearningStudioDemoPage.components';
import {
  serviceButtons,
  type AssessmentForm,
  type EngineService,
  type EngineState,
  type EngineTaskSnapshot,
  type PathForm,
  type PracticeQuestionBatch,
  type ProfileSnapshot,
  type ProfileUpdateSource,
  type PushForm,
  type ResourceForm,
  type TempDownloadLink,
  type VideoResult,
} from './LearningStudioDemoPage.types';

interface EngineServiceViewProps {
  profile: ProfileSnapshot | null;
  profileSummary: string;
  profileUpdatedAt: string;
  profileSource: ProfileUpdateSource;
  showAllWeakPoints: boolean;
  onToggleWeakPoints: () => void;
  selectedService: EngineService | null;
  engineBusy: boolean;
  taskId: string;
  taskProgress: number;
  taskStatus: string;
  taskSummary: string;
  serviceResultLines: string[];
  downloadLinks: TempDownloadLink[];
  videoResult: VideoResult | null;
  activeEngineSnapshot: EngineTaskSnapshot;
  engineStateView: EngineState;
  onSelectService: (service: EngineService) => void;
  onResourceChange: (next: ResourceForm) => void;
  onPathChange: (next: PathForm) => void;
  onPushChange: (next: PushForm) => void;
  onAssessmentChange: (next: AssessmentForm) => void;
  onSubmitService: () => void;
  onStopService: () => void;
  onSubmitPracticeAnswers: (batch: PracticeQuestionBatch, answers: Record<string, string>) => void;
  resourceForm: ResourceForm;
  pathForm: PathForm;
  pushForm: PushForm;
  assessmentForm: AssessmentForm;
}

export default function EngineServiceView(props: EngineServiceViewProps) {
  const snapshot = props.activeEngineSnapshot;

  return (
    <div className="mx-auto max-w-[1180px] space-y-6 pb-10 px-1 md:px-0">
      <RealtimeProfile
        profile={props.profile}
        summary={props.profileSummary}
        updatedAt={props.profileUpdatedAt}
        source={props.profileSource}
        showAllWeakPoints={props.showAllWeakPoints}
        onToggleWeakPoints={props.onToggleWeakPoints}
      />

      <div className="modern-card p-5 md:p-6">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-800 dark:text-white md:text-[34px]">
            你好，我是智学引擎
          </h1>
          <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
            选择一项智能服务，开始你的学习之旅
          </p>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-2 md:flex md:flex-wrap md:justify-center md:gap-3">
          {serviceButtons.map((item) => {
            const active = props.selectedService === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => props.onSelectService(item.id)}
                className={`group flex flex-col items-center gap-1.5 rounded-2xl border px-4 py-3 text-sm transition-all duration-200 md:flex-row md:gap-2 md:px-4 md:py-2 ${
                  active
                    ? 'border-indigo-300 bg-indigo-50 text-indigo-700 shadow-sm dark:border-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-indigo-200 hover:bg-indigo-50/50 hover:text-indigo-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:border-indigo-700 dark:hover:bg-indigo-500/5'
                }`}
              >
                <item.icon
                  className={`h-5 w-5 md:h-4 md:w-4 ${
                    active
                      ? 'text-indigo-600 dark:text-indigo-400'
                      : 'text-slate-400 group-hover:text-indigo-500 dark:text-slate-500'
                  }`}
                />
                <span className="text-xs md:text-sm">{item.label}</span>
              </button>
            );
          })}
        </div>

        <ServiceDynamicForm
          service={props.selectedService}
          resourceForm={props.resourceForm}
          pathForm={props.pathForm}
          pushForm={props.pushForm}
          assessmentForm={props.assessmentForm}
          onResourceChange={props.onResourceChange}
          onPathChange={props.onPathChange}
          onPushChange={props.onPushChange}
          onAssessmentChange={props.onAssessmentChange}
        />

        <ServiceSubmitPanel
          disabled={!props.selectedService || props.engineBusy}
          onSubmit={props.onSubmitService}
          onStop={props.onStopService}
          canStop={props.engineBusy}
          taskId={props.taskId}
          progress={props.taskProgress}
          status={props.taskStatus}
          uiState={props.engineStateView}
        />
      </div>

      <TaskResultPanel
        service={props.selectedService}
        taskSummary={props.taskSummary}
        serviceResultLines={props.serviceResultLines}
        downloadLinks={props.downloadLinks}
        videoResult={props.videoResult}
        inlineResource={snapshot.inlineResource}
        practiceBatch={snapshot.practiceBatch}
        judgeResult={snapshot.judgeResult}
        canSubmitPractice={snapshot.taskId === '' || snapshot.engineState === 'ENGINE_COMPLETED' || snapshot.engineState === 'ENGINE_FAILED'}
        onSubmitPracticeAnswers={props.onSubmitPracticeAnswers}
      />
    </div>
  );
}
