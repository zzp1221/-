import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import type { AuthUser } from '../api/auth';
import { smartEngineApi } from '../api/smartEngine';
import { RealtimeProfile } from '../pages/LearningStudioDemoPage.components';
import type { ProfileSnapshot, ProfileUpdateSource } from '../pages/LearningStudioDemoPage.types';
import { mapProfileResponse } from '../pages/LearningStudioDemoPage.utils';

interface ProfileDrawerProps {
  open: boolean;
  currentUser: AuthUser | null;
  onClose: () => void;
}

export default function ProfileDrawer({ open, currentUser, onClose }: ProfileDrawerProps) {
  const [profile, setProfile] = useState<ProfileSnapshot | null>(null);
  const [profileSummary, setProfileSummary] = useState('');
  const [profileUpdatedAt, setProfileUpdatedAt] = useState('');
  const [profileSource, setProfileSource] = useState<ProfileUpdateSource>('BACKEND');
  const [showAllWeakPoints, setShowAllWeakPoints] = useState(false);

  useEffect(() => {
    if (!open || !currentUser) {
      return;
    }
    let cancelled = false;
    const load = async () => {
      try {
        const response = await smartEngineApi.getCurrentProfile(String(currentUser.id));
        if (cancelled) return;
        setProfile(mapProfileResponse(response));
        setProfileSummary(response.summary ?? '');
        setProfileUpdatedAt(response.updatedAt ?? '');
        setProfileSource('BACKEND');
      } catch {
        if (!cancelled) {
          setProfile(null);
          setProfileSummary('');
          setProfileUpdatedAt('');
        }
      }
    };
    load();
    return () => { cancelled = true; };
  }, [open, currentUser]);

  useEffect(() => {
    setShowAllWeakPoints(false);
  }, [profile]);

  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm md:hidden"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: 480 }}
            animate={{ x: 0 }}
            exit={{ x: 480 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="fixed right-0 top-0 z-40 flex h-screen w-full max-w-[520px] flex-col border-l border-slate-200/60 bg-white/95 backdrop-blur-xl shadow-2xl dark:border-slate-700/60 dark:bg-slate-900/95"
          >
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3 dark:border-slate-800">
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">个人画像</h2>
              <button
                type="button"
                onClick={onClose}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              <RealtimeProfile
                profile={profile}
                summary={profileSummary}
                updatedAt={profileUpdatedAt}
                source={profileSource}
                showAllWeakPoints={showAllWeakPoints}
                onToggleWeakPoints={() => setShowAllWeakPoints((prev) => !prev)}
              />
            </div>
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
  );
}
