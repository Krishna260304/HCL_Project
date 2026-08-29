import React, { createContext, useContext, useEffect, useReducer, useCallback } from 'react';
import { authService, type AuthUser } from '@/services/authService';
import { wsManager } from '@/services/websocket/WebSocketManager';

// ─── State ────────────────────────────────────────────────────────────────────

type ConnectionStatus = 'connected' | 'disconnected' | 'reconnecting';

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  connectionStatus: ConnectionStatus;
}

type AuthAction =
  | { type: 'SET_USER'; user: AuthUser }
  | { type: 'CLEAR_USER' }
  | { type: 'SET_LOADING'; loading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'SET_CONNECTION'; status: ConnectionStatus };

function reducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.user, loading: false, error: null };
    case 'CLEAR_USER':
      return { ...state, user: null, loading: false, error: null };
    case 'SET_LOADING':
      return { ...state, loading: action.loading };
    case 'SET_ERROR':
      return { ...state, error: action.error, loading: false };
    case 'SET_CONNECTION':
      return { ...state, connectionStatus: action.status };
    default:
      return state;
  }
}

const initialState: AuthState = {
  user: null,
  loading: true,
  error: null,
  connectionStatus: 'disconnected',
};

// ─── Context ──────────────────────────────────────────────────────────────────

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (payload: {
    email: string;
    password: string;
    name: string;
  }) => Promise<AuthUser>;
  logout: () => Promise<void>;
  isAdmin: boolean;
  isLearner: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // ── Restore session on mount ──────────────────────────────────────────────
  useEffect(() => {
    const session = authService.restoreSession();
    if (session) {
      dispatch({ type: 'SET_USER', user: session.user });
    } else {
      dispatch({ type: 'SET_LOADING', loading: false });
    }
  }, []);

  // ── Monitor WebSocket connection status ───────────────────────────────────
  useEffect(() => {
    const unsub = wsManager.onConnectionChange((status) => {
      dispatch({ type: 'SET_CONNECTION', status });

      // On reconnect, if user is logged in, re-authenticate
      if (status === 'connected' && state.user) {
        const token = localStorage.getItem('lp_access');
        if (token) wsManager.updateToken(token);
      }
    });
    return unsub;
  }, [state.user]);

  // ── Actions ───────────────────────────────────────────────────────────────

  const login = useCallback(async (email: string, password: string): Promise<AuthUser> => {
    dispatch({ type: 'SET_LOADING', loading: true });
    dispatch({ type: 'SET_ERROR', error: null });
    try {
      const data = await authService.login(email, password);
      dispatch({ type: 'SET_USER', user: data.user });
      return data.user;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Login failed';
      dispatch({ type: 'SET_ERROR', error: msg });
      throw err;
    }
  }, []);

  const register = useCallback(
    async (payload: { email: string; password: string; name: string }): Promise<AuthUser> => {
      dispatch({ type: 'SET_LOADING', loading: true });
      dispatch({ type: 'SET_ERROR', error: null });
      try {
        const data = await authService.register(payload);
        dispatch({ type: 'SET_USER', user: data.user });
        return data.user;
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Registration failed';
        dispatch({ type: 'SET_ERROR', error: msg });
        throw err;
      }
    },
    [],
  );

  const logout = useCallback(async (): Promise<void> => {
    dispatch({ type: 'SET_LOADING', loading: true });
    await authService.logout();
    dispatch({ type: 'CLEAR_USER' });
  }, []);

  const value: AuthContextValue = {
    ...state,
    login,
    register,
    logout,
    isAdmin: state.user?.role === 'admin',
    isLearner: state.user?.role === 'learner',
    isAuthenticated: Boolean(state.user),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
