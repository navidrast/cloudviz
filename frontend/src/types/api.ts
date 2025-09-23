/**
 * TypeScript type definitions for CloudViz API
 */

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_info: UserInfo;
}

export interface UserInfo {
  username: string;
  email: string;
  roles: string[];
  permissions: string[];
}

// Cloud provider types
export enum CloudProvider {
  AZURE = 'azure',
  AWS = 'aws',
  GCP = 'gcp'
}

export enum ExtractionScope {
  SUBSCRIPTION = 'subscription',
  RESOURCE_GROUP = 'resource_group',
  REGION = 'region'
}

// Resource extraction types
export interface ExtractionRequest {
  provider: CloudProvider;
  scope: ExtractionScope;
  scope_identifier: string;
  filters?: {
    resource_types?: string[];
    regions?: string[];
    tags?: Record<string, string>;
  };
  include_relationships?: boolean;
  resource_types?: string[];
  regions?: string[];
  tags?: Record<string, string>;
}

export interface ExtractionResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  estimated_duration_seconds?: number;
  result_url?: string;
}

export enum JobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  progress: number;
  result?: any;
  error?: string;
  created_at: string;
  updated_at: string;
}

// Resource inventory types
export interface ResourceInventory {
  resources: CloudResource[];
  relationships: ResourceRelationship[];
  metadata: InventoryMetadata;
}

export interface CloudResource {
  id: string;
  name: string;
  type: string;
  provider: CloudProvider;
  region: string;
  resource_group?: string;
  subscription?: string;
  project?: string;
  tags: Record<string, string>;
  properties: Record<string, any>;
  cost?: ResourceCost;
  compliance?: ComplianceStatus;
}

export interface ResourceRelationship {
  source_id: string;
  target_id: string;
  relationship_type: string;
  properties?: Record<string, any>;
}

export interface InventoryMetadata {
  extraction_time: string;
  resource_count: number;
  relationship_count: number;
  providers: CloudProvider[];
  regions: string[];
  total_cost?: number;
}

// Visualization types
export enum OutputFormat {
  MERMAID = 'mermaid',
  GRAPHVIZ = 'graphviz',
  PNG = 'png',
  SVG = 'svg',
  PDF = 'pdf'
}

export enum ThemeName {
  PROFESSIONAL = 'professional',
  DARK = 'dark',
  LIGHT = 'light',
  MINIMAL = 'minimal'
}

export enum LayoutAlgorithm {
  HIERARCHICAL = 'hierarchical',
  CIRCULAR = 'circular',
  FORCE_DIRECTED = 'force_directed',
  TREE = 'tree'
}

export interface RenderRequest {
  inventory: ResourceInventory;
  format?: OutputFormat;
  theme?: ThemeName;
  layout?: LayoutAlgorithm;
  options?: RenderOptions;
}

export interface RenderOptions {
  width?: number;
  height?: number;
  dpi?: number;
  background_color?: string;
  include_legend?: boolean;
  group_by?: string;
}

export interface RenderResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  result_url?: string;
}

export interface DiagramResponse {
  content: string;
  format: OutputFormat;
  metadata: {
    width: number;
    height: number;
    created_at: string;
  };
}

// Cost analytics types
export interface ResourceCost {
  monthly_cost: number;
  currency: string;
  cost_breakdown?: Record<string, number>;
}

export interface CostSummary {
  total_monthly_cost: number;
  providers: Record<CloudProvider, ProviderCostSummary>;
  cost_breakdown: Record<string, number>;
}

export interface ProviderCostSummary {
  cost: number;
  resources: number;
  regions: number;
}

// Compliance types
export interface ComplianceStatus {
  compliant: boolean;
  violations: ComplianceViolation[];
  score: number;
}

export interface ComplianceViolation {
  rule: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  remediation?: string;
}

// Filter types
export interface ResourceFilters {
  providers: CloudProvider[];
  resource_types: string[];
  regions: string[];
  tags: Record<string, string>;
  environments: string[];
  date_range?: {
    start: string;
    end: string;
  };
}

// API response wrapper
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Error types
export interface ApiError {
  detail: string;
  status: number;
  type?: string;
}

// Provider configuration
export interface ProviderConfig {
  name: CloudProvider;
  display_name: string;
  supported: boolean;
  configured: boolean;
  features: string[];
  supported_scopes: string[];
  supported_resource_types: string[];
  authentication_methods: string[];
  regions: string[];
}

export interface ProvidersResponse {
  providers: ProviderConfig[];
}