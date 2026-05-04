import { request } from './request';

export interface AuthUser {
  id: number | string;
  userId?: number | string;
  loginId?: string;
  fullName?: string;
  majorCode?: string;
  username?: string;
}

export interface LoginPayload {
  loginId: string;
  password: string;
}

export interface RegisterPayload {
  loginId: string;
  password: string;
  fullName: string;
  majorCode?: string;
}

export interface AuthResponse {
  token?: string;
  user?: AuthUser;
  userId?: number | string;
  id?: number | string;
  loginId?: string;
  fullName?: string;
  majorCode?: string;
}

export const authApi = {
  login(payload: LoginPayload): Promise<AuthResponse> {
    return request.post<AuthResponse>('/api/auth/login', payload);
  },
  register(payload: RegisterPayload): Promise<AuthResponse> {
    return request.post<AuthResponse>('/api/auth/register', payload);
  },
  logout(): Promise<void> {
    return request.post<void>('/api/auth/logout');
  },
  me(): Promise<AuthResponse> {
    return request.get<AuthResponse>('/api/auth/me');
  },
};
