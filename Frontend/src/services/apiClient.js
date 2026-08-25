import axios from 'axios';

/**
 * Base URL is inlined by Vite at build time. It defaults to `/api`, which is
 * what the bundled nginx proxies to the backend — same origin, so no CORS.
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const TOKEN_KEY = 'inventoryx.token';

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
});

apiClient.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/**
 * Listeners are notified when the server rejects our token, so the React tree
 * can route to /login through the router.
 *
 * The previous client did `window.location.href = '/login'`, which triggers a
 * full page reload and discards any unsaved form state.
 */
const unauthorizedListeners = new Set();
export function onUnauthorized(fn) {
  unauthorizedListeners.add(fn);
  return () => unauthorizedListeners.delete(fn);
}

/** Turn any axios failure into a single readable sentence. */
export function errorMessage(error, fallback = 'Something went wrong.') {
  if (axios.isCancel?.(error)) return 'Request cancelled.';
  if (error?.code === 'ECONNABORTED') return 'The server took too long to respond.';
  if (!error?.response) return 'Cannot reach the server. Check your connection.';

  const { status, data } = error.response;
  if (status === 401) return 'Your session has expired. Please sign in again.';
  if (status === 403) return data?.detail || 'You do not have permission to do that.';
  if (status === 429) return data?.detail || 'Too many attempts. Please wait and try again.';

  // FastAPI validation errors arrive as a list of {field, message}.
  if (Array.isArray(data?.errors) && data.errors.length) {
    return data.errors.map((e) => `${e.field}: ${e.message}`).join('; ');
  }
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail)) {
    return data.detail.map((d) => d.msg || String(d)).join('; ');
  }
  return fallback;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only a rejected token should sign the user out. A 401 from the login form
    // itself just means the password was wrong.
    const isLoginAttempt = error?.config?.url?.includes('/auth/login');
    if (error?.response?.status === 401 && !isLoginAttempt) {
      tokenStore.clear();
      unauthorizedListeners.forEach((fn) => fn());
    }
    return Promise.reject(error);
  },
);

export default apiClient;
