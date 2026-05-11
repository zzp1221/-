import { useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { conversationApi } from '../api/conversation';
import { getErrorMessage } from '../api/request';
import { smartEngineApi } from '../api/smartEngine';
import {
  ServiceDynamicForm,
  ServiceSubmitPanel,
  TaskResultPanel,
} from '../pages/LearningStudioDemoPage.components';
import {
  defaultAssessmentDimensions,
  defaultResourceForm,
  serviceButtons,
  serviceTypeMap,
  type AssessmentForm,
  type EngineService,
  type EngineTaskSnapshot,
  type PathForm,
  type PracticeQuestionBatch,
  type PushForm,
  type ResourceForm,
} from '../pages/LearningStudioDemoPage.types';
import {
  buildServiceParams,
  cleanupStreamSchedulers,
  runByApiTask,
  toUiTaskStatus,
} from '../pages/LearningStudioDemoPage.utils';

const ACTIVE_CONVERSATION_ID_STORAGE_KEY = 'learning_studio_active_conversation_id';

function createEmptyEngineTaskSnapshot(): EngineTaskSnapshot {
  return {
    engineState: 'ENGINE_IDLE',
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

interface ServiceDrawerProps {
  open: boolean;
  isAuthenticated: boolean;
  onClose: () => void;
  zIndex?: number;
}

export default function ServiceDrawer({ open, isAuthenticated, onClose, zIndex = 40 }: ServiceDrawerProps) {
  const mountedRef = useRef(true);
  const conversationIdRef = useRef('');
  const engineSubmitVersionRef = useRef(0);
  const activeTaskMonitorsRef = useRef<Partial<Record<EngineService, string>>>({});
  const taskMonitorRefsRef = useRef<Record<EngineService, {
    taskStreamAbortRef: { current: AbortController | null };
    streamQueueRef: { current: string[] };
    streamFlushTimerRef: { current: number | null };
    streamRafRef: { current: number | null };
  }>>({
    resource: { taskStreamAbortRef: { current: null }, streamQueueRef: { current: [] }, streamFlushTimerRef: { current: null }, streamRafRef: { current: null } },
    path: { taskStreamAbortRef: { current: null }, streamQueueRef: { current: [] }, streamFlushTimerRef: { current: null }, streamRafRef: { current: null } },
    push: { taskStreamAbortRef: { current: null }, streamQueueRef: { current: [] }, streamFlushTimerRef: { current: null }, streamRafRef: { current: null } },
    assessment: { taskStreamAbortRef: { current: null }, streamQueueRef: { current: [] }, streamFlushTimerRef: { current: null }, streamRafRef: { current: null } },
  });

  const [selectedService, setSelectedService] = useState<EngineService | null>(null);
  const [serviceSnapshots, setServiceSnapshots] = useState<Record<EngineService, EngineTaskSnapshot>>(createInitialEngineSnapshots);
  const [resourceForm, setResourceForm] = useState<ResourceForm>(defaultResourceForm);
  const [pathForm, setPathForm] = useState<PathForm>({ targetPeriod: '14 天', weeklyHours: '8', currentProgress: '已完成基础概念，准备进入案例训练' });
  const [pushForm, setPushForm] = useState<PushForm>({ preferredType: 'CODE_CASE' });
  const [assessmentForm, setAssessmentForm] = useState<AssessmentForm>({ range: '30d', dimensions: defaultAssessmentDimensions });

  const activeEngineSnapshot = selectedService ? serviceSnapshots[selectedService] : createEmptyEngineTaskSnapshot();
  const engineBusy = selectedService ? hasLockedTask(activeEngineSnapshot) : false;

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
    if (!open) return;
    mountedRef.current = true;
  }, [open]);

  useEffect(() => {
    conversationIdRef.current = window.sessionStorage.getItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY)?.trim() ?? '';
  }, [open]);

  const updateServiceSnapshot = useCallback(
    (service: EngineService, updater: EngineTaskSnapshot | ((current: EngineTaskSnapshot) => EngineTaskSnapshot)) => {
      setServiceSnapshots((prev) => {
        const current = prev[service];
        const next = typeof updater === 'function' ? updater(current) : updater;
        return { ...prev, [service]: next };
      });
    },
    [],
  );

  const ensureEngineConversationId = useCallback(async () => {
    const currentId = conversationIdRef.current.trim();
    if (currentId) return currentId;
    const storedId = window.sessionStorage.getItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY)?.trim() ?? '';
    if (storedId) {
      conversationIdRef.current = storedId;
      window.dispatchEvent(new Event('app:conversation-updated'));
      return storedId;
    }
    const recent = await conversationApi.listRecentConversations();
    const latestId = recent[0]?.conversationId?.trim() ?? '';
    if (latestId) {
      conversationIdRef.current = latestId;
      window.dispatchEvent(new Event('app:conversation-updated'));
      return latestId;
    }
    const createdId = (await conversationApi.createConversation()).conversationId;
    conversationIdRef.current = createdId;
    window.dispatchEvent(new Event('app:conversation-updated'));
    return createdId;
  }, []);

  const markFormEditing = () => {
    if (!selectedService) return;
    updateServiceSnapshot(selectedService, (current) => {
      if (hasLockedTask(current)) return current;
      return { ...current, engineState: 'ENGINE_FORM_EDITING' };
    });
  };

  const handleSelectService = (service: EngineService) => {
    setSelectedService(service);
    updateServiceSnapshot(service, (current) => {
      if (current.engineState !== 'ENGINE_IDLE' || current.taskId) return current;
      return { ...current, engineState: 'ENGINE_SERVICE_SELECTED' };
    });
  };

  const monitorTask = useCallback(
    async (service: EngineService, currentTaskId: string) => {
      if (activeTaskMonitorsRef.current[service] === currentTaskId) return;
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
      if (!mountedRef.current) return;

      if (outcome === 'completed') {
        updateServiceSnapshot(service, (c) => ({ ...c, engineState: 'ENGINE_COMPLETED', taskStatus: '任务完成' }));
      } else if (outcome === 'failed') {
        updateServiceSnapshot(service, (c) => ({ ...c, engineState: 'ENGINE_FAILED', taskStatus: '任务失败' }));
      } else if (outcome === 'aborted') {
        updateServiceSnapshot(service, (c) => ({ ...c, engineState: 'ENGINE_FAILED', taskStatus: '连接中断，请重试' }));
      } else if (outcome === 'running') {
        updateServiceSnapshot(service, (c) => ({
          ...c, engineState: 'ENGINE_RUNNING', taskStatus: '后台运行中',
          serviceResultLines: c.serviceResultLines.includes('任务仍在后台执行') ? c.serviceResultLines : [...c.serviceResultLines, '任务仍在后台执行，可关闭面板，稍后继续查看结果。'],
        }));
      } else if (outcome === 'unauthorized') {
        updateServiceSnapshot(service, (c) => ({ ...c, engineState: 'ENGINE_RUNNING', taskStatus: '登录失效，待重新登录' }));
      }
    },
    [updateServiceSnapshot],
  );

  const handleSubmitService = async () => {
    if (!isAuthenticated || !selectedService || engineBusy) return;
    const refs = taskMonitorRefsRef.current[selectedService];
    refs.taskStreamAbortRef.current?.abort();
    refs.taskStreamAbortRef.current = null;
    refs.streamQueueRef.current = [];
    cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    updateServiceSnapshot(selectedService, {
      engineState: 'ENGINE_SUBMITTING', taskId: '', taskProgress: 8, taskStatus: '已提交，等待受理',
      taskSummary: '', serviceResultLines: [], downloadLinks: [], videoResult: null,
      inlineResource: null, practiceBatch: null, judgeResult: null,
    });
    const params = buildServiceParams(selectedService, { resourceForm, pathForm, pushForm, assessmentForm });
    try {
      engineSubmitVersionRef.current += 1;
      const submitVersion = engineSubmitVersionRef.current;
      const ensuredId = await ensureEngineConversationId();
      if (engineSubmitVersionRef.current !== submitVersion) return;
      const submitResp = await smartEngineApi.submit({ conversationId: ensuredId, serviceType: serviceTypeMap[selectedService], params });
      updateServiceSnapshot(selectedService, (c) => ({ ...c, taskId: submitResp.taskId, engineState: 'ENGINE_RUNNING', taskStatus: toUiTaskStatus(submitResp.status) }));
      void monitorTask(selectedService, submitResp.taskId);
    } catch (error) {
      const message = getErrorMessage(error);
      updateServiceSnapshot(selectedService, (c) => ({ ...c, engineState: 'ENGINE_FAILED', taskStatus: '任务失败', serviceResultLines: [...c.serviceResultLines, `接口失败：${message}`] }));
    }
  };

  const handleStopService = () => {
    if (!selectedService) return;
    const refs = taskMonitorRefsRef.current[selectedService];
    refs.taskStreamAbortRef.current?.abort();
    refs.taskStreamAbortRef.current = null;
    activeTaskMonitorsRef.current[selectedService] = '';
    cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    updateServiceSnapshot(selectedService, (c) => ({
      ...c, engineState: 'ENGINE_FAILED', taskStatus: '已停止实时接收',
      serviceResultLines: c.serviceResultLines.includes('已停止') ? c.serviceResultLines : [...c.serviceResultLines, '已停止当前面板的实时接收，任务可能仍在后台继续执行。'],
    }));
  };

  const handleSubmitPracticeAnswers = async (batch: PracticeQuestionBatch, answers: Record<string, string>) => {
    if (!isAuthenticated) return;
    const targetService: EngineService = selectedService === 'assessment' ? 'assessment' : 'resource';
    if (hasLockedTask(serviceSnapshots[targetService])) return;
    const refs = taskMonitorRefsRef.current[targetService];
    refs.taskStreamAbortRef.current?.abort();
    refs.taskStreamAbortRef.current = null;
    refs.streamQueueRef.current = [];
    cleanupStreamSchedulers(refs.streamFlushTimerRef, refs.streamRafRef);
    updateServiceSnapshot(targetService, (c) => ({ ...c, engineState: 'ENGINE_SUBMITTING', taskId: '', taskProgress: 12, taskStatus: '已提交判题任务', taskSummary: '', serviceResultLines: [], judgeResult: null }));
    try {
      const ensuredId = await ensureEngineConversationId();
      const assessmentDimension = batch.assessmentDimension || (targetService === 'assessment' ? assessmentForm.dimensions[0] : '');
      const batchTopic = batch.topic || resourceForm.keyPoints || resourceForm.course;
      const judgeQuery = targetService === 'assessment' ? `${assessmentDimension || '专项评估'} ${batchTopic} 判题` : `${resourceForm.course} ${batchTopic} 练习题判题`;
      const submitResp = await smartEngineApi.submit({
        conversationId: ensuredId, serviceType: 'PRACTICE_JUDGE',
        params: { topic: targetService === 'assessment' && assessmentDimension ? `${assessmentDimension}：${batchTopic}` : batchTopic, query: judgeQuery, practiceQuestionBatch: batch, practiceQuestions: batch.questions, answers, assessmentDimension, learningContext: { course: resourceForm.course, chapter: batchTopic } },
      });
      updateServiceSnapshot(targetService, (c) => ({ ...c, taskId: submitResp.taskId, engineState: 'ENGINE_RUNNING', taskStatus: toUiTaskStatus(submitResp.status) }));
      void monitorTask(targetService, submitResp.taskId);
    } catch (error) {
      const message = getErrorMessage(error);
      updateServiceSnapshot(targetService, (c) => ({ ...c, engineState: 'ENGINE_FAILED', taskStatus: '判题失败', serviceResultLines: [...c.serviceResultLines, `判题失败：${message}`] }));
    }
  };

  const drawerWidth = 'max-w-[540px]';

  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className={`fixed inset-0 bg-black/20 backdrop-blur-sm md:hidden`}
            style={{ zIndex }}
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: 540 }}
            animate={{ x: 0 }}
            exit={{ x: 540 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className={`fixed right-0 top-0 flex h-screen w-full ${drawerWidth} flex-col border-l border-slate-200/60 bg-white/95 backdrop-blur-xl shadow-2xl dark:border-slate-700/60 dark:bg-slate-900/95`}
            style={{ zIndex }}
          >
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3 dark:border-slate-800">
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">学习服务</h2>
              <button
                type="button"
                onClick={onClose}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              <div className="space-y-4 p-4">
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-slate-800 dark:text-white">选择一项智能服务</h3>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">开始你的学习之旅</p>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {serviceButtons.map((item) => {
                    const active = selectedService === item.id;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => handleSelectService(item.id)}
                        className={`flex flex-col items-center gap-1 rounded-xl border px-3 py-2.5 text-sm transition-all duration-200 ${
                          active
                            ? 'border-indigo-300 bg-indigo-50 text-indigo-700 shadow-sm dark:border-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400'
                            : 'border-slate-200 bg-white text-slate-600 hover:border-indigo-200 hover:bg-indigo-50/50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:border-indigo-700'
                        }`}
                      >
                        <item.icon className={`h-5 w-5 ${active ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'}`} />
                        <span className="text-xs">{item.label}</span>
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
                  onResourceChange={(next) => { setResourceForm(next); markFormEditing(); }}
                  onPathChange={(next) => { setPathForm(next); markFormEditing(); }}
                  onPushChange={(next) => { setPushForm(next); markFormEditing(); }}
                  onAssessmentChange={(next) => { setAssessmentForm(next); markFormEditing(); }}
                />

                <ServiceSubmitPanel
                  disabled={!selectedService || engineBusy}
                  onSubmit={handleSubmitService}
                  onStop={handleStopService}
                  canStop={engineBusy}
                  taskId={activeEngineSnapshot.taskId}
                  progress={activeEngineSnapshot.taskProgress}
                  status={activeEngineSnapshot.taskStatus}
                  uiState={activeEngineSnapshot.engineState}
                />
              </div>

              <div className="px-4 pb-8">
                <TaskResultPanel
                  service={selectedService}
                  taskSummary={activeEngineSnapshot.taskSummary}
                  serviceResultLines={activeEngineSnapshot.serviceResultLines}
                  downloadLinks={activeEngineSnapshot.downloadLinks}
                  videoResult={activeEngineSnapshot.videoResult}
                  inlineResource={activeEngineSnapshot.inlineResource}
                  practiceBatch={activeEngineSnapshot.practiceBatch}
                  judgeResult={activeEngineSnapshot.judgeResult}
                  canSubmitPractice={!hasLockedTask(activeEngineSnapshot)}
                  onSubmitPracticeAnswers={handleSubmitPracticeAnswers}
                />
              </div>
            </div>
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
  );
}
