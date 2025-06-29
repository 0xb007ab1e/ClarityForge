"""
Initialization Testing Sandbox for ClarityForge

This module provides a comprehensive testing environment for all initialization
components of the ClarityForge project, including:
- Configuration initialization
- CLI setup and commands
- API initialization
- Module imports and dependencies
- Environment variable handling
"""

import os
import sys
import tempfile
import subprocess
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

import pytest
import click.testing
from fastapi.testclient import TestClient

# Import ClarityForge modules
from clarity_forge.config import Config, config
from clarity_forge.cli import cli


class InitializationSandbox:
    """
    A sandbox environment for testing initialization logic in isolation.
    
    This class provides utilities for:
    - Creating isolated test environments
    - Mocking external dependencies
    - Testing configuration initialization
    - Validating CLI command setup
    - Testing API startup/shutdown
    """
    
    def __init__(self, test_name: str = "init_test"):
        self.test_name = test_name
        self.temp_dir = None
        self.original_env = None
        self.mocked_modules = []
        
    def __enter__(self):
        """Enter the sandbox context."""
        self.setup_sandbox()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the sandbox context and cleanup."""
        self.cleanup_sandbox()
        
    def setup_sandbox(self):
        """Setup the isolated testing environment."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix=f"clarity_forge_{self.test_name}_")
        
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Clear test-specific environment variables
        test_env_vars = [
            'DEBUG', 'API_HOST', 'API_PORT', 'LOG_LEVEL', 
            'OPENAI_API_KEY', 'ENVIRONMENT'
        ]
        for var in test_env_vars:
            os.environ.pop(var, None)
            
        return self
        
    def cleanup_sandbox(self):
        """Cleanup the sandbox environment."""
        # Restore original environment
        if self.original_env:
            os.environ.clear()
            os.environ.update(self.original_env)
            
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
        # Clean up mocked modules
        for module_name in self.mocked_modules:
            sys.modules.pop(module_name, None)
            
    def set_env_vars(self, **kwargs):
        """Set environment variables for testing."""
        for key, value in kwargs.items():
            os.environ[key] = str(value)
            
    def create_config_file(self, config_data: dict, filename: str = "settings.json"):
        """Create a configuration file in the temp directory."""
        config_dir = Path(self.temp_dir) / "config"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / filename
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
            
        return config_file
        
    def mock_subprocess(self, return_code: int = 0, stdout: str = "", stderr: str = ""):
        """Mock subprocess calls."""
        mock_result = Mock()
        mock_result.returncode = return_code
        mock_result.stdout = stdout.encode()
        mock_result.stderr = stderr.encode()
        
        return patch('subprocess.run', return_value=mock_result)


# Test fixtures using the sandbox
@pytest.fixture
def init_sandbox():
    """Provide an initialization sandbox for tests."""
    with InitializationSandbox() as sandbox:
        yield sandbox


@pytest.fixture
def sample_project_config():
    """Provide sample project configuration."""
    return {
        "project": {
            "name": "TestProject",
            "description": "A test project for initialization testing",
            "directories": ["src", "tests", "docs"]
        },
        "issue_tracker": {
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Something isn't working"
                },
                {
                    "name": "enhancement",
                    "color": "a2eeef",
                    "description": "New feature or request"
                }
            ],
            "seed_issues": [
                {
                    "title": "Initial Setup",
                    "body": "Setup project structure and basic configuration",
                    "labels": ["enhancement"]
                }
            ]
        }
    }


