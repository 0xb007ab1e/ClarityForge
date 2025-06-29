"""Unit tests for AI Engine models endpoint."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

# Add the service directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from main import app
from schemas import StandardResponse, ModelsResponse, AIModel


class TestModelsEndpoint:
    """Test suite for the /ai-engine/models endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def mock_models_data(self):
        """Mock data for available models."""
        return [
            {
                "id": "google/flan-t5-base",
                "name": "FLAN-T5 Base",
                "description": "General-purpose model for natural language understanding",
                "capabilities": ["text_generation", "question_answering", "summarization"],
                "version": "base",
                "provider": "Google"
            },
            {
                "id": "facebook/bart-large-mnli",
                "name": "BART Large MNLI",
                "description": "Model for zero-shot classification and natural language inference",
                "capabilities": ["classification", "zero_shot_classification"],
                "version": "large",
                "provider": "Facebook"
            }
        ]

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_success(self, mock_get_models, client, mock_models_data):
        """Test successful retrieval of available models."""
        # Mock the AIEngine get_available_models method
        mock_get_models.return_value = mock_models_data
        
        response = client.get("/ai-engine/models")
        
        # Verify response status and structure
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "timestamp" in data
        assert "status" in data
        assert data["status"] == "success"
        
        # Verify models data structure
        models_data = data["data"]
        assert "models" in models_data
        assert len(models_data["models"]) == 2
        
        # Verify first model
        first_model = models_data["models"][0]
        assert first_model["id"] == "google/flan-t5-base"
        assert first_model["name"] == "FLAN-T5 Base"
        assert first_model["provider"] == "Google"
        assert "text_generation" in first_model["capabilities"]
        
        # Verify second model
        second_model = models_data["models"][1]
        assert second_model["id"] == "facebook/bart-large-mnli"
        assert second_model["name"] == "BART Large MNLI"
        assert second_model["provider"] == "Facebook"
        assert "classification" in second_model["capabilities"]
        
        # Verify AIEngine method was called
        mock_get_models.assert_called_once()

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_empty_list(self, mock_get_models, client):
        """Test response when no models are available."""
        # Mock empty models list
        mock_get_models.return_value = []
        
        response = client.get("/ai-engine/models")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["models"] == []

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_internal_error(self, mock_get_models, client):
        """Test error handling when AIEngine fails."""
        # Mock AIEngine to raise an exception
        mock_get_models.side_effect = Exception("Database connection failed")
        
        response = client.get("/ai-engine/models")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "MODELS_FETCH_ERROR"
        assert data["detail"]["message"] == "Failed to fetch available models"
        assert "original_error" in data["detail"]["details"]
        assert data["detail"]["details"]["original_error"] == "Database connection failed"

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_response_schema_conformity(self, mock_get_models, client, mock_models_data):
        """Test that response conforms to StandardResponse schema."""
        mock_get_models.return_value = mock_models_data
        
        response = client.get("/ai-engine/models")
        
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

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_models_response_schema_conformity(self, mock_get_models, client, mock_models_data):
        """Test that models data conforms to ModelsResponse schema."""
        mock_get_models.return_value = mock_models_data
        
        response = client.get("/ai-engine/models")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate models data against ModelsResponse schema
        try:
            models_response = ModelsResponse(**data["data"])
            assert len(models_response.models) == 2
            
            # Validate each model conforms to AIModel schema
            for model in models_response.models:
                assert isinstance(model, AIModel)
                assert model.id is not None
                assert model.name is not None
                assert model.description is not None
                assert isinstance(model.capabilities, list)
                assert model.version is not None
                assert model.provider is not None
                
        except Exception as e:
            pytest.fail(f"Models data does not conform to ModelsResponse schema: {e}")

    def test_get_models_content_type(self, client):
        """Test that response has correct content type."""
        with patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models') as mock_get_models:
            mock_get_models.return_value = []
            
            response = client.get("/ai-engine/models")
            
            assert response.headers["content-type"] == "application/json"

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_logging(self, mock_get_models, client, caplog):
        """Test that appropriate logging occurs."""
        mock_get_models.return_value = []
        
        with caplog.at_level("INFO"):
            response = client.get("/ai-engine/models")
        
        assert response.status_code == 200
        assert "Fetching available models" in caplog.text

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_error_logging(self, mock_get_models, client, caplog):
        """Test that errors are logged appropriately."""
        mock_get_models.side_effect = Exception("Test error")
        
        with caplog.at_level("ERROR"):
            response = client.get("/ai-engine/models")
        
        assert response.status_code == 500
        assert "Error fetching models" in caplog.text
        assert "Test error" in caplog.text

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_caching_behavior(self, mock_get_models, client, mock_models_data):
        """Test that models are cached by the AIEngine."""
        mock_get_models.return_value = mock_models_data
        
        # Make multiple requests
        for _ in range(3):
            response = client.get("/ai-engine/models")
            assert response.status_code == 200
        
        # get_available_models should be called each time since FastAPI doesn't cache
        assert mock_get_models.call_count == 3

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_malformed_data_handling(self, mock_get_models, client):
        """Test handling of malformed data from AIEngine."""
        # Mock AIEngine to return malformed data
        mock_get_models.return_value = [
            {
                "id": "test-model",
                # Missing required fields
            }
        ]
        
        response = client.get("/ai-engine/models")
        
        # Should result in an error due to missing required fields
        assert response.status_code == 500

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_single_model(self, mock_get_models, client):
        """Test response with a single model."""
        single_model_data = [
            {
                "id": "single/model",
                "name": "Single Model",
                "description": "A single test model",
                "capabilities": ["testing"],
                "version": "1.0",
                "provider": "Test Provider"
            }
        ]
        
        mock_get_models.return_value = single_model_data
        
        response = client.get("/ai-engine/models")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["models"]) == 1
        assert data["data"]["models"][0]["id"] == "single/model"

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_large_number_of_models(self, mock_get_models, client):
        """Test response with a large number of models."""
        large_model_list = []
        for i in range(50):
            large_model_list.append({
                "id": f"model-{i}",
                "name": f"Model {i}",
                "description": f"Test model number {i}",
                "capabilities": ["testing"],
                "version": "1.0",
                "provider": "Test Provider"
            })
        
        mock_get_models.return_value = large_model_list
        
        response = client.get("/ai-engine/models")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["models"]) == 50

    def test_get_models_http_methods(self, client):
        """Test that only GET method is allowed for models endpoint."""
        # GET should work
        with patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models') as mock_get_models:
            mock_get_models.return_value = []
            response = client.get("/ai-engine/models")
            assert response.status_code == 200
        
        # POST should not be allowed
        response = client.post("/ai-engine/models")
        assert response.status_code == 405  # Method Not Allowed
        
        # PUT should not be allowed
        response = client.put("/ai-engine/models")
        assert response.status_code == 405  # Method Not Allowed
        
        # DELETE should not be allowed
        response = client.delete("/ai-engine/models")
        assert response.status_code == 405  # Method Not Allowed

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_concurrent_requests(self, mock_get_models, client, mock_models_data):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        mock_get_models.return_value = mock_models_data
        
        # Add a small delay to simulate processing time
        def delayed_get_models():
            time.sleep(0.1)
            return mock_models_data
        
        mock_get_models.side_effect = delayed_get_models
        
        responses = []
        threads = []
        
        def make_request():
            response = client.get("/ai-engine/models")
            responses.append(response)
        
        # Create multiple threads to make concurrent requests
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(responses) == 3
        for response in responses:
            assert response.status_code == 200

    @patch('scripts.assistant.ai_engine.main.AIEngine.get_available_models')
    def test_get_models_unicode_handling(self, mock_get_models, client):
        """Test handling of unicode characters in model data."""
        unicode_model_data = [
            {
                "id": "unicode/model",
                "name": "Modèle Spéciàl",
                "description": "Un modèle avec des caractères spéciaux: ñ, ü, ç",
                "capabilities": ["génération", "analyse"],
                "version": "1.0α",
                "provider": "Føõ Corporation"
            }
        ]
        
        mock_get_models.return_value = unicode_model_data
        
        response = client.get("/ai-engine/models")
        
        assert response.status_code == 200
        data = response.json()
        model = data["data"]["models"][0]
        assert model["name"] == "Modèle Spéciàl"
        assert "caractères spéciaux" in model["description"]
