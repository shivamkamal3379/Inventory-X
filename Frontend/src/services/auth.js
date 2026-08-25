import apiClient, { tokenStore } from './apiClient';

function decodeExpiry(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return typeof payload.exp === 'number' ? payload.exp * 1000 : null;
  } catch {
    return null;
  }
}

export const authService = {
  async login(username, password) {
    // The token endpoint follows the OAuth2 password flow, which is
    // form-encoded rather than JSON.
    const params = new URLSearchParams({ username, password });
    const { data } = await apiClient.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    tokenStore.set(data.access_token);
    return data;
  },

  logout() {
    tokenStore.clear();
  },

  async me() {
    const { data } = await apiClient.get('/auth/me');
    return data;
  },

  async changePassword(currentPassword, newPassword) {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  /**
   * Checks the token is present *and* unexpired.
   *
   * The old guard only checked that a string existed in localStorage, so an
   * expired session rendered the whole dashboard before every request failed
   * with 401 and bounced the user out.
   */
  isAuthenticated() {
    const token = tokenStore.get();
    if (!token) return false;
    const expiry = decodeExpiry(token);
    if (expiry === null) return true; // unparseable: let the server decide
    if (expiry <= Date.now()) {
      tokenStore.clear();
      return false;
    }
    return true;
  },
};
