"""AI Engine Service - FastAPI Web Service.

This module provides a FastAPI-based web service that exposes AI-powered analysis
capabilities through REST API endpoints. It serves as the main entry point for
the AI Engine Service microservice.

The service provides the following capabilities:
- Content analysis using various AI models
- Model management and discovery
- Health monitoring and status reporting
- Request validation and error handling

Example:
    To run the service:
    $ uvicorn main:app --host 0.0.0.0 --port 8000
    
    To access interactive documentation:
    Navigate to http://localhost:8000/docs

Attributes:
    app (FastAPI): The main FastAPI application instance
    ai_engine (AIEngine): AI processing engine instance
    logger (Logger): Application logger for debugging and monitoring
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import logging

# Import schemas for request/response validation
from schemas import (
    AnalysisRequest as AnalysisRequestSchema,
    AnalysisResponse,
    AIModel,
    ModelsResponse,
    StandardResponse,
    ErrorResponse
)

# Import the core AI Engine logic
from scripts.assistant.ai_engine.main import AIEngine, AnalysisRequest, AnalysisResult
from scripts.ai_engine.model import error_tracker

# Configure logging for service monitoring and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with comprehensive metadata
app = FastAPI(
    title="AI Engine Service",
    description="""AI-powered analysis and processing service for the ClarityForge platform.
    
    This service provides intelligent content analysis capabilities including:
    - Code review and quality assessment
    - Requirement extraction from documents
    - Technology stack recommendations
    - Risk assessment and mitigation strategies
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Initialize the AI Engine core processing component
ai_engine = AIEngine()

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions and return standardized error response.
    
    This global exception handler catches any unhandled exceptions that occur
    during request processing and returns a standardized error response to the client.
    It also logs the exception details for debugging purposes.
    
    Args:
        request (Request): The incoming FastAPI request object
        exc (Exception): The unhandled exception that was raised
        
    Returns:
        JSONResponse: Standardized error response with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "details": {"exception_type": type(exc).__name__}
        }
    )

@app.post("/ai-engine/analyze", response_model=StandardResponse)
async def analyze_content(request_data: AnalysisRequestSchema):
    """Analyze content using AI models.
    
    This endpoint processes content using various AI models to provide intelligent
    analysis based on the specified analysis type. It supports multiple analysis
    types including code review, requirement extraction, technology recommendations,
    and risk assessment.
    
    The analysis process includes:
    1. Request validation using Pydantic schemas
    2. Content processing using the specified AI model
    3. Confidence scoring and recommendation generation
    4. Response formatting with timing metrics
    
    Args:
        request_data (AnalysisRequestSchema): Analysis request containing:
            - content: The text content to be analyzed
            - analysis_type: Type of analysis to perform
            - model: Optional specific model to use
            - parameters: Optional additional parameters
            
    Returns:
        StandardResponse: Standardized response containing:
            - data: Analysis results with ID, confidence, and recommendations
            - timestamp: Response generation timestamp
            - status: Request processing status
            
    Raises:
        HTTPException 400: For validation errors or invalid parameters
        HTTPException 500: For analysis processing errors
        
    Example:
        POST /ai-engine/analyze
        {
            "content": "def hello(): print('world')",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
    """
    try:
        logger.info(f"Processing analysis request for type: {request_data.analysis_type}")
        
        # Create internal request object
        request = AnalysisRequest(
            content=request_data.content,
            analysis_type=request_data.analysis_type.value,
            model=request_data.model,
            parameters=request_data.parameters
        )
        
        # Perform analysis
        result: AnalysisResult = ai_engine.analyze_content(request)
        
        # Create response
        analysis_response = AnalysisResponse(
            analysis_id=result.analysis_id,
            results=result.results,
            confidence=result.confidence,
            recommendations=result.recommendations,
            processing_time_ms=result.processing_time_ms
        )
        
        return StandardResponse(
            data=analysis_response.dict(),
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            status="success"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ANALYSIS_ERROR",
                "message": "Failed to perform analysis",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "details": {"original_error": str(e)}
            }
        )

