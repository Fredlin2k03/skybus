/**
 * Authentication Store - Zustand state management for user auth.
 */

import { create } from 'zustand';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('skybus_user') || 'null'),
  token: localStorage.getItem('skybus_token') || null,
  isAuthenticated: !!localStorage.getItem('skybus_token'),
  loading: false,
  error: null,

  // Register new user
  register: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.register(data);
      const { access_token, user } = response.data;
      
      localStorage.setItem('skybus_token', access_token);
      localStorage.setItem('skybus_user', JSON.stringify(user));
      
      set({ user, token: access_token, isAuthenticated: true, loading: false });
      toast.success(`Welcome to SkyBus, ${user.full_name}!`);
      return true;
    } catch (error) {
      set({ loading: false, error: error.message });
      toast.error(error.message || 'Registration failed');
      return false;
    }
  },

  // Login existing user
  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem('skybus_token', access_token);
      localStorage.setItem('skybus_user', JSON.stringify(user));
      
      set({ user, token: access_token, isAuthenticated: true, loading: false });
      toast.success(`Welcome back, ${user.full_name}!`);
      return true;
    } catch (error) {
      set({ loading: false, error: error.message });
      toast.error(error.message || 'Login failed');
      return false;
    }
  },

  // Logout
  logout: () => {
    localStorage.removeItem('skybus_token');
    localStorage.removeItem('skybus_user');
    set({ user: null, token: null, isAuthenticated: false });
    toast.success('Logged out successfully');
  },

  // Update user in store
  updateUser: (userData) => {
    localStorage.setItem('skybus_user', JSON.stringify(userData));
    set({ user: userData });
  },

  // Check if user is admin
  isAdmin: () => {
    const { user } = get();
    return user?.role === 'admin';
  },
}));

export default useAuthStore;
