import type { ComponentType } from 'react';
import { ChartColumn, Compass, Sparkles, Target } from 'lucide-react';
import type { SmartEngineServiceType, SmartEngineStreamEvent, SmartEngineTaskResponse, UserProfileResponse } from '../api/smartEngine';
import type { ConversationStreamEventPayload } from '../api/conversation';
import type { VideoCardStyle } from '../components/VideoCard';

export type EngineService = 'resource' | 'path' | 'push' | 'assessment';
export type ResourceType = 'EXPLANATION' | 'CODE_CASE' | 'QUIZ' | 'MINDMAP' | 'READING' | 'VIDEO';
export type QnaState = 'QNA_IDLE' | 'QNA_STREAMING';
export type EngineState =
  | 'ENGINE_IDLE'
  | 'ENGINE_SERVICE_SELECTED'
  | 'ENGINE_FORM_EDITING'
  | 'ENGINE_SUBMITTING'
  | 'ENGINE_RUNNING'
  | 'ENGINE_COMPLETED'
  | 'ENGINE_FAILED';
export type ProfileUpdateSource = 'BACKEND' | 'TASK_REFRESH';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export interface TempDownloadLink {
  title: string;
  url: string;
  expiresHint: string;
  resourceType?: string;
  thumbnailUrl?: string;
  duration?: number;
  style?: VideoCardStyle;
  knowledgePoint?: string;
}

export interface VideoResult {
  title: string;
  videoUrl: string;
  thumbnailUrl?: string;
  duration?: number;
  style?: VideoCardStyle;
  knowledgePoint?: string;
  expiresHint?: string;
}

export interface EngineTaskSnapshot {
  engineState: EngineState;
  taskId: string;
  taskProgress: number;
  taskStatus: string;
  taskSummary: string;
  serviceResultLines: string[];
  downloadLinks: TempDownloadLink[];
  videoResult: VideoResult | null;
}

export interface ResourceForm {
  resourceTypes: ResourceType[];
  course: string;
  difficulty: 'basic' | 'intermediate' | 'advanced';
  keyPoints: string;
  videoStyle: VideoCardStyle;
  durationSeconds: string;
}

export interface PathForm {
  targetPeriod: string;
  weeklyHours: string;
  currentProgress: string;
}

export interface PushForm {
  keyword: string;
  preferredType: ResourceType;
  courseScope: string;
}

export interface AssessmentForm {
  range: '7d' | '30d' | '60d';
  dimensions: string[];
}

export interface ProfileSnapshot {
  major: string;
  goal: string;
  knowledgeBase: string;
  weakPoints: string[];
  preference: string[];
  cognitiveStyle: string;
  confidenceLevel: string;
}

export interface TaskRunHandlers {
  onProgress: (progress: number, statusHint?: string) => void;
  onLine: (line: string) => void;
  onSummary: (summary: string) => void;
  onDownload: (item: TempDownloadLink) => void;
  onVideo: (item: VideoResult) => void;
}

export interface RunByApiTaskArgs {
  service: EngineService;
  currentTaskId: string;
  streamQueueRef: React.MutableRefObject<string[]>;
  streamFlushTimerRef: React.MutableRefObject<number | null>;
  streamRafRef: React.MutableRefObject<number | null>;
  setServiceResultLines: (value: React.SetStateAction<string[]>) => void;
  setTaskProgress: (value: React.SetStateAction<number>) => void;
  setTaskStatus: (value: React.SetStateAction<string>) => void;
  setTaskSummary: (value: React.SetStateAction<string>) => void;
  setDownloadLinks: (value: React.SetStateAction<TempDownloadLink[]>) => void;
  setVideoResult: (value: React.SetStateAction<VideoResult | null>) => void;
  taskStreamAbortRef: React.MutableRefObject<AbortController | null>;
}

export interface ServiceFormsPayload {
  resourceForm: ResourceForm;
  pathForm: PathForm;
  pushForm: PushForm;
  assessmentForm: AssessmentForm;
}

export interface ServiceButtonConfig {
  id: EngineService;
  label: string;
  icon: ComponentType<{ className?: string }>;
}

export interface ResourceTypeButtonConfig {
  type: ResourceType;
  label: string;
}

export type {
  ConversationStreamEventPayload,
  SmartEngineServiceType,
  SmartEngineStreamEvent,
  SmartEngineTaskResponse,
  UserProfileResponse,
  VideoCardStyle,
};

export const QNA_GREETING = '你好。你现在有什么要求？';
export const EMPTY_VALUE = '--';
export const defaultAssessmentDimensions = ['知识基础', '案例迁移', '练习掌握'];
export const assessmentDimensionOptions = ['知识基础', '案例迁移', '练习掌握', '学习主动性', '复盘闭环'];

export const serviceButtons: ServiceButtonConfig[] = [
  { id: 'resource', label: '资源生成', icon: Sparkles },
  { id: 'path', label: '学习路径规划', icon: Compass },
  { id: 'push', label: '资源推送', icon: Target },
  { id: 'assessment', label: '学习效果评估', icon: ChartColumn },
];

export const resourceTypeButtons: ResourceTypeButtonConfig[] = [
  { type: 'EXPLANATION', label: '讲解文档' },
  { type: 'CODE_CASE', label: '代码案例' },
  { type: 'QUIZ', label: '练习题' },
  { type: 'MINDMAP', label: '思维导图' },
  { type: 'READING', label: '拓展阅读' },
  { type: 'VIDEO', label: '教学视频/动画' },
];

export const serviceTypeMap: Record<EngineService, SmartEngineServiceType> = {
  resource: 'RESOURCE_GENERATION',
  path: 'PATH_PLANNING',
  push: 'RESOURCE_PUSH',
  assessment: 'LEARNING_EVALUATION',
};

export const defaultResourceForm: ResourceForm = {
  resourceTypes: ['EXPLANATION', 'CODE_CASE', 'QUIZ', 'VIDEO'],
  course: 'Java 程序设计',
  difficulty: 'intermediate',
  keyPoints: '并发编程',
  videoStyle: 'hybrid',
  durationSeconds: '60',
};
