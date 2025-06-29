"""Integration tests for AI Engine Service."""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import sys
import os
import json
from datetime import datetime

# Add the service directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from main import app
from schemas import AnalysisType


class TestAIEngineServiceIntegration:
    """Integration test suite for the entire AI Engine Service."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def mock_hf_responses(self):
        """Mock responses for HuggingFace API calls."""
        return {
            "generate_response": [{"generated_text": "This is a comprehensive code review response with detailed feedback."}],
            "classify": {"labels": ["tech support", "billing"], "scores": [0.8, 0.6]}
        }

    @patch('scripts.ai_engine.model._hf_request')
    def test_full_service_workflow(self, mock_hf_request, client, mock_hf_responses):
        """Test complete workflow: get models, then analyze content."""
        
        # Setup mock responses for _hf_request
        mock_hf_request.return_value = mock_hf_responses["generate_response"]
        
        # Step 1: Get available models
        models_response = client.get("/ai-engine/models")
        assert models_response.status_code == 200
        
        models_data = models_response.json()
        assert models_data["status"] == "success"
        assert len(models_data["data"]["models"]) == 2
        
        # Extract model IDs for use in analysis
        available_models = [model["id"] for model in models_data["data"]["models"]]
        assert "google/flan-t5-base" in available_models
        assert "facebook/bart-large-mnli" in available_models
        
        # Step 2: Analyze content using one of the available models
        analysis_payload = {
            "content": "def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base",
            "parameters": {"temperature": 0.7}
        }
        
        analysis_response = client.post("/ai-engine/analyze", json=analysis_payload)
        assert analysis_response.status_code == 200
        
        analysis_data = analysis_response.json()
        assert analysis_data["status"] == "success"
        assert "data" in analysis_data
        
        # Verify analysis response structure
        analysis_result = analysis_data["data"]
        assert "analysis_id" in analysis_result
        assert "results" in analysis_result
        assert "confidence" in analysis_result
        assert "recommendations" in analysis_result
        assert "processing_time_ms" in analysis_result
        
        # Verify the model used matches what we requested
        assert analysis_result["results"]["model_used"] == "google/flan-t5-base"
        assert analysis_result["results"]["analysis_type"] == "code_review"

    @patch('scripts.ai_engine.model._hf_request')
    def test_multiple_analysis_types_workflow(self, mock_hf_request, client, mock_hf_responses):
        """Test workflow with different analysis types."""
        
        # Configure mock to handle different analysis types
        def mock_hf_side_effect(*args, **kwargs):
            if "candidate_labels" in args[1]:  # classify call
                return mock_hf_responses["classify"]
            else:  # generate_response call
                return mock_hf_responses["generate_response"]
        
        mock_hf_request.side_effect = mock_hf_side_effect
        
        # Test different analysis types
        analysis_types = [
            ("code_review", "def hello(): print('world')"),
            ("requirement_extraction", "Build a web app with user authentication"),
            ("tech_recommendation", "E-commerce platform with microservices"),
            ("risk_assessment", "Cloud migration project")
        ]
        
        for analysis_type, content in analysis_types:
            payload = {
                "content": content,
                "analysis_type": analysis_type,
                "model": "google/flan-t5-base"
            }
            
            response = client.post("/ai-engine/analyze", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            # Check that the analysis was completed (confidence can be 0 in error cases)
            assert 0.0 <= data["data"]["confidence"] <= 1.0
            assert "analysis_id" in data["data"]
            assert "results" in data["data"]

    @patch('scripts.ai_engine.model._hf_request')
    def test_error_handling_workflow(self, mock_hf_request, client):
        """Test error handling across the service."""
        
        # Test models endpoint with error
        mock_hf_request.side_effect = Exception("HuggingFace API down")
        
        # Models endpoint should still work (doesn't use _hf_request directly)
        models_response = client.get("/ai-engine/models")
        assert models_response.status_code == 200
        
        # Analysis should handle the error gracefully
        analysis_payload = {
            "content": "test content",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        analysis_response = client.post("/ai-engine/analyze", json=analysis_payload)
        assert analysis_response.status_code == 200  # Service handles errors gracefully
        
        analysis_data = analysis_response.json()
        assert analysis_data["status"] == "success"
        # The AIEngine should return error results with confidence 0
        assert analysis_data["data"]["confidence"] == 0.0
        assert "error" in analysis_data["data"]["results"]

    def test_invalid_requests_handling(self, client):
        """Test handling of invalid requests."""
        
        # Test analyze endpoint with invalid analysis type
        invalid_payload = {
            "content": "test content",
            "analysis_type": "invalid_type",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=invalid_payload)
        assert response.status_code == 422  # Validation error
        
        # Test analyze endpoint with missing required fields
        incomplete_payload = {
            "content": "test content"
            # Missing analysis_type
        }
        
        response = client.post("/ai-engine/analyze", json=incomplete_payload)
        assert response.status_code == 422  # Validation error
        
        # Test analyze endpoint with empty content
        empty_content_payload = {
            "content": "",
            "analysis_type": "code_review"
        }
        
        response = client.post("/ai-engine/analyze", json=empty_content_payload)
        assert response.status_code == 422  # Validation error

    @patch('scripts.ai_engine.model._hf_request')
    def test_content_type_handling(self, mock_hf_request, client, mock_hf_responses):
        """Test handling of different content types."""
        
        mock_hf_request.return_value = mock_hf_responses["generate_response"]
        
        # Test with application/json (default)
        payload = {
            "content": "def test(): pass",
            "analysis_type": "code_review"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 200
        
        # Test with explicit Content-Type header
        response = client.post(
            "/ai-engine/analyze", 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200

    @patch('scripts.ai_engine.model._hf_request')
    def test_large_content_handling(self, mock_hf_request, client, mock_hf_responses):
        """Test handling of large content."""
        
        mock_hf_request.return_value = mock_hf_responses["generate_response"]
        
        # Create large content (10KB)
        large_content = "def function():\n    pass\n" * 500
        
        payload = {
            "content": large_content,
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["processing_time_ms"] >= 0

    @patch('scripts.ai_engine.model._hf_request')
    def test_concurrent_requests_integration(self, mock_hf_request, client, mock_hf_responses):
        """Test handling of concurrent requests to both endpoints."""
        import threading
        import time
        
        mock_hf_request.return_value = mock_hf_responses["generate_response"]
        
        results = []
        
        def make_models_request():
            response = client.get("/ai-engine/models")
            results.append(("models", response.status_code))
        
        def make_analyze_request():
            payload = {
                "content": "test content",
                "analysis_type": "code_review"
            }
            response = client.post("/ai-engine/analyze", json=payload)
            results.append(("analyze", response.status_code))
        
        # Create multiple concurrent requests
        threads = []
        for _ in range(2):
            threads.append(threading.Thread(target=make_models_request))
            threads.append(threading.Thread(target=make_analyze_request))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 4
        for endpoint, status_code in results:
            assert status_code == 200

    def test_health_check_integration(self, client):
        """Test health check endpoint integration."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-engine"
        assert "timestamp" in data

    @patch('scripts.ai_engine.model._hf_request')
    def test_response_consistency(self, mock_hf_request, client, mock_hf_responses):
        """Test that responses are consistent across multiple calls."""
        
        mock_hf_request.return_value = mock_hf_responses["generate_response"]
        
        payload = {
            "content": "def test(): return 'hello'",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        responses = []
        for _ in range(3):
            response = client.post("/ai-engine/analyze", json=payload)
            assert response.status_code == 200
            responses.append(response.json())
        
        # Verify consistent structure (but different analysis_ids)
        for response_data in responses:
            assert response_data["status"] == "success"
            assert "data" in response_data
            assert "timestamp" in response_data
            
            analysis_data = response_data["data"]
            assert "analysis_id" in analysis_data
            assert analysis_data["results"]["analysis_type"] == "code_review"
            assert analysis_data["results"]["model_used"] == "google/flan-t5-base"
        
        # Analysis IDs should be unique
        analysis_ids = [resp["data"]["analysis_id"] for resp in responses]
        assert len(set(analysis_ids)) == 3

    @patch('scripts.ai_engine.model._hf_request')
    def test_parameter_passing_integration(self, mock_hf_request, client, mock_hf_responses):
        """Test that parameters are properly passed through the system."""
        
        mock_hf_request.return_value = mock_hf_responses["generate_response"]
        
        payload = {
            "content": "test content",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base",
            "parameters": {
                "temperature": 0.8,
                "max_tokens": 100,
                "custom_param": "test_value"
            }
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 200
        
        # The service should accept and process the parameters
        # (even if the underlying AI engine doesn't use all of them)
        data = response.json()
        assert data["status"] == "success"

    @patch('scripts.ai_engine.model._hf_request')
    def test_service_performance_monitoring(self, mock_hf_request, client, mock_hf_responses):
        """Test that service provides performance monitoring data."""
        
        # Add a small delay to mock to simulate processing time
        def delayed_response(*args, **kwargs):
            import time
            time.sleep(0.01)  # 10ms delay
            return mock_hf_responses["generate_response"]
        
        mock_hf_request.side_effect = delayed_response
        
        payload = {
            "content": "def slow_function(): time.sleep(1)",
            "analysis_type": "code_review"
        }
        
        start_time = datetime.utcnow()
        response = client.post("/ai-engine/analyze", json=payload)
        end_time = datetime.utcnow()
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        # Verify processing time is captured
        processing_time_ms = data["data"]["processing_time_ms"]
        assert processing_time_ms > 0
        
        # Verify timestamp is recent (allow some tolerance for microseconds)
        response_timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        time_diff = abs((response_timestamp - start_time).total_seconds())
        assert time_diff <= 5.0  # Within 5 seconds should be reasonable

    def test_all_analysis_types_enum_coverage(self, client):
        """Test that all defined analysis types are handled."""
        
        # Get all analysis types from the enum
        analysis_types = [item.value for item in AnalysisType]
        
        with patch('scripts.ai_engine.model._hf_request') as mock_hf_request:
            mock_hf_request.return_value = [{"generated_text": "test response"}]
            
            for analysis_type in analysis_types:
                payload = {
                    "content": f"Test content for {analysis_type}",
                    "analysis_type": analysis_type
                }
                
                response = client.post("/ai-engine/analyze", json=payload)
                assert response.status_code == 200
                
                data = response.json()
                assert data["status"] == "success"
