export const authService = {
  login: async (username, password) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    if (username === 'admin' && password === 'password') {
      const token = 'mock-jwt-token-12345';
      localStorage.setItem('token', token);
      return { success: true, token };
    }
    
    return { success: false, message: 'Invalid credentials' };
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
};
