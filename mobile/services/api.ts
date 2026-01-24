import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

const DEFAULT_BASE_URL = 'http://10.0.2.2:8000'; // Android emulator localhost

const api = axios.create({
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(async (config) => {
  const storedUrl = await AsyncStorage.getItem('api_base_url');
  config.baseURL = storedUrl || DEFAULT_BASE_URL;
  return config;
});

export const apiService = {
  // Dashboard
  getDashboard: () => api.get('/api/dashboard'),

  // Tasks
  getTasks: (folder: string = 'Pending_Approval', limit = 20) =>
    api.get('/api/tasks', { params: { folder, limit } }),

  getPendingTasks: (limit = 20) =>
    api.get('/api/tasks/pending', { params: { limit } }),

  getTask: (id: string) => api.get(`/api/tasks/${id}`),

  approveTask: (id: string, note?: string) =>
    api.post(`/api/tasks/${id}/approve`, { approved: true, note }),

  rejectTask: (id: string, note?: string) =>
    api.post(`/api/tasks/${id}/approve`, { approved: false, note }),

  // Chat
  sendChatMessage: (message: string, context?: Record<string, any>) =>
    api.post('/api/chat/send', { message, context }),

  getChatHistory: (limit = 50) =>
    api.get('/api/chat/history', { params: { limit } }),

  // Activity
  getRecentActivity: (limit = 10) =>
    api.get('/api/activity', { params: { limit } }),

  // Notifications
  registerPush: (token: string, deviceName: string) =>
    api.post('/api/notifications/subscribe', {
      fcm_token: token,
      device_name: deviceName,
      platform: Platform.OS,
    }),

  // Health
  health: () => api.get('/api/health'),

  // Settings
  setBaseUrl: async (url: string) => {
    await AsyncStorage.setItem('api_base_url', url);
  },

  getBaseUrl: async () => {
    return (await AsyncStorage.getItem('api_base_url')) || DEFAULT_BASE_URL;
  }
};
