/**
 * React Query hooks for CloudViz API
 */

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import {
  LoginRequest,
  ExtractionRequest,
  RenderRequest,
  ResourceFilters,
} from '../types/api';

// Query keys
export const queryKeys = {
  health: ['health'],
  providers: ['providers'],
  user: ['user'],
  costSummary: (filters?: ResourceFilters) => ['cost-summary', filters],
  extractionJob: (jobId: string) => ['extraction-job', jobId],
  renderJob: (jobId: string) => ['render-job', jobId],
  inventory: (jobId: string) => ['inventory', jobId],
  diagram: (jobId: string) => ['diagram', jobId],
};

// Health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3,
  });
};

// Authentication hooks
export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (credentials: LoginRequest) => apiClient.login(credentials),
    onSuccess: () => {
      // Invalidate and refetch user data
      queryClient.invalidateQueries({ queryKey: queryKeys.user });
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => apiClient.logout(),
    onSuccess: () => {
      // Clear all queries on logout
      queryClient.clear();
    },
  });
};

export const useValidateToken = () => {
  return useQuery({
    queryKey: queryKeys.user,
    queryFn: () => apiClient.validateToken(),
    enabled: apiClient.isAuthenticated(),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Provider hooks
export const useProviders = () => {
  return useQuery({
    queryKey: queryKeys.providers,
    queryFn: () => apiClient.getProviders(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Resource extraction hooks
export const useStartExtraction = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: ExtractionRequest) => apiClient.startExtraction(request),
    onSuccess: (data) => {
      // Start polling the job
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.extractionJob(data.job_id) 
      });
    },
  });
};

export const useExtractionJob = (jobId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.extractionJob(jobId),
    queryFn: () => apiClient.getExtractionJob(jobId),
    enabled: enabled && !!jobId,
    refetchInterval: (query) => {
      // Stop polling when job is completed or failed
      const data = query.state.data;
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });
};

export const useInventory = (jobId: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: queryKeys.inventory(jobId),
    queryFn: () => apiClient.getInventory(jobId),
    enabled: enabled && !!jobId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Visualization hooks
export const useRenderDiagram = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: RenderRequest) => apiClient.renderDiagram(request),
    onSuccess: (data) => {
      // Start polling the render job
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.renderJob(data.job_id) 
      });
    },
  });
};

export const useRenderJob = (jobId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.renderJob(jobId),
    queryFn: () => apiClient.getRenderJob(jobId),
    enabled: enabled && !!jobId,
    refetchInterval: (query) => {
      // Stop polling when job is completed or failed
      const data = query.state.data;
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });
};

export const useDiagram = (jobId: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: queryKeys.diagram(jobId),
    queryFn: () => apiClient.getDiagram(jobId),
    enabled: enabled && !!jobId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useDownloadDiagram = () => {
  return useMutation({
    mutationFn: ({ jobId, format }: { jobId: string; format: string }) =>
      apiClient.downloadDiagram(jobId, format),
    onSuccess: (blob, variables) => {
      // Auto-download the file
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `diagram-${variables.jobId}.${variables.format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
  });
};

// Cost analytics hooks
export const useCostSummary = (filters?: ResourceFilters) => {
  return useQuery({
    queryKey: queryKeys.costSummary(filters),
    queryFn: () => apiClient.getCostSummary(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useResourceCosts = () => {
  return useMutation({
    mutationFn: (resourceIds: string[]) => apiClient.getResourceCosts(resourceIds),
  });
};

// Compliance hooks
export const useComplianceReport = () => {
  return useMutation({
    mutationFn: (resourceIds?: string[]) => apiClient.getComplianceReport(resourceIds),
  });
};

// Custom hooks for complex workflows
export const useExtractionWorkflow = () => {
  const startExtraction = useStartExtraction();
  
  const extractAndPoll = async (request: ExtractionRequest) => {
    try {
      const response = await startExtraction.mutateAsync(request);
      
      // Poll until completion
      const finalJob = await apiClient.pollJob(response.job_id, false);
      
      if (finalJob.status === 'completed') {
        const inventory = await apiClient.getInventory(response.job_id);
        return { job: finalJob, inventory };
      } else {
        throw new Error(finalJob.error || 'Extraction failed');
      }
    } catch (error) {
      throw error;
    }
  };
  
  return {
    extractAndPoll,
    isLoading: startExtraction.isPending,
    error: startExtraction.error,
  };
};

export const useVisualizationWorkflow = () => {
  const renderDiagram = useRenderDiagram();
  
  const renderAndPoll = async (request: RenderRequest) => {
    try {
      const response = await renderDiagram.mutateAsync(request);
      
      // Poll until completion
      const finalJob = await apiClient.pollJob(response.job_id, true);
      
      if (finalJob.status === 'completed') {
        const diagram = await apiClient.getDiagram(response.job_id);
        return { job: finalJob, diagram };
      } else {
        throw new Error(finalJob.error || 'Rendering failed');
      }
    } catch (error) {
      throw error;
    }
  };
  
  return {
    renderAndPoll,
    isLoading: renderDiagram.isPending,
    error: renderDiagram.error,
  };
};

// WebSocket hook for real-time updates
export const useJobWebSocket = (jobId: string, enabled: boolean = false) => {
  const queryClient = useQueryClient();
  
  React.useEffect(() => {
    if (!enabled || !jobId) return;
    
    const ws = apiClient.createWebSocket(jobId);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Update the job query with real-time data
      if (data.type === 'extraction_update') {
        queryClient.setQueryData(queryKeys.extractionJob(jobId), data.job);
      } else if (data.type === 'render_update') {
        queryClient.setQueryData(queryKeys.renderJob(jobId), data.job);
      }
    };
    
    return () => {
      ws.close();
    };
  }, [jobId, enabled, queryClient]);
};