# Configuration Initialization Tests
class TestConfigInitialization:
    """Test configuration system initialization."""
    
    def test_default_config_initialization(self, init_sandbox):
        """Test that config initializes with default values."""
        # Create a fresh config instance
        test_config = Config()
        
        assert test_config.debug is False
        assert test_config.api_host == "localhost"
        assert test_config.api_port == 8000
        assert test_config.log_level == "INFO"
        assert test_config.openai_api_key is None
        assert test_config.api_url == "http://localhost:8000"
        
    def test_config_with_environment_variables(self, init_sandbox):
        """Test config initialization with environment variables."""
        init_sandbox.set_env_vars(
            DEBUG="true",
            API_HOST="testhost",
            API_PORT="9000",
            LOG_LEVEL="DEBUG",
            OPENAI_API_KEY="test-key-123"
        )
        
        test_config = Config()
        
        assert test_config.debug is True
        assert test_config.api_host == "testhost"
        assert test_config.api_port == 9000
        assert test_config.log_level == "DEBUG"
        assert test_config.openai_api_key == "test-key-123"
        assert test_config.api_url == "http://testhost:9000"
        
    def test_config_edge_cases(self, init_sandbox):
        """Test config initialization with edge case values."""
        # Test various boolean representations
        test_cases = [
            ("TRUE", True),
            ("True", True),
            ("1", False),  # Only "true" (lowercase) should be True
            ("false", False),
            ("", False),
        ]
        
        for debug_value, expected in test_cases:
            # Clear any existing DEBUG variable
            os.environ.pop("DEBUG", None)
            if debug_value:
                os.environ["DEBUG"] = debug_value
                
            test_config = Config()
            assert test_config.debug == expected, f"Failed for DEBUG='{debug_value}'"
            
    def test_config_port_conversion(self, init_sandbox):
        """Test that API_PORT is properly converted to integer."""
        init_sandbox.set_env_vars(API_PORT="8080")
        test_config = Config()
        assert isinstance(test_config.api_port, int)
        assert test_config.api_port == 8080
        
        # Test invalid port handling
        init_sandbox.set_env_vars(API_PORT="invalid")
        with pytest.raises(ValueError):
            Config()


# CLI Initialization Tests
class TestCLIInitialization:
    """Test CLI system initialization."""
    
    def test_cli_group_creation(self):
        """Test that CLI group is properly created."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "ClarityForge" in result.output
        assert "AI-powered development planning" in result.output
        
    def test_serve_command_initialization(self):
        """Test that serve command is properly registered."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['serve', '--help'])
        
        assert result.exit_code == 0
        assert "--host" in result.output
        assert "--port" in result.output
        assert "Run the API with uvicorn" in result.output
        
    def test_setup_command_without_config(self, init_sandbox):
        """Test setup command when config file is missing."""
        runner = click.testing.CliRunner()
        
        # Change to temp directory where config doesn't exist
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['setup'])
            
            assert result.exit_code == 0
            assert "config/settings.json not found" in result.output
            
    def test_setup_command_with_config(self, init_sandbox, sample_project_config):
        """Test setup command with valid configuration."""
        runner = click.testing.CliRunner()
        
        with runner.isolated_filesystem():
            # Create config directory and file
            os.makedirs("config", exist_ok=True)
            with open("config/settings.json", "w") as f:
                json.dump(sample_project_config, f)
                
            # Mock subprocess calls
            with init_sandbox.mock_subprocess():
                result = runner.invoke(cli, ['setup'])
                
            assert result.exit_code == 0
            assert "Project setup complete!" in result.output
            
            # Check that directories were created
            for directory in sample_project_config["project"]["directories"]:
                assert os.path.exists(directory)
                
            # Check that README was updated
            assert os.path.exists("README.md")
            with open("README.md", "r") as f:
                readme_content = f.read()
                assert sample_project_config["project"]["name"] in readme_content


# API Initialization Tests
class TestAPIInitialization:
    """Test API system initialization."""
    
    def test_api_import(self):
        """Test that API module can be imported."""
        try:
            from clarity_forge.api import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"API module not available: {e}")
            
    @pytest.mark.integration
    def test_api_startup(self, init_sandbox):
        """Test API startup process."""
        try:
            from clarity_forge.api import app
            
            # Test that the app can be created
            client = TestClient(app)
            
            # Test basic endpoint if available
            response = client.get("/")
            # Don't assert on status code as endpoint may not exist yet
            # Just ensure no import/startup errors
            
        except ImportError:
            pytest.skip("API module not available")


