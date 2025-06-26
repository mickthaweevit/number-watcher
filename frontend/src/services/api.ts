import axios from 'axios';
import type { Game, Result } from '../types';

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

export const gameApi = {
  getAllGames: async (): Promise<Game[]> => {
    const response = await api.get('/games');
    return response.data;
  },

  getAllResults: async (): Promise<Result[]> => {
    const response = await api.get('/results');
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
  getSchedulerStatus: async () => {
    const response = await api.get('/scheduler/status');
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
  }
};

export default api;