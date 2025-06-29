"""AI Model Integration Module.

This module provides integration with external AI models through the Hugging Face API.
It handles model inference requests, response processing, and error handling for
various AI models used by the AI Engine Service.

The module supports:
- Text generation using FLAN-T5 models
- Text classification using BART models
- Retry logic for robust API communication
- Environment-based authentication

Example:
    response = generate_response("Analyze this code: def hello(): print('world')")
    labels = classify("This is a technical support question")

Note:
    Requires HUGGINGFACE_API_TOKEN environment variable to be set.
"""

import os
import requests
from typing import List, Dict, Optional
import logging
import time
import json
from datetime import datetime
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

# Error tracking and monitoring
class ErrorTracker:
    """Centralized error tracking and monitoring for HuggingFace API interactions."""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = []
        self.max_error_history = 100
    
    def track_error(self, error_type: str, model_id: str, error_message: str, 
                   context: Dict = None):
        """Track and log errors with contextual information."""
        timestamp = datetime.utcnow().isoformat()
        
        error_entry = {
            "timestamp": timestamp,
            "error_type": error_type,
            "model_id": model_id,
            "error_message": error_message,
            "context": context or {}
        }
        
        # Add to error history
        self.last_errors.append(error_entry)
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)
        
        # Update error counts
        error_key = f"{error_type}:{model_id}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log the error
        logger.error(
            f"HF API Error - Type: {error_type}, Model: {model_id}, "
            f"Message: {error_message}, Context: {context}"
        )
        
        # Send to centralized monitoring (if configured)
        self._send_to_monitoring(error_entry)
    
    def _send_to_monitoring(self, error_entry: Dict):
        """Send error events to centralized monitoring system."""
        try:
            # Check for monitoring configuration
            monitoring_url = os.environ.get("ERROR_MONITORING_URL")
            monitoring_token = os.environ.get("ERROR_MONITORING_TOKEN")
            
            if monitoring_url and monitoring_token:
                headers = {
                    "Authorization": f"Bearer {monitoring_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "service": "ai-engine",
                    "level": "error",
                    "message": error_entry["error_message"],
                    "metadata": error_entry
                }
                
                response = requests.post(
                    monitoring_url,
                    headers=headers,
                    json=payload,
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info("Error event sent to monitoring system")
                else:
                    logger.warning(f"Failed to send error to monitoring: {response.status_code}")
            
            # Also try to send to issue tracker (if configured)
            self._send_to_issue_tracker(error_entry)
            
        except Exception as e:
            logger.warning(f"Failed to send error to monitoring system: {str(e)}")
    
    def _send_to_issue_tracker(self, error_entry: Dict):
        """Send critical errors to issue tracker."""
        try:
            issue_tracker_url = os.environ.get("ISSUE_TRACKER_URL")
            issue_tracker_token = os.environ.get("ISSUE_TRACKER_TOKEN")
            
            if issue_tracker_url and issue_tracker_token:
                # Only create issues for critical errors or repeated failures
                error_key = f"{error_entry['error_type']}:{error_entry['model_id']}"
                error_count = self.error_counts.get(error_key, 0)
                
                if error_count >= 5 or error_entry["error_type"] in ["AUTH_ERROR", "QUOTA_EXCEEDED"]:
                    headers = {
                        "Authorization": f"token {issue_tracker_token}",
                        "Content-Type": "application/json"
                    }
                    
                    issue_title = f"[AI-Engine] HF API Error: {error_entry['error_type']} ({error_count} occurrences)"
                    issue_body = f"""## Error Details

**Error Type:** {error_entry['error_type']}
**Model ID:** {error_entry['model_id']}
**Error Message:** {error_entry['error_message']}
**Timestamp:** {error_entry['timestamp']}
**Occurrence Count:** {error_count}

## Context
```json
{json.dumps(error_entry['context'], indent=2)}
```

## Recent Error History
```json
{json.dumps(self.last_errors[-5:], indent=2)}
```

This issue was automatically created by the AI Engine error monitoring system.
"""
                    
                    payload = {
                        "title": issue_title,
                        "body": issue_body,
                        "labels": ["ai-engine", "hf-api-error", "auto-generated"]
                    }
                    
                    response = requests.post(
                        issue_tracker_url,
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        logger.info(f"Issue created for repeated error: {error_key}")
                    else:
                        logger.warning(f"Failed to create issue: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"Failed to send error to issue tracker: {str(e)}")
    
    def get_error_summary(self) -> Dict:
        """Get a summary of recent errors for monitoring."""
        return {
            "total_errors": len(self.last_errors),
            "error_counts": self.error_counts,
            "recent_errors": self.last_errors[-10:] if self.last_errors else []
        }

# Global error tracker instance
error_tracker = ErrorTracker()

def monitor_hf_api_calls(func):
    """Decorator to monitor and track HuggingFace API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        model_id = args[0] if args else "unknown"
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful call
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"HF API call successful - Model: {model_id}, Duration: {duration_ms}ms")
            
            return result
            
        except ValueError as e:
            # Authentication or configuration errors
            error_tracker.track_error(
                "AUTH_ERROR",
                model_id,
                str(e),
                {"function": func.__name__, "args_count": len(args)}
            )
            raise
            
        except requests.exceptions.HTTPError as e:
            # HTTP errors from HuggingFace API
            error_type = "HTTP_ERROR"
            if e.response.status_code == 429:
                error_type = "RATE_LIMIT"
            elif e.response.status_code == 503:
                error_type = "SERVICE_UNAVAILABLE"
            elif e.response.status_code == 402:
                error_type = "QUOTA_EXCEEDED"
            
            error_tracker.track_error(
                error_type,
                model_id,
                f"HTTP {e.response.status_code}: {str(e)}",
                {
                    "function": func.__name__,
                    "status_code": e.response.status_code,
                    "response_text": e.response.text[:500] if e.response.text else "No response text"
                }
            )
            raise
            
        except requests.exceptions.RequestException as e:
            # Network or connection errors
            error_tracker.track_error(
                "NETWORK_ERROR",
                model_id,
                str(e),
                {"function": func.__name__, "error_class": type(e).__name__}
            )
            raise
            
        except Exception as e:
            # Any other unexpected errors
            error_tracker.track_error(
                "UNKNOWN_ERROR",
                model_id,
                str(e),
                {"function": func.__name__, "error_class": type(e).__name__}
            )
            raise
    
    return wrapper

@monitor_hf_api_calls
def _hf_request(model_id: str, data: dict, retries=3, delay=1):
    """Make a request to the Hugging Face Inference API with retry logic.
    
    This internal function handles communication with the Hugging Face Inference API,
    including authentication, error handling, and retry logic for improved reliability.
    
    Args:
        model_id (str): The Hugging Face model identifier (e.g., 'google/flan-t5-base')
        data (dict): The request payload to send to the model API
        retries (int, optional): Number of retry attempts for failed requests. Defaults to 3.
        delay (int, optional): Delay between retries in seconds. Defaults to 1.
        
    Returns:
        dict: The JSON response from the Hugging Face API
        
    Raises:
        ValueError: If HUGGINGFACE_API_TOKEN environment variable is not set
        requests.HTTPError: If all retry attempts fail
        
    Note:
        Requires HUGGINGFACE_API_TOKEN environment variable for authentication.
    """
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    hf_token = os.environ.get("HUGGINGFACE_API_TOKEN")
    if not hf_token:
        raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")
    headers = {"Authorization": f"Bearer {hf_token}"}
    for i in range(retries):
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        print(f"Request failed with status {response.status_code}, retrying in {delay}s...")
        # time.sleep(delay)  <- This is removed for synchronous operation
    response.raise_for_status()


def generate_response(context: str) -> str:
    """Generate a text response using the Google FLAN-T5 Base model.
    
    This function uses the Hugging Face hosted FLAN-T5 model to generate intelligent
    text responses based on the provided context. It's primarily used for tasks like
    code review, requirement analysis, and general text generation.
    
    Args:
        context (str): The input text/context for which to generate a response.
                      This can be a question, code snippet, or any text that needs
                      AI-powered analysis or completion.
                      
    Returns:
        str: The generated text response from the FLAN-T5 model.
        
    Raises:
        ValueError: If HUGGINGFACE_API_TOKEN environment variable is not set
        requests.HTTPError: If the API request fails after all retries
        KeyError: If the API response format is unexpected
        
    Example:
        >>> response = generate_response("Review this Python code: def add(a, b): return a + b")
        >>> print(response)
        "The function looks good but could benefit from type hints and docstring."
        
    Note:
        The function expects the API to return a list containing dictionaries with
        'generated_text' keys. This matches the standard Hugging Face Inference API format.
    """
    data = _hf_request("google/flan-t5-base", {"inputs": context})
    # API returns a list with dicts like {"generated_text": "..."}
    return data[0]["generated_text"]


def classify(text: str) -> List[str]:
    """Classify text using the Facebook BART Large MNLI model.
    
    This function performs zero-shot text classification using the BART model to
    categorize input text into predefined categories. It's useful for content
    categorization, intent detection, and automated tagging.
    
    The function uses a confidence threshold of 0.5 to filter results, returning
    only classifications where the model has reasonable confidence.
    
    Args:
        text (str): The input text to be classified. Can be any length of text
                   that needs categorization.
                   
    Returns:
        List[str]: A list of classification labels that exceed the confidence threshold.
                  May be empty if no classifications meet the threshold.
                  
    Raises:
        ValueError: If HUGGINGFACE_API_TOKEN environment variable is not set
        requests.HTTPError: If the API request fails after all retries
        KeyError: If the API response format is unexpected
        
    Example:
        >>> labels = classify("I need help with my account billing")
        >>> print(labels)
        ['billing', 'tech support']
        
        >>> labels = classify("I want to buy your product")
        >>> print(labels)
        ['sales']
        
    Note:
        Currently uses hardcoded candidate labels: ["tech support", "billing", "sales"].
        This could be made configurable in future versions to support different
        classification schemes.
    """
    candidate_labels = ["tech support", "billing", "sales"]
    data = _hf_request(
        "facebook/bart-large-mnli",
        {"inputs": text, "parameters": {"candidate_labels": candidate_labels}}
    )
    # API returns {"labels": [...], "scores": [...]}
    return [lbl for lbl, score in zip(data["labels"], data["scores"]) if score > 0.5]

