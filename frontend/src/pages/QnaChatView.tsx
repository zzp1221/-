import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { ChatPanel, InputPanel } from './LearningStudioDemoPage.components';
import type { ChatMessage } from './LearningStudioDemoPage.types';

interface QnaChatViewProps {
  hasStartedConversation: boolean;
  qnaInput: string;
  qnaBusy: boolean;
  qnaMessages: ChatMessage[];
  onChange: (value: string) => void;
  onSend: () => void;
}

export default function QnaChatView(props: QnaChatViewProps) {
  if (!props.hasStartedConversation) {
    return (
      <div className="mx-auto flex h-[calc(100vh-12rem)] w-full max-w-[1120px] flex-col items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-xl shadow-indigo-500/25">
            <Sparkles className="h-7 w-7 text-white" />
          </div>
          <h1 className="mb-3 text-3xl font-semibold tracking-tight text-slate-800 dark:text-white md:text-[56px]">
            你好，我是智学引擎
          </h1>
          <p className="mb-9 text-slate-500 dark:text-slate-400">
            AI驱动的个性化学习助手，随时为你解答问题
          </p>
        </motion.div>
        <div className="w-full max-w-[720px] md:max-w-[860px]">
          <InputPanel
            value={props.qnaInput}
            busy={props.qnaBusy}
            placeholder="向智学引擎提问"
            onChange={props.onChange}
            onSend={props.onSend}
            variant="landing"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] w-full max-w-[1120px] flex-col md:h-[calc(100vh-9.5rem)]">
      <ChatPanel messages={props.qnaMessages} />
      <InputPanel
        value={props.qnaInput}
        busy={props.qnaBusy}
        placeholder="向智学引擎提问"
        onChange={props.onChange}
        onSend={props.onSend}
        variant="chat"
      />
    </div>
  );
}
