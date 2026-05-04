import { FormEvent, useEffect, useState } from 'react';
import { authApi, type AuthResponse, type AuthUser } from '../api/auth';
import { getErrorMessage, persistAuthSession } from '../api/request';

type AuthTab = 'login' | 'register';

interface AuthModalProps {
  open: boolean;
  defaultTab: AuthTab;
  hint?: string;
  onClose: () => void;
  onSuccess: (user: AuthUser) => void;
}

export default function AuthModal(props: AuthModalProps) {
  const [tab, setTab] = useState<AuthTab>(props.defaultTab);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [majorCode, setMajorCode] = useState('');

  useEffect(() => {
    if (!props.open) {
      return;
    }
    setTab(props.defaultTab);
    setError('');
  }, [props.defaultTab, props.open]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedLoginId = loginId.trim();
    const hasPasswordEdgeWhitespace = password !== password.trim();
    if (!normalizedLoginId || !password.trim()) {
      setError('请填写账号和密码');
      return;
    }
    if (hasPasswordEdgeWhitespace) {
      setError('密码首尾不能包含空格，请确认后重试');
      return;
    }
    if (tab === 'register' && !fullName.trim()) {
      setError('请填写姓名');
      return;
    }
    if (tab === 'register' && password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    setSubmitting(true);
    setError('');
    try {
      const result =
        tab === 'login'
          ? await authApi.login({
              loginId: normalizedLoginId,
              password,
            })
          : await authApi.register({
              loginId: normalizedLoginId,
              password,
              fullName: fullName.trim(),
              majorCode: majorCode.trim() || undefined,
            });

      const user = normalizeUser(result);
      window.localStorage.setItem('auth_user', JSON.stringify(user));
      persistAuthSession({
        token: result.token,
        userId: String(user.id),
      });
      props.onSuccess(user);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (!props.open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/45 px-4">
      <div className="w-full max-w-[420px] rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-base font-semibold text-slate-900">请先登录</h3>
          <button type="button" onClick={props.onClose} className="text-sm text-slate-500 hover:text-slate-700">
            关闭
          </button>
        </div>

        {props.hint ? <div className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">{props.hint}</div> : null}

        <div className="mb-4 grid grid-cols-2 rounded-lg border border-slate-200 bg-slate-50 p-1">
          <button
            type="button"
            onClick={() => setTab('login')}
            className={`rounded-md px-3 py-2 text-sm ${tab === 'login' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600'}`}
          >
            登录
          </button>
          <button
            type="button"
            onClick={() => setTab('register')}
            className={`rounded-md px-3 py-2 text-sm ${tab === 'register' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600'}`}
          >
            注册
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-3">
          <label className="block">
            <div className="mb-1 text-xs text-slate-500">登录账号</div>
            <input
              value={loginId}
              onChange={(e) => setLoginId(e.target.value)}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-400"
              placeholder="请输入登录账号"
            />
          </label>
          <label className="block">
            <div className="mb-1 text-xs text-slate-500">密码</div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-400"
              placeholder="请输入密码"
            />
          </label>

          {tab === 'register' ? (
            <>
              <label className="block">
                <div className="mb-1 text-xs text-slate-500">确认密码</div>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-400"
                  placeholder="请再次输入密码"
                />
              </label>
              <label className="block">
                <div className="mb-1 text-xs text-slate-500">姓名</div>
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-400"
                  placeholder="请输入姓名"
                />
              </label>
              <label className="block">
                <div className="mb-1 text-xs text-slate-500">专业方向（可选）</div>
                <input
                  value={majorCode}
                  onChange={(e) => setMajorCode(e.target.value)}
                  className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-400"
                  placeholder="例如：CS"
                />
              </label>
            </>
          ) : null}

          {error ? <div className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div> : null}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {submitting ? '提交中...' : tab === 'login' ? '登录' : '注册'}
          </button>
        </form>
      </div>
    </div>
  );
}

function normalizeUser(input: AuthResponse): AuthUser {
  if (input.user) {
    const resolvedId = input.user.userId ?? input.user.id ?? input.userId ?? input.id;
    if (resolvedId === undefined || resolvedId === null || String(resolvedId).trim() === '') {
      throw new Error('登录响应缺少用户标识，请稍后重试');
    }
    return {
      id: resolvedId,
      userId: resolvedId,
      loginId: input.user.loginId ?? input.user.username,
      fullName: input.user.fullName ?? input.user.username,
      majorCode: input.user.majorCode,
      username: input.user.username ?? input.user.loginId,
    };
  }
  if (input.userId === undefined && input.id === undefined) {
    throw new Error('登录响应缺少用户标识，请稍后重试');
  }
  const resolvedId = input.userId ?? input.id;
  if (resolvedId === undefined || resolvedId === null) {
    throw new Error('登录响应缺少用户标识，请稍后重试');
  }
  return {
    id: resolvedId,
    userId: resolvedId,
    loginId: input.loginId,
    fullName: input.fullName ?? input.loginId ?? '用户',
    majorCode: input.majorCode,
  };
}
