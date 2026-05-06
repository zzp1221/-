import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { motion } from 'framer-motion';

type Theme = 'light' | 'dark';

function getSystemTheme(): Theme {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getStoredTheme(): Theme | null {
  if (typeof window === 'undefined') return null;
  const stored = localStorage.getItem('theme');
  if (stored === 'dark' || stored === 'light') return stored;
  return null;
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => getStoredTheme() ?? getSystemTheme());

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => {
      if (!getStoredTheme()) {
        const next = getSystemTheme();
        setTheme(next);
      }
    };
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  const toggle = () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));

  return (
    <button
      type="button"
      onClick={toggle}
      className="relative flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
      title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
    >
      <motion.div
        key={theme}
        initial={{ rotate: -90, opacity: 0, scale: 0.5 }}
        animate={{ rotate: 0, opacity: 1, scale: 1 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
      >
        {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
      </motion.div>
    </button>
  );
}
