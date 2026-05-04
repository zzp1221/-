export interface RawSseEvent {
  event: string;
  data: string;
}

interface StreamSseOptions {
  init: RequestInit;
  missingBodyMessage: string;
  requestFailedMessage: (status: number) => string;
  onOpen?: () => void;
  onEvent: (event: RawSseEvent) => boolean | void;
  onDone: () => void;
  onError: (error: Error) => void;
  defaultEvent?: string;
}

export async function streamSse(url: string, options: StreamSseOptions): Promise<void> {
  try {
    const response = await fetch(url, options.init);
    if (!response.ok) {
      throw new Error(options.requestFailedMessage(response.status));
    }
    options.onOpen?.();

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error(options.missingBodyMessage);
    }

    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        buffer += decoder.decode();
        const trailingEvent = parseSseEventBlock(buffer, options.defaultEvent);
        if (trailingEvent && options.onEvent(trailingEvent)) {
          return;
        }
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const eventBlocks = buffer.split('\n\n');
      buffer = eventBlocks.pop() ?? '';

      for (const block of eventBlocks) {
        const parsed = parseSseEventBlock(block, options.defaultEvent);
        if (!parsed) {
          continue;
        }
        if (options.onEvent(parsed)) {
          return;
        }
      }
    }

    options.onDone();
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return;
    }
    options.onError(error instanceof Error ? error : new Error('SSE 流执行失败'));
  }
}

export function parseSseEventBlock(block: string, defaultEvent = 'message'): RawSseEvent | null {
  if (!block.trim()) {
    return null;
  }

  const lines = block.split('\n');
  let event = defaultEvent;
  const dataParts: string[] = [];
  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (line.startsWith('event:')) {
      event = line.slice(6).trim();
      continue;
    }
    if (line.startsWith('data:')) {
      dataParts.push(line.slice(5).trimStart());
    }
  }

  return {
    event,
    data: dataParts.join('\n'),
  };
}
