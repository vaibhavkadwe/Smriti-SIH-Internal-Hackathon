import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import { api, setAuthToken } from './api';

export type Role = 'patient' | 'family_caregiver' | 'asha_worker' | 'clinician' | 'admin';

interface User {
  id: string;
  phone: string;
  email: string | null;
  role: Role;
  preferred_language: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  consentGiven: boolean;
}

interface AuthContextValue extends AuthState {
  login: (phone: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setConsent: (v: boolean) => void;
  isCaregiver: boolean;
  isPatient: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/** Decode JWT payload without a library — we only need the role claim. */
function decodeRole(token: string): Role | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role as Role;
  } catch {
    return null;
  }
}

function decodeSub(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub as string;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // Tokens in memory ONLY — never localStorage/sessionStorage.
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    consentGiven: false,
  });

  // Keep the module-level token ref in sync — the api interceptor reads it
  // live so post-refresh retries always carry the fresh token.
  useEffect(() => {
    setAuthToken(state.accessToken);
  }, [state.accessToken]);

  // Listen for 401 events from the response interceptor
  useEffect(() => {
    const handler = async () => {
      if (!state.refreshToken) {
        window.dispatchEvent(new CustomEvent('auth:refreshed', { detail: { resolved: false } }));
        setState({ user: null, accessToken: null, refreshToken: null, consentGiven: false });
        window.location.href = '/login';
        return;
      }
      try {
        const { data } = await api.post('/auth/refresh', { refresh_token: state.refreshToken });
        setState((prev) => ({
          ...prev,
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
        }));
        window.dispatchEvent(new CustomEvent('auth:refreshed', { detail: { resolved: true } }));
      } catch {
        window.dispatchEvent(new CustomEvent('auth:refreshed', { detail: { resolved: false } }));
        setState({ user: null, accessToken: null, refreshToken: null, consentGiven: false });
        window.location.href = '/login';
      }
    };
    window.addEventListener('auth:unauthorized', handler);
    return () => { window.removeEventListener('auth:unauthorized', handler); };
  }, [state.refreshToken]);

  const login = useCallback(async (phone: string, password: string) => {
    const { data } = await api.post('/auth/login', { phone, password });
    const role = decodeRole(data.access_token);
    const sub = decodeSub(data.access_token);
    setState({
      user: {
        id: sub || '',
        phone,
        email: null,
        role: role || 'patient',
        preferred_language: 'english',
        is_active: true,
      },
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      consentGiven: false,
    });
  }, []);

  const logout = useCallback(async () => {
    try { await api.post('/auth/logout'); } catch { /* best effort */ }
    setState({ user: null, accessToken: null, refreshToken: null, consentGiven: false });
  }, []);

  const setConsent = useCallback((v: boolean) => {
    setState((prev) => ({ ...prev, consentGiven: v }));
  }, []);

  const role = state.user?.role;
  const isCaregiver = role === 'family_caregiver' || role === 'asha_worker' || role === 'clinician' || role === 'admin';
  const isPatient = role === 'patient';

  return (
    <AuthContext.Provider value={{ ...state, login, logout, setConsent, isCaregiver, isPatient }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