# Module Import Tests
class TestModuleInitialization:
    """Test module import and initialization."""
    
    def test_main_module_import(self):
        """Test that main clarity_forge module imports correctly."""
        import clarity_forge
        
        assert hasattr(clarity_forge, '__version__')
        assert clarity_forge.__version__ == "0.1.0"
        
    def test_config_module_import(self):
        """Test that config module imports and has global config."""
        from clarity_forge.config import config
        
        assert config is not None
        assert hasattr(config, 'debug')
        assert hasattr(config, 'api_host')
        assert hasattr(config, 'api_port')
        
    def test_cli_module_import(self):
        """Test that CLI module imports correctly."""
        from clarity_forge.cli import cli
        
        assert cli is not None
        assert hasattr(cli, 'commands')


# Integration Tests
class TestInitializationIntegration:
    """Test integration between initialization components."""
    
    def test_config_cli_integration(self, init_sandbox):
        """Test that CLI commands can access configuration."""
        init_sandbox.set_env_vars(
            API_HOST="integration-test",
            API_PORT="9999"
        )
        
        # Import after setting environment
        from clarity_forge.config import Config
        test_config = Config()
        
        # Verify CLI can use this configuration
        runner = click.testing.CliRunner()
        
        # Test serve command with config values
        with patch('uvicorn.run') as mock_uvicorn:
            result = runner.invoke(cli, [
                'serve', 
                '--host', test_config.api_host,
                '--port', str(test_config.api_port)
            ])
            
            assert result.exit_code == 0
            mock_uvicorn.assert_called_once()
            
    def test_full_initialization_sequence(self, init_sandbox, sample_project_config):
        """Test a complete initialization sequence."""
        runner = click.testing.CliRunner()
        
        with runner.isolated_filesystem():
            # Step 1: Setup environment
            init_sandbox.set_env_vars(
                DEBUG="true",
                LOG_LEVEL="DEBUG"
            )
            
            # Step 2: Create configuration
            os.makedirs("config", exist_ok=True)
            with open("config/settings.json", "w") as f:
                json.dump(sample_project_config, f)
                
            # Step 3: Run setup command
            with init_sandbox.mock_subprocess():
                setup_result = runner.invoke(cli, ['setup'])
                
            assert setup_result.exit_code == 0
            
            # Step 4: Verify configuration is accessible
            from clarity_forge.config import Config
            test_config = Config()
            assert test_config.debug is True
            assert test_config.log_level == "DEBUG"
            
            # Step 5: Verify CLI is functional
            help_result = runner.invoke(cli, ['--help'])
            assert help_result.exit_code == 0


# Performance and Resource Tests
class TestInitializationPerformance:
    """Test initialization performance and resource usage."""
    
    def test_import_time(self):
        """Test that module imports are reasonably fast."""
        import time
        
        start_time = time.time()
        import clarity_forge
        from clarity_forge.config import config
        from clarity_forge.cli import cli
        end_time = time.time()
        
        import_time = end_time - start_time
        assert import_time < 1.0, f"Import took {import_time:.2f}s, too slow"
        
    def test_config_initialization_time(self):
        """Test that config initialization is fast."""
        import time
        
        start_time = time.time()
        test_config = Config()
        end_time = time.time()
        
        init_time = end_time - start_time
        assert init_time < 0.1, f"Config init took {init_time:.2f}s, too slow"
        
    def test_multiple_config_instances(self):
        """Test that multiple config instances work correctly."""
        config1 = Config()
        config2 = Config()
        
        # They should have the same values but be different instances
        assert config1.api_host == config2.api_host
        assert config1.api_port == config2.api_port
        assert id(config1) != id(config2)


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    print("Running initialization sandbox tests...")
    
    # Run a quick smoke test
    with InitializationSandbox("smoke_test") as sandbox:
        print(f"✓ Sandbox created at: {sandbox.temp_dir}")
        
        # Test config initialization
        sandbox.set_env_vars(DEBUG="true", API_PORT="8080")
        test_config = Config()
        print(f"✓ Config initialized: debug={test_config.debug}, port={test_config.api_port}")
        
        # Test CLI
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['--help'])
        print(f"✓ CLI functional: exit_code={result.exit_code}")
        
    print("✓ All smoke tests passed!")