@app.get("/ai-engine/models", response_model=StandardResponse)
async def get_available_models():
    """Retrieve a list of all available AI models.
    
    This endpoint returns comprehensive information about all AI models that are
    currently available for analysis tasks. The response includes model metadata
    such as capabilities, providers, versions, and supported features.
    
    The model information is cached for performance and includes:
    - Model identifiers and human-readable names
    - Detailed descriptions of model capabilities
    - Supported analysis types and features
    - Version and provider information
    
    Returns:
        StandardResponse: Standardized response containing:
            - data: ModelsResponse with list of available models
            - timestamp: Response generation timestamp
            - status: Request processing status
            
    Raises:
        HTTPException 500: If model information retrieval fails
        
    Example Response:
        {
            "data": {
                "models": [
                    {
                        "id": "google/flan-t5-base",
                        "name": "FLAN-T5 Base",
                        "description": "General-purpose NLU model",
                        "capabilities": ["text_generation", "summarization"],
                        "version": "base",
                        "provider": "Google"
                    }
                ]
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "status": "success"
        }
    """
    try:
        logger.info("Fetching available models")
        
        models_data = ai_engine.get_available_models()
        
        # Convert to proper schema
        models = [
            AIModel(
                id=model["id"],
                name=model["name"],
                description=model["description"],
                capabilities=model["capabilities"],
                version=model["version"],
                provider=model["provider"]
            )
            for model in models_data
        ]
        
        models_response = ModelsResponse(models=models)
        
        return StandardResponse(
            data=models_response.dict(),
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "MODELS_FETCH_ERROR",
                "message": "Failed to fetch available models",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "details": {"original_error": str(e)}
            }
        )

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring.
    
    This endpoint provides a comprehensive health check mechanism for monitoring the
    AI Engine Service status. It's used by load balancers, orchestration systems,
    and monitoring tools to verify that the service is running and responsive.
    
    The endpoint performs service validation and returns detailed status information including:
    - Overall service health status
    - AIEngine component status
    - HuggingFace API connectivity status
    - Available models status
    - Service identifier
    - Response timestamp
    
    Returns:
        dict: Health status response containing:
            - status: Overall service health status ('healthy', 'degraded', or 'unhealthy')
            - service: Service identifier ('ai-engine')
            - timestamp: Health check response timestamp
            - components: Detailed status of individual components
            
    Example Response:
        {
            "status": "healthy",
            "service": "ai-engine",
            "timestamp": "2024-01-01T12:00:00Z",
            "components": {
                "ai_engine": {
                    "status": "healthy",
                    "message": "AIEngine initialized and ready"
                },
                "huggingface_api": {
                    "status": "healthy",
                    "message": "API connectivity verified"
                },
                "models": {
                    "status": "healthy",
                    "available_count": 2,
                    "message": "All models available"
                }
            }
        }
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    components = {}
    overall_status = "healthy"
    
    # Check AIEngine status
    try:
        if ai_engine is not None:
            components["ai_engine"] = {
                "status": "healthy",
                "message": "AIEngine initialized and ready"
            }
        else:
            components["ai_engine"] = {
                "status": "unhealthy",
                "message": "AIEngine not initialized"
            }
            overall_status = "unhealthy"
    except Exception as e:
        components["ai_engine"] = {
            "status": "unhealthy",
            "message": f"AIEngine error: {str(e)}"
        }
        overall_status = "unhealthy"
    
    # Check HuggingFace API connectivity
    try:
        hf_status = ai_engine.check_hf_api_health()
        components["huggingface_api"] = hf_status
        if hf_status["status"] != "healthy":
            overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
    except Exception as e:
        components["huggingface_api"] = {
            "status": "unhealthy",
            "message": f"HuggingFace API check failed: {str(e)}"
        }
        overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
    
    # Check available models
    try:
        models = ai_engine.get_available_models()
        components["models"] = {
            "status": "healthy",
            "available_count": len(models),
            "message": f"{len(models)} models available"
        }
    except Exception as e:
        components["models"] = {
            "status": "unhealthy",
            "message": f"Model availability check failed: {str(e)}"
        }
        overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "service": "ai-engine",
        "timestamp": timestamp,
        "components": components
    }

@app.get("/monitoring/errors")
async def get_error_monitoring():
    """Retrieve error monitoring and tracking information.
    
    This endpoint provides comprehensive error monitoring data for the AI Engine Service,
    including HuggingFace API error statistics, recent error history, and error patterns.
    It's used by monitoring systems and developers to track service reliability.
    
    The endpoint returns:
    - Total error counts by type and model
    - Recent error history with timestamps and context
    - Error patterns and frequencies
    - Service health indicators based on error rates
    
    Returns:
        dict: Error monitoring data containing:
            - error_summary: Summary statistics of recent errors
            - health_indicators: Service health based on error patterns
            - timestamp: Response generation timestamp
            
    Example Response:
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
                "error_rate": "low",
                "most_frequent_error": "RATE_LIMIT",
                "recommendations": ["Consider implementing rate limiting"]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Get error summary from the global error tracker
        error_summary = error_tracker.get_error_summary()
        
        # Generate health indicators based on error patterns
        health_indicators = _generate_health_indicators(error_summary)
        
        return {
            "error_summary": error_summary,
            "health_indicators": health_indicators,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"Error fetching monitoring data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "MONITORING_ERROR",
                "message": "Failed to fetch error monitoring data",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "details": {"original_error": str(e)}
            }
        )

def _generate_health_indicators(error_summary: dict) -> dict:
    """Generate health indicators based on error patterns."""
    total_errors = error_summary.get("total_errors", 0)
    error_counts = error_summary.get("error_counts", {})
    
    # Determine error rate level
    if total_errors == 0:
        error_rate = "none"
    elif total_errors < 10:
        error_rate = "low"
    elif total_errors < 50:
        error_rate = "medium"
    else:
        error_rate = "high"
    
    # Find most frequent error type
    most_frequent_error = None
    max_count = 0
    for error_key, count in error_counts.items():
        if count > max_count:
            max_count = count
            most_frequent_error = error_key.split(":")[0] if ":" in error_key else error_key
    
    # Generate recommendations based on error patterns
    recommendations = []
    
    if "RATE_LIMIT" in str(error_counts):
        recommendations.append("Consider implementing request rate limiting and backoff strategies")
    
    if "AUTH_ERROR" in str(error_counts):
        recommendations.append("Verify HuggingFace API token configuration")
    
    if "NETWORK_ERROR" in str(error_counts):
        recommendations.append("Check network connectivity and implement circuit breaker pattern")
    
    if "QUOTA_EXCEEDED" in str(error_counts):
        recommendations.append("Monitor API usage and consider upgrading HuggingFace plan")
    
    if total_errors > 20:
        recommendations.append("High error rate detected - investigate service stability")
    
    if not recommendations:
        recommendations.append("Service error rates are within normal parameters")
    
    return {
        "error_rate": error_rate,
        "most_frequent_error": most_frequent_error,
        "recommendations": recommendations,
        "total_error_count": total_errors,
        "unique_error_types": len(error_counts)
    }
