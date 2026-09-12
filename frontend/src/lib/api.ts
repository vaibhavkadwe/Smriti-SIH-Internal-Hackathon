import axios from 'axios';
import { API_V1 } from '../config';

/**
 * Module-level token ref — the request interceptor reads it live, so a retry
 * after refresh always carries the NEW token (no stale-closure race).
 * AuthContext owns the value; tokens still never touch localStorage.
 */
let authToken: string | null = null;
export function setAuthToken(token: string | null) {
  authToken = token;
}

/**
 * Axios instance for all /api/v1 calls.
 * 401 → dispatch 'auth:unauthorized' (AuthContext refreshes once) → retry the
 * original request with the fresh token; if refresh fails, reject to caller.
 */
export const api = axios.create({
  baseURL: API_V1,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const isRefreshCall = typeof original?.url === 'string' && original.url.includes('/auth/refresh');
    if (error.response?.status === 401 && !original._retried && !isRefreshCall) {
      original._retried = true;
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      return new Promise((resolve, reject) => {
        const handler = (e: Event) => {
          const custom = e as CustomEvent<{ resolved: boolean }>;
          window.removeEventListener('auth:refreshed', handler);
          if (custom.detail?.resolved) {
            resolve(api(original));
          } else {
            reject(error);
          }
        };
        window.addEventListener('auth:refreshed', handler);
      });
    }
    return Promise.reject(error);
  }
);
