import axios from 'axios';
import type { Game, Result } from '../types';

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  last_login?: string;
}

export interface DashboardProfile {
  id: number;
  user_id: number;
  profile_name: string;
  bet_amount: number;
  selected_patterns: string[];
  selected_game_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface SchedulerStatus {
  is_running: boolean;
  external_api_configured: boolean;
  next_jobs: string[];
  thread_alive: boolean;
}

export interface DateRangeImportResult {
  success: boolean;
  message: string;
  total_dates: number;
  successful_dates: number;
  failed_dates: number;
  total_games_created: number;
  total_results_updated: number;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const gameApi = {
  getAllGames: async (signal?: AbortSignal): Promise<Game[]> => {
    const response = await api.get('/games', { signal });
    return response.data;
  },

  getAllResults: async (signal?: AbortSignal): Promise<Result[]> => {
    const response = await api.get('/results', { signal });
    return response.data;
  },

  importSampleData: async () => {
    const response = await api.post('/import-sample-data');
    return response.data;
  },

  importLiveData: async (date?: string) => {
    const params = date ? { date } : {};
    const response = await api.post('/import-live-data', null, { params });
    return response.data;
  },

  clearData: async () => {
    const response = await api.delete('/clear-data');
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Scheduler endpoints
  getSchedulerStatus: async (signal?: AbortSignal) => {
    const response = await api.get('/scheduler/status', { signal });
    return response.data;
  },

  startScheduler: async () => {
    const response = await api.post('/scheduler/start');
    return response.data;
  },

  stopScheduler: async () => {
    const response = await api.post('/scheduler/stop');
    return response.data;
  },

  triggerManualImport: async () => {
    const response = await api.post('/scheduler/trigger');
    return response.data;
  },

  importDateRange: async (startDate: string, endDate: string) => {
    const response = await api.post('/scheduler/import-range', null, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },

  // Backup endpoints
  exportData: async () => {
    const response = await api.get('/export-data');
    return response.data;
  },

  importBackup: async (backupData: any) => {
    const response = await api.post('/import-backup', backupData);
    return response.data;
  },

  getImportLogs: async (signal?: AbortSignal) => {
    const response = await api.get('/import-logs', { signal });
    return response.data;
  },

  clearImportLogs: async () => {
    const response = await api.delete('/import-logs');
    return response.data;
  }
};

export const authApi = {
  register: async (userData: RegisterData): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (userData: LoginData): Promise<Token> => {
    const response = await api.post('/auth/login', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

export const profileApi = {
  getProfiles: async (): Promise<DashboardProfile[]> => {
    const response = await api.get('/profiles');
    return response.data;
  },

  createProfile: async (profileData: Omit<DashboardProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<DashboardProfile> => {
    const response = await api.post('/profiles', profileData);
    return response.data;
  },

  deleteProfile: async (profileId: number): Promise<{ message: string }> => {
    const response = await api.delete(`/profiles/${profileId}`);
    return response.data;
  }
};

export const adminApi = {
  createInviteCode: async (inviteData: { expires_at: string | null }) => {
    const response = await api.post('/admin/invite-codes', inviteData);
    return response.data;
  },

  getInviteCodes: async () => {
    const response = await api.get('/admin/invite-codes');
    return response.data;
  },

  getUsers: async (): Promise<User[]> => {
    const response = await api.get('/admin/users');
    return response.data;
  }
};

export default api;