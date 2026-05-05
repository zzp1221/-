import { useEffect, useMemo, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Clock3, Compass, History, MessageCirclePlus, Search, Sparkles } from 'lucide-react';
import AuthModal from './AuthModal';
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
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [defaultTab, setDefaultTab] = useState<AuthTab>('login');
  const [authHint, setAuthHint] = useState('');
  const [conversationHistory, setConversationHistory] = useState<ConversationHistoryItem[]>([]);
  const [lastSyncAt, setLastSyncAt] = useState('');
  const [activeConversationId, setActiveConversationId] = useState('');
  const [historySearch, setHistorySearch] = useState('');

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
  };

  const handleOpenConversation = (item: ConversationHistoryItem) => {
    if (item.conversationId === activeConversationId && location.pathname === '/') {
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
  };

  return (
    <div className="flex min-h-screen bg-[#f7f8fb] text-slate-900">
      <aside className="fixed left-0 top-0 z-40 flex h-screen w-[280px] flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-4">
          <NavLink to="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-white">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <p className="text-base font-semibold text-slate-900">智学引擎</p>
              <p className="text-xs text-slate-500">比赛系统 DEMO</p>
            </div>
          </NavLink>
        </div>

        <div className="px-4 py-4">
          <NavLink
            to="/"
            onClick={handleCreateNewChat}
            className={({ isActive }) =>
              `mb-2 flex w-full items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`
            }
          >
            <MessageCirclePlus className="h-4 w-4" />
            新对话
          </NavLink>
          <NavLink
            to="/engine"
            className={({ isActive }) =>
              `flex w-full items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`
            }
          >
            <Compass className="h-4 w-4" />
            智学引擎
          </NavLink>
        </div>

        <div className="px-4 pb-2">
          {!isAuthenticated ? (
            <button
              type="button"
              onClick={() => openAuthModal('login', '')}
              className="w-full rounded-xl bg-blue-600 px-3 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
            >
              立即登录
            </button>
          ) : (
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <div className="text-xs text-slate-500">当前用户</div>
              <div className="mt-1 text-sm font-medium text-slate-800">{userDisplayName}</div>
              <button type="button" onClick={handleLogout} className="mt-2 text-xs text-blue-600 hover:text-blue-700">
                退出登录
              </button>
            </div>
          )}
        </div>

        <div className="px-4">
          <label className="flex rounded-xl border border-slate-200 bg-white px-3 py-2">
            <div className="mr-2 flex items-center text-slate-400">
              <Search className="h-3.5 w-3.5" />
            </div>
            <input
              value={historySearch}
              onChange={(event) => setHistorySearch(event.target.value)}
              placeholder="搜索历史对话"
              className="w-full bg-transparent text-xs text-slate-600 outline-none placeholder:text-slate-400"
            />
          </label>
        </div>

        <div className="mt-4 flex-1 overflow-y-auto px-3 pb-4">
          <div className="mb-2 flex items-center gap-2 px-2 text-xs font-medium text-slate-500">
            <History className="h-3.5 w-3.5" />
            最近对话
          </div>
          <div className="space-y-1">
            {filteredConversationHistory.length > 0 ? filteredConversationHistory.map((item) => (
              <button
                key={item.conversationId}
                type="button"
                onClick={() => handleOpenConversation(item)}
                className={`w-full truncate rounded-lg border px-3 py-2 text-left text-sm transition ${
                  item.conversationId === activeConversationId
                    ? 'border-blue-300 bg-blue-50 text-blue-700'
                    : 'border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
                title={item.lastMessagePreview || item.title}
              >
                {item.title}
              </button>
            )) : (
              <div className="rounded-lg px-3 py-2 text-sm text-slate-400">
                {isAuthenticated
                  ? historySearch.trim()
                    ? '没有匹配的历史对话'
                    : '暂无最近对话'
                  : '登录后显示最近对话'}
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-slate-200 px-4 py-3">
          <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Clock3 className="h-3.5 w-3.5" />
              最后同步 {lastSyncAt ? new Date(lastSyncAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '--'}
            </div>
            <button type="button" onClick={() => void loadRecentConversations()} className="text-xs text-blue-600 hover:text-blue-700">
              记录
            </button>
          </div>
        </div>
      </aside>

      <main className="ml-[280px] min-h-screen flex-1">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-200 bg-white/90 px-8 py-3 backdrop-blur">
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <Compass className="h-4 w-4 text-blue-600" />
            {inEngine ? '智学引擎 / 服务选择面板' : '新对话 / 智能辅导链路'}
          </div>
          <div className="flex items-center gap-5 text-xs text-slate-500">
            <span>API 服务已连接</span>
            <span>当前已是最新版本</span>
            <span>反馈通道筹备中</span>
          </div>
        </header>

        <div className="px-8 py-6">
          <motion.div
            key={inEngine ? 'engine-shell' : 'qna-shell'}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="relative"
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
    </div>
  );
}
