# AI Engine Service

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-0%25-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.9-blue)

A FastAPI-based micro-service that provides AI-powered analysis and processing capabilities for the ClarityForge platform.

## AI Engine Service

The AI Engine Service is a sophisticated microservice that leverages machine learning models to provide intelligent analysis capabilities. It serves as the core AI processing component within the ClarityForge ecosystem, offering various analysis types to support software development and project management workflows.

### Core Capabilities

- **Code Review Analysis**: Automated code quality assessment, identifying potential issues, bugs, and improvement opportunities
- **Requirement Extraction**: Intelligent parsing of project documents to extract and categorize functional and non-functional requirements  
- **Technology Recommendations**: AI-driven suggestions for appropriate technology stacks based on project requirements and constraints
- **Risk Assessment**: Comprehensive analysis of project risks with mitigation strategies and recommendations

### AI Models Integration

The service integrates with multiple AI models through the Hugging Face API:

- **Google FLAN-T5 Base**: General-purpose natural language understanding for text generation, question answering, and summarization
- **Facebook BART Large MNLI**: Specialized in zero-shot classification and natural language inference

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   AI Engine     │    │   Hugging Face  │
│   Web Service   │───▶│   Core Logic    │───▶│   API Models    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Request       │    │   Analysis      │    │   Model         │
│   Validation    │    │   Processing    │    │   Inference     │
│   (Pydantic)    │    │   & Results     │    │   & Response    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Service Features

- **High Performance**: Optimized request processing with response caching
- **Robust Error Handling**: Comprehensive error management with detailed logging
- **Scalable Architecture**: Designed for horizontal scaling in containerized environments
- **API Standards Compliance**: Full OpenAPI 3.0 specification support
- **Health Monitoring**: Built-in health check endpoints for service monitoring
- **Security**: Token-based authentication for external AI model access

## Features

- **Content Analysis**: Analyze various types of content using AI models
- **Model Management**: List and manage available AI models
- **Standards Compliance**: Full compliance with OpenAPI specifications
- **Error Handling**: Comprehensive error handling with standardized responses
- **Validation**: Request/response validation using Pydantic schemas

## API Endpoints

### POST /ai-engine/analyze

Analyze content using AI models.

**Request Body:**
```json
{
  "content": "Content to analyze",
  "analysis_type": "code_review|requirement_extraction|tech_recommendation|risk_assessment",
  "model": "optional_model_id",
  "parameters": {}
}
```

**Response:**
```json
{
  "data": {
    "analysis_id": "uuid",
    "results": {},
    "confidence": 0.85,
    "recommendations": [],
    "processing_time_ms": 1500
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "success"
}
```

### GET /ai-engine/models

List available AI models.

**Response:**
```json
{
  "data": {
    "models": [
      {
        "id": "model_id",
        "name": "Model Name",
        "description": "Model description",
        "capabilities": [],
        "version": "1.0",
        "provider": "Provider"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "success"
}
```

### GET /health

Health check endpoint.

## Environment Variables

- `HUGGINGFACE_API_TOKEN`: Required for accessing Hugging Face models
- `HOST`: Host to bind the service (default: 0.0.0.0)
- `PORT`: Port to run the service (default: 8000)

## Running the Service

### Using Docker Compose

```bash
# From the root of the ClarityForge project
docker-compose up ai_engine_service
```

### Direct Python Execution

```bash
cd services/ai_engine_service
pip install -r requirements.txt
export HUGGINGFACE_API_TOKEN=your_token_here
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Development

The service is built using:
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server implementation

### Directory Structure

```
services/ai_engine_service/
├── main.py              # FastAPI application
├── schemas.py           # Pydantic models
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── entrypoint.sh       # Service startup script
├── README.md           # This file
└── scripts/            # Copied AI Engine logic
    ├── ai_engine/
    └── assistant/
```

## Testing

The service can be tested using the interactive API documentation available at:
- `http://localhost:8002/docs` (when running via docker-compose)
- `http://localhost:8000/docs` (when running directly)

## Error Handling

The service implements comprehensive error handling with standardized error responses:

- **400 Bad Request**: Validation errors
- **500 Internal Server Error**: Processing errors
- All errors include timestamp and error details

## Integration

This service integrates with the existing ClarityForge AIEngine class and provides a REST API wrapper around its functionality. It follows the OpenAPI specification defined in the main project.
