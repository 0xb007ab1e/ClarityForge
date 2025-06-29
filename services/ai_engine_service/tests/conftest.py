"""Pytest configuration for AI Engine Service tests."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the service directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)


@pytest.fixture
def mock_hf_token():
    """Mock HuggingFace API token for tests."""
    with patch.dict(os.environ, {"HUGGINGFACE_API_TOKEN": "test_token"}):
        yield "test_token"


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    import logging
    from unittest.mock import Mock
    
    logger = Mock(spec=logging.Logger)
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    
    return logger


@pytest.fixture
def sample_hf_responses():
    """Provide sample HuggingFace API responses for testing."""
    return {
        "generate_response": [{"generated_text": "This is a sample generated response from the model."}],
        "classify": {"labels": ["tech support", "billing", "sales"], "scores": [0.8, 0.6, 0.4]},
        "error": {"error": "Model not found"}
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as an API test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "mock_hf: mark test as using HuggingFace mocks")


@pytest.fixture(autouse=True)
def clear_lru_cache():
    """Clear LRU cache between tests to ensure test isolation."""
    from scripts.assistant.ai_engine.main import AIEngine
    
    # Clear the LRU cache for get_available_models
    if hasattr(AIEngine.get_available_models, 'cache_clear'):
        AIEngine.get_available_models.cache_clear()
    
    yield
    
    # Clear again after test
    if hasattr(AIEngine.get_available_models, 'cache_clear'):
        AIEngine.get_available_models.cache_clear()


@pytest.fixture
def clean_imports():
    """Clean up imported modules after test to avoid import cache issues."""
    import sys
    
    # Store modules that were already imported
    initial_modules = set(sys.modules.keys())
    
    yield
    
    # Remove any modules that were imported during the test
    current_modules = set(sys.modules.keys())
    new_modules = current_modules - initial_modules
    
    for module in new_modules:
        if any(module.startswith(prefix) for prefix in ['scripts', 'main', 'schemas']):
            sys.modules.pop(module, None)
