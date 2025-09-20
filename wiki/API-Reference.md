# CloudViz API Reference

Complete API documentation for the CloudViz multi-cloud infrastructure visualization platform.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs and Versioning](#base-urls-and-versioning)
4. [Common Patterns](#common-patterns)
5. [Health and Status Endpoints](#health-and-status-endpoints)
6. [Authentication Endpoints](#authentication-endpoints)
7. [Resource Extraction Endpoints](#resource-extraction-endpoints)
8. [Visualization Endpoints](#visualization-endpoints)
9. [Job Management Endpoints](#job-management-endpoints)
10. [Provider-Specific Endpoints](#provider-specific-endpoints)
11. [Admin Endpoints](#admin-endpoints)
12. [Error Handling](#error-handling)
13. [Rate Limiting](#rate-limiting)
14. [Webhooks](#webhooks)
15. [SDK Examples](#sdk-examples)

## Overview

The CloudViz API is a RESTful API built with FastAPI that provides programmatic access to cloud infrastructure discovery, visualization, and management capabilities. The API supports JSON request/response format and follows standard HTTP conventions.

### Key Features
- **Multi-cloud support**: AWS, Azure, and Google Cloud Platform
- **Asynchronous operations**: Background job processing for long-running tasks
- **Multiple output formats**: Mermaid, Graphviz, PNG, SVG, PDF
- **Real-time status updates**: WebSocket support for job progress
- **Comprehensive filtering**: Resource type, tag, region, and scope-based filtering
- **Relationship mapping**: Automatic discovery of resource dependencies
- **Caching**: Intelligent caching for improved performance

## Authentication

CloudViz API uses JWT (JSON Web Tokens) for authentication. All API requests (except health check and authentication endpoints) require a valid JWT token in the Authorization header.

### Obtaining a Token

```http
POST /auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-id",
    "username": "your-username",
    "email": "user@example.com",
    "roles": ["user"],
    "permissions": ["extract", "visualize", "view"]
  }
}
```

### Using the Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Token Refresh

```http
POST /auth/refresh
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Base URLs and Versioning

### Base URL
- **Production**: `https://api.cloudviz.com`
- **Development**: `http://localhost:8000`

### API Versioning
- **Current Version**: `v1`
- **Base Path**: `/api/v1`
- **Full URL**: `https://api.cloudviz.com/api/v1`

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`, `image/png`, `image/svg+xml`, `text/plain`

## Common Patterns

### Standard Response Format

```json
{
  "data": {...},
  "metadata": {
    "timestamp": "2023-12-01T10:00:00Z",
    "correlation_id": "req-123456",
    "version": "1.0.0"
  },
  "links": {
    "self": "/api/v1/resource",
    "related": "/api/v1/related-resource"
  }
}
```

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": "Validation error on field 'provider'",
    "correlation_id": "req-123456",
    "timestamp": "2023-12-01T10:00:00Z"
  }
}
```

### Pagination

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "links": {
    "next": "/api/v1/resource?page=2",
    "prev": null,
    "first": "/api/v1/resource?page=1",
    "last": "/api/v1/resource?page=3"
  }
}
```

## Health and Status Endpoints

### Health Check

Get system health status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2023-12-01T10:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5,
      "connections": {
        "active": 2,
        "max": 20
      }
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 1,
      "memory_usage": "45%"
    },
    "providers": {
      "azure": "configured",
      "aws": "not_configured",
      "gcp": "configured"
    }
  },
  "performance": {
    "uptime_seconds": 86400,
    "requests_total": 1500,
    "active_jobs": 3
  }
}
```

### System Metrics

Get detailed system metrics.

```http
GET /health/metrics
Authorization: Bearer <token>
```

**Response:**
```json
{
  "system": {
    "cpu_usage": 25.5,
    "memory_usage": 65.2,
    "disk_usage": 40.1
  },
  "application": {
    "active_connections": 15,
    "cache_hit_rate": 94.5,
    "avg_response_time_ms": 120
  },
  "providers": {
    "azure": {
      "last_check": "2023-12-01T10:00:00Z",
      "status": "healthy",
      "rate_limit_remaining": 95
    }
  }
}
```

## Authentication Endpoints

### User Login

Authenticate user and receive JWT token.

```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh-token-here",
  "user": {
    "id": "user-123",
    "username": "user@example.com",
    "email": "user@example.com",
    "roles": ["user", "admin"],
    "permissions": ["extract", "visualize", "view", "admin"],
    "last_login": "2023-12-01T10:00:00Z"
  }
}
```

### Token Refresh

Refresh an existing JWT token.

```http
POST /auth/refresh
Content-Type: application/json
Authorization: Bearer <refresh-token>

{
  "refresh_token": "refresh-token-here"
}
```

### User Logout

Invalidate current token.

```http
POST /auth/logout
Authorization: Bearer <token>
```

### User Profile

Get current user profile information.

```http
GET /auth/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "user-123",
  "username": "user@example.com",
  "email": "user@example.com",
  "roles": ["user"],
  "permissions": ["extract", "visualize", "view"],
  "created_at": "2023-01-01T00:00:00Z",
  "last_login": "2023-12-01T10:00:00Z",
  "preferences": {
    "default_theme": "professional",
    "default_format": "mermaid",
    "timezone": "UTC"
  }
}
```

## Resource Extraction Endpoints

### Start Resource Extraction

Initiate cloud resource discovery and extraction.

```http
POST /api/v1/extract
Content-Type: application/json
Authorization: Bearer <token>

{
  "provider": "azure",
  "scope": "subscription",
  "scope_identifier": "subscription-id-here",
  "filters": {
    "resource_types": ["virtual_machine", "storage_account", "sql_database"],
    "regions": ["eastus", "westus2"],
    "tags": {
      "Environment": "production",
      "Owner": "team-alpha"
    }
  },
  "include_relationships": true,
  "options": {
    "include_properties": true,
    "include_tags": true,
    "max_resources": 1000
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `provider` | string | Yes | Cloud provider: `azure`, `aws`, `gcp` |
| `scope` | string | Yes | Extraction scope: `subscription`, `resource_group`, `region` |
| `scope_identifier` | string | Yes | Subscription ID, Resource Group name, or Region name |
| `filters` | object | No | Resource filtering options |
| `include_relationships` | boolean | No | Include resource relationships (default: true) |
| `options` | object | No | Additional extraction options |

**Response:**
```json
{
  "job_id": "job-12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "message": "Extraction job started successfully",
  "estimated_duration_seconds": 120,
  "created_at": "2023-12-01T10:00:00Z",
  "links": {
    "status": "/api/v1/jobs/job-12345678-1234-1234-1234-123456789abc",
    "cancel": "/api/v1/jobs/job-12345678-1234-1234-1234-123456789abc/cancel"
  }
}
```

### List Available Providers

Get supported cloud providers and their configuration status.

```http
GET /api/v1/providers
Authorization: Bearer <token>
```

**Response:**
```json
{
  "providers": [
    {
      "name": "azure",
      "display_name": "Microsoft Azure",
      "supported": true,
      "configured": true,
      "features": ["extraction", "visualization", "relationships"],
      "supported_scopes": ["subscription", "resource_group"],
      "supported_resource_types": [
        "virtual_machine",
        "storage_account",
        "sql_database",
        "virtual_network",
        "load_balancer"
      ],
      "authentication_methods": ["service_principal", "managed_identity", "interactive"],
      "regions": ["eastus", "westus2", "northeurope", "westeurope"]
    },
    {
      "name": "aws",
      "display_name": "Amazon Web Services",
      "supported": true,
      "configured": false,
      "features": ["extraction", "visualization"],
      "supported_scopes": ["account", "region"],
      "supported_resource_types": [
        "ec2_instance",
        "s3_bucket",
        "rds_instance",
        "vpc",
        "load_balancer"
      ],
      "authentication_methods": ["access_key", "iam_role", "sso"],
      "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
    },
    {
      "name": "gcp",
      "display_name": "Google Cloud Platform",
      "supported": true,
      "configured": true,
      "features": ["extraction", "visualization"],
      "supported_scopes": ["project"],
      "supported_resource_types": [
        "compute_instance",
        "cloud_storage",
        "cloud_sql",
        "vpc_network",
        "load_balancer"
      ],
      "authentication_methods": ["service_account", "oauth", "adc"],
      "regions": ["us-central1", "us-west1", "europe-west1", "asia-east1"]
    }
  ]
}
```

### Test Provider Authentication

Test authentication with a specific cloud provider.

```http
POST /api/v1/providers/{provider}/test-auth
Authorization: Bearer <token>

{
  "credentials": {
    "tenant_id": "tenant-id",
    "client_id": "client-id",
    "client_secret": "client-secret"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Authentication successful",
  "provider": "azure",
  "account_info": {
    "tenant_id": "tenant-id",
    "subscription_id": "subscription-id",
    "subscription_name": "Production Subscription",
    "available_regions": ["eastus", "westus2"]
  },
  "permissions": {
    "read": true,
    "list": true,
    "describe": true
  }
}
```

## Visualization Endpoints

### Render Infrastructure Diagram

Generate visualization diagrams from resource inventory.

```http
POST /api/v1/render
Content-Type: application/json
Authorization: Bearer <token>

{
  "inventory": {
    "resources": [...],
    "relationships": [...],
    "metadata": {...}
  },
  "format": "mermaid",
  "theme": "professional",
  "layout": "hierarchical",
  "options": {
    "width": 1920,
    "height": 1080,
    "dpi": 300,
    "background_color": "white",
    "include_legend": true,
    "group_by": "resource_type"
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inventory` | object | Yes | Resource inventory data from extraction |
| `format` | string | No | Output format: `mermaid`, `graphviz`, `png`, `svg`, `pdf` |
| `theme` | string | No | Visual theme: `professional`, `dark`, `light`, `minimal`, `colorful` |
| `layout` | string | No | Layout algorithm: `hierarchical`, `force`, `circular`, `grid`, `mindmap` |
| `options` | object | No | Format-specific rendering options |

**Response:**
```json
{
  "job_id": "render-12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "message": "Rendering job started",
  "format": "mermaid",
  "estimated_duration_seconds": 30,
  "created_at": "2023-12-01T10:00:00Z",
  "links": {
    "status": "/api/v1/jobs/render-12345678-1234-1234-1234-123456789abc",
    "result": "/api/v1/render/render-12345678-1234-1234-1234-123456789abc/result"
  }
}
```

### Get Available Themes

List available visualization themes.

```http
GET /api/v1/render/themes
Authorization: Bearer <token>
```

**Response:**
```json
{
  "themes": [
    {
      "name": "professional",
      "display_name": "Professional",
      "description": "Corporate-ready styling with neutral colors",
      "preview_url": "/api/v1/render/themes/professional/preview"
    },
    {
      "name": "dark",
      "display_name": "Dark Mode",
      "description": "Dark theme optimized for development environments",
      "preview_url": "/api/v1/render/themes/dark/preview"
    },
    {
      "name": "colorful",
      "display_name": "Colorful",
      "description": "Provider-specific color coding and rich styling",
      "preview_url": "/api/v1/render/themes/colorful/preview"
    }
  ]
}
```

### Compare Infrastructure States

Generate comparison diagrams between two infrastructure states.

```http
POST /api/v1/render/compare
Content-Type: application/json
Authorization: Bearer <token>

{
  "before_inventory": {...},
  "after_inventory": {...},
  "format": "mermaid",
  "theme": "professional",
  "highlight_changes": true,
  "change_types": ["added", "removed", "modified"],
  "options": {
    "show_unchanged": false,
    "group_changes": true
  }
}
```

**Response:**
```json
{
  "job_id": "compare-12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "changes_detected": {
    "added": 5,
    "removed": 2,
    "modified": 8
  },
  "estimated_duration_seconds": 45
}
```

For complete API documentation with interactive examples, visit the [Swagger UI](http://localhost:8000/docs) when running CloudViz locally.
