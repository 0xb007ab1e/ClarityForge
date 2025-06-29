"""Pytest configuration and shared fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for tests."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create some basic project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "README.md").write_text("# Test Project")
    
    return project_dir


@pytest.fixture
def sample_config():
    """Provide sample configuration for testing."""
    return {
        "project_name": "test-project",
        "version": "0.1.0",
        "description": "A test project for ClarityForge",
        "author": "Test Author",
        "license": "MIT"
    }


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Set test-specific environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture(scope="function")
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
        if module.startswith('clarity_forge'):
            sys.modules.pop(module, None)
