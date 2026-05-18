import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock3, Compass, History, LayoutGrid, Menu, MessageCirclePlus, Search, Sparkles, UserRoundSearch } from 'lucide-react';
import AuthModal from './AuthModal';
import ThemeToggle from './ThemeToggle';

const ServiceDrawer = lazy(() => import('./ServiceDrawer'));
import { authApi, type AuthUser } from '../api/auth';
import { conversationApi, type ConversationHistoryItem } from '../api/conversation';
import { clearAuthSession, getAuthToken, isUnauthorizedError } from '../api/request';

type AuthTab = 'login' | 'register';

export interface LayoutOutletContext {
  isAuthenticated: boolean;
  currentUser: AuthUser | null;
  openAuthModal: (tab?: AuthTab, hint?: string) => void;
}

const SELECTED_CONVERSATION_STORAGE_KEY = 'learning_studio_selected_conversation';
const ACTIVE_CONVERSATION_ID_STORAGE_KEY = 'learning_studio_active_conversation_id';
const ENGINE_TASK_STORAGE_KEY = 'learning_studio_engine_tasks';
const QNA_SNAPSHOT_STORAGE_KEY = 'learning_studio_qna_snapshot';

function normalizeAuthUser(input: Awaited<ReturnType<typeof authApi.me>>): AuthUser | null {
  if (input.user) {
    const resolvedId = input.user.userId ?? input.user.id ?? input.userId ?? input.id;
    if (resolvedId === undefined || resolvedId === null) {
      return null;
    }
    return {
      id: resolvedId,
      userId: resolvedId,
      loginId: input.user.loginId ?? input.loginId ?? input.user.username,
      fullName: input.user.fullName ?? input.fullName ?? input.user.username,
      majorCode: input.user.majorCode ?? input.majorCode,
      username: input.user.username ?? input.user.loginId,
    };
  }

  const fallbackId = input.userId ?? input.id;
  if (fallbackId === undefined || fallbackId === null) {
    return null;
  }
  return {
    id: fallbackId,
    userId: fallbackId,
    loginId: input.loginId,
    fullName: input.fullName ?? input.loginId ?? `用户${fallbackId}`,
    majorCode: input.majorCode,
  };
}

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const inEngine = location.pathname.startsWith('/engine');
  const inProfile = location.pathname.startsWith('/profile');
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [defaultTab, setDefaultTab] = useState<AuthTab>('login');
  const [authHint, setAuthHint] = useState('');
  const [conversationHistory, setConversationHistory] = useState<ConversationHistoryItem[]>([]);
  const [lastSyncAt, setLastSyncAt] = useState('');
  const [activeConversationId, setActiveConversationId] = useState('');
  const [historySearch, setHistorySearch] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);
  const moreMenuRef = useRef<HTMLDivElement>(null);
  const [servicePanelOpen, setServicePanelOpen] = useState(false);

  const isAuthenticated = Boolean(currentUser);

  useEffect(() => {
    const token = getAuthToken();
    if (!token || typeof window === 'undefined') {
      return;
    }
    const rawAuthUser = window.localStorage.getItem('auth_user');
    if (!rawAuthUser) {
      return;
    }
    try {
      const parsed = JSON.parse(rawAuthUser) as AuthUser;
      if (parsed?.id !== undefined && parsed?.id !== null) {
        setCurrentUser(parsed);
      }
    } catch {
      // Ignore corrupted local cache and let bootstrapAuth resolve it.
    }
  }, []);

  const loadRecentConversations = async () => {
    if (!getAuthToken()) {
      setConversationHistory([]);
      setLastSyncAt('');
      return;
    }
    try {
      const items = await conversationApi.listRecentConversations();
      const sorted = [...items].sort((left, right) => {
        const leftTime = Date.parse(left.lastMessageAt || left.updatedAt || '') || 0;
        const rightTime = Date.parse(right.lastMessageAt || right.updatedAt || '') || 0;
        return rightTime - leftTime;
      });
      setConversationHistory(sorted);
      setLastSyncAt(new Date().toISOString());
    } catch (error) {
      console.error('Failed to load conversation history:', error);
      if (isUnauthorizedError(error)) {
        setConversationHistory([]);
        setLastSyncAt('');
      }
    }
  };

  useEffect(() => {
    const bootstrapAuth = async () => {
      const token = getAuthToken();
      if (!token) {
        setCurrentUser(null);
        return;
      }

      try {
        const me = await authApi.me();
        const resolved = normalizeAuthUser(me);
        if (!resolved) {
          clearAuthSession();
          setCurrentUser(null);
          return;
        }
        window.localStorage.setItem('auth_user', JSON.stringify(resolved));
        window.localStorage.setItem('userId', String(resolved.id));
        setCurrentUser(resolved);
        await loadRecentConversations();
      } catch (error) {
        if (isUnauthorizedError(error)) {
          clearAuthSession();
          setCurrentUser(null);
          setConversationHistory([]);
          setLastSyncAt('');
          return;
        }
      }
    };

    bootstrapAuth();
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    setActiveConversationId(window.sessionStorage.getItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY) ?? '');
    const handleActiveConversationChanged = (event: Event) => {
      const customEvent = event as CustomEvent<{ conversationId?: string }>;
      const nextId = customEvent.detail?.conversationId?.trim() ?? '';
      setActiveConversationId(nextId);
      if (nextId) {
        window.sessionStorage.setItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY, nextId);
      } else {
        window.sessionStorage.removeItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY);
      }
    };
    window.addEventListener('app:active-conversation-changed', handleActiveConversationChanged as EventListener);
    return () => {
      window.removeEventListener('app:active-conversation-changed', handleActiveConversationChanged as EventListener);
    };
  }, []);

  useEffect(() => {
    const handleConversationUpdated = () => {
      void loadRecentConversations();
    };
    window.addEventListener('app:conversation-updated', handleConversationUpdated);
    return () => {
      window.removeEventListener('app:conversation-updated', handleConversationUpdated);
    };
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
        setMoreMenuOpen(false);
      }
    };
    if (moreMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [moreMenuOpen]);

  const handleOpenProfilePage = useCallback(() => {
    setMoreMenuOpen(false);
    closeSidebar();
    setServicePanelOpen(false);
    if (!isAuthenticated) {
      openAuthModal('login', '?????????');
      return;
    }
    navigate('/profile');
  }, [isAuthenticated, navigate]);

  const handleOpenServicePanel = useCallback(() => {
    setMoreMenuOpen(false);
    closeSidebar();
    setServicePanelOpen(true);
  }, []);

  const openAuthModal = (tab: AuthTab = 'login', hint = '请先登录') => {
    setDefaultTab(tab);
    setAuthHint(hint);
    setModalOpen(true);
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore network error on logout cleanup
    } finally {
      clearAuthSession();
      setCurrentUser(null);
      setConversationHistory([]);
      setLastSyncAt('');
    }
  };

  const userDisplayName = useMemo(() => {
    if (!currentUser) {
      return '';
    }
    return currentUser.fullName || currentUser.loginId || currentUser.username || `用户${currentUser.id}`;
  }, [currentUser]);

  const filteredConversationHistory = useMemo(() => {
    const keyword = historySearch.trim().toLowerCase();
    if (!keyword) {
      return conversationHistory;
    }
    return conversationHistory.filter((item) => {
      const title = item.title?.toLowerCase() ?? '';
      const preview = item.lastMessagePreview?.toLowerCase() ?? '';
      return title.includes(keyword) || preview.includes(keyword);
    });
  }, [conversationHistory, historySearch]);

  const handleCreateNewChat = () => {
    if (!isAuthenticated) {
      openAuthModal('login', '登录后即可创建和保存新对话');
      return;
    }
    if (typeof window !== 'undefined') {
      window.sessionStorage.removeItem(SELECTED_CONVERSATION_STORAGE_KEY);
      window.sessionStorage.removeItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY);
      window.sessionStorage.removeItem(ENGINE_TASK_STORAGE_KEY);
      window.sessionStorage.removeItem(QNA_SNAPSHOT_STORAGE_KEY);
    }
    setActiveConversationId('');
    window.dispatchEvent(new CustomEvent('app:active-conversation-changed', { detail: { conversationId: '' } }));
    window.dispatchEvent(new Event('app:new-chat'));
    setSidebarOpen(false);
  };

  const handleOpenConversation = (item: ConversationHistoryItem) => {
    if (item.conversationId === activeConversationId && location.pathname === '/') {
      setSidebarOpen(false);
      return;
    }
    if (typeof window !== 'undefined') {
      window.sessionStorage.setItem(
        SELECTED_CONVERSATION_STORAGE_KEY,
        JSON.stringify({
          conversationId: item.conversationId,
          title: item.title,
          lastMessagePreview: item.lastMessagePreview ?? '',
        }),
      );
      window.sessionStorage.setItem(ACTIVE_CONVERSATION_ID_STORAGE_KEY, item.conversationId);
    }
    setActiveConversationId(item.conversationId);
    navigate('/');
    window.dispatchEvent(
      new CustomEvent('app:open-conversation', {
        detail: {
          conversationId: item.conversationId,
          title: item.title,
          lastMessagePreview: item.lastMessagePreview ?? '',
        },
      }),
    );
    window.dispatchEvent(
      new CustomEvent('app:active-conversation-changed', {
        detail: {
          conversationId: item.conversationId,
        },
      }),
    );
    setSidebarOpen(false);
  };

  const closeSidebar = () => setSidebarOpen(false);

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="border-b border-slate-200/60 px-5 py-4 dark:border-slate-700/60">
        <NavLink to="/" onClick={closeSidebar} className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600 text-white shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <p className="text-base font-semibold tracking-tight text-slate-900 dark:text-white">智学引擎</p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">AI 学习平台</p>
          </div>
        </NavLink>
      </div>

      {/* Navigation */}
      <div className="px-4 py-4 space-y-1.5">
        <NavLink
          to="/"
          onClick={() => {
            handleCreateNewChat();
          }}
          className={({ isActive }) =>
            `flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
              isActive
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
            }`
          }
        >
          <MessageCirclePlus className="h-4 w-4" />
          新对话
        </NavLink>
        <div className="relative" ref={moreMenuRef}>
          <button
            type="button"
            onClick={() => setMoreMenuOpen((prev) => !prev)}
            className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
              moreMenuOpen || inEngine || inProfile
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
            }`}
          >
            <LayoutGrid className="h-4 w-4" />
            更多功能
          </button>
          <AnimatePresence>
            {moreMenuOpen ? (
              <motion.div
                initial={{ opacity: 0, y: -4, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -4, scale: 0.96 }}
                transition={{ duration: 0.15 }}
                className="absolute left-0 top-full z-50 mt-1 w-full min-w-[200px] overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-xl shadow-slate-200/50 dark:border-slate-700 dark:bg-slate-900 dark:shadow-slate-900/50"
              >
                <button
                  type="button"
                  onClick={handleOpenProfilePage}
                  className="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-slate-600 transition-colors hover:bg-primary-50 hover:text-primary-700 dark:text-slate-400 dark:hover:bg-primary-900/50 dark:hover:text-primary-300"
                >
                  <UserRoundSearch className="h-4 w-4" />
                  查看个人画像
                </button>
                <button
                  type="button"
                  onClick={handleOpenServicePanel}
                  className="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-slate-600 transition-colors hover:bg-primary-50 hover:text-primary-700 dark:text-slate-400 dark:hover:bg-primary-900/50 dark:hover:text-primary-300"
                >
                  <Sparkles className="h-4 w-4" />
                  学习服务
                </button>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>

      {/* Auth / User */}
      <div className="px-4 pb-3">
        {!isAuthenticated ? (
          <button
            type="button"
            onClick={() => {
              closeSidebar();
              openAuthModal('login', '');
            }}
            className="w-full rounded-xl bg-primary-600 px-3 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-primary-700 active:scale-[0.98]"
          >
            立即登录
          </button>
        ) : (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-slate-700 dark:bg-slate-800/50">
            <div className="text-[11px] text-slate-400 dark:text-slate-500">当前用户</div>
            <div className="mt-0.5 text-sm font-medium text-slate-800 dark:text-slate-200">{userDisplayName}</div>
            <button type="button" onClick={handleLogout} className="mt-1.5 text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">
              退出登录
            </button>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="px-4 pb-3">
        <label className="flex items-center rounded-xl border border-slate-200 bg-white px-3 py-2 transition-all focus-within:border-primary-300 focus-within:ring-2 focus-within:ring-primary-500/20 dark:border-slate-700 dark:bg-slate-900 dark:focus-within:border-primary-600">
          <Search className="mr-2 h-3.5 w-3.5 shrink-0 text-slate-400" />
          <input
            value={historySearch}
            onChange={(event) => setHistorySearch(event.target.value)}
            placeholder="搜索历史对话"
            className="w-full bg-transparent text-xs text-slate-700 outline-none placeholder:text-slate-400 dark:text-slate-300 dark:placeholder:text-slate-500"
          />
        </label>
      </div>

      {/* Conversation List */}
      <div className="mt-2 flex-1 overflow-y-auto scrollbar-thin px-3 pb-4">
        <div className="mb-2 flex items-center gap-2 px-2 text-[11px] font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500">
          <History className="h-3.5 w-3.5" />
          最近对话
        </div>
        <div className="space-y-0.5">
          <AnimatePresence mode="popLayout">
            {filteredConversationHistory.length > 0 ? filteredConversationHistory.map((item, index) => (
              <motion.button
                key={item.conversationId}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: Math.min(index * 0.02, 0.3) }}
                type="button"
                onClick={() => handleOpenConversation(item)}
                className={`group w-full truncate rounded-lg px-3 py-2 text-left text-sm transition-all duration-200 ${
                  item.conversationId === activeConversationId
                    ? 'bg-primary-50 text-primary-700 ring-1 ring-primary-200/50 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/20'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
                }`}
                title={item.lastMessagePreview || item.title}
              >
                <div className="truncate text-[13px] font-medium">{item.title}</div>
                {item.lastMessagePreview ? (
                  <div className="mt-0.5 truncate text-[11px] opacity-60">{item.lastMessagePreview}</div>
                ) : null}
              </motion.button>
            )) : (
              <div className="rounded-lg px-3 py-2 text-[13px] text-slate-400 dark:text-slate-500">
                {isAuthenticated
                  ? historySearch.trim()
                    ? '没有匹配的历史对话'
                    : '暂无最近对话'
                  : '登录后显示最近对话'}
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-slate-200/60 px-4 py-3 dark:border-slate-700/60">
        <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 dark:bg-slate-800/50">
          <div className="flex items-center gap-2 text-[11px] text-slate-400 dark:text-slate-500">
            <Clock3 className="h-3.5 w-3.5" />
            同步 {lastSyncAt ? new Date(lastSyncAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '--'}
          </div>
          <button type="button" onClick={() => void loadRecentConversations()} className="text-[11px] text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">
            刷新
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      {/* Desktop Sidebar */}
      <aside className="fixed left-0 top-0 z-40 hidden h-screen w-[280px] flex-col border-r border-slate-200/60 bg-white/90 backdrop-blur-xl dark:border-slate-700/60 dark:bg-slate-900/90 md:flex">
        {sidebarContent}
      </aside>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen ? (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm md:hidden"
              onClick={closeSidebar}
            />
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="fixed left-0 top-0 z-50 flex h-screen w-[280px] flex-col border-r border-slate-200/60 bg-white/95 backdrop-blur-xl dark:border-slate-700/60 dark:bg-slate-900/95 md:hidden"
            >
              {sidebarContent}
            </motion.aside>
          </>
        ) : null}
      </AnimatePresence>

      {/* Main Content */}
      <main className={`flex-1 md:ml-[280px] transition-[margin-right] duration-300 ${servicePanelOpen ? 'md:mr-[520px]' : ''}`}>
        {/* Top Header */}
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-200/60 bg-white/80 px-4 py-3 backdrop-blur-xl dark:border-slate-700/60 dark:bg-slate-900/80 md:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 md:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
              <Compass className="h-4 w-4 text-primary-500" />
              <span className="hidden sm:inline">{inEngine ? '更多功能 / 服务选择面板' : '新对话 / 智能辅导链路'}</span>
              <span className="sm:hidden">{inEngine ? '服务面板' : '智能对话'}</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-[11px] text-slate-400 dark:text-slate-500 lg:inline">API 已连接</span>
            <ThemeToggle />
            {!isAuthenticated ? (
              <button
                type="button"
                onClick={() => openAuthModal('login', '')}
                className="rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700 md:hidden"
              >
                登录
              </button>
            ) : null}
          </div>
        </header>

        {/* Page Content */}
        <div className="px-4 py-4 md:px-6 md:py-6">
          <motion.div
            key={inProfile ? 'profile-shell' : inEngine ? 'engine-shell' : 'qna-shell'}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet context={{ isAuthenticated, currentUser, openAuthModal } satisfies LayoutOutletContext} />
          </motion.div>
        </div>
      </main>

      <AuthModal
        open={modalOpen}
        defaultTab={defaultTab}
        hint={authHint}
        onClose={() => setModalOpen(false)}
        onSuccess={(user) => {
          setCurrentUser(user);
          setModalOpen(false);
          void loadRecentConversations();
        }}
      />

      <Suspense fallback={null}>
        <ServiceDrawer
          open={servicePanelOpen}
          isAuthenticated={isAuthenticated}
          onClose={() => setServicePanelOpen(false)}
          zIndex={40}
        />
      </Suspense>
    </div>
  );
}
