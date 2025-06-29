# Error Monitoring & Health Monitoring Configuration

This document describes the configuration options for the enhanced error monitoring and health monitoring features added to the AI Engine Service.

## Environment Variables

The following environment variables can be set to configure centralized error reporting and issue tracking:

### Required for Basic Operation
```bash
# HuggingFace API Token (required for AI model access)
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

### Optional for Centralized Error Monitoring
```bash
# Centralized Error Monitoring System (e.g., DataDog, New Relic, custom endpoint)
ERROR_MONITORING_URL=https://your-monitoring-system.com/api/events
ERROR_MONITORING_TOKEN=your_monitoring_token_here

# Issue Tracker Integration (e.g., GitHub Issues, Jira, etc.)
ISSUE_TRACKER_URL=https://api.github.com/repos/your-org/your-repo/issues
ISSUE_TRACKER_TOKEN=your_github_token_here
```

## Enhanced Health Endpoint

The `/health` endpoint now provides comprehensive health checking including:

### Components Monitored
- **AIEngine Status**: Verifies the AI engine is properly initialized
- **HuggingFace API Connectivity**: Tests API connectivity and authentication
- **Model Availability**: Checks that AI models are accessible

### Response Format
```json
{
  "status": "healthy|degraded|unhealthy",
  "service": "ai-engine",
  "timestamp": "2024-01-01T12:00:00Z",
  "components": {
    "ai_engine": {
      "status": "healthy|unhealthy",
      "message": "Status description"
    },
    "huggingface_api": {
      "status": "healthy|degraded|unhealthy",
      "message": "API status description",
      "response_time_ms": 150
    },
    "models": {
      "status": "healthy|unhealthy",
      "available_count": 2,
      "message": "Model availability status"
    }
  }
}
```

## Error Monitoring Endpoint

New `/monitoring/errors` endpoint provides detailed error tracking:

### Features
- **Error Summary**: Total counts by error type and model
- **Recent Error History**: Last 10 errors with full context
- **Health Indicators**: Service health assessment based on error patterns
- **Actionable Recommendations**: Suggested actions based on error patterns

### Response Format
```json
{
  "error_summary": {
    "total_errors": 5,
    "error_counts": {
      "RATE_LIMIT:google/flan-t5-base": 3,
      "NETWORK_ERROR:facebook/bart-large-mnli": 2
    },
    "recent_errors": [...]
  },
  "health_indicators": {
    "error_rate": "low|medium|high",
    "most_frequent_error": "RATE_LIMIT",
    "recommendations": ["Consider implementing rate limiting"],
    "total_error_count": 5,
    "unique_error_types": 2
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Error Types Tracked

The system tracks and categorizes the following error types:

### HuggingFace API Errors
- **AUTH_ERROR**: Authentication or API token issues
- **RATE_LIMIT**: API rate limiting (HTTP 429)
- **SERVICE_UNAVAILABLE**: HF service temporarily unavailable (HTTP 503)
- **QUOTA_EXCEEDED**: API quota or billing issues (HTTP 402)
- **HTTP_ERROR**: Other HTTP errors from HuggingFace API
- **NETWORK_ERROR**: Network connectivity issues
- **UNKNOWN_ERROR**: Unexpected errors not matching other categories

## Centralized Error Reporting

When configured, the system automatically sends error events to:

### Monitoring System Integration
- Sends real-time error events to configured monitoring URL
- Includes full error context and metadata
- Supports Bearer token authentication

### Issue Tracker Integration
- Automatically creates issues for critical or repeated errors
- Triggers on:
  - 5+ occurrences of the same error type/model combination
  - Critical error types (AUTH_ERROR, QUOTA_EXCEEDED)
- Includes error history and context in issue body
- Supports GitHub Issues API format

## Example Configuration

### Docker Environment
```bash
# .env file
HUGGINGFACE_API_TOKEN=hf_your_token_here
ERROR_MONITORING_URL=https://api.datadoghq.com/api/v1/events
ERROR_MONITORING_TOKEN=your_datadog_api_key
ISSUE_TRACKER_URL=https://api.github.com/repos/myorg/ai-engine-issues/issues
ISSUE_TRACKER_TOKEN=ghp_your_github_token
```

### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-engine-config
data:
  ERROR_MONITORING_URL: "https://your-monitoring-system.com/api/events"
  ISSUE_TRACKER_URL: "https://api.github.com/repos/myorg/ai-engine-issues/issues"
```

## Monitoring Best Practices

### Health Check Integration
- Use `/health` endpoint for load balancer health checks
- Monitor component-level status for detailed diagnostics
- Set up alerts based on overall status changes

### Error Monitoring Integration
- Poll `/monitoring/errors` endpoint for error trend analysis
- Set up alerts for high error rates or critical error types
- Use recommendations for proactive issue resolution

### Logging Integration
- All errors are logged with structured format
- Use log aggregation systems (ELK, Splunk) for analysis
- Correlate logs with monitoring data for root cause analysis

## Security Considerations

- Store API tokens and credentials securely (e.g., Kubernetes secrets)
- Use least-privilege access for monitoring and issue tracker tokens
- Regularly rotate authentication tokens
- Monitor access to error monitoring endpoints
