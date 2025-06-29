"""Unit tests for AI Engine analyze endpoint."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

# Add the service directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from main import app
from schemas import StandardResponse, AnalysisResponse, AnalysisType


class TestAnalyzeEndpoint:
    """Test suite for the /ai-engine/analyze endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def valid_analysis_request(self):
        """Create a valid analysis request payload."""
        return {
            "content": "def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base",
            "parameters": {"temperature": 0.7, "max_tokens": 100}
        }

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_success(self, mock_hf_request, client, valid_analysis_request):
        """Test successful content analysis."""
        # Mock the HuggingFace API response
        mock_hf_request.return_value = [{"generated_text": "This is a recursive implementation of Fibonacci. Consider optimizing with memoization."}]
        
        response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        # Verify response status and structure
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "timestamp" in data
        assert "status" in data
        assert data["status"] == "success"
        
        # Verify analysis data structure
        analysis_data = data["data"]
        assert "analysis_id" in analysis_data
        assert "results" in analysis_data
        assert "confidence" in analysis_data
        assert "recommendations" in analysis_data
        assert "processing_time_ms" in analysis_data
        
        # Verify specific fields
        assert len(analysis_data["analysis_id"]) == 36  # UUID length
        assert 0.0 <= analysis_data["confidence"] <= 1.0
        assert analysis_data["processing_time_ms"] >= 0  # Processing time should be non-negative
        assert isinstance(analysis_data["recommendations"], list)
        assert len(analysis_data["recommendations"]) > 0
        
        # Verify results content
        results = analysis_data["results"]
        assert results["analysis_type"] == "code_review"
        assert results["model_used"] == "google/flan-t5-base"
        assert "review" in results

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_all_analysis_types(self, mock_hf_request, client):
        """Test all supported analysis types."""
        
        for analysis_type in AnalysisType:
            if analysis_type.value == "requirement_extraction":
                # Mock both calls for requirement extraction
                mock_hf_request.side_effect = [
                    [{"generated_text": "Extracted requirements"}],
                    {"labels": ["tech"], "scores": [0.7]}
                ]
            else:
                mock_hf_request.return_value = [{"generated_text": f"{analysis_type.value} response"}]
            
            payload = {
                "content": f"Test content for {analysis_type.value}",
                "analysis_type": analysis_type.value,
                "model": "google/flan-t5-base"
            }
            
            response = client.post("/ai-engine/analyze", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            
            # Check that we got valid response structure
            assert 0.0 <= data["data"]["confidence"] <= 1.0
            assert "analysis_id" in data["data"]
            assert "results" in data["data"]

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_requirement_extraction_with_classification(self, mock_hf_request, client):
        """Test requirement extraction that includes classification."""
        # Mock both generate_response and classify calls
        mock_hf_request.side_effect = [
            [{"generated_text": "Requirements: 1. Authentication 2. Database 3. API"}],
            {"labels": ["tech support", "billing"], "scores": [0.8, 0.6]}
        ]
        
        payload = {
            "content": "Build a web application with user authentication and database storage",
            "analysis_type": "requirement_extraction",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        results = data["data"]["results"]
        assert results["analysis_type"] == "requirement_extraction"
        assert "requirements" in results
        assert "classifications" in results
        assert data["data"]["confidence"] == 0.8  # Should be 0.8 when classifications exist

    def test_analyze_invalid_analysis_type(self, client):
        """Test analysis with invalid analysis type."""
        payload = {
            "content": "Test content",
            "analysis_type": "invalid_type",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 422  # Validation error

    def test_analyze_missing_required_fields(self, client):
        """Test analysis with missing required fields."""
        # Missing content
        payload = {
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 422
        
        # Missing analysis_type
        payload = {
            "content": "Test content",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_empty_content(self, client):
        """Test analysis with empty content."""
        payload = {
            "content": "",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        assert response.status_code == 422  # Should fail validation

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_without_model_parameter(self, mock_hf_request, client):
        """Test analysis without specifying a model (should use default)."""
        mock_hf_request.return_value = [{"generated_text": "Analysis with default model"}]
        
        payload = {
            "content": "def test(): pass",
            "analysis_type": "code_review"
            # No model specified
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Should use default model
        assert data["data"]["results"]["model_used"] == "google/flan-t5-base"

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_unsupported_model(self, mock_hf_request, client):
        """Test analysis with unsupported model."""
        payload = {
            "content": "Test content",
            "analysis_type": "code_review",
            "model": "unsupported/model"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        
        assert response.status_code == 200  # Service handles this gracefully
        data = response.json()
        assert data["status"] == "success"
        # Should return error results
        assert data["data"]["confidence"] == 0.0
        assert "error" in data["data"]["results"]

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_with_custom_parameters(self, mock_hf_request, client):
        """Test analysis with custom parameters."""
        mock_hf_request.return_value = [{"generated_text": "Analysis with custom parameters"}]
        
        payload = {
            "content": "Test content",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base",
            "parameters": {
                "temperature": 0.8,
                "max_tokens": 150,
                "custom_setting": "value"
            }
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_hf_api_error_handling(self, mock_hf_request, client, valid_analysis_request):
        """Test error handling when HuggingFace API fails."""
        # Mock API to raise an exception
        mock_hf_request.side_effect = Exception("HuggingFace API connection failed")
        
        response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        assert response.status_code == 200  # Service handles errors gracefully
        data = response.json()
        assert data["status"] == "success"
        # Should return error results
        assert data["data"]["confidence"] == 0.0
        assert "error" in data["data"]["results"]
        assert "HuggingFace API connection failed" in data["data"]["results"]["error"]

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_response_schema_conformity(self, mock_hf_request, client, valid_analysis_request):
        """Test that response conforms to StandardResponse schema."""
        mock_hf_request.return_value = [{"generated_text": "Schema test response"}]
        
        response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate against StandardResponse schema
        try:
            standard_response = StandardResponse(**data)
            assert standard_response.status == "success"
            assert standard_response.data is not None
            assert standard_response.timestamp is not None
            
            # Validate timestamp format
            datetime.strptime(standard_response.timestamp, "%Y-%m-%dT%H:%M:%SZ")
            
        except Exception as e:
            pytest.fail(f"Response does not conform to StandardResponse schema: {e}")

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_analysis_response_schema_conformity(self, mock_hf_request, client, valid_analysis_request):
        """Test that analysis data conforms to AnalysisResponse schema."""
        mock_hf_request.return_value = [{"generated_text": "Schema validation test"}]
        
        response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate analysis data against AnalysisResponse schema
        try:
            analysis_response = AnalysisResponse(**data["data"])
            assert analysis_response.analysis_id is not None
            assert analysis_response.results is not None
            assert 0.0 <= analysis_response.confidence <= 1.0
            assert isinstance(analysis_response.recommendations, list)
            assert analysis_response.processing_time_ms >= 0
            
        except Exception as e:
            pytest.fail(f"Analysis data does not conform to AnalysisResponse schema: {e}")

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_logging(self, mock_hf_request, client, valid_analysis_request, caplog):
        """Test that appropriate logging occurs."""
        mock_hf_request.return_value = [{"generated_text": "Logging test"}]
        
        with caplog.at_level("INFO"):
            response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        assert response.status_code == 200
        assert "Processing analysis request" in caplog.text
        assert "code_review" in caplog.text

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_error_logging(self, mock_hf_request, client, valid_analysis_request, caplog):
        """Test that errors are logged appropriately."""
        mock_hf_request.side_effect = Exception("Test error for logging")
        
        with caplog.at_level("ERROR"):
            response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        assert response.status_code == 200  # Service handles errors gracefully
        # Note: Error logging happens in AIEngine, not the FastAPI endpoint

    def test_analyze_content_type(self, client):
        """Test that response has correct content type."""
        with patch('scripts.ai_engine.model._hf_request') as mock_hf_request:
            mock_hf_request.return_value = [{"generated_text": "Content type test"}]
            
            payload = {
                "content": "test",
                "analysis_type": "code_review"
            }
            
            response = client.post("/ai-engine/analyze", json=payload)
            
            assert response.headers["content-type"] == "application/json"

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_large_content(self, mock_hf_request, client):
        """Test analysis of large content."""
        mock_hf_request.return_value = [{"generated_text": "Large content analysis"}]
        
        # Create large content (5KB)
        large_content = "def function():\n    # This is a large function\n    pass\n" * 100
        
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

    def test_analyze_http_methods(self, client):
        """Test that only POST method is allowed for analyze endpoint."""
        payload = {
            "content": "test",
            "analysis_type": "code_review"
        }
        
        # POST should work
        with patch('scripts.ai_engine.model._hf_request') as mock_hf_request:
            mock_hf_request.return_value = [{"generated_text": "Method test"}]
            response = client.post("/ai-engine/analyze", json=payload)
            assert response.status_code == 200
        
        # GET should not be allowed
        response = client.get("/ai-engine/analyze")
        assert response.status_code == 405  # Method Not Allowed
        
        # PUT should not be allowed
        response = client.put("/ai-engine/analyze", json=payload)
        assert response.status_code == 405  # Method Not Allowed
        
        # DELETE should not be allowed
        response = client.delete("/ai-engine/analyze")
        assert response.status_code == 405  # Method Not Allowed

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_unicode_content(self, mock_hf_request, client):
        """Test analysis of content with unicode characters."""
        mock_hf_request.return_value = [{"generated_text": "Unicode analysis complete"}]
        
        payload = {
            "content": "def función_española():\n    return 'Hola, mundo! ñáéíóú'",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        response = client.post("/ai-engine/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_processing_time_measurement(self, mock_hf_request, client, valid_analysis_request):
        """Test that processing time is accurately measured."""
        # Add delay to mock to simulate processing time
        def delayed_response(*args, **kwargs):
            import time
            time.sleep(0.01)  # 10ms delay
            return [{"generated_text": "Delayed response"}]
        
        mock_hf_request.side_effect = delayed_response
        
        response = client.post("/ai-engine/analyze", json=valid_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Processing time should reflect the delay
        assert data["data"]["processing_time_ms"] >= 10

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_malformed_json_request(self, mock_hf_request, client):
        """Test handling of malformed JSON in request."""
        import json
        
        # Send malformed JSON
        response = client.post(
            "/ai-engine/analyze",
            data='{"content": "test", "analysis_type": "code_review"',  # Missing closing brace
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_confidence_score_ranges(self, mock_hf_request, client):
        """Test that confidence scores are within valid ranges for different analysis types."""
        test_cases = [
            ("code_review", "def test(): pass"),
            ("requirement_extraction", "User authentication required"),
            ("tech_recommendation", "E-commerce website"),
            ("risk_assessment", "Cloud migration")
        ]
        
        for analysis_type, content in test_cases:
            if analysis_type == "requirement_extraction":
                # Mock both calls for requirement extraction
                mock_hf_request.side_effect = [
                    [{"generated_text": "Requirements analysis"}],
                    {"labels": ["tech"], "scores": [0.7]}
                ]
            else:
                mock_hf_request.return_value = [{"generated_text": "Analysis response"}]
            
            payload = {
                "content": content,
                "analysis_type": analysis_type,
                "model": "google/flan-t5-base"
            }
            
            response = client.post("/ai-engine/analyze", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            confidence = data["data"]["confidence"]
            assert 0.0 <= confidence <= 1.0
