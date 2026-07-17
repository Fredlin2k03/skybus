/**
 * API Service - Centralized HTTP client for all backend communication.
 * Uses axios with interceptors for auth token injection.
 */

import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - inject auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('skybus_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Something went wrong';
    
    if (error.response?.status === 401) {
      localStorage.removeItem('skybus_token');
      localStorage.removeItem('skybus_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      toast.error('Access denied');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    
    return Promise.reject({ message, status: error.response?.status });
  }
);

// ===== AUTH API =====
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data),
};

// ===== ROUTES & SEARCH API =====
export const routesAPI = {
  searchCities: (query) => api.get(`/routes/cities?q=${encodeURIComponent(query)}`),
  searchBuses: (params) => api.get('/routes/search', { params }),
  getPopularRoutes: () => api.get('/routes/popular'),
  getScheduleStops: (scheduleId) => api.get(`/routes/schedule/${scheduleId}/stops`),
};

// ===== BUSES API =====
export const busesAPI = {
  getSeatLayout: (scheduleId, date) => api.get(`/buses/${scheduleId}/seats?date=${date}`),
  trackBus: (busId) => api.get(`/buses/${busId}/track`),
  getBusTypes: () => api.get('/buses/types'),
};

// ===== BOOKINGS API =====
export const bookingsAPI = {
  create: (data) => api.post('/bookings/', data),
  getMyBookings: (params) => api.get('/bookings/my-bookings', { params }),
  getBooking: (bookingId) => api.get(`/bookings/${bookingId}`),
  cancel: (bookingId, data) => api.post(`/bookings/${bookingId}/cancel`, data),
};

// ===== PAYMENTS API =====
export const paymentsAPI = {
  createOrder: (data) => api.post('/payments/create-order', data),
  verify: (data) => api.post('/payments/verify', data),
  simulateSuccess: (data) => api.post('/payments/simulate-success', data),
  getStatus: (bookingId) => api.get(`/payments/${bookingId}/status`),
};

// ===== USERS API =====
export const usersAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (data) => api.put('/users/profile', data),
  getBookingStats: () => api.get('/users/booking-stats'),
};

// ===== ADMIN API =====
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getBookings: (params) => api.get('/admin/bookings', { params }),
  getRevenue: (period) => api.get(`/admin/revenue?period=${period}`),
  getUsers: (params) => api.get('/admin/users', { params }),
  getCoupons: () => api.get('/admin/coupons'),
  createCoupon: (data) => api.post('/admin/coupons', data),
  toggleCoupon: (id) => api.put(`/admin/coupons/${id}/toggle`),
};

// ===== COUPONS API =====
export const couponsAPI = {
  validate: (code, amount, routeId) => 
    api.post(`/coupons/validate?code=${code}&amount=${amount}${routeId ? `&route_id=${routeId}` : ''}`),
};

export default api;
