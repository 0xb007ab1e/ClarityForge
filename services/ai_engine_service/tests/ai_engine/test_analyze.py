"""Unit tests for AI Engine analyze functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid
import sys
import os

# Add the service directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from scripts.assistant.ai_engine.main import AIEngine, AnalysisRequest, AnalysisResult


class TestAIEngineAnalyze:
    """Test suite for AIEngine analyze functionality."""

    @pytest.fixture
    def ai_engine(self):
        """Create an AIEngine instance for testing."""
        return AIEngine()

    @pytest.fixture
    def sample_analysis_request(self):
        """Create a sample analysis request."""
        return AnalysisRequest(
            content="def hello_world():\n    print('Hello, World!')",
            analysis_type="code_review",
            model="google/flan-t5-base",
            parameters={"temperature": 0.7}
        )

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_code_review_success(self, mock_hf_request, ai_engine, sample_analysis_request):
        """Test successful code review analysis."""
        # Mock the HuggingFace API response
        mock_hf_request.return_value = [{"generated_text": "This code looks good. Consider adding error handling and documentation."}]
        
        result = ai_engine.analyze_content(sample_analysis_request)
        
        # Verify the result structure
        assert isinstance(result, AnalysisResult)
        assert result.analysis_id is not None
        assert len(result.analysis_id) == 36  # UUID length
        assert result.confidence > 0.0
        assert result.confidence <= 1.0
        assert isinstance(result.results, dict)
        assert result.results["analysis_type"] == "code_review"
        assert result.results["model_used"] == "google/flan-t5-base"
        assert "review" in result.results
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0
        assert result.processing_time_ms >= 0  # Processing time should be non-negative
        
        # Verify the HuggingFace request was called correctly
        mock_hf_request.assert_called_once()
        call_args = mock_hf_request.call_args
        assert call_args[0][0] == "google/flan-t5-base"
        assert "inputs" in call_args[0][1]

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_requirement_extraction_success(self, mock_hf_request, ai_engine):
        """Test successful requirement extraction analysis."""
        # Mock responses for both generate_response and classify calls
        mock_hf_request.side_effect = [
            [{"generated_text": "Key requirements: 1. User authentication 2. Data storage 3. API endpoints"}],
            {"labels": ["tech support", "billing"], "scores": [0.8, 0.6]}
        ]
        
        request = AnalysisRequest(
            content="Build a web application with user login and database",
            analysis_type="requirement_extraction",
            model="google/flan-t5-base"
        )
        
        result = ai_engine.analyze_content(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.results["analysis_type"] == "requirement_extraction"
        assert "requirements" in result.results
        assert "classifications" in result.results
        assert result.confidence == 0.8  # Should be 0.8 when classifications exist
        assert len(result.recommendations) > 0
        
        # Verify both HuggingFace requests were made
        assert mock_hf_request.call_count == 2

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_tech_recommendation_success(self, mock_hf_request, ai_engine):
        """Test successful tech recommendation analysis."""
        mock_hf_request.return_value = [{"generated_text": "Recommended technologies: React, Node.js, PostgreSQL"}]
        
        request = AnalysisRequest(
            content="E-commerce website with real-time inventory",
            analysis_type="tech_recommendation",
            model="google/flan-t5-base"
        )
        
        result = ai_engine.analyze_content(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.results["analysis_type"] == "tech_recommendation"
        assert "recommendations" in result.results
        assert result.confidence == 0.75  # Fixed confidence for tech recommendations
        assert len(result.recommendations) > 0

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_risk_assessment_success(self, mock_hf_request, ai_engine):
        """Test successful risk assessment analysis."""
        mock_hf_request.return_value = [{"generated_text": "Potential risks: Security vulnerabilities, scalability issues"}]
        
        request = AnalysisRequest(
            content="Cloud-based microservices architecture",
            analysis_type="risk_assessment",
            model="google/flan-t5-base"
        )
        
        result = ai_engine.analyze_content(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.results["analysis_type"] == "risk_assessment"
        assert "risk_assessment" in result.results
        assert result.confidence == 0.7  # Fixed confidence for risk assessment
        assert len(result.recommendations) > 0

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_default_analysis_success(self, mock_hf_request, ai_engine):
        """Test successful default analysis for unknown analysis type."""
        mock_hf_request.return_value = [{"generated_text": "General analysis response"}]
        
        request = AnalysisRequest(
            content="Some content to analyze",
            analysis_type="unknown_type",
            model="google/flan-t5-base"
        )
        
        result = ai_engine.analyze_content(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.results["analysis_type"] == "general"
        assert "generated_text" in result.results
        assert result.confidence == 0.8  # Fixed confidence for default analysis

    def test_analyze_content_unsupported_model(self, ai_engine):
        """Test analysis with unsupported model."""
        request = AnalysisRequest(
            content="Test content",
            analysis_type="code_review",
            model="unsupported/model"
        )
        
        result = ai_engine.analyze_content(request)
        
        # Should return error result
        assert isinstance(result, AnalysisResult)
        assert result.confidence == 0.0
        assert "error" in result.results
        assert result.results["status"] == "failed"
        assert len(result.recommendations) > 0
        assert "Review input parameters" in result.recommendations[0]

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_api_error_handling(self, mock_hf_request, ai_engine, sample_analysis_request):
        """Test error handling when HuggingFace API fails."""
        # Mock API to raise an exception
        mock_hf_request.side_effect = Exception("API connection failed")
        
        result = ai_engine.analyze_content(sample_analysis_request)
        
        # Should return error result
        assert isinstance(result, AnalysisResult)
        assert result.confidence == 0.0
        assert "error" in result.results
        assert result.results["status"] == "failed"
        assert "API connection failed" in result.results["error"]

    @patch('scripts.ai_engine.model._hf_request')
    def test_analyze_content_confidence_calculation(self, mock_hf_request, ai_engine):
        """Test confidence calculation for different response lengths."""
        # Test with short response
        mock_hf_request.return_value = [{"generated_text": "Short"}]
        
        request = AnalysisRequest(
            content="def test(): pass",
            analysis_type="code_review",
            model="google/flan-t5-base"
        )
        
        result = ai_engine.analyze_content(request)
        
        # Confidence should be calculated based on response length
        assert result.confidence >= 0.6  # Minimum confidence
        assert result.confidence <= 0.95  # Maximum confidence

    def test_analyze_content_default_model_selection(self, ai_engine):
        """Test that default model is selected when none specified."""
        request = AnalysisRequest(
            content="Test content",
            analysis_type="code_review",
            model=None  # No model specified
        )
        
        with patch('scripts.ai_engine.model._hf_request') as mock_hf_request:
            mock_hf_request.return_value = [{"generated_text": "Default model response"}]
            
            result = ai_engine.analyze_content(request)
            
            # Should use default model
            assert result.results["model_used"] == "google/flan-t5-base"

    def test_generate_recommendations_by_analysis_type(self, ai_engine):
        """Test recommendation generation for different analysis types."""
        # Test code review recommendations
        code_review_recommendations = ai_engine._generate_recommendations({}, "code_review")
        assert "automated testing" in code_review_recommendations[0].lower()
        
        # Test requirement extraction recommendations
        req_recommendations = ai_engine._generate_recommendations({}, "requirement_extraction")
        assert "prioritize" in req_recommendations[0].lower()
        
        # Test tech recommendation recommendations
        tech_recommendations = ai_engine._generate_recommendations({}, "tech_recommendation")
        assert "expertise" in tech_recommendations[0].lower()
        
        # Test risk assessment recommendations
        risk_recommendations = ai_engine._generate_recommendations({}, "risk_assessment")
        assert "contingency" in risk_recommendations[0].lower()

    def test_analysis_request_creation(self):
        """Test AnalysisRequest object creation."""
        request = AnalysisRequest(
            content="test content",
            analysis_type="code_review",
            model="test-model",
            parameters={"param1": "value1"}
        )
        
        assert request.content == "test content"
        assert request.analysis_type == "code_review"
        assert request.model == "test-model"
        assert request.parameters == {"param1": "value1"}

    def test_analysis_request_default_parameters(self):
        """Test AnalysisRequest with default parameter values."""
        request = AnalysisRequest(
            content="test content",
            analysis_type="code_review"
        )
        
        assert request.content == "test content"
        assert request.analysis_type == "code_review"
        assert request.model is None
        assert request.parameters == {}

    def test_analysis_result_creation(self):
        """Test AnalysisResult object creation."""
        result = AnalysisResult(
            analysis_id="test-id",
            results={"key": "value"},
            confidence=0.85,
            recommendations=["rec1", "rec2"],
            processing_time_ms=1500
        )
        
        assert result.analysis_id == "test-id"
        assert result.results == {"key": "value"}
        assert result.confidence == 0.85
        assert result.recommendations == ["rec1", "rec2"]
        assert result.processing_time_ms == 1500

    @patch('scripts.ai_engine.model._hf_request')
    def test_processing_time_measurement(self, mock_hf_request, ai_engine, sample_analysis_request):
        """Test that processing time is measured correctly."""
        # Add a small delay to the mock to ensure processing time > 0
        def delayed_response(*args, **kwargs):
            import time
            time.sleep(0.001)  # 1ms delay
            return [{"generated_text": "Delayed response"}]
        
        mock_hf_request.side_effect = delayed_response
        
        result = ai_engine.analyze_content(sample_analysis_request)
        
        # Processing time should be greater than 0
        assert result.processing_time_ms > 0

    def test_supported_models_configuration(self, ai_engine):
        """Test that supported models are configured correctly."""
        assert "google/flan-t5-base" in ai_engine.supported_models
        assert "facebook/bart-large-mnli" in ai_engine.supported_models
        
        # Check model details
        flan_model = ai_engine.supported_models["google/flan-t5-base"]
        assert flan_model["name"] == "FLAN-T5 Base"
        assert flan_model["provider"] == "Google"
        assert "text_generation" in flan_model["capabilities"]
        
        bart_model = ai_engine.supported_models["facebook/bart-large-mnli"]
        assert bart_model["name"] == "BART Large MNLI"
        assert bart_model["provider"] == "Facebook"
        assert "classification" in bart_model["capabilities"]
