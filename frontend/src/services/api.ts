import axios from 'axios';
import { ChatRequest, ChatResponse, HealthResponse } from '../types/api';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const llmRouterApi = {
  async routeChat(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/route/chat', request);
    return response.data;
  },

  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/healthz');
    return response.data;
  },

  async getMetrics(): Promise<string> {
    const response = await api.get<string>('/metrics');
    return response.data;
  },
};