# AIEngine Architecture

## Overview

The AIEngine is the core component responsible for orchestrating AI-powered content analysis operations. It provides a unified interface for various analysis types while internally routing requests to appropriate Hugging Face models.

## Public Interface

### AIEngine Class

The `AIEngine` class serves as the primary entry point for all AI analysis operations, providing a clean abstraction over the underlying model infrastructure.

#### Methods

##### `analyze_content(content: str, analysis_type: str, **kwargs) -> AnalysisResult`

**Purpose**: Performs AI-powered analysis on provided content based on the specified analysis type.

**Parameters**:
- `content` (str): The text content to be analyzed
- `analysis_type` (str): The type of analysis to perform (see Analysis Types section)
- `**kwargs`: Additional parameters specific to analysis type

**Returns**: `AnalysisResult` object containing analysis results and metadata

**OpenAPI Mapping**: Maps 1-to-1 to the `/api/v1/analyze` POST operation

##### `get_available_models() -> List[ModelInfo]`

**Purpose**: Retrieves information about all available models and their capabilities.

**Parameters**: None

**Returns**: List of `ModelInfo` objects containing model metadata

**OpenAPI Mapping**: Maps 1-to-1 to the `/api/v1/models` GET operation

## Analysis Types

The AIEngine supports the following analysis types, each optimized for specific use cases:

### Supported Analysis Types

```python
from enum import Enum

class AnalysisType(str, Enum):
    CODE_REVIEW = "code_review"
    REQUIREMENT_EXTRACTION = "requirement_extraction" 
    TECH_RECOMMENDATION = "tech_recommendation"
    RISK_ASSESSMENT = "risk_assessment"
```

#### `code_review`
- **Purpose**: Analyzes source code for quality, security, and best practices
- **Target Models**: Code-specialized models (e.g., CodeBERT, CodeT5)
- **Output**: Code quality metrics, security vulnerabilities, improvement suggestions

#### `requirement_extraction`
- **Purpose**: Extracts structured requirements from natural language documents
- **Target Models**: NLP models optimized for information extraction
- **Output**: Structured requirement objects with categorization

#### `tech_recommendation`
- **Purpose**: Provides technology stack recommendations based on project requirements
- **Target Models**: Domain-specific recommendation models
- **Output**: Ranked technology recommendations with rationale

#### `risk_assessment`
- **Purpose**: Identifies and evaluates potential risks in project specifications
- **Target Models**: Risk analysis and classification models
- **Output**: Risk categories, severity levels, and mitigation strategies

## Internal Architecture

### Model Routing

#### `_route_to_model(analysis_type: str) -> str`

**Purpose**: Internal helper method that selects the appropriate Hugging Face model ID based on analysis type.

**Implementation Strategy**:
```python
def _route_to_model(self, analysis_type: str) -> str:
    """Route analysis type to appropriate HF model ID."""
    model_mapping = {
        AnalysisType.CODE_REVIEW: "microsoft/codebert-base",
        AnalysisType.REQUIREMENT_EXTRACTION: "facebook/bart-large-mnli",
        AnalysisType.TECH_RECOMMENDATION: "sentence-transformers/all-MiniLM-L6-v2",
        AnalysisType.RISK_ASSESSMENT: "cardiffnlp/twitter-roberta-base-sentiment-latest"
    }
    
    if analysis_type not in model_mapping:
        raise ValueError(f"Unsupported analysis type: {analysis_type}")
    
    return model_mapping[analysis_type]
```

**Characteristics**:
- Maintains a mapping between analysis types and HF model IDs
- Validates analysis type before routing
- Supports model fallback strategies
- Enables easy model updates without API changes

## Error Handling Contract

### Standard Error Schema

All errors returned by AIEngine operations follow a consistent schema:

```python
class AIEngineError:
    error_code: str          # Standardized error code
    message: str             # Human-readable error message
    details: Optional[Dict]  # Additional error context
    timestamp: datetime      # When the error occurred
    request_id: str         # Unique identifier for tracing
```

### Error Types

#### `ANALYSIS_TYPE_UNSUPPORTED`
- **Trigger**: Invalid or unsupported analysis_type provided
- **HTTP Status**: 400 Bad Request
- **Recovery**: Use supported analysis types from enum

#### `MODEL_UNAVAILABLE`
- **Trigger**: Selected HF model is not accessible or loaded
- **HTTP Status**: 503 Service Unavailable
- **Recovery**: Retry with exponential backoff

#### `CONTENT_TOO_LARGE`
- **Trigger**: Input content exceeds model context limits
- **HTTP Status**: 413 Payload Too Large
- **Recovery**: Chunk content or use summarization

#### `PROCESSING_TIMEOUT`
- **Trigger**: Analysis operation exceeds configured timeout
- **HTTP Status**: 504 Gateway Timeout
- **Recovery**: Retry with longer timeout or simpler analysis

#### `RATE_LIMIT_EXCEEDED`
- **Trigger**: Too many requests in time window
- **HTTP Status**: 429 Too Many Requests
- **Recovery**: Implement client-side rate limiting

### Timeout Handling

**Default Timeouts**:
- Model loading: 30 seconds
- Analysis processing: 120 seconds
- Model inference: 60 seconds

**Timeout Strategy**:
1. Graceful degradation with partial results when possible
2. Automatic retry with exponential backoff for transient failures
3. Circuit breaker pattern for persistent model failures
4. Fallback to simpler models when primary models timeout

### Error Response Format

```json
{
  "error": {
    "error_code": "PROCESSING_TIMEOUT",
    "message": "Analysis operation timed out after 120 seconds",
    "details": {
      "analysis_type": "code_review",
      "timeout_duration": 120,
      "content_length": 15000
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123def456"
  }
}
```

## Implementation Considerations

### Performance
- Model caching to reduce loading times
- Async processing for concurrent requests
- Request queuing for resource management

### Scalability
- Horizontal scaling through model sharding
- Load balancing across model instances
- Resource isolation per analysis type

### Monitoring
- Request/response logging
- Model performance metrics
- Error rate tracking
- Resource utilization monitoring

## Dependencies

- **Hugging Face Transformers**: Model loading and inference
- **FastAPI**: Web framework for OpenAPI operations
- **Pydantic**: Data validation and serialization
- **asyncio**: Asynchronous processing
- **Redis**: Caching and session management
