import { useMemo, useState } from 'react';
import { PlayCircle } from 'lucide-react';

export type VideoCardStyle = 'talking_head' | 'animation' | 'hybrid';

export interface VideoCardProps {
  title: string;
  videoUrl: string;
  thumbnailUrl?: string;
  duration?: number;
  style?: VideoCardStyle;
  knowledgePoint?: string;
  expiresHint?: string;
  onPlay?: () => void;
  onComplete?: () => void;
}

const styleLabelMap: Record<VideoCardStyle, string> = {
  talking_head: '数字人讲解',
  animation: '动画演示',
  hybrid: '混合讲解',
};

export default function VideoCard(props: VideoCardProps) {
  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);

  const durationLabel = useMemo(() => {
    if (typeof props.duration !== 'number' || Number.isNaN(props.duration) || props.duration <= 0) {
      return '';
    }
    const minutes = Math.floor(props.duration / 60);
    const seconds = Math.floor(props.duration % 60);
    if (minutes <= 0) {
      return `${seconds} 秒`;
    }
    return `${minutes} 分 ${seconds.toString().padStart(2, '0')} 秒`;
  }, [props.duration]);

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="relative aspect-video bg-slate-900">
        {props.thumbnailUrl ? (
          <img src={props.thumbnailUrl} alt={props.title} className="absolute inset-0 h-full w-full object-cover" />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900" />
        )}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/70 via-transparent to-transparent" />
        <div className="pointer-events-none absolute left-4 top-4 inline-flex items-center gap-1 rounded-full bg-black/45 px-2.5 py-1 text-xs text-white">
          <PlayCircle className="h-3.5 w-3.5" />
          教学视频
        </div>
        {durationLabel ? (
          <div className="pointer-events-none absolute bottom-4 right-4 rounded-full bg-black/60 px-2.5 py-1 text-xs text-white">{durationLabel}</div>
        ) : null}
        <video
          controls
          preload="metadata"
          poster={props.thumbnailUrl}
          className="relative z-10 h-full w-full"
          onPlay={() => {
            if (!started) {
              setStarted(true);
              props.onPlay?.();
            }
          }}
          onEnded={() => {
            if (!completed) {
              setCompleted(true);
              props.onComplete?.();
            }
          }}
        >
          <source src={props.videoUrl} />
          当前浏览器不支持视频播放，请直接下载后查看。
        </video>
      </div>
      <div className="space-y-3 p-4">
        <div>
          <div className="text-base font-semibold text-slate-800">{props.title}</div>
          {props.knowledgePoint ? <div className="mt-1 text-sm text-slate-500">知识点：{props.knowledgePoint}</div> : null}
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          {props.style ? <span className="rounded-full bg-blue-50 px-2.5 py-1 text-blue-700">{styleLabelMap[props.style]}</span> : null}
          {started ? <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-700">已开始观看</span> : null}
          {completed ? <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-700">已观看完成</span> : null}
        </div>
        <div className="flex items-center justify-between gap-3 text-sm">
          <span className="text-slate-500">{props.expiresHint || '视频资源已生成'}</span>
          <a href={props.videoUrl} target="_blank" rel="noreferrer" className="font-medium text-blue-600 hover:text-blue-700">
            打开原始视频
          </a>
        </div>
      </div>
    </div>
  );
}
