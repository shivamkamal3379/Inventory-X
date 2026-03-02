import apiClient from './apiClient';

export const authService = {
  login: async (username, password) => {
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await apiClient.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      const data = response.data;
      
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        return { success: true, token: data.access_token };
      }
      return { success: false, message: 'Authentication failed' };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Invalid credentials' 
      };
    }
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
};
