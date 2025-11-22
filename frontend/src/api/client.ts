import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ExperimentConfig {
  duration: number;
  intensity: 'low' | 'medium' | 'high';
}

export interface StartExperimentRequest {
  scenario: string;
  config?: ExperimentConfig;
}

export interface ExperimentResponse {
  experiment_id: string;
  status: string;
  created_at: string;
}

export interface StatusResponse {
  experiment_id: string;
  status: string;
  progress: number;
  message?: string;
}

export interface ExperimentMetrics {
  cpu_peak: number;
  memory_peak: number;
  error_count: number;
  recovery_time_seconds: number;
  latency_p95?: number;
}

export interface ResultsResponse {
  experiment_id: string;
  summary: string;
  metrics: ExperimentMetrics;
  grafana_url?: string;
  recommendations: string[];
  severity: string;
  raw_logs?: string;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chaosLabAPI = {
  async startExperiment(request: StartExperimentRequest): Promise<ExperimentResponse> {
    const response = await api.post('/api/experiment/start', request);
    return response.data;
  },

  async getStatus(experimentId: string): Promise<StatusResponse> {
    const response = await api.get(`/api/experiment/${experimentId}/status`);
    return response.data;
  },

  async getResults(experimentId: string): Promise<ResultsResponse> {
    const response = await api.get(`/api/experiment/${experimentId}/results`);
    return response.data;
  },

  async healthCheck(): Promise<any> {
    const response = await api.get('/');
    return response.data;
  },
};
