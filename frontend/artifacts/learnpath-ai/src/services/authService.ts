import { wsManager } from './websocket/WebSocketManager';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in?: number;
}

export interface AuthUser {
  id: string;
  email: string;
  role: 'learner' | 'admin';
  status: string;
  profile_id?: string | null;
}

export interface AuthResponse {
  user: AuthUser;
  tokens: AuthTokens;
}

// ─── Token storage helpers ────────────────────────────────────────────────────
// We store tokens in sessionStorage (per tab) + localStorage for "remember me".
// Never expose to other origins via postMessage.

const ACCESS_KEY = 'lp_access';
const REFRESH_KEY = 'lp_refresh';
const USER_KEY = 'lp_user';

export const tokenStorage = {
  set(tokens: AuthTokens, user: AuthUser): void {
    localStorage.setItem(ACCESS_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear(): void {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  },
  getAccess(): string | null {
    return localStorage.getItem(ACCESS_KEY);
  },
  getRefresh(): string | null {
    return localStorage.getItem(REFRESH_KEY);
  },
  getUser(): AuthUser | null {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? (JSON.parse(raw) as AuthUser) : null;
    } catch {
      return null;
    }
  },
};

// ─── AuthService ──────────────────────────────────────────────────────────────

export const authService = {
  async register(payload: {
    email: string;
    password: string;
    name: string;
    current_role?: string;
    experience_level?: string;
    target_outcome?: string;
    age_range?: string;
    country?: string;
    language?: string;
  }): Promise<AuthResponse> {
    const data = await wsManager.request<AuthResponse>('auth.register', payload);
    tokenStorage.set(data.tokens, data.user);
    wsManager.connect(data.tokens.access_token);
    return data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const data = await wsManager.request<AuthResponse>('auth.login', { email, password });
    tokenStorage.set(data.tokens, data.user);
    wsManager.connect(data.tokens.access_token);
    return data;
  },

  async refreshToken(): Promise<{ access_token: string }> {
    const refresh_token = tokenStorage.getRefresh();
    if (!refresh_token) throw new Error('No refresh token available');
    const data = await wsManager.request<{ access_token: string }>('auth.refresh', { refresh_token });
    const user = tokenStorage.getUser();
    if (user) {
      tokenStorage.set(
        {
          access_token: data.access_token,
          refresh_token: refresh_token,
        },
        user,
      );
      wsManager.updateToken(data.access_token);
    }
    return data;
  },

  async logout(): Promise<void> {
    const refresh_token = tokenStorage.getRefresh();
    try {
      await wsManager.request('auth.logout', { refresh_token });
    } catch {
      // Best-effort logout
    }
    tokenStorage.clear();
    wsManager.disconnect();
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await wsManager.request('auth.change_password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  /** Restore session from storage on page load. */
  restoreSession(): { user: AuthUser; token: string } | null {
    const token = tokenStorage.getAccess();
    const user = tokenStorage.getUser();
    if (!token || !user) return null;
    wsManager.connect(token);
    return { user, token };
  },

  getSavedUser(): AuthUser | null {
    return tokenStorage.getUser();
  },
};
