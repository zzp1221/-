import { memo, useEffect, useId, useRef, useState, type ClipboardEvent, type DragEvent } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowDown, FileImage, LoaderCircle, Paperclip, SendHorizontal, Sparkles, X, XCircle } from 'lucide-react';
import MarkdownRenderer from '../components/MarkdownRenderer';
import { normalizeCopyText } from './LearningStudioDemoPage.utils';
import type { ChatMessage, PendingChatImage } from './LearningStudioDemoPage.types';

interface ChatMessageBubbleProps {
  message: ChatMessage;
  isStreaming: boolean;
  onPreviewImage: (imageUrl: string) => void;
  onCopy: (message: ChatMessage) => void;
  copiedMessageId: string | null;
}

const ChatMessageBubble = memo(function ChatMessageBubble({
  message,
  isStreaming,
  onPreviewImage,
  onCopy,
  copiedMessageId,
}: ChatMessageBubbleProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-[90%] md:max-w-[82%] ${message.role === 'user' ? '' : 'w-full md:w-auto'}`}>
        {message.role === 'user' ? (
          <div className="rounded-2xl rounded-br-md bg-primary-600 px-4 py-2.5 text-[15px] leading-7 text-white shadow-sm">
            {message.imageUrls?.length ? (
              <div className="mb-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
                {message.imageUrls.map((imageUrl, index) => (
                  <button
                    key={`${message.id}-image-${index}`}
                    type="button"
                    className="overflow-hidden rounded-xl border border-white/20 bg-white/10"
                    onClick={() => onPreviewImage(imageUrl)}
                  >
                    <img src={imageUrl} alt={`上传图片 ${index + 1}`} className="h-24 w-full object-cover" />
                  </button>
                ))}
              </div>
            ) : null}
            {message.content ? <div>{message.content}</div> : <div className="text-white/80">[图片提问]</div>}
          </div>
        ) : (
          <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {message.content ? (
              <MarkdownRenderer content={message.content} isStreaming={isStreaming} />
            ) : (
              <MarkdownRenderer content="" isStreaming={true} />
            )}
          </div>
        )}
        {message.content ? (
          <div className={`mt-1.5 flex items-center gap-2 text-xs ${message.role === 'user' ? 'justify-end' : ''}`}>
            {message.role === 'assistant' ? (
              <span className="text-slate-400 dark:text-slate-500">
                <Sparkles className="inline h-3 w-3" /> 智学引擎
              </span>
            ) : null}
            <button
              type="button"
              onClick={() => onCopy(message)}
              className="rounded-md px-1.5 py-0.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:text-slate-500 dark:hover:bg-slate-800 dark:hover:text-slate-300"
            >
              {copiedMessageId === message.id ? '已复制' : '复制'}
            </button>
          </div>
        ) : null}
      </div>
    </motion.div>
  );
});

export const ChatPanel = memo(function ChatPanel({ messages }: { messages: ChatMessage[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const lastMessage = messages[messages.length - 1];
  const isStreaming = Boolean(lastMessage && lastMessage.role === 'assistant' && !lastMessage.content);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
  }, []);

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
          {messages.map((message) => (
            <ChatMessageBubble
              key={message.id}
              message={message}
              isStreaming={message.id === lastMessage?.id && isStreaming}
              onPreviewImage={setPreviewImage}
              onCopy={handleCopy}
              copiedMessageId={copiedMessageId}
            />
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
      {previewImage ? (
        <button
          type="button"
          onClick={() => setPreviewImage(null)}
          className="absolute inset-0 z-20 flex items-center justify-center bg-slate-950/80 p-4"
        >
          <img src={previewImage} alt="图片预览" className="max-h-[90%] max-w-[90%] rounded-2xl object-contain shadow-2xl" />
        </button>
      ) : null}
    </div>
  );
});

export function InputPanel(props: {
  value: string;
  busy: boolean;
  placeholder: string;
  pendingImages: PendingChatImage[];
  errorMessage?: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onPickImages: (files: File[]) => void;
  onRemoveImage: (id: string) => void;
  variant?: 'landing' | 'chat';
}) {
  const isLanding = props.variant === 'landing';
  const fileInputId = useId();
  const [isDragActive, setIsDragActive] = useState(false);

  const pickFiles = (files: FileList | null) => {
    if (!files || files.length === 0) {
      return;
    }
    props.onPickImages(Array.from(files));
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    pickFiles(event.dataTransfer.files);
  };

  const handlePaste = (event: ClipboardEvent<HTMLTextAreaElement>) => {
    const imageFiles = Array.from(event.clipboardData.files).filter((file) => file.type.startsWith('image/'));
    if (!imageFiles.length) {
      return;
    }
    event.preventDefault();
    props.onPickImages(imageFiles);
  };

  return (
    <div className="shrink-0 px-2 pb-4 md:px-0">
      <div className={`mx-auto transition-all duration-300 ${
        isLanding
          ? 'rounded-3xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-900'
          : 'rounded-3xl border border-slate-200 bg-white shadow-sm focus-within:shadow-md focus-within:ring-2 focus-within:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:focus-within:ring-primary-500/10'
      }`}>
        <div
          className={`${isDragActive ? 'bg-primary-50/80 dark:bg-primary-500/10' : ''} rounded-3xl transition-colors`}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragActive(true);
          }}
          onDragLeave={(event) => {
            event.preventDefault();
            setIsDragActive(false);
          }}
          onDrop={handleDrop}
        >
          {props.pendingImages.length ? (
            <div className="flex flex-wrap gap-3 px-4 pt-4 md:px-5">
              {props.pendingImages.map((image) => (
                <div key={image.id} className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800">
                  <img src={image.previewUrl} alt="待上传图片" className="h-24 w-24 object-cover" />
                  <button
                    type="button"
                    onClick={() => props.onRemoveImage(image.id)}
                    className="absolute right-2 top-2 rounded-full bg-slate-900/70 p-1 text-white opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                  <div className="absolute inset-x-0 bottom-0 bg-slate-950/70 px-2 py-1 text-[11px] text-white">
                    {image.uploadStatus === 'failed'
                      ? '上传失败'
                      : image.uploadStatus === 'uploaded'
                        ? '上传完成'
                        : `上传中 ${image.uploadProgress}%`}
                  </div>
                </div>
              ))}
            </div>
          ) : null}
          <div className="flex items-end gap-3 px-4 py-4 md:px-5">
            <label
              htmlFor={fileInputId}
              className={`flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-2xl border text-slate-500 transition-colors ${
                props.busy
                  ? 'cursor-not-allowed border-slate-200 bg-slate-100 text-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-600'
                  : 'border-slate-200 bg-slate-50 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:border-primary-700 dark:hover:bg-primary-500/10 dark:hover:text-primary-400'
              }`}
            >
              <Paperclip className="h-4.5 w-4.5" />
            </label>
            <input
              id={fileInputId}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              multiple
              disabled={props.busy}
              className="hidden"
              onChange={(event) => {
                pickFiles(event.target.files);
                event.currentTarget.value = '';
              }}
            />
            <div className="min-w-0 flex-1">
              <textarea
                value={props.value}
                onChange={(event) => props.onChange(event.target.value)}
                onPaste={handlePaste}
                rows={isLanding ? 3 : 2}
                placeholder={props.placeholder}
                disabled={props.busy}
                className="max-h-48 min-h-[56px] w-full resize-none border-none bg-transparent px-0 py-1 text-[15px] leading-7 text-slate-700 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed dark:text-slate-200 dark:placeholder:text-slate-500"
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    props.onSend();
                  }
                }}
              />
              {props.errorMessage ? (
                <div className="mt-2 flex items-center gap-1.5 text-xs text-rose-500">
                  <XCircle className="h-3.5 w-3.5" />
                  <span>{props.errorMessage}</span>
                </div>
              ) : (
                <div className="mt-2 flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500">
                  <FileImage className="h-3.5 w-3.5" />
                  <span>支持粘贴、拖拽或上传图片，Enter 发送，Shift + Enter 换行</span>
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={props.onSend}
              disabled={props.busy || (!props.value.trim() && props.pendingImages.every((item) => !item.uploadedUrl))}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-primary-600 text-white shadow-sm transition-all hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 dark:disabled:bg-slate-700 dark:disabled:text-slate-500"
            >
              {props.busy ? <LoaderCircle className="h-4.5 w-4.5 animate-spin" /> : <SendHorizontal className="h-4.5 w-4.5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
