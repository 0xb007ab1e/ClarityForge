"""Pydantic Models and Schemas for AI Engine Service.

This module defines all the data models used for request validation, response
formatting, and API documentation in the AI Engine Service. The schemas ensure
data integrity and provide automatic validation for all API endpoints.

The module includes:
- Request/response models for content analysis
- AI model metadata schemas  
- Standard response wrappers
- Error response structures
- Enumeration types for analysis categories

All models use Pydantic for automatic validation, serialization, and OpenAPI
schema generation.

Example:
    from schemas import AnalysisRequest, AnalysisResponse
    
    request = AnalysisRequest(
        content="Code to analyze",
        analysis_type="code_review"
    )
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    """Enumeration of supported analysis types.
    
    This enum defines all the analysis types that the AI Engine Service supports.
    Each type represents a different kind of AI-powered analysis that can be
    performed on the provided content.
    
    Attributes:
        CODE_REVIEW: Analyze code for quality, bugs, and improvements
        REQUIREMENT_EXTRACTION: Extract requirements from project documentation
        TECH_RECOMMENDATION: Generate technology stack recommendations
        RISK_ASSESSMENT: Identify project risks and mitigation strategies
    """
    CODE_REVIEW = "code_review"
    REQUIREMENT_EXTRACTION = "requirement_extraction"
    TECH_RECOMMENDATION = "tech_recommendation"
    RISK_ASSESSMENT = "risk_assessment"

class AnalysisRequest(BaseModel):
    """Request model for content analysis.
    
    This model defines the structure for analysis requests sent to the AI Engine.
    It includes validation rules to ensure content quality and proper parameter
    specification.
    
    Attributes:
        content: The text content to be analyzed (must be non-empty)
        analysis_type: The type of analysis to perform (from AnalysisType enum)
        model: Optional specific AI model identifier to use
        parameters: Optional additional parameters for customizing analysis behavior
        
    Example:
        {
            "content": "def hello(): print('world')",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base",
            "parameters": {"focus_areas": ["performance"]}
        }
    """
    content: str = Field(..., min_length=1, description="Content to be analyzed")
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    model: Optional[str] = Field(None, description="Specific model to use for analysis")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters for analysis")

class AnalysisResponse(BaseModel):
    """Response model for analysis results.
    
    This model defines the structure of successful analysis responses returned
    by the AI Engine. It includes the analysis outcome details such as result
    data, confidence scoring, and processing time.
    
    Attributes:
        analysis_id: Unique identifier for the analysis
        results: The result of the analysis as a key-value dictionary
        confidence: The confidence score for the analysis result
        recommendations: Actionable recommendations generated from the analysis
        processing_time_ms: Total processing time in milliseconds
        
    Example:
        {
            "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
            "results": {...},
            "confidence": 0.85,
            "recommendations": ["Improve error handling in code"],
            "processing_time_ms": 1200
        }
    """
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the analysis")
    recommendations: List[str] = Field(default_factory=list, description="Generated recommendations")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

class AIModel(BaseModel):
    """Data model for AI model metadata.
    
    This model encapsulates metadata for individual AI models that are integrated with
    the AI Engine Service. It provides detailed information about each model's capabilities
    and usage.
    
    Attributes:
        id: Unique model identifier string
        name: Human-readable name of the model
        description: Detailed model description and capabilities
        capabilities: List of functions supported by the model
        version: Model version string
        provider: Name of the model provider
        
    Example:
        {
            "id": "google/flan-t5-base",
            "name": "FLAN-T5 Base",
            "description": "General-purpose model for NLU",
            "capabilities": ["text generation", "summarization"],
            "version": "base",
            "provider": "Google"
        }
    """
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Human-readable model name")
    description: str = Field(..., description="Model description")
    capabilities: List[str] = Field(..., description="List of model capabilities")
    version: str = Field(..., description="Model version")
    provider: str = Field(..., description="Model provider")

class ModelsResponse(BaseModel):
    """Response model for available AI models.
    
    This model structures the response for listing available AI models via the AI Engine Service.
    It provides a comprehensive list of AI models with corresponding metadata.
    
    Attributes:
        models: A list of AIModel instances representing available models
        
    Example:
        {
            "models": [
                {
                    "id": "google/flan-t5-base",
                    "name": "FLAN-T5 Base",
                    "description": "General-purpose model for NLU",
                    "capabilities": ["text generation", "summarization"],
                    "version": "base",
                    "provider": "Google"
                }
            ]
        }
    """
    models: List[AIModel] = Field(..., description="List of available models")

class StandardResponse(BaseModel):
    """Standard response model for all successful API responses.
    
    This generic response structure is used by the API to return success results,
    timestamps, and status codes. It ensures consistency across different endpoint
    responses and facilitates easy parsing by clients.
    
    Attributes:
        data: The main content of the response, which varies by endpoint
        timestamp: The time when the response was generated, in UTC format
        status: The status of the response (e.g., success)
        
    Example:
        {
            "data": {...},
            "timestamp": "2024-01-01T12:00:00Z",
            "status": "success"
        }
    """
    data: Any = Field(..., description="Response data")
    timestamp: str = Field(..., description="Response timestamp")
    status: str = Field(default="success", description="Response status")

class ErrorResponse(BaseModel):
    """Error response model for all failed API interactions.
    
    This standard error response structure is used whenever an API call fails due to
    client-side or server-side errors. It provides useful information for debugging
    and understanding the causes of failures.
    
    Attributes:
        error: A code representing the error type (e.g., VALIDATION_ERROR)
        message: A descriptive message detailing the error
        timestamp: The time when the error occurred, in UTC format
        details: Additional contextual information or sub-errors about the failure
        
    Example:
        {
            "error": "VALIDATION_ERROR",
            "message": "Invalid analysis_type provided",
            "timestamp": "2024-01-01T12:00:00Z",
            "details": {
                "field": "analysis_type",
                "allowed_values": ["code_review", "requirement_extraction", "tech_recommendation", "risk_assessment"]
            }
        }
    """
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
