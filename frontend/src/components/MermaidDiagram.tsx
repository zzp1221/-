import { useEffect, useId, useState } from 'react';
import DOMPurify from 'dompurify';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
}

let mermaidInitialized = false;

function ensureMermaidInitialized(): void {
  if (mermaidInitialized) {
    return;
  }
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'default',
  });
  mermaidInitialized = true;
}

function normalizeMermaidChart(chart: string): string {
  const trimmed = chart.trim();
  if (!trimmed) {
    return '';
  }
  const withoutFence = trimmed
    .replace(/^```mermaid\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/\s*```$/i, '')
    .trim();
  const mindmapIndex = withoutFence.toLowerCase().indexOf('mindmap');
  if (mindmapIndex >= 0) {
    return withoutFence.slice(mindmapIndex).trim();
  }
  return withoutFence;
}

export default function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const id = useId().replace(/:/g, '-');
  const [svg, setSvg] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    async function renderChart() {
      const normalizedChart = normalizeMermaidChart(chart);
      if (!normalizedChart) {
        setSvg('');
        setError('');
        return;
      }
      ensureMermaidInitialized();
      try {
        const result = await mermaid.render(`mermaid-${id}`, normalizedChart);
        if (!cancelled) {
          setSvg(DOMPurify.sanitize(result.svg, { USE_PROFILES: { svg: true } }));
          setError('');
        }
      } catch (renderError) {
        if (!cancelled) {
          setSvg('');
          const message = renderError instanceof Error ? renderError.message : 'Mermaid 渲染失败';
          setError(`思维导图渲染失败：${message}`);
        }
      }
    }
    void renderChart();
    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  if (error) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700 dark:border-amber-800 dark:bg-amber-500/10 dark:text-amber-300">
        {error}
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-400">
        思维导图渲染中...
      </div>
    );
  }

  return (
    <div
      className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-950"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
