import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SplashScreenProps {
  onComplete: () => void;
}

export default function SplashScreen({ onComplete }: SplashScreenProps) {
  const [ready, setReady] = useState(false);

  const handleComplete = useCallback(() => {
    onComplete();
  }, [onComplete]);

  useEffect(() => {
    setReady(true);

    const onMessage = (e: MessageEvent) => {
      if (e.data === 'splash-complete') handleComplete();
    };
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, [handleComplete]);

  return (
    <AnimatePresence>
      {ready && (
        <motion.div
          className="fixed inset-0 z-[9999]"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.01 }}
        >
          <iframe
            src="/splash.html"
            className="w-full h-full border-0"
            title="智学引擎启动"
            allow="fullscreen"
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
