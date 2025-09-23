/**
 * CloudViz API Client
 * Handles all API communication with the FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';
import {
  LoginRequest,
  LoginResponse,
  ExtractionRequest,
  ExtractionResponse,
  RenderRequest,
  RenderResponse,
  JobResponse,
  ResourceInventory,
  DiagramResponse,
  CostSummary,
  ProvidersResponse,
  ApiError,
  ResourceFilters
} from '../types/api';

class CloudVizApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          // Redirect to login or emit auth error event
          window.dispatchEvent(new CustomEvent('auth-error'));
        }
        return Promise.reject(this.handleApiError(error));
      }
    );

    // Load token from localStorage
    this.loadToken();
  }

  private handleApiError(error: any): ApiError {
    if (error.response) {
      return {
        detail: error.response.data?.detail || error.response.statusText,
        status: error.response.status,
        type: error.response.data?.type,
      };
    } else if (error.request) {
      return {
        detail: 'Network error - unable to reach the server',
        status: 0,
      };
    } else {
      return {
        detail: error.message || 'Unknown error occurred',
        status: 0,
      };
    }
  }

  // Token management
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('cloudviz_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('cloudviz_token');
  }

  private loadToken() {
    const token = localStorage.getItem('cloudviz_token');
    if (token) {
      this.token = token;
    }
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/auth/login', credentials);
    this.setToken(response.data.access_token);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearToken();
    }
  }

  async validateToken(): Promise<any> {
    const response = await this.client.get('/auth/validate');
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Provider endpoints
  async getProviders(): Promise<ProvidersResponse> {
    const response = await this.client.get<ProvidersResponse>('/api/v1/providers');
    return response.data;
  }

  // Resource extraction endpoints
  async startExtraction(request: ExtractionRequest): Promise<ExtractionResponse> {
    const response = await this.client.post<ExtractionResponse>('/api/v1/extract', request);
    return response.data;
  }

  async getExtractionJob(jobId: string): Promise<JobResponse> {
    const response = await this.client.get<JobResponse>(`/api/v1/jobs/${jobId}`);
    return response.data;
  }

  async getInventory(jobId: string): Promise<ResourceInventory> {
    const response = await this.client.get<ResourceInventory>(`/api/v1/jobs/${jobId}/result`);
    return response.data;
  }

  // Visualization endpoints
  async renderDiagram(request: RenderRequest): Promise<RenderResponse> {
    const response = await this.client.post<RenderResponse>('/api/v1/render', request);
    return response.data;
  }

  async getRenderJob(jobId: string): Promise<JobResponse> {
    const response = await this.client.get<JobResponse>(`/api/v1/render/jobs/${jobId}`);
    return response.data;
  }

  async getDiagram(jobId: string): Promise<DiagramResponse> {
    const response = await this.client.get<DiagramResponse>(`/api/v1/render/jobs/${jobId}/result`);
    return response.data;
  }

  async downloadDiagram(jobId: string, format: string): Promise<Blob> {
    const response = await this.client.get(`/api/v1/render/jobs/${jobId}/download`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  // Cost analytics endpoints
  async getCostSummary(filters?: ResourceFilters): Promise<CostSummary> {
    const response = await this.client.get<CostSummary>('/api/v1/costs/summary', {
      params: filters,
    });
    return response.data;
  }

  async getResourceCosts(resourceIds: string[]): Promise<any> {
    const response = await this.client.post('/api/v1/costs/resources', {
      resource_ids: resourceIds,
    });
    return response.data;
  }

  // Compliance endpoints
  async getComplianceReport(resourceIds?: string[]): Promise<any> {
    const response = await this.client.post('/api/v1/compliance/report', {
      resource_ids: resourceIds,
    });
    return response.data;
  }

  // Utility methods for polling jobs
  async pollJob(jobId: string, isRenderJob: boolean = false): Promise<JobResponse> {
    const endpoint = isRenderJob ? this.getRenderJob.bind(this) : this.getExtractionJob.bind(this);
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const job = await endpoint(jobId);
          
          if (job.status === 'completed' || job.status === 'failed') {
            resolve(job);
          } else {
            setTimeout(poll, 2000); // Poll every 2 seconds
          }
        } catch (error) {
          reject(error);
        }
      };
      
      poll();
    });
  }

  // WebSocket connection for real-time updates
  createWebSocket(jobId: string): WebSocket {
    const wsUrl = this.client.defaults.baseURL?.replace('http', 'ws') || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/ws/jobs/${jobId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected for job:', jobId);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return ws;
  }
}

// Export singleton instance
export const apiClient = new CloudVizApiClient();
export default CloudVizApiClient;