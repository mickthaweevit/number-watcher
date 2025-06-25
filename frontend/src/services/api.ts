import axios from 'axios';
import type { Game, Result } from '../types';

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

  clearData: async () => {
    const response = await api.delete('/clear-data');
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;