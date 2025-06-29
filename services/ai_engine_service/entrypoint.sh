#!/bin/bash

# Entrypoint script for AI Engine Service

echo "Starting AI Engine Service..."

# Check if HUGGINGFACE_API_TOKEN is set
if [ -z "$HUGGINGFACE_API_TOKEN" ]; then
    echo "Warning: HUGGINGFACE_API_TOKEN environment variable is not set"
    echo "Some AI functionality may not work without proper authentication"
fi

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info
